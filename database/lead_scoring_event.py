"""
LeadScoringEvent model for tracking behavioral analytics and lead scoring.
Records user interactions and assigns scoring impact for lead qualification.
"""
import uuid
from datetime import datetime
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB

from .db_setup import Base


class LeadScoringEvent(Base):
    """
    Model for tracking lead scoring events and behavioral analytics.
    Records user interactions with scoring impact for lead qualification pipeline.
    """
    __tablename__ = "lead_scoring_events"
    
    # Primary identifier
    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    lead_id = Column(PG_UUID(as_uuid=True), ForeignKey("assessment_leads.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Event classification
    event_type = Column(String(100), nullable=False, index=True)  # assessment_start, question_answered, etc.
    event_category = Column(String(50), nullable=False, index=True)  # engagement, assessment, conversion
    event_action = Column(String(100), nullable=False)  # specific action taken
    event_label = Column(String(200), nullable=True)  # additional context
    
    # Scoring impact
    score_impact = Column(Integer, default=0, nullable=False)  # Points to add/subtract
    cumulative_score = Column(Integer, nullable=True)  # Total score after this event
    
    # Event context and metadata (JSONB for flexibility)
    event_metadata = Column(JSONB, nullable=True)
    session_context = Column(JSONB, nullable=True)
    
    # Timing and performance
    event_duration = Column(Integer, nullable=True)  # Duration in seconds
    page_url = Column(String(500), nullable=True)
    referrer_url = Column(String(500), nullable=True)
    
    # Technical metadata
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    session_id = Column(String(64), nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def __init__(self, **kwargs):
        """Initialize scoring event with default values."""
        super().__init__(**kwargs)
        if not self.event_metadata:
            self.event_metadata = {}
        if not self.session_context:
            self.session_context = {}
    
    def add_metadata(self, key: str, value):
        """Add metadata to the event."""
        if not self.event_metadata:
            self.event_metadata = {}
        self.event_metadata[key] = value
    
    def add_session_context(self, key: str, value):
        """Add session context data."""
        if not self.session_context:
            self.session_context = {}
        self.session_context[key] = value
    
    def get_score_category(self) -> str:
        """Get human-readable score impact category."""
        if self.score_impact <= 0:
            return "Negative"
        elif self.score_impact <= 10:
            return "Low"
        elif self.score_impact <= 25:
            return "Medium"
        elif self.score_impact <= 50:
            return "High"
        else:
            return "Critical"
    
    def is_engagement_event(self) -> bool:
        """Check if this is an engagement-type event."""
        return self.event_category == "engagement"
    
    def is_assessment_event(self) -> bool:
        """Check if this is an assessment-type event."""
        return self.event_category == "assessment"
    
    def is_conversion_event(self) -> bool:
        """Check if this is a conversion-type event."""
        return self.event_category == "conversion"
    
    @classmethod
    def create_assessment_start_event(cls, lead_id: uuid.UUID, session_id: str = None, metadata: dict = None):
        """Factory method for assessment start events."""
        return cls(
            lead_id=lead_id,
            event_type="assessment_start",
            event_category="engagement",
            event_action="started_assessment",
            score_impact=10,
            session_id=session_id,
            event_metadata=metadata or {}
        )
    
    @classmethod
    def create_question_answered_event(cls, lead_id: uuid.UUID, question_type: str, score_impact: int = 5, metadata: dict = None):
        """Factory method for question answered events."""
        return cls(
            lead_id=lead_id,
            event_type="question_answered",
            event_category="assessment",
            event_action=f"answered_{question_type}_question",
            score_impact=score_impact,
            event_metadata=metadata or {}
        )
    
    @classmethod
    def create_assessment_completed_event(cls, lead_id: uuid.UUID, completion_rate: float, metadata: dict = None):
        """Factory method for assessment completion events."""
        # Higher score for complete assessments
        score_impact = 50 if completion_rate >= 1.0 else int(completion_rate * 30)
        
        return cls(
            lead_id=lead_id,
            event_type="assessment_completed",
            event_category="conversion",
            event_action="completed_assessment",
            score_impact=score_impact,
            event_metadata={
                "completion_rate": completion_rate,
                **(metadata or {})
            }
        )
    
    def __repr__(self):
        return f"<LeadScoringEvent(type='{self.event_type}', action='{self.event_action}', impact={self.score_impact})>"