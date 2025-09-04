from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_active_user
from api.dependencies.database import get_async_db
from api.dependencies.rbac_auth import get_current_user_with_roles, UserWithRoles, require_permission
from api.schemas.models import ComplianceFrameworkResponse, FrameworkRecommendation
from database.user import User
from services.framework_service import get_framework_by_id, get_relevant_frameworks

router = APIRouter()


@router.get("/", response_model=List[ComplianceFrameworkResponse])
async def list_frameworks(
    current_user: UserWithRoles = Depends(require_permission("framework_list")), 
    db: AsyncSession = Depends(get_async_db)
):
    """List frameworks accessible to the current user based on their permissions."""
    frameworks = await get_relevant_frameworks(db, current_user)
    
    # Filter frameworks based on user's framework access permissions
    accessible_frameworks = []
    for fw_data in frameworks:
        framework = fw_data["framework"]
        framework_id = str(framework.id)
        
        # Check if user has access to this specific framework
        has_access = any(
            af["id"] == framework_id 
            for af in current_user.accessible_frameworks
        )
        
        if has_access:
            accessible_frameworks.append(framework)
    
    return accessible_frameworks


@router.get("/recommendations", response_model=List[FrameworkRecommendation])
async def get_framework_recommendations(
    current_user: UserWithRoles = Depends(require_permission("framework_list")), 
    db: AsyncSession = Depends(get_async_db)
):
    """Get framework recommendations filtered by user's access permissions."""
    recommendations = await get_relevant_frameworks(db, current_user)
    
    # Filter recommendations based on user's framework access permissions
    accessible_recommendations = []
    for rec in recommendations:
        framework = rec["framework"]
        framework_id = str(framework.id)
        
        # Check if user has access to this specific framework
        has_access = any(
            af["id"] == framework_id 
            for af in current_user.accessible_frameworks
        )
        
        if has_access:
            accessible_recommendations.append(
                FrameworkRecommendation(
                    framework=framework,
                    relevance_score=rec["relevance_score"],
                    reasons=rec.get("reasons", []),
                    priority=rec.get("priority", "medium"),
                )
            )
    
    return accessible_recommendations


@router.get("/recommendations/{business_profile_id}", response_model=List[FrameworkRecommendation])
async def get_framework_recommendations_for_profile(
    business_profile_id: UUID,
    current_user: UserWithRoles = Depends(require_permission("framework_list")),
    db: AsyncSession = Depends(get_async_db),
):
    """Get framework recommendations for a specific business profile."""
    recommendations = await get_relevant_frameworks(db, current_user)
    
    # Filter recommendations based on user's framework access permissions
    accessible_recommendations = []
    for rec in recommendations:
        framework = rec["framework"]
        framework_id = str(framework.id)
        
        # Check if user has access to this specific framework
        has_access = any(
            af["id"] == framework_id 
            for af in current_user.accessible_frameworks
        )
        
        if has_access:
            accessible_recommendations.append(
                FrameworkRecommendation(
                    framework=framework,
                    relevance_score=rec["relevance_score"],
                    reasons=rec.get("reasons", []),
                    priority=rec.get("priority", "medium"),
                )
            )
    
    return accessible_recommendations


@router.get("/{framework_id}", response_model=ComplianceFrameworkResponse)
async def get_framework(
    framework_id: UUID,
    current_user: UserWithRoles = Depends(require_permission("framework_list")),
    db: AsyncSession = Depends(get_async_db),
):
    """Get a specific framework if user has access to it."""
    # Check if user has access to this specific framework
    has_access = any(
        af["id"] == str(framework_id) 
        for af in current_user.accessible_frameworks
    )
    
    if not has_access:
        raise HTTPException(
            status_code=403, 
            detail="Access denied: You don't have permission to access this framework"
        )

    framework = await get_framework_by_id(db, current_user, framework_id)
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")

    # Convert to proper response format with controls
    controls = []
    if framework.control_domains:
        controls = [
            {"name": domain, "description": f"{domain} controls"}
            for domain in framework.control_domains
        ]

    return ComplianceFrameworkResponse(
        id=framework.id,
        name=framework.name,
        description=framework.description,
        category=framework.category,
        version=framework.version,
        controls=controls,
    )
