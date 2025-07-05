"""add data_sensitivity field to business_profiles

Revision ID: 005
Revises: 004
Create Date: 2025-01-21

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    """Add data_sensitivity column to business_profiles table."""
    # Add data_sensitivity column with default value 'Low'
    op.add_column('business_profiles', 
                  sa.Column('data_sensitivity', sa.String(), nullable=True, default='Low'))
    
    # Update existing records to have the default value
    op.execute("UPDATE business_profiles SET data_sensitivity = 'Low' WHERE data_sensitivity IS NULL")
    
    # Make the column non-nullable after setting default values
    op.alter_column('business_profiles', 'data_sensitivity', nullable=False)


def downgrade():
    """Remove data_sensitivity column from business_profiles table."""
    op.drop_column('business_profiles', 'data_sensitivity')
