"""
UK Compliance Frameworks API Router

Provides endpoints for managing UK-specific compliance frameworks.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database.db_setup import get_db
from database.compliance_framework import ComplianceFramework
from api.schemas.compliance import (
    UKFrameworkSchema, FrameworkResponse, FrameworkListResponse,
    FrameworkLoadRequest, FrameworkLoadResponse
)
from services.compliance_loader import UKComplianceLoader, GeographicValidator
from api.dependencies.auth import get_current_active_user
from api.middleware.rate_limiter import RateLimited


router = APIRouter(tags=["UK Compliance"])


@router.get(
    "/frameworks",
    response_model=FrameworkListResponse,
    dependencies=[Depends(RateLimited(requests=100, window=60))]
)
async def get_frameworks(
    region: Optional[str] = Query(None, description="Filter by geographic region"),
    category: Optional[str] = Query(None, description="Filter by framework category"),
    industry: Optional[str] = Query(None, description="Filter by applicable industry"),
    complexity_min: Optional[int] = Query(None, ge=1, le=10),
    complexity_max: Optional[int] = Query(None, ge=1, le=10),
    active_only: bool = Query(True, description="Include only active frameworks"),
    db: Session = Depends(get_db)
):
    """
    Get compliance frameworks with optional filtering.

    Supports filtering by region, category, industry, and complexity.
    """
    query = db.query(ComplianceFramework)

    # Apply filters
    if active_only:
        query = query.filter(ComplianceFramework.is_active)

    if region:
        query = query.filter(ComplianceFramework.geographic_scop.contains([region]))

    if category:
        query = query.filter(ComplianceFramework.category == category)

    if industry:
        query = query.filter(ComplianceFramework.applicable_indu.contains([industry]))

    if complexity_min is not None:
        query = query.filter(ComplianceFramework.complexity_scor >= complexity_min)

    if complexity_max is not None:
        query = query.filter(ComplianceFramework.complexity_scor <= complexity_max)

    # Get total count before pagination
    total_count = db.query(ComplianceFramework).count()
    filtered_count = query.count()

    # Execute query
    frameworks = query.all()

    # Convert to response format
    framework_responses = [
        FrameworkResponse(
            id=str(fw.id),
            name=fw.name,
            display_name=fw.display_name,
            description=fw.description,
            category=fw.category,
            geographic_scope=fw.geographic_scop,
            complexity_score=fw.complexity_scor,
            version=fw.version,
            is_active=fw.is_active,
            created_at=fw.created_at.isoformat(),
            updated_at=fw.updated_at.isoformat()
        )
        for fw in frameworks
    ]

    return FrameworkListResponse(
        frameworks=framework_responses,
        total_count=total_count,
        filtered_count=filtered_count,
        region=region,
        category=category
    )


@router.get(
    "/frameworks/{framework_id}",
    response_model=FrameworkResponse,
    dependencies=[Depends(RateLimited(requests=200, window=60))]
)
async def get_framework(
    framework_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific compliance framework by ID.
    """
    framework = db.query(ComplianceFramework)\
        .filter(ComplianceFramework.id == framework_id)\
        .first()

    if not framework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Framework not found: {framework_id}"
        )

    return FrameworkResponse(
        id=str(framework.id),
        name=framework.name,
        display_name=framework.display_name,
        description=framework.description,
        category=framework.category,
        geographic_scope=framework.geographic_scop,
        complexity_score=framework.complexity_scor,
        version=framework.version,
        is_active=framework.is_active,
        created_at=framework.created_at.isoformat(),
        updated_at=framework.updated_at.isoformat()
    )


@router.post(
    "/frameworks/load",
    response_model=FrameworkLoadResponse,
    dependencies=[
        Depends(get_current_active_user),
        Depends(RateLimited(requests=10, window=60))
    ]
)
async def load_frameworks(
    request: FrameworkLoadRequest,
    db: Session = Depends(get_db)
):
    """
    Bulk load UK compliance frameworks.

    Requires authentication. Limited to 10 requests per minute.
    """
    # Validate geographic scope for UK frameworks
    validator = GeographicValidator()

    frameworks_data = []
    for framework_schema in request.frameworks:
        # Convert schema to dict with proper field mappings
        framework_dict = {
            "name": framework_schema.name,
            "display_name": framework_schema.display_name,
            "description": framework_schema.description,
            "category": framework_schema.category,
            "applicable_indu": framework_schema.applicable_industries,
            "employee_thresh": framework_schema.employee_threshold,
            "revenue_thresho": framework_schema.revenue_threshold,
            "geographic_scop": [str(region) for region in framework_schema.geographic_scope],
            "key_requirement": framework_schema.key_requirements,
            "control_domains": framework_schema.control_domains,
            "evidence_types": framework_schema.evidence_types,
            "relevance_facto": framework_schema.relevance_factors,
            "complexity_scor": framework_schema.complexity_score,
            "implementation_": framework_schema.implementation_time_weeks,
            "estimated_cost_": framework_schema.estimated_cost_range,
            "policy_template": framework_schema.policy_template,
            "control_templat": framework_schema.control_templates,
            "evidence_templa": framework_schema.evidence_templates,
            "version": framework_schema.version,
            "is_active": framework_schema.is_active
        }

        # Validate UK scope
        if not validator.validate_uk_scope(framework_dict["geographic_scop"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid geographic scope for UK framework: {framework_schema.name}"
            )

        frameworks_data.append(framework_dict)

    # Load frameworks using service
    loader = UKComplianceLoader(db_session=db)
    result = loader.load_frameworks(frameworks_data)

    return FrameworkLoadResponse(
        success=result.success,
        loaded_count=len(result.loaded_frameworks),
        skipped_count=len(result.skipped_frameworks),
        error_count=len(result.errors),
        loaded_frameworks=[fw.name for fw in result.loaded_frameworks],
        skipped_frameworks=result.skipped_frameworks,
        errors=result.errors,
        total_processed=result.total_processed
    )


@router.put(
    "/frameworks/{framework_id}",
    response_model=FrameworkResponse,
    dependencies=[
        Depends(get_current_active_user),
        Depends(RateLimited(requests=50, window=60))
    ]
)
async def update_framework(
    framework_id: str,
    framework_update: UKFrameworkSchema,
    db: Session = Depends(get_db)
):
    """
    Update a specific compliance framework.

    Requires authentication.
    """
    # Find existing framework
    framework = db.query(ComplianceFramework)\
        .filter(ComplianceFramework.id == framework_id)\
        .first()

    if not framework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Framework not found: {framework_id}"
        )

    # Update framework fields with truncated column mappings
    framework.name = framework_update.name
    framework.display_name = framework_update.display_name
    framework.description = framework_update.description
    framework.category = framework_update.category
    framework.applicable_indu = framework_update.applicable_industries
    framework.employee_thresh = framework_update.employee_threshold
    framework.revenue_thresho = framework_update.revenue_threshold
    framework.geographic_scop = [str(region) for region in framework_update.geographic_scope]
    framework.key_requirement = framework_update.key_requirements
    framework.control_domains = framework_update.control_domains
    framework.evidence_types = framework_update.evidence_types
    framework.relevance_facto = framework_update.relevance_factors
    framework.complexity_scor = framework_update.complexity_score
    framework.implementation_ = framework_update.implementation_time_weeks
    framework.estimated_cost_ = framework_update.estimated_cost_range
    framework.policy_template = framework_update.policy_template
    framework.control_templat = framework_update.control_templates
    framework.evidence_templa = framework_update.evidence_templates
    framework.version = framework_update.version
    framework.is_active = framework_update.is_active

    try:
        db.commit()
        db.refresh(framework)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update framework: {str(e)}"
        )

    return FrameworkResponse(
        id=str(framework.id),
        name=framework.name,
        display_name=framework.display_name,
        description=framework.description,
        category=framework.category,
        geographic_scope=framework.geographic_scop,
        complexity_score=framework.complexity_scor,
        version=framework.version,
        is_active=framework.is_active,
        created_at=framework.created_at.isoformat(),
        updated_at=framework.updated_at.isoformat()
    )


@router.delete(
    "/frameworks/{framework_id}",
    dependencies=[
        Depends(get_current_active_user),
        Depends(RateLimited(requests=20, window=60))
    ]
)
async def delete_framework(
    framework_id: str,
    db: Session = Depends(get_db)
):
    """
    Soft delete a compliance framework (set is_active = False).

    Requires authentication.
    """
    framework = db.query(ComplianceFramework)\
        .filter(ComplianceFramework.id == framework_id)\
        .first()

    if not framework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Framework not found: {framework_id}"
        )

    # Soft delete
    framework.is_active = False

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete framework: {str(e)}"
        )

    return {"message": f"Framework {framework_id} deactivated successfully"}
