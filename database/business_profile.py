import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from .db_setup import Base


class BusinessProfile(Base):
    """Business profile information for compliance assessment"""
    __tablename__ = "business_profiles"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=False, unique=True) # Assuming one profile per user

    # Basic company information
    company_name = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    employee_count = Column(Integer, nullable=False)
    annual_revenue = Column(String, nullable=True) # Consider Numeric/Decimal or specific range type
    country = Column(String, default="UK")
    data_sensitivity = Column(String, default="Low", nullable=False)  # Re-added for framework relevance calculation

    # Business characteristics (truncated column names to match database)
    handles_persona = Column(Boolean, nullable=False)  # handles_personal_data truncated
    processes_payme = Column(Boolean, nullable=False)  # processes_payments truncated
    stores_health_d = Column(Boolean, nullable=False)  # stores_health_data truncated
    provides_financ = Column(Boolean, nullable=False)  # provides_financial_services truncated
    operates_critic = Column(Boolean, nullable=False)  # operates_critical_infrastructure truncated
    has_internation = Column(Boolean, nullable=False)  # has_international_operations truncated

    # Technology stack (truncated column names to match database)
    cloud_providers = Column(PG_JSONB, default=list)  # AWS, Azure, GCP, etc.
    saas_tools = Column(PG_JSONB, default=list)  # Office 365, Salesforce, etc.
    development_too = Column(PG_JSONB, default=list)  # GitHub, GitLab, etc. (truncated)

    # Current compliance state (truncated column names to match database)
    existing_framew = Column(PG_JSONB, default=list)  # Currently compliant with (truncated)
    planned_framewo = Column(PG_JSONB, default=list)  # Planning to achieve (truncated)
    compliance_budg = Column(String, nullable=True) # Consider Numeric/Decimal (truncated)
    compliance_time = Column(String, nullable=True)  # compliance_timeline truncated

    # Assessment status (truncated column names to match database)
    assessment_comp = Column(Boolean, default=False)  # assessment_completed truncated
    assessment_data = Column(PG_JSONB, default=dict)  # Store questionnaire responses

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="business_profiles")
    evidence_items = relationship("EvidenceItem", back_populates="business_profile")
