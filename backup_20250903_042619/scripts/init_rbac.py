"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Initialize RBAC System

Sets up default roles, permissions, and role-permission assignments
for the ruleIQ compliance platform.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from database.db_setup import get_db
from services.rbac_service import RBACService, initialize_rbac_system
from database.rbac import Role, Permission


def assign_permissions_to_roles(db_session) ->None:
    """Assign permissions to default roles based on role responsibilities."""
    rbac = RBACService(db_session)
    roles = {role.name: role for role in db_session.query(Role).all()}
    permissions = {perm.name: perm for perm in db_session.query(Permission)
        .all()}
    role_permissions = {'admin': ['user_create', 'user_update',
        'user_delete', 'user_list', 'framework_create', 'framework_update',
        'framework_delete', 'framework_list', 'assessment_create',
        'assessment_update', 'assessment_delete', 'assessment_list',
        'policy_generate', 'policy_refine', 'policy_validate',
        'report_view', 'report_export', 'report_schedule', 'admin_roles',
        'admin_permissions', 'admin_audit'], 'framework_manager': [
        'framework_create', 'framework_update', 'framework_list',
        'policy_generate', 'policy_refine', 'policy_validate',
        'report_view', 'report_export', 'user_list'], 'assessor': [
        'framework_list', 'assessment_create', 'assessment_update',
        'assessment_delete', 'assessment_list', 'policy_generate',
        'policy_refine', 'report_view', 'report_export'], 'viewer': [
        'framework_list', 'assessment_list', 'report_view'],
        'business_user': ['framework_list', 'assessment_create',
        'assessment_update', 'assessment_list', 'policy_generate',
        'policy_refine', 'policy_validate', 'report_view', 'report_export',
        'user_create', 'user_list', 'user_update']}
    for role_name, permission_names in role_permissions.items():
        if role_name not in roles:
            logger.info("Warning: Role '%s' not found" % role_name)
            continue
        role = roles[role_name]
        for permission_name in permission_names:
            if permission_name not in permissions:
                logger.info("Warning: Permission '%s' not found" %
                    permission_name)
                continue
            permission = permissions[permission_name]
            try:
                rbac.assign_permission_to_role(role.id, permission.id)
                logger.info("✓ Assigned '%s' to '%s'" % (permission_name,
                    role_name))
            except ValueError as e:
                if 'already assigned' in str(e):
                    print(
                        f"- Permission '{permission_name}' already assigned to '{role_name}'",
                        )
                else:
                    print(
                        f"✗ Error assigning '{permission_name}' to '{role_name}': {e}",
                        )


def main() ->bool:
    """Initialize the RBAC system."""
    logger.info('=== Initializing RBAC System ===')
    try:
        db_session = next(get_db())
        logger.info('\n1. Creating default permissions and roles...')
        initialize_rbac_system(db_session)
        logger.info('\n2. Assigning permissions to roles...')
        assign_permissions_to_roles(db_session)
        logger.info('\n3. Verifying setup...')
        role_count = db_session.query(Role).count()
        permission_count = db_session.query(Permission).count()
        logger.info('✓ Created %s roles' % role_count)
        logger.info('✓ Created %s permissions' % permission_count)
        logger.info('\nRole Summary:')
        roles = db_session.query(Role).all()
        for role in roles:
            permission_count = len(role.role_permissions)
            print(
                f'  - {role.display_name} ({role.name}): {permission_count} permissions',
                )
        logger.info('\n✅ RBAC system initialized successfully!')
        logger.info('\nNext steps:')
        logger.info('1. Create user accounts')
        logger.info('2. Assign roles to users')
        logger.info('3. Configure framework access levels')
    except Exception as e:
        logger.info('\n❌ Error initializing RBAC system: %s' % e)
        import traceback
        traceback.print_exc()
        return False
    finally:
        session.close()
        db_session.close()
    return True


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
