from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_active_user
from api.dependencies.database import get_async_db
from api.schemas.models import FrameworkRecommendation, ComplianceFrameworkResponse, ComplianceFrameworkResponse
from database.user import User
from services.framework_service import get_framework_by_id, get_relevant_frameworks

router = APIRouter()

@router.get("/", response_model=List[ComplianceFrameworkResponse])
async def list_frameworks(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    frameworks = await get_relevant_frameworks(db, current_user)
    return [fw["framework"] for fw in frameworks]

@router.get("/recommendations", response_model=List[FrameworkRecommendation])
async def get_framework_recommendations(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    recommendations = await get_relevant_frameworks(db, current_user)
    return [
        FrameworkRecommendation(
            framework=rec["framework"],
            relevance_score=rec["relevance_score"],
            reasons=rec.get("reasons", []),
            priority=rec.get("priority", "medium")
        )
        for rec in recommendations
    ]

@router.get("/recommendations/{business_profile_id}", response_model=List[FrameworkRecommendation])
async def get_framework_recommendations_for_profile(
    business_profile_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get framework recommendations for a specific business profile."""
    recommendations = await get_relevant_frameworks(db, current_user)
    return [
        FrameworkRecommendation(
            framework=rec["framework"],
            relevance_score=rec["relevance_score"],
            reasons=rec.get("reasons", []),
            priority=rec.get("priority", "medium")
        )
        for rec in recommendations
    ]

@router.get("/{framework_id}", response_model=ComplianceFrameworkResponse)
async def get_framework(
    framework_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    framework = await get_framework_by_id(db, current_user, framework_id)
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")

    # Convert to proper response format with controls
    controls = []
    if framework.control_domains:
        controls = [{"name": domain, "description": f"{domain} controls"} for domain in framework.control_domains]

    return ComplianceFrameworkResponse(
        id=framework.id,
        name=framework.name,
        description=framework.description,
        category=framework.category,
        version=framework.version,
        controls=controls
    )
