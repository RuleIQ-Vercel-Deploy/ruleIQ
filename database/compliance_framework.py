import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from .db_setup import Base


class ComplianceFramework(Base):
    """Compliance frameworks and their requirements"""
    __tablename__ = "compliance_frameworks"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Framework basic info
    name = Column(String, nullable=False, unique=True)  # GDPR, FCA, CQC, etc.
    display_name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String, nullable=False)  # Data Protection, Financial, Healthcare, etc.

    # Framework characteristics (truncated column names to match database)
    applicable_indu = Column(PG_JSONB, default=list)  # applicable_industries truncated
    employee_thresh = Column(Integer, nullable=True)  # employee_threshold truncated
    revenue_thresho = Column(String, nullable=True) # revenue_threshold truncated
    geographic_scop = Column(PG_JSONB, default=lambda: ["UK"])  # geographic_scope truncated

    # Requirements and controls (truncated column names to match database)
    key_requirement = Column(PG_JSONB, default=list)  # key_requirements truncated
    control_domains = Column(PG_JSONB, default=list)
    evidence_types = Column(PG_JSONB, default=list)

    # Assessment criteria (truncated column names to match database)
    relevance_facto = Column(PG_JSONB, default=dict)  # relevance_factors truncated
    complexity_scor = Column(Integer, default=1)  # complexity_score truncated
    implementation_ = Column(Integer, default=12)  # implementation_time_weeks truncated
    estimated_cost_ = Column(String, default="£5,000-£25,000") # estimated_cost_range truncated

    # Content templates (truncated column names to match database)
    policy_template = Column(Text, default="")
    control_templat = Column(PG_JSONB, default=dict)  # control_templates truncated
    evidence_templa = Column(PG_JSONB, default=dict)  # evidence_templates truncated

    # Metadata
    is_active = Column(Boolean, default=True)
    version = Column(String, default="1.0")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
