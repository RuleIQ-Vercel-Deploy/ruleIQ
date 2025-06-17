import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from .db_setup import Base


class EvidenceItem(Base):
    """Evidence collection tracking for compliance audits"""
    __tablename__ = "evidence_items"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # Assuming foreign key references. Adjust table.column names if necessary.
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    business_profile_id = Column(PG_UUID(as_uuid=True), ForeignKey('business_profiles.id'), nullable=False)
    framework_id = Column(PG_UUID(as_uuid=True), ForeignKey('compliance_frameworks.id'), nullable=False)

    # Evidence metadata
    evidence_name = Column(String, nullable=False)
    evidence_type = Column(String, nullable=False)  # Policy, Procedure, Log, Certificate, etc.
    control_reference = Column(String, nullable=False)  # Which control this evidence supports

    # Requirements
    description = Column(Text, nullable=False)
    required_for_audit = Column(Boolean, default=True)
    collection_frequency = Column(String, default="once")  # once, monthly, quarterly, annually

    # Collection details
    collection_method = Column(String, default="manual")  # manual, automated, semi_automated
    automation_source = Column(String, nullable=True)  # AWS, Office365, GitHub, etc.
    automation_guidance = Column(Text, default="")

    # File information
    file_path = Column(String, nullable=True)
    file_type = Column(String, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)

    # Status tracking
    status = Column(String, default="not_started")  # not_started, in_progress, collected, approved, rejected
    collection_notes = Column(Text, default="")
    review_notes = Column(Text, default="")

    # Approval workflow
    collected_by = Column(String, nullable=True)
    collected_at = Column(DateTime, nullable=True)
    reviewed_by = Column(String, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    approved_by = Column(String, nullable=True)
    approved_at = Column(DateTime, nullable=True)

    # Metadata
    priority = Column(String, default="medium")  # low, medium, high, critical
    effort_estimate = Column(String, default="2-4 hours")

    # Compliance mapping
    audit_section = Column(String, default="")
    compliance_score_impact = Column(Float, default=0.0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
