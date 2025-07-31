"""
FastAPI router for Agentic Assessment endpoints
Provides conversational, context-aware assessments that build relationships with users
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import logging

from services.agentic_assessment import (
    AgenticAssessmentService,
    get_agentic_assessment_service,
    ConversationState
)
from services.context_service import TrustLevel, CommunicationStyle
from api.dependencies.stack_auth import get_current_stack_user, User
from api.middleware.rate_limiter import rate_limit
from api.schemas.base import StandardResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agentic-assessments", tags=["Agentic Assessments"])

# Request schemas
class StartConversationalAssessmentRequest(BaseModel):
    business_profile_id: str = Field(..., description="Business profile identifier")
    framework_types: List[str] = Field(
        ..., description="Frameworks to assess (ISO27001, GDPR, etc.)"
    )
    resume_previous: bool = Field(
        False, description="Resume a previous incomplete assessment"
    )

class ConversationResponseRequest(BaseModel):
    user_response: str = Field(
        ..., min_length=1, max_length=2000,
        description="User's response to current question"
    )
    additional_context: Optional[Dict[str, Any]] = Field(
        None, description="Optional additional context"
    )

class PauseConversationRequest(BaseModel):
    reason: Optional[str] = Field(None, description="Optional reason for pausing")

# Response schemas
class ConversationStatus(BaseModel):
    conversation_id: str
    state: ConversationState
    progress: float
    current_question: Optional[Dict[str, Any]] = None
    estimated_remaining_time: Optional[int] = None
    trust_level: TrustLevel
    communication_style: CommunicationStyle

class ConversationSummary(BaseModel):
    conversation_id: str
    state: ConversationState
    progress: float
    started_at: str
    last_activity: str
    questions_answered: int
    estimated_total_questions: int
    framework_types: List[str]
    trust_signals_count: int

@router.get(
    "/predicted-needs",
    response_model=StandardResponse[List[Dict[str, Any]]],
    dependencies=[Depends(rate_limit(requests_per_minute=10))]
)
async def get_predicted_needs(
    current_user: dict = Depends(get_current_stack_user),
    agentic_service: AgenticAssessmentService = Depends(get_agentic_assessment_service)
) -> StandardResponse[List[Dict[str, Any]]]:
    """
    Get predicted user needs based on patterns and context

    Returns proactive suggestions for compliance tasks, policy updates,
    and automation opportunities.
    """
    try:
        logger.info(f"Getting predicted needs for user {current_user["id"]}")

        predictions = await agentic_service.context_service.predict_user_needs(
            current_user["id"]
        )

        predicted_needs = [
            {
                "need_type": p.need_type,
                "confidence": p.confidence,
                "reasoning": p.reasoning,
                "suggested_action": p.suggested_action,
                "estimated_value": p.estimated_value,
                "urgency": p.urgency
            }
            for p in predictions
        ]

        return StandardResponse(
            success=True,
            data=predicted_needs,
            message=f"Found {len(predicted_needs)} predicted needs"
        )

    except Exception as e:
        logger.error(f"Error getting predicted needs: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get predicted needs: {str(e)}"
        )
