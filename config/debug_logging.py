"""
Comprehensive Debug Logging Framework for ruleIQ

Provides structured logging with context, performance metrics,
and debug traces for development and production environments.
"""

import os
import sys
import logging
import time
import traceback
from datetime import datetime
from typing import Dict, Any, Optional
from functools import wraps
from contextlib import contextmanager
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger


class ContextFilter(logging.Filter):
    """Add contextual information to log records"""

    def __init__(self, context: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.context = context or {}

    def filter(self, record):
        # Add context to record
        for key, value in self.context.items():
            setattr(record, key, value)

        # Add timestamp
        record.timestamp = datetime.utcnow().isoformat()

        # Add request context if available
        record.request_id = getattr(record, "request_id", "no-request")
        record.user_id = getattr(record, "user_id", "anonymous")
        record.session_id = getattr(record, "session_id", "no-session")

        return True


class PerformanceLogger:
    """Track and log performance metrics"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.timers: Dict[str, float] = {}

    @contextmanager
    def timer(self, operation: str, threshold_ms: float = 1000.0):
        """Context manager to time operations"""
        start_time = time.perf_counter()
        try:
            yield
        finally:
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log if over threshold or in debug mode
            log_level = logging.WARNING if duration_ms > threshold_ms else logging.DEBUG

            self.logger.log(
                log_level,
                f"Performance: {operation} took {duration_ms:.2f}ms",
                extra={
                    "operation": operation,
                    "duration_ms": duration_ms,
                    "over_threshold": duration_ms > threshold_ms,
                    "event_type": "performance",
                },
            )

    def log_metric(self, metric_name: str, value: float, unit: str = "count"):
        """Log a custom metric"""
        self.logger.info(
            f"Metric: {metric_name} = {value} {unit}",
            extra={
                "metric_name": metric_name,
                "metric_value": value,
                "metric_unit": unit,
                "event_type": "metric",
            },
        )


class DebugLogger:
    """Enhanced logger for debugging and development"""

    def __init__(self, name: str, level: str = "INFO"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.performance = PerformanceLogger(self.logger)
        self.setup_logger(level)

    def setup_logger(self, level: str):
        """Configure logger with appropriate handlers and formatters"""
        self.logger.setLevel(getattr(logging, level.upper()))

        # Clear existing handlers
        self.logger.handlers.clear()

        # Console handler for development
        if os.getenv("ENVIRONMENT", "development") == "development":
            console_handler = logging.StreamHandler(sys.stdout)
            console_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - [%(request_id)s] - %(message)s"
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)

        # File handler for persistent logging
        if os.getenv("LOG_TO_FILE", "true").lower() == "true":
            log_dir = os.getenv("LOG_DIR", "logs")
            os.makedirs(log_dir, exist_ok=True)

            # Rotating file handler
            file_handler = RotatingFileHandler(
                filename=os.path.join(log_dir, f"{self.name}.log"),
                maxBytes=10 * 1024 * 1024,  # 10MB
                backupCount=5,
            )

            # JSON formatter for structured logging
            json_formatter = jsonlogger.JsonFormatter(
                "%(timestamp)s %(name)s %(levelname)s %(request_id)s %(user_id)s %(message)s"
            )
            file_handler.setFormatter(json_formatter)
            self.logger.addHandler(file_handler)

        # Add context filter
        context_filter = ContextFilter()
        self.logger.addFilter(context_filter)

    def set_context(self, **context):
        """Set logging context for this session"""
        for handler in self.logger.handlers:
            if hasattr(handler, "filters"):
                for filter_obj in handler.filters:
                    if isinstance(filter_obj, ContextFilter):
                        filter_obj.context.update(context)

    def debug_request(
        self,
        request_data: Dict[str, Any],
        response_data: Optional[Dict[str, Any]] = None,
    ):
        """Log detailed request/response information"""
        log_data = {
            "event_type": "api_request",
            "request": request_data,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if response_data:
            log_data["response"] = response_data

        self.logger.debug("API Request Debug", extra=log_data)

    def debug_db_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        duration_ms: Optional[float] = None,
    ):
        """Log database query information"""
        log_data = {
            "event_type": "db_query",
            "query": query[:500],  # Truncate long queries
            "params": params or {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        if duration_ms:
            log_data["duration_ms"] = duration_ms

        self.logger.debug("Database Query", extra=log_data)

    def debug_external_call(
        self,
        service: str,
        endpoint: str,
        method: str,
        response_code: Optional[int] = None,
    ):
        """Log external service calls"""
        log_data = {
            "event_type": "external_call",
            "service": service,
            "endpoint": endpoint,
            "method": method,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if response_code:
            log_data["response_code"] = response_code

        self.logger.debug("External Service Call", extra=log_data)

    def error_with_context(
        self, message: str, error: Exception, context: Optional[Dict[str, Any]] = None
    ):
        """Log errors with full context and stack trace"""
        error_data = {
            "event_type": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "stack_trace": traceback.format_exc(),
            "context": context or {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        self.logger.error(f"Error: {message}", extra=error_data)

    def security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security-related events"""
        security_data = {
            "event_type": "security",
            "security_event": event_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
        }

        self.logger.warning(f"Security Event: {event_type}", extra=security_data)

    def compliance_event(
        self,
        action: str,
        framework: str,
        result: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Log compliance-related actions"""
        compliance_data = {
            "event_type": "compliance",
            "action": action,
            "framework": framework,
            "result": result,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat(),
        }

        self.logger.info(f"Compliance: {action} for {framework}", extra=compliance_data)


class DebugMiddleware:
    """Middleware to add debug logging to FastAPI"""

    def __init__(self, app, logger: DebugLogger):
        self.app = app
        self.logger = logger

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Generate request ID
        import uuid

        request_id = str(uuid.uuid4())[:8]

        # Set context
        self.logger.set_context(request_id=request_id)

        start_time = time.perf_counter()

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                duration_ms = (time.perf_counter() - start_time) * 1000

                # Log request completion
                self.logger.performance.log_metric(
                    f"request_duration_{scope['method'].lower()}", duration_ms, "ms"
                )

            await send(message)

        # Log request start
        request_data = {
            "method": scope.get("method"),
            "path": scope.get("path"),
            "query_string": scope.get("query_string", b"").decode(),
            "headers": dict(scope.get("headers", [])),
            "client": scope.get("client"),
        }

        self.logger.debug_request(request_data)

        await self.app(scope, receive, send_wrapper)


# Debugging decorators
def debug_function(
    logger: DebugLogger, include_args: bool = False, include_result: bool = False
):
    """Decorator to debug function calls"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__name__}"

            debug_data = {"function": func_name, "event_type": "function_call"}

            if include_args:
                debug_data["args"] = str(args)
                debug_data["kwargs"] = str(kwargs)

            with logger.performance.timer(f"function.{func_name}"):
                try:
                    result = func(*args, **kwargs)

                    if include_result:
                        debug_data["result"] = str(result)[
                            :200
                        ]  # Truncate large results

                    logger.logger.debug(f"Function call: {func_name}", extra=debug_data)
                    return result

                except Exception as e:
                    logger.error_with_context(
                        f"Function {func_name} failed", e, debug_data
                    )
                    raise

        return wrapper

    return decorator


def debug_async_function(
    logger: DebugLogger, include_args: bool = False, include_result: bool = False
):
    """Decorator to debug async function calls"""

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            func_name = f"{func.__module__}.{func.__name__}"

            debug_data = {"function": func_name, "event_type": "async_function_call"}

            if include_args:
                debug_data["args"] = str(args)
                debug_data["kwargs"] = str(kwargs)

            with logger.performance.timer(f"async_function.{func_name}"):
                try:
                    result = await func(*args, **kwargs)

                    if include_result:
                        debug_data["result"] = str(result)[
                            :200
                        ]  # Truncate large results

                    logger.logger.debug(
                        f"Async function call: {func_name}", extra=debug_data
                    )
                    return result

                except Exception as e:
                    logger.error_with_context(
                        f"Async function {func_name} failed", e, debug_data
                    )
                    raise

        return wrapper

    return decorator


# Global debug logger instances
api_logger = DebugLogger("ruleiq.api")
db_logger = DebugLogger("ruleiq.database")
ai_logger = DebugLogger("ruleiq.ai")
security_logger = DebugLogger("ruleiq.security")
compliance_logger = DebugLogger("ruleiq.compliance")
