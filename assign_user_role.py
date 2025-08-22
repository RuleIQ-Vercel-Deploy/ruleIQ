#!/usr/bin/env python3
"""
Assign business_user role to a specific test user for API testing
"""

import asyncio
import asyncpg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def assign_user_role():
    """Assign business_user role to the test user"""

    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False

    try:
        # Connect to database
        conn = await asyncpg.connect(database_url)
        print("✅ Connected to database")

        # The specific test user that needs permissions
        user_email = "test-1754509023483@debugtest.com"

        # Get user ID
        user_result = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1",
            user_email
        )

        if not user_result:
            print(f"❌ User not found: {user_email}")
            await conn.close()
            return False

        user_id = user_result['id']
        print(f"✅ Found user: {user_email} (ID: {user_id})")

        # Get business_user role ID
        role_result = await conn.fetchrow(
            "SELECT id FROM rbac_roles WHERE name = 'business_user'"
        )

        if not role_result:
            print("❌ business_user role not found")
            await conn.close()
            return False

        role_id = role_result['id']
        print(f"✅ Found business_user role (ID: {role_id})")

        # Check if user already has this role
        existing_assignment = await conn.fetchrow(
            "SELECT id FROM rbac_user_roles WHERE user_id = $1 AND role_id = $2",
            user_id, role_id
        )

        if existing_assignment:
            print("ℹ️  User already has business_user role assigned")
        else:
            # Assign the role
            await conn.execute(
                "INSERT INTO rbac_user_roles (user_id, role_id) VALUES ($1, $2)",
                user_id, role_id
            )
            print("✅ Successfully assigned business_user role to user")

        # Verify the assignment by checking permissions
        permissions_query = """
        SELECT DISTINCT p.name
        FROM rbac_permissions p
        JOIN rbac_role_permissions rp ON p.id = rp.permission_id
        JOIN rbac_user_roles ur ON rp.role_id = ur.role_id
        WHERE ur.user_id = $1
        ORDER BY p.name
        """

        permissions = await conn.fetch(permissions_query, user_id)
        permission_names = [p['name'] for p in permissions]

        print(f"\n✅ User now has {len(permission_names)} permissions:")
        for perm in permission_names[:10]:  # Show first 10
            print(f"   - {perm}")
        if len(permission_names) > 10:
            print(f"   ... and {len(permission_names) - 10} more")

        # Check specifically for assessment permissions
        assessment_perms = [p for p in permission_names if 'assessment' in p]
        if assessment_perms:
            print("\n🎯 Assessment permissions found:")
            for perm in assessment_perms:
                print(f"   - {perm}")
        else:
            print("\n⚠️  No assessment permissions found")

        await conn.close()
        print("\n✅ Role assignment completed successfully")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(assign_user_role())
    exit(0 if success else 1)
