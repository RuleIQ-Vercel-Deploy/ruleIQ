#!/usr/bin/env python3
"""
Setup test database with all required tables.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set up environment
os.environ["ENV"] = "testing"
os.environ["DATABASE_URL"] = (
    "postgresql://neondb_owner:npg_s0JhnfGNy3Ze@ep-wild-grass-a8o37wq8-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
)
os.environ["SECRET_KEY"] = "test_secret_key"
os.environ["GOOGLE_API_KEY"] = "test_key"
os.environ["USE_MOCK_AI"] = "true"

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text

# Import all models to ensure they're registered
from database.db_setup import Base
from typing import Optional


async def create_tables() -> Optional[bool]:
    """Create all database tables."""
    db_url = os.environ["DATABASE_URL"]
    async_url = db_url.replace("postgresql://", "postgresql+asyncpg://")

    if "sslmode=require" in async_url:
        async_url = async_url.replace("?sslmode=require", "")
        ssl_config = {"ssl": "require"}
    else:
        ssl_config = {}

    engine = create_async_engine(async_url, poolclass=NullPool, echo=True, connect_args=ssl_config)

    try:
        # Drop all tables first (for clean slate)
        print("Dropping existing tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

        # Create all tables
        print("\nCreating tables...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # Verify tables were created
        async with engine.begin() as conn:
            result = await conn.execute(
                text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
            )
            tables = [row[0] for row in result]
            print(f"\nCreated {len(tables)} tables:")
            for table in tables:
                print(f"  - {table}")

        # Initialize default frameworks
        print("\nInitializing default frameworks...")
        from services.framework_service import initialize_default_frameworks

        AsyncSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

        async with AsyncSessionLocal() as session:
            await initialize_default_frameworks(session)
            print("Default frameworks initialized successfully")

        return True

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        await engine.dispose()


def main() -> int:
    """Run the setup."""
    print("Setting up test database")
    print("=" * 50)

    success = asyncio.run(create_tables())

    print("\n" + "=" * 50)
    if success:
        print("Test database setup completed successfully!")
        return 0
    else:
        print("Test database setup failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
