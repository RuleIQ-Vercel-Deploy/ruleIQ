"""add integration configs table

Revision ID: 004
Revises: 003
Create Date: 2024-01-20

"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade():
    # Create enum type for integration status using raw SQL for better control
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE integrationstatus AS ENUM (
                'connected', 'disconnected', 'error', 'refreshing', 'rate_limited'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Create integration_configs table using raw SQL to avoid enum creation issues
    op.execute("""
        CREATE TABLE integration_configs (
            id UUID NOT NULL,
            user_id UUID NOT NULL,
            provider VARCHAR NOT NULL,
            credentials JSON,
            settings JSON,
            status integrationstatus NOT NULL,
            last_sync TIMESTAMP,
            last_error VARCHAR,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            PRIMARY KEY (id)
        )
    """)

    # Create indices
    op.create_index(
        op.f("ix_integration_configs_user_id"), "integration_configs", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_integration_configs_provider"), "integration_configs", ["provider"], unique=False
    )
    op.create_index("ix_user_provider", "integration_configs", ["user_id", "provider"], unique=True)


def downgrade():
    # Drop indices if they exist
    op.execute("DROP INDEX IF EXISTS ix_user_provider")
    op.execute("DROP INDEX IF EXISTS ix_integration_configs_provider")
    op.execute("DROP INDEX IF EXISTS ix_integration_configs_user_id")
    
    # Drop table
    op.execute("DROP TABLE IF EXISTS integration_configs")

    # Drop enum type if it exists
    op.execute("DROP TYPE IF EXISTS integrationstatus")
