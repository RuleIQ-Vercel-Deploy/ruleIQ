"""
AI Policy Generation API Router

Provides endpoints for AI-powered policy generation with dual provider support.
"""
from __future__ import annotations
from typing import Optional, Any, Dict, AsyncGenerator, Generator
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from database.db_setup import get_db
from database.compliance_framework import ComplianceFramework
from api.schemas.ai_policy import PolicyGenerationRequest, PolicyGenerationResponse, PolicyRefinementRequest, PolicyRefinementResponse, PolicyTemplatesResponse, PolicyTemplate, AIProviderMetrics, PolicyGenerationMetrics
from services.ai.policy_generator import PolicyGenerator, TemplateProcessor
from api.dependencies.auth import get_current_active_user
from api.middleware.rate_limiter import RateLimited
from services.rate_limiting import RateLimitService
from database.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from database.db_setup import get_async_db
import logging
logger = logging.getLogger(__name__)
router = APIRouter(tags=['AI Policy Generation'])

@router.post('/generate-policy', response_model=PolicyGenerationResponse,
    status_code=status.HTTP_201_CREATED, dependencies=[Depends(
    get_current_active_user), Depends(RateLimited(requests=20, window=60))])
async def generate_policy(request: PolicyGenerationRequest,
    background_tasks: BackgroundTasks, current_user: User=Depends(
    get_current_active_user), db: Session=Depends(get_db), async_db:
    AsyncSession=Depends(get_async_db)) -> PolicyGenerationResponse:
    """Generate a new policy based on the provided data using OpenAI or Gemini."""
    rate_limiter = RateLimitService()
    allowed, wait_time = await rate_limiter.check_rate_limit(user_id=
        current_user['id'], action_type='policy_generation', db=async_db)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f'Rate limit exceeded. Please wait {wait_time:.0f} seconds.')
    if not request.framework_id and not request.control_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail
            ='Either framework_id or control_id must be provided')
    generator = PolicyGenerator()
    framework = None
    if request.framework_id:
        framework = db.query(ComplianceFramework).filter(ComplianceFramework.
            id == request.framework_id).first()
        if not framework:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Framework with ID {request.framework_id} not found')
    try:
        policy_data = await generator.generate_policy(business_context=
            request.business_context, policy_type=request.policy_type,
            control_id=request.control_id, framework=framework, provider=
            request.ai_provider, use_cache=request.use_cache, model_params
            =request.model_params, db=async_db)
        background_tasks.add_task(generator.log_generation_metrics, user_id
            =current_user['id'], framework_id=request.framework_id,
            provider=request.ai_provider, success=True, db=async_db)
        return PolicyGenerationResponse(**policy_data)
    except ValueError as e:
        background_tasks.add_task(generator.log_generation_metrics, user_id
            =current_user['id'], framework_id=request.framework_id,
            provider=request.ai_provider, success=False, error=str(e), db=
            async_db)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail
            =str(e))
    except Exception as e:
        background_tasks.add_task(generator.log_generation_metrics, user_id
            =current_user['id'], framework_id=request.framework_id,
            provider=request.ai_provider, success=False, error=str(e), db=
            async_db)
        logger.error(f'Policy generation failed: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Policy generation failed')

@router.post('/refine-policy', response_model=PolicyRefinementResponse,
    dependencies=[Depends(get_current_active_user), Depends(RateLimited(
    requests=30, window=60))])
async def refine_policy(request: PolicyRefinementRequest, current_user:
    User=Depends(get_current_active_user), async_db: AsyncSession=Depends(
    get_async_db)) -> PolicyRefinementResponse:
    """Refine an existing policy based on user feedback."""
    rate_limiter = RateLimitService()
    allowed, wait_time = await rate_limiter.check_rate_limit(user_id=
        current_user['id'], action_type='policy_refinement', db=async_db)
    if not allowed:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f'Rate limit exceeded. Please wait {wait_time:.0f} seconds.')
    generator = PolicyGenerator()
    try:
        refined_policy = await generator.refine_policy(policy_id=request.
            policy_id, refinement_instructions=request.
            refinement_instructions, additional_context=request.
            additional_context, provider=request.ai_provider, model_params
            =request.model_params, db=async_db)
        return PolicyRefinementResponse(**refined_policy)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail
            =str(e))
    except Exception as e:
        logger.error(f'Policy refinement failed: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Policy refinement failed')

@router.get('/templates', response_model=PolicyTemplatesResponse,
    dependencies=[Depends(get_current_active_user)])
async def get_policy_templates(policy_type: Optional[str]=None, framework_id:
    Optional[int]=None, current_user: User=Depends(get_current_active_user),
    db: Session=Depends(get_db)) -> PolicyTemplatesResponse:
    """Get available policy templates."""
    try:
        processor = TemplateProcessor()
        templates = processor.get_templates(policy_type=policy_type,
            framework_id=framework_id, db=db)
        return PolicyTemplatesResponse(templates=templates, total=len(
            templates))
    except Exception as e:
        logger.error(f'Failed to fetch policy templates: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to fetch policy templates')

@router.get('/metrics', response_model=PolicyGenerationMetrics, dependencies=
    [Depends(get_current_active_user)])
async def get_policy_generation_metrics(provider: Optional[str]=None,
    current_user: User=Depends(get_current_active_user), async_db:
    AsyncSession=Depends(get_async_db)) -> PolicyGenerationMetrics:
    """Get policy generation metrics and provider statistics."""
    try:
        generator = PolicyGenerator()
        metrics = await generator.get_generation_metrics(user_id=
            current_user['id'], provider=provider, db=async_db)
        return PolicyGenerationMetrics(**metrics)
    except Exception as e:
        logger.error(f'Failed to fetch policy generation metrics: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to fetch metrics')

@router.post('/validate-policy', dependencies=[Depends(get_current_active_user)
    ])
async def validate_policy(policy_content: str, policy_type: str,
    current_user: User=Depends(get_current_active_user)) -> Dict[str, Any]:
    """Validate policy content for compliance and best practices."""
    try:
        generator = PolicyGenerator()
        validation_result = await generator.validate_policy(policy_content
            =policy_content, policy_type=policy_type)
        return validation_result
    except Exception as e:
        logger.error(f'Policy validation failed: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Policy validation failed')

@router.get('/provider-status', dependencies=[Depends(get_current_active_user)])
async def get_provider_status(current_user: User=Depends(
    get_current_active_user)) -> Dict[str, Any]:
    """Get current status of AI providers (OpenAI and Gemini)."""
    try:
        generator = PolicyGenerator()
        status = await generator.get_provider_status()
        return status
    except Exception as e:
        logger.error(f'Failed to fetch provider status: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to fetch provider status')