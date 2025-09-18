"""Create safety_decisions table for durable safety and audit trail

Revision ID: 9f1e4a78f2b0
Revises: 433c68d53999
Create Date: 2025-09-18

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = "9f1e4a78f2b0"
down_revision = "433c68d53999"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ensure required extensions are available
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    # Create safety_decisions table (append-only, immutable by convention)
    op.create_table(
        "safety_decisions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column("org_id", sa.String(100), nullable=True),
        sa.Column("business_profile_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("conversation_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("content_type", sa.String(50), nullable=False),
        sa.Column("decision", sa.String(20), nullable=False),
        sa.Column("confidence", sa.Numeric(3, 2), nullable=True),
        sa.Column(
            "applied_filters",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column("request_hash", sa.String(64), nullable=False),
        sa.Column("prev_hash", sa.String(64), nullable=True),
        sa.Column("record_hash", sa.String(64), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Foreign keys to existing tables (soft references; SET NULL on delete)
    op.create_foreign_key(
        "fk_safety_decisions_user",
        "safety_decisions",
        "users",
        ["user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_safety_decisions_bp",
        "safety_decisions",
        "business_profiles",
        ["business_profile_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_safety_decisions_conversation",
        "safety_decisions",
        "chat_conversations",
        ["conversation_id"],
        ["id"],
        ondelete="SET NULL",
    )

    # Indexes for common query paths
    op.create_index(
        "idx_safety_org_time", "safety_decisions", ["org_id", "created_at"]
    )
    op.create_index(
        "idx_safety_bp_time",
        "safety_decisions",
        ["business_profile_id", "created_at"],
    )
    op.create_index(
        "idx_safety_user_time", "safety_decisions", ["user_id", "created_at"]
    )
    op.create_index(
        "idx_safety_request_hash", "safety_decisions", ["request_hash"]
    )
    op.create_index(
        "uq_safety_record_hash",
        "safety_decisions",
        ["record_hash"],
        unique=True,
    )

    # GIN index on metadata for flexible filters
    op.execute(
        text(
            "CREATE INDEX IF NOT EXISTS idx_safety_metadata_gin "
            "ON safety_decisions USING GIN (metadata)"
        )
    )

    # Constraints
    op.create_check_constraint(
        "ck_safety_confidence_range",
        "safety_decisions",
        "confidence >= 0 AND confidence <= 1",
    )
    op.create_check_constraint(
        "ck_safety_decision_values",
        "safety_decisions",
        "decision IN ('allow','block','modify','escalate')",
    )


def downgrade() -> None:
    # Drop constraints and indexes in reverse order
    op.drop_constraint(
        "ck_safety_decision_values", "safety_decisions", type_="check"
    )
    op.drop_constraint(
        "ck_safety_confidence_range", "safety_decisions", type_="check"
    )
    op.execute("DROP INDEX IF EXISTS idx_safety_metadata_gin;")
    op.drop_index("uq_safety_record_hash", table_name="safety_decisions")
    op.drop_index("idx_safety_request_hash", table_name="safety_decisions")
    op.drop_index("idx_safety_user_time", table_name="safety_decisions")
    op.drop_index("idx_safety_bp_time", table_name="safety_decisions")
    op.drop_index("idx_safety_org_time", table_name="safety_decisions")

    # Drop FKs
    op.drop_constraint(
        "fk_safety_decisions_conversation",
        "safety_decisions",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_safety_decisions_bp", "safety_decisions", type_="foreignkey"
    )
    op.drop_constraint(
        "fk_safety_decisions_user", "safety_decisions", type_="foreignkey"
    )

    # Drop table
    op.drop_table("safety_decisions")