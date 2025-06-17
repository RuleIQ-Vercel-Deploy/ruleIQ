import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID

from core.business_profile import BusinessProfile
from core.compliance_framework import ComplianceFramework
from core.generated_policy import GeneratedPolicy
from core.implementation_plan import ImplementationPlan
from sqlalchemy_access import User, authenticated


@authenticated
def generate_implementation_plan(
    user: User,
    framework_id: UUID,
    policy_id: Optional[UUID] = None,
    control_domain: str = "All Domains",
    timeline_weeks: int = 12
) -> ImplementationPlan:
    """Generate a detailed implementation plan for compliance controls."""

    # Get business profile
    profile_results = BusinessProfile.sql(
        "SELECT * FROM business_profiles WHERE user_id = %(user_id)s",
        {"user_id": user.id}
    )

    if not profile_results:
        raise ValueError("Business profile not found")

    profile = BusinessProfile(**profile_results[0])

    # Get compliance framework
    framework_results = ComplianceFramework.sql(
        "SELECT * FROM compliance_frameworks WHERE id = %(framework_id)s",
        {"framework_id": framework_id}
    )

    if not framework_results:
        raise ValueError("Compliance framework not found")

    framework = ComplianceFramework(**framework_results[0])

    # Get policy if provided
    policy = None
    if policy_id:
        policy_results = GeneratedPolicy.sql(
            "SELECT * FROM generated_policies WHERE id = %(policy_id)s AND user_id = %(user_id)s",
            {"policy_id": policy_id, "user_id": user.id}
        )
        if policy_results:
            policy = GeneratedPolicy(**policy_results[0])

    # Generate implementation plan using AI
    plan_data = generate_plan_with_ai(profile, framework, policy, control_domain, timeline_weeks)

    # Calculate timeline dates
    start_date = datetime.now()
    end_date = start_date + timedelta(weeks=timeline_weeks)

    # Create implementation plan
    plan = ImplementationPlan(
        user_id=user.id,
        business_profile_id=profile.id,
        framework_id=framework_id,
        policy_id=policy_id,
        plan_name=f"{framework.display_name} Implementation Plan - {control_domain}",
        framework_name=framework.name,
        control_domain=control_domain,
        phases=plan_data["phases"],
        total_estimated_hours=plan_data["total_estimated_hours"],
        total_estimated_cost=plan_data["total_estimated_cost"],
        estimated_duration_weeks=timeline_weeks,
        total_phases=len(plan_data["phases"]),
        phase_details=plan_data["phase_details"],
        required_roles=plan_data["required_roles"],
        external_resources=plan_data["external_resources"],
        budget_breakdown=plan_data["budget_breakdown"],
        planned_start_date=start_date,
        planned_end_date=end_date,
        risk_factors=plan_data.get("risk_factors", [])
    )

    plan.sync()
    return plan

def generate_plan_with_ai(
    profile: BusinessProfile,
    framework: ComplianceFramework,
    policy: Optional[GeneratedPolicy],
    control_domain: str,
    timeline_weeks: int
) -> Dict:
    """Generate implementation plan using AI."""

    business_context = f"""
Company Profile:
- Name: {profile.company_name}
- Industry: {profile.industry}
- Size: {profile.employee_count} employees
- Budget: {profile.compliance_budget or 'Not specified'}
- Timeline: {profile.compliance_timeline or f'{timeline_weeks} weeks'}
- Cloud Providers: {', '.join(profile.cloud_providers) if profile.cloud_providers else 'None'}
- SaaS Tools: {', '.join(profile.saas_tools) if profile.saas_tools else 'None'}
"""

    framework_context = f"""
Framework: {framework.display_name}
Control Domain: {control_domain}
Key Requirements: {', '.join(framework.key_requirements)}
Estimated Implementation Time: {framework.implementation_time_weeks} weeks
Estimated Cost Range: {framework.estimated_cost_range}
"""

    policy_context = ""
    if policy:
        policy_context = f"""
Related Policy Controls:
{json.dumps([control['title'] for control in policy.controls[:5]], indent=2)}
"""

    prompt = f"""Create a detailed implementation plan for {framework.display_name} compliance focusing on {control_domain}.

{business_context}

{framework_context}
{policy_context}

Requirements:
1. Break down implementation into 4-6 phases with specific timelines
2. Provide detailed tasks for each phase with effort estimates (hours)
3. Assign appropriate roles (CEO, CISO, IT Manager, Staff, External Consultants)
4. Include realistic budget breakdown by category
5. Identify required external resources and tools
6. Provide specific implementation guidance
7. Consider the company size and industry context
8. Include risk factors and mitigation strategies
9. Make the plan actionable and practical

The plan should be achievable within {timeline_weeks} weeks for a {profile.employee_count}-person company.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a compliance implementation expert. Create detailed, practical implementation plans with realistic timelines and budgets."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "implementation_plan",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "phases": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "phase_number": {"type": "number"},
                                        "title": {"type": "string"},
                                        "description": {"type": "string"},
                                        "duration_weeks": {"type": "number"},
                                        "tasks": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "task_id": {"type": "string"},
                                                    "title": {"type": "string"},
                                                    "description": {"type": "string"},
                                                    "responsible_role": {"type": "string"},
                                                    "estimated_hours": {"type": "number"},
                                                    "dependencies": {
                                                        "type": "array",
                                                        "items": {"type": "string"}
                                                    },
                                                    "deliverables": {
                                                        "type": "array",
                                                        "items": {"type": "string"}
                                                    }
                                                },
                                                "required": ["task_id", "title", "description", "responsible_role", "estimated_hours", "dependencies", "deliverables"],
                                                "additionalProperties": False
                                            }
                                        }
                                    },
                                    "required": ["phase_number", "title", "description", "duration_weeks", "tasks"],
                                    "additionalProperties": False
                                }
                            },
                            "total_estimated_hours": {"type": "number"},
                            "total_estimated_cost": {"type": "string"},
                            "phase_details": {
                                "type": "object",
                                "additionalProperties": {
                                    "type": "object",
                                    "properties": {
                                        "objectives": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                        "success_criteria": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                        "key_milestones": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    },
                                    "required": ["objectives", "success_criteria", "key_milestones"],
                                    "additionalProperties": False
                                }
                            },
                            "required_roles": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "external_resources": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "budget_breakdown": {
                                "type": "object",
                                "additionalProperties": {"type": "string"}
                            },
                            "risk_factors": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "risk": {"type": "string"},
                                        "impact": {"type": "string"},
                                        "mitigation": {"type": "string"}
                                    },
                                    "required": ["risk", "impact", "mitigation"],
                                    "additionalProperties": False
                                }
                            }
                        },
                        "required": ["phases", "total_estimated_hours", "total_estimated_cost", "phase_details", "required_roles", "external_resources", "budget_breakdown", "risk_factors"],
                        "additionalProperties": False
                    }
                }
            }
        )

        return json.loads(response.choices[0].message.content)

    except Exception as e:
        raise ValueError(f"Failed to generate implementation plan: {e!s}")

@authenticated
def get_user_implementation_plans(user: User) -> List[ImplementationPlan]:
    """Get all implementation plans for the user."""
    results = ImplementationPlan.sql(
        "SELECT * FROM implementation_plans WHERE user_id = %(user_id)s ORDER BY created_at DESC",
        {"user_id": user.id}
    )

    return [ImplementationPlan(**result) for result in results]

@authenticated
def get_implementation_plan_by_id(user: User, plan_id: UUID) -> Optional[ImplementationPlan]:
    """Get a specific implementation plan by ID."""
    results = ImplementationPlan.sql(
        "SELECT * FROM implementation_plans WHERE id = %(plan_id)s AND user_id = %(user_id)s",
        {"plan_id": plan_id, "user_id": user.id}
    )

    if results:
        return ImplementationPlan(**results[0])
    return None

@authenticated
def update_plan_progress(
    user: User,
    plan_id: UUID,
    completed_tasks: List[str],
    blocked_tasks: Optional[List[str]] = None,
    progress_notes: str = ""
) -> ImplementationPlan:
    """Update the progress of an implementation plan."""

    if blocked_tasks is None:
        blocked_tasks = []
    plan = get_implementation_plan_by_id(user, plan_id)
    if not plan:
        raise ValueError("Implementation plan not found")

    # Calculate completion percentage
    total_tasks = 0
    for phase in plan.phases:
        total_tasks += len(phase.get("tasks", []))

    completion_percentage = len(completed_tasks) / total_tasks * 100 if total_tasks > 0 else 0

    plan.completed_tasks = completed_tasks
    plan.blocked_tasks = blocked_tasks
    plan.completion_percentage = completion_percentage
    plan.progress_notes = progress_notes
    plan.updated_at = datetime.now()

    # Update status based on progress
    if completion_percentage == 0:
        plan.status = "planning"
    elif completion_percentage < 100:
        plan.status = "in_progress"
        if not plan.actual_start_date:
            plan.actual_start_date = datetime.now()
    else:
        plan.status = "completed"
        plan.actual_end_date = datetime.now()

    plan.sync()
    return plan

@authenticated
def start_implementation_plan(user: User, plan_id: UUID) -> ImplementationPlan:
    """Start an implementation plan."""

    plan = get_implementation_plan_by_id(user, plan_id)
    if not plan:
        raise ValueError("Implementation plan not found")

    plan.status = "in_progress"
    plan.actual_start_date = datetime.now()
    plan.updated_at = datetime.now()

    plan.sync()
    return plan

@authenticated
def get_plan_dashboard_data(user: User, plan_id: UUID) -> Dict:
    """Get dashboard data for an implementation plan."""

    plan = get_implementation_plan_by_id(user, plan_id)
    if not plan:
        raise ValueError("Implementation plan not found")

    # Calculate phase progress
    phase_progress = []
    for phase in plan.phases:
        phase_tasks = phase.get("tasks", [])
        completed_in_phase = [task for task in phase_tasks if task.get("task_id") in plan.completed_tasks]

        phase_progress.append({
            "phase_number": phase["phase_number"],
            "title": phase["title"],
            "total_tasks": len(phase_tasks),
            "completed_tasks": len(completed_in_phase),
            "progress_percentage": len(completed_in_phase) / len(phase_tasks) * 100 if phase_tasks else 0
        })

    # Calculate timeline status
    days_elapsed = 0
    days_remaining = 0
    if plan.actual_start_date:
        days_elapsed = (datetime.now() - plan.actual_start_date).days
    if plan.planned_end_date:
        days_remaining = (plan.planned_end_date - datetime.now()).days

    # Get upcoming tasks
    upcoming_tasks = []
    for phase in plan.phases:
        for task in phase.get("tasks", []):
            if task.get("task_id") not in plan.completed_tasks:
                upcoming_tasks.append({
                    "task_id": task["task_id"],
                    "title": task["title"],
                    "phase": phase["title"],
                    "responsible_role": task["responsible_role"],
                    "estimated_hours": task["estimated_hours"]
                })

    upcoming_tasks = upcoming_tasks[:5]  # Limit to next 5 tasks

    return {
        "plan": plan,
        "phase_progress": phase_progress,
        "overall_progress": plan.completion_percentage,
        "timeline": {
            "days_elapsed": days_elapsed,
            "days_remaining": max(0, days_remaining),
            "on_track": days_remaining >= 0
        },
        "upcoming_tasks": upcoming_tasks,
        "blocked_tasks_count": len(plan.blocked_tasks),
        "total_tasks": sum(len(phase.get("tasks", [])) for phase in plan.phases)
    }
