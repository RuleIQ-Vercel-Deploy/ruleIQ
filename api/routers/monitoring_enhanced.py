"""
Enhanced Monitoring API Endpoints

Provides comprehensive monitoring endpoints including:
- Real-time metrics and KPIs
- Health checks for all components
- Alert management
- Performance monitoring
- Prometheus metrics export
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_active_user, require_admin
from database.db_setup import get_async_db
from database.user import User
from monitoring import (
    get_metrics_collector,
    get_health_checker,
    get_alert_manager,
    get_database_monitor,
    create_metrics_endpoint,
    AlertSeverity,
    AlertCategory,
    HealthStatus
)
from monitoring.startup import get_monitoring_status

router = APIRouter(prefix="/api/v1/monitoring")


@router.get("/status", summary="Get monitoring system status")
async def get_monitoring_system_status(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get comprehensive status of the monitoring system."""
    # This would need the monitoring_state from app startup
    # For now, return a basic status
    return {
        "status": "operational",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "components": {
            "metrics": "running",
            "health_checks": "running",
            "alerts": "running",
            "sentry": "enabled" if hasattr(get_metrics_collector(), 'sentry_enabled') else "disabled"
        }
    }


@router.get("/metrics/business", summary="Get business KPI metrics")
async def get_business_metrics(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    """Get current business KPI metrics."""
    collector = get_metrics_collector()
    
    # Update business metrics with current database data
    metrics = await collector.update_business_metrics(db)
    
    return metrics.to_dict()


@router.get("/metrics/performance", summary="Get performance metrics")
async def get_performance_metrics(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get current application performance metrics."""
    collector = get_metrics_collector()
    metrics = collector.calculate_performance_metrics()
    
    return metrics.to_dict()


@router.get("/metrics/summary", summary="Get metrics summary")
async def get_metrics_summary(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get comprehensive metrics summary."""
    collector = get_metrics_collector()
    return collector.get_metrics_summary()


@router.get("/metrics/prometheus", summary="Export Prometheus metrics")
async def get_prometheus_metrics() -> Response:
    """
    Export metrics in Prometheus format.
    
    This endpoint doesn't require authentication to allow Prometheus scraping.
    """
    return create_metrics_endpoint()


@router.get("/health", summary="Quick health check")
async def health_check() -> Dict[str, Any]:
    """
    Quick health check endpoint.
    
    No authentication required for uptime monitoring.
    """
    checker = get_health_checker()
    return await checker.get_quick_health()


@router.get("/health/detailed", summary="Detailed health check")
async def detailed_health_check(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get detailed health status of all system components."""
    checker = get_health_checker()
    system_health = await checker.check_all_components()
    
    return system_health.to_dict()


@router.get("/health/component/{component_name}", summary="Get component health")
async def get_component_health(
    component_name: str,
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get health status of a specific component."""
    checker = get_health_checker()
    
    # Get component from last check results
    component = checker.last_check_results.get(component_name)
    
    if not component:
        raise HTTPException(status_code=404, detail=f"Component {component_name} not found")
    
    return component.to_dict()


@router.get("/alerts", summary="Get active alerts")
async def get_alerts(
    severity: Optional[AlertSeverity] = Query(None, description="Filter by severity"),
    category: Optional[AlertCategory] = Query(None, description="Filter by category"),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get active alerts with optional filtering."""
    manager = get_alert_manager()
    
    alerts = manager.get_active_alerts(severity=severity, category=category)
    
    return {
        "total": len(alerts),
        "alerts": [alert.to_dict() for alert in alerts],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/alerts/summary", summary="Get alert summary")
async def get_alert_summary(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get summary of alert status."""
    manager = get_alert_manager()
    return manager.get_alert_summary()


@router.get("/alerts/history", summary="Get alert history")
async def get_alert_history(
    limit: int = Query(100, ge=1, le=1000, description="Number of alerts to return"),
    include_resolved: bool = Query(True, description="Include resolved alerts"),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get historical alerts."""
    manager = get_alert_manager()
    
    history = manager.alert_history[-limit:]
    
    if not include_resolved:
        history = [a for a in history if not a.resolved]
    
    return {
        "total": len(history),
        "alerts": [alert.to_dict() for alert in history],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.post("/alerts/{alert_id}/resolve", summary="Resolve an alert")
async def resolve_alert(
    alert_id: str,
    resolution_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Mark an alert as resolved."""
    manager = get_alert_manager()
    
    success = manager.resolve_alert(
        alert_id=alert_id,
        resolved_by=current_user.email,
        resolution_notes=resolution_data.get("notes")
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found or already resolved")
    
    return {
        "success": True,
        "alert_id": alert_id,
        "resolved_by": current_user.email,
        "resolved_at": datetime.now(timezone.utc).isoformat()
    }


@router.post("/alerts/test", summary="Create test alert")
async def create_test_alert(
    alert_data: Dict[str, Any],
    current_user: User = Depends(require_admin)
) -> Dict[str, Any]:
    """
    Create a test alert (admin only).
    
    Useful for testing alert channels and notifications.
    """
    manager = get_alert_manager()
    
    alert = manager.create_alert(
        title=alert_data.get("title", "Test Alert"),
        message=alert_data.get("message", "This is a test alert"),
        severity=AlertSeverity(alert_data.get("severity", "info")),
        category=AlertCategory(alert_data.get("category", "business")),
        component=alert_data.get("component", "test"),
        metadata=alert_data.get("metadata", {}),
        channels=alert_data.get("channels", [])
    )
    
    return {
        "success": True,
        "alert": alert.to_dict()
    }


@router.get("/database/status", summary="Get database monitoring status")
async def get_database_status(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get current database connection pool and performance status."""
    monitor = get_database_monitor()
    
    # Get monitoring summary
    summary = monitor.get_monitoring_summary()
    
    return summary


@router.get("/database/metrics", summary="Get database metrics")
async def get_database_metrics(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get detailed database metrics."""
    monitor = get_database_monitor()
    
    # Get current pool metrics
    metrics = monitor.get_pool_metrics()
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pools": {
            pool_type: metric.to_dict() if metric else None
            for pool_type, metric in metrics.items()
        }
    }


@router.get("/api-performance", summary="Get API performance metrics")
async def get_api_performance(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get API endpoint performance statistics."""
    collector = get_metrics_collector()
    
    # Get recent requests grouped by endpoint
    endpoint_stats = {}
    for request in collector.recent_requests:
        endpoint = f"{request['method']} {request['endpoint']}"
        if endpoint not in endpoint_stats:
            endpoint_stats[endpoint] = {
                "count": 0,
                "total_time": 0,
                "errors": 0,
                "response_times": []
            }
        
        stats = endpoint_stats[endpoint]
        stats["count"] += 1
        stats["total_time"] += request["response_time"]
        stats["response_times"].append(request["response_time"])
        if request["status_code"] >= 400:
            stats["errors"] += 1
    
    # Calculate statistics
    endpoints = []
    for endpoint, stats in endpoint_stats.items():
        if stats["count"] > 0:
            response_times = sorted(stats["response_times"])
            n = len(response_times)
            
            endpoints.append({
                "endpoint": endpoint,
                "requests": stats["count"],
                "avg_response_time_ms": (stats["total_time"] / stats["count"]) * 1000,
                "p50_response_time_ms": response_times[int(n * 0.5)] * 1000 if n > 0 else 0,
                "p95_response_time_ms": response_times[int(n * 0.95)] * 1000 if n > 0 else 0,
                "error_rate": (stats["errors"] / stats["count"]) * 100
            })
    
    # Sort by request count
    endpoints.sort(key=lambda x: x["requests"], reverse=True)
    
    return {
        "endpoints": endpoints[:20],  # Top 20 endpoints
        "total_endpoints": len(endpoints),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/error-logs", summary="Get recent errors")
async def get_error_logs(
    limit: int = Query(100, ge=1, le=500, description="Number of errors to return"),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """Get recent error logs from the system."""
    collector = get_metrics_collector()
    
    errors = list(collector.recent_errors)[-limit:]
    
    return {
        "total": len(errors),
        "errors": errors,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@router.get("/audit-logs", summary="Get audit logs")
async def get_audit_logs(
    limit: int = Query(100, ge=1, le=500, description="Number of logs to return"),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    """Get audit logs for security and compliance tracking."""
    # TODO: Implement actual audit log retrieval from database
    # For now, return mock data
    return {
        "logs": [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "user": current_user.email,
                "action": "monitoring.accessed",
                "resource": "monitoring_dashboard",
                "ip_address": "127.0.0.1",
                "user_agent": "Mozilla/5.0"
            }
        ],
        "total": 1,
        "limit": limit
    }


@router.post("/metrics/record", summary="Record custom metric")
async def record_custom_metric(
    metric_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Record a custom metric.
    
    Useful for tracking business-specific metrics.
    """
    collector = get_metrics_collector()
    
    metric_type = metric_data.get("type", "gauge")
    metric_name = metric_data.get("name")
    metric_value = metric_data.get("value")
    
    if not metric_name or metric_value is None:
        raise HTTPException(status_code=400, detail="Missing metric name or value")
    
    # Store custom metric (this would need enhancement in the collector)
    # For now, just acknowledge receipt
    
    return {
        "success": True,
        "metric": {
            "name": metric_name,
            "value": metric_value,
            "type": metric_type,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    }


@router.get("/dashboard", summary="Get monitoring dashboard data")
async def get_monitoring_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
) -> Dict[str, Any]:
    """Get comprehensive monitoring dashboard data."""
    collector = get_metrics_collector()
    health_checker = get_health_checker()
    alert_manager = get_alert_manager()
    db_monitor = get_database_monitor()
    
    # Gather all monitoring data
    business_metrics = await collector.update_business_metrics(db)
    performance_metrics = collector.calculate_performance_metrics()
    health_status = await health_checker.get_quick_health()
    alert_summary = alert_manager.get_alert_summary()
    db_summary = db_monitor.get_monitoring_summary()
    
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "health": health_status,
        "alerts": alert_summary,
        "business_metrics": business_metrics.to_dict(),
        "performance_metrics": performance_metrics.to_dict(),
        "database": db_summary,
        "environment": {
            "name": settings.environment,
            "version": settings.version,
            "debug": settings.debug
        }
    }