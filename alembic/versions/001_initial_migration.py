"""Initial migration - create base tables

Revision ID: 001
Revises:
Create Date: 2024-01-01

"""

# revision identifiers, used by Alembic.
revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Create initial tables."""
    pass  # Tables are created by the application initialization


def downgrade():
    """Drop initial tables."""
    pass  # Tables are managed by the application
