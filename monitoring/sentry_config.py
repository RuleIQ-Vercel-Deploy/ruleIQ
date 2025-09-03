"""
Sentry Configuration and Integration for RuleIQ

Provides comprehensive error tracking, performance monitoring, and alerting
through Sentry integration with custom context and metric tracking.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from config.settings import settings

logger = logging.getLogger(__name__)


def get_sentry_environment() -> str:
    """Get the appropriate Sentry environment based on settings."""
    if settings.is_testing:
        return "testing"
    elif settings.is_production:
        return "production"
    elif settings.environment == "staging":
        return "staging"
    else:
        return "development"


def get_release_version() -> str:
    """Get the release version for Sentry tracking."""
    # Try to get from environment variable first
    version = os.getenv("RELEASE_VERSION")
    if version:
        return f"ruleiq@{version}"
    
    # Try to get from git commit hash
    try:
        import subprocess
        commit_hash = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()[:7]
        return f"ruleiq@{commit_hash}"
    except Exception:
        pass
    
    # Fallback to settings version
    return f"ruleiq@{settings.version}"


def before_send(event: Dict[str, Any], hint: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Filter and modify events before sending to Sentry.
    
    Args:
        event: The event data to be sent
        hint: Additional context about the event
        
    Returns:
        Modified event or None to drop the event
    """
    # Don't send events in testing environment
    if settings.is_testing:
        return None
    
    # Filter out expected errors
    if "exc_info" in hint:
        exc_type, exc_value, tb = hint["exc_info"]
        
        # Don't report expected validation errors
        if exc_type.__name__ in ["ValidationError", "RequestValidationError"]:
            return None
        
        # Don't report rate limiting errors
        if exc_type.__name__ == "HTTPException" and hasattr(exc_value, "status_code"):
            if exc_value.status_code == 429:  # Too Many Requests
                return None
    
    # Add custom context
    if event.get("user") is None:
        event["user"] = {}
    
    # Add environment context
    event.setdefault("tags", {})
    event["tags"]["environment"] = settings.environment
    event["tags"]["debug_mode"] = str(settings.debug)
    
    # Add custom context
    event.setdefault("contexts", {})
    event["contexts"]["app"] = {
        "app_name": settings.app_name,
        "version": settings.version,
        "host": settings.host,
        "port": settings.port,
    }
    
    return event


def traces_sampler(sampling_context: Dict[str, Any]) -> float:
    """
    Dynamic sampling based on the transaction.
    
    Args:
        sampling_context: Context about the transaction
        
    Returns:
        Sample rate between 0.0 and 1.0
    """
    # Get the transaction name
    transaction_name = sampling_context.get("transaction_context", {}).get("name", "")
    
    # Health check endpoints - very low sampling
    if "/health" in transaction_name or "/ping" in transaction_name:
        return 0.001
    
    # Static assets and docs - no sampling
    if any(path in transaction_name for path in ["/docs", "/redoc", "/openapi.json", "/static"]):
        return 0
    
    # Authentication endpoints - higher sampling
    if "/auth" in transaction_name:
        return 0.5
    
    # AI endpoints - highest sampling for performance monitoring
    if any(path in transaction_name for path in ["/ai", "/chat", "/policy/generate"]):
        return 0.8
    
    # Payment endpoints - high sampling
    if "/payment" in transaction_name:
        return 0.7
    
    # Default sampling rate
    return settings.traces_sample_rate


def init_sentry() -> None:
    """Initialize Sentry SDK with comprehensive configuration."""
    if not settings.enable_sentry or not settings.sentry_dsn:
        logger.info("Sentry integration disabled or DSN not configured")
        return
    
    try:
        # Configure logging integration
        logging_integration = LoggingIntegration(
            level=logging.INFO,  # Capture info and above
            event_level=logging.ERROR  # Send errors as events
        )
        
        # Initialize Sentry
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=get_sentry_environment(),
            release=get_release_version(),
            
            # Integrations
            integrations=[
                FastApiIntegration(
                    transaction_style="endpoint",
                    failed_request_status_codes={400, 401, 403, 404, 429, 500, 502, 503, 504},
                ),
                SqlalchemyIntegration(),
                RedisIntegration(),
                AioHttpIntegration(),
                logging_integration,
            ],
            
            # Performance monitoring
            traces_sample_rate=settings.traces_sample_rate,
            traces_sampler=traces_sampler,
            profiles_sample_rate=settings.profiles_sample_rate,
            
            # Error filtering and processing
            before_send=before_send,
            
            # Session tracking
            auto_session_tracking=True,
            
            # Breadcrumb configuration
            max_breadcrumbs=100,
            attach_stacktrace=True,
            
            # Request bodies
            request_bodies="medium",  # Capture request bodies for errors
            
            # In-app detection
            in_app_include=["api", "services", "database", "monitoring"],
            in_app_exclude=["tests", "migrations"],
            
            # Debug mode
            debug=settings.debug and settings.environment == "development",
            
            # Additional options
            send_default_pii=False,  # Don't send personally identifiable information
            server_name=os.getenv("SERVER_NAME", "ruleiq-api"),
            shutdown_timeout=5,
        )
        
        logger.info(f"Sentry initialized successfully for {get_sentry_environment()} environment")
        
        # Test Sentry connection
        if settings.environment == "development":
            sentry_sdk.capture_message("Sentry integration initialized", level="info")
            
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")


def capture_exception(error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Capture an exception with optional context.
    
    Args:
        error: The exception to capture
        context: Optional additional context
    """
    if not settings.enable_sentry:
        return
    
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_context(key, value)
        
        sentry_sdk.capture_exception(error)


def capture_message(message: str, level: str = "info", context: Optional[Dict[str, Any]] = None) -> None:
    """
    Capture a message with optional context.
    
    Args:
        message: The message to capture
        level: Message level (debug, info, warning, error, fatal)
        context: Optional additional context
    """
    if not settings.enable_sentry:
        return
    
    with sentry_sdk.push_scope() as scope:
        if context:
            for key, value in context.items():
                scope.set_context(key, value)
        
        sentry_sdk.capture_message(message, level=level)


def set_user_context(user_id: str, email: Optional[str] = None, username: Optional[str] = None) -> None:
    """
    Set user context for Sentry events.
    
    Args:
        user_id: The user's ID
        email: The user's email (optional)
        username: The user's username (optional)
    """
    if not settings.enable_sentry:
        return
    
    sentry_sdk.set_user({
        "id": user_id,
        "email": email,
        "username": username,
    })


def add_breadcrumb(message: str, category: str = "custom", level: str = "info", data: Optional[Dict[str, Any]] = None) -> None:
    """
    Add a breadcrumb for better error context.
    
    Args:
        message: The breadcrumb message
        category: Category of the breadcrumb
        level: Level of the breadcrumb
        data: Optional additional data
    """
    if not settings.enable_sentry:
        return
    
    sentry_sdk.add_breadcrumb(
        message=message,
        category=category,
        level=level,
        data=data or {}
    )


def start_transaction(name: str, op: str = "http.server") -> Any:
    """
    Start a performance monitoring transaction.
    
    Args:
        name: Name of the transaction
        op: Operation type
        
    Returns:
        Transaction object
    """
    if not settings.enable_sentry or not settings.enable_performance_monitoring:
        return None
    
    return sentry_sdk.start_transaction(name=name, op=op)


def measure_performance(name: str, op: str = "function"):
    """
    Decorator to measure function performance.
    
    Args:
        name: Name of the span
        op: Operation type
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not settings.enable_sentry or not settings.enable_performance_monitoring:
                return func(*args, **kwargs)
            
            with sentry_sdk.start_span(description=name, op=op):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator