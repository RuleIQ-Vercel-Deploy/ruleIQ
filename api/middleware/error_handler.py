"""
Error Handling Middleware for ComplianceGPT API

This module provides a global error handler that catches exceptions and returns
a standardized JSON response, leveraging the custom exception hierarchy.
"""

import traceback
import uuid

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from config.logging_config import get_logger
from config.settings import settings
from core.exceptions import ApplicationException

logger = get_logger(__name__)

async def error_handler_middleware(request: Request, call_next):
    """
    Global error handling middleware.

    Catches all exceptions and formats them into a standardized JSON response.
    It handles custom ApplicationExceptions, Pydantic ValidationErrors,
    SQLAlchemyErrors, and generic Python Exceptions.
    """
    request_id = str(uuid.uuid4())
    try:
        return await call_next(request)

    except ApplicationException as exc:
        # Handle custom application exceptions defined in core/exceptions.py
        logger.warning(
            f"{exc.__class__.__name__} caught: {exc.message}",
            extra={"request_id": request_id, "status_code": exc.status_code},
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.message,  # FastAPI standard field for compatibility
                "error": {
                    "type": exc.__class__.__name__,
                    "message": exc.message,
                    "request_id": request_id,
                },
            },
        )

    except ValidationError as exc:
        # Handle Pydantic's input validation errors
        logger.warning(
            "ValidationError caught", extra={"request_id": request_id, "errors": exc.errors()}
        )
        return JSONResponse(
            status_code=422,  # Unprocessable Entity
            content={
                "detail": exc.errors(),  # FastAPI standard field for validation errors
                "error": {
                    "type": "ValidationException",
                    "message": "Input validation failed",
                    "details": exc.errors(),
                    "request_id": request_id,
                },
            },
        )

    except SQLAlchemyError as exc:
        # Handle generic database errors
        logger.error(
            f"SQLAlchemyError caught: {exc}",
            exc_info=settings.is_development,
            extra={"request_id": request_id},
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "A database error occurred. Please check logs for details.",
                "error": {
                    "type": "DatabaseException",
                    "message": "A database error occurred. Please check logs for details.",
                    "request_id": request_id,
                },
            },
        )

    except Exception as exc:
        # Catch-all for any other unexpected errors
        tb = traceback.format_exc()
        logger.critical(
            f"Unhandled exception: {exc}",
            exc_info=True,
            extra={
                "request_id": request_id,
                "traceback": tb if settings.is_development else "Omitted",
            },
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An unexpected internal server error occurred.",
                "error": {
                    "type": "InternalServerError",
                    "message": "An unexpected internal server error occurred.",
                    "request_id": request_id,
                },
            },
        )
