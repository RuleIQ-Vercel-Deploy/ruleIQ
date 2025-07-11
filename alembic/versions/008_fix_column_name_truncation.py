"""Fix column name truncation in business_profiles table

Revision ID: 008
Revises: 007
Create Date: 2025-01-07

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "008"
down_revision = "007"
branch_labels = None
depends_on = None


def upgrade():
    """Fix truncated column names in business_profiles table."""

    # Check and rename columns only if they exist with truncated names
    column_mappings = [
        ("handles_persona", "handles_personal_data"),
        ("processes_payme", "processes_payments"),
        ("stores_health_d", "stores_health_data"),
        ("provides_financ", "provides_financial_services"),
        ("operates_critic", "operates_critical_infrastructure"),
        ("has_internation", "has_international_operations"),
        ("development_too", "development_tools"),
        ("existing_framew", "existing_frameworks"),
        ("planned_framewo", "planned_frameworks"),
        ("compliance_budg", "compliance_budget"),
        ("compliance_time", "compliance_timeline"),
        ("assessment_comp", "assessment_completed"),
    ]

    for old_name, new_name in column_mappings:
        op.execute(f"""
            DO $$ 
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='business_profiles' 
                    AND column_name='{old_name}'
                ) AND NOT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name='business_profiles' 
                    AND column_name='{new_name}'
                ) THEN
                    ALTER TABLE business_profiles 
                    RENAME COLUMN {old_name} TO {new_name};
                END IF;
            END $$;
        """)


def downgrade():
    """Revert column names back to truncated versions."""

    # Revert column names to truncated versions
    op.alter_column("business_profiles", "handles_personal_data", new_column_name="handles_persona")
    op.alter_column("business_profiles", "processes_payments", new_column_name="processes_payme")
    op.alter_column("business_profiles", "stores_health_data", new_column_name="stores_health_d")
    op.alter_column(
        "business_profiles", "provides_financial_services", new_column_name="provides_financ"
    )
    op.alter_column(
        "business_profiles", "operates_critical_infrastructure", new_column_name="operates_critic"
    )
    op.alter_column(
        "business_profiles", "has_international_operations", new_column_name="has_internation"
    )
    op.alter_column("business_profiles", "development_tools", new_column_name="development_too")
    op.alter_column("business_profiles", "existing_frameworks", new_column_name="existing_framew")
    op.alter_column("business_profiles", "planned_frameworks", new_column_name="planned_framewo")
    op.alter_column("business_profiles", "compliance_budget", new_column_name="compliance_budg")
    op.alter_column("business_profiles", "compliance_timeline", new_column_name="compliance_time")
    op.alter_column("business_profiles", "assessment_completed", new_column_name="assessment_comp")
