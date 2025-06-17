from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies.auth import get_current_active_user
from api.schemas.models import (
    ImplementationPlanCreate,
    ImplementationPlanResponse,
    ImplementationTaskUpdate,
)
from database.user import User

router = APIRouter()

@router.post("/plans", response_model=ImplementationPlanResponse)
async def create_plan(
    plan_data: ImplementationPlanCreate,
    current_user: User = Depends(get_current_active_user)
):
    plan = await create_implementation_plan(
        current_user,
        plan_data.framework_id,
        plan_data.control_ids
    )
    return plan

@router.get("/plans", response_model=List[ImplementationPlanResponse])
async def list_plans(
    current_user: User = Depends(get_current_active_user)
):
    plans = get_user_plans(current_user)
    return plans

@router.get("/plans/{plan_id}", response_model=ImplementationPlanResponse)
async def get_plan(
    plan_id: UUID,
    current_user: User = Depends(get_current_active_user)
):
    plan = get_plan_by_id(current_user, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Implementation plan not found")
    return plan

@router.put("/plans/{plan_id}/tasks/{task_id}")
async def update_task(
    plan_id: UUID,
    task_id: str,
    task_update: ImplementationTaskUpdate,
    current_user: User = Depends(get_current_active_user)
):
    update_task_status(
        current_user,
        plan_id,
        task_id,
        task_update
    )
    return {"message": "Task updated", "plan_id": plan_id, "task_id": task_id}
