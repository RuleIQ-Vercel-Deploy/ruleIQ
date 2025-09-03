"""
Monitoring System Startup and Initialization

Handles initialization of all monitoring components during application startup.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List

from monitoring import (
    init_sentry,
    get_metrics_collector,
    start_metrics_background_tasks,
    get_health_checker,
    run_health_check_loop,
    get_alert_manager,
    run_alert_evaluation_loop,
    get_database_monitor
)
from config.settings import settings

logger = logging.getLogger(__name__)


async def initialize_monitoring_system() -> Dict[str, Any]:
    """
    Initialize all monitoring components.
    
    Returns:
        Dictionary containing references to monitoring tasks and components
    """
    monitoring_state = {
        "tasks": [],
        "components": {},
        "status": "initializing"
    }
    
    try:
        # Initialize Sentry error tracking
        if settings.enable_sentry:
            init_sentry()
            logger.info("✅ Sentry error tracking initialized")
            monitoring_state["components"]["sentry"] = "initialized"
        else:
            logger.info("⚠️ Sentry disabled in configuration")
            monitoring_state["components"]["sentry"] = "disabled"
        
        # Initialize metrics collector
        metrics_collector = get_metrics_collector()
        monitoring_state["components"]["metrics_collector"] = metrics_collector
        logger.info("✅ Metrics collector initialized")
        
        # Start metrics background tasks
        await start_metrics_background_tasks()
        logger.info("✅ Metrics background tasks started")
        
        # Initialize health checker
        health_checker = get_health_checker()
        monitoring_state["components"]["health_checker"] = health_checker
        logger.info("✅ Health checker initialized")
        
        # Start health check loop
        health_check_task = asyncio.create_task(
            run_health_check_loop(interval=30)
        )
        monitoring_state["tasks"].append(health_check_task)
        logger.info("✅ Health check loop started (30s interval)")
        
        # Initialize alert manager
        alert_manager = get_alert_manager()
        monitoring_state["components"]["alert_manager"] = alert_manager
        logger.info("✅ Alert manager initialized")
        
        # Start alert evaluation loop
        alert_task = asyncio.create_task(
            run_alert_evaluation_loop(interval=30)
        )
        monitoring_state["tasks"].append(alert_task)
        logger.info("✅ Alert evaluation loop started (30s interval)")
        
        # Initialize database monitor
        db_monitor = get_database_monitor()
        monitoring_state["components"]["database_monitor"] = db_monitor
        
        # Start database monitoring
        db_monitoring_task = asyncio.create_task(
            db_monitor.start_monitoring_loop(interval_seconds=30)
        )
        monitoring_state["tasks"].append(db_monitoring_task)
        logger.info("✅ Database monitoring started (30s interval)")
        
        # Run initial health check
        initial_health = await health_checker.check_all_components()
        logger.info(f"📊 Initial health check: {initial_health.status}")
        
        # Log monitoring summary
        logger.info(
            "🎯 Monitoring system initialized successfully\n"
            f"  - Sentry: {monitoring_state['components'].get('sentry', 'disabled')}\n"
            f"  - Metrics: Collecting {len(metrics_collector.registry._collector_to_names)} metrics\n"
            f"  - Health Checks: {len(initial_health.components)} components monitored\n"
            f"  - Alerts: {len(alert_manager.alert_rules)} rules configured\n"
            f"  - Background Tasks: {len(monitoring_state['tasks'])} tasks running"
        )
        
        monitoring_state["status"] = "running"
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize monitoring system: {e}")
        monitoring_state["status"] = "error"
        monitoring_state["error"] = str(e)
    
    return monitoring_state


async def shutdown_monitoring_system(monitoring_state: Dict[str, Any]) -> None:
    """
    Gracefully shutdown monitoring components.
    
    Args:
        monitoring_state: State dictionary from initialize_monitoring_system
    """
    logger.info("Shutting down monitoring system...")
    
    # Cancel all monitoring tasks
    for task in monitoring_state.get("tasks", []):
        if not task.done():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            except Exception as e:
                logger.warning(f"Error cancelling monitoring task: {e}")
    
    logger.info("✅ Monitoring system shut down successfully")


def get_monitoring_status(monitoring_state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get current status of monitoring system.
    
    Args:
        monitoring_state: State dictionary from initialize_monitoring_system
        
    Returns:
        Status information about monitoring components
    """
    from monitoring import get_metrics_collector, get_health_checker, get_alert_manager
    
    status = {
        "status": monitoring_state.get("status", "unknown"),
        "components": {}
    }
    
    # Check Sentry status
    status["components"]["sentry"] = {
        "enabled": settings.enable_sentry,
        "status": monitoring_state.get("components", {}).get("sentry", "unknown")
    }
    
    # Check metrics collector
    try:
        metrics = get_metrics_collector()
        status["components"]["metrics"] = {
            "status": "running",
            "metrics_count": len(metrics.registry._collector_to_names),
            "recent_requests": len(metrics.recent_requests),
            "recent_errors": len(metrics.recent_errors)
        }
    except Exception as e:
        status["components"]["metrics"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check health checker
    try:
        health_checker = get_health_checker()
        status["components"]["health"] = {
            "status": "running",
            "last_check": health_checker.last_full_check.isoformat() if health_checker.last_full_check else None,
            "components_checked": len(health_checker.last_check_results)
        }
    except Exception as e:
        status["components"]["health"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check alert manager
    try:
        alerts = get_alert_manager()
        alert_summary = alerts.get_alert_summary()
        status["components"]["alerts"] = {
            "status": "running",
            "active_alerts": alert_summary["total_active"],
            "rules_count": len(alerts.alert_rules),
            "by_severity": alert_summary["by_severity"]
        }
    except Exception as e:
        status["components"]["alerts"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Check background tasks
    tasks_running = sum(1 for task in monitoring_state.get("tasks", []) if not task.done())
    status["background_tasks"] = {
        "total": len(monitoring_state.get("tasks", [])),
        "running": tasks_running,
        "stopped": len(monitoring_state.get("tasks", [])) - tasks_running
    }
    
    return status