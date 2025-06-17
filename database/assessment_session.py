import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from .db_setup import Base


class AssessmentSession(Base):
    """User assessment sessions for compliance scoping"""
    __tablename__ = "assessment_sessions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    business_profil = Column(PG_UUID(as_uuid=True), ForeignKey('business_profiles.id'), nullable=True)  # business_profile_id truncated

    # Session metadata
    session_type = Column(String, default="compliance_scoping")  # scoping, readiness, etc.
    status = Column(String, default="in_progress")  # in_progress, completed, abandoned

    # Assessment progress (truncated column names to match database)
    current_stage = Column(Integer, default=1)
    total_stages = Column(Integer, default=5)
    questions_answe = Column(Integer, default=0)  # questions_answered truncated
    total_questions = Column(Integer, default=0)

    # Assessment data (truncated column names to match database)
    responses = Column(PG_JSONB, default=dict)  # Question ID -> Answer mapping
    calculated_scor = Column(PG_JSONB, default=dict)  # calculated_scores truncated
    recommendations = Column(PG_JSONB, default=list)  # Recommended frameworks with scores

    # Session state
    started_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Results (truncated column names to match database)
    recommended_fra = Column(PG_JSONB, default=list)  # recommended_frameworks truncated
    priority_order = Column(PG_JSONB, default=list)
    next_steps = Column(PG_JSONB, default=list)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
