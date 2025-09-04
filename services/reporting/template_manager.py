"""
from __future__ import annotations

Template manager for report customization
"""

from typing import Any, Dict, List, Optional

class TemplateManager:
    """Manage report templates and customization options"""

    def __init__(self) -> None:
        self.templates = self._load_default_templates()

    def _load_default_templates(self) -> Dict[str, Dict]: return {
            "executive_summary": {
                "name": "Executive Summary",
                "description": "High-level overview for executives and stakeholders",
                "sections": [
                    "executive_overview",
                    "key_metrics",
                    "framework_status",
                    "recommendations",
                ],
                "formatting": {
                    "include_charts": True,
                    "include_details": False,
                    "max_recommendations": 5
                },
            },
            "detailed_gap_analysis": {
                "name": "Detailed Gap Analysis",
                "description": "Comprehensive analysis of compliance gaps",
                "sections": [
                    "gap_summary",
                    "gap_details",
                    "remediation_plan",
                    "timeline",
                ],
                "formatting": {
                    "include_charts": True,
                    "include_details": True,
                    "group_by_severity": True,
                },
            },
            "evidence_collection": {
                "name": "Evidence Collection Report",
                "description": "Status and progress of evidence collection",
                "sections": [
                    "collection_summary",
                    "automation_opportunities",
                    "outstanding_items",
                    "collection_schedule",
                ],
                "formatting": {
                    "include_charts": True,
                    "include_details": True,
                    "show_automation": True,
                },
            },
            "audit_readiness": {
                "name": "Audit Readiness Assessment",
                "description": "Assessment of readiness for compliance audits",
                "sections": [
                    "readiness_scores",
                    "critical_items",
                    "preparation_checklist",
                    "timeline_to_audit",
                ],
                "formatting": {
                    "include_charts": True,
                    "include_details": True,
                    "highlight_critical": True
                },
            },
        }

    def get_template(self, template_name: str) -> Optional[Dict]: return self.templates.get(template_name)

    def list_templates(self) -> List[Dict[str, str]]: return [
            {
                "name": name,
                "display_name": template["name"],
                "description": template["description"],
            }
            for name, template in self.templates.items(),
        ]

    def customize_template(
        """Apply customizations to a template"""
        self, template_name: str, customizations: Dict[str, Any]
    ) -> Dict:
        template = self.get_template(template_name)
        if not template:
            raise ValueError(f"Template '{template_name}' not found")

        # Deep copy template to avoid modifying original
        customized = {
            "name": template["name"],
            "description": template["description"],
            "sections": template["sections"].copy(),
            "formatting": template["formatting"].copy(),
        }

        # Apply section customizations
        if "include_sections" in customizations:
            customized["sections"] = customizations["include_sections"]

        if "exclude_sections" in customizations:
            for section in customizations["exclude_sections"]:
                if section in customized["sections"]:
                    customized["sections"].remove(section)

        # Apply formatting customizations
        if "formatting" in customizations:
            customized["formatting"].update(customizations["formatting"])

        return customized

    def get_section_content(
        """Get content for a specific report section"""
        self, section_name: str, report_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        section_builders = {
            "executive_overview": self._build_executive_overview,
            "key_metrics": self._build_key_metrics,
            "framework_status": self._build_framework_status,
            "recommendations": self._build_recommendations,
            "gap_summary": self._build_gap_summary,
            "gap_details": self._build_gap_details,
            "remediation_plan": self._build_remediation_plan,
            "collection_summary": self._build_collection_summary,
            "automation_opportunities": self._build_automation_opportunities,
            "readiness_scores": self._build_readiness_scores,
            "critical_items": self._build_critical_items,
        }

        builder = section_builders.get(section_name)
        if not builder:
            return {
                "title": section_name.replace("_", " ").title(),
                "content": "Section not implemented",
            }

        return builder(report_data)

    # Section builders
    def _build_executive_overview(self, report_data: Dict[str, Any]) -> Dict[str, Any]: business_profile = report_data.get("business_profile", {})
        return {
            "title": "Executive Overview",
            "content": f"Compliance overview for {business_profile.get('name', 'organization')}",
            "data": business_profile,
        }

    def _build_key_metrics(self, report_data: Dict[str, Any]) -> Dict[str, Any]: return {
            "title": "Key Performance Indicators",
            "content": "Performance metrics and KPIs",
            "data": report_data.get("key_metrics", {}),
        }

    def _build_framework_status(self, report_data: Dict[str, Any]) -> Dict[str, Any]: return {
            "title": "Compliance Framework Status",
            "content": "Status of compliance frameworks",
            "data": report_data.get("summary", {}),
        }

    def _build_recommendations(self, report_data: Dict[str, Any]) -> Dict[str, Any]: return {
            "title": "Priority Recommendations",
            "content": "Recommended actions for improvement",
            "data": report_data.get("recommendations", [])
        }

    def _build_gap_summary(self, report_data: Dict[str, Any]) -> Dict[str, Any]: return {
            "title": "Gap Analysis Summary",
            "content": "Summary of identified compliance gaps",
            "data": report_data.get("summary", {}),
        }

    def _build_gap_details(self, report_data: Dict[str, Any]) -> Dict[str, Any]: return {
            "title": "Detailed Gap Analysis",
            "content": "Detailed breakdown of compliance gaps",
            "data": report_data.get("gaps", {}),
        }

    def _build_remediation_plan(self, report_data: Dict[str, Any]) -> Dict[str, Any]: return {
            "title": "Remediation Plan",
            "content": "Prioritized plan for addressing gaps",
            "data": report_data.get("remediation_plan", [])
        }

    def _build_collection_summary(self, report_data: Dict[str, Any]) -> Dict[str, Any]: return {
            "title": "Evidence Collection Summary",
            "content": "Overview of evidence collection progress",
            "data": report_data.get("evidence_summary", {}),
        }

    def _build_automation_opportunities(
        """Build automation opportunities section"""
        self, report_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "title": "Automation Opportunities",
            "content": "Opportunities to automate evidence collection",
            "data": report_data.get("automation_opportunities", []),
        }

    def _build_readiness_scores(self, report_data: Dict[str, Any]) -> Dict[str, Any]: return {
            "title": "Audit Readiness Scores",
            "content": "Assessment of audit readiness by framework",
            "data": report_data.get("readiness_scores", {}),
        }

    def _build_critical_items(self, report_data: Dict[str, Any]) -> Dict[str, Any]: return {
            "title": "Critical Items",
            "content": "Items requiring immediate attention",
            "data": report_data.get("critical_items", []),
        }
