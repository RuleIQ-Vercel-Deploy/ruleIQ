"""
Monitoring package for ruleIQ.

Provides comprehensive monitoring, observability, and alerting:
- Database monitoring and health checks
- Performance metrics collection
- Business KPI tracking
- Sentry error tracking
- Alert management
- Health check system
"""

from .database_monitor import get_database_monitor, get_database_health_status
from .metrics import (
    get_metrics_collector,
    MetricsCollector,
    BusinessMetrics,
    PerformanceMetrics,
    start_metrics_background_tasks,
    create_metrics_endpoint
)
from .health_checks import (
    get_health_checker,
    HealthChecker,
    HealthStatus,
    ComponentHealth,
    SystemHealth,
    run_health_check_loop
)
from .alerting import (
    get_alert_manager,
    AlertManager,
    Alert,
    AlertSeverity,
    AlertCategory,
    AlertChannel,
    run_alert_evaluation_loop
)
from .sentry_config import (
    init_sentry,
    capture_exception,
    capture_message,
    set_user_context,
    add_breadcrumb,
    start_transaction,
    measure_performance
)

__all__ = [
    # Database monitoring
    "get_database_monitor",
    "get_database_health_status",
    
    # Metrics
    "get_metrics_collector",
    "MetricsCollector",
    "BusinessMetrics",
    "PerformanceMetrics",
    "start_metrics_background_tasks",
    "create_metrics_endpoint",
    
    # Health checks
    "get_health_checker",
    "HealthChecker",
    "HealthStatus",
    "ComponentHealth",
    "SystemHealth",
    "run_health_check_loop",
    
    # Alerting
    "get_alert_manager",
    "AlertManager",
    "Alert",
    "AlertSeverity",
    "AlertCategory",
    "AlertChannel",
    "run_alert_evaluation_loop",
    
    # Sentry
    "init_sentry",
    "capture_exception",
    "capture_message",
    "set_user_context",
    "add_breadcrumb",
    "start_transaction",
    "measure_performance",
]