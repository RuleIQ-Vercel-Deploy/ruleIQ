#!/usr/bin/env python3
"""
Extract ISO framework obligations and controls.
This covers the main ISO standards relevant to enterprise compliance.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import hashlib

# ISO Standards with their controls and requirements
ISO_STANDARDS = {
    "ISO 27001:2022": {
        "title": "Information Security Management System",
        "version": "2022",
        "clauses": {
            "4": {
                "title": "Context of the organization",
                "controls": [
                    {
                        "id": "4.1",
                        "title": "Understanding the organization and its context",
                        "description": "Determine external and internal issues relevant to ISMS",
                        "type": "mandatory",
                        "category": "context",
                    },
                    {
                        "id": "4.2",
                        "title": "Understanding needs and expectations of interested parties",
                        "description": "Determine interested parties and their requirements",
                        "type": "mandatory",
                        "category": "context",
                    },
                    {
                        "id": "4.3",
                        "title": "Determining the scope of the ISMS",
                        "description": "Define boundaries and applicability of ISMS",
                        "type": "mandatory",
                        "category": "context",
                    },
                    {
                        "id": "4.4",
                        "title": "Information security management system",
                        "description": "Establish, implement, maintain and continually improve ISMS",
                        "type": "mandatory",
                        "category": "context",
                    },
                ],
            },
            "5": {
                "title": "Leadership",
                "controls": [
                    {
                        "id": "5.1",
                        "title": "Leadership and commitment",
                        "description": "Top management must demonstrate leadership and commitment",
                        "type": "mandatory",
                        "category": "leadership",
                    },
                    {
                        "id": "5.2",
                        "title": "Policy",
                        "description": "Establish information security policy",
                        "type": "mandatory",
                        "category": "leadership",
                    },
                    {
                        "id": "5.3",
                        "title": "Organizational roles, responsibilities and authorities",
                        "description": "Assign and communicate responsibilities and authorities",
                        "type": "mandatory",
                        "category": "leadership",
                    },
                ],
            },
            "6": {
                "title": "Planning",
                "controls": [
                    {
                        "id": "6.1.1",
                        "title": "Risk assessment",
                        "description": "Establish risk assessment process",
                        "type": "mandatory",
                        "category": "planning",
                    },
                    {
                        "id": "6.1.2",
                        "title": "Risk treatment",
                        "description": "Define and apply risk treatment process",
                        "type": "mandatory",
                        "category": "planning",
                    },
                    {
                        "id": "6.2",
                        "title": "Information security objectives",
                        "description": "Establish security objectives at relevant functions",
                        "type": "mandatory",
                        "category": "planning",
                    },
                    {
                        "id": "6.3",
                        "title": "Planning of changes",
                        "description": "Plan changes to ISMS",
                        "type": "mandatory",
                        "category": "planning",
                    },
                ],
            },
            "7": {
                "title": "Support",
                "controls": [
                    {
                        "id": "7.1",
                        "title": "Resources",
                        "description": "Determine and provide necessary resources",
                        "type": "mandatory",
                        "category": "support",
                    },
                    {
                        "id": "7.2",
                        "title": "Competence",
                        "description": "Ensure competence of persons doing work",
                        "type": "mandatory",
                        "category": "support",
                    },
                    {
                        "id": "7.3",
                        "title": "Awareness",
                        "description": "Ensure awareness of information security policy",
                        "type": "mandatory",
                        "category": "support",
                    },
                    {
                        "id": "7.4",
                        "title": "Communication",
                        "description": "Determine internal and external communications",
                        "type": "mandatory",
                        "category": "support",
                    },
                    {
                        "id": "7.5",
                        "title": "Documented information",
                        "description": "Control documented information",
                        "type": "mandatory",
                        "category": "support",
                    },
                ],
            },
            "8": {
                "title": "Operation",
                "controls": [
                    {
                        "id": "8.1",
                        "title": "Operational planning and control",
                        "description": "Plan, implement and control processes",
                        "type": "mandatory",
                        "category": "operation",
                    },
                    {
                        "id": "8.2",
                        "title": "Information security risk assessment",
                        "description": "Perform risk assessments at planned intervals",
                        "type": "mandatory",
                        "category": "operation",
                    },
                    {
                        "id": "8.3",
                        "title": "Information security risk treatment",
                        "description": "Implement risk treatment plan",
                        "type": "mandatory",
                        "category": "operation",
                    },
                ],
            },
            "9": {
                "title": "Performance evaluation",
                "controls": [
                    {
                        "id": "9.1",
                        "title": "Monitoring, measurement, analysis and evaluation",
                        "description": "Evaluate information security performance",
                        "type": "mandatory",
                        "category": "evaluation",
                    },
                    {
                        "id": "9.2",
                        "title": "Internal audit",
                        "description": "Conduct internal audits at planned intervals",
                        "type": "mandatory",
                        "category": "evaluation",
                    },
                    {
                        "id": "9.3",
                        "title": "Management review",
                        "description": "Review ISMS at planned intervals",
                        "type": "mandatory",
                        "category": "evaluation",
                    },
                ],
            },
            "10": {
                "title": "Improvement",
                "controls": [
                    {
                        "id": "10.1",
                        "title": "Continual improvement",
                        "description": "Continually improve ISMS suitability and effectiveness",
                        "type": "mandatory",
                        "category": "improvement",
                    },
                    {
                        "id": "10.2",
                        "title": "Nonconformity and corrective action",
                        "description": "React to nonconformity and take corrective action",
                        "type": "mandatory",
                        "category": "improvement",
                    },
                ],
            },
            "A": {
                "title": "Annex A Controls",
                "controls": [
                    # Information Security Controls (93 controls from Annex A)
                    {
                        "id": "A.5.1",
                        "title": "Information security policy",
                        "description": "Policies for information security",
                        "type": "control",
                        "category": "organizational",
                    },
                    {
                        "id": "A.5.2",
                        "title": "Information security roles and responsibilities",
                        "description": "All information security responsibilities shall be defined",
                        "type": "control",
                        "category": "organizational",
                    },
                    {
                        "id": "A.5.3",
                        "title": "Segregation of duties",
                        "description": "Conflicting duties shall be segregated",
                        "type": "control",
                        "category": "organizational",
                    },
                    {
                        "id": "A.5.4",
                        "title": "Management responsibilities",
                        "description": "Management shall require compliance with security policies",
                        "type": "control",
                        "category": "organizational",
                    },
                    {
                        "id": "A.6.1",
                        "title": "Screening",
                        "description": "Background verification checks on candidates",
                        "type": "control",
                        "category": "people",
                    },
                    {
                        "id": "A.6.2",
                        "title": "Terms and conditions of employment",
                        "description": "Employment agreements shall include security responsibilities",
                        "type": "control",
                        "category": "people",
                    },
                    {
                        "id": "A.6.3",
                        "title": "Information security awareness",
                        "description": "Personnel shall receive security awareness training",
                        "type": "control",
                        "category": "people",
                    },
                    {
                        "id": "A.7.1",
                        "title": "Physical security perimeter",
                        "description": "Security perimeters shall protect areas with information",
                        "type": "control",
                        "category": "physical",
                    },
                    {
                        "id": "A.7.2",
                        "title": "Physical entry",
                        "description": "Secure areas shall be protected by appropriate entry controls",
                        "type": "control",
                        "category": "physical",
                    },
                    {
                        "id": "A.8.1",
                        "title": "User endpoint devices",
                        "description": "Information on endpoint devices shall be protected",
                        "type": "control",
                        "category": "technological",
                    },
                    {
                        "id": "A.8.2",
                        "title": "Privileged access rights",
                        "description": "Allocation of privileged access rights shall be restricted",
                        "type": "control",
                        "category": "technological",
                    },
                    {
                        "id": "A.8.3",
                        "title": "Information access restriction",
                        "description": "Access to information shall be restricted",
                        "type": "control",
                        "category": "technological",
                    },
                    {
                        "id": "A.8.4",
                        "title": "Access to source code",
                        "description": "Read and write access to source code shall be restricted",
                        "type": "control",
                        "category": "technological",
                    },
                    {
                        "id": "A.8.5",
                        "title": "Secure authentication",
                        "description": "Secure authentication technologies shall be implemented",
                        "type": "control",
                        "category": "technological",
                    },
                    {
                        "id": "A.8.9",
                        "title": "Configuration management",
                        "description": "Configurations shall be established and maintained",
                        "type": "control",
                        "category": "technological",
                    },
                    {
                        "id": "A.8.10",
                        "title": "Information deletion",
                        "description": "Information shall be deleted when no longer required",
                        "type": "control",
                        "category": "technological",
                    },
                    {
                        "id": "A.8.11",
                        "title": "Data masking",
                        "description": "Data masking shall be used in accordance with policy",
                        "type": "control",
                        "category": "technological",
                    },
                    {
                        "id": "A.8.12",
                        "title": "Data leakage prevention",
                        "description": "Data leakage prevention measures shall be applied",
                        "type": "control",
                        "category": "technological",
                    },
                ],
            },
        },
    },
    "ISO 9001:2015": {
        "title": "Quality Management System",
        "version": "2015",
        "clauses": {
            "4": {
                "title": "Context of the organization",
                "controls": [
                    {
                        "id": "4.1",
                        "title": "Understanding the organization and its context",
                        "description": "Determine issues relevant to QMS",
                        "type": "mandatory",
                        "category": "context",
                    },
                    {
                        "id": "4.2",
                        "title": "Understanding needs of interested parties",
                        "description": "Determine requirements of interested parties",
                        "type": "mandatory",
                        "category": "context",
                    },
                    {
                        "id": "4.3",
                        "title": "Determining scope of QMS",
                        "description": "Define boundaries of quality management system",
                        "type": "mandatory",
                        "category": "context",
                    },
                    {
                        "id": "4.4",
                        "title": "Quality management system and its processes",
                        "description": "Establish and maintain QMS processes",
                        "type": "mandatory",
                        "category": "context",
                    },
                ],
            },
            "5": {
                "title": "Leadership",
                "controls": [
                    {
                        "id": "5.1",
                        "title": "Leadership and commitment",
                        "description": "Top management leadership for QMS",
                        "type": "mandatory",
                        "category": "leadership",
                    },
                    {
                        "id": "5.2",
                        "title": "Quality policy",
                        "description": "Establish quality policy",
                        "type": "mandatory",
                        "category": "leadership",
                    },
                    {
                        "id": "5.3",
                        "title": "Organizational roles and responsibilities",
                        "description": "Assign QMS responsibilities",
                        "type": "mandatory",
                        "category": "leadership",
                    },
                ],
            },
            "6": {
                "title": "Planning",
                "controls": [
                    {
                        "id": "6.1",
                        "title": "Actions to address risks and opportunities",
                        "description": "Plan to address risks and opportunities",
                        "type": "mandatory",
                        "category": "planning",
                    },
                    {
                        "id": "6.2",
                        "title": "Quality objectives and planning",
                        "description": "Establish quality objectives",
                        "type": "mandatory",
                        "category": "planning",
                    },
                    {
                        "id": "6.3",
                        "title": "Planning of changes",
                        "description": "Plan changes to QMS",
                        "type": "mandatory",
                        "category": "planning",
                    },
                ],
            },
            "7": {
                "title": "Support",
                "controls": [
                    {
                        "id": "7.1",
                        "title": "Resources",
                        "description": "Determine and provide resources for QMS",
                        "type": "mandatory",
                        "category": "support",
                    },
                    {
                        "id": "7.2",
                        "title": "Competence",
                        "description": "Ensure competence of personnel",
                        "type": "mandatory",
                        "category": "support",
                    },
                    {
                        "id": "7.3",
                        "title": "Awareness",
                        "description": "Ensure awareness of quality policy",
                        "type": "mandatory",
                        "category": "support",
                    },
                    {
                        "id": "7.4",
                        "title": "Communication",
                        "description": "Determine QMS communications",
                        "type": "mandatory",
                        "category": "support",
                    },
                    {
                        "id": "7.5",
                        "title": "Documented information",
                        "description": "Control QMS documented information",
                        "type": "mandatory",
                        "category": "support",
                    },
                ],
            },
            "8": {
                "title": "Operation",
                "controls": [
                    {
                        "id": "8.1",
                        "title": "Operational planning and control",
                        "description": "Plan and control operations",
                        "type": "mandatory",
                        "category": "operation",
                    },
                    {
                        "id": "8.2",
                        "title": "Requirements for products and services",
                        "description": "Determine customer requirements",
                        "type": "mandatory",
                        "category": "operation",
                    },
                    {
                        "id": "8.3",
                        "title": "Design and development",
                        "description": "Control design and development",
                        "type": "mandatory",
                        "category": "operation",
                    },
                    {
                        "id": "8.4",
                        "title": "Control of external provision",
                        "description": "Control external providers",
                        "type": "mandatory",
                        "category": "operation",
                    },
                    {
                        "id": "8.5",
                        "title": "Production and service provision",
                        "description": "Control production and services",
                        "type": "mandatory",
                        "category": "operation",
                    },
                    {
                        "id": "8.6",
                        "title": "Release of products and services",
                        "description": "Verify requirements before release",
                        "type": "mandatory",
                        "category": "operation",
                    },
                    {
                        "id": "8.7",
                        "title": "Control of nonconforming outputs",
                        "description": "Control nonconforming products",
                        "type": "mandatory",
                        "category": "operation",
                    },
                ],
            },
            "9": {
                "title": "Performance evaluation",
                "controls": [
                    {
                        "id": "9.1",
                        "title": "Monitoring, measurement, analysis and evaluation",
                        "description": "Monitor QMS performance",
                        "type": "mandatory",
                        "category": "evaluation",
                    },
                    {
                        "id": "9.2",
                        "title": "Internal audit",
                        "description": "Conduct QMS internal audits",
                        "type": "mandatory",
                        "category": "evaluation",
                    },
                    {
                        "id": "9.3",
                        "title": "Management review",
                        "description": "Review QMS performance",
                        "type": "mandatory",
                        "category": "evaluation",
                    },
                ],
            },
            "10": {
                "title": "Improvement",
                "controls": [
                    {
                        "id": "10.1",
                        "title": "General improvement requirements",
                        "description": "Improve products, services and QMS",
                        "type": "mandatory",
                        "category": "improvement",
                    },
                    {
                        "id": "10.2",
                        "title": "Nonconformity and corrective action",
                        "description": "Address nonconformities",
                        "type": "mandatory",
                        "category": "improvement",
                    },
                    {
                        "id": "10.3",
                        "title": "Continual improvement",
                        "description": "Continually improve QMS",
                        "type": "mandatory",
                        "category": "improvement",
                    },
                ],
            },
        },
    },
    "ISO 22301:2019": {
        "title": "Business Continuity Management System",
        "version": "2019",
        "clauses": {
            "4": {
                "title": "Context of the organization",
                "controls": [
                    {
                        "id": "4.1",
                        "title": "Understanding the organization",
                        "description": "Determine issues for BCMS",
                        "type": "mandatory",
                        "category": "context",
                    },
                    {
                        "id": "4.2",
                        "title": "Understanding stakeholder needs",
                        "description": "Determine BCMS requirements",
                        "type": "mandatory",
                        "category": "context",
                    },
                    {
                        "id": "4.3",
                        "title": "Determining BCMS scope",
                        "description": "Define BCMS boundaries",
                        "type": "mandatory",
                        "category": "context",
                    },
                    {
                        "id": "4.4",
                        "title": "Business continuity management system",
                        "description": "Establish and maintain BCMS",
                        "type": "mandatory",
                        "category": "context",
                    },
                ],
            },
            "5": {
                "title": "Leadership",
                "controls": [
                    {
                        "id": "5.1",
                        "title": "Leadership and commitment",
                        "description": "Top management commitment to BCMS",
                        "type": "mandatory",
                        "category": "leadership",
                    },
                    {
                        "id": "5.2",
                        "title": "Business continuity policy",
                        "description": "Establish BC policy",
                        "type": "mandatory",
                        "category": "leadership",
                    },
                    {
                        "id": "5.3",
                        "title": "Organizational roles",
                        "description": "Assign BCMS responsibilities",
                        "type": "mandatory",
                        "category": "leadership",
                    },
                ],
            },
            "6": {
                "title": "Planning",
                "controls": [
                    {
                        "id": "6.1",
                        "title": "Actions to address risks",
                        "description": "Address BCMS risks",
                        "type": "mandatory",
                        "category": "planning",
                    },
                    {
                        "id": "6.2",
                        "title": "Business continuity objectives",
                        "description": "Establish BC objectives",
                        "type": "mandatory",
                        "category": "planning",
                    },
                    {
                        "id": "6.3",
                        "title": "Planning changes to BCMS",
                        "description": "Plan BCMS changes",
                        "type": "mandatory",
                        "category": "planning",
                    },
                ],
            },
            "8": {
                "title": "Operation",
                "controls": [
                    {
                        "id": "8.1",
                        "title": "Operational planning",
                        "description": "Plan BC operations",
                        "type": "mandatory",
                        "category": "operation",
                    },
                    {
                        "id": "8.2",
                        "title": "Business impact analysis",
                        "description": "Conduct BIA",
                        "type": "mandatory",
                        "category": "operation",
                    },
                    {
                        "id": "8.3",
                        "title": "Risk assessment",
                        "description": "Assess BC risks",
                        "type": "mandatory",
                        "category": "operation",
                    },
                    {
                        "id": "8.4",
                        "title": "Business continuity strategies",
                        "description": "Determine BC strategies",
                        "type": "mandatory",
                        "category": "operation",
                    },
                    {
                        "id": "8.5",
                        "title": "Business continuity procedures",
                        "description": "Establish BC procedures",
                        "type": "mandatory",
                        "category": "operation",
                    },
                    {
                        "id": "8.6",
                        "title": "Exercise and testing",
                        "description": "Test BC procedures",
                        "type": "mandatory",
                        "category": "operation",
                    },
                ],
            },
        },
    },
    "ISO 14001:2015": {
        "title": "Environmental Management System",
        "version": "2015",
        "clauses": {
            "4": {
                "title": "Context of the organization",
                "controls": [
                    {
                        "id": "4.1",
                        "title": "Understanding context",
                        "description": "Determine environmental issues",
                        "type": "mandatory",
                        "category": "context",
                    },
                    {
                        "id": "4.2",
                        "title": "Understanding needs",
                        "description": "Determine environmental requirements",
                        "type": "mandatory",
                        "category": "context",
                    },
                    {
                        "id": "4.3",
                        "title": "EMS scope",
                        "description": "Define EMS boundaries",
                        "type": "mandatory",
                        "category": "context",
                    },
                    {
                        "id": "4.4",
                        "title": "Environmental management system",
                        "description": "Establish and maintain EMS",
                        "type": "mandatory",
                        "category": "context",
                    },
                ],
            },
            "6": {
                "title": "Planning",
                "controls": [
                    {
                        "id": "6.1.1",
                        "title": "Environmental risks",
                        "description": "Address environmental risks",
                        "type": "mandatory",
                        "category": "planning",
                    },
                    {
                        "id": "6.1.2",
                        "title": "Environmental aspects",
                        "description": "Determine environmental aspects",
                        "type": "mandatory",
                        "category": "planning",
                    },
                    {
                        "id": "6.1.3",
                        "title": "Compliance obligations",
                        "description": "Determine compliance obligations",
                        "type": "mandatory",
                        "category": "planning",
                    },
                    {
                        "id": "6.1.4",
                        "title": "Planning action",
                        "description": "Plan actions for aspects and risks",
                        "type": "mandatory",
                        "category": "planning",
                    },
                    {
                        "id": "6.2",
                        "title": "Environmental objectives",
                        "description": "Establish environmental objectives",
                        "type": "mandatory",
                        "category": "planning",
                    },
                ],
            },
        },
    },
    "ISO 45001:2018": {
        "title": "Occupational Health and Safety Management System",
        "version": "2018",
        "clauses": {
            "4": {
                "title": "Context of the organization",
                "controls": [
                    {
                        "id": "4.1",
                        "title": "Understanding context",
                        "description": "Determine OH&S issues",
                        "type": "mandatory",
                        "category": "context",
                    },
                    {
                        "id": "4.2",
                        "title": "Understanding workers needs",
                        "description": "Determine worker requirements",
                        "type": "mandatory",
                        "category": "context",
                    },
                    {
                        "id": "4.3",
                        "title": "OH&S scope",
                        "description": "Define OH&S boundaries",
                        "type": "mandatory",
                        "category": "context",
                    },
                    {
                        "id": "4.4",
                        "title": "OH&S management system",
                        "description": "Establish and maintain OH&S",
                        "type": "mandatory",
                        "category": "context",
                    },
                ],
            },
            "5": {
                "title": "Leadership and worker participation",
                "controls": [
                    {
                        "id": "5.1",
                        "title": "Leadership commitment",
                        "description": "Top management OH&S commitment",
                        "type": "mandatory",
                        "category": "leadership",
                    },
                    {
                        "id": "5.2",
                        "title": "OH&S policy",
                        "description": "Establish OH&S policy",
                        "type": "mandatory",
                        "category": "leadership",
                    },
                    {
                        "id": "5.3",
                        "title": "Organizational roles",
                        "description": "Assign OH&S responsibilities",
                        "type": "mandatory",
                        "category": "leadership",
                    },
                    {
                        "id": "5.4",
                        "title": "Worker consultation",
                        "description": "Consult with workers",
                        "type": "mandatory",
                        "category": "leadership",
                    },
                ],
            },
            "6": {
                "title": "Planning",
                "controls": [
                    {
                        "id": "6.1.1",
                        "title": "General planning",
                        "description": "Plan OH&S system",
                        "type": "mandatory",
                        "category": "planning",
                    },
                    {
                        "id": "6.1.2",
                        "title": "Hazard identification",
                        "description": "Identify hazards and assess risks",
                        "type": "mandatory",
                        "category": "planning",
                    },
                    {
                        "id": "6.1.3",
                        "title": "Legal requirements",
                        "description": "Determine legal requirements",
                        "type": "mandatory",
                        "category": "planning",
                    },
                    {
                        "id": "6.1.4",
                        "title": "Planning action",
                        "description": "Plan actions for risks",
                        "type": "mandatory",
                        "category": "planning",
                    },
                    {
                        "id": "6.2",
                        "title": "OH&S objectives",
                        "description": "Establish OH&S objectives",
                        "type": "mandatory",
                        "category": "planning",
                    },
                ],
            },
        },
    },
}


def extract_iso_obligations():
    """Extract all ISO obligations and controls."""

    all_obligations = []
    framework_summary = {}

    for standard_name, standard_data in ISO_STANDARDS.items():
        framework_summary[standard_name] = {
            "title": standard_data["title"],
            "version": standard_data["version"],
            "obligations": [],
            "control_count": 0,
            "mandatory_count": 0,
        }

        for clause_num, clause_data in standard_data["clauses"].items():
            for control in clause_data["controls"]:
                # Create obligation object
                obligation = {
                    "framework": standard_name,
                    "framework_title": standard_data["title"],
                    "clause": clause_num,
                    "clause_title": clause_data["title"],
                    "control_id": control["id"],
                    "title": control["title"],
                    "description": control["description"],
                    "type": control["type"],
                    "category": control["category"],
                    "compliance_level": (
                        "mandatory" if control["type"] == "mandatory" else "recommended"
                    ),
                    "obligation_id": f"{standard_name.replace(':', '_').replace(' ', '_')}-{control['id']}",
                }

                all_obligations.append(obligation)
                framework_summary[standard_name]["obligations"].append(obligation)
                framework_summary[standard_name]["control_count"] += 1

                if control["type"] == "mandatory":
                    framework_summary[standard_name]["mandatory_count"] += 1

    return all_obligations, framework_summary


def create_iso_manifest(obligations: List[Dict], framework_summary: Dict):
    """Create ISO compliance manifest."""

    manifest = {
        "version": "1.0",
        "created_at": datetime.now().isoformat(),
        "total_obligations": len(obligations),
        "frameworks": {},
        "obligations": obligations,
    }

    # Organize by framework
    for framework_name, summary in framework_summary.items():
        manifest["frameworks"][framework_name] = {
            "name": framework_name,
            "title": summary["title"],
            "version": summary["version"],
            "control_count": summary["control_count"],
            "mandatory_count": summary["mandatory_count"],
            "obligations": summary["obligations"],
        }

    return manifest


def main():
    """Main extraction process."""

    print("=" * 80)
    print("ISO FRAMEWORK EXTRACTION")
    print("=" * 80)

    # Extract obligations
    obligations, framework_summary = extract_iso_obligations()

    print(
        f"\nExtracted {len(obligations)} total obligations from {len(framework_summary)} ISO standards"
    )

    # Display summary
    print("\nBy Framework:")
    for framework, summary in framework_summary.items():
        print(
            f"  - {framework}: {summary['control_count']} controls ({summary['mandatory_count']} mandatory)"
        )

    # Create manifest
    manifest = create_iso_manifest(obligations, framework_summary)

    # Save manifest
    output_dir = Path("/home/omar/Documents/ruleIQ/data/manifests")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / "iso_compliance_manifest.json"
    with open(output_path, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\nManifest saved to: {output_path}")

    # Save summary
    summary_path = output_dir / "iso_framework_summary.json"
    with open(summary_path, "w") as f:
        json.dump(framework_summary, f, indent=2)

    print(f"Summary saved to: {summary_path}")

    # Display sample obligations
    print("\n" + "=" * 80)
    print("SAMPLE ISO OBLIGATIONS")
    print("=" * 80)

    for i, obl in enumerate(obligations[:10], 1):
        print(f"\n{i}. {obl['obligation_id']}")
        print(f"   Framework: {obl['framework']}")
        print(f"   Control: {obl['control_id']} - {obl['title']}")
        print(f"   Description: {obl['description']}")
        print(f"   Type: {obl['type']}, Category: {obl['category']}")


if __name__ == "__main__":
    main()
