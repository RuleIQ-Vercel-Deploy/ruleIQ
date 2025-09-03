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
    user_id = Column(
        PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True
    )  # Assuming one profile per user

    # Basic company information
    company_name = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    employee_count = Column(Integer, nullable=False)
    annual_revenue = Column(
        String, nullable=True
    )  # Consider Numeric/Decimal or specific range type
    country = Column(String, default="UK")
    data_sensitivity = Column(
        String, default="Low", nullable=False
    )  # Re-added for framework relevance calculation

    # Business characteristics (full column names after migration)
    handles_personal_data = Column(Boolean, nullable=False)
    processes_payments = Column(Boolean, nullable=False)
    stores_health_data = Column(Boolean, nullable=False)
    provides_financial_services = Column(Boolean, nullable=False)
    operates_critical_infrastructure = Column(Boolean, nullable=False)
    has_international_operations = Column(Boolean, nullable=False)

    # Technology stack (full column names after migration)
    cloud_providers = Column(PG_JSONB, default=list)  # AWS, Azure, GCP, etc.
    saas_tools = Column(PG_JSONB, default=list)  # Office 365, Salesforce, etc.
    development_tools = Column(PG_JSONB, default=list)  # GitHub, GitLab, etc.

    # Current compliance state (full column names after migration)
    existing_frameworks = Column(PG_JSONB, default=list)  # Currently compliant with
    planned_frameworks = Column(PG_JSONB, default=list)  # Planning to achieve
    compliance_budget = Column(String, nullable=True)  # Consider Numeric/Decimal
    compliance_timeline = Column(String, nullable=True)

    # Assessment status (full column names after migration)
    assessment_completed = Column(Boolean, default=False)
    assessment_data = Column(PG_JSONB, default=dict)  # Store questionnaire responses

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="business_profiles")
    evidence_items = relationship("EvidenceItem", back_populates="business_profile")
