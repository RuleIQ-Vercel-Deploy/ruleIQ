"""
Example data migration script to adapt existing evidence items to the
new schema required by the integration framework.

This script demonstrates how to handle data migrations when adding new
features like automated evidence collection and AI assistant functionality.
"""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_setup import get_db
from database.evidence_item import EvidenceItem
from database.chat_conversation import ChatConversation
from database.chat_message import ChatMessage

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:password@localhost:5432/compliance_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_table_exists(table_name: str) -> bool:
    """Check if a table exists in the database."""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

def add_integration_columns_to_evidence():
    """
    Add new columns to support automated evidence collection.
    
    Note: In production, this should be handled by an Alembic migration.
    This is for demonstration purposes.
    """
    print("Checking evidence_items table schema...")
    
    inspector = inspect(engine)
    if not check_table_exists("evidence_items"):
        print("❌ evidence_items table does not exist. Please run database initialization first.")
        return False
    
    columns = [col['name'] for col in inspector.get_columns("evidence_items")]
    
    new_columns = []
    
    # Check and add automation_source column
    if 'automation_source' not in columns:
        new_columns.append("ADD COLUMN automation_source VARCHAR(50)")
    
    # Check and add auto_collected column
    if 'auto_collected' not in columns:
        new_columns.append("ADD COLUMN auto_collected BOOLEAN DEFAULT FALSE")
    
    # Check and add collection_metadata column
    if 'collection_metadata' not in columns:
        new_columns.append("ADD COLUMN collection_metadata JSONB DEFAULT '{}'::jsonb")
    
    # Check and add quality_score column
    if 'quality_score' not in columns:
        new_columns.append("ADD COLUMN quality_score FLOAT")
    
    if new_columns:
        ddl = f"ALTER TABLE evidence_items {', '.join(new_columns)};"
        print(f"Adding new columns: {', '.join(new_columns)}")
        
        try:
            with engine.connect() as conn:
                conn.execute(text(ddl))
                conn.commit()
            print("✅ Successfully added new columns to evidence_items table")
            return True
        except Exception as e:
            print(f"❌ Error adding columns: {e}")
            return False
    else:
        print("✅ All required columns already exist in evidence_items table")
        return True

def create_chat_tables():
    """
    Create chat conversation and message tables if they don't exist.
    
    Note: In production, this should be handled by an Alembic migration.
    """
    print("Checking chat tables...")
    
    # Create chat_conversations table
    if not check_table_exists("chat_conversations"):
        print("Creating chat_conversations table...")
        ddl = """
        CREATE TABLE chat_conversations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES users(id),
            business_profile_id UUID NOT NULL REFERENCES business_profiles(id),
            title VARCHAR(255) NOT NULL,
            status VARCHAR(20) DEFAULT 'active' NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
        );
        """
        
        try:
            with engine.connect() as conn:
                conn.execute(text(ddl))
                conn.commit()
            print("✅ Successfully created chat_conversations table")
        except Exception as e:
            print(f"❌ Error creating chat_conversations table: {e}")
            return False
    
    # Create chat_messages table
    if not check_table_exists("chat_messages"):
        print("Creating chat_messages table...")
        ddl = """
        CREATE TABLE chat_messages (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            conversation_id UUID NOT NULL REFERENCES chat_conversations(id) ON DELETE CASCADE,
            role VARCHAR(20) NOT NULL,
            content TEXT NOT NULL,
            metadata JSONB DEFAULT '{}'::jsonb,
            sequence_number INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
        );
        """
        
        try:
            with engine.connect() as conn:
                conn.execute(text(ddl))
                conn.commit()
            print("✅ Successfully created chat_messages table")
        except Exception as e:
            print(f"❌ Error creating chat_messages table: {e}")
            return False
    
    print("✅ Chat tables are ready")
    return True

def backfill_existing_evidence():
    """
    Updates existing, manually-added evidence to conform to the new schema.
    """
    print("Backfilling existing evidence items...")
    
    try:
        db = SessionLocal()
        
        # Update evidence items that don't have automation_source set
        updated_count = 0
        evidence_items = db.query(EvidenceItem).filter(
            EvidenceItem.automation_source.is_(None)
        ).all()
        
        for item in evidence_items:
            item.automation_source = 'manual'
            item.auto_collected = False
            
            # Set default collection metadata
            if not item.collection_metadata:
                item.collection_metadata = {
                    "migrated": True,
                    "migration_date": datetime.utcnow().isoformat(),
                    "original_source": "manual_entry"
                }
            
            updated_count += 1
        
        db.commit()
        print(f"✅ Updated {updated_count} existing evidence items")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during evidence backfill: {e}")
        if db:
            db.rollback()
        return False
    finally:
        if db:
            db.close()

def add_indexes_for_performance():
    """
    Add database indexes to improve query performance for new features.
    """
    print("Adding performance indexes...")
    
    indexes = [
        # Evidence table indexes
        "CREATE INDEX IF NOT EXISTS idx_evidence_automation_source ON evidence_items(automation_source)",
        "CREATE INDEX IF NOT EXISTS idx_evidence_auto_collected ON evidence_items(auto_collected)",
        "CREATE INDEX IF NOT EXISTS idx_evidence_quality_score ON evidence_items(quality_score)",
        "CREATE INDEX IF NOT EXISTS idx_evidence_user_created ON evidence_items(user_id, created_at)",
        
        # Chat table indexes
        "CREATE INDEX IF NOT EXISTS idx_chat_conversations_user ON chat_conversations(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_chat_conversations_profile ON chat_conversations(business_profile_id)",
        "CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation ON chat_messages(conversation_id)",
        "CREATE INDEX IF NOT EXISTS idx_chat_messages_sequence ON chat_messages(conversation_id, sequence_number)",
    ]
    
    try:
        with engine.connect() as conn:
            for index_sql in indexes:
                conn.execute(text(index_sql))
            conn.commit()
        
        print(f"✅ Successfully added {len(indexes)} performance indexes")
        return True
        
    except Exception as e:
        print(f"❌ Error adding indexes: {e}")
        return False

def verify_migration():
    """
    Verify that the migration completed successfully.
    """
    print("Verifying migration...")
    
    try:
        db = SessionLocal()
        
        # Check evidence items with new fields
        evidence_count = db.query(EvidenceItem).count()
        automated_count = db.query(EvidenceItem).filter(
            EvidenceItem.auto_collected == True
        ).count()
        manual_count = db.query(EvidenceItem).filter(
            EvidenceItem.automation_source == 'manual'
        ).count()
        
        print(f"📊 Evidence items: {evidence_count} total, {automated_count} automated, {manual_count} manual")
        
        # Check chat tables
        if check_table_exists("chat_conversations"):
            conversation_count = db.query(ChatConversation).count()
            print(f"📊 Chat conversations: {conversation_count}")
        
        if check_table_exists("chat_messages"):
            message_count = db.query(ChatMessage).count()
            print(f"📊 Chat messages: {message_count}")
        
        print("✅ Migration verification completed")
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False
    finally:
        if db:
            db.close()

def create_alembic_migration_template():
    """
    Create a template for an Alembic migration that includes all our changes.
    """
    template = '''"""Add support for evidence automation and AI chat

Revision ID: 005_add_automation_features
Revises: 004_add_integration_configs
Create Date: {create_date}

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_add_automation_features'
down_revision = '004_add_integration_configs'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Add automation columns to evidence_items
    op.add_column('evidence_items', sa.Column('automation_source', sa.String(50), nullable=True))
    op.add_column('evidence_items', sa.Column('auto_collected', sa.Boolean(), default=False))
    op.add_column('evidence_items', sa.Column('collection_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('evidence_items', sa.Column('quality_score', sa.Float(), nullable=True))

    # Create chat_conversations table
    op.create_table('chat_conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('business_profile_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('business_profiles.id'), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('status', sa.String(20), default='active', nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime, default=sa.func.now(), nullable=False),
    )

    # Create chat_messages table
    op.create_table('chat_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('chat_conversations.id', ondelete='CASCADE'), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('sequence_number', sa.Integer, nullable=False),
        sa.Column('created_at', sa.DateTime, default=sa.func.now(), nullable=False),
    )

    # Add indexes for performance
    op.create_index('idx_evidence_automation_source', 'evidence_items', ['automation_source'])
    op.create_index('idx_evidence_auto_collected', 'evidence_items', ['auto_collected'])
    op.create_index('idx_evidence_quality_score', 'evidence_items', ['quality_score'])
    op.create_index('idx_chat_conversations_user', 'chat_conversations', ['user_id'])
    op.create_index('idx_chat_messages_conversation', 'chat_messages', ['conversation_id'])

def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_chat_messages_conversation')
    op.drop_index('idx_chat_conversations_user')
    op.drop_index('idx_evidence_quality_score')
    op.drop_index('idx_evidence_auto_collected')
    op.drop_index('idx_evidence_automation_source')
    
    # Drop tables
    op.drop_table('chat_messages')
    op.drop_table('chat_conversations')
    
    # Drop columns
    op.drop_column('evidence_items', 'quality_score')
    op.drop_column('evidence_items', 'collection_metadata')
    op.drop_column('evidence_items', 'auto_collected')
    op.drop_column('evidence_items', 'automation_source')
'''.format(create_date=datetime.utcnow().isoformat())
    
    migration_file = "/home/omar/Documents/Experiment/alembic/versions/005_add_automation_features.py"
    
    try:
        with open(migration_file, 'w') as f:
            f.write(template)
        print(f"✅ Created Alembic migration template: {migration_file}")
        print("   Run 'alembic upgrade head' to apply the migration")
        return True
    except Exception as e:
        print(f"❌ Error creating migration template: {e}")
        return False

def main():
    """
    Main migration function that runs all migration steps.
    """
    print("🚀 Starting ComplianceGPT database migration...")
    print("=" * 60)
    
    success = True
    
    # Step 1: Add new columns to evidence table
    if not add_integration_columns_to_evidence():
        success = False
    
    print()
    
    # Step 2: Create chat tables
    if not create_chat_tables():
        success = False
    
    print()
    
    # Step 3: Backfill existing data
    if not backfill_existing_evidence():
        success = False
    
    print()
    
    # Step 4: Add performance indexes
    if not add_indexes_for_performance():
        success = False
    
    print()
    
    # Step 5: Verify migration
    if not verify_migration():
        success = False
    
    print()
    
    # Step 6: Create Alembic migration template
    if not create_alembic_migration_template():
        success = False
    
    print()
    print("=" * 60)
    
    if success:
        print("✅ Database migration completed successfully!")
        print()
        print("Next steps:")
        print("1. Review the generated Alembic migration file")
        print("2. Test the migration in a development environment")
        print("3. Run 'alembic upgrade head' to apply migrations")
        print("4. Update your application to use the new features")
    else:
        print("❌ Database migration encountered errors!")
        print("Please review the error messages above and fix any issues.")
    
    return success

if __name__ == "__main__":
    print("This is a demonstration script for database migration.")
    print("In production, use Alembic for schema migrations.")
    print()
    
    # Ask for confirmation before running
    response = input("Do you want to run the migration? (y/N): ")
    if response.lower() in ['y', 'yes']:
        main()
    else:
        print("Migration cancelled.")
        
        # Still create the Alembic template
        print("Creating Alembic migration template only...")
        create_alembic_migration_template()