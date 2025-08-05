"""Merge freemium and main branches

Revision ID: b405cc54d9a0
Revises: freemium_001, d354bd6c0c4b
Create Date: 2025-08-05 15:44:40.028805

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b405cc54d9a0'
down_revision = ('freemium_001', 'd354bd6c0c4b')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass