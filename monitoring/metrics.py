"""
Custom Metrics Collection and Business KPIs for RuleIQ

Provides comprehensive metrics tracking for:
- Business metrics (users, assessments, compliance scores)
- Performance metrics (response times, throughput)
- Resource utilization (CPU, memory, database)
- AI usage and costs
"""
from __future__ import annotations

import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Deque
from enum import Enum

from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.core import CollectorRegistry
from fastapi import Response
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from database import User, Assessment, BusinessProfile, Policy
from database.db_setup import get_async_db

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of metrics collected."""
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


@dataclass
class BusinessMetrics:
    """Business KPI metrics."""
    timestamp: datetime
    total_users: int
    active_users_daily: int
    active_users_weekly: int
    active_users_monthly: int
    total_assessments: int
    assessments_today: int
    assessments_week: int
    assessments_month: int
    average_compliance_score: float
    policies_generated: int
    policies_generated_today: int
    evidence_documents: int
    ai_requests_total: int
    ai_requests_today: int
    ai_cost_today: float
    ai_cost_month: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result["timestamp"] = self.timestamp.isoformat()
        return result


@dataclass
class PerformanceMetrics:
    """Application performance metrics."""
    timestamp: datetime
    avg_response_time_ms: float
    p50_response_time_ms: float
    p95_response_time_ms: float
    p99_response_time_ms: float
    requests_per_second: float
    error_rate: float
    success_rate: float
    active_connections: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result["timestamp"] = self.timestamp.isoformat()
        return result


class MetricsCollector:
    """Centralized metrics collection and management."""
    
    def __init__(self):
        """Initialize metrics collector with Prometheus metrics."""
        # Create a custom registry
        self.registry = CollectorRegistry()
        
        # Request metrics
        self.request_counter = Counter(
            'ruleiq_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status'],
            registry=self.registry
        )
        
        self.request_duration = Histogram(
            'ruleiq_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint'],
            registry=self.registry
        )
        
        # Business metrics
        self.user_gauge = Gauge(
            'ruleiq_users_total',
            'Total number of users',
            registry=self.registry
        )
        
        self.active_users_gauge = Gauge(
            'ruleiq_active_users',
            'Number of active users',
            ['period'],
            registry=self.registry
        )
        
        self.assessment_counter = Counter(
            'ruleiq_assessments_total',
            'Total number of assessments',
            registry=self.registry
        )
        
        self.compliance_score_gauge = Gauge(
            'ruleiq_average_compliance_score',
            'Average compliance score across all assessments',
            registry=self.registry
        )
        
        self.policy_counter = Counter(
            'ruleiq_policies_generated_total',
            'Total number of policies generated',
            registry=self.registry
        )
        
        # AI metrics
        self.ai_request_counter = Counter(
            'ruleiq_ai_requests_total',
            'Total number of AI requests',
            ['model', 'endpoint'],
            registry=self.registry
        )
        
        self.ai_cost_counter = Counter(
            'ruleiq_ai_cost_dollars',
            'Total AI cost in dollars',
            ['model'],
            registry=self.registry
        )
        
        self.ai_response_time = Histogram(
            'ruleiq_ai_response_time_seconds',
            'AI response time in seconds',
            ['model', 'endpoint'],
            registry=self.registry
        )
        
        # Database metrics
        self.db_connection_gauge = Gauge(
            'ruleiq_database_connections',
            'Number of database connections',
            ['state'],  # active, idle, total
            registry=self.registry
        )
        
        self.db_query_duration = Histogram(
            'ruleiq_database_query_duration_seconds',
            'Database query duration in seconds',
            ['operation'],  # select, insert, update, delete
            registry=self.registry
        )
        
        # System metrics
        self.cpu_usage_gauge = Gauge(
            'ruleiq_cpu_usage_percent',
            'CPU usage percentage',
            registry=self.registry
        )
        
        self.memory_usage_gauge = Gauge(
            'ruleiq_memory_usage_bytes',
            'Memory usage in bytes',
            ['type'],  # used, available, percent
            registry=self.registry
        )
        
        self.disk_usage_gauge = Gauge(
            'ruleiq_disk_usage_bytes',
            'Disk usage in bytes',
            ['type'],  # used, available, percent
            registry=self.registry
        )
        
        # Error tracking
        self.error_counter = Counter(
            'ruleiq_errors_total',
            'Total number of errors',
            ['type', 'endpoint'],
            registry=self.registry
        )
        
        # Rate limiting metrics
        self.rate_limit_counter = Counter(
            'ruleiq_rate_limit_hits_total',
            'Total number of rate limit hits',
            ['endpoint'],
            registry=self.registry
        )
        
        # Cache metrics
        self.cache_hit_counter = Counter(
            'ruleiq_cache_hits_total',
            'Total number of cache hits',
            registry=self.registry
        )
        
        self.cache_miss_counter = Counter(
            'ruleiq_cache_misses_total',
            'Total number of cache misses',
            registry=self.registry
        )
        
        # Security metrics
        self.auth_attempt_counter = Counter(
            'ruleiq_auth_attempts_total',
            'Total number of authentication attempts',
            ['result'],  # success, failure
            registry=self.registry
        )
        
        self.security_event_counter = Counter(
            'ruleiq_security_events_total',
            'Total number of security events',
            ['type'],  # login, logout, password_reset, suspicious_activity
            registry=self.registry
        )
        
        # Application info
        self.app_info = Info(
            'ruleiq_app',
            'Application information',
            registry=self.registry
        )
        self.app_info.info({
            'version': settings.version,
            'environment': settings.environment,
            'app_name': settings.app_name,
        })
        
        # In-memory storage for recent metrics
        self.recent_requests: Deque[Dict[str, Any]] = deque(maxlen=1000)
        self.recent_errors: Deque[Dict[str, Any]] = deque(maxlen=100)
        self.business_metrics_history: Deque[BusinessMetrics] = deque(maxlen=100)
        self.performance_metrics_history: Deque[PerformanceMetrics] = deque(maxlen=100)
        
        # Response time buckets for percentile calculations
        self.response_times: Deque[float] = deque(maxlen=10000)
        
        # Metric aggregation intervals
        self.last_business_metrics_update = datetime.now(timezone.utc)
        self.last_performance_metrics_update = datetime.now(timezone.utc)
    
    def record_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        response_time: float,
        user_id: Optional[str] = None
    ) -> None:
        """Record an HTTP request."""
        # Update Prometheus metrics
        self.request_counter.labels(
            method=method,
            endpoint=endpoint,
            status=str(status_code)
        ).inc()
        
        self.request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(response_time)
        
        # Store in recent requests
        self.recent_requests.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "method": method,
            "endpoint": endpoint,
            "status_code": status_code,
            "response_time": response_time,
            "user_id": user_id
        })
        
        # Add to response time tracking
        self.response_times.append(response_time)
        
        # Track errors
        if status_code >= 400:
            error_type = "client_error" if status_code < 500 else "server_error"
            self.error_counter.labels(
                type=error_type,
                endpoint=endpoint
            ).inc()
            
            self.recent_errors.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "method": method,
                "endpoint": endpoint,
                "status_code": status_code,
                "error_type": error_type
            })
    
    def record_ai_request(
        self,
        model: str,
        endpoint: str,
        response_time: float,
        cost: float,
        tokens_used: int
    ) -> None:
        """Record an AI API request."""
        self.ai_request_counter.labels(
            model=model,
            endpoint=endpoint
        ).inc()
        
        self.ai_cost_counter.labels(model=model).inc(cost)
        
        self.ai_response_time.labels(
            model=model,
            endpoint=endpoint
        ).observe(response_time)
    
    def record_database_query(
        self,
        operation: str,
        duration: float
    ) -> None:
        """Record a database query."""
        self.db_query_duration.labels(operation=operation).observe(duration)
    
    def update_database_connections(
        self,
        active: int,
        idle: int,
        total: int
    ) -> None:
        """Update database connection metrics."""
        self.db_connection_gauge.labels(state='active').set(active)
        self.db_connection_gauge.labels(state='idle').set(idle)
        self.db_connection_gauge.labels(state='total').set(total)
    
    def record_cache_access(self, hit: bool) -> None:
        """Record a cache access."""
        if hit:
            self.cache_hit_counter.inc()
        else:
            self.cache_miss_counter.inc()
    
    def record_auth_attempt(self, success: bool) -> None:
        """Record an authentication attempt."""
        result = "success" if success else "failure"
        self.auth_attempt_counter.labels(result=result).inc()
    
    def record_security_event(self, event_type: str) -> None:
        """Record a security event."""
        self.security_event_counter.labels(type=event_type).inc()
    
    def record_rate_limit_hit(self, endpoint: str) -> None:
        """Record a rate limit hit."""
        self.rate_limit_counter.labels(endpoint=endpoint).inc()
    
    async def update_business_metrics(self, db: AsyncSession) -> BusinessMetrics:
        """Update business KPI metrics from database."""
        now = datetime.now(timezone.utc)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now - timedelta(days=30)
        
        # Get user metrics
        total_users = await db.scalar(select(func.count(User.id)))
        active_users_daily = await db.scalar(
            select(func.count(User.id)).where(User.last_login >= today_start)
        )
        active_users_weekly = await db.scalar(
            select(func.count(User.id)).where(User.last_login >= week_start)
        )
        active_users_monthly = await db.scalar(
            select(func.count(User.id)).where(User.last_login >= month_start)
        )
        
        # Get assessment metrics
        total_assessments = await db.scalar(select(func.count(Assessment.id)))
        assessments_today = await db.scalar(
            select(func.count(Assessment.id)).where(Assessment.created_at >= today_start)
        )
        assessments_week = await db.scalar(
            select(func.count(Assessment.id)).where(Assessment.created_at >= week_start)
        )
        assessments_month = await db.scalar(
            select(func.count(Assessment.id)).where(Assessment.created_at >= month_start)
        )
        
        # Get average compliance score
        avg_score = await db.scalar(
            select(func.avg(Assessment.compliance_score)).where(
                Assessment.compliance_score.isnot(None)
            )
        ) or 0.0
        
        # Get policy metrics
        policies_generated = await db.scalar(select(func.count(Policy.id)))
        policies_generated_today = await db.scalar(
            select(func.count(Policy.id)).where(Policy.created_at >= today_start)
        )
        
        # Create metrics object
        metrics = BusinessMetrics(
            timestamp=now,
            total_users=total_users or 0,
            active_users_daily=active_users_daily or 0,
            active_users_weekly=active_users_weekly or 0,
            active_users_monthly=active_users_monthly or 0,
            total_assessments=total_assessments or 0,
            assessments_today=assessments_today or 0,
            assessments_week=assessments_week or 0,
            assessments_month=assessments_month or 0,
            average_compliance_score=float(avg_score),
            policies_generated=policies_generated or 0,
            policies_generated_today=policies_generated_today or 0,
            evidence_documents=0,  # TODO: Implement evidence counting
            ai_requests_total=0,  # TODO: Get from AI cost monitoring
            ai_requests_today=0,  # TODO: Get from AI cost monitoring
            ai_cost_today=0.0,  # TODO: Get from AI cost monitoring
            ai_cost_month=0.0,  # TODO: Get from AI cost monitoring
        )
        
        # Update Prometheus gauges
        self.user_gauge.set(metrics.total_users)
        self.active_users_gauge.labels(period='daily').set(metrics.active_users_daily)
        self.active_users_gauge.labels(period='weekly').set(metrics.active_users_weekly)
        self.active_users_gauge.labels(period='monthly').set(metrics.active_users_monthly)
        self.compliance_score_gauge.set(metrics.average_compliance_score)
        
        # Store in history
        self.business_metrics_history.append(metrics)
        self.last_business_metrics_update = now
        
        return metrics
    
    def calculate_performance_metrics(self) -> PerformanceMetrics:
        """Calculate current performance metrics."""
        now = datetime.now(timezone.utc)
        
        if not self.response_times:
            return PerformanceMetrics(
                timestamp=now,
                avg_response_time_ms=0,
                p50_response_time_ms=0,
                p95_response_time_ms=0,
                p99_response_time_ms=0,
                requests_per_second=0,
                error_rate=0,
                success_rate=100,
                active_connections=0
            )
        
        # Calculate response time percentiles
        sorted_times = sorted(self.response_times)
        n = len(sorted_times)
        
        avg_time = sum(sorted_times) / n * 1000  # Convert to ms
        p50 = sorted_times[int(n * 0.5)] * 1000 if n > 0 else 0
        p95 = sorted_times[int(n * 0.95)] * 1000 if n > 0 else 0
        p99 = sorted_times[int(n * 0.99)] * 1000 if n > 0 else 0
        
        # Calculate request rate
        recent_requests = [r for r in self.recent_requests 
                          if datetime.fromisoformat(r['timestamp']) > now - timedelta(seconds=60)]
        requests_per_second = len(recent_requests) / 60.0
        
        # Calculate error rate
        errors = sum(1 for r in recent_requests if r['status_code'] >= 400)
        error_rate = (errors / len(recent_requests) * 100) if recent_requests else 0
        success_rate = 100 - error_rate
        
        metrics = PerformanceMetrics(
            timestamp=now,
            avg_response_time_ms=avg_time,
            p50_response_time_ms=p50,
            p95_response_time_ms=p95,
            p99_response_time_ms=p99,
            requests_per_second=requests_per_second,
            error_rate=error_rate,
            success_rate=success_rate,
            active_connections=0  # TODO: Get from connection tracking
        )
        
        # Store in history
        self.performance_metrics_history.append(metrics)
        self.last_performance_metrics_update = now
        
        return metrics
    
    def update_system_metrics(self) -> None:
        """Update system resource metrics."""
        try:
            import psutil
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.cpu_usage_gauge.set(cpu_percent)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.memory_usage_gauge.labels(type='used').set(memory.used)
            self.memory_usage_gauge.labels(type='available').set(memory.available)
            self.memory_usage_gauge.labels(type='percent').set(memory.percent)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            self.disk_usage_gauge.labels(type='used').set(disk.used)
            self.disk_usage_gauge.labels(type='available').set(disk.free)
            self.disk_usage_gauge.labels(type='percent').set(disk.percent)
            
        except ImportError:
            logger.warning("psutil not installed, system metrics unavailable")
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")
    
    def get_prometheus_metrics(self) -> bytes:
        """Get metrics in Prometheus format."""
        return generate_latest(self.registry)
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of all current metrics."""
        # Get latest business metrics
        business_metrics = (
            self.business_metrics_history[-1].to_dict() 
            if self.business_metrics_history 
            else {}
        )
        
        # Get latest performance metrics
        performance_metrics = (
            self.performance_metrics_history[-1].to_dict()
            if self.performance_metrics_history
            else {}
        )
        
        # Calculate cache hit rate
        cache_hits = self.cache_hit_counter._value.get()
        cache_misses = self.cache_miss_counter._value.get()
        cache_total = cache_hits + cache_misses
        cache_hit_rate = (cache_hits / cache_total * 100) if cache_total > 0 else 0
        
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "business": business_metrics,
            "performance": performance_metrics,
            "cache": {
                "hit_rate": cache_hit_rate,
                "total_hits": cache_hits,
                "total_misses": cache_misses
            },
            "recent_errors": list(self.recent_errors)[-10:],  # Last 10 errors
            "environment": {
                "version": settings.version,
                "environment": settings.environment,
                "debug": settings.debug
            }
        }


# Global metrics collector instance
_metrics_collector: Optional[MetricsCollector] = None


def get_metrics_collector() -> MetricsCollector:
    """Get or create the global metrics collector instance."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


async def start_metrics_background_tasks() -> None:
    """Start background tasks for periodic metrics updates."""
    collector = get_metrics_collector()
    
    async def update_business_metrics_task():
        """Periodically update business metrics."""
        while True:
            try:
                async for db in get_async_db():
                    await collector.update_business_metrics(db)
                    break
            except Exception as e:
                logger.error(f"Error updating business metrics: {e}")
            
            await asyncio.sleep(300)  # Update every 5 minutes
    
    async def update_system_metrics_task():
        """Periodically update system metrics."""
        while True:
            try:
                collector.update_system_metrics()
            except Exception as e:
                logger.error(f"Error updating system metrics: {e}")
            
            await asyncio.sleep(30)  # Update every 30 seconds
    
    async def update_performance_metrics_task():
        """Periodically calculate performance metrics."""
        while True:
            try:
                collector.calculate_performance_metrics()
            except Exception as e:
                logger.error(f"Error calculating performance metrics: {e}")
            
            await asyncio.sleep(60)  # Update every minute
    
    # Start background tasks
    asyncio.create_task(update_business_metrics_task())
    asyncio.create_task(update_system_metrics_task())
    asyncio.create_task(update_performance_metrics_task())


def create_metrics_endpoint() -> Response:
    """Create a FastAPI response with Prometheus metrics."""
    collector = get_metrics_collector()
    metrics_data = collector.get_prometheus_metrics()
    return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)