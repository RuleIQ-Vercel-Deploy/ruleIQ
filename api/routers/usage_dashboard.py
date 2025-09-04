"""
Usage Dashboard API for SMB owners.
Provides visibility into AI feature usage and remaining limits.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
from api.dependencies.auth import get_current_active_user, require_auth
from api.dependencies.database import get_async_db
from database.user import User
from database.rbac import AuditLog
from services.rate_limiting import RateLimitService
import json
import requests

router = APIRouter(tags=['Usage Dashboard'])

class UsageStats(BaseModel):
    """Usage statistics for a feature."""
    feature: str
    used_today: int
    daily_limit: int
    remaining: int
    reset_time: datetime

class UsageDashboard(BaseModel):
    """Complete usage dashboard response."""
    user_id: str
    current_plan: str
    features: List[UsageStats]
    total_api_calls_today: int
    last_updated: datetime

@router.get('/usage/dashboard', response_model=UsageDashboard, summary=
    'Get Usage Dashboard', description=
    'View current usage statistics and remaining limits')
async def get_usage_dashboard(current_user: User=Depends(
    get_current_active_user), db: AsyncSession=Depends(get_async_db)
    ) -> UsageDashboard:
    """Get usage dashboard for the current user."""
    user_id = current_user['id']
    rate_limiter = RateLimitService()
    feature_configs = {'ai_assessment': {'daily_limit': 50, 'feature_name':
        'AI Assessment Tools'}, 'policy_generation': {'daily_limit': 20,
        'feature_name': 'Policy Generation'}, 'evidence_analysis': {
        'daily_limit': 100, 'feature_name': 'Evidence Analysis'},
        'compliance_check': {'daily_limit': 30, 'feature_name':
        'Compliance Checks'}, 'report_generation': {'daily_limit': 10,
        'feature_name': 'Report Generation'}, 'iq_agent': {'daily_limit':
        100, 'feature_name': 'IQ Agent Chat'}}
    features = []
    total_api_calls = 0
    current_time = datetime.now(timezone.utc)
    today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0
        )
    tomorrow_start = today_start + timedelta(days=1)
    for action_type, config in feature_configs.items():
        usage_query = select(AuditLog).where(and_(AuditLog.user_id ==
            user_id, AuditLog.action == action_type, AuditLog.created_at >=
            today_start))
        result = await db.execute(usage_query)
        usage_logs = result.scalars().all()
        used_today = len(usage_logs)
        total_api_calls += used_today
        daily_limit = config['daily_limit']
        remaining = max(0, daily_limit - used_today)
        features.append(UsageStats(feature=config['feature_name'],
            used_today=used_today, daily_limit=daily_limit, remaining=
            remaining, reset_time=tomorrow_start))
    current_plan = 'Free Tier'
    if hasattr(current_user, 'subscription_plan'):
        current_plan = current_user.subscription_plan or 'Free Tier'
    return UsageDashboard(user_id=user_id, current_plan=current_plan,
        features=features, total_api_calls_today=total_api_calls,
        last_updated=current_time)

@router.get('/usage/history', summary='Get Usage History', description=
    'Get historical usage data for the past 30 days')
async def get_usage_history(days: int=30, current_user: User=Depends(
    get_current_active_user), db: AsyncSession=Depends(get_async_db)) -> Dict[
    str, Any]:
    """Get usage history for the specified number of days."""
    user_id = current_user['id']
    current_time = datetime.now(timezone.utc)
    start_date = current_time - timedelta(days=days)
    usage_query = select(AuditLog).where(and_(AuditLog.user_id == user_id,
        AuditLog.created_at >= start_date)).order_by(AuditLog.created_at.desc())
    result = await db.execute(usage_query)
    logs = result.scalars().all()
    daily_usage = {}
    feature_usage = {}
    for log in logs:
        date_key = log.created_at.strftime('%Y-%m-%d')
        if date_key not in daily_usage:
            daily_usage[date_key] = 0
        daily_usage[date_key] += 1
        if log.action not in feature_usage:
            feature_usage[log.action] = 0
        feature_usage[log.action] += 1
    return {'period': {'start': start_date.isoformat(), 'end':
        current_time.isoformat(), 'days': days}, 'daily_usage': daily_usage,
        'feature_usage': feature_usage, 'total_calls': len(logs),
        'average_daily_calls': len(logs) / days if days > 0 else 0}

@router.post('/usage/check-limit', summary='Check Feature Limit', description
    ='Check if a specific feature is within usage limits')
async def check_feature_limit(feature: str, current_user: User=Depends(
    get_current_active_user), db: AsyncSession=Depends(get_async_db)) -> Dict[
    str, Any]:
    """Check if a feature is within usage limits."""
    rate_limiter = RateLimitService()
    allowed, wait_time = await rate_limiter.check_rate_limit(user_id=
        current_user['id'], action_type=feature, db=db)
    if allowed:
        return {'allowed': True, 'message': f'{feature} is available',
            'wait_time': 0}
    else:
        return {'allowed': False, 'message':
            f'Rate limit exceeded for {feature}', 'wait_time': wait_time,
            'retry_after': datetime.now(timezone.utc) + timedelta(seconds=
            wait_time)}

@router.get('/usage/alerts', summary='Get Usage Alerts', description=
    'Get alerts when approaching usage limits')
async def get_usage_alerts(current_user: User=Depends(get_current_active_user
    ), db: AsyncSession=Depends(get_async_db)) -> List[Dict[str, Any]]:
    """Get usage alerts for features approaching limits."""
    user_id = current_user['id']
    alerts = []
    feature_configs = {'ai_assessment': 50, 'policy_generation': 20,
        'evidence_analysis': 100, 'compliance_check': 30,
        'report_generation': 10, 'iq_agent': 100}
    current_time = datetime.now(timezone.utc)
    today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0
        )
    for action_type, daily_limit in feature_configs.items():
        usage_query = select(AuditLog).where(and_(AuditLog.user_id ==
            user_id, AuditLog.action == action_type, AuditLog.created_at >=
            today_start))
        result = await db.execute(usage_query)
        usage_logs = result.scalars().all()
        used_today = len(usage_logs)
        usage_percentage = used_today / daily_limit * 100 if daily_limit > 0 else 0
        if usage_percentage >= 80:
            alerts.append({'feature': action_type, 'severity': 'high' if
                usage_percentage >= 90 else 'medium', 'message':
                f'{action_type} usage at {usage_percentage:.0f}%',
                'used': used_today, 'limit': daily_limit, 'percentage':
                usage_percentage})
    return alerts

@router.post('/usage/reset', summary='Reset Usage Tracking', description=
    'Admin endpoint to reset usage tracking (for testing)', include_in_schema
    =False)
async def reset_usage_tracking(feature: Optional[str]=None, current_user:
    User=Depends(get_current_active_user), db: AsyncSession=Depends(
    get_async_db)) -> Dict[str, str]:
    """Reset usage tracking for testing purposes (admin only)."""
    if not current_user.get('is_admin', False):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=
            'Admin access required')
    user_id = current_user['id']
    if feature:
        await db.execute(
            """DELETE FROM audit_logs 
               WHERE user_id = :user_id 
               AND action = :action
               AND created_at >= :today""", {'user_id': user_id, 'action':
            feature, 'today': datetime.now(timezone.utc).replace(hour=0,
            minute=0, second=0, microsecond=0)})
        await db.commit()
        return {'status': 'success', 'message': f'Reset usage for {feature}'}
    else:
        await db.execute(
            """DELETE FROM audit_logs 
               WHERE user_id = :user_id 
               AND created_at >= :today""", {'user_id': user_id, 'today':
            datetime.now(timezone.utc).replace(hour=0, minute=0, second=0,
            microsecond=0)})
        await db.commit()
        return {'status': 'success', 'message': 'Reset all usage tracking'}