import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

# Import the shared Base from db_setup to ensure all models use the same Base
from .db_setup import Base
# Import existing models from their dedicated files to avoid duplication
from .user import User
from .business_profile import BusinessProfile
from .compliance_framework import ComplianceFramework
from .evidence_item import EvidenceItem
from .generated_policy import GeneratedPolicy
from .implementation_plan import ImplementationPlan
from .integration_configuration import IntegrationConfiguration
from .report_schedule import ReportSchedule

class Policy(Base):
    __tablename__ = "policies"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    business_profile_id = Column(PG_UUID(as_uuid=True), ForeignKey("business_profiles.id"), nullable=False)
    framework_name = Column(String(100), nullable=False)
    policy_title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    version = Column(String(20), default="1.0")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(PG_UUID(as_uuid=True), ForeignKey("assessment_sessions.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=True)
    question_type = Column(String(50), nullable=False)  # e.g., 'multiple_choice', 'free_text', 'yes_no'
    options = Column(JSON, nullable=True) # For multiple choice options
    order = Column(Integer, nullable=False, default=0) # To maintain question order
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    session = relationship("AssessmentSession", back_populates="questions")

class Evidence(Base):
    __tablename__ = "evidence"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    business_profile_id = Column(PG_UUID(as_uuid=True), ForeignKey("business_profiles.id"), nullable=False)
    framework_id = Column(PG_UUID(as_uuid=True), ForeignKey("compliance_frameworks.id"), nullable=False)
    control_id = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    source = Column(String(50), default="manual_upload")
    tags = Column(JSON, default=list)
    file_path = Column(String(255), nullable=True)
    status = Column(String(20), default="pending_review")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="evidences")

class AssessmentSession(Base):
    __tablename__ = "assessment_sessions"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    business_profile_id = Column(PG_UUID(as_uuid=True), ForeignKey("business_profiles.id"), nullable=True)
    framework_id = Column(PG_UUID(as_uuid=True), ForeignKey("compliance_frameworks.id"), nullable=True)
    session_type = Column(String(50), default="compliance_scoping")
    status = Column(String(20), default="in_progress")  # e.g., in_progress, completed, abandoned
    current_stage = Column(Integer, default=1)
    total_stages = Column(Integer, default=5)
    responses = Column(JSON, nullable=True)  # Stores answers to questions
    recommendations = Column(JSON, default=[])
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    overall_progress = Column(Float, default=0.0)
    estimated_time_remaining_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="assessments")
    questions = relationship("AssessmentQuestion", back_populates="session", cascade="all, delete-orphan")

# ImplementationPlan is imported from implementation_plan.py

class ReadinessAssessment(Base):
    __tablename__ = "readiness_assessments"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    business_profile_id = Column(PG_UUID(as_uuid=True), ForeignKey("business_profiles.id"), nullable=False)
    framework_id = Column(PG_UUID(as_uuid=True), ForeignKey("compliance_frameworks.id"), nullable=False)
    overall_score = Column(Float, nullable=False)
    score_breakdown = Column(JSON, nullable=False)
    priority_actions = Column(JSON, nullable=True)
    quick_wins = Column(JSON, nullable=True)
    score_trend = Column(String(20), default="stable")
    estimated_readiness_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="readiness_assessments")

# IntegrationConfiguration is imported from integration_configuration.py

# ReportSchedule is imported from report_schedule.py
