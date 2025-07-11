from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_active_user
from api.schemas.models import (
    ImplementationPlanCreate,
    ImplementationPlanListResponse,
    ImplementationPlanResponse,
    ImplementationTaskUpdate,
)
from database.db_setup import get_async_db
from database.user import User
from services.implementation_service import (
    generate_implementation_plan,
    get_implementation_plan,
    list_implementation_plans,
    update_task_status,
)

router = APIRouter()


@router.post("/plans", response_model=ImplementationPlanResponse, status_code=201)
async def create_plan(
    plan_data: ImplementationPlanCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    plan = await generate_implementation_plan(
        db,
        current_user,
        plan_data.framework_id,
        control_domain=plan_data.control_domain,
        timeline_weeks=plan_data.timeline_weeks,
    )

    # Calculate computed fields for the response
    total_phases = len(plan.phases) if plan.phases else 0
    total_tasks = sum(len(phase.get("tasks", [])) for phase in plan.phases) if plan.phases else 0
    estimated_duration_weeks = plan_data.timeline_weeks or 12

    # Convert plan to dict and add computed fields
    plan_dict = {
        "id": plan.id,
        "user_id": plan.user_id,
        "business_profile_id": plan.business_profile_id,
        "framework_id": plan.framework_id,
        "title": plan.title,
        "status": plan.status,
        "phases": plan.phases,
        "planned_start_date": plan.planned_start_date,
        "planned_end_date": plan.planned_end_date,
        "actual_start_date": plan.actual_start_date,
        "actual_end_date": plan.actual_end_date,
        "created_at": plan.created_at,
        "updated_at": plan.updated_at,
        "total_phases": total_phases,
        "total_tasks": total_tasks,
        "estimated_duration_weeks": estimated_duration_weeks,
    }

    return plan_dict


@router.get("/plans", response_model=ImplementationPlanListResponse)
async def list_plans(
    current_user: User = Depends(get_current_active_user), db: AsyncSession = Depends(get_async_db)
):
    plans = await list_implementation_plans(db, current_user)
    return {"plans": plans}


@router.get("/plans/{plan_id}", response_model=ImplementationPlanResponse)
async def get_plan(
    plan_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    plan = await get_implementation_plan(db, current_user, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Implementation plan not found")

    # Calculate computed fields and flatten tasks for the response
    total_phases = len(plan.phases) if plan.phases else 0
    total_tasks = sum(len(phase.get("tasks", [])) for phase in plan.phases) if plan.phases else 0

    # Flatten all tasks from all phases
    all_tasks = []
    for phase in plan.phases:
        for task in phase.get("tasks", []):
            all_tasks.append(task)

    # Calculate estimated duration from phases
    estimated_duration_weeks = (
        sum(phase.get("duration_weeks", 0) for phase in plan.phases) if plan.phases else 12
    )

    # Convert plan to dict and add computed fields
    plan_dict = {
        "id": plan.id,
        "user_id": plan.user_id,
        "business_profile_id": plan.business_profile_id,
        "framework_id": plan.framework_id,
        "title": plan.title,
        "status": plan.status,
        "phases": plan.phases,
        "planned_start_date": plan.planned_start_date,
        "planned_end_date": plan.planned_end_date,
        "actual_start_date": plan.actual_start_date,
        "actual_end_date": plan.actual_end_date,
        "created_at": plan.created_at,
        "updated_at": plan.updated_at,
        "total_phases": total_phases,
        "total_tasks": total_tasks,
        "estimated_duration_weeks": estimated_duration_weeks,
        "tasks": all_tasks,  # Flattened tasks for test compatibility
    }

    return plan_dict


@router.patch("/plans/{plan_id}/tasks/{task_id}")
async def update_task(
    plan_id: UUID,
    task_id: str,
    task_update: ImplementationTaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    plan = await update_task_status(db, current_user, plan_id, task_id, task_update.status)
    if not plan:
        raise HTTPException(status_code=404, detail="Implementation plan not found")
    return {"message": "Task updated", "plan_id": plan_id, "task_id": task_id}
