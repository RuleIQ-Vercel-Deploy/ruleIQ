#!/usr/bin/env python3
"""
Quick script to generate a test JWT token and create a test user for API testing
"""

import sys
import uuid
from datetime import timedelta

# Add the project root to Python path
sys.path.insert(0, '/home/omar/Documents/ruleIQ')

from api.dependencies.auth import create_access_token

def generate_test_token_and_user():
    """Generate a test JWT token and create a test user"""
    try:
        from database.db_setup import get_db_session
        from database.user import User
        from api.auth.security import get_password_hash

        # Create user in database
        session = get_db_session()
        test_user_id = str(uuid.uuid4())

        # Check if user already exists
        existing_user = session.query(User).filter(User.email == "test@example.com").first()
        if existing_user:
            print(f"Using existing test user: {existing_user.id}")
            test_user_id = str(existing_user.id)
        else:
            # Create new user
            hashed_password = get_password_hash("TestPassword123!")
            db_user = User(
                id=test_user_id,
                email="test@example.com",
                hashed_password=hashed_password,
                is_active=True
            )
            session.add(db_user)
            session.commit()
            print(f"Created new test user: {test_user_id}")

        session.close()

    except Exception as e:
        print(f"Error creating user (using temporary ID): {e}")
        test_user_id = str(uuid.uuid4())

    # Create test user data
    token_data = {
        "sub": test_user_id,
        "email": "test@example.com",
        "is_active": True
    }

    # Create token with 1 hour expiry
    token = create_access_token(
        data=token_data,
        expires_delta=timedelta(hours=1)
    )

    print("\nTest JWT Token:")
    print(f"{token}")
    print(f"\nTest User ID: {test_user_id}")
    print("\nUse with:")
    print(f'curl -H "Authorization: Bearer {token}" http://localhost:8000/api/v1/...')

    return token

if __name__ == "__main__":
    generate_test_token_and_user()
