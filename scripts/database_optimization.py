"""
from __future__ import annotations

Database Optimization Script for ruleIQ

This script creates missing indexes identified in the comprehensive analysis
to improve query performance across the application.

Usage:
    python scripts/database_optimization.py

Environment Variables:
    DATABASE_URL: PostgreSQL connection string
    DRY_RUN: Set to 'true' to see what would be created without executing
"""
import os
import sys
import asyncio
from typing import List, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.logging_config import get_logger
logger = get_logger(__name__)

class DatabaseOptimizer:
    """
    Database optimization manager for creating missing indexes
    and improving query performance.
    """

    def __init__(self, database_url: str, dry_run: bool=False) ->None:
        """
        Initialize the database optimizer.

        Args:
            database_url: PostgreSQL connection string
            dry_run: If True, only print what would be executed
        """
        self.database_url = database_url
        self.dry_run = dry_run
        self.engine = create_async_engine(database_url, echo=False)
        self.session_factory = sessionmaker(bind=self.engine, class_=
            AsyncSession, expire_on_commit=False)
        self.indexes = {'high_priority': [{'name':
            'idx_evidence_user_framework_status', 'table': 'evidence_items',
            'columns': ['user_id', 'framework_id', 'status'], 'description':
            'Composite index for evidence filtering and pagination'}, {
            'name': 'idx_evidence_user_status_created', 'table':
            'evidence_items', 'columns': ['user_id', 'status',
            'created_at DESC'], 'description':
            'Index for evidence dashboard sorting'}, {'name':
            'idx_evidence_user_status_updated', 'table': 'evidence_items',
            'columns': ['user_id', 'status', 'updated_at DESC'],
            'description': 'Index for evidence recent updates'}, {'name':
            'idx_evidence_name_trgm', 'table': 'evidence_items', 'columns':
            ['evidence_name'], 'type': 'gin', 'ops': 'gin_trgm_ops',
            'description': 'Trigram index for evidence name search'}, {
            'name': 'idx_evidence_description_trgm', 'table':
            'evidence_items', 'columns': ['description'], 'type': 'gin',
            'ops': 'gin_trgm_ops', 'description':
            'Trigram index for evidence description search'}, {'name':
            'idx_assessment_user_status_created', 'table':
            'assessment_sessions', 'columns': ['user_id', 'status',
            'created_at DESC'], 'description':
            'Index for assessment session queries'}], 'medium_priority': [{
            'name': 'idx_evidence_user_type_status', 'table':
            'evidence_items', 'columns': ['user_id', 'evidence_type',
            'status'], 'description': 'Index for evidence type filtering'},
            {'name': 'idx_evidence_control_reference', 'table':
            'evidence_items', 'columns': ['control_reference'],
            'description': 'Index for control reference lookups'}, {'name':
            'idx_evidence_dashboard_query', 'table': 'evidence_items',
            'columns': ['user_id', 'framework_id', 'status',
            'updated_at DESC'], 'description':
            'Composite index for evidence dashboard queries'}, {'name':
            'idx_chat_conversations_user_status', 'table':
            'chat_conversations', 'columns': ['user_id', 'status'],
            'description': 'Index for chat conversation filtering'}, {
            'name': 'idx_chat_conversations_user_updated', 'table':
            'chat_conversations', 'columns': ['user_id', 'updated_at DESC'],
            'description': 'Index for recent chat conversations'}, {'name':
            'idx_chat_messages_conversation_created', 'table':
            'chat_messages', 'columns': ['conversation_id',
            'created_at DESC'], 'description':
            'Index for chat message ordering'}, {'name':
            'idx_business_profile_company_name_trgm', 'table':
            'business_profiles', 'columns': ['company_name'], 'type': 'gin',
            'ops': 'gin_trgm_ops', 'description':
            'Trigram index for company name search'}], 'low_priority': [{
            'name': 'idx_assessment_questions_session_id', 'table':
            'assessment_questions', 'columns': ['session_id'],
            'description': 'Foreign key index for assessment questions'}, {
            'name': 'idx_generated_policies_user_id', 'table':
            'generated_policies', 'columns': ['user_id'], 'description':
            'Foreign key index for generated policies'}, {'name':
            'idx_generated_policies_business_profil', 'table':
            'generated_policies', 'columns': ['business_profil'],
            'description':
            'Foreign key index for business profile in policies'}, {'name':
            'idx_generated_policies_framework_id', 'table':
            'generated_policies', 'columns': ['framework_id'],
            'description': 'Foreign key index for framework in policies'},
            {'name': 'idx_assessment_business_profil_status', 'table':
            'assessment_sessions', 'columns': ['business_profil', 'status'],
            'description':
            'Index for assessment business profile filtering'}, {'name':
            'idx_assessment_questions_session_sequence', 'table':
            'assessment_questions', 'columns': ['session_id',
            'sequence_number'], 'description':
            'Index for assessment question ordering'}]}
        self.extensions = ['pg_trgm', 'btree_gin']

    async def check_index_exists(self, session: AsyncSession, index_name: str
        ) ->bool:
        """Check if an index already exists."""
        query = text(
            """
            SELECT EXISTS (
                SELECT 1 FROM pg_indexes
                WHERE indexname = :index_name,
            )
        """,
            )
        result = await session.execute(query, {'index_name': index_name})
        return result.scalar()

    async def check_table_exists(self, session: AsyncSession, table_name: str
        ) ->bool:
        """Check if a table exists."""
        query = text(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_name = :table_name,
            )
        """,
            )
        result = await session.execute(query, {'table_name': table_name})
        return result.scalar()

    async def create_extensions(self, session: AsyncSession) ->None:
        """Create required PostgreSQL extensions."""
        logger.info('Creating required PostgreSQL extensions...')
        for extension in self.extensions:
            try:
                query = text(f'CREATE EXTENSION IF NOT EXISTS {extension}')
                if self.dry_run:
                    logger.info('[DRY RUN] Would create extension: %s' %
                        extension)
                else:
                    await session.execute(query)
                    logger.info('✓ Created extension: %s' % extension)
            except Exception as e:
                logger.error('Failed to create extension %s: %s' % (
                    extension, e))
                raise

    async def create_index(self, session: AsyncSession, index_def: Dict[str,
        Any]) ->bool:
        """Create a single index."""
        name = index_def['name']
        table = index_def['table']
        columns = index_def['columns']
        index_type = index_def.get('type', 'btree')
        ops = index_def.get('ops', '')
        description = index_def.get('description', '')
        if not await self.check_table_exists(session, table):
            logger.warning('Table %s does not exist, skipping index %s' % (
                table, name))
            return False
        if await self.check_index_exists(session, name):
            logger.info('Index %s already exists, skipping' % name)
            return True
        if index_type == 'gin' and ops:
            columns_str = ', '.join([(f'{col} {ops}' if col == columns[0] else
                col) for col in columns])
            query = (
                f'CREATE INDEX CONCURRENTLY IF NOT EXISTS {name} ON {table} USING gin ({columns_str})',
                )
        else:
            columns_str = ', '.join(columns)
            query = (
                f'CREATE INDEX CONCURRENTLY IF NOT EXISTS {name} ON {table} ({columns_str})',
                )
        try:
            if self.dry_run:
                logger.info('[DRY RUN] Would create index: %s' % name)
                logger.info('[DRY RUN] Query: %s' % query)
                logger.info('[DRY RUN] Description: %s' % description)
            else:
                logger.info('Creating index: %s' % name)
                logger.info('Description: %s' % description)
                await session.execute(text(query))
                logger.info('✓ Created index: %s' % name)
            return True
        except Exception as e:
            logger.error('Failed to create index %s: %s' % (name, e))
            return False

    async def analyze_tables(self, session: AsyncSession) ->None:
        """Update table statistics after creating indexes."""
        tables = ['evidence_items', 'assessment_sessions',
            'assessment_questions', 'business_profiles',
            'chat_conversations', 'chat_messages', 'generated_policies']
        logger.info('Updating table statistics...')
        for table in tables:
            if await self.check_table_exists(session, table):
                try:
                    query = text(f'ANALYZE {table}')
                    if self.dry_run:
                        logger.info('[DRY RUN] Would analyze table: %s' % table,
                            )
                    else:
                        await session.execute(query)
                        logger.info('✓ Analyzed table: %s' % table)
                except Exception as e:
                    logger.error('Failed to analyze table %s: %s' % (table, e))

    async def optimize_database(self, priority_levels: List[str]=None) ->None:
        """
        Run the complete database optimization process.

        Args:
            priority_levels: List of priority levels to process ('high_priority', 'medium_priority', 'low_priority')
        """
        if priority_levels is None:
            priority_levels = ['high_priority', 'medium_priority',
                'low_priority']
        logger.info('Starting database optimization (dry_run=%s)' % self.
            dry_run)
        logger.info('Processing priority levels: %s' % priority_levels)
        async with self.session_factory() as session:
            try:
                await self.create_extensions(session)
                await session.commit()
                total_created = 0
                total_attempted = 0
                for priority in priority_levels:
                    if priority not in self.indexes:
                        logger.warning('Unknown priority level: %s' % priority)
                        continue
                    logger.info('\n=== Processing %s indexes ===' % priority)
                    for index_def in self.indexes[priority]:
                        total_attempted += 1
                        success = await self.create_index(session, index_def)
                        if success:
                            total_created += 1
                if not self.dry_run:
                    await session.commit()
                await self.analyze_tables(session)
                if not self.dry_run:
                    await session.commit()
                logger.info('\n=== Optimization Complete ===')
                logger.info('Total indexes attempted: %s' % total_attempted)
                logger.info('Total indexes created: %s' % total_created)
                if self.dry_run:
                    logger.info('DRY RUN: No changes were made to the database',
                        )
                else:
                    logger.info('Database optimization completed successfully')
            except Exception as e:
                logger.error('Database optimization failed: %s' % e)
                await session.rollback()
                raise

    async def close(self) ->None:
        """Close the database connection."""
        await self.engine.dispose()

async def main() ->None:
    """Main entry point for the database optimization script."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error('DATABASE_URL environment variable not set')
        sys.exit(1)
    if '+asyncpg' not in database_url:
        if '+psycopg2' in database_url:
            database_url = database_url.replace('+psycopg2', '+asyncpg')
        elif 'postgresql://' in database_url:
            database_url = database_url.replace('postgresql://',
                'postgresql+asyncpg://')
    dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
    priority_levels = ['high_priority', 'medium_priority', 'low_priority']
    if len(sys.argv) > 1:
        priority_levels = sys.argv[1:]
    optimizer = DatabaseOptimizer(database_url, dry_run=dry_run)
    try:
        await optimizer.optimize_database(priority_levels)
    except Exception as e:
        logger.error('Optimization failed: %s' % e)
        sys.exit(1)
    finally:
        await optimizer.close()

if __name__ == '__main__':
    asyncio.run(main())
