import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from .db_setup import Base  # Import Base from our new db_setup.py

class User(Base):
    __tablename__ = "users"
    """Class for User"""
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(
        String, nullable=False, unique=True
    )  # Added nullable=False and unique=True as common for emails
    hashed_password = Column(String, nullable=True)  # Nullable for OAuth users
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    full_name = Column(String, nullable=True)  # Full name from OAuth providers
    google_id = Column(String, nullable=True, unique=True)  # Google OAuth ID

    # Relationships to other models
    business_profiles = relationship("BusinessProfile", back_populates="owner")
    evidence_items = relationship("EvidenceItem", back_populates="user")
    assessments = relationship("AssessmentSession")
    implementation_plans = relationship("ImplementationPlan")
    readiness_assessments = relationship("ReadinessAssessment")
    report_schedules = relationship("ReportSchedule", back_populates="owner")
