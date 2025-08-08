#!/usr/bin/env python3
"""
Apply performance indexes to the database for Phase 4: Performance Optimization

This script applies the critical database indexes needed to fix the performance issues
identified in the test suite, particularly for evidence queries and pagination.
"""

import asyncio
import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

# Load environment variables
load_dotenv()

from config.logging_config import get_logger, setup_logging
from database.db_setup import _init_async_db
from typing import Optional

# Setup logging
setup_logging()
logger = get_logger(__name__)


async def check_index_exists(db, index_name: str, table_name: str) -> bool:
    """Check if an index already exists."""
    try:
        query = text("""
            SELECT 1 FROM pg_indexes
            WHERE indexname = :index_name AND tablename = :table_name
        """)
        result = await db.execute(query, {"index_name": index_name, "table_name": table_name})
        return result.fetchone() is not None
    except Exception as e:
        logger.warning(f"Error checking index {index_name}: {e}")
        return False


async def create_index_safely(db, index_sql: str, index_name: str, table_name: str) -> bool:
    """Create an index safely, checking if it already exists."""
    try:
        # Check if index already exists
        if await check_index_exists(db, index_name, table_name):
            logger.info(f"Index {index_name} already exists, skipping...")
            return True

        # Create the index
        logger.info(f"Creating index: {index_name}")
        await db.execute(text(index_sql))
        logger.info(f"✓ Successfully created index: {index_name}")
        return True

    except ProgrammingError as e:
        if "already exists" in str(e).lower():
            logger.info(f"Index {index_name} already exists (caught during creation)")
            return True
        else:
            logger.error(f"✗ Failed to create index {index_name}: {e}")
            return False
    except Exception as e:
        logger.error(f"✗ Unexpected error creating index {index_name}: {e}")
        return False


async def apply_performance_indexes():
    """Apply all performance indexes for evidence queries."""
    logger.info("Starting performance index creation...")

    # Initialize async database
    _init_async_db()

    # Import the engine after initialization
    from database.db_setup import _async_engine

    if _async_engine is None:
        logger.error("Failed to initialize database engine")
        return False

    success_count = 0
    total_count = 0

    # Define all indexes to create
    indexes = [
        # Evidence Items Performance Indexes
        (
            "CREATE INDEX IF NOT EXISTS idx_evidence_items_user_id ON evidence_items (user_id)",
            "idx_evidence_items_user_id",
            "evidence_items",
        ),
        (
            "CREATE INDEX IF NOT EXISTS idx_evidence_items_framework_id ON evidence_items (framework_id)",
            "idx_evidence_items_framework_id",
            "evidence_items",
        ),
        (
            "CREATE INDEX IF NOT EXISTS idx_evidence_items_business_profile_id ON evidence_items (business_profile_id)",
            "idx_evidence_items_business_profile_id",
            "evidence_items",
        ),
        (
            "CREATE INDEX IF NOT EXISTS idx_evidence_items_status ON evidence_items (status)",
            "idx_evidence_items_status",
            "evidence_items",
        ),
        (
            "CREATE INDEX IF NOT EXISTS idx_evidence_items_evidence_type ON evidence_items (evidence_type)",
            "idx_evidence_items_evidence_type",
            "evidence_items",
        ),
        # Composite indexes for common query patterns
        (
            "CREATE INDEX IF NOT EXISTS idx_evidence_items_user_framework ON evidence_items (user_id, framework_id)",
            "idx_evidence_items_user_framework",
            "evidence_items",
        ),
        (
            "CREATE INDEX IF NOT EXISTS idx_evidence_items_user_status ON evidence_items (user_id, status)",
            "idx_evidence_items_user_status",
            "evidence_items",
        ),
        (
            "CREATE INDEX IF NOT EXISTS idx_evidence_items_user_type ON evidence_items (user_id, evidence_type)",
            "idx_evidence_items_user_type",
            "evidence_items",
        ),
        (
            "CREATE INDEX IF NOT EXISTS idx_evidence_items_framework_status ON evidence_items (framework_id, status)",
            "idx_evidence_items_framework_status",
            "evidence_items",
        ),
        # Timestamp indexes for sorting and pagination
        (
            "CREATE INDEX IF NOT EXISTS idx_evidence_items_created_at ON evidence_items (created_at)",
            "idx_evidence_items_created_at",
            "evidence_items",
        ),
        (
            "CREATE INDEX IF NOT EXISTS idx_evidence_items_updated_at ON evidence_items (updated_at)",
            "idx_evidence_items_updated_at",
            "evidence_items",
        ),
        # Composite indexes for pagination with user filtering
        (
            "CREATE INDEX IF NOT EXISTS idx_evidence_items_user_created ON evidence_items (user_id, created_at)",
            "idx_evidence_items_user_created",
            "evidence_items",
        ),
        (
            "CREATE INDEX IF NOT EXISTS idx_evidence_items_user_updated ON evidence_items (user_id, updated_at)",
            "idx_evidence_items_user_updated",
            "evidence_items",
        ),
        # Business Profiles Performance Indexes
        (
            "CREATE INDEX IF NOT EXISTS idx_business_profiles_user_id ON business_profiles (user_id)",
            "idx_business_profiles_user_id",
            "business_profiles",
        ),
        # Users table indexes
        ("CREATE INDEX IF NOT EXISTS idx_users_email ON users (email)", "idx_users_email", "users"),
        (
            "CREATE INDEX IF NOT EXISTS idx_users_is_active ON users (is_active)",
            "idx_users_is_active",
            "users",
        ),
    ]

    # Create indexes in transaction
    async with _async_engine.begin() as conn:
        for index_sql, index_name, table_name in indexes:
            total_count += 1
            if await create_index_safely(conn, index_sql, index_name, table_name):
                success_count += 1

    logger.info(f"Index creation completed: {success_count}/{total_count} successful")
    return success_count == total_count


async def verify_indexes() -> bool:
    """Verify that the critical indexes were created successfully."""
    logger.info("Verifying index creation...")

    # Import the engine
    from database.db_setup import _async_engine

    critical_indexes = [
        "idx_evidence_items_user_id",
        "idx_evidence_items_user_framework",
        "idx_evidence_items_user_created",
        "idx_evidence_items_status",
        "idx_business_profiles_user_id",
    ]

    async with _async_engine.begin() as conn:
        for index_name in critical_indexes:
            query = text("SELECT 1 FROM pg_indexes WHERE indexname = :index_name")
            result = await conn.execute(query, {"index_name": index_name})
            if result.fetchone():
                logger.info(f"✓ Verified index: {index_name}")
            else:
                logger.error(f"✗ Missing index: {index_name}")
                return False

    logger.info("✓ All critical indexes verified successfully!")
    return True


async def main() -> Optional[bool]:
    """Main function to apply performance indexes."""
    logger.info("Phase 4: Performance Optimization - Database Index Creation")
    logger.info("=" * 60)

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("DATABASE_URL environment variable not set")
        return False

    logger.info(f"Database URL: {database_url}")

    try:
        # Apply indexes
        if not await apply_performance_indexes():
            logger.error("Failed to apply all performance indexes")
            return False

        # Verify indexes
        if not await verify_indexes():
            logger.error("Index verification failed")
            return False

        logger.info("=" * 60)
        logger.info("✓ Performance indexes applied successfully!")
        logger.info("Database is now optimized for evidence queries and pagination.")
        return True

    except Exception as e:
        logger.error(f"Error during index creation: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
