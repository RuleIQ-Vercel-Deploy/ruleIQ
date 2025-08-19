#!/usr/bin/env python3
"""
Assign business_user role to all existing users

This script assigns the business_user role to all active users in the system.
This is particularly useful for testing scenarios where new users need
to have assessment permissions.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from database.db_setup import get_db
from database.user import User
from database.rbac import Role
from services.rbac_service import RBACService
from typing import Optional


def assign_business_user_roles() -> Optional[bool]:
    """Assign business_user role to all active users"""

    print("=== Assigning business_user Role to All Users ===\n")

    # Get database session
    db = next(get_db())
    rbac = RBACService(db)

    try:
        # Get business_user role
        business_user_role = db.query(Role).filter(Role.name == "business_user").first()
        if not business_user_role:
            print("❌ Error: business_user role not found. Run init_rbac.py first.")
            return False

        print(f"✓ Found business_user role: {business_user_role.id}")

        # Get all active users
        users = db.query(User).filter(User.is_active).all()
        print(f"✓ Found {len(users)} active users")

        if not users:
            print("⚠️  No active users found.")
            return True

        successful_assignments = 0
        already_assigned = 0
        failed_assignments = 0

        for user in users:
            try:
                # Check if user already has the role
                existing_roles = rbac.get_user_roles(user.id)
                if any(role["name"] == "business_user" for role in existing_roles):
                    print(f"  ⭕ User {user.email} already has business_user role")
                    already_assigned += 1
                    continue

                # Assign the role
                rbac.assign_role_to_user(
                    user_id=user.id,
                    role_id=business_user_role.id,
                    granted_by=user.id,  # Self-assignment for this script
                )

                print(f"  ✅ Assigned business_user role to {user.email}")
                successful_assignments += 1

            except Exception as e:
                print(f"  ❌ Failed to assign role to {user.email}: {e}")
                failed_assignments += 1

        db.commit()

        # Summary
        print("\n=== Assignment Summary ===")
        print(f"✅ Successful assignments: {successful_assignments}")
        print(f"⭕ Already assigned: {already_assigned}")
        print(f"❌ Failed assignments: {failed_assignments}")
        print(f"📊 Total users processed: {len(users)}")

        if failed_assignments == 0:
            print("\n🎉 All users now have the business_user role!")
            return True
        else:
            print("\n⚠️  Some assignments failed. Check the errors above.")
            return False

    except Exception as e:
        print(f"❌ Error during role assignment: {e}")
        db.rollback()
        return False

    finally:
        db.close()


def main() -> None:
    """Main execution"""
    success = assign_business_user_roles()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
