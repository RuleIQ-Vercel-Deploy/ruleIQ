from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.dependencies.auth import get_current_active_user
from api.schemas.models import (
    AssessmentQuestion,
    AssessmentResponseUpdate,
    AssessmentSessionCreate,
    AssessmentSessionResponse,
)
from database.user import User
from services.assessment_service import AssessmentService


class QuickAssessmentRequest(BaseModel):
    business_profile_id: str
    assessment_type: str
    industry_standard: bool


class FrameworkInfo(BaseModel):
    name: str
    description: str = ""


class QuickRecommendation(BaseModel):
    framework: FrameworkInfo
    priority: str = "medium"
    description: str = ""


class QuickAssessmentResponse(BaseModel):
    recommendations: List[QuickRecommendation]

router = APIRouter()

@router.post("/quick", response_model=QuickAssessmentResponse)
async def quick_assessment(
    request: QuickAssessmentRequest
):
    """Generate quick compliance recommendations based on business profile."""

    # For now, return basic recommendations based on industry standards
    # This would typically integrate with the assessment service for more sophisticated analysis
    recommendations = []

    # Always recommend GDPR for EU businesses or those handling EU data
    recommendations.append(QuickRecommendation(
        framework=FrameworkInfo(
            name="GDPR (General Data Protection Regulation)",
            description="EU data protection regulation"
        ),
        priority="high",
        description="Essential for businesses handling personal data of EU residents"
    ))

    # Add industry-specific recommendations
    if request.industry_standard:
        recommendations.append(QuickRecommendation(
            framework=FrameworkInfo(
                name="ISO 27001",
                description="Information security management standard"
            ),
            priority="medium",
            description="Industry standard for information security management"
        ))

        recommendations.append(QuickRecommendation(
            framework=FrameworkInfo(
                name="SOC 2",
                description="Security and availability controls"
            ),
            priority="medium",
            description="Important for service organizations handling customer data"
        ))

    return QuickAssessmentResponse(recommendations=recommendations)

@router.post("/start", response_model=AssessmentSessionResponse)
async def start_assessment(
    session_data: AssessmentSessionCreate,
    current_user: User = Depends(get_current_active_user),
    assessment_service: AssessmentService = Depends(AssessmentService) # Inject service
):
    session = assessment_service.start_assessment_session(current_user, session_data.session_type)
    return session

@router.get("/current", response_model=AssessmentSessionResponse)
async def get_current_session(
    current_user: User = Depends(get_current_active_user),
    assessment_service: AssessmentService = Depends(AssessmentService) # Inject service
):
    session = assessment_service.get_active_assessment_session(current_user) # Corrected method name
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active assessment session"
        )
    return session

@router.get("/questions/{stage}", response_model=List[AssessmentQuestion])
async def get_questions(
    stage: int,
    current_user: User = Depends(get_current_active_user),
    assessment_service: AssessmentService = Depends(AssessmentService) # Inject service
):
    questions = assessment_service.get_assessment_questions_for_stage(current_user, stage) # Corrected method name
    return questions

@router.put("/{session_id}/response")
async def update_response(
    session_id: UUID,
    response_data: AssessmentResponseUpdate,
    current_user: User = Depends(get_current_active_user),
    assessment_service: AssessmentService = Depends(AssessmentService) # Inject service
):
    session = assessment_service.update_assessment_response(
        current_user,
        session_id,
        response_data.question_id,
        response_data.response,
        response_data.move_to_next_stage
    )
    return session

@router.post("/{session_id}/complete", response_model=AssessmentSessionResponse)
async def complete_assessment(
    session_id: UUID,
    current_user: User = Depends(get_current_active_user),
    assessment_service: AssessmentService = Depends(AssessmentService) # Inject service
):
    session = assessment_service.complete_assessment_session(current_user, session_id)
    return session
