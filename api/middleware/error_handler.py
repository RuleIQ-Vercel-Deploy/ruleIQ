"""
Error Handling Middleware for ComplianceGPT API

This module provides comprehensive error handling middleware with
proper logging, error formatting, and response standardization.
"""

import traceback
import uuid
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from config.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)


class APIError(Exception):
    """Base API error class"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or "INTERNAL_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class ValidationAPIError(APIError):
    """Validation error"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=422,
            error_code="VALIDATION_ERROR",
            details=details
        )


class AuthenticationError(APIError):
    """Authentication error"""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(APIError):
    """Authorization error"""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR"
        )


class NotFoundError(APIError):
    """Resource not found error"""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND"
        )


class ConflictError(APIError):
    """Resource conflict error"""

    def __init__(self, message: str = "Resource conflict"):
        super().__init__(
            message=message,
            status_code=409,
            error_code="CONFLICT_ERROR"
        )


class RateLimitError(APIError):
    """Rate limit exceeded error"""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED"
        )


async def error_handler_middleware(request: Request, call_next):
    """Global error handling middleware"""

    # Generate request ID for tracking
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    try:
        # Process the request
        response = await call_next(request)
        return response

    except Exception as exc:
        # Log the error with request context
        error_context = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
        }

        logger.log_error(exc, error_context)

        # Handle different types of errors
        if isinstance(exc, APIError):
            return create_error_response(
                message=exc.message,
                status_code=exc.status_code,
                error_code=exc.error_code,
                details=exc.details,
                request_id=request_id
            )

        elif isinstance(exc, HTTPException):
            return create_error_response(
                message=exc.detail,
                status_code=exc.status_code,
                error_code="HTTP_ERROR",
                request_id=request_id
            )

        elif isinstance(exc, ValidationError):
            return create_error_response(
                message="Validation error",
                status_code=422,
                error_code="VALIDATION_ERROR",
                details={"validation_errors": exc.errors()},
                request_id=request_id
            )

        elif isinstance(exc, IntegrityError):
            return create_error_response(
                message="Database integrity constraint violation",
                status_code=409,
                error_code="INTEGRITY_ERROR",
                request_id=request_id
            )

        elif isinstance(exc, SQLAlchemyError):
            return create_error_response(
                message="Database error occurred",
                status_code=500,
                error_code="DATABASE_ERROR",
                request_id=request_id
            )

        else:
            # Generic error handling
            error_message = "Internal server error"
            if settings.is_development:
                error_message = str(exc)

            return create_error_response(
                message=error_message,
                status_code=500,
                error_code="INTERNAL_ERROR",
                details={"traceback": traceback.format_exc()} if settings.is_development else None,
                request_id=request_id
            )


def create_error_response(
    message: str,
    status_code: int,
    error_code: str,
    details: Optional[Dict[str, Any]] = None,
    request_id: Optional[str] = None
) -> JSONResponse:
    """Create standardized error response"""

    error_response = {
        "error": {
            "message": message,
            "code": error_code,
            "status_code": status_code,
        }
    }

    if details:
        error_response["error"]["details"] = details

    if request_id:
        error_response["error"]["request_id"] = request_id

    # Add timestamp
    from datetime import datetime
    error_response["error"]["timestamp"] = datetime.utcnow().isoformat()

    return JSONResponse(
        status_code=status_code,
        content=error_response
    )


class ErrorHandler:
    """Utility class for consistent error handling in routes"""

    @staticmethod
    def handle_validation_error(errors: list, message: str = "Validation failed"):
        """Handle validation errors consistently"""
        raise ValidationAPIError(
            message=message,
            details={"validation_errors": errors}
        )

    @staticmethod
    def handle_not_found(resource: str, identifier: Optional[str] = None):
        """Handle not found errors consistently"""
        message = f"{resource} not found"
        if identifier:
            message += f" with ID: {identifier}"
        raise NotFoundError(message)

    @staticmethod
    def handle_conflict(resource: str, reason: Optional[str] = None):
        """Handle conflict errors consistently"""
        message = f"{resource} conflict"
        if reason:
            message += f": {reason}"
        raise ConflictError(message)

    @staticmethod
    def handle_unauthorized(message: str = "Authentication required"):
        """Handle authentication errors consistently"""
        raise AuthenticationError(message)

    @staticmethod
    def handle_forbidden(message: str = "Insufficient permissions"):
        """Handle authorization errors consistently"""
        raise AuthorizationError(message)
