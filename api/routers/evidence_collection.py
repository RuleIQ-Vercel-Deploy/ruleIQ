"""
Evidence Collection Plan API Router

Endpoints for AI-driven evidence collection planning and task management.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_active_user
from api.schemas.evidence_collection import (
    CollectionPlanCreate,
    CollectionPlanResponse,
    EvidenceTaskResponse,
    TaskStatusUpdate,
    CollectionPlanSummary,
    AutomationOpportunities,
)
from database.db_setup import get_async_db
from database.user import User
from services.ai.smart_evidence_collector import (
    smart_evidence_collector,
    CollectionStatus,
    EvidencePriority,
)
from services.business_profile_service import BusinessProfileService
from config.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/evidence-collection", tags=["evidence-collection"])


@router.post("/plans", response_model=CollectionPlanResponse)
async def create_collection_plan(
    plan_request: CollectionPlanCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Create an AI-driven evidence collection plan.
    
    This endpoint analyzes your business profile and compliance framework requirements
    to generate a prioritized, optimized collection plan with automation recommendations.
    """
    try:
        # Get user's business profile
        profile = await BusinessProfileService.get_profile_by_user_id(db, current_user.id)
        if not profile:
            raise HTTPException(
                status_code=400,
                detail="Business profile not found. Please complete your business profile first."
            )
        
        # Get existing evidence if needed
        existing_evidence = []
        if plan_request.include_existing_evidence:
            # TODO: Fetch existing evidence from database
            pass
        
        # Create business context
        business_context = {
            'industry': profile.industry,
            'employee_count': profile.employee_count,
            'country': profile.country,
            'data_sensitivity': profile.data_sensitivity,
            'handles_personal_data': profile.handles_personal_data,
            'processes_payments': profile.processes_payments,
            'stores_health_data': profile.stores_health_data,
            'provides_financial_services': profile.provides_financial_services,
            'operates_critical_infrastructure': profile.operates_critical_infrastructure,
            'has_international_operations': profile.has_international_operations,
        }
        
        # Create collection plan
        plan = await smart_evidence_collector.create_collection_plan(
            business_profile_id=str(profile.id),
            framework=plan_request.framework,
            business_context=business_context,
            existing_evidence=existing_evidence,
            target_completion_weeks=plan_request.target_completion_weeks or 12
        )
        
        # Convert to response model
        return CollectionPlanResponse(
            plan_id=plan.plan_id,
            business_profile_id=plan.business_profile_id,
            framework=plan.framework,
            total_tasks=plan.total_tasks,
            estimated_total_hours=plan.estimated_total_hours,
            completion_target_date=plan.completion_target_date,
            tasks=[
                EvidenceTaskResponse(
                    task_id=task.task_id,
                    framework=task.framework,
                    control_id=task.control_id,
                    evidence_type=task.evidence_type,
                    title=task.title,
                    description=task.description,
                    priority=task.priority.value,
                    automation_level=task.automation_level.value,
                    estimated_effort_hours=task.estimated_effort_hours,
                    dependencies=task.dependencies,
                    assigned_to=task.assigned_to,
                    due_date=task.due_date,
                    status=task.status.value,
                    created_at=task.created_at,
                    metadata=task.metadata
                )
                for task in plan.tasks
            ],
            automation_opportunities=AutomationOpportunities(**plan.automation_opportunities),
            created_at=plan.created_at
        )
        
    except Exception as e:
        logger.error(f"Error creating collection plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/plans/{plan_id}", response_model=CollectionPlanResponse)
async def get_collection_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get a specific collection plan by ID."""
    plan = await smart_evidence_collector.get_collection_plan(plan_id)
    
    if not plan:
        raise HTTPException(status_code=404, detail="Collection plan not found")
    
    # Verify user owns this plan
    profile = await BusinessProfileService.get_profile_by_user_id(db, current_user.id)
    if not profile or str(profile.id) != plan.business_profile_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Convert to response model
    return CollectionPlanResponse(
        plan_id=plan.plan_id,
        business_profile_id=plan.business_profile_id,
        framework=plan.framework,
        total_tasks=plan.total_tasks,
        estimated_total_hours=plan.estimated_total_hours,
        completion_target_date=plan.completion_target_date,
        tasks=[
            EvidenceTaskResponse(
                task_id=task.task_id,
                framework=task.framework,
                control_id=task.control_id,
                evidence_type=task.evidence_type,
                title=task.title,
                description=task.description,
                priority=task.priority.value,
                automation_level=task.automation_level.value,
                estimated_effort_hours=task.estimated_effort_hours,
                dependencies=task.dependencies,
                assigned_to=task.assigned_to,
                due_date=task.due_date,
                status=task.status.value,
                created_at=task.created_at,
                metadata=task.metadata
            )
            for task in plan.tasks
        ],
        automation_opportunities=AutomationOpportunities(**plan.automation_opportunities),
        created_at=plan.created_at
    )


@router.get("/plans", response_model=List[CollectionPlanSummary])
async def list_collection_plans(
    framework: Optional[str] = Query(None, description="Filter by framework"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all collection plans for the current user."""
    # Get user's business profile
    profile = await BusinessProfileService.get_profile_by_user_id(db, current_user.id)
    if not profile:
        return []
    
    # Filter plans by business profile
    user_plans = []
    for plan_id, plan in smart_evidence_collector.active_plans.items():
        if plan.business_profile_id == str(profile.id):
            # Apply filters
            if framework and plan.framework != framework:
                continue
            
            # Calculate plan status
            completed_tasks = len([t for t in plan.tasks if t.status == CollectionStatus.COMPLETED])
            if completed_tasks == plan.total_tasks:
                plan_status = "completed"
            elif any(t.status == CollectionStatus.IN_PROGRESS for t in plan.tasks):
                plan_status = "in_progress"
            else:
                plan_status = "pending"
            
            if status and plan_status != status:
                continue
            
            # Create summary
            summary = CollectionPlanSummary(
                plan_id=plan.plan_id,
                framework=plan.framework,
                total_tasks=plan.total_tasks,
                completed_tasks=completed_tasks,
                estimated_total_hours=plan.estimated_total_hours,
                completion_target_date=plan.completion_target_date,
                status=plan_status,
                created_at=plan.created_at
            )
            user_plans.append(summary)
    
    return user_plans


@router.get("/plans/{plan_id}/priority-tasks", response_model=List[EvidenceTaskResponse])
async def get_priority_tasks(
    plan_id: str,
    limit: int = Query(5, ge=1, le=20, description="Number of tasks to return"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get the next priority tasks for a collection plan."""
    # Verify plan ownership
    plan = await smart_evidence_collector.get_collection_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Collection plan not found")
    
    profile = await BusinessProfileService.get_profile_by_user_id(db, current_user.id)
    if not profile or str(profile.id) != plan.business_profile_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get priority tasks
    priority_tasks = await smart_evidence_collector.get_next_priority_tasks(plan_id, limit)
    
    # Convert to response model
    return [
        EvidenceTaskResponse(
            task_id=task.task_id,
            framework=task.framework,
            control_id=task.control_id,
            evidence_type=task.evidence_type,
            title=task.title,
            description=task.description,
            priority=task.priority.value,
            automation_level=task.automation_level.value,
            estimated_effort_hours=task.estimated_effort_hours,
            dependencies=task.dependencies,
            assigned_to=task.assigned_to,
            due_date=task.due_date,
            status=task.status.value,
            created_at=task.created_at,
            metadata=task.metadata
        )
        for task in priority_tasks
    ]


@router.patch("/plans/{plan_id}/tasks/{task_id}", response_model=EvidenceTaskResponse)
async def update_task_status(
    plan_id: str,
    task_id: str,
    status_update: TaskStatusUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update the status of a specific task."""
    # Verify plan ownership
    plan = await smart_evidence_collector.get_collection_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Collection plan not found")
    
    profile = await BusinessProfileService.get_profile_by_user_id(db, current_user.id)
    if not profile or str(profile.id) != plan.business_profile_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update task status
    success = await smart_evidence_collector.update_task_status(
        plan_id=plan_id,
        task_id=task_id,
        status=CollectionStatus(status_update.status),
        completion_notes=status_update.completion_notes
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Get updated task
    for task in plan.tasks:
        if task.task_id == task_id:
            return EvidenceTaskResponse(
                task_id=task.task_id,
                framework=task.framework,
                control_id=task.control_id,
                evidence_type=task.evidence_type,
                title=task.title,
                description=task.description,
                priority=task.priority.value,
                automation_level=task.automation_level.value,
                estimated_effort_hours=task.estimated_effort_hours,
                dependencies=task.dependencies,
                assigned_to=task.assigned_to,
                due_date=task.due_date,
                status=task.status.value,
                created_at=task.created_at,
                metadata=task.metadata
            )
    
    raise HTTPException(status_code=404, detail="Task not found")


@router.get("/automation-recommendations/{framework}")
async def get_automation_recommendations(
    framework: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get automation recommendations for a specific framework."""
    # Get user's business profile
    profile = await BusinessProfileService.get_profile_by_user_id(db, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=400,
            detail="Business profile not found. Please complete your business profile first."
        )
    
    # Get automation rules for common evidence types
    automation_rules = smart_evidence_collector.automation_rules
    
    # Provide framework-specific recommendations
    recommendations = {
        "framework": framework,
        "automation_opportunities": [],
        "recommended_tools": set(),
        "estimated_time_savings": 0.0
    }
    
    for evidence_type, rules in automation_rules.items():
        if rules['automation_level'].value in ['fully_automated', 'semi_automated']:
            opportunity = {
                "evidence_type": evidence_type,
                "automation_level": rules['automation_level'].value,
                "effort_reduction": f"{rules['effort_reduction'] * 100:.0f}%",
                "success_rate": f"{rules['success_rate'] * 100:.0f}%",
                "recommended_tools": rules['tools']
            }
            recommendations["automation_opportunities"].append(opportunity)
            recommendations["recommended_tools"].update(rules['tools'])
            recommendations["estimated_time_savings"] += rules['effort_reduction'] * 8  # Assume 8 hours base
    
    recommendations["recommended_tools"] = list(recommendations["recommended_tools"])
    
    return recommendations