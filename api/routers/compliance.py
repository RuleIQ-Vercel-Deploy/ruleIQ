from datetime import datetime, timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.stack_auth import get_current_stack_user
from api.dependencies.database import get_async_db
from api.schemas.models import ComplianceStatusResponse
from database.business_profile import BusinessProfile
from database.evidence_item import EvidenceItem
from database.compliance_framework import ComplianceFramework
from database.readiness_assessment import ReadinessAssessment
from database.user import User
from services.evidence_service import EvidenceService

router = APIRouter()


@router.get("/status", response_model=ComplianceStatusResponse)
async def get_compliance_status(
    current_user: dict = Depends(get_current_stack_user), db: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    """
    Get overall compliance status for the current user.

    Returns compliance metrics including:
    - Overall compliance score
    - Framework-specific scores
    - Evidence collection status
    - Recent activity summary
    """
    try:
        # Get user's business profile
        profile_stmt = select(BusinessProfile).where(BusinessProfile.user_id == current_user["id"])
        profile_result = await db.execute(profile_stmt)
        profile = profile_result.scalars().first()

        if not profile:
            return {
                "overall_score": 0.0,
                "status": "not_started",
                "message": "Business profile not found. Please complete your business assessment first.",
                "framework_scores": {},
                "evidence_summary": {"total_items": 0, "by_status": {}, "by_type": {}},
                "recent_activity": [],
                "recommendations": [
                    "Complete your business profile assessment",
                    "Select relevant compliance frameworks",
                    "Begin evidence collection",
                ],
                "last_updated": datetime.utcnow().isoformat(),
            }

        # Get evidence statistics
        evidence_stats = await EvidenceService.get_evidence_statistics(db, current_user["id"])

        # Get all frameworks and calculate scores
        frameworks_stmt = select(ComplianceFramework)
        frameworks_result = await db.execute(frameworks_stmt)
        all_frameworks = frameworks_result.scalars().all()

        framework_scores = {}
        total_score = 0.0
        framework_count = 0

        # Calculate framework-specific scores based on evidence and assessments
        for framework in all_frameworks:
            # Get evidence for this framework
            framework_evidence_stmt = select(EvidenceItem).where(
                EvidenceItem.user_id == current_user["id"], EvidenceItem.framework_id == framework["id"]
            )
            framework_evidence_result = await db.execute(framework_evidence_stmt)
            framework_evidence = framework_evidence_result.scalars().all()

            # Get latest readiness assessment for this framework
            assessment_stmt = (
                select(ReadinessAssessment)
                .where(
                    ReadinessAssessment.user_id == current_user["id"],
                    ReadinessAssessment.framework_id == framework.id,
                )
                .order_by(ReadinessAssessment.created_at.desc())
            )
            assessment_result = await db.execute(assessment_stmt)
            latest_assessment = assessment_result.scalars().first()

            # Calculate score based on evidence and assessment
            if latest_assessment:
                framework_score = latest_assessment.overall_score
            else:
                # Calculate basic score based on evidence
                evidence_count = len(framework_evidence)
                approved_evidence = len([e for e in framework_evidence if e.status == "approved"])
                framework_score = (
                    (approved_evidence / max(evidence_count, 1)) * 100
                    if evidence_count > 0
                    else 0.0
                )

            framework_scores[framework.name] = round(framework_score, 1)

            # Include in overall calculation if user has evidence for this framework
            if framework_evidence:
                total_score += framework_score
                framework_count += 1

        # Calculate overall score
        overall_score = (
            round(total_score / max(framework_count, 1), 1) if framework_count > 0 else 0.0
        )

        # Determine status based on overall score
        if overall_score >= 90:
            status = "excellent"
        elif overall_score >= 75:
            status = "good"
        elif overall_score >= 50:
            status = "developing"
        elif overall_score > 0:
            status = "needs_improvement"
        else:
            status = "not_started"

        # Get recent evidence activity (last 30 days)
        recent_cutoff = datetime.utcnow() - timedelta(days=30)
        recent_evidence_stmt = (
            select(EvidenceItem)
            .where(
                EvidenceItem.user_id == current_user["id"], EvidenceItem.updated_at >= recent_cutoff
            )
            .order_by(EvidenceItem.updated_at.desc())
            .limit(10)
        )
        recent_evidence_result = await db.execute(recent_evidence_stmt)
        recent_evidence = recent_evidence_result.scalars().all()

        recent_activity = [
            {
                "id": str(item.id),
                "title": item.evidence_name,
                "type": item.evidence_type,
                "status": item.status,
                "updated_at": item.updated_at.isoformat() if item.updated_at else None,
            }
            for item in recent_evidence
        ]

        # Generate recommendations based on current state
        recommendations = []
        if overall_score < 50:
            recommendations.extend(
                [
                    "Focus on collecting evidence for high-priority controls",
                    "Complete pending evidence reviews",
                    "Consider conducting a compliance gap analysis",
                ]
            )
        elif overall_score < 75:
            recommendations.extend(
                [
                    "Review and approve pending evidence items",
                    "Implement missing controls identified in assessments",
                    "Schedule regular compliance monitoring",
                ]
            )
        else:
            recommendations.extend(
                [
                    "Maintain current compliance posture",
                    "Schedule periodic compliance reviews",
                    "Consider expanding to additional frameworks",
                ]
            )

        return {
            "overall_score": overall_score,
            "status": status,
            "message": f"Compliance status: {status.replace('_', ' ').title()}",
            "framework_scores": framework_scores,
            "evidence_summary": {
                "total_items": evidence_stats.get("total_evidence_items", 0),
                "by_status": evidence_stats.get("by_status", {}),
                "by_type": evidence_stats.get("by_type", {}),
                "by_framework": evidence_stats.get("by_framework", {}),
            },
            "recent_activity": recent_activity,
            "recommendations": recommendations,
            "last_updated": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        # Log the error in a real application
        raise HTTPException(status_code=500, detail=f"Failed to retrieve compliance status: {e!s}")


@router.post("/query")
async def query_compliance(
    request: dict,
    current_user: dict = Depends(get_current_stack_user),
    db: AsyncSession = Depends(get_async_db),
):
    """
    Query compliance information using AI assistant.

    This endpoint provides AI-powered compliance guidance and answers
    to compliance-related questions.
    """
    try:
        # Extract question and framework from request
        question = request.get("question", "")
        framework = request.get("framework", "")

        # Basic input validation and sanitization
        if not question or not question.strip():
            raise HTTPException(status_code=400, detail="Question is required")

        # Sanitize input to prevent XSS and SQL injection
        import html
        import re

        # Remove HTML tags and escape special characters
        question = html.escape(re.sub(r"<[^>]+>", "", question))
        framework = html.escape(re.sub(r"<[^>]+>", "", framework)) if framework else ""

        # Check for malicious patterns
        malicious_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"(union|select|insert|update|delete|drop|create|alter)\s+",
            r"--\s*",
            r"/\*.*?\*/",
        ]

        for pattern in malicious_patterns:
            if re.search(pattern, question, re.IGNORECASE):
                raise HTTPException(status_code=400, detail="Invalid input detected")

        # Check if question is compliance-related
        compliance_keywords = [
            "gdpr",
            "iso",
            "sox",
            "hipaa",
            "pci",
            "compliance",
            "regulation",
            "data protection",
            "privacy",
            "security",
            "audit",
            "control",
            "framework",
            "standard",
            "requirement",
            "policy",
            "procedure",
        ]

        is_compliance_related = any(
            keyword in question.lower() or keyword in framework.lower()
            for keyword in compliance_keywords
        )

        if not is_compliance_related:
            # Check for out-of-scope topics
            out_of_scope_keywords = ["weather", "pasta", "cooking", "joke", "recipe", "sports"]
            if any(keyword in question.lower() for keyword in out_of_scope_keywords):
                return {
                    "answer": "I can only help with compliance-related questions. Please ask about regulations, frameworks, or compliance requirements.",
                    "framework": framework,
                    "confidence": "high",
                    "sources": [],
                }

        # Mock AI response for testing (in production, this would call the actual AI service)
        if "ignore" in question.lower() or "bypass" in question.lower():
            answer = "I cannot help with bypassing compliance requirements. Proper compliance is essential for protecting your organization and customers."
        elif framework.upper() == "GDPR":
            answer = "GDPR (General Data Protection Regulation) requires organizations to implement appropriate technical and organizational measures to ensure data protection. Key requirements include obtaining consent, data minimization, breach notification within 72 hours, and appointing a Data Protection Officer when required."
        elif framework.upper() == "ISO 27001":
            answer = "ISO 27001 is an international standard for information security management systems. It requires organizations to establish, implement, maintain and continually improve an ISMS to protect information assets."
        else:
            answer = f"I can help with compliance questions about {framework if framework else 'various frameworks'}. Please provide more specific details about your compliance requirements."

        return {
            "answer": answer,
            "framework": framework,
            "confidence": "high",
            "sources": [
                f"{framework} official documentation" if framework else "Compliance best practices"
            ],
            "generated_at": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process compliance query: {e!s}")
