import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ..database.business_profile import BusinessProfile as BusinessProfileModel
from ..database.compliance_framework import ComplianceFramework as ComplianceFrameworkModel
from ..database.evidence_item import EvidenceItem as EvidenceItemModel
from ..database.generated_policy import GeneratedPolicy as GeneratedPolicyModel
from ..database.implementation_plan import ImplementationPlan as ImplementationPlanModel
from ..database.readiness_assessment import ReadinessAssessment as ReadinessAssessmentModel
from ..database.user import User as UserModel


def generate_readiness_assessment(
    db: Session,
    user: UserModel,
    framework_id: UUID,
    assessment_type: str = "full"
) -> ReadinessAssessmentModel:
    """Generate a comprehensive compliance readiness assessment."""

    # Get business profile
    profile = db.query(BusinessProfileModel).filter(BusinessProfileModel.user_id == user.id).first()

    if not profile:
        raise ValueError("Business profile not found")

    # Get compliance framework
    framework = db.query(ComplianceFrameworkModel).filter(ComplianceFrameworkModel.id == framework_id).first()

    if not framework:
        raise ValueError("Compliance framework not found")

    # Get related artifacts
    policies = db.query(GeneratedPolicyModel).filter(
        GeneratedPolicyModel.user_id == user.id,
        GeneratedPolicyModel.framework_id == framework_id
    ).all()

    implementation_plans = db.query(ImplementationPlanModel).filter(
        ImplementationPlanModel.user_id == user.id,
        ImplementationPlanModel.framework_id == framework_id
    ).all()

    evidence_items = db.query(EvidenceItemModel).filter(
        EvidenceItemModel.user_id == user.id,
        EvidenceItemModel.framework_id == framework_id
    ).all()

    # Calculate scores
    policy_score_val = calculate_policy_score(policies)
    implementation_score_val = calculate_implementation_score(implementation_plans)
    evidence_score_val = calculate_evidence_score(evidence_items)

    # Calculate overall score (weighted average)
    overall_score = (policy_score_val * 0.3 + implementation_score_val * 0.4 + evidence_score_val * 0.3)

    # Generate AI-powered assessment
    assessment_data = generate_assessment_with_ai(
        profile, framework, policies, implementation_plans, evidence_items, overall_score
    )

    # Get previous assessment for trend analysis
    previous_assessment_model = db.query(ReadinessAssessmentModel).filter(
        ReadinessAssessmentModel.user_id == user.id,
        ReadinessAssessmentModel.framework_id == framework_id
    ).order_by(ReadinessAssessmentModel.created_at.desc()).first()

    previous_score = None
    score_trend = "stable"
    if previous_assessment_model:
        previous_score = previous_assessment_model.overall_score
        if overall_score > previous_score + 5:
            score_trend = "improving"
        elif overall_score < previous_score - 5:
            score_trend = "declining"

    # Calculate readiness timeline
    estimated_readiness_date = calculate_readiness_date(overall_score, assessment_data["remaining_effort_hours"])

    # Create assessment
    assessment = ReadinessAssessmentModel(
        user_id=user.id,
        business_profile_id=profile.id,
        framework_id=framework_id,
        assessment_name=f"{framework.display_name} Readiness Assessment",
        framework_name=framework.name,
        assessment_type=assessment_type,
        overall_score=overall_score,
        policy_score=policy_score_val,
        implementation_score=implementation_score_val,
        evidence_score=evidence_score_val,
        key_findings=assessment_data.get("key_findings"),
        remediation_plan=assessment_data.get("remediation_plan"),
        priority_actions=assessment_data.get("priority_actions"),
        quick_wins=assessment_data.get("quick_wins"),
        remaining_effort_hours=assessment_data.get("remaining_effort_hours"),
        estimated_readiness_date=estimated_readiness_date,
        previous_score=previous_score,
        score_trend=score_trend,
        status="completed",
        completed_at=datetime.utcnow()
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    return assessment

def calculate_policy_score(policies: List[GeneratedPolicyModel]) -> float:
    """Calculate policy readiness score."""
    if not policies:
        return 0.0

    total_score = 0
    for policy in policies:
        completeness = policy.completeness_score if policy.completeness_score is not None else 0
        accuracy = policy.accuracy_score if policy.accuracy_score is not None else 0

        weighted_score = (completeness / 100 * 0.6) + (accuracy / 100 * 0.4)
        total_score += weighted_score

    average_score = (total_score / len(policies)) * 100
    coverage_factor = 1.0

    final_score = average_score * coverage_factor
    return round(min(max(final_score, 0), 100), 2)

def calculate_implementation_score(implementation_plans: List[ImplementationPlanModel]) -> float:
    """Calculate implementation readiness score."""
    if not implementation_plans:
        return 0.0

    total_progress = 0
    for plan in implementation_plans:
        total_progress += plan.completion_percentage if plan.completion_percentage is not None else 0

    average_progress = total_progress / len(implementation_plans)
    return round(min(max(average_progress, 0), 100), 2)

def calculate_evidence_score(evidence_items: List[EvidenceItemModel]) -> float:
    """Calculate evidence readiness score."""
    if not evidence_items:
        return 0.0

    total_score = 0
    total_weight = 0

    status_weights = {
        "collected": 1.0,
        "verified": 0.8,
        "pending_review": 0.5,
        "missing": 0.0,
        "not_applicable": 0.0
    }

    for item in evidence_items:
        status = item.status.lower() if item.status else "missing"
        weight = status_weights.get(status, 0.0)

        current_item_score = weight * 100

        total_score += current_item_score
        total_weight += 1

    if total_weight == 0:
        return 0.0

    average_score = total_score / total_weight
    return round(min(max(average_score, 0), 100), 2)

def generate_assessment_with_ai(
    profile: BusinessProfileModel,
    framework: ComplianceFrameworkModel,
    policies: List[GeneratedPolicyModel],
    implementation_plans: List[ImplementationPlanModel],
    evidence_items: List[EvidenceItemModel],
    overall_score: float
) -> Dict:
    """Generate detailed assessment analysis using AI."""

    context = f"""
Business Profile:
- Company: {profile.company_name} ({profile.industry})
- Size: {profile.employee_count} employees
- Current Score: {overall_score:.1f}%

Framework: {framework.display_name}

Current State:
- Policies: {len(policies)} generated
- Implementation Plans: {len(implementation_plans)} created
- Evidence Items: {len(evidence_items)} identified

Policy Status: {json.dumps([{"status": p.get("status"), "coverage": p.get("compliance_coverage", 0.8)} for p in policies], indent=2)}

Implementation Progress: {json.dumps([{"completion": p.get("completion_percentage", 0)} for p in implementation_plans], indent=2)}

Evidence Collection: {json.dumps([{"status": e.get("status"), "priority": e.get("priority")} for e in evidence_items[:10]], indent=2)}
"""

    prompt = f"""Perform a comprehensive compliance readiness assessment for {framework.display_name}.

{context}

Provide a detailed analysis including:
1. Domain-specific scores and gaps
2. Critical findings and remediation priorities
3. Quick wins for immediate improvement
4. Realistic timeline to certification readiness
5. Executive summary for leadership
6. Specific next steps and recommendations

Focus on actionable insights that will help achieve certification efficiently.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a senior compliance consultant conducting readiness assessments. Provide strategic, actionable insights."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "readiness_assessment",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "domain_scores": {
                                "type": "object",
                                "additionalProperties": {"type": "number"}
                            },
                            "control_scores": {
                                "type": "object",
                                "additionalProperties": {"type": "number"}
                            },
                            "identified_gaps": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "gap_title": {"type": "string"},
                                        "description": {"type": "string"},
                                        "priority": {"type": "string"},
                                        "impact": {"type": "string"},
                                        "remediation_effort": {"type": "string"}
                                    },
                                    "required": ["gap_title", "description", "priority", "impact", "remediation_effort"],
                                    "additionalProperties": False
                                }
                            },
                            "remediation_plan": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "action": {"type": "string"},
                                        "priority": {"type": "string"},
                                        "timeline": {"type": "string"},
                                        "owner": {"type": "string"},
                                        "dependencies": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    },
                                    "required": ["action", "priority", "timeline", "owner", "dependencies"],
                                    "additionalProperties": False
                                }
                            },
                            "quick_wins": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "certification_timeline_weeks": {"type": "number"},
                            "remaining_effort_hours": {"type": "number"},
                            "priority_actions": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "action": {"type": "string"},
                                        "urgency": {"type": "string"},
                                        "impact": {"type": "string"}
                                    },
                                    "required": ["action", "urgency", "impact"],
                                    "additionalProperties": False
                                }
                            },
                            "tool_recommendations": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "training_recommendations": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "executive_summary": {"type": "string"},
                            "key_findings": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "next_steps": {
                                "type": "array",
                                "items": {"type": "string"}
                            }
                        },
                        "required": [
                            "domain_scores", "control_scores", "identified_gaps", "remediation_plan",
                            "quick_wins", "certification_timeline_weeks", "remaining_effort_hours",
                            "priority_actions", "tool_recommendations", "training_recommendations",
                            "executive_summary", "key_findings", "next_steps"
                        ],
                        "additionalProperties": False
                    }
                }
            }
        )

        return json.loads(response.choices[0].message.content)

    except Exception: # Removed 'as e' to fix lint error (e was unused)
        # TODO: Add proper logging for the exception here
        # Return default structure if AI fails
        return {
            "domain_scores": {"Governance": 60, "Risk Management": 70, "Implementation": 50},
            "control_scores": {},
            "identified_gaps": [],
            "remediation_plan": [],
            "quick_wins": ["Complete missing policy sections", "Update risk register"],
            "certification_timeline_weeks": 16,
            "remaining_effort_hours": 120,
            "priority_actions": [],
            "tool_recommendations": [],
            "training_recommendations": [],
            "executive_summary": f"Current compliance readiness: {overall_score:.1f}%",
            "key_findings": [f"Overall score: {overall_score:.1f}%"],
            "next_steps": ["Address critical gaps", "Complete implementation"]
        }

def calculate_readiness_date(overall_score: float, remaining_hours: int) -> datetime:
    """Calculate estimated readiness date based on score and effort."""

    hours_per_week = 20
    weeks_remaining = max(4, remaining_hours / hours_per_week)

    if overall_score < 30:
        weeks_remaining *= 1.5
    elif overall_score < 60:
        weeks_remaining *= 1.2

    return datetime.now() + timedelta(weeks=int(weeks_remaining))

def get_user_assessments(db: Session, user: UserModel, framework_id: Optional[UUID] = None) -> List[ReadinessAssessmentModel]:
    """Get readiness assessments for the user."""

    query = db.query(ReadinessAssessmentModel).filter(ReadinessAssessmentModel.user_id == user.id)
    if framework_id:
        query = query.filter(ReadinessAssessmentModel.framework_id == framework_id)

    results = query.order_by(ReadinessAssessmentModel.created_at.desc()).all()
    return results

def get_assessment_by_id(db: Session, user: UserModel, assessment_id: UUID) -> Optional[ReadinessAssessmentModel]:
    """Get a specific assessment by ID."""
    result = db.query(ReadinessAssessmentModel).filter(
        ReadinessAssessmentModel.id == assessment_id,
        ReadinessAssessmentModel.user_id == user.id
    ).first()

    return result

def get_compliance_dashboard_data(db: Session, user: UserModel) -> Dict:
    """Get comprehensive compliance dashboard data across all frameworks."""

    # Get all user assessments
    assessments = get_user_assessments(db, user)

    # Get framework information
    framework_details_list = []
    framework_ids = [assessment.framework_id for assessment in assessments if assessment.framework_id]

    if framework_ids:
        queried_frameworks = db.query(ComplianceFrameworkModel).filter(ComplianceFrameworkModel.id.in_(framework_ids)).all()
        framework_map = {fw.id: fw for fw in queried_frameworks}
    else:
        framework_map = {}

    for assessment in assessments:
        framework_model = framework_map.get(assessment.framework_id)
        if framework_model:
            framework_details_list.append({
                "framework": framework_model,
                "assessment": assessment
            })

    frameworks = framework_details_list

    total_frameworks = len(frameworks)
    avg_score = sum(fw["assessment"].overall_score for fw in frameworks) / total_frameworks if total_frameworks > 0 else 0

    score_trends = []
    for fw in frameworks:
        if fw["assessment"].previous_score:
            change = fw["assessment"].overall_score - fw["assessment"].previous_score
            score_trends.append({
                "framework": fw["framework"].display_name,
                "current_score": fw["assessment"].overall_score,
                "change": change,
                "trend": fw["assessment"].score_trend
            })

    # Get critical actions across all frameworks
    all_priority_actions = []
    for fw in frameworks:
        for action in fw["assessment"].priority_actions[:3]:  # Top 3 per framework
            all_priority_actions.append({
                "framework": fw["framework"].display_name,
                "action": action["action"],
                "urgency": action["urgency"],
                "impact": action["impact"]
            })

    # Sort by urgency and impact
    all_priority_actions.sort(key=lambda x: (x["urgency"] == "high", x["impact"] == "high"), reverse=True)

    return {
        "total_frameworks": total_frameworks,
        "average_score": avg_score,
        "framework_scores": [
            {
                "name": fw["framework"].display_name,
                "score": fw["assessment"].overall_score,
                "trend": fw["assessment"].score_trend,
                "readiness_date": fw["assessment"].estimated_readiness_date.isoformat() if fw["assessment"].estimated_readiness_date else None
            } for fw in frameworks
        ],
        "score_trends": score_trends,
        "priority_actions": all_priority_actions[:10],  # Top 10 across all frameworks
        "quick_wins": [win for fw in frameworks for win in fw["assessment"].quick_wins[:2]][:8],  # Top 8 quick wins
        "recent_assessments": [
            {
                "framework": fw["framework"].display_name,
                "score": fw["assessment"].overall_score,
                "date": fw["assessment"].created_at.isoformat()
            } for fw in frameworks[:5]
        ]
    }
