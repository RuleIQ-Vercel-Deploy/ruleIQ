from __future__ import annotations
import logging
import traceback
import uuid
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

try:
    from config.logging_config import get_logger
    logger = get_logger(__name__)
except Exception:
    import logging
    logger = logging.getLogger(__name__)

from config.settings import settings

try:
    from core.exceptions import ApplicationException
except Exception:
    class ApplicationException(Exception):
        def __init__(self, message: str, status_code: int = 400):
            self.message = message
            self.status_code = status_code

"""
Error Handling Middleware for ruleIQ API.
Provides a global error handler returning standardized JSON responses.
"""


async def error_handler_middleware(request: Request, call_next) ->Any:
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
        logger.warning('%s caught: %s' % (exc.__class__.__name__, exc.
            message), extra={'request_id': request_id, 'status_code': exc.
            status_code})
        return JSONResponse(status_code=exc.status_code, content={'detail':
            exc.message, 'error': {'type': exc.__class__.__name__,
            'message': exc.message, 'request_id': request_id}})
    except ValidationError as exc:
        logger.warning('ValidationError caught', extra={'request_id':
            request_id, 'errors': exc.errors()})
        return JSONResponse(status_code=422, content={'detail': exc.errors(
            ), 'error': {'type': 'ValidationException', 'message':
            'Input validation failed', 'details': exc.errors(),
            'request_id': request_id}})
    except SQLAlchemyError as exc:
        logger.error('SQLAlchemyError caught: %s' % exc, exc_info=settings.
            is_development, extra={'request_id': request_id})
        return JSONResponse(status_code=500, content={'detail':
            'A database error occurred. Please check logs for details.',
            'error': {'type': 'DatabaseException', 'message':
            'A database error occurred. Please check logs for details.',
            'request_id': request_id}})
    except Exception as exc:
        tb = traceback.format_exc()
        logger.critical('Unhandled exception: %s' % exc, exc_info=True,
            extra={'request_id': request_id, 'traceback': tb if settings.
            is_development else 'Omitted'})
        return JSONResponse(status_code=500, content={'detail':
            'An unexpected internal server error occurred.', 'error': {
            'type': 'InternalServerError', 'message':
            'An unexpected internal server error occurred.', 'request_id':
            request_id}})
