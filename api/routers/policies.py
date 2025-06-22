from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_active_user
from api.schemas.models import GeneratedPolicyResponse, PolicyGenerateRequest, PolicyListResponse
from database.db_setup import get_async_db
from database.user import User
from services.policy_service import generate_compliance_policy, get_policy_by_id, get_user_policies

router = APIRouter()

@router.post("/generate", response_model=GeneratedPolicyResponse, status_code=201)
async def generate_policy(
    request: PolicyGenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    policy = await generate_compliance_policy(
        db,
        current_user.id,
        request.framework_id,
        request.policy_type if hasattr(request, 'policy_type') else "comprehensive",
        request.custom_requirements if hasattr(request, 'custom_requirements') else []
    )
    return policy

@router.get("/", response_model=PolicyListResponse)
async def list_policies(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    policies = await get_user_policies(db, current_user.id)
    return {"policies": policies}

@router.get("/{policy_id}", response_model=GeneratedPolicyResponse)
async def get_policy(
    policy_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    policy = await get_policy_by_id(db, policy_id, current_user.id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@router.patch("/{policy_id}/status")
async def update_policy_status(
    policy_id: UUID,
    status_update: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Update policy status"""
    policy = await get_policy_by_id(db, policy_id, current_user.id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    # Update status
    if "status" in status_update:
        policy.status = status_update["status"]

    await db.commit()
    await db.refresh(policy)

    return {
        "id": policy.id,
        "status": policy.status,
        "approved": status_update.get("approved", False)
    }

@router.put("/{policy_id}/approve")
async def approve_policy(
    policy_id: UUID,
    current_user: User = Depends(get_current_active_user)
):
    # Implementation for policy approval
    return {"message": "Policy approved", "policy_id": policy_id}
