"""
Monitoring endpoints for database and system health.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from api.dependencies.auth import get_current_active_user
from database.models import User
from services.monitoring.database_monitor import database_monitor
from database.db_setup import get_engine_info
from config.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/database/status")
async def get_database_status(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get current database monitoring status including pool metrics and alerts.
    
    Requires authentication to prevent information disclosure.
    """
    try:
        status = database_monitor.get_current_status()
        return {
            "status": "success",
            "data": status
        }
    except Exception as e:
        logger.error(f"Error getting database status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get database status")


@router.get("/database/pool")
async def get_pool_metrics(
    current_user: User = Depends(get_current_active_user),
    hours: int = Query(default=1, ge=1, le=24, description="Hours of history to return")
) -> Dict[str, Any]:
    """
    Get database connection pool metrics for the specified time period.
    """
    try:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        recent_metrics = [
            m.to_dict() for m in database_monitor.pool_metrics_history
            if m.timestamp > cutoff
        ]
        
        # Calculate summary statistics
        if recent_metrics:
            utilizations = [m['utilization_percent'] for m in recent_metrics]
            overflows = [m['overflow'] for m in recent_metrics]
            
            summary = {
                'avg_utilization': sum(utilizations) / len(utilizations),
                'max_utilization': max(utilizations),
                'total_overflow_events': sum(1 for o in overflows if o > 0),
                'max_overflow': max(overflows),
                'metrics_count': len(recent_metrics)
            }
        else:
            summary = {
                'avg_utilization': 0,
                'max_utilization': 0,
                'total_overflow_events': 0,
                'max_overflow': 0,
                'metrics_count': 0
            }
        
        return {
            "status": "success",
            "data": {
                "summary": summary,
                "metrics": recent_metrics,
                "period_hours": hours
            }
        }
    except Exception as e:
        logger.error(f"Error getting pool metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pool metrics")


@router.get("/database/sessions")
async def get_session_metrics(
    current_user: User = Depends(get_current_active_user),
    hours: int = Query(default=1, ge=1, le=24, description="Hours of history to return")
) -> Dict[str, Any]:
    """
    Get database session lifecycle metrics for the specified time period.
    """
    try:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        recent_metrics = [
            m.to_dict() for m in database_monitor.session_metrics_history
            if m.timestamp > cutoff
        ]
        
        # Get current session tracker stats
        current_stats = database_monitor.session_tracker.get_stats()
        
        return {
            "status": "success",
            "data": {
                "current_stats": current_stats,
                "metrics": recent_metrics,
                "period_hours": hours
            }
        }
    except Exception as e:
        logger.error(f"Error getting session metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session metrics")


@router.get("/database/alerts")
async def get_database_alerts(
    current_user: User = Depends(get_current_active_user),
    hours: int = Query(default=24, ge=1, le=168, description="Hours of alert history to return"),
    level: str = Query(default=None, description="Filter by alert level (info, warning, critical)")
) -> Dict[str, Any]:
    """
    Get database monitoring alerts for the specified time period.
    """
    try:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        alerts = [
            a.to_dict() for a in database_monitor.alerts
            if a.timestamp > cutoff
        ]
        
        # Filter by level if specified
        if level:
            level = level.lower()
            if level not in ['info', 'warning', 'critical']:
                raise HTTPException(status_code=400, detail="Invalid alert level")
            alerts = [a for a in alerts if a['level'] == level]
        
        # Group alerts by level for summary
        alert_summary = {
            'critical': len([a for a in alerts if a['level'] == 'critical']),
            'warning': len([a for a in alerts if a['level'] == 'warning']),
            'info': len([a for a in alerts if a['level'] == 'info']),
            'total': len(alerts)
        }
        
        return {
            "status": "success",
            "data": {
                "summary": alert_summary,
                "alerts": alerts,
                "period_hours": hours,
                "filter_level": level
            }
        }
    except Exception as e:
        logger.error(f"Error getting database alerts: {e}")
        raise HTTPException(status_code=500, detail="Failed to get database alerts")


@router.get("/database/engine-info")
async def get_engine_info_endpoint(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get raw database engine information for debugging.
    """
    try:
        engine_info = get_engine_info()
        return {
            "status": "success",
            "data": engine_info
        }
    except Exception as e:
        logger.error(f"Error getting engine info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get engine info")


@router.post("/database/collect-metrics")
async def trigger_metrics_collection(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Manually trigger database metrics collection.
    
    Useful for testing or immediate monitoring needs.
    """
    try:
        pool_metrics = database_monitor.collect_pool_metrics()
        session_metrics = database_monitor.collect_session_metrics()
        
        return {
            "status": "success",
            "data": {
                "pool_metrics": pool_metrics.to_dict() if pool_metrics else None,
                "session_metrics": session_metrics.to_dict(),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error collecting metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to collect metrics")


@router.get("/database/health")
async def get_database_health(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get overall database health status with recommendations.
    """
    try:
        status = database_monitor.get_current_status()
        
        # Determine overall health
        critical_alerts = status['alert_counts']['critical']
        warning_alerts = status['alert_counts']['warning']
        
        if critical_alerts > 0:
            health_status = "critical"
            health_message = f"{critical_alerts} critical database issues detected"
        elif warning_alerts > 0:
            health_status = "warning"
            health_message = f"{warning_alerts} database warnings detected"
        else:
            health_status = "healthy"
            health_message = "Database is operating normally"
        
        # Generate recommendations
        recommendations = []
        
        if status['pool_metrics']:
            pool_util = status['pool_metrics']['utilization_percent']
            if pool_util > 80:
                recommendations.append("Consider increasing database connection pool size")
            if status['pool_metrics']['overflow'] > 0:
                recommendations.append("Pool overflow detected - monitor for connection leaks")
        
        if status['session_metrics']['long_running_sessions'] > 0:
            recommendations.append("Long-running sessions detected - review query performance")
        
        if status['session_metrics']['active_sessions'] > 50:
            recommendations.append("High number of active sessions - check for session leaks")
        
        return {
            "status": "success",
            "data": {
                "health_status": health_status,
                "health_message": health_message,
                "recommendations": recommendations,
                "metrics_summary": {
                    "pool_utilization": status['pool_metrics']['utilization_percent'] if status['pool_metrics'] else 0,
                    "active_sessions": status['session_metrics']['active_sessions'],
                    "recent_alerts": status['alert_counts']
                },
                "timestamp": status['timestamp']
            }
        }
    except Exception as e:
        logger.error(f"Error getting database health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get database health")


@router.get("/system/metrics")
async def get_system_metrics(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get basic system metrics for monitoring dashboard.
    """
    try:
        import psutil
        
        # CPU and memory metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Database metrics
        db_status = database_monitor.get_current_status()
        
        return {
            "status": "success",
            "data": {
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory.percent,
                    "memory_available_gb": memory.available / (1024**3),
                    "disk_free_gb": disk.free / (1024**3),
                    "disk_percent": (disk.used / disk.total) * 100
                },
                "database": {
                    "pool_utilization": db_status['pool_metrics']['utilization_percent'] if db_status['pool_metrics'] else 0,
                    "active_sessions": db_status['session_metrics']['active_sessions'],
                    "alert_counts": db_status['alert_counts']
                },
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system metrics")
