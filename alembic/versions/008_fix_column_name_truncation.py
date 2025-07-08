"""Fix column name truncation in business_profiles table

Revision ID: 008
Revises: 007
Create Date: 2025-01-07

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    """Fix truncated column names in business_profiles table."""
    
    # Rename truncated columns to their full names
    op.alter_column('business_profiles', 'handles_persona', new_column_name='handles_personal_data')
    op.alter_column('business_profiles', 'processes_payme', new_column_name='processes_payments')
    op.alter_column('business_profiles', 'stores_health_d', new_column_name='stores_health_data')
    op.alter_column('business_profiles', 'provides_financ', new_column_name='provides_financial_services')
    op.alter_column('business_profiles', 'operates_critic', new_column_name='operates_critical_infrastructure')
    op.alter_column('business_profiles', 'has_internation', new_column_name='has_international_operations')
    op.alter_column('business_profiles', 'development_too', new_column_name='development_tools')
    op.alter_column('business_profiles', 'existing_framew', new_column_name='existing_frameworks')
    op.alter_column('business_profiles', 'planned_framewo', new_column_name='planned_frameworks')
    op.alter_column('business_profiles', 'compliance_budg', new_column_name='compliance_budget')
    op.alter_column('business_profiles', 'compliance_time', new_column_name='compliance_timeline')
    op.alter_column('business_profiles', 'assessment_comp', new_column_name='assessment_completed')


def downgrade():
    """Revert column names back to truncated versions."""
    
    # Revert column names to truncated versions
    op.alter_column('business_profiles', 'handles_personal_data', new_column_name='handles_persona')
    op.alter_column('business_profiles', 'processes_payments', new_column_name='processes_payme')
    op.alter_column('business_profiles', 'stores_health_data', new_column_name='stores_health_d')
    op.alter_column('business_profiles', 'provides_financial_services', new_column_name='provides_financ')
    op.alter_column('business_profiles', 'operates_critical_infrastructure', new_column_name='operates_critic')
    op.alter_column('business_profiles', 'has_international_operations', new_column_name='has_internation')
    op.alter_column('business_profiles', 'development_tools', new_column_name='development_too')
    op.alter_column('business_profiles', 'existing_frameworks', new_column_name='existing_framew')
    op.alter_column('business_profiles', 'planned_frameworks', new_column_name='planned_framewo')
    op.alter_column('business_profiles', 'compliance_budget', new_column_name='compliance_budg')
    op.alter_column('business_profiles', 'compliance_timeline', new_column_name='compliance_time')
    op.alter_column('business_profiles', 'assessment_completed', new_column_name='assessment_comp')