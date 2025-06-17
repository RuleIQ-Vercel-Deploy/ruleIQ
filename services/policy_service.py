import json
import time
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from api.utils.circuit_breaker import google_breaker, CircuitBreakerOpenException
from api.utils.retry import api_retry, RetryExhaustedError
from config.ai_config import generate_compliance_content
from core.business_profile import BusinessProfile
from core.compliance_framework import ComplianceFramework
from core.generated_policy import GeneratedPolicy
from sqlalchemy_access import User, authenticated

# AI client is initialized through config

@authenticated
async def generate_compliance_policy(
    user: User,
    framework_id: UUID,
    policy_type: str = "comprehensive",
    custom_requirements: Optional[List[str]] = None
) -> GeneratedPolicy:
    """Generate a comprehensive compliance policy using AI."""

    if custom_requirements is None:
        custom_requirements = []
    start_time = time.time()

    # Get business profile
    profile_results = BusinessProfile.sql(
        "SELECT * FROM business_profiles WHERE user_id = %(user_id)s",
        {"user_id": user.id}
    )

    if not profile_results:
        raise ValueError("Business profile not found. Please complete your business assessment first.")

    profile = BusinessProfile(**profile_results[0])

    # Get compliance framework
    framework_results = ComplianceFramework.sql(
        "SELECT * FROM compliance_frameworks WHERE id = %(framework_id)s",
        {"framework_id": framework_id}
    )

    if not framework_results:
        raise ValueError("Compliance framework not found")

    framework = ComplianceFramework(**framework_results[0])

    # Build generation prompt
    prompt = build_policy_generation_prompt(profile, framework, policy_type, custom_requirements)

    # Generate policy using AI with circuit breaker and retry protection
    try:
        policy_content = await _generate_policy_with_protection(prompt)
        policy_data = json.loads(policy_content)

    except CircuitBreakerOpenException as e:
        raise ValueError(f"Policy generation service temporarily unavailable: {e.message}")
    except RetryExhaustedError as e:
        raise ValueError(f"Failed to generate policy after {e.attempts} attempts: {e.last_exception}")
    except Exception as e:
        raise ValueError(f"Failed to generate policy: {e!s}")

    generation_time = time.time() - start_time

    # Calculate policy metrics
    word_count = len(policy_data["policy_content"].split())
    estimated_reading_time = max(1, word_count // 200)  # 200 words per minute

    # Create policy record
    policy = GeneratedPolicy(
        user_id=user.id,
        business_profile_id=profile.id,
        framework_id=framework_id,
        policy_name=f"{framework.display_name} Compliance Policy",
        framework_name=framework.name,
        policy_type=policy_type,
        generation_prompt=prompt,
        generation_model="gemini-2.5-flash-preview-05-20",
        generation_time_seconds=generation_time,
        policy_content=policy_data["policy_content"],
        procedures=policy_data["procedures"],
        tool_recommendations=policy_data["tool_recommendations"],
        sections=policy_data["sections"],
        controls=policy_data["controls"],
        responsibilities=policy_data["responsibilities"],
        word_count=word_count,
        estimated_reading_time=estimated_reading_time,
        compliance_coverage=0.85  # Default high coverage score
    )

    policy.sync()
    return policy


@api_retry
async def _generate_policy_with_protection(prompt: str) -> str:
    """Generate policy content with circuit breaker and retry protection."""
    return await google_breaker.call(_async_generate_compliance_content, prompt)


async def _async_generate_compliance_content(prompt: str) -> str:
    """Async wrapper for the generate_compliance_content function."""
    import asyncio
    # Run the sync function in a thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, generate_compliance_content, prompt)


def build_policy_generation_prompt(
    profile: BusinessProfile,
    framework: ComplianceFramework,
    policy_type: str,
    custom_requirements: List[str]
) -> str:
    """Build a comprehensive prompt for policy generation."""

    business_context = f"""
Company Profile:
- Name: {profile.company_name}
- Industry: {profile.industry}
- Size: {profile.employee_count} employees
- Handles Personal Data: {'Yes' if profile.handles_personal_data else 'No'}
- Processes Payments: {'Yes' if profile.processes_payments else 'No'}
- Stores Health Data: {'Yes' if profile.stores_health_data else 'No'}
- Provides Financial Services: {'Yes' if profile.provides_financial_services else 'No'}
- Cloud Providers: {', '.join(profile.cloud_providers) if profile.cloud_providers else 'None specified'}
- SaaS Tools: {', '.join(profile.saas_tools) if profile.saas_tools else 'None specified'}
"""

    framework_context = f"""
Compliance Framework: {framework.display_name}
Description: {framework.description}
Key Requirements: {', '.join(framework.key_requirements)}
Control Domains: {', '.join(framework.control_domains)}
"""

    custom_reqs = ""
    if custom_requirements:
        custom_reqs = "\nAdditional Custom Requirements:\n" + '\n'.join([f"- {req}" for req in custom_requirements])

    prompt = f"""Generate a comprehensive {policy_type} compliance policy for {framework.display_name} tailored to this specific business context:

{business_context}

{framework_context}
{custom_reqs}

Requirements:
1. Create a complete, audit-ready policy document that addresses all key requirements
2. Tailor all content specifically to the company's industry, size, and technical context
3. Include specific procedures with clear step-by-step instructions
4. Provide role-based responsibilities (CEO, CISO, IT Manager, etc.)
5. Recommend specific tools and systems appropriate for this business size and context
6. Include all necessary controls with implementation guidance
7. Specify required evidence and documentation
8. Use clear, professional language suitable for executives and auditors
9. Structure the policy with clear sections and subsections
10. Ensure the policy is practical and implementable for a {profile.employee_count}-person company

The policy should be comprehensive enough to serve as the foundation for achieving compliance certification and passing regulatory audits. Focus on practical implementation rather than theoretical concepts.

Format the response as a structured JSON with all required fields."""

    return prompt

@authenticated
def get_user_policies(user: User) -> List[GeneratedPolicy]:
    """Get all policies generated by the user."""
    results = GeneratedPolicy.sql(
        "SELECT * FROM generated_policies WHERE user_id = %(user_id)s ORDER BY created_at DESC",
        {"user_id": user.id}
    )

    return [GeneratedPolicy(**result) for result in results]

@authenticated
def get_policy_by_id(user: User, policy_id: UUID) -> Optional[GeneratedPolicy]:
    """Get a specific policy by ID."""
    results = GeneratedPolicy.sql(
        "SELECT * FROM generated_policies WHERE id = %(policy_id)s AND user_id = %(user_id)s",
        {"policy_id": policy_id, "user_id": user.id}
    )

    if results:
        return GeneratedPolicy(**results[0])
    return None

@authenticated
def update_policy_status(
    user: User,
    policy_id: UUID,
    status: str,
    review_notes: str = ""
) -> GeneratedPolicy:
    """Update the status of a generated policy."""

    policy = get_policy_by_id(user, policy_id)
    if not policy:
        raise ValueError("Policy not found")

    policy.status = status
    policy.review_notes = review_notes
    policy.updated_at = datetime.now()

    if status == "reviewed":
        policy.reviewed_at = datetime.now()
    elif status == "approved":
        policy.approved_at = datetime.now()

    policy.sync()
    return policy

@authenticated
async def regenerate_policy_section(
    user: User,
    policy_id: UUID,
    section_title: str,
    additional_context: str = ""
) -> GeneratedPolicy:
    """Regenerate a specific section of a policy."""

    policy = get_policy_by_id(user, policy_id)
    if not policy:
        raise ValueError("Policy not found")

    # Get business profile and framework
    profile = BusinessProfile.sql(
        "SELECT * FROM business_profiles WHERE id = %(id)s",
        {"id": policy.business_profile_id}
    )[0]

    framework = ComplianceFramework.sql(
        "SELECT * FROM compliance_frameworks WHERE id = %(id)s",
        {"id": policy.framework_id}
    )[0]

    # Build focused prompt for section regeneration
    prompt = f"""
Regenerate the "{section_title}" section of a {framework['display_name']} compliance policy.

Current section content:
{next((section['content'] for section in policy.sections if section['title'] == section_title), 'Section not found')}

Business context:
- Company: {profile['company_name']} ({profile['industry']})
- Size: {profile['employee_count']} employees

Additional context: {additional_context}

Provide an improved version of this section that is more detailed, specific to the business context, and addresses any gaps in the current content.
"""

    try:
        new_content = await _generate_policy_with_protection(prompt)

        # Update the section in the policy
        for section in policy.sections:
            if section["title"] == section_title:
                section["content"] = new_content
                break

        policy.updated_at = datetime.now()
        policy.sync()

    except CircuitBreakerOpenException as e:
        raise ValueError(f"Policy regeneration service temporarily unavailable: {e.message}")
    except RetryExhaustedError as e:
        raise ValueError(f"Failed to regenerate section after {e.attempts} attempts: {e.last_exception}")
    except Exception as e:
        raise ValueError(f"Failed to regenerate section: {e!s}")

    return policy
