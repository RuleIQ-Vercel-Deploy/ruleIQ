"""
Stack Auth Middleware for FastAPI
Validates Stack Auth tokens via REST API calls
"""
import asyncio
import httpx
import json
from typing import Optional, Dict, Any
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

# Stack Auth configuration
STACK_PROJECT_ID = os.getenv("STACK_PROJECT_ID")
STACK_SECRET_SERVER_KEY = os.getenv("STACK_SECRET_SERVER_KEY")
STACK_API_URL = os.getenv("STACK_API_URL", "https://api.stack-auth.com")

# Token cache to avoid repeated API calls
token_cache: Dict[str, Dict[str, Any]] = {}
CACHE_DURATION = timedelta(minutes=5)

security = HTTPBearer(auto_error=False)


class StackAuthError(Exception):
    """Custom exception for Stack Auth errors"""
    pass


async def validate_stack_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Validate Stack Auth token via REST API
    
    Args:
        token: The access token to validate
        
    Returns:
        User data if token is valid, None if invalid
        
    Raises:
        StackAuthError: If validation fails due to service issues
    """
    if not STACK_PROJECT_ID or not STACK_SECRET_SERVER_KEY:
        logger.error("Stack Auth environment variables not configured")
        raise StackAuthError("Stack Auth not configured")
    
    # Check cache first
    cache_key = f"token:{token[:20]}..."  # Use partial token for cache key
    if cache_key in token_cache:
        cached_data = token_cache[cache_key]
        if datetime.now() < cached_data["expires"]:
            logger.debug("Using cached token validation")
            return cached_data["user"]
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Stack Auth token validation endpoint
            response = await client.get(
                f"{STACK_API_URL}/api/v1/users/me",
                headers={
                    "Authorization": f"Bearer {token}",
                    "x-stack-project-id": STACK_PROJECT_ID,
                    "x-stack-secret-server-key": STACK_SECRET_SERVER_KEY,
                    "x-stack-access-type": "server",
                }
            )
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Cache the validation result
                token_cache[cache_key] = {
                    "user": user_data,
                    "expires": datetime.now() + CACHE_DURATION
                }
                
                logger.debug(f"Token validated for user: {user_data.get('id', 'unknown')}")
                return user_data
                
            elif response.status_code == 401:
                logger.debug("Invalid or expired token")
                return None
                
            else:
                logger.error(f"Stack Auth API error: {response.status_code} - {response.text}")
                raise StackAuthError(f"Token validation failed: {response.status_code}")
                
    except httpx.TimeoutException:
        logger.error("Stack Auth API timeout")
        raise StackAuthError("Token validation timeout")
    except httpx.RequestError as e:
        logger.error(f"Stack Auth API request error: {e}")
        raise StackAuthError("Token validation request failed")
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {e}")
        raise StackAuthError("Token validation error")


async def get_stack_user(request: Request) -> Dict[str, Any]:
    """
    FastAPI dependency to get current Stack Auth user
    
    Args:
        request: FastAPI request object
        
    Returns:
        User data dictionary
        
    Raises:
        HTTPException: If authentication fails
    """
    # Extract token from Authorization header
    authorization = request.headers.get("Authorization")
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = authorization.split(" ")[1]
    
    try:
        user_data = await validate_stack_token(token)
        if not user_data:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return user_data
        
    except StackAuthError as e:
        logger.error(f"Stack Auth error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Authentication service unavailable"
        )


class StackAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle Stack Auth token validation
    Automatically validates tokens for protected routes
    """
    
    # Routes that don't require authentication
    EXCLUDED_PATHS = {
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/auth/google",
        "/api/v1/auth/google/callback",
        "/api/test-utils/cleanup-users",
        "/api/test-utils/create-user", 
        "/api/test-utils/clear-rate-limits",
        "/api/monitoring/health",
        "/api/monitoring/prometheus"
    }
    
    def __init__(self, app, enable_cache: bool = True):
        super().__init__(app)
        self.enable_cache = enable_cache
        logger.info("Stack Auth middleware initialized")
    
    async def dispatch(self, request: Request, call_next):
        # Skip authentication for excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)
        
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Validate Stack Auth token for protected routes
        try:
            user_data = await get_stack_user(request)
            # Add user data to request state for use in route handlers
            request.state.user = user_data
            logger.debug(f"Authenticated user: {user_data.get('id')} for {request.url.path}")
            
        except HTTPException as e:
            # Return the authentication error
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail},
                headers=e.headers or {}
            )
        except Exception as e:
            logger.error(f"Unexpected error in Stack Auth middleware: {e}")
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )
        
        return await call_next(request)


def clear_token_cache():
    """Clear the token validation cache"""
    global token_cache
    token_cache.clear()
    logger.info("Token cache cleared")


def get_cache_stats() -> Dict[str, Any]:
    """Get token cache statistics"""
    now = datetime.now()
    valid_entries = sum(1 for data in token_cache.values() if now < data["expires"])
    expired_entries = len(token_cache) - valid_entries
    
    return {
        "total_entries": len(token_cache),
        "valid_entries": valid_entries,
        "expired_entries": expired_entries,
        "cache_duration_minutes": CACHE_DURATION.total_seconds() / 60
    }