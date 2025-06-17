from typing import Dict, List, Optional
from uuid import UUID

from core.business_profile import BusinessProfile
from core.compliance_framework import ComplianceFramework
from database.db_setup import SessionLocal
from sqlalchemy_access import User, authenticated, public


@public
def get_all_frameworks() -> List[ComplianceFramework]:
    """Get all available compliance frameworks."""
    db = SessionLocal()
    try:
        return db.query(ComplianceFramework).filter(ComplianceFramework.is_active).order_by(ComplianceFramework.name).all()
    finally:
        db.close()

@public
def get_framework_by_id(framework_id: UUID) -> Optional[ComplianceFramework]:
    """Get a specific compliance framework by ID."""
    results = ComplianceFramework.sql(
        "SELECT * FROM compliance_frameworks WHERE id = %(framework_id)s",
        {"framework_id": framework_id}
    )

    if results:
        return ComplianceFramework(**results[0])
    return None

@public
def get_framework_by_name(name: str) -> Optional[ComplianceFramework]:
    """Get a specific compliance framework by name."""
    results = ComplianceFramework.sql(
        "SELECT * FROM compliance_frameworks WHERE name = %(name)s",
        {"name": name}
    )

    if results:
        return ComplianceFramework(**results[0])
    return None

@authenticated
def get_relevant_frameworks(user: User) -> List[Dict]:
    """Get compliance frameworks relevant to the user's business profile with relevance scores."""
    # Get business profile
    profile_results = BusinessProfile.sql(
        "SELECT * FROM business_profiles WHERE user_id = %(user_id)s",
        {"user_id": user.id}
    )

    if not profile_results:
        return []

    profile = BusinessProfile(**profile_results[0])
    frameworks = get_all_frameworks()

    relevant_frameworks = []

    for framework in frameworks:
        relevance_score = calculate_framework_relevance(profile, framework)
        if relevance_score > 0:
            relevant_frameworks.append({
                "framework": framework,
                "relevance_score": relevance_score,
                "relevance_reasons": get_relevance_reasons(profile, framework)
            })

    # Sort by relevance score descending
    relevant_frameworks.sort(key=lambda x: x["relevance_score"], reverse=True)

    return relevant_frameworks

def calculate_framework_relevance(profile: BusinessProfile, framework: ComplianceFramework) -> float:
    """Calculate relevance score (0-1) for a framework given a business profile."""
    score = 0.0

    # Industry relevance (40% weight)
    if profile.industry in framework.applicable_industries:
        score += 0.4
    elif "All" in framework.applicable_industries:
        score += 0.2

    # Employee threshold (20% weight)
    if framework.employee_threshold:
        if profile.employee_count >= framework.employee_threshold:
            score += 0.2
    else:
        score += 0.1  # No threshold means generally applicable

    # Business characteristics (30% weight)
    char_score = 0
    total_chars = 0

    # GDPR relevance
    if framework.name == "GDPR" and profile.handles_personal_data:
        char_score += 1
        total_chars += 1

    # FCA relevance
    if framework.name == "FCA" and profile.provides_financial_services:
        char_score += 1
        total_chars += 1

    # CQC relevance
    if framework.name == "CQC" and profile.stores_health_data:
        char_score += 1
        total_chars += 1

    # PCI DSS relevance
    if framework.name == "PCI DSS" and profile.processes_payments:
        char_score += 1
        total_chars += 1

    # Cyber Essentials relevance (general)
    if framework.name == "Cyber Essentials":
        char_score += 0.8
        total_chars += 1

    # ISO 27001 relevance (general but higher for tech)
    if framework.name == "ISO 27001":
        if profile.industry == "Technology":
            char_score += 1
        else:
            char_score += 0.6
        total_chars += 1

    if total_chars > 0:
        score += (char_score / total_chars) * 0.3

    # Existing/planned frameworks (10% weight)
    if framework.name in profile.existing_frameworks:
        score += 0.1
    elif framework.name in profile.planned_frameworks:
        score += 0.05

    return min(score, 1.0)  # Cap at 1.0

def get_relevance_reasons(profile: BusinessProfile, framework: ComplianceFramework) -> List[str]:
    """Get human-readable reasons why a framework is relevant."""
    reasons = []

    if profile.industry in framework.applicable_industries:
        reasons.append(f"Applies to {profile.industry} industry")

    if framework.employee_threshold and profile.employee_count >= framework.employee_threshold:
        reasons.append(f"Company size ({profile.employee_count} employees) meets threshold")

    # Specific framework reasons
    if framework.name == "GDPR" and profile.handles_personal_data:
        reasons.append("Handles personal data")

    if framework.name == "FCA" and profile.provides_financial_services:
        reasons.append("Provides financial services")

    if framework.name == "CQC" and profile.stores_health_data:
        reasons.append("Stores health data")

    if framework.name == "PCI DSS" and profile.processes_payments:
        reasons.append("Processes payment card data")

    if framework.name == "Cyber Essentials":
        reasons.append("Essential cybersecurity baseline for all UK businesses")

    if framework.name == "ISO 27001":
        reasons.append("International information security standard")

    if framework.name in profile.existing_frameworks:
        reasons.append("Currently implementing or compliant")
    elif framework.name in profile.planned_frameworks:
        reasons.append("Planned for future implementation")

    return reasons

@public
def initialize_default_frameworks():
    """Initialize the database with default compliance frameworks."""
    frameworks_data = [
        {
            "name": "GDPR",
            "display_name": "General Data Protection Regulation",
            "description": "EU regulation on data protection and privacy for individuals within the European Union and European Economic Area",
            "category": "Data Protection",
            "applicable_industries": ["All"],
            "employee_threshold": None,
            "geographic_scope": ["UK", "EU"],
            "key_requirements": [
                "Data protection by design and by default",
                "Lawful basis for processing",
                "Data subject rights",
                "Data protection impact assessments",
                "Data breach notification"
            ],
            "control_domains": [
                "Data Governance",
                "Access Control",
                "Data Minimization",
                "Security Measures",
                "Breach Response"
            ],
            "complexity_score": 4,
            "implementation_time_weeks": 16,
            "estimated_cost_range": "£15,000-£50,000"
        },
        {
            "name": "FCA",
            "display_name": "Financial Conduct Authority",
            "description": "UK financial services regulation ensuring consumer protection and market integrity",
            "category": "Financial Services",
            "applicable_industries": ["Financial Services"],
            "employee_threshold": None,
            "geographic_scope": ["UK"],
            "key_requirements": [
                "Senior Management Arrangements",
                "Systems and Controls",
                "Consumer Protection",
                "Market Conduct",
                "Prudential Requirements"
            ],
            "control_domains": [
                "Governance",
                "Risk Management",
                "Compliance Monitoring",
                "Customer Protection",
                "Financial Crime Prevention"
            ],
            "complexity_score": 5,
            "implementation_time_weeks": 24,
            "estimated_cost_range": "£25,000-£100,000"
        },
        {
            "name": "Cyber Essentials",
            "display_name": "Cyber Essentials",
            "description": "UK government-backed cybersecurity certification scheme",
            "category": "Cybersecurity",
            "applicable_industries": ["All"],
            "employee_threshold": None,
            "geographic_scope": ["UK"],
            "key_requirements": [
                "Boundary firewalls and internet gateways",
                "Secure configuration",
                "Access control",
                "Malware protection",
                "Patch management"
            ],
            "control_domains": [
                "Network Security",
                "System Configuration",
                "Access Management",
                "Malware Protection",
                "Update Management"
            ],
            "complexity_score": 2,
            "implementation_time_weeks": 8,
            "estimated_cost_range": "£5,000-£15,000"
        },
        {
            "name": "ISO 27001",
            "display_name": "ISO 27001 Information Security Management",
            "description": "International standard for information security management systems",
            "category": "Information Security",
            "applicable_industries": ["All"],
            "employee_threshold": 50,
            "geographic_scope": ["Global"],
            "key_requirements": [
                "Information Security Management System",
                "Risk Assessment and Treatment",
                "Security Controls Implementation",
                "Continuous Monitoring",
                "Management Review"
            ],
            "control_domains": [
                "ISMS Framework",
                "Risk Management",
                "Asset Management",
                "Access Control",
                "Cryptography",
                "Physical Security",
                "Incident Management"
            ],
            "complexity_score": 4,
            "implementation_time_weeks": 20,
            "estimated_cost_range": "£20,000-£75,000"
        }
    ]

    for framework_data in frameworks_data:
        # Check if framework already exists
        existing = ComplianceFramework.sql(
            "SELECT * FROM compliance_frameworks WHERE name = %(name)s",
            {"name": framework_data["name"]}
        )

        if not existing:
            framework = ComplianceFramework(**framework_data)
            framework.sync()
