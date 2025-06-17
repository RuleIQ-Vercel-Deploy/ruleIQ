import json
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from core.business_profile import BusinessProfile
from core.compliance_framework import ComplianceFramework
from core.evidence_item import EvidenceItem
from core.generated_policy import GeneratedPolicy
from sqlalchemy_access import User, authenticated


@authenticated
def generate_evidence_checklist(
    user: User,
    framework_id: UUID,
    policy_id: Optional[UUID] = None
) -> List[EvidenceItem]:
    """Generate a comprehensive evidence checklist for a compliance framework."""

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

    # Check if evidence items already exist for this framework
    existing_items = EvidenceItem.sql(
        "SELECT * FROM evidence_items WHERE user_id = %(user_id)s AND framework_id = %(framework_id)s",
        {"user_id": user.id, "framework_id": framework_id}
    )

    if existing_items:
        return [EvidenceItem(**item) for item in existing_items]

    # Generate evidence items using AI
    evidence_data = generate_evidence_with_ai(profile, framework, policy)

    evidence_items = []
    for item_data in evidence_data["evidence_items"]:
        evidence_item = EvidenceItem(
            user_id=user.id,
            business_profile_id=profile.id,
            framework_id=framework_id,
            evidence_name=item_data["evidence_name"],
            evidence_type=item_data["evidence_type"],
            control_reference=item_data["control_reference"],
            description=item_data["description"],
            required_for_audit=item_data["required_for_audit"],
            collection_frequency=item_data["collection_frequency"],
            collection_method=item_data["collection_method"],
            automation_source=item_data.get("automation_source"),
            automation_guidance=item_data.get("automation_guidance", ""),
            priority=item_data["priority"],
            effort_estimate=item_data["effort_estimate"],
            audit_section=item_data.get("audit_section", ""),
            compliance_score_impact=item_data.get("compliance_score_impact", 0.0)
        )
        evidence_item.sync()
        evidence_items.append(evidence_item)

    return evidence_items

def generate_evidence_with_ai(
    profile: BusinessProfile,
    framework: ComplianceFramework,
    policy: Optional[GeneratedPolicy]
) -> Dict:
    """Generate evidence requirements using AI."""

    business_context = f"""
Company Profile:
- Name: {profile.company_name}
- Industry: {profile.industry}
- Size: {profile.employee_count} employees
- Cloud Providers: {', '.join(profile.cloud_providers) if profile.cloud_providers else 'None'}
- SaaS Tools: {', '.join(profile.saas_tools) if profile.saas_tools else 'None'}
- Development Tools: {', '.join(profile.development_tools) if profile.development_tools else 'None'}
"""

    framework_context = f"""
Framework: {framework.display_name}
Key Requirements: {', '.join(framework.key_requirements)}
Control Domains: {', '.join(framework.control_domains)}
"""

    policy_context = ""
    if policy:
        policy_context = f"""
Policy Controls:
{json.dumps([{'id': control['control_id'], 'title': control['title']} for control in policy.controls[:10]], indent=2)}
"""

    prompt = f"""Generate a comprehensive evidence collection checklist for {framework.display_name} compliance.

{business_context}

{framework_context}
{policy_context}

Requirements:
1. Include all evidence required for audit compliance
2. Specify collection methods (manual, automated, semi-automated)
3. Provide automation guidance for cloud tools where applicable
4. Prioritize evidence by criticality (low, medium, high, critical)
5. Estimate effort required for collection
6. Consider the company's technology stack for automation opportunities
7. Include both policies/procedures and technical evidence
8. Map evidence to specific controls and audit sections
9. Specify collection frequency (once, monthly, quarterly, annually)

Focus on practical, achievable evidence collection that auditors expect to see for {framework.display_name} certification.
"""

    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a compliance auditor and evidence collection expert. Generate comprehensive, practical evidence checklists."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "evidence_checklist",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "properties": {
                            "evidence_items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "evidence_name": {"type": "string"},
                                        "evidence_type": {"type": "string"},
                                        "control_reference": {"type": "string"},
                                        "description": {"type": "string"},
                                        "required_for_audit": {"type": "boolean"},
                                        "collection_frequency": {"type": "string"},
                                        "collection_method": {"type": "string"},
                                        "automation_source": {
                                            "type": ["string", "null"]
                                        },
                                        "automation_guidance": {"type": "string"},
                                        "priority": {"type": "string"},
                                        "effort_estimate": {"type": "string"},
                                        "audit_section": {"type": "string"},
                                        "compliance_score_impact": {"type": "number"}
                                    },
                                    "required": [
                                        "evidence_name", "evidence_type", "control_reference",
                                        "description", "required_for_audit", "collection_frequency",
                                        "collection_method", "automation_source", "automation_guidance",
                                        "priority", "effort_estimate", "audit_section", "compliance_score_impact"
                                    ],
                                    "additionalProperties": False
                                }
                            }
                        },
                        "required": ["evidence_items"],
                        "additionalProperties": False
                    }
                }
            }
        )

        return json.loads(response.choices[0].message.content)

    except Exception as e:
        raise ValueError(f"Failed to generate evidence checklist: {e!s}")

@authenticated
def get_user_evidence_items(user: User, framework_id: Optional[UUID] = None) -> List[EvidenceItem]:
    """Get evidence items for the user, optionally filtered by framework."""

    if framework_id:
        results = EvidenceItem.sql(
            "SELECT * FROM evidence_items WHERE user_id = %(user_id)s AND framework_id = %(framework_id)s ORDER BY priority DESC, evidence_name",
            {"user_id": user.id, "framework_id": framework_id}
        )
    else:
        results = EvidenceItem.sql(
            "SELECT * FROM evidence_items WHERE user_id = %(user_id)s ORDER BY priority DESC, evidence_name",
            {"user_id": user.id}
        )

    return [EvidenceItem(**result) for result in results]

@authenticated
def update_evidence_status(
    user: User,
    evidence_id: UUID,
    status: str,
    collection_notes: str = "",
    collected_by: Optional[str] = None
) -> EvidenceItem:
    """Update the status of an evidence item."""

    results = EvidenceItem.sql(
        "SELECT * FROM evidence_items WHERE id = %(evidence_id)s AND user_id = %(user_id)s",
        {"evidence_id": evidence_id, "user_id": user.id}
    )

    if not results:
        raise ValueError("Evidence item not found")

    evidence = EvidenceItem(**results[0])
    evidence.status = status
    evidence.collection_notes = collection_notes
    evidence.updated_at = datetime.now()

    if status == "collected":
        evidence.collected_by = collected_by or user.email
        evidence.collected_at = datetime.now()
    elif status == "approved":
        evidence.approved_by = user.email
        evidence.approved_at = datetime.now()

    evidence.sync()
    return evidence

@authenticated
def get_evidence_dashboard_data(user: User, framework_id: Optional[UUID] = None) -> Dict:
    """Get dashboard data for evidence collection."""

    evidence_items = get_user_evidence_items(user, framework_id)

    # Calculate status counts
    status_counts = {
        "not_started": 0,
        "in_progress": 0,
        "collected": 0,
        "approved": 0,
        "rejected": 0
    }

    priority_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0
    }

    automation_opportunities = 0
    total_compliance_impact = 0

    for item in evidence_items:
        status_counts[item.status] = status_counts.get(item.status, 0) + 1
        priority_counts[item.priority] = priority_counts.get(item.priority, 0) + 1

        if item.collection_method in ["automated", "semi_automated"]:
            automation_opportunities += 1

        total_compliance_impact += item.compliance_score_impact

    # Calculate completion percentage
    total_items = len(evidence_items)
    completed_items = status_counts["approved"] + status_counts["collected"]
    completion_percentage = (completed_items / total_items * 100) if total_items > 0 else 0

    # Get upcoming deadlines (items that should be collected soon)
    upcoming_items = [
        item for item in evidence_items
        if item.status in ["not_started", "in_progress"] and item.priority in ["critical", "high"]
    ][:5]

    return {
        "total_items": total_items,
        "completion_percentage": completion_percentage,
        "status_breakdown": status_counts,
        "priority_breakdown": priority_counts,
        "automation_opportunities": automation_opportunities,
        "total_compliance_impact": total_compliance_impact,
        "upcoming_items": [
            {
                "id": item.id,
                "name": item.evidence_name,
                "priority": item.priority,
                "effort_estimate": item.effort_estimate,
                "automation_source": item.automation_source
            } for item in upcoming_items
        ]
    }

@authenticated
def get_automation_guidance(user: User, cloud_provider: str) -> Dict:
    """Get automation guidance for specific cloud providers."""

    guidance_map = {
        "AWS": {
            "access_logs": "CloudTrail API calls, S3 access logs, VPC Flow Logs",
            "security_config": "Config Rules, Security Hub findings, GuardDuty alerts",
            "backup_evidence": "AWS Backup job status, EBS snapshot schedules",
            "encryption_status": "KMS key usage, EBS/S3 encryption status",
            "user_access": "IAM policies, roles, and access analyzer reports"
        },
        "Microsoft Azure": {
            "access_logs": "Azure Activity Log, Azure AD sign-in logs",
            "security_config": "Azure Security Center recommendations, policies",
            "backup_evidence": "Azure Backup reports, recovery services vault status",
            "encryption_status": "Azure Key Vault usage, disk encryption status",
            "user_access": "Azure AD roles, conditional access policies"
        },
        "Google Cloud": {
            "access_logs": "Cloud Audit Logs, Cloud Logging exports",
            "security_config": "Security Command Center findings, policies",
            "backup_evidence": "Cloud Storage lifecycle policies, snapshots",
            "encryption_status": "Cloud KMS usage, persistent disk encryption",
            "user_access": "IAM policies, Cloud Identity roles"
        },
        "Microsoft 365": {
            "access_logs": "Office 365 audit logs, Azure AD sign-ins",
            "data_governance": "Data Loss Prevention reports, retention policies",
            "security_config": "Microsoft Secure Score, compliance manager",
            "user_access": "Admin role assignments, conditional access",
            "email_security": "Exchange Online Protection reports, anti-malware"
        },
        "Google Workspace": {
            "access_logs": "Google Workspace audit logs, login reports",
            "data_governance": "Drive audit reports, Vault exports",
            "security_config": "Admin console security reports",
            "user_access": "Admin role assignments, 2FA status",
            "email_security": "Gmail security reports, phishing protection"
        }
    }

    return guidance_map.get(cloud_provider, {})

@authenticated
def bulk_update_evidence_status(
    user: User,
    evidence_ids: List[UUID],
    status: str,
    notes: str = ""
) -> List[EvidenceItem]:
    """Bulk update multiple evidence items."""

    updated_items = []

    for evidence_id in evidence_ids:
        try:
            item = update_evidence_status(user, evidence_id, status, notes)
            updated_items.append(item)
        except ValueError:
            # Skip items that don't exist or don't belong to user
            continue

    return updated_items
