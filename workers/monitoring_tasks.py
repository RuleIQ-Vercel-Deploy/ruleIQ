"""
Background tasks for database and system monitoring.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any

from celery import Celery
from celery.schedules import crontab

from services.monitoring.database_monitor import database_monitor
from config.logging_config import get_logger

logger = get_logger(__name__)

# Import celery app
from celery_app import celery_app


@celery_app.task(name="collect_database_metrics")
def collect_database_metrics() -> Dict[str, Any]:
    """
    Collect database connection pool and session metrics.
    
    This task runs periodically to gather monitoring data.
    """
    try:
        logger.info("Starting database metrics collection")
        
        # Collect pool metrics
        pool_metrics = database_monitor.collect_pool_metrics()
        
        # Collect session metrics
        session_metrics = database_monitor.collect_session_metrics()
        
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "pool_metrics": pool_metrics.to_dict() if pool_metrics else None,
            "session_metrics": session_metrics.to_dict(),
            "status": "success"
        }
        
        logger.info(f"Database metrics collected successfully: {result}")
        return result
        
    except Exception as e:
        error_msg = f"Failed to collect database metrics: {e}"
        logger.error(error_msg)
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error",
            "error": str(e)
        }


@celery_app.task(name="database_health_check")
def database_health_check() -> Dict[str, Any]:
    """
    Perform comprehensive database health check.
    
    This task runs less frequently to assess overall database health.
    """
    try:
        logger.info("Starting database health check")
        
        # Get current monitoring status
        status = database_monitor.get_current_status()
        
        # Analyze health
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
        
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "health_status": health_status,
            "health_message": health_message,
            "recommendations": recommendations,
            "metrics_summary": status,
            "status": "success"
        }
        
        # Log health status
        log_method = {
            "healthy": logger.info,
            "warning": logger.warning,
            "critical": logger.error
        }.get(health_status, logger.info)
        
        log_method(f"Database health check completed: {health_message}")
        
        return result
        
    except Exception as e:
        error_msg = f"Database health check failed: {e}"
        logger.error(error_msg)
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error",
            "error": str(e)
        }


@celery_app.task(name="cleanup_monitoring_data")
def cleanup_monitoring_data() -> Dict[str, Any]:
    """
    Clean up old monitoring data to prevent memory growth.
    
    This task runs daily to remove old metrics and alerts.
    """
    try:
        logger.info("Starting monitoring data cleanup")
        
        # Get counts before cleanup
        pool_metrics_before = len(database_monitor.pool_metrics_history)
        session_metrics_before = len(database_monitor.session_metrics_history)
        alerts_before = len(database_monitor.alerts)
        
        # Trigger cleanup (this happens automatically in collect methods, 
        # but we can force it here)
        database_monitor._cleanup_old_metrics()
        
        # Get counts after cleanup
        pool_metrics_after = len(database_monitor.pool_metrics_history)
        session_metrics_after = len(database_monitor.session_metrics_history)
        alerts_after = len(database_monitor.alerts)
        
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "cleanup_summary": {
                "pool_metrics_removed": pool_metrics_before - pool_metrics_after,
                "session_metrics_removed": session_metrics_before - session_metrics_after,
                "alerts_removed": alerts_before - alerts_after,
                "pool_metrics_remaining": pool_metrics_after,
                "session_metrics_remaining": session_metrics_after,
                "alerts_remaining": alerts_after
            },
            "status": "success"
        }
        
        logger.info(f"Monitoring data cleanup completed: {result['cleanup_summary']}")
        return result
        
    except Exception as e:
        error_msg = f"Monitoring data cleanup failed: {e}"
        logger.error(error_msg)
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error",
            "error": str(e)
        }


@celery_app.task(name="system_metrics_collection")
def system_metrics_collection() -> Dict[str, Any]:
    """
    Collect basic system metrics (CPU, memory, disk).
    
    This task runs periodically to gather system resource data.
    """
    try:
        import psutil
        
        logger.info("Starting system metrics collection")
        
        # CPU and memory metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Network I/O (if available)
        try:
            network = psutil.net_io_counters()
            network_data = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
        except Exception:
            network_data = None
        
        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "system_metrics": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "memory_used_gb": memory.used / (1024**3),
                "disk_free_gb": disk.free / (1024**3),
                "disk_used_gb": disk.used / (1024**3),
                "disk_percent": (disk.used / disk.total) * 100,
                "network": network_data
            },
            "status": "success"
        }
        
        logger.info(f"System metrics collected: CPU {cpu_percent}%, Memory {memory.percent}%")
        return result
        
    except Exception as e:
        error_msg = f"System metrics collection failed: {e}"
        logger.error(error_msg)
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "error",
            "error": str(e)
        }


# Celery beat schedule for monitoring tasks
monitoring_schedule = {
    # Collect database metrics every 30 seconds
    'collect-database-metrics': {
        'task': 'collect_database_metrics',
        'schedule': 30.0,  # seconds
    },
    
    # Database health check every 5 minutes
    'database-health-check': {
        'task': 'database_health_check',
        'schedule': crontab(minute='*/5'),  # every 5 minutes
    },
    
    # System metrics every minute
    'system-metrics-collection': {
        'task': 'system_metrics_collection',
        'schedule': 60.0,  # seconds
    },
    
    # Cleanup old monitoring data daily at 2 AM
    'cleanup-monitoring-data': {
        'task': 'cleanup_monitoring_data',
        'schedule': crontab(hour=2, minute=0),  # daily at 2:00 AM
    },
}


def register_monitoring_tasks():
    """Register monitoring tasks with Celery beat scheduler."""
    try:
        from celery_app import celery_app
        
        # Update the beat schedule
        if hasattr(celery_app.conf, 'beat_schedule'):
            celery_app.conf.beat_schedule.update(monitoring_schedule)
        else:
            celery_app.conf.beat_schedule = monitoring_schedule
            
        logger.info("Monitoring tasks registered with Celery beat scheduler")
        
    except Exception as e:
        logger.error(f"Failed to register monitoring tasks: {e}")


# Auto-register tasks when module is imported
register_monitoring_tasks()
