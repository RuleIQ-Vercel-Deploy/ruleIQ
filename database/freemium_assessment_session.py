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

    # Session state - matching actual database columns
    status = Column(String(50), nullable=True)  # This maps to completion_status in service
    current_question_id = Column(String(100), nullable=True)
    total_questions = Column(Integer, nullable=True)
    questions_answered = Column(Integer, nullable=True)
    progress_percentage = Column("progress_percentage", Integer, nullable=True)  # Using double precision in DB

    # Assessment configuration
    assessment_type = Column(String(50), nullable=True)

    # Data storage - matching actual database columns
    questions_data = Column(JSONB, nullable=True)
    ai_responses = Column(JSONB, nullable=True)
    personalization_data = Column(JSONB, nullable=True)

    # Results storage - matching actual database columns
    compliance_score = Column("compliance_score", Integer, nullable=True)  # Using double precision in DB
    risk_assessment = Column(JSONB, nullable=True)
    recommendations = Column(JSONB, nullable=True)
    gaps_identified = Column(JSONB, nullable=True)
    results_summary = Column(Text, nullable=True)

    # User interaction tracking
    results_viewed = Column(Boolean, nullable=True, default=False)
    results_viewed_at = Column(DateTime, nullable=True)
    conversion_cta_clicked = Column(Boolean, nullable=True, default=False)
    conversion_cta_clicked_at = Column(DateTime, nullable=True)
    converted_to_paid = Column(Boolean, nullable=True, default=False)
    converted_at = Column(DateTime, nullable=True)

    # Session analytics
    time_spent_seconds = Column(Integer, nullable=True)
    device_type = Column(String(50), nullable=True)
    browser = Column(String(100), nullable=True)
    session_data = Column(JSONB, nullable=True)

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
            from datetime import timezone
            self.expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    def _generate_secure_token(self) -> str:
        """Generate a cryptographically secure session token."""
        return uuid.uuid4().hex + uuid.uuid4().hex  # 64 characters

    def is_expired(self) -> bool:
        """Check if the session has expired."""
        from datetime import timezone
        now_utc = datetime.now(timezone.utc)

        # Handle both naive and aware datetimes
        if self.expires_at.tzinfo is None:
            # If expires_at is naive, treat it as UTC and make it aware
            expires_at_utc = self.expires_at.replace(tzinfo=timezone.utc)
        else:
            expires_at_utc = self.expires_at

        return now_utc > expires_at_utc

    def is_active(self) -> bool:
        """Check if session is active (not expired and not completed)."""
        return not self.is_expired() and self.status not in ["completed", "expired"]

    def mark_completed(self):
        """Mark session as completed and set completion timestamp."""
        self.status = "completed"
        from datetime import timezone
        self.completed_at = datetime.now(timezone.utc)

    def extend_expiry(self, hours: int = 2):
        """Extend session expiry by specified hours."""
        if self.is_active():
            from datetime import timezone
            self.expires_at = datetime.now(timezone.utc) + timedelta(hours=hours)

    # Properties to maintain backward compatibility with service expectations
    @property
    def completion_status(self):
        """Alias for status to match service expectations."""
        return self.status

    @completion_status.setter
    def completion_status(self, value):
        """Alias setter for status."""
        self.status = value

    @property
    def user_answers(self):
        """Alias for session_data to match service expectations."""
        return self.session_data or {}

    @user_answers.setter
    def user_answers(self, value):
        """Alias setter for session_data."""
        self.session_data = value

    def __repr__(self):
        return f"<FreemiumAssessmentSession(id='{self.id}', status='{self.status}', assessment_type='{self.assessment_type}')>"
