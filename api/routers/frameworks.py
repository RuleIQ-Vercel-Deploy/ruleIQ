from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.database import get_async_db
from api.dependencies.rbac_auth import UserWithRoles, require_permission
from api.schemas.models import ComplianceFrameworkResponse, FrameworkRecommendation
from services.framework_service import get_framework_by_id, get_relevant_frameworks

router = APIRouter()


@router.get("/", response_model=List[ComplianceFrameworkResponse])
async def list_frameworks(
    current_user: UserWithRoles = Depends(require_permission("user_list")),
    db: AsyncSession = Depends(get_async_db),
):
    """List all available frameworks - simplified for compliance wizard."""
    from database.compliance_framework import ComplianceFramework
    from sqlalchemy.future import select

    # Get all active frameworks directly from database (bypass RBAC for now)
    result = await db.execute(select(ComplianceFramework))
    frameworks = result.scalars().all()
    print(f"DEBUG: Found {len(frameworks)} total frameworks")

    # Filter active ones in Python for now
    active_frameworks = [fw for fw in frameworks if fw.is_active]
    print(f"DEBUG: Found {len(active_frameworks)} active frameworks")

    # Convert to response format
    return [
        ComplianceFrameworkResponse(
            id=fw.id,
            name=fw.name,
            description=fw.description or "",
            category=fw.category or "general",
            version=fw.version or "1.0",
            controls=[],  # Simplified for compliance wizard
        )
        for fw in active_frameworks
    ]


@router.get("/recommendations", response_model=List[FrameworkRecommendation])
async def get_framework_recommendations(
    current_user: UserWithRoles = Depends(require_permission("framework_list")),
    db: AsyncSession = Depends(get_async_db),
):
    """Get framework recommendations filtered by user's access permissions."""
    recommendations = await get_relevant_frameworks(db, current_user)

    # Filter recommendations based on user's framework access permissions
    accessible_recommendations = []
    for rec in recommendations:
        framework = rec["framework"]
        framework_id = str(framework.id)

        # Check if user has access to this specific framework
        has_access = any(af["id"] == framework_id for af in current_user.accessible_frameworks)

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
        has_access = any(af["id"] == framework_id for af in current_user.accessible_frameworks)

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


@router.get("/all-public", response_model=List[ComplianceFrameworkResponse])
async def list_all_public_frameworks(
    current_user: UserWithRoles = Depends(require_permission("user_list")),
    db: AsyncSession = Depends(get_async_db),
):
    """List all available frameworks without RBAC restrictions - for compliance wizard."""
    from database.compliance_framework import ComplianceFramework
    from sqlalchemy.future import select

    # Get all active frameworks directly from database
    result = await db.execute(select(ComplianceFramework).where(ComplianceFramework.is_active))
    frameworks = result.scalars().all()

    # Convert to response format
    return [
        ComplianceFrameworkResponse(
            id=fw.id,
            name=fw.name,
            description=fw.description or "",
            category=fw.category or "general",
            version=fw.version or "1.0",
            controls=[],  # Simplified for compliance wizard
        )
        for fw in frameworks
    ]


@router.get("/{framework_id}", response_model=ComplianceFrameworkResponse)
async def get_framework(
    framework_id: UUID,
    current_user: UserWithRoles = Depends(require_permission("framework_list")),
    db: AsyncSession = Depends(get_async_db),
):
    """Get a specific framework if user has access to it."""
    # Check if user has access to this specific framework
    has_access = any(af["id"] == str(framework_id) for af in current_user.accessible_frameworks)

    if not has_access:
        raise HTTPException(
            status_code=403,
            detail="Access denied: You don't have permission to access this framework",
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
