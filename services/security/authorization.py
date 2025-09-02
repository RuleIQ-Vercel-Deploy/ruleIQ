"""
Fine-grained Authorization Service
Implements RBAC, resource-level permissions, and dynamic permission evaluation
"""

from typing import Dict, List, Optional, Any, Set
from datetime import datetime, time
from enum import Enum
import ipaddress
from functools import wraps
from fastapi import HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from database.user import User
from database.rbac import Role, Permission
from services.cache_service import CacheService


class PermissionType(str, Enum):
    """Permission types"""

    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    APPROVE = "approve"
    ADMIN = "admin"


class ResourceType(str, Enum):
    """Resource types"""

    USER = "user"
    ASSESSMENT = "assessment"
    POLICY = "policy"
    EVIDENCE = "evidence"
    REPORT = "report"
    SETTINGS = "settings"
    AUDIT = "audit"
    SECRET = "secret"


class AuthorizationService:
    """Fine-grained authorization with RBAC and resource permissions"""

    # Role hierarchy (higher roles inherit lower role permissions)
    ROLE_HIERARCHY = {
        "super_admin": ["admin", "manager", "user", "viewer"],
        "admin": ["manager", "user", "viewer"],
        "manager": ["user", "viewer"],
        "user": ["viewer"],
        "viewer": [],
    }

    # Default role permissions
    DEFAULT_PERMISSIONS = {
        "super_admin": ["*:*"],  # All permissions
        "admin": [
            "user:*",
            "assessment:*",
            "policy:*",
            "evidence:*",
            "report:*",
            "settings:*",
            "audit:read",
        ],
        "manager": [
            "user:read",
            "assessment:*",
            "policy:*",
            "evidence:*",
            "report:*",
            "settings:read",
        ],
        "user": [
            "user:read:own",
            "assessment:*:own",
            "policy:read",
            "evidence:*:own",
            "report:read:own",
        ],
        "viewer": ["assessment:read", "policy:read", "report:read"],
    }

    def __init__(self, cache_service: Optional[CacheService] = None):
        """Initialize authorization service"""
        self.cache = cache_service or CacheService()
        self._permission_cache = {}

    async def check_permission(
        self,
        user: User,
        resource_type: str,
        permission_type: str,
        resource_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Check if user has permission for resource

        Args:
            user: User object
            resource_type: Type of resource
            permission_type: Type of permission
            resource_id: Optional specific resource ID
            context: Optional context for dynamic evaluation

        Returns:
            True if permission granted
        """
        # Super admin bypass
        if self._is_super_admin(user):
            return True

        # Check cached permissions
        cache_key = f"perm:{user.id}:{resource_type}:{permission_type}:{resource_id}"
        cached = await self.cache.get(cache_key)
        if cached is not None:
            return cached

        # Evaluate permission
        has_permission = await self._evaluate_permission(
            user, resource_type, permission_type, resource_id, context
        )

        # Cache result
        await self.cache.set(cache_key, has_permission, expire_seconds=300)

        return has_permission

    async def _evaluate_permission(
        self,
        user: User,
        resource_type: str,
        permission_type: str,
        resource_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Evaluate permission with all checks"""

        # 1. Check role-based permissions
        if await self._check_role_permission(user, resource_type, permission_type):
            # Check resource ownership if needed
            if resource_id and ":own" in self._get_user_permissions(user):
                return await self._check_ownership(user, resource_type, resource_id)
            return True

        # 2. Check resource-specific permissions
        if resource_id:
            if await self._check_resource_permission(
                user, resource_type, permission_type, resource_id
            ):
                return True

        # 3. Check delegated permissions
        if await self._check_delegated_permission(
            user, resource_type, permission_type, resource_id
        ):
            return True

        # 4. Check dynamic/contextual permissions
        if context:
            if await self._check_dynamic_permission(
                user, resource_type, permission_type, context
            ):
                return True

        return False

    def _is_super_admin(self, user: User) -> bool:
        """Check if user is super admin"""
        return any(role.name == "super_admin" for role in user.roles)

    def _get_user_permissions(self, user: User) -> Set[str]:
        """Get all permissions for user including inherited"""
        permissions = set()

        for role in user.roles:
            # Add direct role permissions
            role_perms = self.DEFAULT_PERMISSIONS.get(role.name, [])
            permissions.update(role_perms)

            # Add inherited permissions
            inherited_roles = self.ROLE_HIERARCHY.get(role.name, [])
            for inherited in inherited_roles:
                inherited_perms = self.DEFAULT_PERMISSIONS.get(inherited, [])
                permissions.update(inherited_perms)

        return permissions

    async def _check_role_permission(
        self, user: User, resource_type: str, permission_type: str
    ) -> bool:
        """Check role-based permission"""
        user_permissions = self._get_user_permissions(user)

        # Check for exact match or wildcard
        permission_patterns = [
            f"{resource_type}:{permission_type}",
            f"{resource_type}:*",
            f"*:{permission_type}",
            "*:*",
        ]

        for pattern in permission_patterns:
            if pattern in user_permissions:
                return True
            # Check ownership variants
            if f"{pattern}:own" in user_permissions:
                return True  # Will check ownership later

        return False

    async def _check_ownership(
        self, user: User, resource_type: str, resource_id: str
    ) -> bool:
        """Check if user owns the resource"""
        # Implementation depends on resource type
        # This is a simplified version
        ownership_key = f"owner:{resource_type}:{resource_id}"
        owner_id = await self.cache.get(ownership_key)

        if owner_id:
            return str(user.id) == str(owner_id)

        # Fallback to database check
        # Would need to query specific resource table
        return False

    async def _check_resource_permission(
        self, user: User, resource_type: str, permission_type: str, resource_id: str
    ) -> bool:
        """Check resource-specific permission"""
        # Check if user has specific permission for this resource
        perm_key = f"resource_perm:{user.id}:{resource_type}:{resource_id}"
        resource_perms = await self.cache.get(perm_key) or []

        return permission_type in resource_perms

    async def _check_delegated_permission(
        self,
        user: User,
        resource_type: str,
        permission_type: str,
        resource_id: Optional[str] = None,
    ) -> bool:
        """Check if permission was delegated to user"""
        delegation_key = f"delegation:{user.id}:{resource_type}"
        if resource_id:
            delegation_key += f":{resource_id}"

        delegations = await self.cache.get(delegation_key) or []
        return permission_type in delegations

    async def _check_dynamic_permission(
        self,
        user: User,
        resource_type: str,
        permission_type: str,
        context: Dict[str, Any],
    ) -> bool:
        """Check dynamic/contextual permissions"""

        # Time-based permissions
        if "time_restriction" in context:
            if not self._check_time_restriction(context["time_restriction"]):
                return False

        # Location-based permissions
        if "ip_restriction" in context:
            if not self._check_ip_restriction(
                context.get("client_ip"), context["ip_restriction"]
            ):
                return False

        # Conditional permissions
        if "conditions" in context:
            if not self._evaluate_conditions(user, context["conditions"]):
                return False

        return True

    def _check_time_restriction(self, restriction: Dict[str, Any]) -> bool:
        """Check time-based access restriction"""
        now = datetime.now()

        # Check day of week
        if "days" in restriction:
            if now.strftime("%A").lower() not in restriction["days"]:
                return False

        # Check time range
        if "start_time" in restriction and "end_time" in restriction:
            current_time = now.time()
            start = time.fromisoformat(restriction["start_time"])
            end = time.fromisoformat(restriction["end_time"])

            if not (start <= current_time <= end):
                return False

        return True

    def _check_ip_restriction(
        self, client_ip: Optional[str], allowed_ips: List[str]
    ) -> bool:
        """Check IP-based access restriction"""
        if not client_ip:
            return False

        try:
            client_addr = ipaddress.ip_address(client_ip)

            for allowed in allowed_ips:
                # Check if it's a network or single IP
                if "/" in allowed:
                    network = ipaddress.ip_network(allowed)
                    if client_addr in network:
                        return True
                else:
                    if client_addr == ipaddress.ip_address(allowed):
                        return True

            return False
        except ValueError:
            return False

    def _evaluate_conditions(self, user: User, conditions: Dict[str, Any]) -> bool:
        """Evaluate conditional permission rules"""
        for condition, value in conditions.items():
            if condition == "department" and getattr(user, "department", None) != value:
                return False
            elif condition == "email_verified" and not getattr(
                user, "email_verified", True
            ):
                return False
            elif condition == "mfa_enabled" and not getattr(user, "mfa_enabled", False):
                return False
            elif condition == "is_active" and not user.is_active:
                return False
            # Add more conditions as needed

        return True

    async def grant_permission(
        self,
        user_id: str,
        resource_type: str,
        permission_type: str,
        resource_id: Optional[str] = None,
        expires_in: Optional[int] = None,
    ) -> None:
        """Grant permission to user"""
        if resource_id:
            # Resource-specific permission
            perm_key = f"resource_perm:{user_id}:{resource_type}:{resource_id}"
            current_perms = await self.cache.get(perm_key) or []
            if permission_type not in current_perms:
                current_perms.append(permission_type)
                await self.cache.set(perm_key, current_perms, expire_seconds=expires_in)
        else:
            # General permission
            perm_key = f"general_perm:{user_id}:{resource_type}"
            current_perms = await self.cache.get(perm_key) or []
            if permission_type not in current_perms:
                current_perms.append(permission_type)
                await self.cache.set(perm_key, current_perms, expire_seconds=expires_in)

    async def revoke_permission(
        self,
        user_id: str,
        resource_type: str,
        permission_type: str,
        resource_id: Optional[str] = None,
    ) -> None:
        """Revoke permission from user"""
        if resource_id:
            perm_key = f"resource_perm:{user_id}:{resource_type}:{resource_id}"
        else:
            perm_key = f"general_perm:{user_id}:{resource_type}"

        current_perms = await self.cache.get(perm_key) or []
        if permission_type in current_perms:
            current_perms.remove(permission_type)
            if current_perms:
                await self.cache.set(perm_key, current_perms)
            else:
                await self.cache.delete(perm_key)

    async def delegate_permission(
        self,
        from_user_id: str,
        to_user_id: str,
        resource_type: str,
        permission_type: str,
        resource_id: Optional[str] = None,
        expires_in: Optional[int] = None,
    ) -> None:
        """Delegate permission from one user to another"""
        delegation_key = f"delegation:{to_user_id}:{resource_type}"
        if resource_id:
            delegation_key += f":{resource_id}"

        delegations = await self.cache.get(delegation_key) or []
        if permission_type not in delegations:
            delegations.append(permission_type)
            await self.cache.set(delegation_key, delegations, expire_seconds=expires_in)

        # Track delegation source
        source_key = f"delegation_source:{delegation_key}"
        await self.cache.set(source_key, from_user_id, expire_seconds=expires_in)

    def check_endpoint_permission(
        self, required_permission: str, resource_type: Optional[str] = None
    ):
        """Decorator for endpoint permission checking"""

        def decorator(func):
            @wraps(func)
            async def wrapper(request: Request, *args, **kwargs):
                # Get user from request
                user = getattr(request.state, "user", None)
                if not user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required",
                    )

                # Check permission
                resource_id = kwargs.get("resource_id")
                context = {
                    "client_ip": request.client.host,
                    "method": request.method,
                    "path": request.url.path,
                }

                has_permission = await self.check_permission(
                    user,
                    resource_type or "general",
                    required_permission,
                    resource_id,
                    context,
                )

                if not has_permission:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Insufficient permissions",
                    )

                return await func(request, *args, **kwargs)

            return wrapper

        return decorator

    async def check_cross_tenant_access(
        self, user: User, tenant_id: str, requested_tenant_id: str
    ) -> bool:
        """Check cross-tenant access prevention"""
        # Users can only access their own tenant data
        if tenant_id != requested_tenant_id:
            # Check if user has cross-tenant permission
            cross_tenant_perm = f"cross_tenant:{requested_tenant_id}"
            user_perms = self._get_user_permissions(user)

            return cross_tenant_perm in user_perms or "*:*" in user_perms

        return True

    async def filter_by_tenant(self, user: User, query, model):
        """Filter query results by tenant"""
        # Add tenant filter to query
        if hasattr(model, "tenant_id"):
            if not self._is_super_admin(user):
                query = query.filter(
                    model.tenant_id == getattr(user, "tenant_id", None)
                )

        return query


# Singleton instance
_authz_service: Optional[AuthorizationService] = None


def get_authz_service() -> AuthorizationService:
    """Get authorization service instance"""
    global _authz_service
    if _authz_service is None:
        _authz_service = AuthorizationService()
    return _authz_service
