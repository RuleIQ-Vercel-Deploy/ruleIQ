"""Base schema setup

Revision ID: 002
Revises: 001
Create Date: 2024-01-10

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Setup base schema."""
    pass  # Base schema is managed by the application


def downgrade():
    """Remove base schema."""
    pass  # Base schema is managed by the application
