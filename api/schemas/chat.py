"""
Pydantic schemas for chat API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

class SendMessageRequest(BaseModel):
    """Request schema for sending a chat message."""
    message: str = Field(..., min_length=1, max_length=2000, description="The user's message")

class MessageResponse(BaseModel):
    """Response schema for a chat message."""
    id: UUID
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str
    metadata: Optional[Dict[str, Any]] = None
    sequence_number: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationSummary(BaseModel):
    """Summary schema for a conversation."""
    id: UUID
    title: str
    status: str
    message_count: int
    last_message_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    """Response schema for a conversation with messages."""
    id: UUID
    title: str
    status: str
    messages: List[MessageResponse]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CreateConversationRequest(BaseModel):
    """Request schema for creating a new conversation."""
    title: Optional[str] = Field(None, max_length=255, description="Optional conversation title")
    initial_message: Optional[str] = Field(None, max_length=2000, description="Optional initial message")

class ConversationListResponse(BaseModel):
    """Response schema for listing conversations."""
    conversations: List[ConversationSummary]
    total: int
    page: int
    per_page: int

class EvidenceRecommendationRequest(BaseModel):
    """Request schema for getting evidence recommendations."""
    framework: Optional[str] = Field(None, description="Specific framework to get recommendations for")
    
class EvidenceRecommendationResponse(BaseModel):
    """Response schema for evidence recommendations."""
    framework: str
    recommendations: str
    generated_at: datetime

class ComplianceAnalysisRequest(BaseModel):
    """Request schema for compliance gap analysis."""
    framework: str = Field(..., description="Framework to analyze")

class ComplianceAnalysisResponse(BaseModel):
    """Response schema for compliance analysis."""
    framework: str
    completion_percentage: float
    evidence_collected: int
    evidence_types: List[str]
    recent_activity: int
    recommendations: List[Dict[str, Any]]