from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from api.dependencies.auth import get_current_active_user
from api.dependencies.database import get_async_db
from api.schemas.models import UserResponse
from database.business_profile import BusinessProfile
from database.db_setup import get_db
from database.user import User

router = APIRouter()

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: User = Depends(get_current_active_user)
):
    return current_user

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """Get user profile - alias for /me endpoint for compatibility"""
    return current_user

@router.get("/dashboard")
async def get_user_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    """Get user dashboard data"""
    from sqlalchemy import select

    # Get user's business profile
    stmt = select(BusinessProfile).where(BusinessProfile.user_id == current_user.id)
    result = await db.execute(stmt)
    business_profile = result.scalars().first()

    # Basic dashboard data
    dashboard_data = {
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "full_name": getattr(current_user, 'full_name', None)
        },
        "business_profile": {
            "id": str(business_profile.id) if business_profile else None,
            "company_name": business_profile.company_name if business_profile else None,
            "industry": business_profile.industry if business_profile else None
        } if business_profile else None,
        "onboarding_completed": business_profile is not None,
        "quick_stats": {
            "evidence_items": 0,  # Would be populated from evidence service
            "active_assessments": 0,  # Would be populated from assessment service
            "compliance_score": 0  # Would be populated from readiness service
        },
        "active_frameworks": [],  # Placeholder for active frameworks
        "implementation_progress": {
            "total_tasks": 0,
            "completed_tasks": 0,
            "in_progress_tasks": 0,
            "percentage_complete": 0
        },
        "next_actions": []  # Placeholder for next recommended actions
    }

    return dashboard_data

@router.put("/me/deactivate")
async def deactivate_account(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    current_user.is_active = False
    db.commit()
    return {"message": "Account deactivated"}
