"""
AI Cost Monitoring API Router

Provides endpoints for AI cost tracking, budget management, optimization insights,
and real-time monitoring of AI service usage and expenses.
"""
from __future__ import annotations
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from api.dependencies.auth import get_current_active_user
from database.user import User
from api.middleware.rate_limiter import RateLimited
from services.ai.cost_management import AICostManager, CostTrackingService, BudgetAlertService, CostOptimizationService
from config.logging_config import get_logger

# Constants
DEFAULT_LIMIT = 100

logger = get_logger(__name__)
router = APIRouter(tags=['AI Cost Management'])

class CostTrackingRequest(BaseModel):
    """Request model for tracking AI usage costs."""
    service_name: str = Field(..., description='Name of the AI service')
    model_name: str = Field(..., description='AI model used')
    input_tokens: int = Field(..., ge=0, description='Number of input tokens')
    output_tokens: int = Field(..., ge=0, description='Number of output tokens'
        )
    session_id: Optional[str] = Field(None, description='Session identifier')
    request_id: Optional[str] = Field(None, description='Request identifier')
    response_quality_score: Optional[float] = Field(None, ge=0, le=1,
        description='Response quality score (0-1)')
    response_time_ms: Optional[float] = Field(None, ge=0, description=
        'Response time in milliseconds')
    cache_hit: bool = Field(False, description=
        'Whether response was served from cache')
    error_occurred: bool = Field(False, description='Whether an error occurred'
        )
    metadata: Optional[Dict[str, Any]] = Field(None, description=
        'Additional metadata')

class CostTrackingResponse(BaseModel):
    """Response model for cost tracking."""
    usage_id: str = Field(..., description='Unique usage identifier')
    cost_usd: Decimal = Field(..., description='Cost in USD')
    efficiency_score: Decimal = Field(..., description='Efficiency score')
    cost_per_token: Decimal = Field(..., description='Cost per token')
    cached_savings_usd: Decimal = Field(..., description='Savings from caching')
    budget_usage_percent: Decimal = Field(..., description=
        'Budget usage percentage')
    daily_spending_usd: Decimal = Field(..., description='Daily spending')
    projected_monthly_cost_usd: Decimal = Field(..., description=
        'Projected monthly cost')
    alert_triggered: bool = Field(..., description='Whether budget alert triggered'
        )
    optimization_suggestions: List[str] = Field(default_factory=list,
        description='Cost optimization suggestions')

class CostAnalysisResponse(BaseModel):
    """Response model for cost analysis."""
    period_start: datetime = Field(..., description='Analysis period start')
    period_end: datetime = Field(..., description='Analysis period end')
    total_cost_usd: Decimal = Field(..., description='Total cost in period')
    average_daily_cost_usd: Decimal = Field(..., description='Average daily cost')
    cost_by_service: Dict[str, Decimal] = Field(default_factory=dict,
        description='Cost breakdown by service')
    cost_by_model: Dict[str, Decimal] = Field(default_factory=dict, description
        ='Cost breakdown by model')
    top_cost_drivers: List[Dict[str, Any]] = Field(default_factory=list,
        description='Top cost driving activities')
    efficiency_metrics: Dict[str, Any] = Field(default_factory=dict,
        description='Efficiency metrics')
    trend_analysis: Dict[str, Any] = Field(default_factory=dict, description=
        'Cost trend analysis')
    optimization_opportunities: List[Dict[str, Any]] = Field(default_factory=
        list, description='Optimization opportunities')
    projected_costs: Dict[str, Decimal] = Field(default_factory=dict,
        description='Projected future costs')

class BudgetAlertConfig(BaseModel):
    """Configuration model for budget alerts."""
    monthly_budget_usd: Decimal = Field(..., gt=0, description=
        'Monthly budget in USD')
    alert_threshold_percent: int = Field(75, ge=50, le=100, description=
        'Alert threshold percentage')
    email_notifications: bool = Field(True, description=
        'Enable email notifications')
    webhook_url: Optional[str] = Field(None, description=
        'Webhook URL for alerts')
    daily_limit_usd: Optional[Decimal] = Field(None, gt=0, description=
        'Daily spending limit')
    auto_pause_on_exceed: bool = Field(False, description=
        'Auto-pause AI services on budget exceed')

class CostOptimizationResponse(BaseModel):
    """Response model for cost optimization recommendations."""
    total_potential_savings_usd: Decimal = Field(..., description=
        'Total potential savings')
    recommendations: List[Dict[str, Any]] = Field(default_factory=list,
        description='Optimization recommendations')
    cache_optimization: Dict[str, Any] = Field(default_factory=dict,
        description='Cache optimization details')
    model_optimization: Dict[str, Any] = Field(default_factory=dict,
        description='Model selection optimization')
    usage_patterns: Dict[str, Any] = Field(default_factory=dict, description=
        'Usage pattern analysis')
    estimated_monthly_savings: Decimal = Field(..., description=
        'Estimated monthly savings')
cost_manager = AICostManager()
cost_tracking_service = CostTrackingService(cost_manager)
budget_alert_service = BudgetAlertService(cost_manager)
cost_optimization_service = CostOptimizationService(cost_manager)

@router.post('/track', response_model=CostTrackingResponse, summary=
    'Track AI Usage Cost', description=
    'Track cost for a single AI service usage and receive budget alerts')
async def track_ai_cost(request: CostTrackingRequest, current_user: User=
    Depends(get_current_active_user)) -> CostTrackingResponse:
    """Track AI usage cost with budget monitoring and optimization insights."""
    try:
        cost_data = cost_tracking_service.track_usage(user_id=current_user[
            'id'], service_name=request.service_name, model_name=request.
            model_name, input_tokens=request.input_tokens, output_tokens=
            request.output_tokens, session_id=request.session_id,
            request_id=request.request_id, response_quality_score=request.
            response_quality_score, response_time_ms=request.response_time_ms,
            cache_hit=request.cache_hit, error_occurred=request.
            error_occurred, metadata=request.metadata)
        budget_status = budget_alert_service.check_budget_status(user_id=
            current_user['id'])
        optimization_suggestions = (cost_optimization_service.
            get_quick_suggestions(user_id=current_user['id'], service_name
            =request.service_name, model_name=request.model_name))
        return CostTrackingResponse(**cost_data, alert_triggered=
            budget_status['alert_triggered'], optimization_suggestions=
            optimization_suggestions)
    except Exception as e:
        logger.error(f'Error tracking AI cost: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to track AI cost')

@router.get('/analysis', response_model=CostAnalysisResponse, summary=
    'Analyze AI Costs', dependencies=[Depends(RateLimited(requests=20, window=
    60))], description='Get detailed cost analysis for specified period')
async def analyze_costs(period_days: int=Query(30, ge=1, le=365,
    description='Analysis period in days'), group_by: str=Query('service',
    regex='^(service|model|date|session)$'), current_user: User=Depends(
    get_current_active_user)) -> CostAnalysisResponse:
    """Get comprehensive cost analysis with trends and breakdowns."""
    try:
        end_date = datetime.now(datetime.timezone.utc)
        start_date = end_date - timedelta(days=period_days)
        analysis = cost_tracking_service.analyze_costs(user_id=current_user[
            'id'], start_date=start_date, end_date=end_date, group_by=group_by
            )
        trend_analysis = cost_tracking_service.analyze_trends(user_id=
            current_user['id'], period_days=period_days)
        cost_drivers = cost_tracking_service.identify_cost_drivers(user_id
            =current_user['id'], limit=5)
        efficiency_metrics = cost_tracking_service.calculate_efficiency_metrics(
            user_id=current_user['id'], period_days=period_days)
        opportunities = cost_optimization_service.identify_opportunities(
            user_id=current_user['id'])
        projections = cost_tracking_service.project_future_costs(user_id=
            current_user['id'], forecast_days=30)
        return CostAnalysisResponse(period_start=start_date, period_end=
            end_date, **analysis, top_cost_drivers=cost_drivers,
            efficiency_metrics=efficiency_metrics, trend_analysis=
            trend_analysis, optimization_opportunities=opportunities,
            projected_costs=projections)
    except Exception as e:
        logger.error(f'Error analyzing costs: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to analyze costs')

@router.get('/usage-summary', summary='Get Usage Summary', dependencies=[
    Depends(RateLimited(requests=30, window=60))], description=
    'Get summary of AI service usage and costs')
async def get_usage_summary(period: str=Query('month', regex=
    '^(day|week|month|year)$'), current_user: User=Depends(
    get_current_active_user)) -> Dict[str, Any]:
    """Get AI usage summary for specified period."""
    try:
        period_days = {'day': 1, 'week': 7, 'month': 30, 'year': 365}[period]
        summary = cost_tracking_service.get_usage_summary(user_id=
            current_user['id'], period_days=period_days)
        return summary
    except Exception as e:
        logger.error(f'Error getting usage summary: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to get usage summary')

@router.post('/budget-alert', summary='Configure Budget Alerts', description
    ='Configure budget alerts and spending limits')
async def configure_budget_alerts(config: BudgetAlertConfig, current_user:
    User=Depends(get_current_active_user)) -> Dict[str, Any]:
    """Configure budget alerts and automated actions."""
    try:
        result = budget_alert_service.configure_alerts(user_id=current_user[
            'id'], monthly_budget_usd=float(config.monthly_budget_usd),
            alert_threshold_percent=config.alert_threshold_percent,
            email_notifications=config.email_notifications, webhook_url=
            config.webhook_url, daily_limit_usd=float(config.daily_limit_usd
            ) if config.daily_limit_usd else None, auto_pause_on_exceed=
            config.auto_pause_on_exceed)
        return {'status': 'configured', 'config': result,
            'current_usage_percent': budget_alert_service.
            get_current_usage_percent(current_user['id'])}
    except Exception as e:
        logger.error(f'Error configuring budget alerts: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to configure budget alerts')

@router.get('/budget-status', summary='Get Budget Status', description=
    'Get current budget status and remaining allowance')
async def get_budget_status(current_user: User=Depends(
    get_current_active_user)) -> Dict[str, Any]:
    """Get current budget status with spending details."""
    try:
        status = budget_alert_service.get_budget_status(user_id=current_user[
            'id'])
        return status
    except Exception as e:
        logger.error(f'Error getting budget status: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to get budget status')

@router.get('/optimization', response_model=CostOptimizationResponse,
    summary='Get Cost Optimization Recommendations', dependencies=[Depends(
    RateLimited(requests=10, window=60))], description=
    'Get personalized cost optimization recommendations')
async def get_cost_optimization(current_user: User=Depends(
    get_current_active_user)) -> CostOptimizationResponse:
    """Get comprehensive cost optimization recommendations."""
    try:
        recommendations = cost_optimization_service.get_recommendations(
            user_id=current_user['id'])
        cache_optimization = (cost_optimization_service.
            analyze_cache_effectiveness(user_id=current_user['id']))
        model_optimization = cost_optimization_service.suggest_model_alternatives(
            user_id=current_user['id'])
        usage_patterns = cost_optimization_service.analyze_usage_patterns(
            user_id=current_user['id'])
        potential_savings = cost_optimization_service.calculate_potential_savings(
            user_id=current_user['id'])
        return CostOptimizationResponse(total_potential_savings_usd=Decimal(
            str(potential_savings['total'])), recommendations=
            recommendations, cache_optimization=cache_optimization,
            model_optimization=model_optimization, usage_patterns=
            usage_patterns, estimated_monthly_savings=Decimal(str(
            potential_savings['monthly'])))
    except Exception as e:
        logger.error(f'Error getting optimization recommendations: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to get optimization recommendations')

@router.post('/cost-comparison', summary='Compare Service Costs', description
    ='Compare costs across different AI services and models')
async def compare_service_costs(services: List[str]=Query(..., description=
    'List of services to compare'), models: List[str]=Query(..., description=
    'List of models to compare'), period_days: int=Query(30, ge=1, le=365),
    current_user: User=Depends(get_current_active_user)) -> Dict[str, Any]:
    """Compare costs across different AI services and models."""
    try:
        comparison = cost_tracking_service.compare_costs(user_id=
            current_user['id'], services=services, models=models,
            period_days=period_days)
        return comparison
    except Exception as e:
        logger.error(f'Error comparing costs: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to compare costs')

@router.get('/export', summary='Export Cost Data', dependencies=[Depends(
    RateLimited(requests=5, window=60))], description=
    'Export cost data in various formats')
async def export_cost_data(format: str=Query('csv', regex='^(csv|json|xlsx)$'
    ), period_days: int=Query(30, ge=1, le=365), include_details: bool=Query
    (False), current_user: User=Depends(get_current_active_user)) -> Dict[
    str, Any]:
    """Export cost data for external analysis."""
    try:
        export_data = cost_tracking_service.export_data(user_id=current_user[
            'id'], format=format, period_days=period_days, include_details
            =include_details)
        return {'format': format, 'period_days': period_days,
            'record_count': export_data['record_count'], 'download_url':
            export_data['download_url'], 'expires_at': export_data[
            'expires_at']}
    except Exception as e:
        logger.error(f'Error exporting cost data: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to export cost data')

@router.delete('/reset-budget', summary='Reset Budget Period', description=
    'Reset budget period and start fresh tracking')
async def reset_budget_period(confirm: bool=Query(False, description=
    'Confirm budget reset'), current_user: User=Depends(
    get_current_active_user)) -> Dict[str, Any]:
    """Reset budget period (admin only)."""
    if not confirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail
            ='Please confirm budget reset')
    try:
        result = budget_alert_service.reset_budget_period(user_id=
            current_user['id'])
        return {'status': 'reset', 'new_period_start': result['period_start'],
            'previous_period_summary': result['previous_summary']}
    except Exception as e:
        logger.error(f'Error resetting budget: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to reset budget')

@router.get('/service-metrics/{service_name}', summary=
    'Get Service-Specific Metrics', description=
    'Get detailed metrics for a specific AI service')
async def get_service_metrics(service_name: str, period_days: int=Query(7,
    ge=1, le=90), current_user: User=Depends(get_current_active_user)
    ) -> Dict[str, Any]:
    """Get detailed metrics for specific AI service."""
    try:
        metrics = cost_tracking_service.get_service_metrics(user_id=
            current_user['id'], service_name=service_name, period_days=
            period_days)
        return metrics
    except Exception as e:
        logger.error(f'Error getting service metrics: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to get service metrics')

@router.post('/simulate-cost', summary='Simulate Usage Cost', description=
    'Simulate cost for planned AI usage')
async def simulate_usage_cost(service_name: str, model_name: str,
    estimated_requests: int, avg_input_tokens: int, avg_output_tokens: int,
    cache_hit_rate: float=Query(0.0, ge=0.0, le=1.0), period_days: int=
    Query(30), current_user: User=Depends(get_current_active_user)) -> Dict[
    str, Any]:
    """Simulate costs for planned AI usage."""
    try:
        simulation = cost_optimization_service.simulate_cost(service_name=
            service_name, model_name=model_name, estimated_requests=
            estimated_requests, avg_input_tokens=avg_input_tokens,
            avg_output_tokens=avg_output_tokens, cache_hit_rate=
            cache_hit_rate, period_days=period_days)
        return simulation
    except Exception as e:
        logger.error(f'Error simulating cost: {e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Failed to simulate cost')