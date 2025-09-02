"""
API Key Authentication Middleware
"""

from typing import Optional, Tuple
from fastapi import Request, HTTPException, status
from fastapi.security.utils import get_authorization_scheme_param
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

from services.api_key_management import APIKeyManager
from services.redis_client import get_redis_client
from database.db_setup import get_db

logger = logging.getLogger(__name__)


class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API key authentication on specific routes.

    This middleware:
    1. Checks for API key in X-API-Key header
    2. Validates the API key
    3. Enforces rate limits
    4. Adds organization context to request
    """

    def __init__(self, app, protected_prefixes: list = None) -> None:
        super().__init__(app)
        self.protected_prefixes = protected_prefixes or [
            "/api/v1/business-profiles",
            "/api/v1/assessments",
            "/api/v1/compliance",
            "/api/v1/policies",
            "/api/v1/evidence",
            "/api/v1/reports",
        ]

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process the request through API key authentication."""

        # Check if path requires API key authentication
        if not self._requires_api_key_auth(request.url.path):
            return await call_next(request)

        # Check for API key in header
        api_key = request.headers.get("X-API-Key")

        # Also check Authorization header as fallback
        if not api_key:
            authorization = request.headers.get("Authorization")
            if authorization:
                scheme, credentials = get_authorization_scheme_param(authorization)
                if scheme.lower() == "apikey":
                    api_key = credentials

        if not api_key:
            # No API key provided, let it fall through to JWT auth
            return await call_next(request)

        # Validate API key
        try:
            is_valid, metadata, error = await self._validate_api_key(api_key, request)

            if not is_valid:
                logger.warning(f"Invalid API key attempt: {error}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=error or "Invalid API key",
                )

            # Add metadata to request state for use in endpoints
            request.state.api_key_metadata = metadata
            request.state.is_api_key_auth = True
            request.state.organization_id = metadata.organization_id
            request.state.organization_name = metadata.organization_name

            # Log successful API key usage
            logger.info(
                f"API key authenticated: org={metadata.organization_name}, "
                f"key_type={metadata.key_type}, endpoint={request.url.path}"
            )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"API key validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication service unavailable",
            )

        response = await call_next(request)
        return response

    def _requires_api_key_auth(self, path: str) -> bool:
        """Check if the path requires API key authentication."""
        for prefix in self.protected_prefixes:
            if path.startswith(prefix):
                return True
        return False

    async def _validate_api_key(
        self, api_key: str, request: Request
    ) -> Tuple[bool, Optional[dict], Optional[str]]:
        """Validate API key using the APIKeyManager."""
        try:
            # Get database and Redis connections
            async for db in get_db():
                redis_client = await get_redis_client()

                manager = APIKeyManager(db, redis_client)

                # Validate the API key
                is_valid, metadata, error = await manager.validate_api_key(
                    api_key=api_key,
                    request_ip=request.client.host,
                    request_origin=request.headers.get("Origin"),
                    required_scope=self._get_required_scope(request.url.path),
                    endpoint=request.url.path,
                    method=request.method,
                )

                return is_valid, metadata, error

        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            return False, None, "Authentication service error"

    def _get_required_scope(self, path: str) -> Optional[str]:
        """Get the required scope for a given path."""
        # Map paths to required scopes
        scope_mapping = {
            "/api/v1/business-profiles": "business_profiles",
            "/api/v1/assessments": "assessments",
            "/api/v1/compliance": "compliance",
            "/api/v1/policies": "policies",
            "/api/v1/evidence": "evidence",
            "/api/v1/reports": "reports",
        }

        for prefix, scope in scope_mapping.items():
            if path.startswith(prefix):
                return scope

        return None


def get_api_key_from_request(request: Request) -> Optional[str]:
    """Extract API key from request headers."""
    # Check X-API-Key header first
    api_key = request.headers.get("X-API-Key")

    if api_key:
        return api_key

    # Check Authorization header as fallback
    authorization = request.headers.get("Authorization")
    if authorization:
        scheme, credentials = get_authorization_scheme_param(authorization)
        if scheme.lower() == "apikey":
            return credentials

    return None
