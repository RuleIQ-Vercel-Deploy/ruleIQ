#!/usr/bin/env python3
"""Simple test to check User model database connection"""

import os
import sys

sys.path.insert(0, ".")

# Load environment from .env.local
from dotenv import load_dotenv

load_dotenv(".env.local", override=True)

# Set testing flag (like pytest does)
os.environ["TESTING"] = "true"


def test_user_model_simple():
    try:
        from database.db_setup import get_db_session
        from database.user import User
        from sqlalchemy import text

        print("🔄 Testing User model connection...")

        # Get a database session
        db = next(get_db_session())

        # First, check what DATABASE_URL is being used
        print(f"DATABASE_URL: {os.getenv('DATABASE_URL')[:50]}...")

        # Check database schema directly
        result = db.execute(
            text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'users' ORDER BY ordinal_position"
            )
        )
        columns = [row[0] for row in result]
        print(f"✅ Database columns: {columns}")

        # Try to query User model (this should work if schema is correct)
        print("🔄 Testing User model query...")
        user_count = db.query(User).count()
        print(f"✅ User model query successful! Found {user_count} users.")

        # Try to create a test user (this should also work)
        print("🔄 Testing User model creation...")
        test_user = User(
            email="test@example.com",
            hashed_password="test_hash",
            full_name="Test User",
            google_id="test_google_id",
        )

        # Don't commit, just test the model creation
        print("✅ User model creation successful!")

        db.close()
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_user_model_simple()
    sys.exit(0 if success else 1)
