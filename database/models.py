import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB, UUID as PG_UUID
from sqlalchemy.orm import relationship

# Import the shared Base from db_setup to ensure all models use the same Base
from .db_setup import Base

# Import existing models from their dedicated files to avoid duplication
from .user import User
from .business_profile import BusinessProfile
from .compliance_framework import ComplianceFramework
from .evidence_item import EvidenceItem
from .assessment_session import AssessmentSession
from .assessment_question import AssessmentQuestion
from .implementation_plan import ImplementationPlan
from .readiness_assessment import ReadinessAssessment
from .generated_policy import GeneratedPolicy
from .chat_conversation import ChatConversation
from .chat_message import ChatMessage
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
    ai_metadata = Column(PG_JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Note: This Evidence model appears to be a duplicate of EvidenceItem
    # The User model references EvidenceItem, not Evidence
    # owner = relationship("User", back_populates="evidence_items")

# AssessmentSession is imported from assessment_session.py

# ImplementationPlan is imported from implementation_plan.py

# ReadinessAssessment is imported from readiness_assessment.py

# IntegrationConfiguration is imported from integration_configuration.py

# ReportSchedule is imported from report_schedule.py
