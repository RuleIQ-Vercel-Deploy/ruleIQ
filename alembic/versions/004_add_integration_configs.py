"""add integration configs table

Revision ID: 004
Revises: 003
Create Date: 2024-01-20

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Create enum type for integration status
    integration_status_enum = postgresql.ENUM(
        'connected', 'disconnected', 'error', 'refreshing', 'rate_limited',
        name='integrationstatus'
    )
    integration_status_enum.create(op.get_bind())

    # Create integration_configs table
    op.create_table('integration_configs',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('credentials', sa.JSON(), nullable=True),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('status', integration_status_enum, nullable=False),
        sa.Column('last_sync', sa.DateTime(), nullable=True),
        sa.Column('last_error', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indices
    op.create_index(op.f('ix_integration_configs_user_id'), 'integration_configs', ['user_id'], unique=False)
    op.create_index(op.f('ix_integration_configs_provider'), 'integration_configs', ['provider'], unique=False)
    op.create_index('ix_user_provider', 'integration_configs', ['user_id', 'provider'], unique=True)


def downgrade():
    op.drop_index('ix_user_provider', table_name='integration_configs')
    op.drop_index(op.f('ix_integration_configs_provider'), table_name='integration_configs')
    op.drop_index(op.f('ix_integration_configs_user_id'), table_name='integration_configs')
    op.drop_table('integration_configs')

    # Drop enum type
    integration_status_enum = postgresql.ENUM(
        'connected', 'disconnected', 'error', 'refreshing', 'rate_limited',
        name='integrationstatus'
    )
    integration_status_enum.drop(op.get_bind())
