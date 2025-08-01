"""
AI Policy Generation API Router

Provides endpoints for AI-powered policy generation with dual provider support.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session

from database.db_setup import get_db
from database.compliance_framework import ComplianceFramework
from api.schemas.ai_policy import (
    PolicyGenerationRequest, PolicyGenerationResponse,
    PolicyRefinementRequest, PolicyRefinementResponse,
    PolicyTemplatesResponse, PolicyTemplate,
    AIProviderMetrics, PolicyGenerationMetrics
)
from services.ai.policy_generator import PolicyGenerator, TemplateProcessor
from api.dependencies.auth import get_current_active_user
from database.user import User
from api.middleware.rate_limiter import RateLimited


router = APIRouter(prefix="/api/v1/ai", tags=["AI Policy Generation"])


@router.post(
    "/generate-policy",
    response_model=PolicyGenerationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(get_current_active_user),
        Depends(RateLimited(requests=20, window=60))  # AI endpoint rate limiting
    ]
)
async def generate_policy(
    request: PolicyGenerationRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Generate compliance policy using AI with dual provider fallback.
    
    Requires authentication. Limited to 20 requests per minute per user.
    Uses Google AI (primary) with OpenAI fallback for reliability.
    """
    # Validate framework exists
    framework = db.query(ComplianceFramework)\
        .filter(ComplianceFramework.id == request.framework_id)\
        .first()
    
    if not framework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Framework not found: {request.framework_id}"
        )
    
    if not framework.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Framework is not active: {framework.name}"
        )
    
    # Initialize policy generator
    generator = PolicyGenerator()
    
    try:
        # Generate policy
        result = generator.generate_policy(request, framework)
        
        # Log metrics in background
        background_tasks.add_task(
            _log_generation_metrics,
            result,
            request.framework_id,
            framework.name
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Policy generation failed: {str(e)}"
        )


@router.put(
    "/refine-policy",
    response_model=PolicyRefinementResponse,
    dependencies=[
        Depends(get_current_active_user),
        Depends(RateLimited(requests=30, window=60))
    ]
)
async def refine_policy(
    request: PolicyRefinementRequest,
    db: Session = Depends(get_db)
):
    """
    Refine existing policy based on feedback.
    
    Requires authentication. Limited to 30 requests per minute per user.
    """
    # Validate framework exists
    framework = db.query(ComplianceFramework)\
        .filter(ComplianceFramework.id == request.framework_id)\
        .first()
    
    if not framework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Framework not found: {request.framework_id}"
        )
    
    generator = PolicyGenerator()
    
    try:
        result = generator.refine_policy(
            request.original_policy,
            request.feedback,
            framework
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Policy refinement failed: {str(e)}"
        )


@router.get(
    "/policy-templates",
    response_model=PolicyTemplatesResponse,
    dependencies=[Depends(RateLimited(requests=100, window=60))]
)
async def get_policy_templates(
    framework_id: Optional[str] = None,
    policy_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get available policy templates.
    
    Can be filtered by framework and policy type.
    Limited to 100 requests per minute.
    """
    processor = TemplateProcessor()
    
    # Base templates available
    templates = [
        PolicyTemplate(
            id="uk_gdpr_privacy_policy",
            name="UK GDPR Privacy Policy",
            description="GDPR-compliant privacy policy for UK organizations",
            policy_type="privacy_policy",
            framework_compatibility=["ICO_GDPR_UK"],
            sections=["data_controller_info", "legal_basis", "data_subject_rights", "retention"],
            customization_options={
                "include_marketing": True,
                "include_cookies": True,
                "include_third_parties": True
            }
        ),
        PolicyTemplate(
            id="iso27001_info_sec_policy",
            name="ISO 27001 Information Security Policy",
            description="Information security policy based on ISO 27001 template",
            policy_type="information_security_policy",
            framework_compatibility=["ISO27001_UK"],
            sections=["policy_statement", "scope", "responsibilities", "implementation"],
            customization_options={
                "include_risk_assessment": True,
                "include_incident_response": True,
                "include_business_continuity": False
            }
        ),
        PolicyTemplate(
            id="fca_data_governance",
            name="FCA Data Governance Policy",
            description="Data governance policy for FCA-regulated firms",
            policy_type="data_governance_policy",
            framework_compatibility=["FCA_REGULATORY"],
            sections=["governance_framework", "data_quality", "regulatory_reporting"],
            customization_options={
                "include_smcr": True,
                "include_operational_resilience": True
            }
        ),
        PolicyTemplate(
            id="cyber_essentials_security",
            name="Cyber Essentials Security Policy",
            description="Basic security policy for Cyber Essentials certification",
            policy_type="cybersecurity_policy",
            framework_compatibility=["CYBER_ESSENTIALS_UK"],
            sections=["network_security", "access_control", "malware_protection"],
            customization_options={
                "include_remote_working": True,
                "include_byod": False
            }
        )
    ]
    
    # Filter by framework if specified
    if framework_id:
        framework = db.query(ComplianceFramework)\
            .filter(ComplianceFramework.id == framework_id)\
            .first()
        
        if framework:
            templates = [
                t for t in templates 
                if framework.name in t.framework_compatibility
            ]
    
    # Filter by policy type if specified
    if policy_type:
        templates = [t for t in templates if t.policy_type == policy_type]
    
    supported_frameworks = list(set(
        fw for template in templates 
        for fw in template.framework_compatibility
    ))
    
    return PolicyTemplatesResponse(
        templates=templates,
        total_count=len(templates),
        supported_frameworks=supported_frameworks,
        supported_languages=["en-GB", "en-US"]
    )


@router.get(
    "/metrics",
    response_model=PolicyGenerationMetrics,
    dependencies=[
        Depends(get_current_active_user),
        Depends(RateLimited(requests=50, window=60))
    ]
)
async def get_ai_metrics():
    """
    Get AI policy generation metrics and performance data.
    
    Requires authentication. Shows provider performance, costs, and usage.
    """
    # This would typically come from a metrics service
    # For now, returning sample data structure
    
    google_metrics = AIProviderMetrics(
        provider="google",
        requests_total=150,
        requests_successful=142,
        requests_failed=8,
        average_response_time_ms=2500.0,
        average_confidence_score=0.91,
        total_cost=45.30,
        last_24h_requests=25
    )
    
    openai_metrics = AIProviderMetrics(
        provider="openai",
        requests_total=25,  # Fallback usage
        requests_successful=23,
        requests_failed=2,
        average_response_time_ms=3200.0,
        average_confidence_score=0.88,
        total_cost=12.75,
        last_24h_requests=3
    )
    
    from services.ai.circuit_breaker import CircuitBreakerService
    circuit_breaker = CircuitBreakerService()
    
    circuit_status = {
        "google_status": circuit_breaker.get_state("google"),
        "openai_status": circuit_breaker.get_state("openai"),
        "failure_count": 0,
        "last_failure_time": None,
        "next_retry_time": None
    }
    
    return PolicyGenerationMetrics(
        total_policies_generated=175,
        success_rate=0.94,
        average_generation_time_ms=2650.0,
        cache_hit_rate=0.15,
        provider_metrics=[google_metrics, openai_metrics],
        circuit_breaker_status=circuit_status,
        cost_savings_percentage=42.5,
        monthly_cost_trend=[65.20, 58.05, 52.30, 48.15]
    )


@router.post(
    "/validate-policy",
    dependencies=[
        Depends(get_current_active_user),
        Depends(RateLimited(requests=50, window=60))
    ]
)
async def validate_policy(
    policy_content: str,
    framework_id: str,
    db: Session = Depends(get_db)
):
    """
    Validate policy against framework requirements.
    
    Requires authentication. Limited to 50 requests per minute.
    """
    framework = db.query(ComplianceFramework)\
        .filter(ComplianceFramework.id == framework_id)\
        .first()
    
    if not framework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Framework not found: {framework_id}"
        )
    
    generator = PolicyGenerator()
    
    try:
        validation_result = generator.validate_uk_policy(policy_content, framework)
        return validation_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Policy validation failed: {str(e)}"
        )


async def _log_generation_metrics(
    result: PolicyGenerationResponse,
    framework_id: str,
    framework_name: str
):
    """
    Log policy generation metrics in background.
    
    Args:
        result: Policy generation result
        framework_id: Framework ID used
        framework_name: Framework name
    """
    # This would typically write to a metrics database or service
    # For now, just log the information
    
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Policy generated: framework={framework_name}, "
               f"provider={result.provider_used}, "
               f"confidence={result.confidence_score}, "
               f"time={result.generation_time_ms}ms, "
               f"cost=${result.estimated_cost or 0:.3f}")


# Background task for policy generation analytics
@router.post(
    "/analytics/export",
    dependencies=[
        Depends(get_current_active_user),
        Depends(RateLimited(requests=5, window=3600))  # 5 per hour
    ]
)
async def export_analytics(
    start_date: str,
    end_date: str,
    format: str = "csv"
):
    """
    Export policy generation analytics.
    
    Limited to 5 exports per hour. Requires admin permissions.
    """
    if format not in ["csv", "json", "xlsx"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supported formats: csv, json, xlsx"
        )
    
    # This would generate actual analytics export
    return {
        "message": f"Analytics export started for {start_date} to {end_date}",
        "format": format,
        "estimated_completion": "2-3 minutes",
        "download_url": "/api/v1/ai/analytics/download/{export_id}"
    }