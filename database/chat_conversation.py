"""
SQLAlchemy model for storing chat conversations.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from database.db_setup import Base

class ConversationStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class ChatConversation(Base):
    __tablename__ = "chat_conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    business_profile_id = Column(UUID(as_uuid=True), ForeignKey("business_profiles.id"), nullable=False)
    title = Column(String(255), nullable=False)
    status = Column(SAEnum(ConversationStatus), default=ConversationStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatConversation(id={self.id}, title='{self.title}', status='{self.status}')>"