"""
FreemiumAssessmentSession model for managing AI-driven assessment sessions.
Stores session data, AI responses, and user interactions for freemium flow.
"""
import uuid
from datetime import datetime, timedelta
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB

from .db_setup import Base


class FreemiumAssessmentSession(Base):
    """
    Model for managing freemium assessment sessions with AI integration.
    Stores session state, AI responses, and user answers with secure tokens.
    """
    __tablename__ = "freemium_assessment_sessions"
    
    # Primary identifiers
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(PG_UUID(as_uuid=True), ForeignKey("assessment_leads.id", ondelete="CASCADE"), nullable=False)
    
    # Session management
    session_token = Column(String(64), nullable=False, unique=True, index=True)
    expires_at = Column(DateTime, nullable=False)
    
    # Business context
    business_type = Column(String(100), nullable=False)
    company_size = Column(String(50), nullable=True)
    industry_sector = Column(String(100), nullable=True)
    
    # Session state
    completion_status = Column(String(20), default="started", nullable=False)  # started, in_progress, completed, expired
    current_step = Column(Integer, default=1, nullable=False)
    total_steps = Column(Integer, default=5, nullable=False)
    
    # AI interaction data (JSONB for flexible storage)
    ai_responses = Column(JSONB, nullable=True)
    user_answers = Column(JSONB, nullable=True)
    assessment_results = Column(JSONB, nullable=True)
    
    # Performance tracking
    questions_generated = Column(Integer, default=0, nullable=False)
    ai_tokens_used = Column(Integer, default=0, nullable=False)
    ai_cost_incurred = Column(Integer, default=0, nullable=False)  # Cost in cents
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    def __init__(self, **kwargs):
        """Initialize session with secure token and default expiration."""
        super().__init__(**kwargs)
        if not self.session_token:
            self.session_token = self._generate_secure_token()
        if not self.expires_at:
            self.expires_at = datetime.utcnow() + timedelta(hours=24)
    
    def _generate_secure_token(self) -> str:
        """Generate a cryptographically secure session token."""
        return uuid.uuid4().hex + uuid.uuid4().hex  # 64 characters
    
    def is_expired(self) -> bool:
        """Check if the session has expired."""
        return datetime.utcnow() > self.expires_at
    
    def is_active(self) -> bool:
        """Check if session is active (not expired and not completed)."""
        return not self.is_expired() and self.completion_status not in ["completed", "expired"]
    
    def mark_completed(self):
        """Mark session as completed and set completion timestamp."""
        self.completion_status = "completed"
        self.completed_at = datetime.utcnow()
    
    def extend_expiry(self, hours: int = 2):
        """Extend session expiry by specified hours."""
        if self.is_active():
            self.expires_at = datetime.utcnow() + timedelta(hours=hours)
    
    def add_ai_cost(self, cost_cents: int):
        """Add AI usage cost to session tracking."""
        self.ai_cost_incurred += cost_cents
    
    def __repr__(self):
        return f"<FreemiumAssessmentSession(id='{self.id}', status='{self.completion_status}', business_type='{self.business_type}')>"