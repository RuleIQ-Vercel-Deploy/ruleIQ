"""
Database optimization utilities for RuleIQ.

Provides query optimization, indexing recommendations, and N+1 prevention.
"""

import logging
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
from sqlalchemy import text, inspect, MetaData, Table
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Query, selectinload, joinedload, subqueryload, contains_eager
from sqlalchemy.sql import Select
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


@dataclass
class QueryMetrics:
    """Metrics for a database query."""
    query: str
    execution_time: float
    rows_returned: int
    timestamp: datetime
    slow: bool = False
    
    @property
    def is_slow(self) -> bool:
        """Check if query is slow (> 1 second)."""
        return self.execution_time > 1.0


@dataclass 
class IndexRecommendation:
    """Recommendation for a database index."""
    table: str
    columns: List[str]
    reason: str
    estimated_improvement: str
    priority: str  # 'high', 'medium', 'low'


class QueryAnalyzer:
    """Analyzes queries for performance issues."""
    
    def __init__(self):
        self.slow_queries: List[QueryMetrics] = []
        self.query_patterns: Dict[str, int] = {}
        
    def analyze_query(self, query: str, execution_time: float, rows: int) -> QueryMetrics:
        """Analyze a single query's performance."""
        metrics = QueryMetrics(
            query=query,
            execution_time=execution_time,
            rows_returned=rows,
            timestamp=datetime.utcnow(),
            slow=execution_time > 1.0
        )
        
        if metrics.is_slow:
            self.slow_queries.append(metrics)
            logger.warning(f"Slow query detected ({execution_time:.2f}s): {query[:100]}...")
            
        # Track query patterns
        pattern = self._extract_pattern(query)
        self.query_patterns[pattern] = self.query_patterns.get(pattern, 0) + 1
        
        return metrics
        
    def _extract_pattern(self, query: str) -> str:
        """Extract query pattern for analysis."""
        # Simplify query to pattern
        query_lower = query.lower()
        
        if 'select' in query_lower:
            if 'join' in query_lower:
                return 'SELECT_WITH_JOIN'
            elif 'where' in query_lower:
                return 'SELECT_WITH_WHERE'
            else:
                return 'SIMPLE_SELECT'
        elif 'insert' in query_lower:
            return 'INSERT'
        elif 'update' in query_lower:
            return 'UPDATE'
        elif 'delete' in query_lower:
            return 'DELETE'
        else:
            return 'OTHER'
            
    def get_recommendations(self) -> List[str]:
        """Get optimization recommendations based on analysis."""
        recommendations = []
        
        # Check for N+1 patterns
        if self.query_patterns.get('SIMPLE_SELECT', 0) > 100:
            recommendations.append(
                "High number of simple SELECTs detected. Consider using eager loading (joinedload/selectinload) to prevent N+1 queries."
            )
            
        # Check for missing indexes on frequently joined tables
        join_count = self.query_patterns.get('SELECT_WITH_JOIN', 0)
        if join_count > 50:
            recommendations.append(
                f"Found {join_count} queries with JOINs. Ensure foreign key columns have indexes."
            )
            
        # Check slow queries
        if len(self.slow_queries) > 5:
            recommendations.append(
                f"Found {len(self.slow_queries)} slow queries. Consider adding indexes or optimizing query structure."
            )
            
        return recommendations


class DatabaseOptimizer:
    """Main database optimization class."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.analyzer = QueryAnalyzer()
        self._index_cache: Optional[Dict[str, List[str]]] = None
        
    async def analyze_table_indexes(self, table_name: str) -> List[Dict[str, Any]]:
        """Analyze indexes for a specific table."""
        query = text("""
            SELECT 
                indexname,
                indexdef,
                tablename,
                schemaname
            FROM pg_indexes
            WHERE tablename = :table_name
        """)
        
        result = await self.session.execute(query, {"table_name": table_name})
        indexes = []
        for row in result:
            indexes.append({
                'name': row.indexname,
                'definition': row.indexdef,
                'table': row.tablename,
                'schema': row.schemaname
            })
            
        return indexes
        
    async def get_table_statistics(self, table_name: str) -> Dict[str, Any]:
        """Get statistics for a table."""
        stats_query = text("""
            SELECT 
                n_live_tup as row_count,
                n_dead_tup as dead_rows,
                last_vacuum,
                last_autovacuum,
                last_analyze,
                last_autoanalyze
            FROM pg_stat_user_tables
            WHERE relname = :table_name
        """)
        
        size_query = text("""
            SELECT 
                pg_size_pretty(pg_total_relation_size(:table_name::regclass)) as total_size,
                pg_size_pretty(pg_table_size(:table_name::regclass)) as table_size,
                pg_size_pretty(pg_indexes_size(:table_name::regclass)) as indexes_size
        """)
        
        stats_result = await self.session.execute(stats_query, {"table_name": table_name})
        size_result = await self.session.execute(size_query, {"table_name": table_name})
        
        stats_row = stats_result.first()
        size_row = size_result.first()
        
        if stats_row and size_row:
            return {
                'row_count': stats_row.row_count,
                'dead_rows': stats_row.dead_rows,
                'last_vacuum': stats_row.last_vacuum,
                'last_autovacuum': stats_row.last_autovacuum,
                'last_analyze': stats_row.last_analyze,
                'last_autoanalyze': stats_row.last_autoanalyze,
                'total_size': size_row.total_size,
                'table_size': size_row.table_size,
                'indexes_size': size_row.indexes_size
            }
        return {}
        
    async def recommend_indexes(self) -> List[IndexRecommendation]:
        """Recommend indexes based on query patterns and missing indexes."""
        recommendations = []
        
        # Check for missing indexes on foreign keys
        fk_query = text("""
            SELECT
                tc.table_name,
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY'
        """)
        
        result = await self.session.execute(fk_query)
        foreign_keys = result.fetchall()
        
        for fk in foreign_keys:
            # Check if index exists for this foreign key
            indexes = await self.analyze_table_indexes(fk.table_name)
            column_indexed = any(
                fk.column_name in idx['definition'] for idx in indexes
            )
            
            if not column_indexed:
                recommendations.append(IndexRecommendation(
                    table=fk.table_name,
                    columns=[fk.column_name],
                    reason=f"Foreign key to {fk.foreign_table_name}.{fk.foreign_column_name} lacks index",
                    estimated_improvement="30-50% faster joins",
                    priority="high"
                ))
        
        # Check for frequently filtered columns without indexes
        filter_patterns = await self._analyze_where_clauses()
        for table, columns in filter_patterns.items():
            for column, count in columns.items():
                if count > 10:  # Threshold for frequent filtering
                    indexes = await self.analyze_table_indexes(table)
                    column_indexed = any(
                        column in idx['definition'] for idx in indexes
                    )
                    
                    if not column_indexed:
                        recommendations.append(IndexRecommendation(
                            table=table,
                            columns=[column],
                            reason=f"Column frequently used in WHERE clauses ({count} times)",
                            estimated_improvement="20-40% faster queries",
                            priority="medium" if count < 50 else "high"
                        ))
        
        return recommendations
        
    async def _analyze_where_clauses(self) -> Dict[str, Dict[str, int]]:
        """Analyze WHERE clauses from pg_stat_statements if available."""
        # This would require pg_stat_statements extension
        # For now, return empty dict
        return {}
        
    async def optimize_query(self, query: Select) -> Select:
        """Optimize a SQLAlchemy query."""
        # Add eager loading for relationships to prevent N+1
        # This is a simplified example - real implementation would analyze relationships
        
        # Example optimizations:
        # 1. Add select_from to specify join order
        # 2. Add options for eager loading
        # 3. Add query hints
        
        return query
        
    async def vacuum_analyze_table(self, table_name: str) -> bool:
        """Run VACUUM ANALYZE on a table."""
        try:
            await self.session.execute(text(f"VACUUM ANALYZE {table_name}"))
            await self.session.commit()
            logger.info(f"Successfully ran VACUUM ANALYZE on {table_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to VACUUM ANALYZE {table_name}: {e}")
            await self.session.rollback()
            return False
            
    async def create_index(
        self, 
        table_name: str, 
        columns: List[str], 
        index_name: Optional[str] = None,
        unique: bool = False,
        concurrent: bool = True
    ) -> bool:
        """Create an index on specified columns."""
        if not index_name:
            index_name = f"idx_{table_name}_{'_'.join(columns)}"
            
        columns_str = ', '.join(columns)
        unique_str = "UNIQUE " if unique else ""
        concurrent_str = "CONCURRENTLY " if concurrent else ""
        
        query = text(
            f"CREATE {unique_str}INDEX {concurrent_str}IF NOT EXISTS {index_name} "
            f"ON {table_name} ({columns_str})"
        )
        
        try:
            await self.session.execute(query)
            await self.session.commit()
            logger.info(f"Created index {index_name} on {table_name}({columns_str})")
            return True
        except Exception as e:
            logger.error(f"Failed to create index {index_name}: {e}")
            await self.session.rollback()
            return False
            
    async def analyze_slow_queries(self, threshold_ms: int = 1000) -> List[Dict[str, Any]]:
        """Analyze slow queries from PostgreSQL logs."""
        query = text("""
            SELECT 
                query,
                calls,
                total_exec_time,
                mean_exec_time,
                max_exec_time,
                rows
            FROM pg_stat_statements
            WHERE mean_exec_time > :threshold
            ORDER BY mean_exec_time DESC
            LIMIT 20
        """)
        
        try:
            result = await self.session.execute(query, {"threshold": threshold_ms})
            slow_queries = []
            for row in result:
                slow_queries.append({
                    'query': row.query,
                    'calls': row.calls,
                    'total_time': row.total_exec_time,
                    'mean_time': row.mean_exec_time,
                    'max_time': row.max_exec_time,
                    'rows': row.rows
                })
            return slow_queries
        except Exception as e:
            logger.warning(f"Could not analyze slow queries (pg_stat_statements may not be enabled): {e}")
            return []


class EagerLoadingOptimizer:
    """Optimizes queries with eager loading to prevent N+1 problems."""
    
    @staticmethod
    def optimize_for_relationships(query: Query, *relationships: str) -> Query:
        """Add eager loading for specified relationships."""
        for rel in relationships:
            if '.' in rel:
                # Nested relationship
                query = query.options(selectinload(rel))
            else:
                # Direct relationship
                query = query.options(joinedload(rel))
        return query
        
    @staticmethod
    def optimize_assessment_query(query: Query) -> Query:
        """Optimize assessment-related queries."""
        return query.options(
            selectinload('business_profile'),
            selectinload('user'),
            selectinload('questions'),
            selectinload('frameworks')
        )
        
    @staticmethod
    def optimize_business_profile_query(query: Query) -> Query:
        """Optimize business profile queries."""
        return query.options(
            selectinload('user'),
            selectinload('assessments'),
            selectinload('compliance_frameworks'),
            selectinload('evidence_items')
        )
        
    @staticmethod
    def optimize_framework_query(query: Query) -> Query:
        """Optimize compliance framework queries."""
        return query.options(
            selectinload('requirements'),
            selectinload('controls'),
            selectinload('evidence_mappings')
        )