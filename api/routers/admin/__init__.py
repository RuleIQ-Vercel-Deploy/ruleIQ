"""
Admin routers package for administrative functionality.

Provides administrative interfaces for:
- User management (CRUD, roles, permissions)
- Token blacklist management
- Data access control and visibility management
- System monitoring and audit logging
"""

from fastapi import APIRouter

from .user_management import router as user_management_router
from .token_management import router as token_management_router
from .data_access import router as data_access_router

# Create a main admin router that includes all admin sub-routers
admin_router = APIRouter(prefix="/api/admin", tags=["admin"])

# Include all admin sub-routers
admin_router.include_router(user_management_router)
admin_router.include_router(token_management_router)
admin_router.include_router(data_access_router)

__all__ = ["admin_router", "user_management_router", "token_management_router", "data_access_router"]