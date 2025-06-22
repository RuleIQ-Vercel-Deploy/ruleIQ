from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_active_user
from api.schemas.models import (
    ImplementationPlanCreate,
    ImplementationPlanResponse,
    ImplementationPlanListResponse,
    ImplementationTaskUpdate,
)
from database.db_setup import get_async_db
from database.user import User
from services.implementation_service import (
    generate_implementation_plan,
    list_implementation_plans,
    get_implementation_plan,
    update_task_status,
)

router = APIRouter()

@router.post("/plans", response_model=ImplementationPlanResponse, status_code=201)
async def create_plan(
    plan_data: ImplementationPlanCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    plan = await generate_implementation_plan(
        db,
        current_user,
        plan_data.framework_id,
        control_domain=plan_data.control_domain,
        timeline_weeks=plan_data.timeline_weeks
    )
    return plan

@router.get("/plans", response_model=ImplementationPlanListResponse)
async def list_plans(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    plans = await list_implementation_plans(db, current_user)
    return {"plans": plans}

@router.get("/plans/{plan_id}", response_model=ImplementationPlanResponse)
async def get_plan(
    plan_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    plan = await get_implementation_plan(db, current_user, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Implementation plan not found")
    return plan

@router.patch("/plans/{plan_id}/tasks/{task_id}")
async def update_task(
    plan_id: UUID,
    task_id: str,
    task_update: ImplementationTaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    plan = await update_task_status(
        db,
        current_user,
        plan_id,
        task_id,
        task_update.status
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Implementation plan not found")
    return {"message": "Task updated", "plan_id": plan_id, "task_id": task_id}
