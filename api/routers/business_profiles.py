from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from api.dependencies.database import get_async_db
from api.dependencies.rbac_auth import (
    UserWithRoles,
    require_permission
)
from services.data_access_service import DataAccessService
from database.db_setup import get_db
from api.schemas.models import BusinessProfileCreate, BusinessProfileResponse, BusinessProfileUpdate
from database.business_profile import BusinessProfile
from utils.input_validation import validate_business_profile_update, ValidationError

router = APIRouter()

# Field mapping no longer needed - column names match API field names after migration


@router.post("/", response_model=BusinessProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_business_profile(
    profile: BusinessProfileCreate,
    current_user: UserWithRoles = Depends(require_permission("user_create")),
    db: AsyncSession = Depends(get_async_db),
):
    # Check if profile already exists
    stmt = select(BusinessProfile).where(BusinessProfile.user_id == current_user.id)
    result = await db.execute(stmt)
    existing = result.scalars().first()

    if existing:
        # Instead of deleting and recreating, update the existing profile
        # This prevents foreign key constraint violations with evidence_items
        profile_data = profile.model_dump()

        # Validate input data against whitelist and security patterns
        try:
            validated_data = validate_business_profile_update(profile_data)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Update existing profile fields with validated data
        ALLOWED_FIELDS = [
            "company_name",
            "industry",
            "company_size",
            "description",
            "data_sensitivity",
            "geographic_scope",
            "target_frameworks",
        ]
        for key, value in validated_data.items():
            if key in ALLOWED_FIELDS:
                setattr(existing, key, value)

        # The updated_at field is automatically handled by the database
        await db.commit()
        await db.refresh(existing)
        return existing
    else:
        # Create new profile only if none exists
        profile_data = profile.model_dump()

        # Validate input data against whitelist and security patterns
        try:
            validated_data = validate_business_profile_update(profile_data)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))

        db_profile = BusinessProfile(id=uuid4(), user_id=current_user.id, **validated_data)
        db.add(db_profile)
        await db.commit()
        await db.refresh(db_profile)
        return db_profile


@router.get("/", response_model=BusinessProfileResponse)
async def get_business_profile(
    current_user: UserWithRoles = Depends(require_permission("user_list")),
    db: AsyncSession = Depends(get_async_db)
):
    stmt = select(BusinessProfile).where(BusinessProfile.user_id == current_user.id)
    result = await db.execute(stmt)
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Business profile not found"
        )
    return profile


@router.get("/{id}", response_model=BusinessProfileResponse)
async def get_business_profile_by_id(
    id: UUID,
    current_user: UserWithRoles = Depends(require_permission("user_list")),
    db: AsyncSession = Depends(get_async_db),
    sync_db: Session = Depends(get_db),
):
    """Get a specific business profile by ID - access controlled by RBAC data visibility."""
    # First get the profile to check ownership
    stmt = select(BusinessProfile).where(BusinessProfile.id == id)
    result = await db.execute(stmt)
    profile = result.scalars().first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Business profile not found"
        )

    # Check data access permissions
    data_access_service = DataAccessService(sync_db)
    if not data_access_service.can_access_business_profile(
        current_user, id, profile.user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Insufficient permissions to view this profile"
        )

    return profile


@router.put("/", response_model=BusinessProfileResponse)
async def update_business_profile(
    profile_update: BusinessProfileUpdate,
    current_user: UserWithRoles = Depends(require_permission("user_update")),
    db: AsyncSession = Depends(get_async_db),
):
    stmt = select(BusinessProfile).where(BusinessProfile.user_id == current_user.id)
    result = await db.execute(stmt)
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Business profile not found"
        )

    update_data = profile_update.model_dump(exclude_unset=True)
    # Remove fields that are not in the BusinessProfile model
    update_data.pop("data_sensitivity", None)  # Temporarily removed until migration is run

    # Validate input data against whitelist and security patterns
    try:
        validated_data = validate_business_profile_update(update_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    ALLOWED_FIELDS = [
        "company_name",
        "industry",
        "company_size",
        "description",
        "data_sensitivity",
        "geographic_scope",
        "target_frameworks",
    ]
    for key, value in validated_data.items():
        if key in ALLOWED_FIELDS:
            setattr(profile, key, value)

    # The updated_at field is automatically handled by the database
    await db.commit()
    await db.refresh(profile)

    return profile


@router.put("/{id}", response_model=BusinessProfileResponse)
async def update_business_profile_by_id(
    profile_id: UUID,
    profile_update: BusinessProfileUpdate,
    current_user: UserWithRoles = Depends(require_permission("user_update")),
    db: AsyncSession = Depends(get_async_db),
    sync_db: Session = Depends(get_db),
):
    """Update a specific business profile by ID - access controlled by RBAC data visibility."""
    # First get the profile to check ownership
    stmt = select(BusinessProfile).where(BusinessProfile.id == profile_id)
    result = await db.execute(stmt)
    profile = result.scalars().first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Business profile not found"
        )

    # Check data access permissions
    data_access_service = DataAccessService(sync_db)
    if not data_access_service.can_access_business_profile(
        current_user, profile_id, profile.user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Insufficient permissions to update this profile"
        )

    update_data = profile_update.model_dump(exclude_unset=True)
    # Remove fields that are not in the BusinessProfile model
    update_data.pop("data_sensitivity", None)  # Temporarily removed until migration is run

    # Validate input data against whitelist and security patterns
    try:
        validated_data = validate_business_profile_update(update_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    ALLOWED_FIELDS = [
        "company_name",
        "industry",
        "company_size",
        "description",
        "data_sensitivity",
        "geographic_scope",
        "target_frameworks",
    ]
    for key, value in validated_data.items():
        if key in ALLOWED_FIELDS:
            setattr(profile, key, value)

    # The updated_at field is automatically handled by the database
    await db.commit()
    await db.refresh(profile)

    return profile


@router.delete("/{id}")
async def delete_business_profile_by_id(
    profile_id: UUID,
    current_user: UserWithRoles = Depends(require_permission("user_delete")),
    db: AsyncSession = Depends(get_async_db),
    sync_db: Session = Depends(get_db),
):
    """Delete a specific business profile by ID - access controlled by RBAC data visibility."""
    # First get the profile to check ownership
    stmt = select(BusinessProfile).where(BusinessProfile.id == profile_id)
    result = await db.execute(stmt)
    profile = result.scalars().first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Business profile not found"
        )

    # Check data access permissions
    data_access_service = DataAccessService(sync_db)
    if not data_access_service.can_access_business_profile(
        current_user, profile_id, profile.user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Insufficient permissions to delete this profile"
        )

    await db.delete(profile)
    await db.commit()

    return {"message": "Business profile deleted successfully"}


@router.get("/list", summary="List all business profiles")
async def list_business_profiles(
    limit: int = 10,
    offset: int = 0,
    current_user: UserWithRoles = Depends(require_permission("user_list")),
    db: AsyncSession = Depends(get_async_db),
    sync_db: Session = Depends(get_db),
):
    """List all business profiles accessible to the current user."""
    # Get profiles based on user's data visibility permissions
    data_access_service = DataAccessService(sync_db)
    
    # For now, return user's own profile(s)
    # In a real implementation, this would check organization membership
    stmt = select(BusinessProfile).where(BusinessProfile.user_id == current_user.id)
    result = await db.execute(stmt)
    profiles = result.scalars().all()
    
    return {
        "profiles": [
            {
                "id": str(profile.id),
                "company_name": profile.company_name,
                "industry": profile.industry,
                "company_size": profile.company_size,
                "created_at": profile.created_at.isoformat() if hasattr(profile, 'created_at') else None,
                "updated_at": profile.updated_at.isoformat() if hasattr(profile, 'updated_at') else None,
            }
            for profile in profiles
        ],
        "total": len(profiles),
        "limit": limit,
        "offset": offset,
    }


@router.get("/{id}/compliance-status", summary="Get compliance status for profile")
async def get_profile_compliance_status(
    profile_id: UUID,
    current_user: UserWithRoles = Depends(require_permission("user_list")),
    db: AsyncSession = Depends(get_async_db),
    sync_db: Session = Depends(get_db),
):
    """Get compliance status for a specific business profile."""
    # First get the profile to check ownership
    stmt = select(BusinessProfile).where(BusinessProfile.id == profile_id)
    result = await db.execute(stmt)
    profile = result.scalars().first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Business profile not found"
        )

    # Check data access permissions
    data_access_service = DataAccessService(sync_db)
    if not data_access_service.can_access_business_profile(
        current_user, profile_id, profile.user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Insufficient permissions to view this profile"
        )

    # Placeholder implementation
    return {
        "profile_id": str(profile_id),
        "overall_compliance": 75,
        "frameworks": [
            {
                "name": "GDPR",
                "compliance_level": 80,
                "status": "Good",
                "last_assessment": "2024-01-10T10:00:00Z",
            },
            {
                "name": "ISO 27001",
                "compliance_level": 70,
                "status": "Fair",
                "last_assessment": "2024-01-08T14:30:00Z",
            },
        ],
        "risk_level": "Medium",
        "action_items": 5,
    }


@router.get("/{id}/team", summary="Get team members for profile")
async def get_profile_team(
    profile_id: UUID,
    current_user: UserWithRoles = Depends(require_permission("user_list")),
    db: AsyncSession = Depends(get_async_db),
    sync_db: Session = Depends(get_db),
):
    """Get team members associated with a business profile."""
    # First get the profile to check ownership
    stmt = select(BusinessProfile).where(BusinessProfile.id == profile_id)
    result = await db.execute(stmt)
    profile = result.scalars().first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Business profile not found"
        )

    # Check data access permissions
    data_access_service = DataAccessService(sync_db)
    if not data_access_service.can_access_business_profile(
        current_user, profile_id, profile.user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Insufficient permissions to view this profile"
        )

    # Placeholder implementation
    return {
        "profile_id": str(profile_id),
        "team_members": [
            {
                "user_id": str(current_user.id),
                "email": current_user.email,
                "role": "Owner",
                "permissions": ["full_access"],
                "joined_at": "2024-01-01T00:00:00Z",
            },
        ],
        "total_members": 1,
        "pending_invites": 0,
    }


@router.post("/{id}/invite", summary="Invite team member to profile")
async def invite_team_member(
    profile_id: UUID,
    invite_data: dict,
    current_user: UserWithRoles = Depends(require_permission("user_create")),
    db: AsyncSession = Depends(get_async_db),
    sync_db: Session = Depends(get_db),
):
    """Invite a team member to a business profile."""
    # First get the profile to check ownership
    stmt = select(BusinessProfile).where(BusinessProfile.id == profile_id)
    result = await db.execute(stmt)
    profile = result.scalars().first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Business profile not found"
        )

    # Check data access permissions
    data_access_service = DataAccessService(sync_db)
    if not data_access_service.can_access_business_profile(
        current_user, profile_id, profile.user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Insufficient permissions to invite to this profile"
        )

    # Placeholder implementation
    email = invite_data.get("email", "")
    role = invite_data.get("role", "viewer")
    
    from uuid import uuid4
    from datetime import datetime
    invite_id = str(uuid4())
    
    return {
        "invite_id": invite_id,
        "profile_id": str(profile_id),
        "invited_email": email,
        "role": role,
        "status": "pending",
        "invited_by": current_user.email,
        "invited_at": datetime.utcnow().isoformat(),
        "expires_at": "2024-01-22T00:00:00Z",
    }


@router.get("/{id}/activity", summary="Get activity log for profile")
async def get_profile_activity(
    profile_id: UUID,
    limit: int = 20,
    current_user: UserWithRoles = Depends(require_permission("user_list")),
    db: AsyncSession = Depends(get_async_db),
    sync_db: Session = Depends(get_db),
):
    """Get activity log for a business profile."""
    # First get the profile to check ownership
    stmt = select(BusinessProfile).where(BusinessProfile.id == profile_id)
    result = await db.execute(stmt)
    profile = result.scalars().first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Business profile not found"
        )

    # Check data access permissions
    data_access_service = DataAccessService(sync_db)
    if not data_access_service.can_access_business_profile(
        current_user, profile_id, profile.user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Insufficient permissions to view this profile"
        )

    # Placeholder implementation
    from datetime import datetime
    
    return {
        "profile_id": str(profile_id),
        "activities": [
            {
                "activity_id": "act_001",
                "type": "profile_updated",
                "description": "Business profile information updated",
                "user": current_user.email,
                "timestamp": "2024-01-15T14:30:00Z",
            },
            {
                "activity_id": "act_002",
                "type": "assessment_completed",
                "description": "GDPR compliance assessment completed",
                "user": current_user.email,
                "timestamp": "2024-01-14T10:00:00Z",
            },
            {
                "activity_id": "act_003",
                "type": "evidence_uploaded",
                "description": "New evidence document uploaded",
                "user": current_user.email,
                "timestamp": "2024-01-13T16:45:00Z",
            },
        ],
        "total": 3,
        "limit": limit,
    }


@router.patch("/{id}", response_model=BusinessProfileResponse)
async def patch_business_profile(
    profile_id: UUID,
    profile_update: BusinessProfileUpdate,
    current_user: UserWithRoles = Depends(require_permission("user_update")),
    db: AsyncSession = Depends(get_async_db),
    sync_db: Session = Depends(get_db),
):
    """Update a specific business profile by ID with partial data - access controlled by RBAC."""
    # First get the profile to check ownership
    stmt = select(BusinessProfile).where(BusinessProfile.id == profile_id)
    result = await db.execute(stmt)
    profile = result.scalars().first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Business profile not found"
        )

    # Check data access permissions
    data_access_service = DataAccessService(sync_db)
    if not data_access_service.can_access_business_profile(
        current_user, profile_id, profile.user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: Insufficient permissions to update this profile"
        )

    update_data = profile_update.model_dump(exclude_unset=True)
    # Remove fields that are not in the BusinessProfile model
    update_data.pop("data_sensitivity", None)  # Temporarily removed until migration is run

    # Handle version-based optimistic locking if version is provided
    if "version" in update_data:
        expected_version = update_data.pop("version")
        current_version = getattr(profile, "version", 1)
        if expected_version != current_version:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": {"message": "Conflict: Profile has been modified by another user"}
                },
            )

    # Validate input data against whitelist and security patterns
    try:
        validated_data = validate_business_profile_update(update_data)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    ALLOWED_FIELDS = [
        "company_name",
        "industry",
        "company_size",
        "description",
        "data_sensitivity",
        "geographic_scope",
        "target_frameworks",
    ]
    for key, value in validated_data.items():
        if key in ALLOWED_FIELDS:
            setattr(profile, key, value)

    # The updated_at field is automatically handled by the database
    await db.commit()
    await db.refresh(profile)

    return profile



@router.get("/{profileId}/compliance", summary="Get compliance status for business profile")
async def get_profile_compliance(
    profileId: str,
    current_user: UserWithRoles = Depends(require_permission("user_view")),
    db: AsyncSession = Depends(get_async_db),
):
    """Get compliance status for a specific business profile."""
    # Placeholder implementation
    return {
        "profile_id": profileId,
        "compliance_status": {
            "gdpr": {
                "score": 75,
                "status": "partial",
                "last_assessment": "2024-01-15T10:30:00Z",
            },
            "iso27001": {
                "score": 82,
                "status": "partial",
                "last_assessment": "2024-01-10T14:20:00Z",
            },
            "pci_dss": {
                "score": 65,
                "status": "non_compliant",
                "last_assessment": "2024-01-05T09:15:00Z",
            },
        },
        "overall_score": 74,
        "high_risk_areas": ["data_retention", "access_controls", "encryption"],
        "recommendations": [
            "Implement data retention policies",
            "Strengthen access control mechanisms",
            "Enable encryption at rest for sensitive data",
        ],
    }
