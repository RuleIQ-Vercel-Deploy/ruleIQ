"""Add ai_metadata JSONB columns to evidence and evidence_items tables

Revision ID: 007
Revises: 006
Create Date: 2025-01-05

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = '007'
down_revision = '006'
branch_labels = None
depends_on = None


def upgrade():
    """Add ai_metadata JSONB columns to evidence and evidence_items tables."""

    # Add ai_metadata column to evidence table
    op.add_column('evidence',
                  sa.Column('ai_metadata', postgresql.JSONB(astext_type=sa.Text()),
                           nullable=True, default=sa.text("'{}'::jsonb")))

    # Add ai_metadata column to evidence_items table
    op.add_column('evidence_items',
                  sa.Column('ai_metadata', postgresql.JSONB(astext_type=sa.Text()),
                           nullable=True, default=sa.text("'{}'::jsonb")))

    # Update existing records to have empty JSON object as default
    op.execute("UPDATE evidence SET ai_metadata = '{}'::jsonb WHERE ai_metadata IS NULL")
    op.execute("UPDATE evidence_items SET ai_metadata = '{}'::jsonb WHERE ai_metadata IS NULL")

    # Create indexes for ai_metadata queries (optional but recommended for performance)
    op.create_index('idx_evidence_ai_metadata', 'evidence', ['ai_metadata'], postgresql_using='gin')
    op.create_index('idx_evidence_items_ai_metadata', 'evidence_items', ['ai_metadata'], postgresql_using='gin')


def downgrade():
    """Remove ai_metadata columns from evidence and evidence_items tables."""

    # Drop indexes first
    op.drop_index('idx_evidence_ai_metadata', 'evidence')
    op.drop_index('idx_evidence_items_ai_metadata', 'evidence_items')

    # Drop ai_metadata columns
    op.drop_column('evidence', 'ai_metadata')
    op.drop_column('evidence_items', 'ai_metadata')
