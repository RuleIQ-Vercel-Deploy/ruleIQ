"""
Error Handling Middleware for ruleIQ API.
Provides a global error handler returning standardized JSON responses.
"""

from __future__ import annotations

import logging
import traceback
import uuid
from typing import Any, Callable

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

# Initialize logger
try:
    from config.logging_config import get_logger
    logger = get_logger(__name__)
except Exception:
    logger = logging.getLogger(__name__)

# Import settings
try:
    from config.settings import settings
    is_development = getattr(settings, 'is_development', False) or getattr(settings, 'debug', False)
except Exception:
    is_development = False

# Import custom exceptions if available
try:
    from core.exceptions import ApplicationException
except Exception:
    class ApplicationException(Exception):
        """Fallback ApplicationException if core.exceptions is not available."""
        def __init__(self, message: str, status_code: int = 400):
            self.message = message
            self.status_code = status_code
            super().__init__(message)


async def error_handler_middleware(request: Request, call_next: Callable) -> Any:
    """
    Global error handling middleware.

    Catches all exceptions and formats them into a standardized JSON response.
    It handles custom ApplicationExceptions, Pydantic ValidationErrors,
    SQLAlchemyErrors, and generic Python Exceptions.
    
    Args:
        request: The incoming HTTP request
        call_next: The next middleware or route handler
    
    Returns:
        The response from the next handler or an error response
    """
    request_id = str(uuid.uuid4())
    
    try:
        # Call the next middleware or route handler
        response = await call_next(request)
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions to be handled by FastAPI
        raise
        
    except ApplicationException as exc:
        logger.warning(
            '%s caught: %s', 
            exc.__class__.__name__, 
            exc.message,
            extra={'request_id': request_id, 'status_code': exc.status_code}
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                'detail': exc.message,
                'error': {
                    'type': exc.__class__.__name__,
                    'message': exc.message,
                    'request_id': request_id
                }
            }
        )
        
    except ValidationError as exc:
        logger.warning(
            'ValidationError caught',
            extra={'request_id': request_id, 'errors': exc.errors()}
        )
        return JSONResponse(
            status_code=422,
            content={
                'detail': exc.errors(),
                'error': {
                    'type': 'ValidationException',
                    'message': 'Input validation failed',
                    'details': exc.errors(),
                    'request_id': request_id
                }
            }
        )
        
    except SQLAlchemyError as exc:
        logger.error(
            'SQLAlchemyError caught: %s',
            exc,
            exc_info=is_development,
            extra={'request_id': request_id}
        )
        return JSONResponse(
            status_code=500,
            content={
                'detail': 'A database error occurred. Please check logs for details.',
                'error': {
                    'type': 'DatabaseException',
                    'message': 'A database error occurred. Please check logs for details.',
                    'request_id': request_id
                }
            }
        )
        
    except Exception as exc:
        tb = traceback.format_exc()
        logger.critical(
            'Unhandled exception: %s',
            exc,
            exc_info=True,
            extra={
                'request_id': request_id,
                'traceback': tb if is_development else 'Omitted'
            }
        )
        
        # In Cloud Run, provide minimal error details for security
        if not is_development:
            return JSONResponse(
                status_code=500,
                content={
                    'detail': 'An unexpected internal server error occurred.',
                    'error': {
                        'type': 'InternalServerError',
                        'message': 'An unexpected internal server error occurred.',
                        'request_id': request_id
                    }
                }
            )
        else:
            # In development, provide more details
            return JSONResponse(
                status_code=500,
                content={
                    'detail': str(exc),
                    'error': {
                        'type': 'InternalServerError',
                        'message': str(exc),
                        'request_id': request_id,
                        'traceback': tb[:1000]  # Limit traceback size
                    }
                }
            )