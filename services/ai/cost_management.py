"""
AI Cost Management and Monitoring System

Comprehensive cost tracking, budgeting, optimization, and reporting for AI services.
Tracks token usage, calculates costs, monitors budgets, and provides optimization recommendations.
"""
from __future__ import annotations
import statistics
from datetime import datetime, date, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import time
from redis.asyncio import Redis
from config.logging_config import get_logger
import redis
from config.settings import settings

logger = get_logger(__name__)

# Pricing per 1K tokens (in USD)
MODEL_PRICING = {
    'gpt-4': {'input': 0.03, 'output': 0.06},
    'gpt-4-32k': {'input': 0.06, 'output': 0.12},
    'gpt-3.5-turbo': {'input': 0.0015, 'output': 0.002},
    'gpt-3.5-turbo-16k': {'input': 0.003, 'output': 0.004},
    'text-embedding-ada-002': {'input': 0.0001, 'output': 0},
    'claude-3-opus': {'input': 0.015, 'output': 0.075},
    'claude-3-sonnet': {'input': 0.003, 'output': 0.015},
    'claude-3-haiku': {'input': 0.00025, 'output': 0.00125},
    'gemini-pro': {'input': 0.00025, 'output': 0.0005},
    'gemini-pro-vision': {'input': 0.00025, 'output': 0.0005}
}

class AIService(Enum):
    """AI service providers."""
    OPENAI = 'openai'
    ANTHROPIC = 'anthropic'
    GOOGLE = 'google'
    COHERE = 'cohere'
    CUSTOM = 'custom'

@dataclass
class CostEntry:
    """Individual cost entry for tracking AI usage."""
    timestamp: datetime
    user_id: str
    service: AIService
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: Decimal
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    response_quality_score: Optional[float] = None
    response_time_ms: Optional[float] = None
    cache_hit: bool = False
    error_occurred: bool = False
    metadata: Optional[Dict[str, Any]] = field(default_factory=dict)

@dataclass
class BudgetConfig:
    """Budget configuration for a user or organization."""
    monthly_budget_usd: Decimal
    alert_threshold_percent: int = 75
    email_notifications: bool = True
    webhook_url: Optional[str] = None
    daily_limit_usd: Optional[Decimal] = None
    auto_pause_on_exceed: bool = False
    cost_breakdown_by_service: bool = True
    cost_breakdown_by_model: bool = True

class AICostManager:
    """
    Central manager for AI cost tracking and management.
    
    Features:
    - Real-time cost tracking
    - Budget monitoring and alerts
    - Usage analytics
    - Cost optimization recommendations
    - Multi-service support
    """
    
    def __init__(self, redis_client: Optional[Redis] = None):
        """Initialize cost manager with optional Redis for caching."""
        self.redis = redis_client
        self.costs: List[CostEntry] = []
        self.budgets: Dict[str, BudgetConfig] = {}
        self.cache_hits = defaultdict(int)
        self.cache_misses = defaultdict(int)
        
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int
        ) -> Decimal:
        """Calculate cost for token usage."""
        if model not in MODEL_PRICING:
            logger.warning(f'Unknown model: {model}, using default pricing')
            model = 'gpt-3.5-turbo'
        pricing = MODEL_PRICING[model]
        input_cost = Decimal(str(pricing['input'])) * Decimal(input_tokens
            ) / Decimal(1000)
        output_cost = Decimal(str(pricing['output'])) * Decimal(output_tokens
            ) / Decimal(1000)
        return input_cost + output_cost
    
    def track_usage(self, user_id: str, service: AIService, model: str,
        input_tokens: int, output_tokens: int, **kwargs) -> CostEntry:
        """Track AI usage and calculate cost."""
        cost = self.calculate_cost(model, input_tokens, output_tokens)
        entry = CostEntry(timestamp=datetime.now(datetime.timezone.utc),
            user_id=user_id, service=service, model=model, input_tokens=
            input_tokens, output_tokens=output_tokens, cost_usd=cost, **kwargs
            )
        self.costs.append(entry)
        if kwargs.get('cache_hit'):
            self.cache_hits[model] += 1
        else:
            self.cache_misses[model] += 1
        return entry
    
    def get_user_costs(self, user_id: str, start_date: Optional[datetime]=
        None, end_date: Optional[datetime]=None) -> List[CostEntry]:
        """Get costs for a specific user within a date range."""
        costs = [c for c in self.costs if c.user_id == user_id]
        if start_date:
            costs = [c for c in costs if c.timestamp >= start_date]
        if end_date:
            costs = [c for c in costs if c.timestamp <= end_date]
        return costs
    
    def calculate_total_cost(self, entries: List[CostEntry]) -> Decimal:
        """Calculate total cost from a list of entries."""
        return sum(e.cost_usd for e in entries)
    
    def get_cost_by_model(self, entries: List[CostEntry]) -> Dict[str, Decimal
        ]:
        """Group costs by model."""
        costs_by_model = defaultdict(Decimal)
        for entry in entries:
            costs_by_model[entry.model] += entry.cost_usd
        return dict(costs_by_model)
    
    def get_cost_by_service(self, entries: List[CostEntry]) -> Dict[str, 
        Decimal]:
        """Group costs by service."""
        costs_by_service = defaultdict(Decimal)
        for entry in entries:
            costs_by_service[entry.service.value] += entry.cost_usd
        return dict(costs_by_service)
    
    def get_daily_costs(self, entries: List[CostEntry]) -> Dict[date, Decimal]:
        """Group costs by day."""
        daily_costs = defaultdict(Decimal)
        for entry in entries:
            day = entry.timestamp.date()
            daily_costs[day] += entry.cost_usd
        return dict(daily_costs)
    
    def calculate_efficiency_metrics(self, entries: List[CostEntry]) -> Dict[
        str, Any]:
        """Calculate efficiency metrics from cost entries."""
        if not entries:
            return {'cache_hit_rate': 0, 'average_response_time_ms': 0,
                'error_rate': 0, 'average_quality_score': 0}
        cache_hits = sum(1 for e in entries if e.cache_hit)
        total_entries = len(entries)
        response_times = [e.response_time_ms for e in entries if e.
            response_time_ms is not None]
        quality_scores = [e.response_quality_score for e in entries if e.
            response_quality_score is not None]
        errors = sum(1 for e in entries if e.error_occurred)
        return {'cache_hit_rate': cache_hits / total_entries * 100 if
            total_entries > 0 else 0, 'average_response_time_ms': statistics
            .mean(response_times) if response_times else 0, 'error_rate':
            errors / total_entries * 100 if total_entries > 0 else 0,
            'average_quality_score': statistics.mean(quality_scores) if
            quality_scores else 0, 'total_cached_savings_usd': sum(e.
            cost_usd for e in entries if e.cache_hit)}
    
    def set_budget(self, user_id: str, config: BudgetConfig):
        """Set budget configuration for a user."""
        self.budgets[user_id] = config
    
    def check_budget_status(self, user_id: str) -> Dict[str, Any]:
        """Check current budget status for a user."""
        if user_id not in self.budgets:
            return {'has_budget': False, 'alert_triggered': False}
        budget = self.budgets[user_id]
        current_month = datetime.now(datetime.timezone.utc).replace(day=1,
            hour=0, minute=0, second=0, microsecond=0)
        monthly_costs = self.get_user_costs(user_id, start_date=current_month)
        total_spent = self.calculate_total_cost(monthly_costs)
        usage_percent = (total_spent / budget.monthly_budget_usd * 100 if
            budget.monthly_budget_usd > 0 else 0)
        alert_triggered = usage_percent >= budget.alert_threshold_percent
        if budget.daily_limit_usd:
            today_start = datetime.now(datetime.timezone.utc).replace(hour=0,
                minute=0, second=0, microsecond=0)
            daily_costs = self.get_user_costs(user_id, start_date=today_start)
            daily_spent = self.calculate_total_cost(daily_costs)
            daily_exceeded = daily_spent >= budget.daily_limit_usd
        else:
            daily_spent = Decimal('0')
            daily_exceeded = False
        return {'has_budget': True, 'monthly_budget_usd': budget.
            monthly_budget_usd, 'total_spent_usd': total_spent,
            'remaining_budget_usd': budget.monthly_budget_usd - total_spent,
            'usage_percent': float(usage_percent), 'alert_triggered':
            alert_triggered, 'daily_limit_usd': budget.daily_limit_usd,
            'daily_spent_usd': daily_spent, 'daily_limit_exceeded':
            daily_exceeded, 'auto_pause_enabled': budget.auto_pause_on_exceed,
            'should_pause': alert_triggered and budget.auto_pause_on_exceed}

class CostTrackingService:
    """Service for tracking and analyzing AI costs."""
    
    def __init__(self, manager: AICostManager):
        """Initialize with a cost manager."""
        self.manager = manager
    
    def track_usage(self, user_id: str, service_name: str, model_name: str,
        input_tokens: int, output_tokens: int, **kwargs) -> Dict[str, Any]:
        """Track AI usage and return tracking data."""
        try:
            service = AIService[service_name.upper()
                ] if service_name.upper() in AIService.__members__ else AIService.CUSTOM
        except:
            service = AIService.CUSTOM
        entry = self.manager.track_usage(user_id=user_id, service=service,
            model=model_name, input_tokens=input_tokens, output_tokens=
            output_tokens, **kwargs)
        budget_status = self.manager.check_budget_status(user_id)
        current_month = datetime.now(datetime.timezone.utc).replace(day=1,
            hour=0, minute=0, second=0, microsecond=0)
        monthly_costs = self.manager.get_user_costs(user_id, start_date=
            current_month)
        daily_spending = self.manager.calculate_total_cost([e for e in
            monthly_costs if e.timestamp.date() == datetime.now(datetime.
            timezone.utc).date()])
        days_in_month = 30
        days_passed = (datetime.now(datetime.timezone.utc) - current_month
            ).days + 1
        avg_daily = self.manager.calculate_total_cost(monthly_costs
            ) / days_passed if days_passed > 0 else Decimal('0')
        projected_monthly = avg_daily * days_in_month
        efficiency = entry.cost_usd * Decimal('0.2') if entry.cache_hit else Decimal(
            '1.0')
        return {'usage_id': f'{user_id}_{int(time.time() * 1000)}',
            'cost_usd': entry.cost_usd, 'efficiency_score': efficiency,
            'cost_per_token': entry.cost_usd / Decimal(input_tokens +
            output_tokens) if input_tokens + output_tokens > 0 else Decimal(
            '0'), 'cached_savings_usd': entry.cost_usd if entry.cache_hit else
            Decimal('0'), 'budget_usage_percent': Decimal(str(budget_status
            .get('usage_percent', 0))), 'daily_spending_usd': daily_spending,
            'projected_monthly_cost_usd': projected_monthly}
    
    def analyze_costs(self, user_id: str, start_date: datetime, end_date:
        datetime, group_by: str='service') -> Dict[str, Any]:
        """Analyze costs for a user over a period."""
        entries = self.manager.get_user_costs(user_id, start_date, end_date)
        total_cost = self.manager.calculate_total_cost(entries)
        days = (end_date - start_date).days + 1
        avg_daily = total_cost / days if days > 0 else Decimal('0')
        if group_by == 'service':
            breakdown = self.manager.get_cost_by_service(entries)
        elif group_by == 'model':
            breakdown = self.manager.get_cost_by_model(entries)
        elif group_by == 'date':
            daily_costs = self.manager.get_daily_costs(entries)
            breakdown = {str(k): v for k, v in daily_costs.items()}
        else:
            breakdown = {}
        return {'total_cost_usd': total_cost, 'average_daily_cost_usd':
            avg_daily, f'cost_by_{group_by}': breakdown, 'entry_count': len(
            entries), 'most_expensive_model': max(self.manager.
            get_cost_by_model(entries).items(), key=lambda x: x[1])[0] if
            entries else None}
    
    def analyze_trends(self, user_id: str, period_days: int=30) -> Dict[str,
        Any]:
        """Analyze cost trends over time."""
        end_date = datetime.now(datetime.timezone.utc)
        start_date = end_date - timedelta(days=period_days)
        entries = self.manager.get_user_costs(user_id, start_date, end_date)
        if not entries:
            return {'trend': 'no_data', 'percentage_change': 0}
        daily_costs = self.manager.get_daily_costs(entries)
        if len(daily_costs) < 2:
            return {'trend': 'insufficient_data', 'percentage_change': 0}
        costs_list = list(daily_costs.values())
        first_half = sum(costs_list[:len(costs_list) // 2])
        second_half = sum(costs_list[len(costs_list) // 2:])
        if first_half == 0:
            trend = 'increasing' if second_half > 0 else 'stable'
            change = 100 if second_half > 0 else 0
        else:
            change = ((second_half - first_half) / first_half * 100)
            if change > 10:
                trend = 'increasing'
            elif change < -10:
                trend = 'decreasing'
            else:
                trend = 'stable'
        return {'trend': trend, 'percentage_change': float(change),
            'daily_costs': {str(k): float(v) for k, v in daily_costs.items()}}
    
    def identify_cost_drivers(self, user_id: str, limit: int=5) -> List[Dict[
        str, Any]]:
        """Identify top cost driving activities."""
        current_month = datetime.now(datetime.timezone.utc).replace(day=1,
            hour=0, minute=0, second=0, microsecond=0)
        entries = self.manager.get_user_costs(user_id, start_date=current_month
            )
        model_costs = self.manager.get_cost_by_model(entries)
        top_models = sorted(model_costs.items(), key=lambda x: x[1],
            reverse=True)[:limit]
        return [{'model': model, 'total_cost_usd': float(cost),
            'usage_count': sum(1 for e in entries if e.model == model),
            'average_cost_per_use': float(cost / sum(1 for e in entries if
            e.model == model))} for model, cost in top_models]
    
    def calculate_efficiency_metrics(self, user_id: str, period_days: int=30
        ) -> Dict[str, Any]:
        """Calculate efficiency metrics for a user."""
        end_date = datetime.now(datetime.timezone.utc)
        start_date = end_date - timedelta(days=period_days)
        entries = self.manager.get_user_costs(user_id, start_date, end_date)
        return self.manager.calculate_efficiency_metrics(entries)
    
    def project_future_costs(self, user_id: str, forecast_days: int=30
        ) -> Dict[str, Decimal]:
        """Project future costs based on historical usage."""
        lookback_days = 30
        end_date = datetime.now(datetime.timezone.utc)
        start_date = end_date - timedelta(days=lookback_days)
        entries = self.manager.get_user_costs(user_id, start_date, end_date)
        if not entries:
            return {'next_week': Decimal('0'), 'next_month': Decimal('0'),
                'next_quarter': Decimal('0')}
        daily_avg = self.manager.calculate_total_cost(entries) / lookback_days
        return {'next_week': daily_avg * 7, 'next_month': daily_avg * 30,
            'next_quarter': daily_avg * 90}
    
    def get_usage_summary(self, user_id: str, period_days: int=30) -> Dict[
        str, Any]:
        """Get comprehensive usage summary."""
        end_date = datetime.now(datetime.timezone.utc)
        start_date = end_date - timedelta(days=period_days)
        entries = self.manager.get_user_costs(user_id, start_date, end_date)
        total_cost = self.manager.calculate_total_cost(entries)
        total_tokens = sum(e.input_tokens + e.output_tokens for e in entries)
        unique_models = set(e.model for e in entries)
        unique_services = set(e.service.value for e in entries)
        return {'period_days': period_days, 'total_cost_usd': float(
            total_cost), 'total_requests': len(entries), 'total_tokens':
            total_tokens, 'unique_models': len(unique_models),
            'unique_services': len(unique_services), 'most_used_model': max(
            self.manager.get_cost_by_model(entries).items(), key=lambda x:
            x[1])[0] if entries else None, 'efficiency_metrics': self.
            manager.calculate_efficiency_metrics(entries)}
    
    def compare_costs(self, user_id: str, services: List[str], models: List[
        str], period_days: int=30) -> Dict[str, Any]:
        """Compare costs across services and models."""
        end_date = datetime.now(datetime.timezone.utc)
        start_date = end_date - timedelta(days=period_days)
        entries = self.manager.get_user_costs(user_id, start_date, end_date)
        service_comparison = {}
        for service in services:
            service_entries = [e for e in entries if e.service.value.lower(
                ) == service.lower()]
            service_comparison[service] = {'total_cost': float(self.manager
                .calculate_total_cost(service_entries)), 'request_count':
                len(service_entries), 'average_cost': float(self.manager.
                calculate_total_cost(service_entries) / len(service_entries)
                if service_entries else 0)}
        model_comparison = {}
        for model in models:
            model_entries = [e for e in entries if e.model == model]
            model_comparison[model] = {'total_cost': float(self.manager.
                calculate_total_cost(model_entries)), 'request_count': len(
                model_entries), 'average_cost': float(self.manager.
                calculate_total_cost(model_entries) / len(model_entries) if
                model_entries else 0)}
        return {'service_comparison': service_comparison, 'model_comparison':
            model_comparison, 'period_days': period_days, 'total_entries':
            len(entries)}
    
    def export_data(self, user_id: str, format: str, period_days: int,
        include_details: bool) -> Dict[str, Any]:
        """Export cost data in various formats."""
        end_date = datetime.now(datetime.timezone.utc)
        start_date = end_date - timedelta(days=period_days)
        entries = self.manager.get_user_costs(user_id, start_date, end_date)
        expires_at = datetime.now(datetime.timezone.utc) + timedelta(hours=24)
        download_url = (
            f'/api/v1/ai/cost/download?user_id={user_id}&format={format}')
        return {'record_count': len(entries), 'download_url': download_url,
            'expires_at': expires_at.isoformat(), 'format': format}
    
    def get_service_metrics(self, user_id: str, service_name: str,
        period_days: int=7) -> Dict[str, Any]:
        """Get detailed metrics for a specific service."""
        end_date = datetime.now(datetime.timezone.utc)
        start_date = end_date - timedelta(days=period_days)
        entries = self.manager.get_user_costs(user_id, start_date, end_date)
        service_entries = [e for e in entries if e.service.value.lower() ==
            service_name.lower()]
        if not service_entries:
            return {'service': service_name, 'no_data': True}
        total_cost = self.manager.calculate_total_cost(service_entries)
        total_requests = len(service_entries)
        total_tokens = sum(e.input_tokens + e.output_tokens for e in
            service_entries)
        models_used = set(e.model for e in service_entries)
        daily_costs = self.manager.get_daily_costs(service_entries)
        response_times = [e.response_time_ms for e in service_entries if e
            .response_time_ms is not None]
        return {'service': service_name, 'period_days': period_days,
            'total_cost_usd': float(total_cost), 'total_requests':
            total_requests, 'total_tokens': total_tokens,
            'average_cost_per_request': float(total_cost / total_requests 
            if total_requests > 0 else 0), 'models_used': list(models_used),
            'daily_breakdown': {str(k): float(v) for k, v in daily_costs.
            items()}, 'average_response_time_ms': statistics.mean(
            response_times) if response_times else None, 'cache_hit_rate':
            sum(1 for e in service_entries if e.cache_hit) / len(
            service_entries) * 100 if service_entries else 0}

class BudgetAlertService:
    """Service for managing budget alerts and notifications."""
    
    def __init__(self, manager: AICostManager):
        """Initialize with a cost manager."""
        self.manager = manager
    
    def configure_alerts(self, user_id: str, monthly_budget_usd: float,
        alert_threshold_percent: int, email_notifications: bool,
        webhook_url: Optional[str], daily_limit_usd: Optional[float],
        auto_pause_on_exceed: bool) -> Dict[str, Any]:
        """Configure budget alerts for a user."""
        config = BudgetConfig(monthly_budget_usd=Decimal(str(
            monthly_budget_usd)), alert_threshold_percent=
            alert_threshold_percent, email_notifications=
            email_notifications, webhook_url=webhook_url, daily_limit_usd=
            Decimal(str(daily_limit_usd)) if daily_limit_usd else None,
            auto_pause_on_exceed=auto_pause_on_exceed)
        self.manager.set_budget(user_id, config)
        return {'monthly_budget_usd': float(config.monthly_budget_usd),
            'alert_threshold_percent': config.alert_threshold_percent,
            'email_notifications': config.email_notifications,
            'webhook_url': config.webhook_url, 'daily_limit_usd': float(
            config.daily_limit_usd) if config.daily_limit_usd else None,
            'auto_pause_on_exceed': config.auto_pause_on_exceed}
    
    def check_budget_status(self, user_id: str) -> Dict[str, Any]:
        """Check current budget status."""
        return self.manager.check_budget_status(user_id)
    
    def get_budget_status(self, user_id: str) -> Dict[str, Any]:
        """Get detailed budget status."""
        status = self.manager.check_budget_status(user_id)
        if not status['has_budget']:
            return {'configured': False, 'message': 'No budget configured'}
        current_month = datetime.now(datetime.timezone.utc).replace(day=1,
            hour=0, minute=0, second=0, microsecond=0)
        days_in_month = 30
        days_remaining = days_in_month - datetime.now(datetime.timezone.utc
            ).day
        if status['remaining_budget_usd'] > 0 and days_remaining > 0:
            recommended_daily = status['remaining_budget_usd'] / days_remaining
        else:
            recommended_daily = Decimal('0')
        return {'configured': True, 'monthly_budget_usd': float(status[
            'monthly_budget_usd']), 'spent_this_month_usd': float(status[
            'total_spent_usd']), 'remaining_budget_usd': float(status[
            'remaining_budget_usd']), 'usage_percentage': status[
            'usage_percent'], 'days_remaining': days_remaining,
            'recommended_daily_spend_usd': float(recommended_daily),
            'alert_active': status['alert_triggered'], 'daily_limit_usd':
            float(status['daily_limit_usd']) if status['daily_limit_usd'] else
            None, 'daily_spent_usd': float(status['daily_spent_usd']),
            'daily_limit_exceeded': status.get('daily_limit_exceeded', False)}
    
    def get_current_usage_percent(self, user_id: str) -> float:
        """Get current usage percentage."""
        status = self.manager.check_budget_status(user_id)
        return status.get('usage_percent', 0.0)
    
    def reset_budget_period(self, user_id: str) -> Dict[str, Any]:
        """Reset budget period (for testing/admin)."""
        current_month = datetime.now(datetime.timezone.utc).replace(day=1,
            hour=0, minute=0, second=0, microsecond=0)
        monthly_costs = self.manager.get_user_costs(user_id, start_date=
            current_month)
        summary = {'total_spent': float(self.manager.calculate_total_cost(
            monthly_costs)), 'request_count': len(monthly_costs)}
        self.manager.costs = [c for c in self.manager.costs if c.user_id !=
            user_id or c.timestamp < current_month]
        return {'period_start': current_month.isoformat(),
            'previous_summary': summary}

class CostOptimizationService:
    """Service for cost optimization recommendations."""
    
    def __init__(self, manager: AICostManager):
        """Initialize with a cost manager."""
        self.manager = manager
    
    def get_recommendations(self, user_id: str) -> List[Dict[str, Any]]:
        """Get cost optimization recommendations."""
        current_month = datetime.now(datetime.timezone.utc).replace(day=1,
            hour=0, minute=0, second=0, microsecond=0)
        entries = self.manager.get_user_costs(user_id, start_date=current_month
            )
        recommendations = []
        model_costs = self.manager.get_cost_by_model(entries)
        for model, cost in model_costs.items():
            if 'gpt-4' in model and cost > Decimal('10'):
                recommendations.append({'type': 'model_downgrade', 'current':
                    model, 'suggested': 'gpt-3.5-turbo', 'potential_savings':
                    float(cost * Decimal('0.9')), 'priority': 'high',
                    'description':
                    f'Consider using GPT-3.5 for simpler tasks instead of {model}'
                    })
        efficiency = self.manager.calculate_efficiency_metrics(entries)
        if efficiency['cache_hit_rate'] < 20:
            recommendations.append({'type': 'caching', 'current_hit_rate':
                efficiency['cache_hit_rate'], 'suggested_hit_rate': 40,
                'potential_savings': float(self.manager.calculate_total_cost(
                entries) * Decimal('0.2')), 'priority': 'medium',
                'description':
                'Implement better caching strategies to reduce API calls'})
        if efficiency['error_rate'] > 5:
            recommendations.append({'type': 'error_reduction', 'current_rate':
                efficiency['error_rate'], 'suggested_rate': 2,
                'potential_savings': float(self.manager.calculate_total_cost([
                e for e in entries if e.error_occurred])), 'priority': 'high',
                'description': 'Fix errors to avoid wasted API calls'})
        daily_costs = self.manager.get_daily_costs(entries)
        if daily_costs:
            avg_daily = sum(daily_costs.values()) / len(daily_costs)
            peak_daily = max(daily_costs.values())
            if peak_daily > avg_daily * Decimal('2'):
                recommendations.append({'type': 'usage_smoothing',
                    'peak_cost': float(peak_daily), 'average_cost': float(
                    avg_daily), 'potential_savings': float((peak_daily -
                    avg_daily) * 15), 'priority': 'low', 'description':
                    'Distribute usage more evenly to avoid peak charges'})
        return recommendations
    
    def analyze_cache_effectiveness(self, user_id: str) -> Dict[str, Any]:
        """Analyze cache effectiveness and potential improvements."""
        current_month = datetime.now(datetime.timezone.utc).replace(day=1,
            hour=0, minute=0, second=0, microsecond=0)
        entries = self.manager.get_user_costs(user_id, start_date=current_month
            )
        cache_hits = sum(1 for e in entries if e.cache_hit)
        total_requests = len(entries)
        hit_rate = cache_hits / total_requests * 100 if total_requests > 0 else 0
        cached_cost_savings = sum(e.cost_usd for e in entries if e.cache_hit)
        potential_additional_savings = sum(e.cost_usd for e in entries if
            not e.cache_hit) * Decimal('0.3')
        model_cache_rates = {}
        for model in set(e.model for e in entries):
            model_entries = [e for e in entries if e.model == model]
            model_hits = sum(1 for e in model_entries if e.cache_hit)
            model_cache_rates[model] = model_hits / len(model_entries
                ) * 100 if model_entries else 0
        return {'current_hit_rate': hit_rate, 'cache_hits': cache_hits,
            'total_requests': total_requests, 'current_savings_usd': float(
            cached_cost_savings), 'potential_additional_savings_usd': float(
            potential_additional_savings), 'model_cache_rates':
            model_cache_rates, 'recommendations': [
            'Implement request deduplication',
            'Use longer cache TTLs for stable responses',
            'Cache similar request patterns', 'Implement semantic caching']}
    
    def suggest_model_alternatives(self, user_id: str) -> Dict[str, Any]:
        """Suggest alternative models for cost optimization."""
        current_month = datetime.now(datetime.timezone.utc).replace(day=1,
            hour=0, minute=0, second=0, microsecond=0)
        entries = self.manager.get_user_costs(user_id, start_date=current_month
            )
        model_usage = {}
        for entry in entries:
            if entry.model not in model_usage:
                model_usage[entry.model] = {'count': 0, 'total_cost':
                    Decimal('0'), 'avg_tokens': 0}
            model_usage[entry.model]['count'] += 1
            model_usage[entry.model]['total_cost'] += entry.cost_usd
            model_usage[entry.model]['avg_tokens'] += (entry.input_tokens +
                entry.output_tokens)
        alternatives = {}
        for model, stats in model_usage.items():
            avg_tokens = stats['avg_tokens'] / stats['count'] if stats['count'
                ] > 0 else 0
            if 'gpt-4' in model:
                if avg_tokens < 2000:
                    alternatives[model] = {'current_model': model,
                        'suggested_model': 'gpt-3.5-turbo',
                        'reason': 'Short conversations', 'current_cost':
                        float(stats['total_cost']), 'projected_cost': float(
                        stats['total_cost'] * Decimal('0.1')),
                        'savings_percent': 90}
                else:
                    alternatives[model] = {'current_model': model,
                        'suggested_model': 'claude-3-sonnet',
                        'reason': 'Better price-performance for long context',
                        'current_cost': float(stats['total_cost']),
                        'projected_cost': float(stats['total_cost'] *
                        Decimal('0.2')), 'savings_percent': 80}
            elif 'claude-3-opus' in model:
                alternatives[model] = {'current_model': model,
                    'suggested_model': 'claude-3-haiku',
                    'reason': 'Similar quality at lower cost',
                    'current_cost': float(stats['total_cost']),
                    'projected_cost': float(stats['total_cost'] * Decimal(
                    '0.05')), 'savings_percent': 95}
        return {'current_models': list(model_usage.keys()), 'alternatives':
            alternatives, 'total_potential_savings': sum(alt[
            'current_cost'] - alt['projected_cost'] for alt in alternatives
            .values()) if alternatives else 0}
    
    def analyze_usage_patterns(self, user_id: str) -> Dict[str, Any]:
        """Analyze usage patterns for optimization opportunities."""
        lookback_days = 30
        end_date = datetime.now(datetime.timezone.utc)
        start_date = end_date - timedelta(days=lookback_days)
        entries = self.manager.get_user_costs(user_id, start_date, end_date)
        hourly_usage = defaultdict(int)
        daily_usage = defaultdict(int)
        for entry in entries:
            hour = entry.timestamp.hour
            day = entry.timestamp.strftime('%A')
            hourly_usage[hour] += 1
            daily_usage[day] += 1
        peak_hour = max(hourly_usage.items(), key=lambda x: x[1])[0
            ] if hourly_usage else None
        peak_day = max(daily_usage.items(), key=lambda x: x[1])[0
            ] if daily_usage else None
        off_peak_hours = [h for h, count in hourly_usage.items() if count <
            sum(hourly_usage.values()) / 24]
        session_patterns = defaultdict(list)
        for entry in entries:
            if entry.session_id:
                session_patterns[entry.session_id].append(entry)
        avg_session_length = (statistics.mean(len(sessions) for sessions in
            session_patterns.values()) if session_patterns else 0)
        return {'peak_usage_hour': peak_hour, 'peak_usage_day': peak_day,
            'off_peak_hours': off_peak_hours, 'hourly_distribution':
            dict(hourly_usage), 'daily_distribution': dict(daily_usage),
            'average_session_length': avg_session_length,
            'total_sessions': len(session_patterns), 'recommendations': [
            'Schedule batch processing during off-peak hours',
            'Implement request batching for similar queries',
            'Use queue-based processing for non-urgent tasks']}
    
    def calculate_potential_savings(self, user_id: str) -> Dict[str, Decimal]:
        """Calculate potential savings from all optimization strategies."""
        current_month = datetime.now(datetime.timezone.utc).replace(day=1,
            hour=0, minute=0, second=0, microsecond=0)
        entries = self.manager.get_user_costs(user_id, start_date=current_month
            )
        total_cost = self.manager.calculate_total_cost(entries)
        cache_savings = total_cost * Decimal('0.3')
        model_optimization_savings = total_cost * Decimal('0.4')
        error_reduction_savings = sum(e.cost_usd for e in entries if e.
            error_occurred)
        batch_processing_savings = total_cost * Decimal('0.1')
        total_savings = (cache_savings + model_optimization_savings +
            error_reduction_savings + batch_processing_savings)
        return {'total': total_savings, 'monthly': total_savings,
            'cache_optimization': cache_savings, 'model_selection':
            model_optimization_savings, 'error_reduction':
            error_reduction_savings, 'batch_processing':
            batch_processing_savings}
    
    def get_quick_suggestions(self, user_id: str, service_name: str,
        model_name: str) -> List[str]:
        """Get quick optimization suggestions for current usage."""
        suggestions = []
        if 'gpt-4' in model_name:
            suggestions.append('Consider GPT-3.5 for simpler tasks')
        if 'opus' in model_name:
            suggestions.append('Try Claude Haiku for cost savings')
        current_month = datetime.now(datetime.timezone.utc).replace(day=1,
            hour=0, minute=0, second=0, microsecond=0)
        recent_entries = self.manager.get_user_costs(user_id, start_date=
            current_month)
        recent_similar = [e for e in recent_entries[-10:] if e.model ==
            model_name]
        if len(recent_similar) >= 3:
            suggestions.append('Consider batching similar requests')
        return suggestions
    
    def identify_opportunities(self, user_id: str) -> List[Dict[str, Any]]:
        """Identify all optimization opportunities."""
        opportunities = []
        recommendations = self.get_recommendations(user_id)
        for rec in recommendations:
            opportunities.append({'opportunity': rec['description'], 'type':
                rec['type'], 'potential_savings': rec.get(
                'potential_savings', 0), 'priority': rec['priority'],
                'implementation': 'automated' if rec['type'] in ['caching',
                'model_downgrade'] else 'manual'})
        return opportunities
    
    def simulate_cost(self, service_name: str, model_name: str,
        estimated_requests: int, avg_input_tokens: int, avg_output_tokens:
        int, cache_hit_rate: float, period_days: int) -> Dict[str, Any]:
        """Simulate costs for planned usage."""
        cost_per_request = self.manager.calculate_cost(model_name,
            avg_input_tokens, avg_output_tokens)
        total_requests = estimated_requests * period_days
        cached_requests = int(total_requests * cache_hit_rate)
        non_cached_requests = total_requests - cached_requests
        non_cached_cost = cost_per_request * non_cached_requests
        cached_cost = cost_per_request * cached_requests * Decimal('0.1')
        total_cost = non_cached_cost + cached_cost
        daily_cost = total_cost / period_days if period_days > 0 else Decimal(
            '0')
        monthly_cost = daily_cost * 30
        return {'service': service_name, 'model': model_name,
            'period_days': period_days, 'total_requests': total_requests,
            'cached_requests': cached_requests, 'cache_hit_rate':
            cache_hit_rate, 'estimated_total_cost_usd': float(total_cost),
            'estimated_daily_cost_usd': float(daily_cost),
            'estimated_monthly_cost_usd': float(monthly_cost),
            'cost_per_request': float(cost_per_request),
            'savings_from_cache': float(non_cached_cost * Decimal(str(
            cache_hit_rate)) * Decimal('0.9'))}