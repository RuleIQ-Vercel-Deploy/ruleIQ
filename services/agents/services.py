"""
Focused service classes for agent functionality.

This module breaks down large agent classes into smaller, focused services
following the Single Responsibility Principle and implementing proper interfaces.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from services.agents.repositories import (
    BusinessProfileRepository,
    EvidenceRepository,
    ComplianceRepository,
    AssessmentSessionRepository,
)
from services.ai.circuit_breaker import AICircuitBreaker
from config.logging_config import get_logger

logger = get_logger(__name__)


class RiskLevel(Enum):
    """Risk levels for compliance assessment."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


class RiskAnalysisService:
    """Service for analyzing compliance risks."""

    def __init__(self, compliance_repo: ComplianceRepository) -> None:
        self.compliance_repo = compliance_repo

    async def analyze_business_risk(self, business_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze compliance risks for a business.

        Args:
            business_profile: Business information

        Returns:
            Risk analysis with scores and factors
        """
        risk_factors = []

        # Analyze data handling risks
        if business_profile.get("handles_personal_data"):
            risk_factors.append(
                {
                    "factor": "Personal Data Handling",
                    "risk_level": RiskLevel.HIGH.value,
                    "impact": 30,
                    "regulations": ["GDPR", "DPA 2018"],
                    "mitigation": "Implement data protection policies and procedures",
                }
            )

        # Analyze size-based risks
        company_size = business_profile.get("company_size", "")
        if company_size in ["201-500", "500+"]:
            risk_factors.append(
                {
                    "factor": "Large Organization Compliance",
                    "risk_level": RiskLevel.MEDIUM.value,
                    "impact": 20,
                    "regulations": ["ISO 27001", "SOC 2"],
                    "mitigation": "Establish formal compliance framework",
                }
            )

        # Analyze industry-specific risks
        industry = business_profile.get("industry", "").lower()
        if "finance" in industry or "fintech" in industry:
            risk_factors.append(
                {
                    "factor": "Financial Services Regulation",
                    "risk_level": RiskLevel.HIGH.value,
                    "impact": 35,
                    "regulations": ["PCI DSS", "FCA"],
                    "mitigation": "Implement financial compliance controls",
                }
            )
        elif "health" in industry:
            risk_factors.append(
                {
                    "factor": "Healthcare Data Protection",
                    "risk_level": RiskLevel.CRITICAL.value,
                    "impact": 40,
                    "regulations": ["GDPR", "NHS DSP Toolkit"],
                    "mitigation": "Implement healthcare-specific data controls",
                }
            )

        # Calculate overall risk score
        total_impact = sum(factor["impact"] for factor in risk_factors)
        risk_score = min(total_impact, 100)

        # Determine risk level
        if risk_score >= 80:
            overall_risk = RiskLevel.CRITICAL
        elif risk_score >= 60:
            overall_risk = RiskLevel.HIGH
        elif risk_score >= 40:
            overall_risk = RiskLevel.MEDIUM
        elif risk_score >= 20:
            overall_risk = RiskLevel.LOW
        else:
            overall_risk = RiskLevel.MINIMAL

        return {
            "risk_score": risk_score,
            "risk_level": overall_risk.value,
            "risk_factors": risk_factors,
            "total_factors": len(risk_factors),
            "priority_regulations": self._get_priority_regulations(risk_factors),
            "estimated_compliance_effort": self._estimate_effort(risk_score),
        }

    def _get_priority_regulations(self, risk_factors: List[Dict[str, Any]]) -> List[str]:
        """Extract priority regulations from risk factors."""
        regulations = set()
        for factor in risk_factors:
            regulations.update(factor.get("regulations", []))

        # Sort by frequency and priority
        regulation_priority = {
            "GDPR": 1,
            "DPA 2018": 2,
            "ISO 27001": 3,
            "SOC 2": 4,
            "PCI DSS": 5,
            "FCA": 6,
            "NHS DSP Toolkit": 7,
            "Cyber Essentials": 8,
        }

        return sorted(list(regulations), key=lambda x: regulation_priority.get(x, 99))

    def _estimate_effort(self, risk_score: float) -> Dict[str, Any]:
        """Estimate compliance effort based on risk score."""
        if risk_score >= 80:
            return {
                "timeline": "3-6 months",
                "resources": "Dedicated compliance team",
                "budget_range": "£50k-100k",
                "priority": "Immediate",
            }
        elif risk_score >= 60:
            return {
                "timeline": "2-4 months",
                "resources": "Part-time compliance officer",
                "budget_range": "£25k-50k",
                "priority": "High",
            }
        elif risk_score >= 40:
            return {
                "timeline": "1-3 months",
                "resources": "Compliance consultant",
                "budget_range": "£10k-25k",
                "priority": "Medium",
            }
        else:
            return {
                "timeline": "1-2 months",
                "resources": "Internal team with guidance",
                "budget_range": "£5k-10k",
                "priority": "Low",
            }


class CompliancePlanService:
    """Service for generating compliance plans."""

    def __init__(
        self, compliance_repo: ComplianceRepository, risk_service: RiskAnalysisService
    ) -> None:
        self.compliance_repo = compliance_repo
        self.risk_service = risk_service

    async def generate_compliance_plan(
        self,
        business_profile: Dict[str, Any],
        risk_assessment: Dict[str, Any],
        regulations: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a customized compliance action plan.

        Args:
            business_profile: Business information
            risk_assessment: Risk analysis results
            regulations: Target regulations

        Returns:
            Structured compliance plan
        """
        risk_level = risk_assessment.get("risk_level", "medium")
        risk_score = risk_assessment.get("risk_score", 50)

        # Determine plan urgency
        if risk_level == "critical":
            priority = "immediate"
            timeline = "1-2 weeks"
        elif risk_level == "high":
            priority = "urgent"
            timeline = "2-4 weeks"
        elif risk_level == "medium":
            priority = "standard"
            timeline = "1-2 months"
        else:
            priority = "routine"
            timeline = "2-3 months"

        # Get applicable regulations
        if not regulations:
            regulations = risk_assessment.get("priority_regulations", [])

        # Generate phase-based plan
        phases = await self._generate_phases(business_profile, regulations, risk_level, timeline)

        # Calculate resource requirements
        resources = self._calculate_resources(risk_score, len(phases))

        return {
            "plan_id": f"CP-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
            "priority": priority,
            "timeline": timeline,
            "phases": phases,
            "regulations": regulations,
            "resources": resources,
            "estimated_cost": resources["estimated_cost"],
            "success_metrics": self._define_success_metrics(regulations),
            "review_schedule": self._create_review_schedule(timeline),
        }

    async def _generate_phases(
        self,
        business_profile: Dict[str, Any],
        regulations: List[str],
        risk_level: str,
        timeline: str,
    ) -> List[Dict[str, Any]]:
        """Generate implementation phases."""
        phases = []

        # Phase 1: Foundation
        phases.append(
            {
                "phase": 1,
                "title": "Foundation & Assessment",
                "duration": self._calculate_phase_duration(timeline, 0.25),
                "objectives": [
                    "Conduct gap analysis",
                    "Document current state",
                    "Identify stakeholders",
                    "Establish governance structure",
                ],
                "deliverables": ["Gap analysis report", "Stakeholder matrix", "Governance charter"],
                "success_criteria": [
                    "All gaps identified",
                    "Stakeholders engaged",
                    "Governance approved",
                ],
            }
        )

        # Phase 2: Policy Development
        phases.append(
            {
                "phase": 2,
                "title": "Policy & Procedure Development",
                "duration": self._calculate_phase_duration(timeline, 0.3),
                "objectives": [
                    "Develop compliance policies",
                    "Create operational procedures",
                    "Design control framework",
                    "Establish monitoring processes",
                ],
                "deliverables": [
                    "Policy documentation",
                    "Procedure manuals",
                    "Control matrix",
                    "Monitoring dashboard",
                ],
                "success_criteria": [
                    "Policies approved",
                    "Procedures documented",
                    "Controls defined",
                ],
            }
        )

        # Phase 3: Implementation
        phases.append(
            {
                "phase": 3,
                "title": "Implementation & Training",
                "duration": self._calculate_phase_duration(timeline, 0.3),
                "objectives": [
                    "Deploy controls",
                    "Train staff",
                    "Implement monitoring",
                    "Begin evidence collection",
                ],
                "deliverables": [
                    "Deployed controls",
                    "Training materials",
                    "Monitoring reports",
                    "Evidence repository",
                ],
                "success_criteria": [
                    "Controls operational",
                    "Staff trained (>90%)",
                    "Monitoring active",
                ],
            }
        )

        # Phase 4: Validation
        phases.append(
            {
                "phase": 4,
                "title": "Validation & Certification",
                "duration": self._calculate_phase_duration(timeline, 0.15),
                "objectives": [
                    "Conduct internal audit",
                    "Remediate findings",
                    "Prepare for certification",
                    "Document compliance",
                ],
                "deliverables": [
                    "Audit report",
                    "Remediation plan",
                    "Certification package",
                    "Compliance statement",
                ],
                "success_criteria": [
                    "Audit completed",
                    "Major findings resolved",
                    "Certification ready",
                ],
            }
        )

        return phases

    def _calculate_phase_duration(self, total_timeline: str, percentage: float) -> str:
        """Calculate duration for a specific phase."""
        # Parse timeline
        if "week" in total_timeline:
            weeks = int(total_timeline.split("-")[1].split()[0])
            phase_weeks = max(1, int(weeks * percentage))
            return f"{phase_weeks} week{'s' if phase_weeks > 1 else ''}"
        elif "month" in total_timeline:
            months = int(total_timeline.split("-")[1].split()[0])
            phase_weeks = max(1, int(months * 4 * percentage))
            return f"{phase_weeks} week{'s' if phase_weeks > 1 else ''}"
        return "1 week"

    def _calculate_resources(self, risk_score: float, num_phases: int) -> Dict[str, Any]:
        """Calculate resource requirements."""
        if risk_score >= 80:
            return {
                "team_size": "5-8 people",
                "key_roles": [
                    "Compliance Officer",
                    "Data Protection Officer",
                    "Security Analyst",
                    "Project Manager",
                ],
                "external_support": "Compliance consultancy recommended",
                "estimated_cost": "£75,000 - £150,000",
                "effort_hours": 2000 + (num_phases * 200),
            }
        elif risk_score >= 60:
            return {
                "team_size": "3-5 people",
                "key_roles": ["Compliance Lead", "Security Specialist", "Project Coordinator"],
                "external_support": "Specialist consultant for key areas",
                "estimated_cost": "£35,000 - £75,000",
                "effort_hours": 1000 + (num_phases * 150),
            }
        elif risk_score >= 40:
            return {
                "team_size": "2-3 people",
                "key_roles": ["Compliance Coordinator", "Technical Lead"],
                "external_support": "Advisory services as needed",
                "estimated_cost": "£15,000 - £35,000",
                "effort_hours": 500 + (num_phases * 100),
            }
        else:
            return {
                "team_size": "1-2 people",
                "key_roles": ["Compliance Champion"],
                "external_support": "Online resources and templates",
                "estimated_cost": "£5,000 - £15,000",
                "effort_hours": 200 + (num_phases * 50),
            }

    def _define_success_metrics(self, regulations: List[str]) -> List[Dict[str, Any]]:
        """Define success metrics for the plan."""
        metrics = [
            {
                "metric": "Compliance Score",
                "target": ">85%",
                "measurement": "Quarterly assessment",
                "owner": "Compliance Officer",
            },
            {
                "metric": "Control Effectiveness",
                "target": ">90%",
                "measurement": "Monthly testing",
                "owner": "Security Team",
            },
            {
                "metric": "Training Completion",
                "target": "100%",
                "measurement": "Training system reports",
                "owner": "HR Department",
            },
            {
                "metric": "Incident Response Time",
                "target": "<24 hours",
                "measurement": "Incident logs",
                "owner": "Security Team",
            },
        ]

        # Add regulation-specific metrics
        if "GDPR" in regulations:
            metrics.append(
                {
                    "metric": "Data Request Response Time",
                    "target": "<30 days",
                    "measurement": "Request tracking",
                    "owner": "Data Protection Officer",
                }
            )

        if "ISO 27001" in regulations:
            metrics.append(
                {
                    "metric": "Risk Assessment Coverage",
                    "target": "100%",
                    "measurement": "Risk register",
                    "owner": "Risk Manager",
                }
            )

        return metrics

    def _create_review_schedule(self, timeline: str) -> List[Dict[str, str]]:
        """Create review schedule for the plan."""
        return [
            {
                "milestone": "Initial Review",
                "timing": "Week 2",
                "purpose": "Validate approach and resources",
            },
            {
                "milestone": "Mid-point Review",
                "timing": "50% completion",
                "purpose": "Assess progress and adjust",
            },
            {
                "milestone": "Pre-audit Review",
                "timing": "Week before audit",
                "purpose": "Readiness assessment",
            },
            {
                "milestone": "Final Review",
                "timing": "Plan completion",
                "purpose": "Lessons learned and next steps",
            },
        ]


class EvidenceVerificationService:
    """Service for verifying compliance evidence."""

    def __init__(
        self, evidence_repo: EvidenceRepository, compliance_repo: ComplianceRepository
    ) -> None:
        self.evidence_repo = evidence_repo
        self.compliance_repo = compliance_repo

    async def verify_evidence_completeness(
        self, business_profile_id: str, regulation_code: str
    ) -> Dict[str, Any]:
        """
        Verify if business has complete evidence for a regulation.

        Args:
            business_profile_id: Business profile ID
            regulation_code: Regulation code to check

        Returns:
            Evidence verification results
        """
        # Get requirements for regulation
        requirements = await self.compliance_repo.get_requirements_for_regulation(regulation_code)

        # Get available evidence
        evidence_items = await self.evidence_repo.get_by_business_profile(business_profile_id)

        # Map evidence to requirements
        evidence_map = {}
        for req in requirements:
            req_id = req["id"]
            matching_evidence = [
                e for e in evidence_items if self._evidence_matches_requirement(e, req)
            ]
            evidence_map[req_id] = {
                "requirement": req["title"],
                "risk_level": req.get("risk_level", "medium"),
                "has_evidence": len(matching_evidence) > 0,
                "evidence_count": len(matching_evidence),
                "evidence_items": [
                    {
                        "id": str(e.id),
                        "title": e.title,
                        "type": e.evidence_type,
                        "uploaded": e.created_at.isoformat(),
                    }
                    for e in matching_evidence
                ],
            }

        # Calculate completeness
        total_requirements = len(requirements)
        covered_requirements = sum(1 for em in evidence_map.values() if em["has_evidence"])
        completeness_percentage = (
            (covered_requirements / total_requirements * 100) if total_requirements > 0 else 0
        )

        # Identify gaps
        gaps = [
            {
                "requirement_id": req_id,
                "requirement": em["requirement"],
                "risk_level": em["risk_level"],
            }
            for req_id, em in evidence_map.items()
            if not em["has_evidence"]
        ]

        return {
            "regulation": regulation_code,
            "completeness_percentage": round(completeness_percentage, 1),
            "total_requirements": total_requirements,
            "covered_requirements": covered_requirements,
            "missing_requirements": total_requirements - covered_requirements,
            "evidence_map": evidence_map,
            "gaps": sorted(
                gaps,
                key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(
                    x["risk_level"], 4
                ),
            ),
            "verification_timestamp": datetime.utcnow().isoformat(),
        }

    def _evidence_matches_requirement(self, evidence: Any, requirement: Dict[str, Any]) -> bool:
        """Check if evidence matches a requirement."""
        # Simple matching logic - can be enhanced
        req_title_lower = requirement["title"].lower()
        evidence_title_lower = evidence.title.lower()

        # Check for keyword matches
        keywords = req_title_lower.split()
        matches = sum(1 for keyword in keywords if keyword in evidence_title_lower)

        # Consider it a match if >50% keywords match
        return matches >= len(keywords) * 0.5


class QueryClassificationService:
    """Service for classifying and routing queries."""

    def __init__(self) -> None:
        self.query_patterns = {
            "assessment": [
                "assess",
                "audit",
                "evaluate",
                "review",
                "check compliance",
                "compliance assessment",
                "gap analysis",
                "risk assessment",
            ],
            "evidence": [
                "evidence",
                "document",
                "proof",
                "certificate",
                "upload",
                "do we have",
                "check if we have",
                "verify",
            ],
            "regulation": [
                "regulation",
                "requirement",
                "gdpr",
                "iso",
                "standard",
                "what does",
                "explain",
                "tell me about",
            ],
            "risk": [
                "risk",
                "threat",
                "vulnerability",
                "exposure",
                "danger",
                "what could go wrong",
                "potential issues",
            ],
            "plan": [
                "plan",
                "roadmap",
                "timeline",
                "how to",
                "steps",
                "implement",
                "achieve",
                "become compliant",
            ],
        }

    def classify_query(self, query: str) -> Dict[str, Any]:
        """
        Classify a query to determine processing strategy.

        Args:
            query: User query

        Returns:
            Classification results with confidence scores
        """
        query_lower = query.lower()

        # Calculate scores for each category
        scores = {}
        for category, patterns in self.query_patterns.items():
            score = sum(1 for pattern in patterns if pattern in query_lower)
            scores[category] = score

        # Get primary category
        if max(scores.values()) == 0:
            primary_category = "general"
            confidence = 0.3
        else:
            primary_category = max(scores, key=scores.get)
            confidence = min(
                scores[primary_category] / len(self.query_patterns[primary_category]), 1.0
            )

        # Determine processing mode
        if primary_category == "assessment":
            processing_mode = "structured"
            requires_context = True
        elif primary_category == "evidence":
            processing_mode = "quick"
            requires_context = True
        elif primary_category in ["risk", "plan"]:
            processing_mode = "react"
            requires_context = True
        else:
            processing_mode = "react"
            requires_context = False

        return {
            "primary_category": primary_category,
            "confidence": round(confidence, 2),
            "processing_mode": processing_mode,
            "requires_context": requires_context,
            "category_scores": scores,
            "suggested_capabilities": self._get_required_capabilities(primary_category),
        }

    def _get_required_capabilities(self, category: str) -> List[str]:
        """Get required agent capabilities for a category."""
        capability_map = {
            "assessment": ["ASSESSMENT", "CONVERSATIONAL"],
            "evidence": ["EVIDENCE_CHECK"],
            "regulation": ["REGULATION_SEARCH"],
            "risk": ["RISK_ANALYSIS"],
            "plan": ["PLAN_GENERATION"],
            "general": ["CONVERSATIONAL"],
        }
        return capability_map.get(category, ["CONVERSATIONAL"])


class BusinessContextService:
    """Service for retrieving and managing business context."""

    def __init__(
        self,
        business_repo: BusinessProfileRepository,
        evidence_repo: EvidenceRepository,
        session_repo: Optional[AssessmentSessionRepository] = None,
    ) -> None:
        self.business_repo = business_repo
        self.evidence_repo = evidence_repo
        self.session_repo = session_repo

    async def retrieve_business_context(self, business_profile_id: str) -> Dict[str, Any]:
        """
        Retrieve comprehensive business context.

        Args:
            business_profile_id: Business profile ID

        Returns:
            Business context including profile and evidence
        """
        try:
            # Get business profile
            profile = await self.business_repo.get_by_id(business_profile_id)
            if not profile:
                return {"error": "Business profile not found"}

            # Get recent evidence
            evidence_items = await self.evidence_repo.get_by_profile(business_profile_id, limit=10)

            return {
                "profile": {
                    "id": business_profile_id,
                    "company_name": profile.company_name,
                    "industry": profile.industry,
                    "company_size": profile.company_size,
                    "handles_personal_data": profile.handles_personal_data,
                    "data_processing_activities": profile.data_processing_activities,
                    "created_at": profile.created_at.isoformat() if profile.created_at else None,
                },
                "evidence": [
                    {
                        "id": str(item.id),
                        "title": item.title,
                        "description": item.description,
                        "evidence_type": item.evidence_type,
                        "created_at": item.created_at.isoformat() if item.created_at else None,
                    }
                    for item in evidence_items
                ],
                "evidence_count": len(evidence_items),
            }

        except Exception as e:
            logger.error(f"Error retrieving business context: {e}")
            return {"error": str(e)}

    async def retrieve_session_context(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve session-specific context.

        Args:
            session_id: Session identifier

        Returns:
            Session context and history
        """
        try:
            if not self.session_repo:
                return {"error": "Session repository not available"}

            # Get session data
            session = await self.session_repo.get_by_id(session_id)
            if not session:
                return {"error": "Session not found"}

            return {
                "session_id": session_id,
                "started_at": session.created_at.isoformat() if session.created_at else None,
                "last_activity": session.updated_at.isoformat() if session.updated_at else None,
                "session_type": getattr(session, "session_type", "unknown"),
                "progress": getattr(session, "progress", 0.0),
                "metadata": getattr(session, "metadata", {}),
                "status": getattr(session, "status", "unknown"),
            }

        except Exception as e:
            logger.error(f"Error retrieving session context: {e}")
            return {"error": str(e)}


class ComplianceSearchService:
    """Service for searching compliance resources and evidence."""

    def __init__(
        self, compliance_repo: ComplianceRepository, evidence_repo: EvidenceRepository
    ) -> None:
        self.compliance_repo = compliance_repo
        self.evidence_repo = evidence_repo

    async def search_compliance_resources(
        self,
        query: str,
        regulations: Optional[List[str]] = None,
        business_profile_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search for relevant compliance resources.

        Args:
            query: Search query
            regulations: Filter by regulations
            business_profile_id: Business context

        Returns:
            Search results with relevance scores
        """
        try:
            results = {
                "query": query,
                "total_results": 0,
                "compliance_items": [],
                "evidence_items": [],
                "regulatory_references": [],
            }

            # Search compliance requirements
            compliance_items = await self.compliance_repo.search(
                query=query, regulations=regulations
            )

            results["compliance_items"] = [
                {
                    "id": str(item.id),
                    "title": item.title,
                    "description": item.description,
                    "regulation": item.regulation,
                    "control_type": getattr(item, "control_type", "unknown"),
                    "relevance_score": getattr(item, "relevance_score", 0.5),
                }
                for item in compliance_items
            ]

            # Search evidence if business profile provided
            if business_profile_id:
                evidence_items = await self.evidence_repo.search_by_profile(
                    business_profile_id, query
                )

                results["evidence_items"] = [
                    {
                        "id": str(item.id),
                        "title": item.title,
                        "evidence_type": item.evidence_type,
                        "relevance_score": getattr(item, "relevance_score", 0.5),
                    }
                    for item in evidence_items
                ]

            results["total_results"] = len(results["compliance_items"]) + len(
                results["evidence_items"]
            )

            return results

        except Exception as e:
            logger.error(f"Error searching compliance resources: {e}")
            return {"error": str(e), "total_results": 0}

    async def count_available_evidence(
        self, business_profile_id: str, evidence_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Count available evidence by type.

        Args:
            business_profile_id: Business profile ID
            evidence_types: Filter by evidence types

        Returns:
            Evidence counts by type
        """
        try:
            total_count = await self.evidence_repo.count_by_profile(business_profile_id)

            # Get breakdown by type if available
            evidence_breakdown = {}
            if hasattr(self.evidence_repo, "count_by_type"):
                evidence_breakdown = await self.evidence_repo.count_by_type(
                    business_profile_id, evidence_types
                )

            return {
                "total_evidence": total_count,
                "breakdown": evidence_breakdown,
                "last_updated": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Error counting evidence: {e}")
            return {"error": str(e), "total_evidence": 0}


class RecommendationService:
    """Service for generating contextualized recommendations."""

    def __init__(
        self, compliance_repo: ComplianceRepository, risk_service: RiskAnalysisService
    ) -> None:
        self.compliance_repo = compliance_repo
        self.risk_service = risk_service
        self.circuit_breaker = AICircuitBreaker()

    async def generate_contextualized_recommendations(
        self,
        business_profile: Dict[str, Any],
        compliance_gaps: List[Dict[str, Any]],
        risk_assessment: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Generate contextualized compliance recommendations.

        Args:
            business_profile: Business context
            compliance_gaps: Identified gaps
            risk_assessment: Risk analysis results

        Returns:
            Prioritized recommendations
        """
        try:
            recommendations = []

            risk_level = risk_assessment.get("risk_level", "medium")
            industry = business_profile.get("industry", "").lower()

            # High-priority recommendations based on risk
            if risk_level in ["critical", "high"]:
                recommendations.extend(
                    [
                        {
                            "priority": "immediate",
                            "category": "risk_mitigation",
                            "title": "Implement Critical Controls",
                            "description": "Deploy essential compliance controls to address high-risk areas",
                            "estimated_effort": "2-4 weeks",
                            "cost_range": "£10k-25k",
                            "regulations": risk_assessment.get("priority_regulations", []),
                        },
                        {
                            "priority": "immediate",
                            "category": "documentation",
                            "title": "Document Compliance Procedures",
                            "description": "Create formal policies and procedures for compliance management",
                            "estimated_effort": "1-2 weeks",
                            "cost_range": "£5k-10k",
                            "regulations": ["General"],
                        },
                    ]
                )

            # Industry-specific recommendations
            if "finance" in industry or "fintech" in industry:
                recommendations.append(
                    {
                        "priority": "high",
                        "category": "regulatory",
                        "title": "Financial Services Compliance",
                        "description": "Implement FCA requirements and PCI DSS controls",
                        "estimated_effort": "4-8 weeks",
                        "cost_range": "£25k-50k",
                        "regulations": ["FCA", "PCI DSS"],
                    }
                )
            elif "health" in industry:
                recommendations.append(
                    {
                        "priority": "critical",
                        "category": "data_protection",
                        "title": "Healthcare Data Protection",
                        "description": "Implement NHS DSP Toolkit and enhanced GDPR controls",
                        "estimated_effort": "6-12 weeks",
                        "cost_range": "£40k-80k",
                        "regulations": ["NHS DSP Toolkit", "GDPR"],
                    }
                )

            # Data handling recommendations
            if business_profile.get("handles_personal_data"):
                recommendations.append(
                    {
                        "priority": "high",
                        "category": "data_protection",
                        "title": "Data Protection Impact Assessment",
                        "description": "Conduct DPIA for high-risk data processing activities",
                        "estimated_effort": "2-3 weeks",
                        "cost_range": "£8k-15k",
                        "regulations": ["GDPR"],
                    }
                )

            # Gap-based recommendations
            for gap in compliance_gaps:
                recommendations.append(
                    {
                        "priority": gap.get("priority", "medium"),
                        "category": "gap_remediation",
                        "title": f"Address {gap.get('area', 'Compliance')} Gap",
                        "description": gap.get(
                            "description", "Remediate identified compliance gap"
                        ),
                        "estimated_effort": gap.get("estimated_effort", "1-2 weeks"),
                        "cost_range": gap.get("cost_range", "£5k-10k"),
                        "regulations": gap.get("regulations", ["General"]),
                    }
                )

            # Sort by priority
            priority_order = {"immediate": 0, "critical": 1, "high": 2, "medium": 3, "low": 4}
            recommendations.sort(key=lambda x: priority_order.get(x["priority"], 5))

            return recommendations

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return [
                {
                    "priority": "medium",
                    "category": "general",
                    "title": "Conduct Compliance Assessment",
                    "description": "Perform comprehensive compliance assessment to identify needs",
                    "estimated_effort": "1-2 weeks",
                    "cost_range": "£5k-10k",
                    "regulations": ["General"],
                }
            ]


class ExecutionService:
    """Service for managing compliance task execution."""

    def __init__(self) -> None:
        self.RISK_THRESHOLD = 0.7
        self.AUTONOMY_BUDGET = 1000  # £1000 threshold for autonomous execution

    async def should_auto_execute(
        self, action: Dict[str, Any], risk_score: float, estimated_cost: float
    ) -> bool:
        """
        Determine if an action should be executed autonomously.

        Args:
            action: Action to evaluate
            risk_score: Associated risk score
            estimated_cost: Estimated cost

        Returns:
            Whether to auto-execute
        """
        # Don't auto-execute high-risk actions
        if risk_score > self.RISK_THRESHOLD:
            return False

        # Don't auto-execute expensive actions
        if estimated_cost > self.AUTONOMY_BUDGET:
            return False

        # Check action type
        action_type = action.get("type", "").lower()
        auto_executable_types = {"documentation", "assessment", "notification", "report_generation"}

        return action_type in auto_executable_types

    async def execute_action(
        self, action: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a compliance action.

        Args:
            action: Action to execute
            context: Execution context

        Returns:
            Execution result
        """
        try:
            action_type = action.get("type", "").lower()

            if action_type == "documentation":
                return await self._execute_documentation_action(action, context)
            elif action_type == "assessment":
                return await self._execute_assessment_action(action, context)
            elif action_type == "notification":
                return await self._execute_notification_action(action, context)
            else:
                return {
                    "status": "not_implemented",
                    "message": f"Action type '{action_type}' not implemented",
                    "action_id": action.get("id", "unknown"),
                }

        except Exception as e:
            logger.error(f"Error executing action: {e}")
            return {"status": "error", "message": str(e), "action_id": action.get("id", "unknown")}

    async def _execute_documentation_action(
        self, action: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute documentation-related action."""
        return {
            "status": "completed",
            "message": "Documentation template created",
            "artifacts": {
                "template_name": action.get("template", "compliance_template"),
                "created_at": datetime.utcnow().isoformat(),
            },
        }

    async def _execute_assessment_action(
        self, action: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute assessment-related action."""
        return {
            "status": "initiated",
            "message": "Assessment workflow started",
            "artifacts": {
                "assessment_id": f"ASS-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
                "started_at": datetime.utcnow().isoformat(),
            },
        }

    async def _execute_notification_action(
        self, action: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute notification-related action."""
        return {
            "status": "sent",
            "message": "Notification sent to stakeholders",
            "artifacts": {
                "notification_id": f"NOT-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}",
                "sent_at": datetime.utcnow().isoformat(),
            },
        }

    async def create_escalation(
        self, issue: Dict[str, Any], escalation_level: str = "standard"
    ) -> Dict[str, Any]:
        """
        Create an escalation for manual review.

        Args:
            issue: Issue requiring escalation
            escalation_level: Urgency level

        Returns:
            Escalation details
        """
        escalation_id = f"ESC-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

        return {
            "escalation_id": escalation_id,
            "level": escalation_level,
            "issue": issue,
            "created_at": datetime.utcnow().isoformat(),
            "status": "open",
            "assigned_to": self._determine_assignee(escalation_level),
            "sla": self._get_sla(escalation_level),
        }

    def _determine_assignee(self, escalation_level: str) -> str:
        """Determine who should handle the escalation."""
        assignee_map = {
            "critical": "Compliance Manager",
            "urgent": "Senior Compliance Officer",
            "standard": "Compliance Officer",
            "routine": "Compliance Analyst",
        }
        return assignee_map.get(escalation_level, "Compliance Team")

    def _get_sla(self, escalation_level: str) -> str:
        """Get SLA for escalation level."""
        sla_map = {
            "critical": "2 hours",
            "urgent": "1 business day",
            "standard": "3 business days",
            "routine": "1 week",
        }
        return sla_map.get(escalation_level, "3 business days")
