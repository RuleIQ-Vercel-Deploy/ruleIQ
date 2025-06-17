from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies.auth import get_current_active_user
from api.schemas.models import GeneratedPolicyResponse, PolicyGenerateRequest
from database.user import User
from services.policy_service import generate_compliance_policy, get_policy_by_id, get_user_policies

router = APIRouter()

@router.post("/generate", response_model=GeneratedPolicyResponse)
async def generate_policy(
    request: PolicyGenerateRequest,
    current_user: User = Depends(get_current_active_user)
):
    policy = generate_compliance_policy(
        current_user,
        request.framework_id,
        request.policy_type if hasattr(request, 'policy_type') else "comprehensive",
        request.custom_requirements if hasattr(request, 'custom_requirements') else []
    )
    return policy

@router.get("/", response_model=List[GeneratedPolicyResponse])
async def list_policies(
    current_user: User = Depends(get_current_active_user)
):
    policies = get_user_policies(current_user)
    return policies

@router.get("/{policy_id}", response_model=GeneratedPolicyResponse)
async def get_policy(
    policy_id: UUID,
    current_user: User = Depends(get_current_active_user)
):
    policy = get_policy_by_id(current_user, policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy

@router.put("/{policy_id}/approve")
async def approve_policy(
    policy_id: UUID,
    current_user: User = Depends(get_current_active_user)
):
    # Implementation for policy approval
    return {"message": "Policy approved", "policy_id": policy_id}
