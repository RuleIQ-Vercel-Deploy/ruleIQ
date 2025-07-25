"""
RBAC Middleware for Automatic API Protection

Provides middleware that automatically enforces role-based access control
on API endpoints based on route patterns and HTTP methods.
"""

import logging
import time
from typing import Dict, List, Optional, Pattern, Set
from uuid import UUID
import re

from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from api.dependencies.rbac_auth import (
    get_current_user_with_roles, UserWithRoles
)
from database.db_setup import get_db
from services.rbac_service import RBACService


logger = logging.getLogger(__name__)


class RBACMiddleware(BaseHTTPMiddleware):
    """
    Middleware for automatic RBAC enforcement and audit logging.
    
    Automatically checks permissions for protected API routes based on
    HTTP method and path patterns. Logs access attempts for audit purposes.
    """
    
    def __init__(self, app, enable_audit_logging: bool = True):
        super().__init__(app)
        self.enable_audit_logging = enable_audit_logging
        
        # Route protection configuration
        self.route_permissions = self._configure_route_permissions()
        
        # Public routes that don't require authentication
        self.public_routes = {
            "/api/v1/auth/login",
            "/api/v1/auth/login-form", 
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/api/v1/health",
            "/docs",
            "/redoc",
            "/openapi.json"
        }
        
        # Routes that require authentication but no specific permissions
        self.authenticated_only_routes = {
            "/api/v1/auth/me",
            "/api/v1/auth/logout",
            "/api/v1/auth/permissions",
            "/api/v1/auth/framework-access"
        }
    
    def _configure_route_permissions(self) -> Dict[Pattern, Dict[str, List[str]]]:
        """
        Configure route patterns and their required permissions by HTTP method.
        
        Returns:
            Dictionary mapping compiled regex patterns to method permissions
        """
        route_config = {
            # Admin routes - require admin permissions
            r"/api/v1/admin/.*": {
                "GET": ["admin_roles", "admin_permissions", "admin_audit"],
                "POST": ["admin_roles", "admin_permissions"],
                "PUT": ["admin_roles", "admin_permissions"],
                "DELETE": ["admin_roles", "admin_permissions"],
                "PATCH": ["admin_roles", "admin_permissions"]
            },
            
            # User management routes
            r"/api/v1/users/?$": {
                "GET": ["user_list"],
                "POST": ["user_create"]
            },
            r"/api/v1/users/[^/]+/?$": {
                "GET": ["user_list"],
                "PUT": ["user_update"],
                "DELETE": ["user_delete"],
                "PATCH": ["user_update"]
            },
            
            # Framework routes
            r"/api/v1/frameworks/?$": {
                "GET": ["framework_list"],
                "POST": ["framework_create"]
            },
            r"/api/v1/frameworks/[^/]+/?$": {
                "GET": ["framework_list"],
                "PUT": ["framework_update"],
                "DELETE": ["framework_delete"],
                "PATCH": ["framework_update"]
            },
            
            # Assessment routes
            r"/api/v1/assessments/?$": {
                "GET": ["assessment_list"],
                "POST": ["assessment_create"]
            },
            r"/api/v1/assessments/[^/]+/?$": {
                "GET": ["assessment_list"],
                "PUT": ["assessment_update"],
                "DELETE": ["assessment_delete"],
                "PATCH": ["assessment_update"]
            },
            
            # AI Policy routes
            r"/api/v1/policies.*": {
                "GET": ["policy_generate"],
                "POST": ["policy_generate", "policy_refine"],
                "PUT": ["policy_refine"],
                "PATCH": ["policy_refine"]
            },
            
            # Report routes
            r"/api/v1/reports.*": {
                "GET": ["report_view"],
                "POST": ["report_export", "report_schedule"]
            },
            
            # Business profile routes - users can access their own, admins can access any
            r"/api/v1/business-profiles/?$": {
                "GET": ["user_list"],  # Admin level for listing all
                "POST": []  # No special permission - users can create their own
            },
            r"/api/v1/business-profiles/[^/]+/?$": {
                "GET": [],  # Will check ownership or admin permission
                "PUT": [],  # Will check ownership or admin permission  
                "DELETE": ["user_delete"],  # Admin only
                "PATCH": []  # Will check ownership or admin permission
            }
        }
        
        # Compile regex patterns for efficient matching
        return {
            re.compile(pattern): permissions 
            for pattern, permissions in route_config.items()
        }
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Main middleware dispatch method.
        
        Args:
            request: FastAPI request object
            call_next: Next middleware/handler in chain
            
        Returns:
            Response from downstream handler
        """
        start_time = time.time()
        
        try:
            # Skip RBAC for public routes
            if self._is_public_route(request.url.path):
                return await call_next(request)
            
            # Get current user with roles
            current_user = await self._get_current_user(request)
            
            # Check if route requires authentication only
            if self._is_authenticated_only_route(request.url.path):
                if current_user is None:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
                # User is authenticated, proceed
                return await call_next(request)
            
            # Check route permissions
            required_permissions = self._get_required_permissions(
                request.url.path, 
                request.method
            )
            
            if required_permissions:
                if current_user is None:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
                
                # Check if user has required permissions
                if not self._check_permissions(current_user, required_permissions, request):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Insufficient permissions"
                    )
            
            # Add user to request state for downstream handlers
            if current_user:
                request.state.current_user = current_user
            
            # Process request
            response = await call_next(request)
            
            # Audit log successful access
            if self.enable_audit_logging and current_user:
                await self._log_access(
                    current_user, request, response.status_code, 
                    time.time() - start_time
                )
            
            return response
            
        except HTTPException as e:
            # Audit log failed access attempts
            if self.enable_audit_logging:
                await self._log_access_failure(
                    request, e.status_code, str(e.detail),
                    time.time() - start_time
                )
            raise
        
        except Exception as e:
            # Log unexpected errors
            logger.error(f"RBAC middleware error: {e}", exc_info=True)
            
            if self.enable_audit_logging:
                await self._log_access_failure(
                    request, 500, f"Internal error: {str(e)}",
                    time.time() - start_time
                )
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    def _is_public_route(self, path: str) -> bool:
        """Check if route is public (no authentication required)."""
        return any(path.startswith(route) for route in self.public_routes)
    
    def _is_authenticated_only_route(self, path: str) -> bool:
        """Check if route requires authentication but no specific permissions."""
        return any(path.startswith(route) for route in self.authenticated_only_routes)
    
    async def _get_current_user(self, request: Request) -> Optional[UserWithRoles]:
        """
        Extract current user from request token.
        
        Args:
            request: FastAPI request object
            
        Returns:
            UserWithRoles instance or None if not authenticated
        """
        try:
            # Extract token from Authorization header
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return None
            
            token = auth_header.split(" ")[1]
            
            # Get database session
            db = next(get_db())
            try:
                # Import decode_token and validate token
                from api.dependencies.auth import decode_token
                
                # Decode and validate token
                payload = decode_token(token)
                if not payload or payload.get("type") != "access":
                    return None
                
                # Get user ID from token
                user_id_str = payload.get("sub")
                if not user_id_str:
                    return None
                
                try:
                    user_id = UUID(user_id_str)
                except ValueError:
                    return None
                
                # Get user from database
                from database.user import User
                user = db.query(User).filter(User.id == user_id).first()
                if not user or not user.is_active:
                    return None
                
                # Get user roles and permissions using RBAC service
                rbac = RBACService(db)
                roles = rbac.get_user_roles(user.id)
                permissions = rbac.get_user_permissions(user.id)
                accessible_frameworks = rbac.get_accessible_frameworks(user.id)
                
                return UserWithRoles(user, roles, permissions, accessible_frameworks)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.debug(f"Failed to get current user: {e}")
            return None
    
    def _get_required_permissions(self, path: str, method: str) -> List[str]:
        """
        Get required permissions for a route and method.
        
        Args:
            path: Request path
            method: HTTP method
            
        Returns:
            List of required permissions
        """
        for pattern, method_permissions in self.route_permissions.items():
            if pattern.match(path):
                return method_permissions.get(method, [])
        
        return []  # No specific permissions required
    
    def _check_permissions(self, user: UserWithRoles, required_permissions: List[str], request: Request) -> bool:
        """
        Check if user has required permissions for the request.
        
        Args:
            user: User with roles and permissions
            required_permissions: List of required permissions
            request: FastAPI request object
            
        Returns:
            True if user has required permissions
        """
        if not required_permissions:
            return True
        
        # Special handling for business profile routes - check ownership
        if "/business-profiles/" in request.url.path and request.method in ["GET", "PUT", "PATCH"]:
            return self._check_business_profile_access(user, request)
        
        # Check if user has any of the required permissions
        return user.has_any_permission(required_permissions)
    
    def _check_business_profile_access(self, user: UserWithRoles, request: Request) -> bool:
        """
        Check business profile access - users can access their own profiles,
        admins can access any profile.
        
        Args:
            user: User with roles
            request: FastAPI request object
            
        Returns:
            True if access allowed
        """
        # Admins can access any profile
        if user.has_any_permission(["admin_roles", "user_list"]):
            return True
        
        # Extract profile ID from URL path
        path_parts = request.url.path.strip("/").split("/")
        if len(path_parts) >= 3 and path_parts[-1]:
            try:
                profile_user_id = UUID(path_parts[-1])
                # Users can access their own profile
                return profile_user_id == user.id
            except ValueError:
                # Invalid UUID in path
                return False
        
        # For listing endpoint, require admin permission
        return False
    
    async def _log_access(self, user: UserWithRoles, request: Request, 
                         status_code: int, duration: float):
        """
        Log successful access for audit purposes.
        
        Args:
            user: User who made the request
            request: FastAPI request object
            status_code: HTTP response status code
            duration: Request processing duration in seconds
        """
        try:
            db = next(get_db())
            try:
                rbac = RBACService(db)
                rbac._log_audit(
                    user_id=user.id,
                    action="api_access",
                    details={
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": status_code,
                        "duration_ms": round(duration * 1000, 2),
                        "user_agent": request.headers.get("user-agent"),
                        "ip_address": getattr(request.client, "host", None),
                        "roles": [role["name"] for role in user.roles],
                        "permissions_count": len(user.permissions)
                    }
                )
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Failed to log access: {e}")
    
    async def _log_access_failure(self, request: Request, status_code: int, 
                                 reason: str, duration: float):
        """
        Log failed access attempts for security monitoring.
        
        Args:
            request: FastAPI request object
            status_code: HTTP response status code
            reason: Failure reason
            duration: Request processing duration in seconds
        """
        try:
            db = next(get_db())
            try:
                rbac = RBACService(db)
                rbac._log_audit(
                    user_id=None,  # No user for failed access
                    action="api_access_denied",
                    details={
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": status_code,
                        "reason": reason,
                        "duration_ms": round(duration * 1000, 2),
                        "user_agent": request.headers.get("user-agent"),
                        "ip_address": getattr(request.client, "host", None)
                    }
                )
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Failed to log access failure: {e}")


class RBACRouteProtector:
    """
    Decorator-based route protection for specific endpoints.
    
    Use this for fine-grained permission control on individual routes
    that need custom logic beyond the middleware patterns.
    """
    
    @staticmethod
    def require_permissions(permissions: List[str]):
        """
        Decorator to require specific permissions for a route.
        
        Args:
            permissions: List of required permissions
            
        Returns:
            Route decorator
        """
        def decorator(func):
            func._required_permissions = permissions
            return func
        return decorator
    
    @staticmethod
    def require_framework_access(framework_id: str, access_level: str = "read"):
        """
        Decorator to require framework access for a route.
        
        Args:
            framework_id: Framework ID to check
            access_level: Required access level
            
        Returns:
            Route decorator
        """
        def decorator(func):
            func._required_framework_access = (framework_id, access_level)
            return func
        return decorator
    
    @staticmethod
    def admin_only(func):
        """
        Decorator to restrict route to admin users only.
        
        Args:
            func: Route function
            
        Returns:
            Decorated function
        """
        func._admin_only = True
        return func


# Convenience decorators for common permission patterns
def require_admin(func):
    """Decorator for admin-only routes."""
    return RBACRouteProtector.admin_only(func)

def require_permissions(*permissions):
    """Decorator for routes requiring specific permissions."""
    return RBACRouteProtector.require_permissions(list(permissions))

def require_framework_access(framework_id: str, access_level: str = "read"):
    """Decorator for routes requiring framework access."""
    return RBACRouteProtector.require_framework_access(framework_id, access_level)