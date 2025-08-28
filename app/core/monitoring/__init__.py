"""
Monitoring and error handling module for RuleIQ.

This module provides comprehensive error handling, structured logging,
health checks, and monitoring capabilities.
"""

from .error_handler import (
    ErrorHandler,
    GlobalErrorHandler,
    setup_error_handling,
    custom_exception_handler
)
from .logger import (
    get_logger,
    setup_logging,
    LogLevel,
    StructuredLogger
)
from .health import (
    HealthCheck,
    HealthStatus,
    run_health_checks,
    register_health_check
)
from .metrics import (
    MetricsCollector,
    track_request,
    track_error,
    track_performance,
    get_metrics
)
from .sentry_integration import (
    setup_sentry,
    capture_exception,
    capture_message,
    set_user_context
)

__all__ = [
    # Error handling
    'ErrorHandler',
    'GlobalErrorHandler',
    'setup_error_handling',
    'custom_exception_handler',
    
    # Logging
    'get_logger',
    'setup_logging',
    'LogLevel',
    'StructuredLogger',
    
    # Health checks
    'HealthCheck',
    'HealthStatus',
    'run_health_checks',
    'register_health_check',
    
    # Metrics
    'MetricsCollector',
    'track_request',
    'track_error',
    'track_performance',
    'get_metrics',
    
    # Sentry
    'setup_sentry',
    'capture_exception',
    'capture_message',
    'set_user_context',
]