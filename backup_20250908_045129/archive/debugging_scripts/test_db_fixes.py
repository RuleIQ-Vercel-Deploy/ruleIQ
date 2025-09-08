#!/usr/bin/env python3
"""Test database connection fixes."""

from __future__ import annotations

import sys
import os
import asyncio
from typing import Optional

# Add project root to path
sys.path.insert(0, ".")

# Set test environment
os.environ["ENV"] = "testing"
os.environ["DATABASE_URL"] = (
    "postgresql://neondb_owner:npg_s0JhnfGNy3Ze@ep-wild-grass-a8o37wq8-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
)


async def test_database_connection() -> Optional[bool]:
    """Test database connection with our fixes."""
    try:
        print("1. Testing database connection...")

        # Import the database manager
        from tests.conftest import _db_manager

        # Test engine creation
        print("2. Testing engine creation...")
        sync_engine = _db_manager.get_sync_engine()
        async_engine = _db_manager.get_async_engine()
        print(f"✓ Sync engine created: {sync_engine}")
        print(f"✓ Async engine created: {async_engine}")

        # Test session makers
        print("3. Testing session makers...")
        sync_session_maker = _db_manager.get_sync_session_maker()
        async_session_maker = _db_manager.get_async_session_maker()
        print("✓ Session makers created")

        # Test actual database connection
        print("4. Testing actual database connection...")

        # Test sync connection
        from sqlalchemy import text

        with sync_session_maker() as session:
            result = session.execute(text("SELECT 1 as test"))
            value = result.scalar()
            print(f"✓ Sync connection test: {value}")

        # Test async connection
        async with async_session_maker() as session:
            result = await session.execute(text("SELECT 1 as test"))
            value = result.scalar()
            print(f"✓ Async connection test: {value}")

        # Test table creation
        print("5. Testing table creation...")
        await _db_manager.create_tables()
        print("✓ Tables created successfully")

        # Test table cleanup
        print("6. Testing table cleanup...")
        await _db_manager.drop_tables()
        print("✓ Tables cleaned up successfully")

        print("\n✅ All database connection tests passed!")
        return True

    except (Exception, ValueError) as e:
        print(f"\n❌ Database connection test failed: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        try:
            await _db_manager.dispose()
            print("✓ Database engines disposed")
        except (Exception, ValueError):
            pass


if __name__ == "__main__":
    success = asyncio.run(test_database_connection())
    sys.exit(0 if success else 1)
