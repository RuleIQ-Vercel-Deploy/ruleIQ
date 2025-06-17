from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies.auth import get_current_active_user
from api.schemas.models import FrameworkRecommendation, FrameworkResponse
from database.user import User
from services.framework_service import get_framework_by_id, get_relevant_frameworks

router = APIRouter()

@router.get("/", response_model=List[FrameworkResponse])
async def list_frameworks(
    current_user: User = Depends(get_current_active_user)
):
    frameworks = get_relevant_frameworks(current_user)
    return [fw["framework"] for fw in frameworks]

@router.get("/recommendations", response_model=List[FrameworkRecommendation])
async def get_framework_recommendations(
    current_user: User = Depends(get_current_active_user)
):
    recommendations = get_relevant_frameworks(current_user)
    return [
        FrameworkRecommendation(
            framework=rec["framework"],
            relevance_score=rec["relevance_score"],
            reasons=rec["reasons"],
            priority=rec["priority"]
        )
        for rec in recommendations
    ]

@router.get("/{framework_id}", response_model=FrameworkResponse)
async def get_framework(
    framework_id: UUID,
    current_user: User = Depends(get_current_active_user)
):
    framework = get_framework_by_id(current_user, framework_id)
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    return framework
