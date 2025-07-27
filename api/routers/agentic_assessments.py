"""
FastAPI router for Agentic Assessment endpoints
Provides conversational, context-aware assessments that build relationships with users
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
import logging
from datetime import datetime

from services.agentic_assessment import (
    AgenticAssessmentService, 
    get_agentic_assessment_service,
    ConversationState,
    QuestionType
)
from services.context_service import TrustLevel, CommunicationStyle
from api.dependencies.auth import get_current_user
from api.middleware.rate_limiter import rate_limit
from api.schemas.responses import StandardResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/agentic-assessments", tags=["Agentic Assessments"])

# Request schemas
class StartConversationalAssessmentRequest(BaseModel):
    business_profile_id: str = Field(..., description="Business profile identifier")
    framework_types: List[str] = Field(..., description="Frameworks to assess (ISO27001, GDPR, etc.)")
    resume_previous: bool = Field(False, description="Resume a previous incomplete assessment")

class ConversationResponseRequest(BaseModel):
    user_response: str = Field(..., min_length=1, max_length=2000, description="User's response to current question")
    additional_context: Optional[Dict[str, Any]] = Field(None, description="Optional additional context")

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

@router.post("/start", response_model=StandardResponse[ConversationStatus])
@rate_limit(requests=10, window=60)  # 10 starts per minute
async def start_conversational_assessment(
    request: StartConversationalAssessmentRequest,
    current_user = Depends(get_current_user),
    agentic_service: AgenticAssessmentService = Depends(get_agentic_assessment_service)
):
    """
    Start a new conversational assessment or resume an existing one
    
    This endpoint initiates an agentic assessment conversation that:
    - Adapts to user communication style and patterns
    - Remembers context from previous interactions
    - Asks personalized follow-up questions
    - Builds trust through transparent reasoning
    - Automates routine parts for trusted users
    """
    try:
        logger.info(f"User {current_user.id} starting conversational assessment for frameworks: {request.framework_types}")
        
        # Generate session ID
        session_id = f"conv_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Start the conversation
        result = await agentic_service.start_conversational_assessment(
            user_id=current_user.id,
            business_profile_id=request.business_profile_id,
            session_id=session_id,
            framework_types=request.framework_types,
            resume_previous=request.resume_previous
        )
        
        # Convert to response format
        status = ConversationStatus(
            conversation_id=result["conversation_id"],
            state=result["state"],
            progress=result["progress"],
            current_question=result.get("current_question"),
            trust_level=result["personalization"]["trust_level"],
            communication_style=result["personalization"]["communication_style"]
        )
        
        return StandardResponse(
            success=True,
            data=status,
            message=f"Conversational assessment started for {', '.join(request.framework_types)}"
        )
        
    except Exception as e:
        logger.error(f"Error starting conversational assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start assessment: {str(e)}")

@router.post("/respond/{session_id}", response_model=StandardResponse[Dict[str, Any]])
@rate_limit(requests=30, window=60)  # 30 responses per minute
async def process_conversation_response(
    session_id: str,
    request: ConversationResponseRequest,
    current_user = Depends(get_current_user),
    agentic_service: AgenticAssessmentService = Depends(get_agentic_assessment_service)
):
    """
    Process user response in the conversational assessment
    
    Analyzes the user's response and determines the next action:
    - Ask the next question
    - Request clarification
    - Complete the assessment
    """
    try:
        logger.info(f"Processing response for session {session_id}")
        
        result = await agentic_service.process_conversation_response(
            session_id=session_id,
            user_response=request.user_response,
            additional_context=request.additional_context
        )
        
        return StandardResponse(
            success=True,
            data=result,
            message="Response processed successfully"
        )
        
    except ValueError as e:
        logger.warning(f"Invalid session or response: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing conversation response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process response: {str(e)}")

@router.post("/pause/{session_id}", response_model=StandardResponse[Dict[str, Any]])
@rate_limit(requests=5, window=60)  # 5 pauses per minute
async def pause_conversation(
    session_id: str,
    request: PauseConversationRequest,
    current_user = Depends(get_current_user),
    agentic_service: AgenticAssessmentService = Depends(get_agentic_assessment_service)
):
    """
    Pause an ongoing conversation for later resumption
    
    Allows users to pause their assessment and return later without losing progress.
    Context and conversation state are preserved.
    """
    try:
        logger.info(f"Pausing conversation session {session_id}")
        
        result = await agentic_service.pause_conversation(session_id)
        
        return StandardResponse(
            success=True,
            data=result,
            message="Conversation paused successfully"
        )
        
    except ValueError as e:
        logger.warning(f"Invalid session: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error pausing conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to pause conversation: {str(e)}")

@router.get("/summary/{session_id}", response_model=StandardResponse[ConversationSummary])
async def get_conversation_summary(
    session_id: str,
    current_user = Depends(get_current_user),
    agentic_service: AgenticAssessmentService = Depends(get_agentic_assessment_service)
):
    """
    Get a summary of the current conversation state
    
    Provides overview of assessment progress, answered questions, and current status.
    """
    try:
        logger.info(f"Getting summary for conversation session {session_id}")
        
        summary_data = await agentic_service.get_conversation_summary(session_id)
        
        summary = ConversationSummary(
            conversation_id=summary_data["conversation_id"],
            state=summary_data["state"],
            progress=summary_data["progress"],
            started_at=summary_data["started_at"],
            last_activity=summary_data["last_activity"],
            questions_answered=summary_data["questions_answered"],
            estimated_total_questions=summary_data["estimated_total_questions"],
            framework_types=summary_data["framework_types"],
            trust_signals_count=summary_data["trust_signals_count"]
        )
        
        return StandardResponse(
            success=True,
            data=summary,
            message="Conversation summary retrieved successfully"
        )
        
    except ValueError as e:
        logger.warning(f"Invalid session: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting conversation summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")

@router.get("/health")
async def health_check(
    agentic_service: AgenticAssessmentService = Depends(get_agentic_assessment_service)
):
    """Health check for the agentic assessment service"""
    try:
        # Check if service is initialized
        if agentic_service.context_service is None:
            await agentic_service.initialize()
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "context_service": "initialized" if agentic_service.context_service else "not_initialized",
                "assessment_service": "available",
                "llm_service": "available"
            },
            "capabilities": {
                "conversational_assessments": True,
                "context_continuity": True,
                "trust_building": True,
                "personalization": True
            }
        }
        
        return JSONResponse(content=health_status)
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )

# Convenience endpoints for common use cases
@router.get("/user-patterns/{user_id}", response_model=StandardResponse[Dict[str, Any]])
async def get_user_patterns(
    user_id: str,
    current_user = Depends(get_current_user),
    agentic_service: AgenticAssessmentService = Depends(get_agentic_assessment_service)
):
    """
    Get learned patterns for a user (admin or self only)
    
    Returns user interaction patterns, trust level, and communication preferences.
    """
    try:
        # Ensure user can only access their own patterns or is admin
        if current_user.id != user_id and not getattr(current_user, 'is_admin', False):
            raise HTTPException(status_code=403, detail="Access denied")
        
        patterns = await agentic_service.context_service.retrieve_user_patterns(user_id)
        
        if not patterns:
            return StandardResponse(
                success=True,
                data=None,
                message="No user patterns found"
            )
        
        return StandardResponse(
            success=True,
            data={
                "trust_level": patterns.trust_level,
                "communication_style": patterns.communication_style,
                "preferred_automation_level": patterns.preferred_automation_level,
                "common_tasks": patterns.common_tasks,
                "confidence_score": patterns.confidence_score,
                "last_updated": patterns.last_updated.isoformat()
            },
            message="User patterns retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting user patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get user patterns: {str(e)}")

@router.get("/predicted-needs", response_model=StandardResponse[List[Dict[str, Any]]])
@rate_limit(requests=10, window=60)  # 10 requests per minute
async def get_predicted_needs(
    current_user = Depends(get_current_user),
    agentic_service: AgenticAssessmentService = Depends(get_agentic_assessment_service)
):
    """
    Get predicted user needs based on patterns and context
    
    Returns proactive suggestions for compliance tasks, policy updates, and automation opportunities.
    """
    try:
        logger.info(f"Getting predicted needs for user {current_user.id}")
        
        predictions = await agentic_service.context_service.predict_user_needs(current_user.id)
        
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
        raise HTTPException(status_code=500, detail=f"Failed to get predicted needs: {str(e)}")