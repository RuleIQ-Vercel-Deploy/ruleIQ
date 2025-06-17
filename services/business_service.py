from datetime import datetime
from typing import Dict, List, Optional

from core.business_profile import BusinessProfile
from sqlalchemy_access import User, authenticated, public


@authenticated
def create_business_profile(
    user: User,
    company_name: str,
    industry: str,
    employee_count: int,
    annual_revenue: Optional[str] = None,
    handles_personal_data: bool = False,
    processes_payments: bool = False,
    stores_health_data: bool = False,
    provides_financial_services: bool = False,
    operates_critical_infrastructure: bool = False,
    has_international_operations: bool = False,
    cloud_providers: Optional[List[str]] = None,
    saas_tools: Optional[List[str]] = None,
    development_tools: Optional[List[str]] = None,
    existing_frameworks: Optional[List[str]] = None,
    planned_frameworks: Optional[List[str]] = None,
    compliance_budget: Optional[str] = None,
    compliance_timeline: Optional[str] = None
) -> BusinessProfile:
    """Create or update a business profile for the authenticated user."""

    # Check if profile already exists
    if planned_frameworks is None:
        planned_frameworks = []
    if existing_frameworks is None:
        existing_frameworks = []
    if development_tools is None:
        development_tools = []
    if saas_tools is None:
        saas_tools = []
    if cloud_providers is None:
        cloud_providers = []
    existing_profiles = BusinessProfile.sql(
        "SELECT * FROM business_profiles WHERE user_id = %(user_id)s",
        {"user_id": user.id}
    )

    if existing_profiles:
        # Update existing profile
        profile_data = existing_profiles[0]
        profile = BusinessProfile(**profile_data)

        # Update fields
        profile.company_name = company_name
        profile.industry = industry
        profile.employee_count = employee_count
        profile.annual_revenue = annual_revenue
        profile.handles_personal_data = handles_personal_data
        profile.processes_payments = processes_payments
        profile.stores_health_data = stores_health_data
        profile.provides_financial_services = provides_financial_services
        profile.operates_critical_infrastructure = operates_critical_infrastructure
        profile.has_international_operations = has_international_operations
        profile.cloud_providers = cloud_providers
        profile.saas_tools = saas_tools
        profile.development_tools = development_tools
        profile.existing_frameworks = existing_frameworks
        profile.planned_frameworks = planned_frameworks
        profile.compliance_budget = compliance_budget
        profile.compliance_timeline = compliance_timeline
        profile.updated_at = datetime.now()
    else:
        # Create new profile
        profile = BusinessProfile(
            user_id=user.id,
            company_name=company_name,
            industry=industry,
            employee_count=employee_count,
            annual_revenue=annual_revenue,
            handles_personal_data=handles_personal_data,
            processes_payments=processes_payments,
            stores_health_data=stores_health_data,
            provides_financial_services=provides_financial_services,
            operates_critical_infrastructure=operates_critical_infrastructure,
            has_international_operations=has_international_operations,
            cloud_providers=cloud_providers,
            saas_tools=saas_tools,
            development_tools=development_tools,
            existing_frameworks=existing_frameworks,
            planned_frameworks=planned_frameworks,
            compliance_budget=compliance_budget,
            compliance_timeline=compliance_timeline
        )

    profile.sync()
    return profile

@authenticated
def get_business_profile(user: User) -> Optional[BusinessProfile]:
    """Get the business profile for the authenticated user."""
    results = BusinessProfile.sql(
        "SELECT * FROM business_profiles WHERE user_id = %(user_id)s",
        {"user_id": user.id}
    )

    if results:
        return BusinessProfile(**results[0])
    return None

@authenticated
def update_assessment_status(user: User, assessment_completed: bool, assessment_data: Dict) -> BusinessProfile:
    """Update the assessment completion status and data."""
    profile = get_business_profile(user)
    if not profile:
        raise ValueError("Business profile not found")

    profile.assessment_completed = assessment_completed
    profile.assessment_data = assessment_data
    profile.updated_at = datetime.now()
    profile.sync()

    return profile

@public
def get_supported_industries() -> List[str]:
    """Get list of supported industries for business profiles."""
    return [
        "Financial Services",
        "Healthcare",
        "Technology",
        "Manufacturing",
        "Retail",
        "Education",
        "Government",
        "Non-profit",
        "Professional Services",
        "Real Estate",
        "Transportation",
        "Energy",
        "Media",
        "Hospitality",
        "Other"
    ]

@public
def get_cloud_provider_options() -> List[str]:
    """Get list of supported cloud providers."""
    return [
        "AWS (Amazon Web Services)",
        "Microsoft Azure",
        "Google Cloud Platform",
        "IBM Cloud",
        "Oracle Cloud",
        "DigitalOcean",
        "Linode",
        "Vultr",
        "Other"
    ]

@public
def get_saas_tool_options() -> List[str]:
    """Get list of common SaaS tools for integration guidance."""
    return [
        "Microsoft 365",
        "Google Workspace",
        "Salesforce",
        "Slack",
        "Zoom",
        "Atlassian (Jira/Confluence)",
        "HubSpot",
        "Zendesk",
        "DocuSign",
        "Dropbox",
        "Box",
        "ServiceNow",
        "Other"
    ]
