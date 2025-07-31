"""
Stack Auth Dependencies for FastAPI Routes
Provides dependency functions for Stack Auth integration
"""
from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, Request
from api.middleware.stack_auth_middleware import get_stack_user, validate_stack_token
import logging

logger = logging.getLogger(__name__)


async def get_current_stack_user(request: Request) -> Dict[str, Any]:
    """
    Get current authenticated Stack Auth user
    
    This is the main dependency to use in route handlers that require authentication.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Dict containing user data from Stack Auth
        
    Raises:
        HTTPException: 401 if not authenticated, 503 if auth service unavailable
        
    Example:
        @router.get("/profile")
        async def get_profile(user: dict = Depends(get_current_stack_user)):
            return {"user_id": user["id"], "email": user["primaryEmail"]}
    """
    # Try to get user from request state first (set by middleware)
    if hasattr(request.state, 'user') and request.state.user:
        return request.state.user
    
    # Fallback to direct token validation
    return await get_stack_user(request)


async def get_current_user_id(user: Dict[str, Any] = Depends(get_current_stack_user)) -> str:
    """
    Get just the user ID from Stack Auth user
    
    Args:
        user: User data from get_current_stack_user
        
    Returns:
        User ID string
        
    Example:
        @router.get("/my-data")
        async def get_my_data(user_id: str = Depends(get_current_user_id)):
            return await fetch_user_data(user_id)
    """
    return user["id"]


async def get_current_user_email(user: Dict[str, Any] = Depends(get_current_stack_user)) -> str:
    """
    Get user email from Stack Auth user
    
    Args:
        user: User data from get_current_stack_user
        
    Returns:
        User email string
        
    Example:
        @router.post("/send-notification")
        async def send_notification(email: str = Depends(get_current_user_email)):
            return await send_email(email, "Hello!")
    """
    return user.get("primaryEmail", user.get("email", ""))


async def get_optional_stack_user(request: Request) -> Optional[Dict[str, Any]]:
    """
    Get current Stack Auth user, but don't raise exception if not authenticated
    
    Useful for routes that have different behavior for authenticated vs anonymous users.
    
    Args:
        request: FastAPI request object  
        
    Returns:
        User data dict if authenticated, None if not authenticated
        
    Raises:
        HTTPException: 503 if auth service unavailable (but not for missing auth)
        
    Example:
        @router.get("/public-data")
        async def get_data(user: Optional[dict] = Depends(get_optional_stack_user)):
            if user:
                return await get_personalized_data(user["id"])
            else:
                return await get_public_data()
    """
    try:
        return await get_current_stack_user(request)
    except HTTPException as e:
        if e.status_code == 401:
            return None  # Not authenticated, but that's okay for optional auth
        raise  # Re-raise service unavailable or other errors


async def require_stack_user_with_role(required_role: str):
    """
    Dependency factory for role-based access control
    
    Args:
        required_role: Role name required for access
        
    Returns:
        Dependency function that checks for the required role
        
    Example:
        require_admin = require_stack_user_with_role("admin")
        
        @router.delete("/admin/users/{user_id}")
        async def delete_user(user: dict = Depends(require_admin)):
            return await delete_user_logic()
    """
    async def check_role(user: Dict[str, Any] = Depends(get_current_stack_user)) -> Dict[str, Any]:
        user_roles = user.get("roles", [])
        
        # Check if user has the required role
        has_role = any(
            role.get("name") == required_role or role.get("id") == required_role 
            for role in user_roles
        )
        
        if not has_role:
            logger.warning(f"User {user.get('id')} missing required role: {required_role}")
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required role: {required_role}"
            )
        
        return user
    
    return check_role


# Common role dependencies (these are dependency factories, call them in your routes)
# Example usage: @router.get("/admin-only", dependencies=[Depends(require_stack_user_with_role("admin"))])
# Or: require_admin = require_stack_user_with_role("admin"); @router.get("/admin", dependencies=[Depends(require_admin)])


def get_user_from_token_directly(token: str) -> Dict[str, Any]:
    """
    Synchronous function to get user data from token
    Useful for background tasks or non-async contexts
    
    Args:
        token: Stack Auth access token
        
    Returns:
        User data dictionary
        
    Raises:
        HTTPException: If token validation fails
    """
    import asyncio
    
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(validate_stack_token(token))
    except RuntimeError:
        # No event loop running, create a new one
        return asyncio.run(validate_stack_token(token))


# Legacy compatibility - for gradual migration from JWT
async def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Legacy compatibility function
    Routes using this will be automatically migrated to Stack Auth
    """
    logger.warning("get_current_user is deprecated, use get_current_stack_user instead")
    return await get_current_stack_user(request)


# Export the main dependency for convenience - but don't override the middleware function!
# get_stack_user already imported from middleware, don't reassign it