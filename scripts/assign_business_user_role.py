"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Assign business_user role to all existing users

This script assigns the business_user role to all active users in the system.
This is particularly useful for testing scenarios where new users need
to have assessment permissions.
"""

from typing import Any
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))
from database.db_setup import get_db
from database.user import User
from database.rbac import Role
from services.rbac_service import RBACService


def assign_business_user_roles() ->Any:
    """Assign business_user role to all active users"""
    logger.info('=== Assigning business_user Role to All Users ===\n')
    db = next(get_db())
    rbac = RBACService(db)
    try:
        business_user_role = db.query(Role).filter(Role.name == 'business_user'
            ).first()
        if not business_user_role:
            logger.info(
                '❌ Error: business_user role not found. Run init_rbac.py first.',
                )
            return False
        logger.info('✓ Found business_user role: %s' % business_user_role.id)
        users = db.query(User).filter(User.is_active == True).all()
        logger.info('✓ Found %s active users' % len(users))
        if not users:
            logger.info('⚠️  No active users found.')
            return True
        successful_assignments = 0
        already_assigned = 0
        failed_assignments = 0
        for user in users:
            try:
                existing_roles = rbac.get_user_roles(user.id)
                if any(role['name'] == 'business_user' for role in
                    existing_roles):
                    logger.info(
                        '  ⭕ User %s already has business_user role' % user
                        .email)
                    already_assigned += 1
                    continue
                rbac.assign_role_to_user(user_id=user.id, role_id=
                    business_user_role.id, granted_by=user.id)
                logger.info('  ✅ Assigned business_user role to %s' % user.
                    email)
                successful_assignments += 1
            except Exception as e:
                logger.info('  ❌ Failed to assign role to %s: %s' % (user.
                    email, e))
                failed_assignments += 1
        db.commit()
        logger.info('\n=== Assignment Summary ===')
        logger.info('✅ Successful assignments: %s' % successful_assignments)
        logger.info('⭕ Already assigned: %s' % already_assigned)
        logger.info('❌ Failed assignments: %s' % failed_assignments)
        logger.info('📊 Total users processed: %s' % len(users))
        if failed_assignments == 0:
            logger.info('\n🎉 All users now have the business_user role!')
            return True
        else:
            logger.info(
                '\n⚠️  Some assignments failed. Check the errors above.')
            return False
    except Exception as e:
        logger.info('❌ Error during role assignment: %s' % e)
        db.rollback()
        return False
    finally:
        db.close()


def main() ->Any:
    """Main execution"""
    success = assign_business_user_roles()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
