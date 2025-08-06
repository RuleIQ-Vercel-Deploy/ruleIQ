#!/usr/bin/env python3
"""
Initialize RBAC System

Sets up default roles, permissions, and role-permission assignments
for the ruleIQ compliance platform.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from database.db_setup import get_db
from services.rbac_service import RBACService, initialize_rbac_system
from database.rbac import Role, Permission


def assign_permissions_to_roles(db_session):
    """Assign permissions to default roles based on role responsibilities."""

    rbac = RBACService(db_session)

    # Get all roles and permissions
    roles = {role.name: role for role in db_session.query(Role).all()}
    permissions = {perm.name: perm for perm in db_session.query(Permission).all()}

    # Role-permission assignments
    role_permissions = {
        "admin": [
            # Admin has all permissions
            "user_create", "user_update", "user_delete", "user_list",
            "framework_create", "framework_update", "framework_delete", "framework_list",
            "assessment_create", "assessment_update", "assessment_delete", "assessment_list",
            "policy_generate", "policy_refine", "policy_validate",
            "report_view", "report_export", "report_schedule",
            "admin_roles", "admin_permissions", "admin_audit"
        ],
        "framework_manager": [
            # Framework managers can manage frameworks and policies
            "framework_create", "framework_update", "framework_list",
            "policy_generate", "policy_refine", "policy_validate",
            "report_view", "report_export",
            "user_list"  # Can view users but not manage them
        ],
        "assessor": [
            # Assessors can manage assessments and view frameworks
            "framework_list",
            "assessment_create", "assessment_update", "assessment_delete", "assessment_list",
            "policy_generate", "policy_refine",  # Can generate policies for assessments
            "report_view", "report_export"
        ],
        "viewer": [
            # Viewers have read-only access
            "framework_list",
            "assessment_list",
            "report_view"
        ],
        "business_user": [
            # Business users can create assessments and policies for their organization
            "framework_list",
            "assessment_create", "assessment_update", "assessment_list",
            "policy_generate", "policy_refine", "policy_validate",
            "report_view", "report_export"
        ]
    }

    # Assign permissions to roles
    for role_name, permission_names in role_permissions.items():
        if role_name not in roles:
            print(f"Warning: Role '{role_name}' not found")
            continue

        role = roles[role_name]

        for permission_name in permission_names:
            if permission_name not in permissions:
                print(f"Warning: Permission '{permission_name}' not found")
                continue

            permission = permissions[permission_name]

            try:
                rbac.assign_permission_to_role(role.id, permission.id)
                print(f"✓ Assigned '{permission_name}' to '{role_name}'")
            except ValueError as e:
                if "already assigned" in str(e):
                    print(f"- Permission '{permission_name}' already assigned to '{role_name}'")
                else:
                    print(f"✗ Error assigning '{permission_name}' to '{role_name}': {e}")


def main():
    """Initialize the RBAC system."""

    print("=== Initializing RBAC System ===")

    try:
        # Get database session
        db_session = next(get_db())

        print("\n1. Creating default permissions and roles...")
        initialize_rbac_system(db_session)

        print("\n2. Assigning permissions to roles...")
        assign_permissions_to_roles(db_session)

        print("\n3. Verifying setup...")

        # Count roles and permissions
        role_count = db_session.query(Role).count()
        permission_count = db_session.query(Permission).count()

        print(f"✓ Created {role_count} roles")
        print(f"✓ Created {permission_count} permissions")

        # Show role summary
        print("\nRole Summary:")
        roles = db_session.query(Role).all()
        for role in roles:
            permission_count = len(role.role_permissions)
            print(f"  - {role.display_name} ({role.name}): {permission_count} permissions")

        print("\n✅ RBAC system initialized successfully!")
        print("\nNext steps:")
        print("1. Create user accounts")
        print("2. Assign roles to users")
        print("3. Configure framework access levels")

    except Exception as e:
        print(f"\n❌ Error initializing RBAC system: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        db_session.close()

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
