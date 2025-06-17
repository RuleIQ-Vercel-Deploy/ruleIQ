from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies.auth import get_current_active_user
from api.schemas.models import (
    AssessmentQuestion,
    AssessmentResponseUpdate,
    AssessmentSessionCreate,
    AssessmentSessionResponse,
)
from database.user import User
from services.assessment_service import (
    complete_assessment_session,
    get_assessment_questions,
    get_current_assessment_session,
    start_assessment_session,
    update_assessment_response,
)

router = APIRouter()

@router.post("/start", response_model=AssessmentSessionResponse)
async def start_assessment(
    session_data: AssessmentSessionCreate,
    current_user: User = Depends(get_current_active_user)
):
    session = start_assessment_session(current_user, session_data.session_type)
    return session

@router.get("/current", response_model=AssessmentSessionResponse)
async def get_current_session(
    current_user: User = Depends(get_current_active_user)
):
    session = get_current_assessment_session(current_user)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active assessment session"
        )
    return session

@router.get("/questions/{stage}", response_model=List[AssessmentQuestion])
async def get_questions(
    stage: int,
    current_user: User = Depends(get_current_active_user)
):
    questions = get_assessment_questions(current_user, stage)
    return questions

@router.put("/{session_id}/response")
async def update_response(
    session_id: UUID,
    response_data: AssessmentResponseUpdate,
    current_user: User = Depends(get_current_active_user)
):
    session = update_assessment_response(
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
    current_user: User = Depends(get_current_active_user)
):
    session = complete_assessment_session(current_user, session_id)
    return session
