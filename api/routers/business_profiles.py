from uuid import uuid4, UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_active_user
from api.dependencies.database import get_async_db
from api.schemas.models import BusinessProfileCreate, BusinessProfileResponse, BusinessProfileUpdate
from database.business_profile import BusinessProfile
from database.user import User

router = APIRouter()

@router.post("/", response_model=BusinessProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_business_profile(
    profile: BusinessProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    # Check if profile already exists
    stmt = select(BusinessProfile).where(BusinessProfile.user_id == current_user.id)
    result = await db.execute(stmt)
    existing = result.scalars().first()

    if existing:
        # Instead of deleting and recreating, update the existing profile
        # This prevents foreign key constraint violations with evidence_items
        profile_data = profile.model_dump()
        # Remove fields that are not in the BusinessProfile model
        profile_data.pop('data_sensitivity', None)  # Temporarily removed until migration is run

        # Update existing profile fields
        for key, value in profile_data.items():
            if hasattr(existing, key):
                setattr(existing, key, value)

        existing.updated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(existing)
        return existing
    else:
        # Create new profile only if none exists
        profile_data = profile.model_dump()
        # Remove fields that are not in the BusinessProfile model
        profile_data.pop('data_sensitivity', None)  # Temporarily removed until migration is run

        db_profile = BusinessProfile(
            id=uuid4(),
            user_id=current_user.id,
            **profile_data
        )
        db.add(db_profile)
        await db.commit()
        await db.refresh(db_profile)
        return db_profile

@router.get("/", response_model=BusinessProfileResponse)
async def get_business_profile(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    stmt = select(BusinessProfile).where(BusinessProfile.user_id == current_user.id)
    result = await db.execute(stmt)
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found"
        )
    return profile

@router.get("/{profile_id}", response_model=BusinessProfileResponse)
async def get_business_profile_by_id(
    profile_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get a specific business profile by ID - only accessible by the profile owner."""
    stmt = select(BusinessProfile).where(
        BusinessProfile.id == profile_id,
        BusinessProfile.user_id == current_user.id
    )
    result = await db.execute(stmt)
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found"
        )
    return profile

@router.put("/", response_model=BusinessProfileResponse)
async def update_business_profile(
    profile_update: BusinessProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    stmt = select(BusinessProfile).where(BusinessProfile.user_id == current_user.id)
    result = await db.execute(stmt)
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found"
        )

    update_data = profile_update.model_dump(exclude_unset=True)
    # Remove fields that are not in the BusinessProfile model
    update_data.pop('data_sensitivity', None)  # Temporarily removed until migration is run
    for key, value in update_data.items():
        setattr(profile, key, value)

    await db.commit()
    await db.refresh(profile)

    return profile

@router.put("/{profile_id}", response_model=BusinessProfileResponse)
async def update_business_profile_by_id(
    profile_id: UUID,
    profile_update: BusinessProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Update a specific business profile by ID - only accessible by the profile owner."""
    stmt = select(BusinessProfile).where(
        BusinessProfile.id == profile_id,
        BusinessProfile.user_id == current_user.id
    )
    result = await db.execute(stmt)
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found"
        )

    update_data = profile_update.model_dump(exclude_unset=True)
    # Remove fields that are not in the BusinessProfile model
    update_data.pop('data_sensitivity', None)  # Temporarily removed until migration is run
    for key, value in update_data.items():
        setattr(profile, key, value)

    profile.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(profile)

    return profile

@router.delete("/{profile_id}")
async def delete_business_profile_by_id(
    profile_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a specific business profile by ID - only accessible by the profile owner."""
    stmt = select(BusinessProfile).where(
        BusinessProfile.id == profile_id,
        BusinessProfile.user_id == current_user.id
    )
    result = await db.execute(stmt)
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found"
        )

    await db.delete(profile)
    await db.commit()

    return {"message": "Business profile deleted successfully"}

@router.patch("/{profile_id}", response_model=BusinessProfileResponse)
async def patch_business_profile(
    profile_id: UUID,
    profile_update: BusinessProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Update a specific business profile by ID with partial data."""
    stmt = select(BusinessProfile).where(
        BusinessProfile.id == profile_id,
        BusinessProfile.user_id == current_user.id
    )
    result = await db.execute(stmt)
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found"
        )

    update_data = profile_update.model_dump(exclude_unset=True)
    # Remove fields that are not in the BusinessProfile model
    update_data.pop('data_sensitivity', None)  # Temporarily removed until migration is run

    # Handle version-based optimistic locking if version is provided
    if 'version' in update_data:
        expected_version = update_data.pop('version')
        current_version = getattr(profile, 'version', 1)
        if expected_version != current_version:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": {"message": "Conflict: Profile has been modified by another user"}}
            )

    for key, value in update_data.items():
        if hasattr(profile, key):
            setattr(profile, key, value)

    profile.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(profile)

    return profile
