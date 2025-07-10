"""Fix column name truncation in assessment_sessions table

Revision ID: 009
Revises: 008
Create Date: 2025-01-09

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade():
    """Fix truncated column names in assessment_sessions table."""
    
    # Rename truncated columns to their full names
    op.alter_column('assessment_sessions', 'business_profil', new_column_name='business_profile_id')
    op.alter_column('assessment_sessions', 'questions_answe', new_column_name='questions_answered')
    op.alter_column('assessment_sessions', 'calculated_scor', new_column_name='calculated_scores')
    op.alter_column('assessment_sessions', 'recommended_fra', new_column_name='recommended_frameworks')


def downgrade():
    """Revert column names back to truncated versions."""
    
    # Revert column names to truncated versions
    op.alter_column('assessment_sessions', 'business_profile_id', new_column_name='business_profil')
    op.alter_column('assessment_sessions', 'questions_answered', new_column_name='questions_answe')
    op.alter_column('assessment_sessions', 'calculated_scores', new_column_name='calculated_scor')
    op.alter_column('assessment_sessions', 'recommended_frameworks', new_column_name='recommended_fra')