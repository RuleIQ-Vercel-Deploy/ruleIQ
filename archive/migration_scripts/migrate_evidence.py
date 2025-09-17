"""
from __future__ import annotations

Asynchronous data migration script to adapt existing evidence items to the
new schema required by the integration framework.

This script demonstrates how to handle data migrations when adding new
features like automated evidence collection and AI assistant functionality.
"""
import asyncio
import os
import sys
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncInspector, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.logging_config import get_logger, setup_logging
from database.chat_conversation import ChatConversation
from database.chat_message import ChatMessage
from database.db_setup import Base
from typing import Optional, Any
setup_logging()
logger = get_logger(__name__)
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    logger.error('DATABASE_URL environment variable not set. Please set it for asyncpg.')
    sys.exit(1)
async_engine = create_async_engine(DATABASE_URL)
AsyncSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)

async def check_table_exists(table_name: str) -> bool:
    """Check if a table exists in the database asynchronously."""
    try:
        async_inspector = await AsyncInspector.from_engine(async_engine)
        tables = await async_inspector.get_table_names()
        return table_name in tables
    except Exception as e:
        logger.error(f'Error checking if table {table_name} exists: {e}', exc_info=True)
        return False

async def add_integration_columns_to_evidence() -> Optional[bool]:
    """Add new columns to support automated evidence collection asynchronously."""
    logger.info('Checking evidence_items table schema...')
    if not await check_table_exists('evidence_items'):
        logger.error('evidence_items table does not exist. Please run database initialization first.')
        return False
    try:
        async_inspector = await AsyncInspector.from_engine(async_engine)
        columns_info = await async_inspector.get_columns('evidence_items')
        columns = [col['name'] for col in columns_info]
        ddl_statements = []
        if 'automation_source' not in columns:
            ddl_statements.append('ALTER TABLE evidence_items ADD COLUMN automation_source VARCHAR(50)')
        if 'auto_collected' not in columns:
            ddl_statements.append('ALTER TABLE evidence_items ADD COLUMN auto_collected BOOLEAN DEFAULT FALSE')
        if 'collection_details' not in columns:
            ddl_statements.append('ALTER TABLE evidence_items ADD COLUMN collection_details JSONB')
        if 'last_verified_at' not in columns:
            ddl_statements.append('ALTER TABLE evidence_items ADD COLUMN last_verified_at TIMESTAMP WITHOUT TIME ZONE')
        if ddl_statements:
            async with async_engine.connect() as conn:
                for stmt in ddl_statements:
                    logger.info(f'Executing DDL: {stmt}')
                    await conn.execute(text(stmt))
                await conn.commit()
            logger.info('Integration columns added/verified in evidence_items table.')
        else:
            logger.info('All integration columns already exist in evidence_items table.')
        return True
    except Exception as e:
        logger.error(f'Error adding integration columns to evidence_items: {e}', exc_info=True)
        return False

async def create_chat_tables() -> Optional[bool]:
    """Create chat_conversations and chat_messages tables asynchronously if they don't exist."""
    logger.info('Checking and creating chat tables...')
    try:
        tables_to_create = []
        if not await check_table_exists(ChatConversation.__tablename__):
            tables_to_create.append(ChatConversation.__table__)
        if not await check_table_exists(ChatMessage.__tablename__):
            tables_to_create.append(ChatMessage.__table__)
        if tables_to_create:
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all, tables=tables_to_create)
            logger.info('Chat tables created/verified successfully.')
        else:
            logger.info('Chat tables already exist.')
        return True
    except Exception as e:
        logger.error(f'Error creating chat tables: {e}', exc_info=True)
        return False

async def backfill_existing_evidence() -> Optional[bool]:
    """Backfill existing evidence items with default values for new columns asynchronously."""
    logger.info('Backfilling existing evidence items...')
    try:
        async with AsyncSessionLocal() as session:
            stmt = text('UPDATE evidence_items SET automation_source = \'manual\', auto_collected = FALSE, collection_details = \'{"method": "manual_migration"}\'::jsonb WHERE automation_source IS NULL')
            result = await session.execute(stmt)
            await session.commit()
            logger.info(f'{result.rowcount} evidence items backfilled with default integration data.')
        return True
    except Exception as e:
        logger.error(f'Error backfilling evidence data: {e}', exc_info=True)
        return False

async def add_indexes_for_performance() -> Optional[bool]:
    """Add indexes to new columns for performance asynchronously."""
    logger.info('Adding performance indexes...')
    indexes_ddl = ['CREATE INDEX IF NOT EXISTS idx_evidence_automation_source ON evidence_items (automation_source);', 'CREATE INDEX IF NOT EXISTS idx_evidence_auto_collected ON evidence_items (auto_collected);', 'CREATE INDEX IF NOT EXISTS idx_chat_conversations_user_id ON chat_conversations (user_id);', 'CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation_id ON chat_messages (conversation_id);']
    try:
        async with async_engine.connect() as conn:
            for stmt in indexes_ddl:
                logger.info(f'Executing DDL: {stmt}')
                await conn.execute(text(stmt))
            await conn.commit()
        logger.info('Performance indexes added/verified.')
        return True
    except Exception as e:
        logger.error(f'Error adding performance indexes: {e}', exc_info=True)
        return False

async def verify_migration() -> bool:
    """Verify that the migration steps were successful asynchronously."""
    logger.info('Verifying migration...')
    if not await check_table_exists('chat_conversations') or not await check_table_exists('chat_messages'):
        logger.error('Chat tables not found post-migration.')
        return False
    logger.info('Migration verification checks passed (basic). Add more specific checks as needed.')
    return True

def create_alembic_migration_template() -> Optional[bool]:
    """Creates a template for an Alembic migration script."""
    logger.info('Creating Alembic migration template (alembic_migration_template.txt)...')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    template_content = f'''from alembic import op\nimport sqlalchemy as sa\nfrom sqlalchemy.dialects import postgresql\n\n# revision identifiers, used by Alembic.\nrevision = '{timestamp}_add_integration_features'\ndown_revision = 'PREVIOUS_REVISION_HERE' # Set this to your last migration's revision\nbranch_labels = None\ndepends_on = None\n\ndef upgrade():\n    # ### commands auto generated by Alembic - please adjust! ###\n    op.add_column('evidence_items', sa.Column('automation_source', sa.String(length=50), nullable=True))\n    op.add_column('evidence_items', sa.Column('auto_collected', sa.Boolean(), server_default=sa.text('false'), nullable=True))\n    op.add_column('evidence_items', sa.Column('collection_details', postgresql.JSONB(astext_type=sa.Text()), nullable=True))\n    op.add_column('evidence_items', sa.Column('last_verified_at', sa.TIMESTAMP(), nullable=True))\n\n    op.create_table('chat_conversations',\n        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),\n        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),\n        sa.Column('title', sa.String(length=255), nullable=True),\n        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),\n        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),\n        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),\n        sa.PrimaryKeyConstraint('id')\n    )\n    op.create_index(op.f('ix_chat_conversations_user_id'), 'chat_conversations', ['user_id'], unique=False)\n\n    op.create_table('chat_messages',\n        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),\n        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),\n        sa.Column('sender_type', sa.String(length=50), nullable=False),\n        sa.Column('content', sa.Text(), nullable=False),\n        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),\n        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),\n        sa.ForeignKeyConstraint(['conversation_id'], ['chat_conversations.id'], ),\n        sa.PrimaryKeyConstraint('id')\n    )\n    op.create_index(op.f('ix_chat_messages_conversation_id'), 'chat_messages', ['conversation_id'], unique=False)\n\n    # Backfill data (example)\n    op.execute("""\n        UPDATE evidence_items\n        SET automation_source = 'manual', auto_collected = FALSE,\n            collection_details = '{{"method": "manual_migration"}}'::jsonb\n        WHERE automation_source IS NULL;\n    """)\n\n    # Add indexes\n    op.create_index('idx_evidence_automation_source', 'evidence_items', ['automation_source'], unique=False)\n    op.create_index('idx_evidence_auto_collected', 'evidence_items', ['auto_collected'], unique=False)\n    # ### end Alembic commands ###\n\ndef downgrade():\n    # ### commands auto generated by Alembic - please adjust! ###\n    op.drop_index('idx_evidence_auto_collected', table_name='evidence_items')\n    op.drop_index('idx_evidence_automation_source', table_name='evidence_items')\n\n    op.drop_index(op.f('ix_chat_messages_conversation_id'), table_name='chat_messages')\n    op.drop_table('chat_messages')\n    op.drop_index(op.f('ix_chat_conversations_user_id'), table_name='chat_conversations')\n    op.drop_table('chat_conversations')\n\n    op.drop_column('evidence_items', 'last_verified_at')\n    op.drop_column('evidence_items', 'collection_details')\n    op.drop_column('evidence_items', 'auto_collected')\n    op.drop_column('evidence_items', 'automation_source')\n    # ### end Alembic commands ###\n'''
    try:
        with open('alembic_migration_template.txt', 'w') as f:
            f.write(template_content)
        logger.info('Alembic migration template created successfully.')
        return True
    except OSError as e:
        logger.error(f'Failed to write Alembic template: {e}', exc_info=True)
        return False

async def main_async() -> Any:
    """Main asynchronous migration function."""
    logger.info('Starting ComplianceGPT database migration (Async)...')
    logger.info('=' * 60)
    success = True
    if not await add_integration_columns_to_evidence():
        success = False
    if not await create_chat_tables():
        success = False
    if not await backfill_existing_evidence():
        success = False
    if not await add_indexes_for_performance():
        success = False
    if not await verify_migration():
        success = False
    if not create_alembic_migration_template():
        success = False
    logger.info('=' * 60)
    if success:
        logger.info('Database migration completed successfully!')
        logger.info("Next steps: Review alembic_migration_template.txt, test, and run 'alembic upgrade head'.")
    else:
        logger.error('Database migration encountered errors! Review logs.')
    return success
if __name__ == '__main__':
    logger.info('This is a demonstration script for database migration.')
    logger.info('In production, use Alembic for schema migrations.')
    response = input('Do you want to run the migration? (y/N): ')
    if response.lower() in ['y', 'yes']:
        asyncio.run(main_async())
    else:
        logger.info('Migration cancelled by user.')
        logger.info('Creating Alembic migration template only...')
        create_alembic_migration_template()
