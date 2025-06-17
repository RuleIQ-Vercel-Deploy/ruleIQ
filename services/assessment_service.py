from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from core.assessment_session import AssessmentSession
from core.business_profile import BusinessProfile
from core.framework_service import get_relevant_frameworks
from sqlalchemy_access import User, authenticated


@authenticated
def start_assessment_session(user: User, session_type: str = "compliance_scoping") -> AssessmentSession:
    """Start a new assessment session for the user."""

    # Check if there's an active session
    existing_sessions = AssessmentSession.sql(
        "SELECT * FROM assessment_sessions WHERE user_id = %(user_id)s AND status = 'in_progress' ORDER BY created_at DESC",
        {"user_id": user.id}
    )

    if existing_sessions:
        # Return the most recent active session
        return AssessmentSession(**existing_sessions[0])

    # Get business profile if it exists
    profile_results = BusinessProfile.sql(
        "SELECT * FROM business_profiles WHERE user_id = %(user_id)s",
        {"user_id": user.id}
    )

    business_profile_id = None
    if profile_results:
        business_profile_id = profile_results[0]["id"]

    # Create new session
    session = AssessmentSession(
        user_id=user.id,
        business_profile_id=business_profile_id,
        session_type=session_type,
        total_stages=5,  # Basic info, Industry, Data handling, Tech stack, Compliance goals
        total_questions=25
    )

    session.sync()
    return session

@authenticated
def get_assessment_session(user: User, session_id: UUID) -> Optional[AssessmentSession]:
    """Get a specific assessment session."""
    results = AssessmentSession.sql(
        "SELECT * FROM assessment_sessions WHERE id = %(session_id)s AND user_id = %(user_id)s",
        {"session_id": session_id, "user_id": user.id}
    )

    if results:
        return AssessmentSession(**results[0])
    return None

@authenticated
def get_current_assessment_session(user: User) -> Optional[AssessmentSession]:
    """Get the current active assessment session for the user."""
    results = AssessmentSession.sql(
        "SELECT * FROM assessment_sessions WHERE user_id = %(user_id)s AND status = 'in_progress' ORDER BY created_at DESC LIMIT 1",
        {"user_id": user.id}
    )

    if results:
        return AssessmentSession(**results[0])
    return None

@authenticated
def update_assessment_response(
    user: User,
    session_id: UUID,
    question_id: str,
    response: str,
    move_to_next_stage: bool = False
) -> AssessmentSession:
    """Update an assessment response and optionally move to next stage."""

    session = get_assessment_session(user, session_id)
    if not session:
        raise ValueError("Assessment session not found")

    # Update response
    session.responses[question_id] = response
    session.questions_answered = len(session.responses)
    session.last_activity = datetime.now()

    # Move to next stage if requested
    if move_to_next_stage and session.current_stage < session.total_stages:
        session.current_stage += 1

    session.sync()
    return session

@authenticated
def complete_assessment_session(user: User, session_id: UUID) -> AssessmentSession:
    """Complete an assessment session and generate recommendations."""

    session = get_assessment_session(user, session_id)
    if not session:
        raise ValueError("Assessment session not found")

    # Update business profile with assessment data
    profile_results = BusinessProfile.sql(
        "SELECT * FROM business_profiles WHERE user_id = %(user_id)s",
        {"user_id": user.id}
    )

    if profile_results:
        profile = BusinessProfile(**profile_results[0])

        # Extract key information from responses
        profile.assessment_completed = True
        profile.assessment_data = session.responses

        # Update profile fields based on responses
        if "handles_personal_data" in session.responses:
            profile.handles_personal_data = session.responses["handles_personal_data"].lower() == "yes"
        if "processes_payments" in session.responses:
            profile.processes_payments = session.responses["processes_payments"].lower() == "yes"
        if "stores_health_data" in session.responses:
            profile.stores_health_data = session.responses["stores_health_data"].lower() == "yes"
        if "provides_financial_services" in session.responses:
            profile.provides_financial_services = session.responses["provides_financial_services"].lower() == "yes"

        profile.sync()

    # Generate framework recommendations
    relevant_frameworks = get_relevant_frameworks(user)

    session.recommendations = relevant_frameworks
    session.recommended_frameworks = [fw["framework"].name for fw in relevant_frameworks[:5]]
    session.priority_order = [fw["framework"].name for fw in relevant_frameworks]

    # Generate next steps
    next_steps = []
    if relevant_frameworks:
        top_framework = relevant_frameworks[0]["framework"]
        next_steps = [
            f"Start with {top_framework.display_name} as your highest priority framework",
            "Generate comprehensive policies for your top framework",
            "Create implementation plans for required controls",
            "Set up evidence collection processes",
            "Schedule regular compliance readiness assessments"
        ]

    session.next_steps = next_steps
    session.status = "completed"
    session.completed_at = datetime.now()

    session.sync()
    return session

@authenticated
def get_assessment_questions(user: User, stage: int) -> List[Dict]:
    """Get assessment questions for a specific stage."""

    questions = {
        1: [  # Basic Company Information
            {
                "id": "company_name",
                "question": "What is your company name?",
                "type": "text",
                "required": True
            },
            {
                "id": "industry",
                "question": "What industry does your company operate in?",
                "type": "select",
                "options": [
                    "Financial Services", "Healthcare", "Technology", "Manufacturing",
                    "Retail", "Education", "Government", "Non-profit", "Other"
                ],
                "required": True
            },
            {
                "id": "employee_count",
                "question": "How many employees does your company have?",
                "type": "number",
                "required": True
            },
            {
                "id": "annual_revenue",
                "question": "What is your approximate annual revenue?",
                "type": "select",
                "options": [
                    "Under £1M", "£1M-£5M", "£5M-£25M", "£25M-£100M", "Over £100M"
                ],
                "required": False
            }
        ],
        2: [  # Data and Services
            {
                "id": "handles_personal_data",
                "question": "Does your company collect, process, or store personal data of customers or employees?",
                "type": "radio",
                "options": ["Yes", "No"],
                "required": True
            },
            {
                "id": "processes_payments",
                "question": "Does your company process payment card transactions?",
                "type": "radio",
                "options": ["Yes", "No"],
                "required": True
            },
            {
                "id": "stores_health_data",
                "question": "Does your company handle health or medical information?",
                "type": "radio",
                "options": ["Yes", "No"],
                "required": True
            },
            {
                "id": "provides_financial_services",
                "question": "Does your company provide regulated financial services?",
                "type": "radio",
                "options": ["Yes", "No"],
                "required": True
            },
            {
                "id": "international_operations",
                "question": "Does your company operate internationally or serve customers outside the UK?",
                "type": "radio",
                "options": ["Yes", "No"],
                "required": True
            }
        ],
        3: [  # Technology Infrastructure
            {
                "id": "cloud_providers",
                "question": "Which cloud providers does your company use? (Select all that apply)",
                "type": "checkbox",
                "options": [
                    "AWS", "Microsoft Azure", "Google Cloud", "IBM Cloud", "None", "Other"
                ],
                "required": False
            },
            {
                "id": "saas_tools",
                "question": "Which SaaS tools does your company use? (Select all that apply)",
                "type": "checkbox",
                "options": [
                    "Microsoft 365", "Google Workspace", "Salesforce", "Slack",
                    "Zoom", "Atlassian", "Other"
                ],
                "required": False
            },
            {
                "id": "development_tools",
                "question": "Which development/collaboration tools does your company use?",
                "type": "checkbox",
                "options": [
                    "GitHub", "GitLab", "Bitbucket", "Azure DevOps", "Other", "None"
                ],
                "required": False
            }
        ],
        4: [  # Current Compliance State
            {
                "id": "existing_frameworks",
                "question": "Which compliance frameworks is your company currently compliant with?",
                "type": "checkbox",
                "options": [
                    "GDPR", "ISO 27001", "Cyber Essentials", "FCA", "PCI DSS", "SOC 2", "None"
                ],
                "required": False
            },
            {
                "id": "planned_frameworks",
                "question": "Which compliance frameworks is your company planning to achieve?",
                "type": "checkbox",
                "options": [
                    "GDPR", "ISO 27001", "Cyber Essentials", "FCA", "PCI DSS", "SOC 2"
                ],
                "required": False
            },
            {
                "id": "compliance_budget",
                "question": "What is your budget range for compliance initiatives?",
                "type": "select",
                "options": [
                    "Under £10K", "£10K-£25K", "£25K-£50K", "£50K-£100K", "Over £100K"
                ],
                "required": False
            }
        ],
        5: [  # Goals and Timeline
            {
                "id": "compliance_timeline",
                "question": "What is your target timeline for achieving compliance?",
                "type": "select",
                "options": [
                    "3 months", "6 months", "12 months", "18+ months"
                ],
                "required": True
            },
            {
                "id": "primary_driver",
                "question": "What is the primary driver for your compliance initiative?",
                "type": "select",
                "options": [
                    "Customer requirements", "Regulatory requirement", "Business growth",
                    "Risk management", "Competitive advantage"
                ],
                "required": True
            },
            {
                "id": "biggest_challenge",
                "question": "What do you expect to be your biggest compliance challenge?",
                "type": "select",
                "options": [
                    "Understanding requirements", "Resource allocation", "Technical implementation",
                    "Policy development", "Evidence collection", "Ongoing maintenance"
                ],
                "required": False
            }
        ]
    }

    return questions.get(stage, [])
