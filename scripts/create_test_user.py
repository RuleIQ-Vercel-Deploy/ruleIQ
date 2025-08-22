#!/usr/bin/env python3
"""
Create a test user for API testing
"""
import asyncio
import sys
sys.path.append('/home/omar/Documents/ruleIQ')

from database.db_setup import get_async_db
from database.user import User
from api.dependencies.auth import get_password_hash
from sqlalchemy.future import select
import uuid

async def create_test_user():
    """Create a test user for API testing"""
    async for db in get_async_db():
        try:
            # Check if test user exists
            email = "test@ruleiq.dev"
            result = await db.execute(select(User).where(User.email == email))
            existing_user = result.scalars().first()

            if existing_user:
                print(f"✅ Test user already exists: {email}")
                print(f"   ID: {existing_user.id}")
                print(f"   Is Active: {existing_user.is_active}")

                # Update password to ensure we know it
                existing_user.hashed_password = get_password_hash("TestPassword123!")
                existing_user.is_active = True
                await db.commit()
                print("✅ Password updated to: TestPassword123!")

            else:
                # Create new test user
                new_user = User(
                    id=str(uuid.uuid4()),
                    email=email,
                    hashed_password=get_password_hash("TestPassword123!"),
                    is_active=True,
                    is_superuser=False
                )
                db.add(new_user)
                await db.commit()
                print(f"✅ Created new test user: {email}")
                print(f"   ID: {new_user.id}")
                print("   Password: TestPassword123!")

            print("\n📝 Use these credentials for testing:")
            print(f"   Email: {email}")
            print("   Password: TestPassword123!")

            break
        except Exception as e:
            print(f"❌ Error creating/updating user: {e}")
            await db.rollback()
            break

if __name__ == "__main__":
    asyncio.run(create_test_user())
