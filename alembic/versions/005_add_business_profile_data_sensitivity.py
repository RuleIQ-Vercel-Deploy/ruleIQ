"""add data_sensitivity field to business_profiles

Revision ID: 005
Revises: 004
Create Date: 2025-01-21

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade():
    """Add data_sensitivity column to business_profiles table."""
    # Check if column already exists
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name='business_profiles' 
                AND column_name='data_sensitivity'
            ) THEN
                ALTER TABLE business_profiles 
                ADD COLUMN data_sensitivity VARCHAR DEFAULT 'Low';
                
                -- Update existing records to have the default value
                UPDATE business_profiles 
                SET data_sensitivity = 'Low' 
                WHERE data_sensitivity IS NULL;
                
                -- Make the column non-nullable after setting default values
                ALTER TABLE business_profiles 
                ALTER COLUMN data_sensitivity SET NOT NULL;
            END IF;
        END $$;
    """)


def downgrade():
    """Remove data_sensitivity column from business_profiles table."""
    op.drop_column("business_profiles", "data_sensitivity")
