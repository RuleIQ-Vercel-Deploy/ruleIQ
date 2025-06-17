import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from .db_setup import Base


class ImplementationPlan(Base):
    """Control implementation plans with timelines and budgets"""
    __tablename__ = "implementation_plans"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Assuming foreign key references. Adjust table.column names if necessary.
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    business_profile_id = Column(PG_UUID(as_uuid=True), ForeignKey('business_profiles.id'), nullable=False)
    framework_id = Column(PG_UUID(as_uuid=True), ForeignKey('compliance_frameworks.id'), nullable=False)
    policy_id = Column(PG_UUID(as_uuid=True), ForeignKey('generated_policies.id'), nullable=True)

    # Plan metadata
    plan_name = Column(String, nullable=False)
    framework_name = Column(String, nullable=False) # Consider deriving from framework_id
    control_domain = Column(String, nullable=False) # Access Control, Data Protection, etc.

    # Implementation details
    phases = Column(PG_JSONB, default=list)  # Implementation phases with tasks
    total_estimated_hours = Column(Integer, default=0)
    total_estimated_cost = Column(String, default="£0-£5,000") # Consider using Numeric/Decimal for currency
    estimated_duration_weeks = Column(Integer, default=12)

    # Phase structure
    current_phase = Column(Integer, default=1)
    total_phases = Column(Integer, default=4)
    phase_details = Column(PG_JSONB, default=dict)  # Phase number -> details mapping

    # Resource requirements
    required_roles = Column(PG_JSONB, default=list)  # CISO, IT Admin, etc.
    external_resources = Column(PG_JSONB, default=list)  # Consultants, tools, etc.
    budget_breakdown = Column(PG_JSONB, default=dict)  # Category -> cost mapping

    # Timeline
    planned_start_date = Column(DateTime, nullable=True)
    planned_end_date = Column(DateTime, nullable=True)
    actual_start_date = Column(DateTime, nullable=True)
    actual_end_date = Column(DateTime, nullable=True)

    # Progress tracking
    completion_percentage = Column(Float, default=0.0)
    completed_tasks = Column(PG_JSONB, default=list)
    blocked_tasks = Column(PG_JSONB, default=list)

    # Status
    status = Column(String, default="planning")  # planning, in_progress, completed, on_hold
    progress_notes = Column(String, default="")
    risk_factors = Column(PG_JSONB, default=list)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
