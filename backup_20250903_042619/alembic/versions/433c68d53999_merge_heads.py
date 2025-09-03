"""merge_heads

Revision ID: 433c68d53999
Revises: add_api_key_tables, aca23a693098
Create Date: 2025-09-02 12:47:15.941777

"""
from alembic import op
import sqlalchemy as sa
revision = '433c68d53999'
down_revision = ('add_api_key_tables', 'aca23a693098')
branch_labels = None
depends_on = None

def upgrade() -> None:
    pass

def downgrade() -> None:
    pass