#!/usr/bin/env python3
"""
RuleIQ Database Health Check Script

Comprehensive database health monitoring and diagnostics for:
- Connection pool health
- Query performance
- Table statistics
- Index usage
- Lock monitoring
- Slow query analysis
"""

import sys
import asyncio
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime, timedelta
import json

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseHealthChecker:
    """Comprehensive database health monitoring and diagnostics."""

    def __init__(self):
        self.results: Dict[str, Any] = {}
        self.issues: List[str] = []
        self.warnings: List[str] = []
        self.recommendations: List[str] = []

    async def check_database_connectivity(self) -> bool:
        """Basic database connectivity check."""
        try:
            from database.db_setup import get_async_db, get_engine_info
            from sqlalchemy import text

            engine_info = get_engine_info()
            if not engine_info.get('async_engine_initialized'):
                self.issues.append("Database engine not initialized")
                self.results['connectivity'] = {
                    'status': 'failed',
                    'message': 'Engine not initialized'
                }
                return False

            async for db in get_async_db():
                try:
                    result = await db.execute(text("SELECT version()"))
                    version = result.scalar()
                    self.results['connectivity'] = {
                        'status': 'connected',
                        'database_version': version,
                        'message': 'Connection successful'
                    }
                    logger.info(f"✓ Connected to database: {version}")
                    return True
                finally:
                    await db.close()
                    break

        except Exception as e:
            self.issues.append(f"Connection failed: {str(e)}")
            self.results['connectivity'] = {
                'status': 'failed',
                'error': str(e)
            }
            return False

    async def check_connection_pool_health(self) -> Dict[str, Any]:
        """Monitor connection pool statistics."""
        try:
            from database.db_setup import get_engine_info
            from monitoring.database_monitor import get_database_monitor

            monitor = get_database_monitor()
            if monitor:
                summary = monitor.get_monitoring_summary()
                current_metrics = summary.get('current_metrics', {})

                pool_health = {
                    'status': 'healthy',
                    'metrics': {}
                }

                for pool_type, metrics in current_metrics.items():
                    if metrics:
                        utilization = metrics.get('utilization_percent', 0)
                        pool_health['metrics'][pool_type] = {
                            'size': metrics.get('size', 0),
                            'checked_out': metrics.get('checked_out_connections', 0),
                            'overflow': metrics.get('overflow', 0),
                            'utilization_percent': utilization
                        }

                        # Check for pool exhaustion
                        if utilization > 90:
                            self.warnings.append(f"{pool_type} pool utilization high: {utilization}%")
                            pool_health['status'] = 'warning'
                        elif utilization > 95:
                            self.issues.append(f"{pool_type} pool nearly exhausted: {utilization}%")
                            pool_health['status'] = 'critical'

                self.results['connection_pool'] = pool_health
                return pool_health
            else:
                self.results['connection_pool'] = {
                    'status': 'unavailable',
                    'message': 'Monitor not initialized'
                }
                return {}

        except Exception as e:
            self.results['connection_pool'] = {
                'status': 'error',
                'error': str(e)
            }
            return {}

    async def check_table_statistics(self) -> Dict[str, Any]:
        """Analyze table sizes and row counts."""
        try:
            from database.db_setup import get_async_db
            from sqlalchemy import text

            table_stats = {}

            async for db in get_async_db():
                try:
                    # Get table statistics
                    query = text("""
                        SELECT
                            schemaname,
                            tablename,
                            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
                            pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
                            n_live_tup AS row_count,
                            n_dead_tup AS dead_rows,
                            last_vacuum,
                            last_autovacuum
                        FROM pg_stat_user_tables
                        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                        LIMIT 20
                    """)

                    result = await db.execute(query)
                    tables = result.fetchall()

                    for table in tables:
                        table_name = f"{table[0]}.{table[1]}"
                        stats = {
                            'total_size': table[2],
                            'table_size': table[3],
                            'row_count': table[4],
                            'dead_rows': table[5],
                            'last_vacuum': str(table[6]) if table[6] else None,
                            'last_autovacuum': str(table[7]) if table[7] else None
                        }
                        table_stats[table_name] = stats

                        # Check for maintenance issues
                        if table[5] > table[4] * 0.2:  # Dead rows > 20% of live rows
                            self.warnings.append(f"Table {table_name} has high dead row ratio")
                            self.recommendations.append(f"Consider running VACUUM on {table_name}")

                    self.results['table_statistics'] = {
                        'status': 'analyzed',
                        'table_count': len(tables),
                        'tables': table_stats
                    }

                finally:
                    await db.close()
                    break

            return table_stats

        except Exception as e:
            self.results['table_statistics'] = {
                'status': 'error',
                'error': str(e)
            }
            return {}

    async def check_index_usage(self) -> Dict[str, Any]:
        """Analyze index usage and identify missing indexes."""
        try:
            from database.db_setup import get_async_db
            from sqlalchemy import text

            index_stats = {
                'unused_indexes': [],
                'missing_indexes': [],
                'index_usage': {}
            }

            async for db in get_async_db():
                try:
                    # Find unused indexes
                    unused_query = text("""
                        SELECT
                            schemaname,
                            tablename,
                            indexname,
                            pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
                            idx_scan
                        FROM pg_stat_user_indexes
                        WHERE idx_scan = 0
                        AND indexrelid != 0
                        ORDER BY pg_relation_size(indexrelid) DESC
                        LIMIT 10
                    """)

                    result = await db.execute(unused_query)
                    unused = result.fetchall()

                    for idx in unused:
                        index_info = {
                            'schema': idx[0],
                            'table': idx[1],
                            'index': idx[2],
                            'size': idx[3],
                            'scans': idx[4]
                        }
                        index_stats['unused_indexes'].append(index_info)
                        self.warnings.append(f"Unused index: {idx[2]} on {idx[1]} (size: {idx[3]})")

                    # Find tables with sequential scans
                    seq_scan_query = text("""
                        SELECT
                            schemaname,
                            tablename,
                            seq_scan,
                            seq_tup_read,
                            idx_scan,
                            n_live_tup
                        FROM pg_stat_user_tables
                        WHERE seq_scan > idx_scan
                        AND n_live_tup > 1000
                        ORDER BY seq_tup_read DESC
                        LIMIT 10
                    """)

                    result = await db.execute(seq_scan_query)
                    seq_scans = result.fetchall()

                    for table in seq_scans:
                        if table[2] > table[4] * 10:  # Significantly more seq scans than index scans
                            table_name = f"{table[0]}.{table[1]}"
                            self.recommendations.append(f"Consider adding indexes to {table_name}")
                            index_stats['missing_indexes'].append({
                                'table': table_name,
                                'seq_scans': table[2],
                                'index_scans': table[4],
                                'rows': table[5]
                            })

                    self.results['index_analysis'] = index_stats

                finally:
                    await db.close()
                    break

            return index_stats

        except Exception as e:
            self.results['index_analysis'] = {
                'status': 'error',
                'error': str(e)
            }
            return {}

    async def check_active_queries(self) -> List[Dict]:
        """Monitor currently active queries."""
        try:
            from database.db_setup import get_async_db
            from sqlalchemy import text

            active_queries = []

            async for db in get_async_db():
                try:
                    query = text("""
                        SELECT
                            pid,
                            usename,
                            application_name,
                            state,
                            query_start,
                            state_change,
                            wait_event_type,
                            wait_event,
                            LEFT(query, 100) as query_snippet
                        FROM pg_stat_activity
                        WHERE state != 'idle'
                        AND pid != pg_backend_pid()
                        ORDER BY query_start
                    """)

                    result = await db.execute(query)
                    queries = result.fetchall()

                    for q in queries:
                        query_info = {
                            'pid': q[0],
                            'user': q[1],
                            'application': q[2],
                            'state': q[3],
                            'query_start': str(q[4]) if q[4] else None,
                            'state_change': str(q[5]) if q[5] else None,
                            'wait_type': q[6],
                            'wait_event': q[7],
                            'query': q[8]
                        }
                        active_queries.append(query_info)

                        # Check for long-running queries
                        if q[4]:
                            duration = datetime.now() - q[4].replace(tzinfo=None)
                            if duration > timedelta(minutes=5):
                                self.warnings.append(f"Long-running query (PID {q[0]}): {duration}")

                    self.results['active_queries'] = {
                        'count': len(active_queries),
                        'queries': active_queries
                    }

                finally:
                    await db.close()
                    break

            return active_queries

        except Exception as e:
            self.results['active_queries'] = {
                'status': 'error',
                'error': str(e)
            }
            return []

    async def check_lock_status(self) -> Dict[str, Any]:
        """Check for blocking locks."""
        try:
            from database.db_setup import get_async_db
            from sqlalchemy import text

            lock_info = {
                'blocking_locks': [],
                'lock_count': 0
            }

            async for db in get_async_db():
                try:
                    query = text("""
                        SELECT
                            blocked_locks.pid AS blocked_pid,
                            blocked_activity.usename AS blocked_user,
                            blocking_locks.pid AS blocking_pid,
                            blocking_activity.usename AS blocking_user,
                            blocked_activity.application_name AS blocked_application,
                            blocking_activity.application_name AS blocking_application,
                            blocked_activity.query_start AS blocked_query_start,
                            LEFT(blocked_activity.query, 50) AS blocked_query,
                            LEFT(blocking_activity.query, 50) AS blocking_query
                        FROM pg_locks blocked_locks
                        JOIN pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
                        JOIN pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
                            AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
                            AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
                            AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
                            AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
                            AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
                            AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
                            AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
                            AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
                            AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
                            AND blocking_locks.pid != blocked_locks.pid
                        JOIN pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
                        WHERE NOT blocked_locks.granted
                    """)

                    result = await db.execute(query)
                    locks = result.fetchall()

                    for lock in locks:
                        lock_detail = {
                            'blocked_pid': lock[0],
                            'blocked_user': lock[1],
                            'blocking_pid': lock[2],
                            'blocking_user': lock[3],
                            'blocked_application': lock[4],
                            'blocking_application': lock[5],
                            'blocked_since': str(lock[6]) if lock[6] else None,
                            'blocked_query': lock[7],
                            'blocking_query': lock[8]
                        }
                        lock_info['blocking_locks'].append(lock_detail)
                        self.issues.append(f"Blocking lock detected: PID {lock[2]} blocking PID {lock[0]}")

                    lock_info['lock_count'] = len(locks)
                    self.results['lock_status'] = lock_info

                finally:
                    await db.close()
                    break

            return lock_info

        except Exception as e:
            self.results['lock_status'] = {
                'status': 'error',
                'error': str(e)
            }
            return {}

    async def check_redis_health(self) -> Dict[str, Any]:
        """Check Redis cache health if configured."""
        try:
            import os
            redis_url = os.getenv('REDIS_URL')

            if not redis_url:
                return {
                    'status': 'not_configured',
                    'message': 'Redis not configured (optional)'
                }

            from database.redis_client import get_redis_client

            redis = await get_redis_client()
            if redis:
                # Ping Redis
                await redis.ping()

                # Get Redis info
                info = await redis.info()

                redis_health = {
                    'status': 'healthy',
                    'connected': True,
                    'version': info.get('redis_version', 'unknown'),
                    'uptime_seconds': info.get('uptime_in_seconds', 0),
                    'connected_clients': info.get('connected_clients', 0),
                    'used_memory': info.get('used_memory_human', 'unknown'),
                    'used_memory_peak': info.get('used_memory_peak_human', 'unknown')
                }

                self.results['redis'] = redis_health
                return redis_health
            else:
                self.results['redis'] = {
                    'status': 'error',
                    'message': 'Redis client initialization failed'
                }
                return {}

        except Exception as e:
            self.results['redis'] = {
                'status': 'error',
                'error': str(e)
            }
            return {}

    async def generate_health_report(self) -> bool:
        """Generate comprehensive health report."""
        logger.info("\n" + "=" * 60)
        logger.info("DATABASE HEALTH CHECK REPORT")
        logger.info("=" * 60)
        logger.info(f"Timestamp: {datetime.now().isoformat()}")

        # Determine overall health status
        if self.issues:
            overall_status = "CRITICAL"
        elif self.warnings:
            overall_status = "WARNING"
        else:
            overall_status = "HEALTHY"

        logger.info(f"\nOverall Status: {overall_status}")

        # Report issues
        if self.issues:
            logger.error("\n--- CRITICAL ISSUES ---")
            for issue in self.issues:
                logger.error(f"  ✗ {issue}")

        # Report warnings
        if self.warnings:
            logger.warning("\n--- WARNINGS ---")
            for warning in self.warnings:
                logger.warning(f"  ⚠ {warning}")

        # Report recommendations
        if self.recommendations:
            logger.info("\n--- RECOMMENDATIONS ---")
            for rec in self.recommendations:
                logger.info(f"  → {rec}")

        # Summary statistics
        logger.info("\n--- SUMMARY ---")
        for component, data in self.results.items():
            if isinstance(data, dict) and 'status' in data:
                status = data['status']
                symbol = "✓" if status in ['healthy', 'connected', 'analyzed'] else "✗"
                logger.info(f"  {symbol} {component}: {status}")

        # Save detailed report
        report_path = PROJECT_ROOT / "database_health_report.json"
        with open(report_path, "w") as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'overall_status': overall_status,
                'issues': self.issues,
                'warnings': self.warnings,
                'recommendations': self.recommendations,
                'detailed_results': self.results
            }, f, indent=2, default=str)

        logger.info(f"\nDetailed report saved to: {report_path}")

        return overall_status == "HEALTHY"

    async def run_health_check(self) -> bool:
        """Run complete database health check."""
        try:
            # Run all health checks
            logger.info("Starting database health check...")

            # 1. Basic connectivity
            logger.info("\n1. Checking database connectivity...")
            await self.check_database_connectivity()

            # 2. Connection pool health
            logger.info("\n2. Checking connection pool health...")
            await self.check_connection_pool_health()

            # 3. Table statistics
            logger.info("\n3. Analyzing table statistics...")
            await self.check_table_statistics()

            # 4. Index usage
            logger.info("\n4. Analyzing index usage...")
            await self.check_index_usage()

            # 5. Active queries
            logger.info("\n5. Checking active queries...")
            await self.check_active_queries()

            # 6. Lock status
            logger.info("\n6. Checking for blocking locks...")
            await self.check_lock_status()

            # 7. Redis health (if configured)
            logger.info("\n7. Checking Redis cache health...")
            await self.check_redis_health()

            # Generate report
            return await self.generate_health_report()

        except Exception as e:
            logger.error(f"Health check failed with error: {str(e)}")
            return False


async def main():
    """Main entry point."""
    checker = DatabaseHealthChecker()
    success = await checker.run_health_check()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())