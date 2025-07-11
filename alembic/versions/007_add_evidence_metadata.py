"""Add ai_metadata JSONB columns to evidence and evidence_items tables

Revision ID: 007
Revises: 006
Create Date: 2025-01-05

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "007"
down_revision = "006"
branch_labels = None
depends_on = None


def upgrade():
    """Add ai_metadata JSONB columns to evidence and evidence_items tables."""

    # Add ai_metadata column to evidence table if it doesn't exist
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='evidence' 
                AND column_name='ai_metadata'
            ) THEN
                ALTER TABLE evidence 
                ADD COLUMN ai_metadata JSONB DEFAULT '{}'::jsonb;
            END IF;
        END $$;
    """)

    # Add ai_metadata column to evidence_items table if it doesn't exist
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='evidence_items' 
                AND column_name='ai_metadata'
            ) THEN
                ALTER TABLE evidence_items 
                ADD COLUMN ai_metadata JSONB DEFAULT '{}'::jsonb;
            END IF;
        END $$;
    """)

    # Update existing records to have empty JSON object as default
    op.execute("UPDATE evidence SET ai_metadata = '{}'::jsonb WHERE ai_metadata IS NULL")
    op.execute("UPDATE evidence_items SET ai_metadata = '{}'::jsonb WHERE ai_metadata IS NULL")

    # Create indexes for ai_metadata queries if they don't exist
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_evidence_ai_metadata 
        ON evidence USING gin (ai_metadata);
    """)
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_evidence_items_ai_metadata 
        ON evidence_items USING gin (ai_metadata);
    """)


def downgrade():
    """Remove ai_metadata columns from evidence and evidence_items tables."""

    # Drop indexes first if they exist
    op.execute("DROP INDEX IF EXISTS idx_evidence_ai_metadata")
    op.execute("DROP INDEX IF EXISTS idx_evidence_items_ai_metadata")

    # Drop ai_metadata columns if they exist
    op.execute("""
        ALTER TABLE evidence DROP COLUMN IF EXISTS ai_metadata;
        ALTER TABLE evidence_items DROP COLUMN IF EXISTS ai_metadata;
    """)
