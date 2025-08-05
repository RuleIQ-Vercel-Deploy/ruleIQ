"""
FastAPI router for Freemium Assessment Strategy endpoints.

Implements the email-gated AI assessment funnel with 5 core endpoints:
1. POST /freemium/leads - Email capture and UTM tracking
2. POST /freemium/sessions - Start AI assessment session
3. GET /freemium/sessions/{session_token} - Get session progress
4. POST /freemium/sessions/{session_token}/answers - Submit answers
5. GET /freemium/sessions/{session_token}/results - Get assessment results

Following ruleIQ patterns: Rate limiting, RBAC middleware, field mappers, error handling.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field

from api.dependencies.database import get_db
from api.dependencies.rate_limiter import rate_limit
from api.middleware.rbac_middleware import require_permission
from database import (
    AssessmentLead,
    FreemiumAssessmentSession,
    AIQuestionBank,
    LeadScoringEvent,
)
from services.freemium_assessment_service import FreemiumAssessmentService
from services.lead_scoring_service import LeadScoringService
from config.logging_config import get_logger

logger = get_logger(__name__)

# Create router with prefix and tags
router = APIRouter(
    prefix="/freemium",
    tags=["Freemium Assessment"],
    responses={
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"},
    },
)


# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================

class LeadCaptureRequest(BaseModel):
    """Schema for email capture and lead generation."""
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    company_name: Optional[str] = Field(None, max_length=200)
    company_size: Optional[str] = Field(None, regex="^(1-10|11-50|51-200|201-500|500+)$")
    industry: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    
    # UTM tracking parameters
    utm_source: Optional[str] = Field(None, max_length=100)
    utm_medium: Optional[str] = Field(None, max_length=100)
    utm_campaign: Optional[str] = Field(None, max_length=200)
    utm_term: Optional[str] = Field(None, max_length=200)
    utm_content: Optional[str] = Field(None, max_length=200)
    
    # Browser and context data
    referrer_url: Optional[str] = Field(None, max_length=500)
    landing_page: Optional[str] = Field(None, max_length=500)
    user_agent: Optional[str] = None
    
    # Consent and preferences
    marketing_consent: bool = Field(default=False)
    newsletter_subscribed: bool = Field(default=True)


class SessionStartRequest(BaseModel):
    """Schema for starting an assessment session."""
    lead_email: EmailStr
    business_type: str = Field(..., max_length=100)
    company_size: Optional[str] = Field(None, regex="^(1-10|11-50|51-200|201-500|500+)$")
    assessment_type: str = Field(default="general", regex="^(general|gdpr|security|compliance)$")
    
    # Personalization preferences
    industry_focus: Optional[str] = Field(None, max_length=100)
    compliance_frameworks: Optional[List[str]] = Field(default_factory=list)
    priority_areas: Optional[List[str]] = Field(default_factory=list)


class AnswerSubmissionRequest(BaseModel):
    """Schema for submitting assessment answers."""
    question_id: str
    answer: str
    answer_confidence: Optional[str] = Field(None, regex="^(low|medium|high)$")
    time_spent_seconds: Optional[int] = Field(None, ge=0)
    skip_reason: Optional[str] = Field(None, max_length=200)


class LeadResponse(BaseModel):
    """Response schema for lead capture."""
    lead_id: UUID
    email: str
    lead_score: int
    lead_status: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class SessionResponse(BaseModel):
    """Response schema for assessment sessions."""
    session_id: UUID
    session_token: str
    lead_id: UUID
    status: str
    progress_percentage: float
    current_question_id: Optional[str]
    total_questions: int
    questions_answered: int
    expires_at: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuestionResponse(BaseModel):
    """Response schema for AI-generated questions."""
    question_id: str
    question_text: str
    question_type: str
    options: Optional[List[str]]
    context: Optional[str]
    category: str
    difficulty_level: int
    
    class Config:
        from_attributes = True


class AssessmentResultsResponse(BaseModel):
    """Response schema for assessment results."""
    session_id: UUID
    compliance_score: Optional[float]
    risk_level: str
    completed_at: Optional[datetime]
    
    # AI-generated insights
    risk_assessment: dict
    recommendations: List[dict]
    gaps_identified: List[dict]
    results_summary: str
    
    # Conversion tracking
    conversion_opportunities: List[dict]
    next_steps: List[str]
    
    class Config:
        from_attributes = True


# ============================================================================
# ENDPOINT IMPLEMENTATIONS
# ============================================================================

@router.post(
    "/leads",
    response_model=LeadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Capture lead and track UTM parameters",
    description="Email capture endpoint with UTM tracking for freemium funnel conversion analytics"
)
@rate_limit(requests=20, window=60)  # 20 requests per minute for lead capture
async def capture_lead(
    request: Request,
    lead_data: LeadCaptureRequest,
    db: Session = Depends(get_db)
) -> LeadResponse:
    """
    Capture lead information and UTM parameters for freemium assessment funnel.
    
    Creates or updates an AssessmentLead record with:
    - Email validation and deduplication
    - UTM parameter tracking for attribution
    - Initial lead scoring (engagement = +10 points)
    - GDPR-compliant consent management
    """
    try:
        # Extract IP address for geolocation (if needed)
        client_ip = request.client.host
        
        # Check for existing lead by email
        existing_lead = db.query(AssessmentLead).filter_by(email=lead_data.email).first()
        
        if existing_lead:
            logger.info(f"Updating existing lead: {lead_data.email}")
            
            # Update existing lead with new information
            for field, value in lead_data.dict(exclude_unset=True).items():
                if hasattr(existing_lead, field) and value is not None:
                    setattr(existing_lead, field, value)
            
            existing_lead.last_activity_at = datetime.utcnow()
            existing_lead.lead_score += 5  # Returning visitor bonus
            
            db.commit()
            db.refresh(existing_lead)
            
            # Track returning visitor event
            scoring_service = LeadScoringService(db)
            await scoring_service.track_event(
                lead_id=existing_lead.id,
                event_type="lead_return",
                event_category="engagement",
                event_action="returned_visitor",
                score_impact=5,
                metadata={"source": "freemium_capture"}
            )
            
            return LeadResponse.from_orm(existing_lead)
        
        else:
            logger.info(f"Creating new lead: {lead_data.email}")
            
            # Create new lead
            new_lead = AssessmentLead(
                **lead_data.dict(exclude_unset=True),
                ip_address=client_ip,
                lead_score=10,  # Initial engagement score
                lead_status="new",
                last_activity_at=datetime.utcnow()
            )
            
            if lead_data.marketing_consent:
                new_lead.consent_date = datetime.utcnow()
            
            db.add(new_lead)
            db.commit()
            db.refresh(new_lead)
            
            # Track new lead conversion event
            scoring_service = LeadScoringService(db)
            await scoring_service.track_event(
                lead_id=new_lead.id,
                event_type="lead_capture",
                event_category="conversion",
                event_action="email_submitted",
                score_impact=10,
                metadata={
                    "utm_source": lead_data.utm_source,
                    "utm_campaign": lead_data.utm_campaign,
                    "consent_given": lead_data.marketing_consent
                }
            )
            
            logger.info(f"New lead created successfully: {new_lead.id}")
            return LeadResponse.from_orm(new_lead)
    
    except Exception as e:
        logger.error(f"Error capturing lead {lead_data.email}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to capture lead information"
        )


@router.post(
    "/sessions",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start AI assessment session",
    description="Initialize personalized AI assessment session with dynamic question generation"
)
@rate_limit(requests=10, window=60)  # 10 session starts per minute
async def start_assessment_session(
    request: Request,
    session_data: SessionStartRequest,
    db: Session = Depends(get_db)
) -> SessionResponse:
    """
    Start a new freemium assessment session for a lead.
    
    Creates a FreemiumAssessmentSession with:
    - Secure session token generation
    - AI-driven question personalization
    - Progress tracking initialization
    - Lead scoring event tracking
    """
    try:
        # Find the lead by email
        lead = db.query(AssessmentLead).filter_by(email=session_data.lead_email).first()
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lead not found. Please capture lead information first."
            )
        
        logger.info(f"Starting assessment session for lead: {lead.id}")
        
        # Initialize FreemiumAssessmentService
        assessment_service = FreemiumAssessmentService(db)
        
        # Create new assessment session
        session = await assessment_service.create_session(
            lead_id=lead.id,
            business_type=session_data.business_type,
            company_size=session_data.company_size,
            assessment_type=session_data.assessment_type,
            personalization_data={
                "industry_focus": session_data.industry_focus,
                "compliance_frameworks": session_data.compliance_frameworks,
                "priority_areas": session_data.priority_areas
            }
        )
        
        # Update lead activity and score
        lead.last_activity_at = datetime.utcnow()
        lead.lead_score += 15  # Assessment start bonus
        db.commit()
        
        # Track assessment start event
        scoring_service = LeadScoringService(db)
        await scoring_service.track_event(
            lead_id=lead.id,
            event_type="assessment_start",
            event_category="engagement",
            event_action="started_assessment",
            score_impact=15,
            session_id=str(session.id),
            metadata={
                "business_type": session_data.business_type,
                "assessment_type": session_data.assessment_type
            }
        )
        
        logger.info(f"Assessment session created: {session.id}")
        return SessionResponse.from_orm(session)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting assessment session: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start assessment session"
        )


@router.get(
    "/sessions/{session_token}",
    response_model=SessionResponse,
    summary="Get assessment session progress",
    description="Retrieve current session state, progress, and next question"
)
@rate_limit(requests=30, window=60)  # 30 requests per minute for progress checks
async def get_session_progress(
    session_token: str,
    db: Session = Depends(get_db)
) -> SessionResponse:
    """
    Get current assessment session progress and state.
    
    Returns:
    - Session progress percentage
    - Current question information
    - Questions answered count
    - Session expiration status
    """
    try:
        # Find session by token
        session = db.query(FreemiumAssessmentSession).filter_by(
            session_token=session_token
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment session not found"
            )
        
        # Check if session is expired
        if session.is_expired():
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Assessment session has expired"
            )
        
        logger.info(f"Retrieved session progress: {session.id}")
        return SessionResponse.from_orm(session)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving session {session_token}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve session progress"
        )


@router.post(
    "/sessions/{session_token}/answers",
    response_model=dict,
    summary="Submit assessment answers",
    description="Submit answers and get next AI-generated question with scoring"
)
@rate_limit(requests=25, window=60)  # 25 answer submissions per minute
async def submit_assessment_answer(
    session_token: str,
    answer_data: AnswerSubmissionRequest,
    db: Session = Depends(get_db)
) -> dict:
    """
    Submit an answer to the current assessment question.
    
    Processes:
    - Answer validation and storage
    - AI-driven question progression
    - Dynamic lead scoring based on responses
    - Next question generation
    """
    try:
        # Find and validate session
        session = db.query(FreemiumAssessmentSession).filter_by(
            session_token=session_token
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment session not found"
            )
        
        if session.is_expired():
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Assessment session has expired"
            )
        
        logger.info(f"Processing answer for session: {session.id}")
        
        # Initialize assessment service
        assessment_service = FreemiumAssessmentService(db)
        
        # Process the answer and get next question
        result = await assessment_service.process_answer(
            session_id=session.id,
            question_id=answer_data.question_id,
            answer=answer_data.answer,
            answer_confidence=answer_data.answer_confidence,
            time_spent_seconds=answer_data.time_spent_seconds
        )
        
        # Calculate score impact based on answer
        score_impact = assessment_service.calculate_answer_score_impact(
            question_id=answer_data.question_id,
            answer=answer_data.answer,
            confidence=answer_data.answer_confidence
        )
        
        # Track answer submission event
        scoring_service = LeadScoringService(db)
        await scoring_service.track_event(
            lead_id=session.lead_id,
            event_type="question_answered",
            event_category="assessment",
            event_action="submitted_answer",
            score_impact=score_impact,
            session_id=str(session.id),
            metadata={
                "question_id": answer_data.question_id,
                "answer_length": len(str(answer_data.answer)),
                "time_spent_seconds": answer_data.time_spent_seconds,
                "confidence": answer_data.answer_confidence
            }
        )
        
        logger.info(f"Answer processed successfully for session: {session.id}")
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing answer for session {session_token}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process assessment answer"
        )


@router.get(
    "/sessions/{session_token}/results",
    response_model=AssessmentResultsResponse,
    summary="Get AI assessment results",
    description="Generate comprehensive assessment results with AI insights and conversion opportunities"
)
@rate_limit(requests=15, window=60)  # 15 results requests per minute
async def get_assessment_results(
    session_token: str,
    db: Session = Depends(get_db)
) -> AssessmentResultsResponse:
    """
    Generate and return comprehensive assessment results.
    
    Provides:
    - AI-generated compliance score and risk assessment
    - Personalized recommendations based on answers
    - Identified compliance gaps and priorities
    - Conversion opportunities and next steps
    """
    try:
        # Find and validate session
        session = db.query(FreemiumAssessmentSession).filter_by(
            session_token=session_token
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Assessment session not found"
            )
        
        if session.is_expired():
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Assessment session has expired"
            )
        
        logger.info(f"Generating results for session: {session.id}")
        
        # Initialize assessment service
        assessment_service = FreemiumAssessmentService(db)
        
        # Generate comprehensive results
        results = await assessment_service.generate_results(session.id)
        
        # Mark results as viewed for conversion tracking
        if not session.results_viewed:
            session.results_viewed = True
            session.results_viewed_at = datetime.utcnow()
            db.commit()
            
            # Track results view event with high score impact
            scoring_service = LeadScoringService(db)
            await scoring_service.track_event(
                lead_id=session.lead_id,
                event_type="results_viewed",
                event_category="conversion",
                event_action="viewed_assessment_results",
                score_impact=25,  # High value conversion event
                session_id=str(session.id),
                metadata={
                    "completion_status": session.completion_status,
                    "questions_answered": session.questions_answered,
                    "compliance_score": results.get("compliance_score")
                }
            )
            
            # Update lead score for completing assessment
            lead = db.query(AssessmentLead).filter_by(id=session.lead_id).first()
            if lead:
                lead.lead_score += 25
                lead.lead_status = "qualified"  # Mark as qualified lead
                lead.last_activity_at = datetime.utcnow()
                db.commit()
        
        logger.info(f"Results generated successfully for session: {session.id}")
        return AssessmentResultsResponse(**results)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating results for session {session_token}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate assessment results"
        )


# ============================================================================
# HEALTH CHECK AND UTILITY ENDPOINTS
# ============================================================================

@router.get(
    "/health",
    summary="Freemium API health check",
    description="Check freemium API health and database connectivity"
)
async def health_check(db: Session = Depends(get_db)) -> dict:
    """Health check endpoint for freemium API router."""
    try:
        # Test database connectivity
        db.execute("SELECT 1")
        
        # Check freemium tables exist
        lead_count = db.query(AssessmentLead).count()
        session_count = db.query(FreemiumAssessmentSession).count()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "leads_count": lead_count,
            "sessions_count": session_count,
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )