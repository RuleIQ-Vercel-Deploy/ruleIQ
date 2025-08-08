"""
Role-Based Access Control (RBAC) Service

Provides high-level operations for managing roles, permissions, and access control.
Implements security patterns for UK compliance requirements.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from database.rbac import (
    Role, Permission, UserRole, RolePermission, FrameworkAccess,
    AuditLog
)
from database.user import User
from database.compliance_framework import ComplianceFramework


logger = logging.getLogger(__name__)


class RBACService:
    """
    Service for Role-Based Access Control operations.

    Provides centralized management of roles, permissions, and access control
    with comprehensive audit logging for UK compliance requirements.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # Role Management

    def create_role(
        self,
        name: str,
        display_name: str,
        description: str = None,
        is_system_role: bool = False,
        created_by: UUID = None
    ) -> Role:
        """
        Create a new role.

        Args:
            name: Unique role name (slug format)
            display_name: Human-readable role name
            description: Optional role description
            is_system_role: Whether this is a built-in system role
            created_by: User ID who created the role

        Returns:
            Created Role instance

        Raises:
            ValueError: If role name already exists
        """
        # Check if role already exists
        existing = self.db.query(Role).filter(Role.name == name).first()
        if existing:
            raise ValueError(f"Role '{name}' already exists")

        role = Role(
            name=name,
            display_name=display_name,
            description=description,
            is_system_role=is_system_role
        )

        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)

        # Audit log
        self._log_audit(
            user_id=created_by,
            action="role_created",
            resource_type="role",
            resource_id=str(role.id),
            details={"role_name": name, "display_name": display_name}
        )

        logger.info(f"Role created: {name} (ID: {role.id})")
        return role

    def assign_role_to_user(
        self,
        user_id: UUID,
        role_id: UUID,
        granted_by: UUID = None,
        expires_at: datetime = None
    ) -> UserRole:
        """
        Assign a role to a user.

        Args:
            user_id: User to assign role to
            role_id: Role to assign
            granted_by: User who granted the role
            expires_at: Optional expiration date

        Returns:
            UserRole assignment

        Raises:
            ValueError: If user or role doesn't exist, or assignment already exists
        """
        # Validate user exists
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User not found: {user_id}")

        # Validate role exists
        role = self.db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise ValueError(f"Role not found: {role_id}")

        # Check if assignment already exists
        existing = self.db.query(UserRole).filter(
            and_(UserRole.user_id == user_id, UserRole.role_id == role_id)
        ).first()

        if existing:
            if existing.is_active:
                raise ValueError(f"User already has role '{role.name}'")
            else:
                # Reactivate existing assignment
                existing.is_active = True
                existing.granted_by = granted_by
                existing.granted_at = datetime.utcnow()
                existing.expires_at = expires_at
                self.db.commit()
                user_role = existing
        else:
            # Create new assignment
            user_role = UserRole(
                user_id=user_id,
                role_id=role_id,
                granted_by=granted_by,
                expires_at=expires_at
            )
            self.db.add(user_role)
            self.db.commit()
            self.db.refresh(user_role)

        # Audit log
        self._log_audit(
            user_id=granted_by,
            action="role_assigned",
            resource_type="user_role",
            resource_id=str(user_role.id),
            details={
                "user_id": str(user_id),
                "role_name": role.name,
                "expires_at": expires_at.isoformat() if expires_at else None
            }
        )

        logger.info(f"Role '{role.name}' assigned to user {user_id}")
        return user_role

    def revoke_role_from_user(
        self,
        user_id: UUID,
        role_id: UUID,
        revoked_by: UUID = None
    ) -> bool:
        """
        Revoke a role from a user.

        Args:
            user_id: User to revoke role from
            role_id: Role to revoke
            revoked_by: User who revoked the role

        Returns:
            True if role was revoked, False if assignment didn't exist
        """
        user_role = self.db.query(UserRole).filter(
            and_(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
                UserRole.is_active
            )
        ).first()

        if not user_role:
            return False

        user_role.is_active = False
        self.db.commit()

        # Get role name for logging
        role = self.db.query(Role).filter(Role.id == role_id).first()
        role_name = role.name if role else "unknown"

        # Audit log
        self._log_audit(
            user_id=revoked_by,
            action="role_revoked",
            resource_type="user_role",
            resource_id=str(user_role.id),
            details={
                "user_id": str(user_id),
                "role_name": role_name
            }
        )

        logger.info(f"Role '{role_name}' revoked from user {user_id}")
        return True

    # Permission Management

    def create_permission(
        self,
        name: str,
        display_name: str,
        category: str,
        description: str = None,
        resource_type: str = None
    ) -> Permission:
        """
        Create a new permission.

        Args:
            name: Unique permission name
            display_name: Human-readable permission name
            category: Permission category for grouping
            description: Optional description
            resource_type: Type of resource this permission applies to

        Returns:
            Created Permission instance
        """
        # Check if permission already exists
        existing = self.db.query(Permission).filter(Permission.name == name).first()
        if existing:
            raise ValueError(f"Permission '{name}' already exists")

        permission = Permission(
            name=name,
            display_name=display_name,
            category=category,
            description=description,
            resource_type=resource_type
        )

        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)

        logger.info(f"Permission created: {name} (ID: {permission.id})")
        return permission

    def assign_permission_to_role(
        self,
        role_id: UUID,
        permission_id: UUID,
        granted_by: UUID = None
    ) -> RolePermission:
        """
        Assign a permission to a role.

        Args:
            role_id: Role to assign permission to
            permission_id: Permission to assign
            granted_by: User who granted the permission

        Returns:
            RolePermission assignment
        """
        # Check if assignment already exists
        existing = self.db.query(RolePermission).filter(
            and_(
                RolePermission.role_id == role_id,
                RolePermission.permission_id == permission_id
            )
        ).first()

        if existing:
            raise ValueError("Permission already assigned to role")

        role_permission = RolePermission(
            role_id=role_id,
            permission_id=permission_id,
            granted_by=granted_by
        )

        self.db.add(role_permission)
        self.db.commit()
        self.db.refresh(role_permission)

        logger.info(f"Permission {permission_id} assigned to role {role_id}")
        return role_permission

    # Framework Access Control

    def grant_framework_access(
        self,
        role_id: UUID,
        framework_id: UUID,
        access_level: str = "read",
        granted_by: UUID = None
    ) -> FrameworkAccess:
        """
        Grant framework access to a role.

        Args:
            role_id: Role to grant access to
            framework_id: Framework to grant access to
            access_level: Access level (read, write, admin)
            granted_by: User who granted the access

        Returns:
            FrameworkAccess instance
        """
        if access_level not in ["read", "write", "admin"]:
            raise ValueError("Access level must be 'read', 'write', or 'admin'")

        # Check if access already exists
        existing = self.db.query(FrameworkAccess).filter(
            and_(
                FrameworkAccess.role_id == role_id,
                FrameworkAccess.framework_id == framework_id,
                FrameworkAccess.is_active
            )
        ).first()

        if existing:
            # Update existing access level
            existing.access_level = access_level
            existing.granted_by = granted_by
            existing.granted_at = datetime.utcnow()
            self.db.commit()
            framework_access = existing
        else:
            # Create new access
            framework_access = FrameworkAccess(
                role_id=role_id,
                framework_id=framework_id,
                access_level=access_level,
                granted_by=granted_by
            )
            self.db.add(framework_access)
            self.db.commit()
            self.db.refresh(framework_access)

        logger.info(f"Framework access granted: role {role_id}, framework {framework_id}, level {access_level}")
        return framework_access

    # User Access Checks

    def user_has_permission(
        self,
        user_id: UUID,
        permission_name: str
    ) -> bool:
        """
        Check if a user has a specific permission.

        Args:
            user_id: User to check
            permission_name: Permission name to check

        Returns:
            True if user has the permission
        """
        # Get user's active roles
        user_roles = self.db.query(UserRole).filter(
            and_(
                UserRole.user_id == user_id,
                UserRole.is_active,
                or_(
                    UserRole.expires_at.is_(None),
                    UserRole.expires_at > datetime.utcnow()
                )
            )
        ).all()

        if not user_roles:
            return False

        role_ids = [ur.role_id for ur in user_roles]

        # Check if any role has the permission
        permission_count = self.db.query(RolePermission).join(Permission).filter(
            and_(
                RolePermission.role_id.in_(role_ids),
                Permission.name == permission_name,
                Permission.is_active
            )
        ).count()

        return permission_count > 0

    def user_has_framework_access(
        self,
        user_id: UUID,
        framework_id: UUID,
        required_level: str = "read"
    ) -> bool:
        """
        Check if a user has access to a specific framework.

        Args:
            user_id: User to check
            framework_id: Framework to check access for
            required_level: Required access level (read, write, admin)

        Returns:
            True if user has the required access level
        """
        level_hierarchy = {"read": 1, "write": 2, "admin": 3}
        required_level_value = level_hierarchy.get(required_level, 1)

        # Get user's active roles
        user_roles = self.db.query(UserRole).filter(
            and_(
                UserRole.user_id == user_id,
                UserRole.is_active,
                or_(
                    UserRole.expires_at.is_(None),
                    UserRole.expires_at > datetime.utcnow()
                )
            )
        ).all()

        if not user_roles:
            return False

        role_ids = [ur.role_id for ur in user_roles]

        # Check framework access for user's roles
        framework_access = self.db.query(FrameworkAccess).filter(
            and_(
                FrameworkAccess.role_id.in_(role_ids),
                FrameworkAccess.framework_id == framework_id,
                FrameworkAccess.is_active
            )
        ).all()

        # Check if any access level meets the requirement
        for access in framework_access:
            access_level_value = level_hierarchy.get(access.access_level, 1)
            if access_level_value >= required_level_value:
                return True

        return False

    def get_user_roles(self, user_id: UUID) -> List[Dict]:
        """
        Get all active roles for a user.

        Args:
            user_id: User ID to get roles for

        Returns:
            List of role information dictionaries
        """
        user_roles = self.db.query(UserRole).join(Role).filter(
            and_(
                UserRole.user_id == user_id,
                UserRole.is_active,
                Role.is_active,
                or_(
                    UserRole.expires_at.is_(None),
                    UserRole.expires_at > datetime.utcnow()
                )
            )
        ).all()

        return [
            {
                "id": str(ur.role.id),
                "name": ur.role.name,
                "display_name": ur.role.display_name,
                "description": ur.role.description,
                "granted_at": ur.granted_at.isoformat(),
                "expires_at": ur.expires_at.isoformat() if ur.expires_at else None
            }
            for ur in user_roles
        ]

    def get_user_permissions(self, user_id: UUID) -> List[str]:
        """
        Get all permissions for a user through their roles.

        Args:
            user_id: User ID to get permissions for

        Returns:
            List of permission names
        """
        # Get user's active roles
        user_roles = self.db.query(UserRole).filter(
            and_(
                UserRole.user_id == user_id,
                UserRole.is_active,
                or_(
                    UserRole.expires_at.is_(None),
                    UserRole.expires_at > datetime.utcnow()
                )
            )
        ).all()

        if not user_roles:
            return []

        role_ids = [ur.role_id for ur in user_roles]

        # Get permissions for these roles
        permissions = self.db.query(Permission).join(RolePermission).filter(
            and_(
                RolePermission.role_id.in_(role_ids),
                Permission.is_active
            )
        ).all()

        return list(set(p.name for p in permissions))

    def get_accessible_frameworks(self, user_id: UUID) -> List[Dict]:
        """
        Get all frameworks accessible to a user.

        Args:
            user_id: User ID to get frameworks for

        Returns:
            List of framework information with access levels
        """
        # Get user's active roles
        user_roles = self.db.query(UserRole).filter(
            and_(
                UserRole.user_id == user_id,
                UserRole.is_active,
                or_(
                    UserRole.expires_at.is_(None),
                    UserRole.expires_at > datetime.utcnow()
                )
            )
        ).all()

        if not user_roles:
            return []

        role_ids = [ur.role_id for ur in user_roles]

        # Get framework access for these roles
        framework_access = self.db.query(FrameworkAccess).join(ComplianceFramework).filter(
            and_(
                FrameworkAccess.role_id.in_(role_ids),
                FrameworkAccess.is_active,
                ComplianceFramework.is_active
            )
        ).all()

        # Group by framework and get highest access level
        frameworks = {}
        level_hierarchy = {"read": 1, "write": 2, "admin": 3}

        for access in framework_access:
            framework_id = str(access.framework_id)
            current_level = level_hierarchy.get(access.access_level, 1)

            if framework_id not in frameworks or current_level > frameworks[framework_id]["access_level_value"]:
                frameworks[framework_id] = {
                    "id": framework_id,
                    "name": access.framework.name,
                    "display_name": access.framework.display_name,
                    "access_level": access.access_level,
                    "access_level_value": current_level
                }

        return [
            {k: v for k, v in framework.items() if k != "access_level_value"}
            for framework in frameworks.values()
        ]

    # Audit and Security

    def _log_audit(
        self,
        action: str,
        user_id: UUID = None,
        resource_type: str = None,
        resource_id: str = None,
        details: Dict = None,
        severity: str = "info"
    ) -> None:
        """
        Log an audit event.

        Args:
            action: Action performed
            user_id: User who performed the action
            resource_type: Type of resource affected
            resource_id: ID of resource affected
            details: Additional details as dictionary
            severity: Event severity (info, warning, error, critical)
        """
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=json.dumps(details) if details else None,
            severity=severity
        )

        self.db.add(audit_log)
        self.db.commit()

    def cleanup_expired_roles(self) -> int:
        """
        Clean up expired role assignments.

        Returns:
            Number of expired roles cleaned up
        """
        current_time = datetime.utcnow()

        expired_roles = self.db.query(UserRole).filter(
            and_(
                UserRole.expires_at <= current_time,
                UserRole.is_active
            )
        ).all()

        count = len(expired_roles)

        for user_role in expired_roles:
            user_role.is_active = False

            # Audit log
            self._log_audit(
                action="role_expired",
                resource_type="user_role",
                resource_id=str(user_role.id),
                details={
                    "user_id": str(user_role.user_id),
                    "role_id": str(user_role.role_id),
                    "expired_at": current_time.isoformat()
                }
            )

        if count > 0:
            self.db.commit()
            logger.info(f"Cleaned up {count} expired role assignments")

        return count


# Initialize default roles and permissions
def initialize_rbac_system(db: Session) -> None:
    """
    Initialize the RBAC system with default roles and permissions.
    Should be called during application startup or migration.
    """
    rbac = RBACService(db)

    # Create default permissions
    default_permissions = [
        # User management
        ("user_create", "Create Users", "user_management", "Create new user accounts"),
        ("user_update", "Update Users", "user_management", "Update user information"),
        ("user_delete", "Delete Users", "user_management", "Delete user accounts"),
        ("user_list", "List Users", "user_management", "View user listings"),

        # Framework management
        ("framework_create", "Create Frameworks", "framework_management", "Create compliance frameworks"),
        ("framework_update", "Update Frameworks", "framework_management", "Update framework information"),
        ("framework_delete", "Delete Frameworks", "framework_management", "Delete frameworks"),
        ("framework_list", "List Frameworks", "framework_management", "View framework listings"),

        # Assessment management
        ("assessment_create", "Create Assessments", "assessment_management", "Create new assessments"),
        ("assessment_update", "Update Assessments", "assessment_management", "Update assessment information"),
        ("assessment_delete", "Delete Assessments", "assessment_management", "Delete assessments"),
        ("assessment_list", "List Assessments", "assessment_management", "View assessment listings"),

        # Policy generation
        ("policy_generate", "Generate Policies", "policy_generation", "Generate AI policies"),
        ("policy_refine", "Refine Policies", "policy_generation", "Refine existing policies"),
        ("policy_validate", "Validate Policies", "policy_generation", "Validate policy compliance"),

        # Report access
        ("report_view", "View Reports", "report_access", "View compliance reports"),
        ("report_export", "Export Reports", "report_access", "Export reports to files"),
        ("report_schedule", "Schedule Reports", "report_access", "Schedule automated reports"),

        # Admin functions
        ("admin_roles", "Manage Roles", "admin_functions", "Manage system roles"),
        ("admin_permissions", "Manage Permissions", "admin_functions", "Manage system permissions"),
        ("admin_audit", "View Audit Logs", "admin_functions", "Access audit logs"),
    ]

    for name, display_name, category, description in default_permissions:
        try:
            rbac.create_permission(name, display_name, category, description)
        except ValueError:
            # Permission already exists
            pass

    # Create default roles
    default_roles = [
        ("admin", "Administrator", "Full system access with all permissions", True),
        ("framework_manager", "Framework Manager", "Manage compliance frameworks and policies", True),
        ("assessor", "Assessor", "Create and manage compliance assessments", True),
        ("viewer", "Viewer", "Read-only access to compliance data", True),
        ("business_user", "Business User", "Standard business user access", True),
    ]

    for name, display_name, description, is_system in default_roles:
        try:
            rbac.create_role(name, display_name, description, is_system)
        except ValueError:
            # Role already exists
            pass

    logger.info("RBAC system initialized with default roles and permissions")
