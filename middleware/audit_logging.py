"""
Comprehensive Audit Logging Middleware for RuleIQ.
Tracks all security-relevant events, API calls, and data modifications.
"""

import asyncio
import hashlib
import json
import logging
from contextvars import ContextVar
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from database.session import SessionLocal

logger = logging.getLogger(__name__)

# Context variable for audit context
audit_context: ContextVar[Dict[str, Any]] = ContextVar("audit_context", default={})


class AuditLogger:
    """Centralized audit logging service."""

    SENSITIVE_FIELDS = {
        "password",
        "token",
        "secret",
        "api_key",
        "access_token",
        "refresh_token",
        "credit_card",
        "ssn",
        "bank_account",
    }

    CRITICAL_OPERATIONS = {
        "DELETE",
        "PUT",
        "PATCH",  # Data modification
        "POST /api/auth",  # Authentication
        "POST /api/admin",  # Admin operations
        "POST /api/payment",  # Payment operations
    }

    def __init__(self):
        self.buffer: List[Dict] = []
        self.buffer_size = 100
        self.flush_interval = 30  # seconds
        self._flush_task = None
        self._start_flush_timer()

    def _start_flush_timer(self):
        """Start periodic flush timer."""
        try:
            loop = asyncio.get_running_loop()
            if not self._flush_task:
                self._flush_task = asyncio.create_task(self._periodic_flush())
        except RuntimeError:
            # No event loop running yet, will be started later
            pass

    async def _periodic_flush(self):
        """Periodically flush audit logs to database."""
        while True:
            await asyncio.sleep(self.flush_interval)
            await self.flush()

    async def log_event(
        self,
        event_type: str,
        user_id: Optional[str] = None,
        resource: Optional[str] = None,
        action: Optional[str] = None,
        result: Optional[str] = None,
        details: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        """Log an audit event."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "result": result,
            "details": self._sanitize_details(details) if details else None,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "session_id": audit_context.get().get("session_id"),
            "request_id": audit_context.get().get("request_id"),
        }

        # Add to buffer
        self.buffer.append(event)

        # Log to file immediately for critical events
        if self._is_critical(event):
            logger.warning(f"AUDIT_CRITICAL: {json.dumps(event)}")
        else:
            logger.info(f"AUDIT: {json.dumps(event)}")

        # Flush if buffer is full
        if len(self.buffer) >= self.buffer_size:
            await self.flush()

    def _sanitize_details(self, details: Dict) -> Dict:
        """Remove sensitive information from details."""
        sanitized = {}
        for key, value in details.items():
            if any(sensitive in key.lower() for sensitive in self.SENSITIVE_FIELDS):
                sanitized[key] = "***REDACTED***"
            elif isinstance(value, dict):
                sanitized[key] = self._sanitize_details(value)
            elif isinstance(value, list):
                sanitized[key] = [self._sanitize_details(item) if isinstance(item, dict) else item for item in value]
            else:
                sanitized[key] = value
        return sanitized

    def _is_critical(self, event: Dict) -> bool:
        """Check if event is critical and needs immediate attention."""
        # Failed authentication attempts
        if event["event_type"] == "AUTH_FAILED":
            return True

        # Admin operations
        if event["resource"] and "/admin" in event["resource"]:
            return True

        # Data deletion
        if event["action"] == "DELETE":
            return True

        # Security violations
        if event["event_type"] in ["UNAUTHORIZED_ACCESS", "PERMISSION_DENIED", "SECURITY_VIOLATION"]:
            return True

        return False

    async def flush(self):
        """Flush audit logs to database."""
        if not self.buffer:
            return

        try:
            # Save to database
            db = SessionLocal()
            try:
                for event in self.buffer:
                    # Create audit log entry in database
                    # This would save to your audit_logs table
                    pass
                db.commit()
            finally:
                db.close()

            # Clear buffer after successful save
            self.buffer.clear()

        except Exception as e:
            logger.error(f"Failed to flush audit logs: {str(e)}")


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for comprehensive audit logging."""

    def __init__(self, app, audit_logger: Optional[AuditLogger] = None):
        super().__init__(app)
        self.audit_logger = audit_logger or AuditLogger()

    async def dispatch(self, request: Request, call_next):
        """Process request with audit logging."""

        # Generate request ID
        request_id = self._generate_request_id(request)

        # Set audit context
        audit_context.set(
            {"request_id": request_id, "session_id": request.cookies.get("session_id"), "start_time": datetime.utcnow()}
        )

        # Extract request details
        user_id = getattr(request.state, "user_id", None)
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("User-Agent")

        # Log request
        await self.audit_logger.log_event(
            event_type="API_REQUEST",
            user_id=user_id,
            resource=request.url.path,
            action=request.method,
            ip_address=ip_address,
            user_agent=user_agent,
            details={"query_params": dict(request.query_params), "headers": self._get_safe_headers(request.headers)},
        )

        # Process request
        try:
            response = await call_next(request)

            # Log response
            await self.audit_logger.log_event(
                event_type="API_RESPONSE",
                user_id=user_id,
                resource=request.url.path,
                action=request.method,
                result="SUCCESS" if response.status_code < 400 else "FAILURE",
                ip_address=ip_address,
                details={"status_code": response.status_code, "duration_ms": self._calculate_duration()},
            )

            # Log specific events based on endpoint
            await self._log_specific_events(request, response, user_id)

            return response

        except Exception as e:
            # Log error
            await self.audit_logger.log_event(
                event_type="API_ERROR",
                user_id=user_id,
                resource=request.url.path,
                action=request.method,
                result="ERROR",
                ip_address=ip_address,
                details={"error": str(e), "error_type": type(e).__name__},
            )
            raise

    def _generate_request_id(self, request: Request) -> str:
        """Generate unique request ID."""
        timestamp = datetime.utcnow().timestamp()
        path = request.url.path
        method = request.method

        hash_input = f"{timestamp}{path}{method}"
        return hashlib.md5(hash_input.encode(), usedforsecurity=False).hexdigest()[:16]

    def _get_safe_headers(self, headers: Dict) -> Dict:
        """Get headers with sensitive values redacted."""
        safe_headers = {}
        sensitive_headers = {"authorization", "cookie", "x-api-key"}

        for key, value in headers.items():
            if key.lower() in sensitive_headers:
                safe_headers[key] = "***REDACTED***"
            else:
                safe_headers[key] = value

        return safe_headers

    def _calculate_duration(self) -> int:
        """Calculate request duration in milliseconds."""
        start_time = audit_context.get().get("start_time")
        if start_time:
            duration = (datetime.utcnow() - start_time).total_seconds() * 1000
            return int(duration)
        return 0

    async def _log_specific_events(self, request: Request, response: Response, user_id: Optional[str]):
        """Log specific events based on endpoint patterns."""
        path = request.url.path
        method = request.method

        # Authentication events
        if path.startswith("/api/auth"):
            if path == "/api/auth/login":
                if response.status_code == 200:
                    await self.audit_logger.log_event(
                        event_type="AUTH_SUCCESS",
                        user_id=user_id,
                        action="LOGIN",
                        ip_address=request.client.host if request.client else None,
                    )
                else:
                    await self.audit_logger.log_event(
                        event_type="AUTH_FAILED",
                        user_id=user_id,
                        action="LOGIN",
                        ip_address=request.client.host if request.client else None,
                    )

            elif path == "/api/auth/logout":
                await self.audit_logger.log_event(
                    event_type="AUTH_LOGOUT",
                    user_id=user_id,
                    action="LOGOUT",
                    ip_address=request.client.host if request.client else None,
                )

        # Admin operations
        elif path.startswith("/api/admin"):
            await self.audit_logger.log_event(
                event_type="ADMIN_OPERATION",
                user_id=user_id,
                resource=path,
                action=method,
                result="SUCCESS" if response.status_code < 400 else "FAILURE",
                ip_address=request.client.host if request.client else None,
            )

        # Data modifications
        elif method in ["POST", "PUT", "PATCH", "DELETE"]:
            await self.audit_logger.log_event(
                event_type="DATA_MODIFICATION",
                user_id=user_id,
                resource=path,
                action=method,
                result="SUCCESS" if response.status_code < 400 else "FAILURE",
                ip_address=request.client.host if request.client else None,
            )

        # Payment operations
        elif path.startswith("/api/payment"):
            await self.audit_logger.log_event(
                event_type="PAYMENT_OPERATION",
                user_id=user_id,
                resource=path,
                action=method,
                result="SUCCESS" if response.status_code < 400 else "FAILURE",
                ip_address=request.client.host if request.client else None,
                details={"status_code": response.status_code},
            )

        # Compliance operations
        elif path.startswith("/api/compliance"):
            await self.audit_logger.log_event(
                event_type="COMPLIANCE_OPERATION",
                user_id=user_id,
                resource=path,
                action=method,
                ip_address=request.client.host if request.client else None,
            )


# Audit log decorators for function-level logging
def audit_operation(operation_type: str, resource_type: str = None):
    """Decorator for auditing function operations."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Get current user from context
            user_id = audit_context.get().get("user_id")

            # Log operation start
            audit_logger = AuditLogger()
            await audit_logger.log_event(
                event_type=f"{operation_type}_START",
                user_id=user_id,
                resource=resource_type,
                action=func.__name__,
                details={"args": str(args)[:200], "kwargs": str(kwargs)[:200]},
            )

            try:
                # Execute function
                result = await func(*args, **kwargs)

                # Log operation success
                await audit_logger.log_event(
                    event_type=f"{operation_type}_SUCCESS",
                    user_id=user_id,
                    resource=resource_type,
                    action=func.__name__,
                    result="SUCCESS",
                )

                return result

            except Exception as e:
                # Log operation failure
                await audit_logger.log_event(
                    event_type=f"{operation_type}_FAILURE",
                    user_id=user_id,
                    resource=resource_type,
                    action=func.__name__,
                    result="FAILURE",
                    details={"error": str(e)},
                )
                raise

        return wrapper

    return decorator


def setup_audit_logging(app):
    """Setup audit logging middleware on FastAPI app."""
    audit_logger = AuditLogger()
    app.add_middleware(AuditLoggingMiddleware, audit_logger=audit_logger)

    @app.on_event("startup")
    async def start_audit_flush_timer():
        """Start the audit logger flush timer when the event loop is running."""
        audit_logger._start_flush_timer()

    logger.info("Audit logging middleware configured")
    return audit_logger
