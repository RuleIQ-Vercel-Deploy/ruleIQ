from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional, Any

from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB, UUID as PG_UUID

from .db_setup import Base


class SafetyDecision(Base):
    __tablename__ = "safety_decisions"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    org_id = Column(String(100), nullable=True)

    business_profile_id = Column(PG_UUID(as_uuid=True), ForeignKey("business_profiles.id"), nullable=True)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    conversation_id = Column(PG_UUID(as_uuid=True), ForeignKey("chat_conversations.id"), nullable=True)

    content_type = Column(String(50), nullable=False)
    decision = Column(String(20), nullable=False)  # allow | block | modify | escalate
    confidence = Column(Numeric(3, 2), nullable=True)

    applied_filters = Column(PG_JSONB(astext_type=Text()), nullable=False, default=list)

    request_hash = Column(String(64), nullable=False)
    prev_hash = Column(String(64), nullable=True)
    record_hash = Column(String(64), nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    metadata = Column(PG_JSONB(astext_type=Text()), nullable=False, default=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "org_id": self.org_id,
            "business_profile_id": str(self.business_profile_id) if self.business_profile_id else None,
            "user_id": str(self.user_id) if self.user_id else None,
            "conversation_id": str(self.conversation_id) if self.conversation_id else None,
            "content_type": self.content_type,
            "decision": self.decision,
            "confidence": float(self.confidence) if self.confidence is not None else None,
            "applied_filters": self.applied_filters or [],
            "request_hash": self.request_hash,
            "prev_hash": self.prev_hash,
            "record_hash": self.record_hash,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "metadata": self.metadata or {},
        }