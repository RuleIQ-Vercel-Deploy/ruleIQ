from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.dependencies.auth import get_current_active_user
from api.schemas.models import BusinessProfileCreate, BusinessProfileResponse, BusinessProfileUpdate
from database.business_profile import BusinessProfile
from database.db_setup import get_db
from database.user import User

router = APIRouter()

@router.post("/", response_model=BusinessProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_business_profile(
    profile: BusinessProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Check if profile already exists
    existing = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Business profile already exists"
        )

    # Filter out fields that don't exist in the database model
    profile_data = profile.model_dump()
    # Remove fields that are not in the BusinessProfile model
    profile_data.pop('data_sensitivity', None)

    # Set default values for required boolean fields if not provided
    boolean_defaults = {
        'handles_persona': False,
        'processes_payme': False,
        'stores_health_d': False,
        'provides_financ': False,
        'operates_critic': False,
        'has_internation': False,
    }
    for field, default_value in boolean_defaults.items():
        if field not in profile_data:
            profile_data[field] = default_value

    db_profile = BusinessProfile(
        id=uuid4(),
        user_id=current_user.id,
        **profile_data
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)

    return db_profile

@router.get("/", response_model=BusinessProfileResponse)
async def get_business_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
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
    db: Session = Depends(get_db)
):
    profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business profile not found"
        )

    update_data = profile_update.model_dump(exclude_unset=True)
    # Remove fields that are not in the BusinessProfile model
    update_data.pop('data_sensitivity', None)
    for key, value in update_data.items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)

    return profile
