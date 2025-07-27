"""
Monitoring API Endpoints

Provides API endpoints for system monitoring including:
- Database connection pool metrics
- System health checks
- Performance metrics
- Alert status
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from datetime import datetime

from monitoring.database_monitor import get_database_monitor, get_database_health_status
from database.db_setup import get_engine_info


"""
Monitoring API Endpoints

Provides API endpoints for system monitoring including:
- Database connection pool metrics
- System health checks
- Performance metrics
- Alert status
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime

from monitoring.database_monitor import get_database_monitor, get_database_health_status
from database.db_setup import get_engine_info
from api.dependencies.auth import get_current_active_user
from database import User

router = APIRouter(prefix="/monitoring", tags=["monitoring"])


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    Returns overall system health status.
    """
    try:
        monitor = get_database_monitor()
        
        # Perform quick health checks
        health_checks = monitor.check_connection_health()
        async_health = await monitor.check_async_connection_health()
        
        # Determine overall health
        all_healthy = all(check.success for check in health_checks.values())
        if async_health:
            all_healthy = all_healthy and async_health.success
        
        return {
            "status": "healthy" if all_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": {
                "sync": health_checks.get("sync", {}).success if "sync" in health_checks else False,
                "async": async_health.success if async_health else False,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/database")
async def database_status(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get comprehensive database monitoring status.
    Includes pool metrics, health checks, and alerts.
    Requires authentication for detailed monitoring data.
    """
    try:
        return get_database_health_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database monitoring failed: {str(e)}")


@router.get("/database/pool")
async def database_pool_metrics(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get current database connection pool metrics.
    Requires authentication for detailed pool information.
    """
    try:
        monitor = get_database_monitor()
        metrics = monitor.get_pool_metrics()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "pools": {k: v.to_dict() for k, v in metrics.items()}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pool metrics failed: {str(e)}")


@router.get("/database/alerts")
async def database_alerts(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get current database alerts.
    Requires authentication for alert information.
    """
    try:
        monitor = get_database_monitor()
        metrics = monitor.get_pool_metrics()
        alerts = monitor.check_alerts(metrics)
        
        # Group alerts by severity
        alert_counts = {"critical": 0, "warning": 0, "info": 0}
        for alert in alerts:
            severity = alert.get("severity", "info")
            alert_counts[severity] = alert_counts.get(severity, 0) + 1
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "alert_counts": alert_counts,
            "alerts": alerts,
            "thresholds": monitor.alert_thresholds.__dict__
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database alerts failed: {str(e)}")


@router.get("/database/engine-info")
async def database_engine_info(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get detailed database engine information.
    Requires authentication for engine details.
    """
    try:
        engine_info = get_engine_info()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "engine_info": engine_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Engine info failed: {str(e)}")


@router.get("/prometheus")
async def prometheus_metrics() -> str:
    """
    Prometheus-compatible metrics endpoint.
    Public endpoint for metrics scraping.
    """
    try:
        monitor = get_database_monitor()
        metrics = monitor.get_pool_metrics()
        health_checks = monitor.check_connection_health()
        async_health = await monitor.check_async_connection_health()
        
        # Generate Prometheus format metrics
        prometheus_metrics = []
        
        # Help and type declarations
        prometheus_metrics.append("# HELP ruleiq_db_pool_size Database connection pool size")
        prometheus_metrics.append("# TYPE ruleiq_db_pool_size gauge")
        prometheus_metrics.append("# HELP ruleiq_db_pool_checked_out Database connections checked out")
        prometheus_metrics.append("# TYPE ruleiq_db_pool_checked_out gauge")
        prometheus_metrics.append("# HELP ruleiq_db_pool_utilization Database pool utilization percentage")
        prometheus_metrics.append("# TYPE ruleiq_db_pool_utilization gauge")
        prometheus_metrics.append("# HELP ruleiq_db_pool_overflow Database pool overflow connections")
        prometheus_metrics.append("# TYPE ruleiq_db_pool_overflow gauge")
        prometheus_metrics.append("# HELP ruleiq_db_health Database health check status")
        prometheus_metrics.append("# TYPE ruleiq_db_health gauge")
        prometheus_metrics.append("# HELP ruleiq_db_response_time Database response time in milliseconds")
        prometheus_metrics.append("# TYPE ruleiq_db_response_time gauge")
        
        # Pool metrics
        for pool_type, metric in metrics.items():
            labels = f'pool_type="{pool_type}"'
            prometheus_metrics.append(f'ruleiq_db_pool_size{{{labels}}} {metric.pool_size}')
            prometheus_metrics.append(f'ruleiq_db_pool_checked_out{{{labels}}} {metric.checked_out}')
            prometheus_metrics.append(f'ruleiq_db_pool_utilization{{{labels}}} {metric.utilization_percent}')
            prometheus_metrics.append(f'ruleiq_db_pool_overflow{{{labels}}} {metric.overflow}')
        
        # Health check metrics
        for pool_type, health in health_checks.items():
            labels = f'pool_type="{pool_type}"'
            health_value = 1 if health.success else 0
            prometheus_metrics.append(f'ruleiq_db_health{{{labels}}} {health_value}')
            prometheus_metrics.append(f'ruleiq_db_response_time{{{labels}}} {health.response_time_ms}')
        
        if async_health:
            labels = f'pool_type="async"'
            health_value = 1 if async_health.success else 0
            prometheus_metrics.append(f'ruleiq_db_health{{{labels}}} {health_value}')
            prometheus_metrics.append(f'ruleiq_db_response_time{{{labels}}} {async_health.response_time_ms}')
        
        return "\n".join(prometheus_metrics) + "\n"
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prometheus metrics failed: {str(e)}")


@router.post("/database/test-connection")
async def test_database_connection(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Manually trigger database connection test.
    Requires authentication for connection testing.
    """
    try:
        monitor = get_database_monitor()
        
        # Perform health checks
        sync_health = monitor.check_connection_health()
        async_health = await monitor.check_async_connection_health()
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "sync_health": {k: v.to_dict() for k, v in sync_health.items()},
        }
        
        if async_health:
            results["async_health"] = async_health.to_dict()
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")


@router.get("/status")
async def get_monitoring_status(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get comprehensive monitoring status including all metrics and alerts.
    Requires authentication for full monitoring data.
    """
    try:
        monitor = get_database_monitor()
        summary = monitor.get_monitoring_summary()
        
        return {
            "service_status": "active",
            "monitoring_summary": summary,
            "endpoints": {
                "health": "/api/monitoring/health",
                "database": "/api/monitoring/database", 
                "alerts": "/api/monitoring/database/alerts",
                "metrics": "/api/monitoring/prometheus",
                "pool_metrics": "/api/monitoring/database/pool"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Monitoring status failed: {str(e)}")


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    Returns overall system health status.
    """
    try:
        monitor = get_database_monitor()
        
        # Perform quick health checks
        health_checks = monitor.check_connection_health()
        async_health = await monitor.check_async_connection_health()
        
        # Determine overall health
        all_healthy = all(check.success for check in health_checks.values())
        if async_health:
            all_healthy = all_healthy and async_health.success
        
        return {
            "status": "healthy" if all_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": {
                "sync": health_checks.get("sync", {}).success if "sync" in health_checks else False,
                "async": async_health.success if async_health else False,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/database")
async def database_status() -> Dict[str, Any]:
    """
    Get comprehensive database monitoring status.
    Includes pool metrics, health checks, and alerts.
    """
    try:
        return get_database_health_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database monitoring failed: {str(e)}")


@router.get("/database/pool")
async def database_pool_metrics() -> Dict[str, Any]:
    """
    Get current database connection pool metrics.
    """
    try:
        monitor = get_database_monitor()
        metrics = monitor.get_pool_metrics()
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "pools": {k: v.to_dict() for k, v in metrics.items()}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pool metrics failed: {str(e)}")


@router.get("/database/alerts")
async def database_alerts() -> Dict[str, Any]:
    """
    Get current database alerts.
    """
    try:
        monitor = get_database_monitor()
        metrics = monitor.get_pool_metrics()
        alerts = monitor.check_alerts(metrics)
        
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "alert_count": len(alerts),
            "alerts": alerts,
            "thresholds": monitor.alert_thresholds.__dict__
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database alerts failed: {str(e)}")


@router.get("/database/engine-info")
async def database_engine_info() -> Dict[str, Any]:
    """
    Get detailed database engine information.
    """
    try:
        engine_info = get_engine_info()
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "engine_info": engine_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Engine info failed: {str(e)}")


@router.get("/prometheus")
async def prometheus_metrics() -> str:
    """
    Prometheus-compatible metrics endpoint.
    """
    try:
        monitor = get_database_monitor()
        metrics = monitor.get_pool_metrics()
        health_checks = monitor.check_connection_health()
        async_health = await monitor.check_async_connection_health()
        
        # Generate Prometheus format metrics
        prometheus_metrics = []
        
        # Help and type declarations
        prometheus_metrics.append("# HELP ruleiq_db_pool_size Database connection pool size")
        prometheus_metrics.append("# TYPE ruleiq_db_pool_size gauge")
        prometheus_metrics.append("# HELP ruleiq_db_pool_checked_out Database connections checked out")
        prometheus_metrics.append("# TYPE ruleiq_db_pool_checked_out gauge")
        prometheus_metrics.append("# HELP ruleiq_db_pool_utilization Database pool utilization percentage")
        prometheus_metrics.append("# TYPE ruleiq_db_pool_utilization gauge")
        prometheus_metrics.append("# HELP ruleiq_db_pool_overflow Database pool overflow connections")
        prometheus_metrics.append("# TYPE ruleiq_db_pool_overflow gauge")
        prometheus_metrics.append("# HELP ruleiq_db_health Database health check status")
        prometheus_metrics.append("# TYPE ruleiq_db_health gauge")
        prometheus_metrics.append("# HELP ruleiq_db_response_time Database response time in milliseconds")
        prometheus_metrics.append("# TYPE ruleiq_db_response_time gauge")
        
        # Pool metrics
        for pool_type, metric in metrics.items():
            labels = f'pool_type="{pool_type}"'
            prometheus_metrics.append(f'ruleiq_db_pool_size{{{labels}}} {metric.pool_size}')
            prometheus_metrics.append(f'ruleiq_db_pool_checked_out{{{labels}}} {metric.checked_out}')
            prometheus_metrics.append(f'ruleiq_db_pool_utilization{{{labels}}} {metric.utilization_percent}')
            prometheus_metrics.append(f'ruleiq_db_pool_overflow{{{labels}}} {metric.overflow}')
        
        # Health check metrics
        for pool_type, health in health_checks.items():
            labels = f'pool_type="{pool_type}"'
            health_value = 1 if health.success else 0
            prometheus_metrics.append(f'ruleiq_db_health{{{labels}}} {health_value}')
            prometheus_metrics.append(f'ruleiq_db_response_time{{{labels}}} {health.response_time_ms}')
        
        if async_health:
            labels = f'pool_type="async"'
            health_value = 1 if async_health.success else 0
            prometheus_metrics.append(f'ruleiq_db_health{{{labels}}} {health_value}')
            prometheus_metrics.append(f'ruleiq_db_response_time{{{labels}}} {async_health.response_time_ms}')
        
        return "\n".join(prometheus_metrics) + "\n"
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prometheus metrics failed: {str(e)}")


@router.post("/database/test-connection")
async def test_database_connection() -> Dict[str, Any]:
    """
    Manually trigger database connection test.
    """
    try:
        monitor = get_database_monitor()
        
        # Perform health checks
        sync_health = monitor.check_connection_health()
        async_health = await monitor.check_async_connection_health()
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "sync_health": {k: v.to_dict() for k, v in sync_health.items()},
        }
        
        if async_health:
            results["async_health"] = async_health.to_dict()
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Connection test failed: {str(e)}")