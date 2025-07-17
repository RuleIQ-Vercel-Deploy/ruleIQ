"""
Manual migration script to create integration and evidence tables
Run this script to create the required database tables for the integration system
"""

import asyncio
from database.db_setup import get_async_engine
from database.models.integrations import Base
from config.logging_config import get_logger

logger = get_logger(__name__)


async def create_integration_tables():
    """Create all integration-related tables"""
    try:
        engine = get_async_engine()

        # Create all tables defined in the models
        async with engine.begin() as conn:
            # Use Alembic migrations instead of create_all
        # This function is deprecated - use 'alembic upgrade head' instead
        logger.warning("create_integration_tables is deprecated. Use 'alembic upgrade head' instead.")
        return True
            logger.info("Successfully created integration tables")

        logger.info("Integration tables created successfully")

    except Exception as e:
        logger.error(f"Failed to create integration tables: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(create_integration_tables())
