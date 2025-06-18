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
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    business_profiles = relationship("BusinessProfile", back_populates="owner")
    evidences = relationship("Evidence", back_populates="owner")
    assessments = relationship("AssessmentSession", back_populates="owner")
    implementation_plans = relationship("ImplementationPlan", back_populates="owner")
    readiness_assessments = relationship("ReadinessAssessment", back_populates="owner")
    report_schedules = relationship("ReportSchedule", back_populates="owner")

class BusinessProfile(Base):
    __tablename__ = "business_profiles"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    company_name = Column(String(100), nullable=False)
    industry = Column(String(50), nullable=False)
    employee_count = Column(Integer, nullable=False)
    annual_revenue = Column(String(50), nullable=True)
    country = Column(String(50), default="United Kingdom")
    data_sensitivity = Column(String(50), default="Low")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="business_profiles")

class ComplianceFramework(Base):
    __tablename__ = "compliance_frameworks"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    version = Column(String(20), nullable=True)
    controls = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GeneratedPolicy(Base):
    __tablename__ = "generated_policies"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    framework_id = Column(PG_UUID(as_uuid=True), ForeignKey("compliance_frameworks.id"), nullable=False)
    framework_name = Column(String(100), nullable=False)
    policy_title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    version = Column(String(20), default="1.0")
    created_at = Column(DateTime, default=datetime.utcnow)

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
    framework_id = Column(PG_UUID(as_uuid=True), ForeignKey("compliance_frameworks.id"), nullable=False)
    control_id = Column(String(100), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
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

    owner = relationship("User", back_populates="assessments")
    questions = relationship("AssessmentQuestion", back_populates="session", cascade="all, delete-orphan")

class ImplementationPlan(Base):
    __tablename__ = "implementation_plans"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    framework_id = Column(PG_UUID(as_uuid=True), ForeignKey("compliance_frameworks.id"), nullable=False)
    title = Column(String(255), nullable=False)
    status = Column(String(20), default="not_started")
    phases = Column(JSON, nullable=False)
    current_phase_index = Column(Integer, default=0)
    overall_progress = Column(Float, default=0.0)
    start_date = Column(DateTime, nullable=True)
    estimated_completion_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="implementation_plans")

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

class IntegrationConfiguration(Base):
    __tablename__ = "integration_configurations"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    integration_name = Column(String(100), nullable=False)
    credentials = Column(Text, nullable=False) # This should be encrypted in practice
    is_active = Column(Boolean, default=False)
    last_sync_status = Column(String(20), nullable=True)
    last_sync_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ReportSchedule(Base):
    __tablename__ = "report_schedules"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    report_name = Column(String(100), nullable=False)
    report_type = Column(String(50), nullable=False)
    framework_id = Column(PG_UUID(as_uuid=True), ForeignKey("compliance_frameworks.id"), nullable=False)
    schedule_cron = Column(String(50), nullable=False)
    recipients = Column(JSON, nullable=False) # List of email addresses
    is_active = Column(Boolean, default=True)
    last_run_time = Column(DateTime, nullable=True)
    last_run_status = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="report_schedules")
