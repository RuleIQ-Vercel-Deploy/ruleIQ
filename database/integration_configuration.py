"""
ORM model for storing third-party integration configurations.
"""

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from .db_setup import Base


class IntegrationConfiguration(Base):
    __tablename__ = "integration_configurations"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    provider = Column(String(100), nullable=False, index=True)  # e.g., 'google_workspace', 'microsoft_365'
    
    # Store encrypted credentials as a string (Fernet tokens are URL-safe base64 strings).
    # The encryption/decryption logic is handled in the BaseIntegration class.
    credentials = Column(Text, nullable=True)
    settings = Column(JSON, nullable=True) # Specific settings for the integration
    
    status = Column(String(50), default="disconnected")  # e.g., 'connected', 'disconnected', 'error', 'syncing'
    last_sync_at = Column(DateTime, nullable=True)
    last_sync_status = Column(String(50), nullable=True) # e.g., 'success', 'failed'
    last_sync_message = Column(Text, nullable=True)
    is_enabled = Column(Boolean, default=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")

    def __repr__(self):
        return f"<IntegrationConfiguration(id={self.id}, user_id={self.user_id}, provider='{self.provider}', status='{self.status}')>"
