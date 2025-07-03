"""
AI Assessment Assistant API Router

Dedicated endpoints for AI-powered assessment features including:
- Question help and guidance
- Follow-up question generation
- Assessment analysis and insights
- Personalized recommendations
- Performance metrics and feedback
"""

import logging
from typing import Dict, Any, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime

from api.dependencies.auth import get_current_active_user
from api.dependencies.database import get_async_db
from database.user import User
from database.business_profile import BusinessProfile
from services.ai import ComplianceAssistant
from services.ai.exceptions import (
    AIServiceException, AITimeoutException, AIQuotaExceededException,
    handle_ai_error
)
from core.exceptions import NotFoundException
from api.middleware.ai_rate_limiter import (
    ai_help_rate_limit,
    ai_followup_rate_limit,
    ai_analysis_rate_limit,
    ai_recommendations_rate_limit,
    add_rate_limit_headers,
    ai_rate_limit_stats,
    get_ai_rate_limit_stats
)

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai/assessments", tags=["AI Assessment Assistant"])

# Request/Response Models
class AIHelpRequest(BaseModel):
    question_id: str
    question_text: str
    framework_id: str
    section_id: Optional[str] = None
    user_context: Optional[Dict[str, Any]] = None

class AIHelpResponse(BaseModel):
    guidance: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    related_topics: Optional[List[str]] = None
    follow_up_suggestions: Optional[List[str]] = None
    source_references: Optional[List[str]] = None
    request_id: str
    generated_at: str

class AIFollowUpRequest(BaseModel):
    framework_id: str
    current_answers: Dict[str, Any]
    business_context: Optional[Dict[str, Any]] = None
    max_questions: int = Field(default=3, ge=1, le=10)

class AIFollowUpQuestion(BaseModel):
    id: str
    text: str
    type: str
    options: Optional[List[Dict[str, str]]] = None
    reasoning: str
    priority: str

class AIFollowUpResponse(BaseModel):
    questions: List[AIFollowUpQuestion]
    total_generated: int
    request_id: str
    generated_at: str

class AIAnalysisRequest(BaseModel):
    assessment_results: Dict[str, Any]
    framework_id: str
    business_profile_id: str

class Gap(BaseModel):
    id: str
    section: str
    severity: str
    description: str
    impact: str
    current_state: str
    target_state: str

class Recommendation(BaseModel):
    id: str
    title: str
    description: str
    priority: str
    effort_estimate: str
    impact_score: float
    resources: Optional[List[str]] = None
    implementation_steps: Optional[List[str]] = None

class AIAnalysisResponse(BaseModel):
    gaps: List[Gap]
    recommendations: List[Recommendation]
    risk_assessment: Dict[str, Any]
    compliance_insights: Dict[str, Any]
    evidence_requirements: List[Dict[str, Any]]
    request_id: str
    generated_at: str

class AIRecommendationRequest(BaseModel):
    gaps: List[Dict[str, Any]]
    business_profile: Dict[str, Any]
    existing_policies: Optional[List[str]] = None
    industry_context: Optional[str] = None
    timeline_preferences: Optional[str] = "standard"

class ImplementationPhase(BaseModel):
    phase_number: int
    phase_name: str
    duration_weeks: int
    tasks: List[str]
    dependencies: List[str]

class ImplementationPlan(BaseModel):
    phases: List[ImplementationPhase]
    total_timeline_weeks: int
    resource_requirements: List[str]

class AIRecommendationResponse(BaseModel):
    recommendations: List[Recommendation]
    implementation_plan: ImplementationPlan
    success_metrics: List[str]
    request_id: str
    generated_at: str

class AIFeedbackRequest(BaseModel):
    interaction_id: str
    helpful: bool
    rating: Optional[int] = Field(None, ge=1, le=5)
    comments: Optional[str] = None
    improvement_suggestions: Optional[List[str]] = None

class AIMetricsResponse(BaseModel):
    response_times: Dict[str, float]
    accuracy_score: float
    user_satisfaction: float
    total_interactions: int
    quota_usage: Dict[str, Any]

# Helper function to get business profile
async def get_user_business_profile(
    user: User,
    db: AsyncSession,
    business_profile_id: Optional[str] = None
) -> BusinessProfile:
    """Get business profile for the current user."""
    if business_profile_id:
        # Get specific business profile
        result = await db.execute(
            select(BusinessProfile).where(
                BusinessProfile.id == business_profile_id,
                BusinessProfile.user_id == str(user.id)
            )
        )
        profile = result.scalars().first()
    else:
        # Get user's default business profile
        result = await db.execute(
            select(BusinessProfile).where(BusinessProfile.user_id == str(user.id))
        )
        profile = result.scalars().first()
    
    if not profile:
        raise NotFoundException("Business profile not found")
    
    return profile

# AI Assessment Endpoints

@router.post("/{framework_id}/help", response_model=AIHelpResponse)
async def get_question_help(
    framework_id: str,
    request: AIHelpRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
    _: None = Depends(ai_help_rate_limit)
):
    """
    Get AI-powered help for a specific assessment question.
    
    Provides contextual guidance, related topics, and follow-up suggestions
    based on the question, framework, and user's business context.
    """
    try:
        # Get business profile for context
        profile = await get_user_business_profile(current_user, db)
        
        # Initialize AI assistant
        assistant = ComplianceAssistant(db)

        # Generate AI guidance using ComplianceAssistant (Phase 2.2 integration)
        guidance_response = await assistant.get_assessment_help(
            question_id=request.question_id,
            question_text=request.question_text,
            framework_id=framework_id,
            business_profile_id=UUID(str(profile.id)),
            section_id=request.section_id or "",
            user_context=request.user_context or {}
        )
        
        # Record request for statistics
        ai_rate_limit_stats.record_request("help", rate_limited=False)

        return AIHelpResponse(
            guidance=guidance_response["guidance"],
            confidence_score=guidance_response.get("confidence_score", 0.8),
            related_topics=guidance_response.get("related_topics", []),
            follow_up_suggestions=guidance_response.get("follow_up_suggestions", []),
            source_references=guidance_response.get("source_references", []),
            request_id=guidance_response.get("request_id", f"help_{framework_id}_{request.question_id}"),
            generated_at=guidance_response.get("generated_at", "")
        )
        
    except AIServiceException as e:
        logger.error(f"AI service error in question help: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI assistance temporarily unavailable: {e.message}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in question help: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to provide AI assistance at this time"
        )

@router.post("/followup", response_model=AIFollowUpResponse)
async def generate_followup_questions(
    request: AIFollowUpRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
    _: None = Depends(ai_followup_rate_limit)
):
    """
    Generate AI-powered follow-up questions based on current assessment responses.
    
    Analyzes user's answers to suggest additional questions that could provide
    deeper insights into their compliance posture.
    """
    try:
        # Get business profile for context
        profile = await get_user_business_profile(current_user, db)
        
        # Initialize AI assistant
        assistant = ComplianceAssistant(db)

        # Generate follow-up questions using ComplianceAssistant (Phase 2.2 integration)
        followup_response = await assistant.generate_assessment_followup(
            current_answers=request.current_answers,
            framework_id=request.framework_id,
            business_profile_id=UUID(str(profile.id)),
            assessment_context=request.business_context or {}
        )
        
        # Convert to response format
        questions = [
            AIFollowUpQuestion(
                id=q["id"],
                text=q["text"],
                type=q["type"],
                options=q.get("options"),
                reasoning=q["reasoning"],
                priority=q["priority"]
            )
            for q in followup_response["questions"]
        ]
        
        # Record request for statistics
        ai_rate_limit_stats.record_request("followup", rate_limited=False)

        return AIFollowUpResponse(
            questions=questions,
            total_generated=len(questions),
            request_id=followup_response.get("request_id", f"followup_{request.framework_id}"),
            generated_at=followup_response.get("generated_at", "")
        )
        
    except AIServiceException as e:
        logger.error(f"AI service error in follow-up generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unable to generate follow-up questions: {e.message}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in follow-up generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate follow-up questions at this time"
        )

@router.post("/analysis", response_model=AIAnalysisResponse)
async def analyze_assessment_results(
    request: AIAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
    _: None = Depends(ai_analysis_rate_limit)
):
    """
    Perform comprehensive AI analysis of assessment results.

    Analyzes completed assessment to identify gaps, risks, and provide
    detailed compliance insights with evidence requirements.
    """
    try:
        # Get business profile
        profile = await get_user_business_profile(
            current_user, db, request.business_profile_id
        )

        # Initialize AI assistant
        assistant = ComplianceAssistant(db)

        # Perform comprehensive analysis using ComplianceAssistant (Phase 2.2 integration)
        analysis_response = await assistant.analyze_assessment_results(
            assessment_results=request.assessment_results,
            framework_id=request.framework_id,
            business_profile_id=UUID(str(profile.id))
        )

        # Convert gaps to response format
        gaps = [
            Gap(
                id=gap["id"],
                section=gap["section"],
                severity=gap["severity"],
                description=gap["description"],
                impact=gap["impact"],
                current_state=gap["current_state"],
                target_state=gap["target_state"]
            )
            for gap in analysis_response["gaps"]
        ]

        # Convert recommendations to response format
        recommendations = [
            Recommendation(
                id=rec["id"],
                title=rec["title"],
                description=rec["description"],
                priority=rec["priority"],
                effort_estimate=rec["effort_estimate"],
                impact_score=rec["impact_score"],
                resources=rec.get("resources"),
                implementation_steps=rec.get("implementation_steps")
            )
            for rec in analysis_response["recommendations"]
        ]

        return AIAnalysisResponse(
            gaps=gaps,
            recommendations=recommendations,
            risk_assessment=analysis_response["risk_assessment"],
            compliance_insights=analysis_response["compliance_insights"],
            evidence_requirements=analysis_response["evidence_requirements"],
            request_id=analysis_response.get("request_id", f"analysis_{request.framework_id}"),
            generated_at=analysis_response.get("generated_at", "")
        )

    except AIServiceException as e:
        logger.error(f"AI service error in assessment analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unable to analyze assessment: {e.message}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in assessment analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to analyze assessment results at this time"
        )

@router.post("/recommendations", response_model=AIRecommendationResponse)
async def generate_personalized_recommendations(
    request: AIRecommendationRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
    _: None = Depends(ai_recommendations_rate_limit)
):
    """
    Generate personalized compliance recommendations with implementation plans.

    Creates detailed, actionable recommendations based on identified gaps,
    business context, and timeline preferences.
    """
    try:
        # Initialize AI assistant
        assistant = ComplianceAssistant(db)

        # Generate personalized recommendations using ComplianceAssistant (Phase 2.2 integration)
        rec_response = await assistant.get_assessment_recommendations(
            gaps=request.gaps,
            business_profile=request.business_profile,
            framework_id="general",  # Extract from request if available
            existing_policies=request.existing_policies or [],
            industry_context=request.industry_context or "",
            timeline_preferences=request.timeline_preferences or "standard"
        )

        # Convert recommendations
        recommendations = [
            Recommendation(
                id=rec["id"],
                title=rec["title"],
                description=rec["description"],
                priority=rec["priority"],
                effort_estimate=rec["effort_estimate"],
                impact_score=rec["impact_score"],
                resources=rec.get("resources"),
                implementation_steps=rec.get("implementation_steps")
            )
            for rec in rec_response["recommendations"]
        ]

        # Convert implementation plan
        phases = [
            ImplementationPhase(
                phase_number=phase["phase_number"],
                phase_name=phase["phase_name"],
                duration_weeks=phase["duration_weeks"],
                tasks=phase["tasks"],
                dependencies=phase["dependencies"]
            )
            for phase in rec_response["implementation_plan"]["phases"]
        ]

        implementation_plan = ImplementationPlan(
            phases=phases,
            total_timeline_weeks=rec_response["implementation_plan"]["total_timeline_weeks"],
            resource_requirements=rec_response["implementation_plan"]["resource_requirements"]
        )

        return AIRecommendationResponse(
            recommendations=recommendations,
            implementation_plan=implementation_plan,
            success_metrics=rec_response["success_metrics"],
            request_id=rec_response.get("request_id", f"recommendations_{current_user.id}"),
            generated_at=rec_response.get("generated_at", "")
        )

    except AIServiceException as e:
        logger.error(f"AI service error in recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Unable to generate recommendations: {e.message}"
        )
    except Exception as e:
        logger.error(f"Unexpected error in recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to generate recommendations at this time"
        )

@router.post("/feedback")
async def submit_ai_feedback(
    request: AIFeedbackRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Submit feedback on AI assistance quality.

    Collects user feedback to improve AI performance and track satisfaction metrics.
    """
    try:
        # Log feedback for analytics
        logger.info(
            f"AI feedback received from user {current_user.id}: "
            f"helpful={request.helpful}, rating={request.rating}"
        )

        # In a full implementation, you would:
        # 1. Store feedback in database
        # 2. Update AI performance metrics
        # 3. Trigger model retraining if needed

        return {"message": "Feedback submitted successfully", "status": "received"}

    except Exception as e:
        logger.error(f"Error submitting AI feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to submit feedback at this time"
        )

@router.get("/metrics", response_model=AIMetricsResponse)
async def get_ai_metrics(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
    days: int = Query(default=30, ge=1, le=365, description="Number of days to include in metrics")
):
    """
    Get AI performance metrics for admin users.

    Returns response times, accuracy scores, user satisfaction, and quota usage.
    """
    try:
        # Check if user has admin permissions (implement based on your auth system)
        # if not current_user.is_admin:
        #     raise HTTPException(status_code=403, detail="Admin access required")

        # Mock metrics - in production, fetch from analytics database
        metrics = {
            "response_times": {
                "avg": 1.2,
                "p95": 3.5,
                "p99": 8.1
            },
            "accuracy_score": 0.87,
            "user_satisfaction": 4.2,
            "total_interactions": 1247,
            "quota_usage": {
                "requests_used": 8432,
                "requests_limit": 10000,
                "tokens_used": 245678,
                "tokens_limit": 500000,
                "cost_usd": 12.34
            }
        }

        return AIMetricsResponse(**metrics)

    except Exception as e:
        logger.error(f"Error retrieving AI metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to retrieve AI metrics at this time"
        )


@router.get("/rate-limit-stats")
async def get_rate_limit_statistics(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get AI rate limiting statistics.

    Returns current rate limiting statistics including total requests,
    rate limited requests, and per-operation breakdowns.
    """
    try:
        stats = get_ai_rate_limit_stats()

        return {
            "rate_limit_stats": stats,
            "current_limits": {
                "ai_help": "10 requests/minute",
                "ai_followup": "5 requests/minute",
                "ai_analysis": "3 requests/minute",
                "ai_recommendations": "3 requests/minute"
            },
            "burst_allowances": {
                "ai_help": 2,
                "ai_followup": 1,
                "ai_analysis": 1,
                "ai_recommendations": 1
            },
            "generated_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Error retrieving rate limit stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve rate limit statistics"
        )


# Helper methods for AI service integration
async def _get_mock_guidance_response(question_text: str, framework: str) -> Dict[str, Any]:
    """Mock AI guidance response - replace with actual AI service call"""
    return {
        "guidance": f"For the question '{question_text}' in {framework}, consider implementing proper documentation and regular reviews. Ensure you have clear policies in place and that all stakeholders understand their responsibilities.",
        "confidence_score": 0.85,
        "related_topics": ["Documentation", "Policy Management", "Stakeholder Training"],
        "follow_up_suggestions": [
            "Do you have documented procedures for this process?",
            "How often do you review and update these policies?",
            "Who is responsible for ensuring compliance in this area?"
        ],
        "source_references": [f"{framework} Article 5", "Best Practice Guidelines"],
        "request_id": f"help_{framework}_{hash(question_text) % 10000}",
        "generated_at": datetime.utcnow().isoformat()
    }

async def _get_mock_followup_response(framework: str, answers: Dict[str, Any]) -> Dict[str, Any]:
    """Mock follow-up questions response - replace with actual AI service call"""
    return {
        "questions": [
            {
                "id": f"followup_{framework}_1",
                "text": "Based on your previous answers, do you have automated monitoring in place for data processing activities?",
                "type": "radio",
                "options": [
                    {"value": "yes", "label": "Yes, fully automated"},
                    {"value": "partial", "label": "Partially automated"},
                    {"value": "no", "label": "No automation"}
                ],
                "reasoning": "Your responses indicate potential gaps in monitoring capabilities",
                "priority": "high"
            }
        ],
        "request_id": f"followup_{framework}_{hash(str(answers)) % 10000}",
        "generated_at": datetime.utcnow().isoformat()
    }

async def _get_mock_analysis_response(framework: str, assessment_results: Dict[str, Any]) -> Dict[str, Any]:
    """Mock analysis response - replace with actual AI service call"""
    return {
        "gaps": [
            {
                "id": "gap_1",
                "section": "Data Retention",
                "severity": "high",
                "description": "No documented data retention policy found",
                "impact": "Potential compliance violations and legal risks",
                "current_state": "Ad-hoc data deletion",
                "target_state": "Formal retention policy with automated enforcement"
            }
        ],
        "recommendations": [
            {
                "id": "rec_1",
                "title": "Implement Data Retention Policy",
                "description": "Create and implement a comprehensive data retention policy",
                "priority": "high",
                "effort_estimate": "2-4 weeks",
                "impact_score": 8.5,
                "resources": ["DPO", "Legal Team", "IT Team"],
                "implementation_steps": [
                    "Audit current data storage practices",
                    "Define retention periods by data category",
                    "Implement automated deletion systems"
                ]
            }
        ],
        "risk_assessment": {
            "overall_risk_level": "medium",
            "risk_score": 6.5,
            "key_risk_areas": ["Data Retention", "Access Controls", "Documentation"]
        },
        "compliance_insights": {
            "maturity_level": "Developing",
            "score_breakdown": {"Data Processing": 75, "Subject Rights": 82},
            "improvement_priority": ["Data Retention", "Security Controls"]
        },
        "evidence_requirements": [
            {
                "priority": "high",
                "evidence_type": "Policy Documentation",
                "description": "Documented data retention policy",
                "control_mapping": ["GDPR Article 5"]
            }
        ],
        "request_id": f"analysis_{framework}_{hash(str(assessment_results)) % 10000}",
        "generated_at": datetime.utcnow().isoformat()
    }

async def _get_mock_recommendations_response(gaps: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Mock recommendations response - replace with actual AI service call"""
    return {
        "recommendations": [
            {
                "id": "rec_1",
                "title": "Implement Data Retention Policy",
                "description": "Create comprehensive data retention policy with automated enforcement",
                "priority": "high",
                "effort_estimate": "2-4 weeks",
                "impact_score": 8.5,
                "resources": ["DPO", "Legal Team"],
                "implementation_steps": [
                    "Audit current data storage",
                    "Define retention periods",
                    "Implement automation"
                ]
            }
        ],
        "implementation_plan": {
            "phases": [
                {
                    "phase_number": 1,
                    "phase_name": "Foundation & Documentation",
                    "duration_weeks": 4,
                    "tasks": ["Document current practices", "Create policy", "Get approval"],
                    "dependencies": []
                }
            ],
            "total_timeline_weeks": 10,
            "resource_requirements": ["DPO (0.5 FTE)", "Legal Counsel"]
        },
        "success_metrics": [
            "100% of data categories have documented retention periods",
            "Automated deletion operational for 80% of data types"
        ],
        "request_id": f"recommendations_{hash(str(gaps)) % 10000}",
        "generated_at": datetime.utcnow().isoformat()
    }
