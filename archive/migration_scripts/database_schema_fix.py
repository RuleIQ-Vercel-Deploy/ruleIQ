#!/usr/bin/env python3
"""
Database Schema Fix Script for ruleIQ Platform
Fixes column name truncation issues and applies necessary migrations
"""

import asyncio
import logging
from typing import List, Dict

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseSchemaFixer:
    """Handles database schema fixes for column name truncation issues."""

    def __init__(self, database_url: str, async_database_url: str) -> None:
        self.database_url = database_url
        self.async_database_url = async_database_url
        self.engine = create_engine(database_url)
        self.async_engine = create_async_engine(async_database_url)

    async def check_current_schema(self) -> Dict[str, List[str]]:
        """Check current database schema for truncation issues."""
        logger.info("Checking current database schema...")

        async with self.async_engine.begin() as conn:
            # Check assessment_sessions table columns
            assessment_result = await conn.execute(
                text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'assessment_sessions'
                AND column_name IN ('business_profil', 'questions_answe', 'calculated_scor', 'recommended_fra')
            """)
            )

            truncated_assessment_columns = [row[0] for row in assessment_result.fetchall()]

            # Check business_profiles table columns
            business_result = await conn.execute(
                text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'business_profiles'
                AND column_name IN ('handles_persona', 'processes_payme', 'stores_health_d')
            """)
            )

            truncated_business_columns = [row[0] for row in business_result.fetchall()]

            return {
                "assessment_sessions": truncated_assessment_columns,
                "business_profiles": truncated_business_columns,
            }

    async def verify_migrations_applied(self) -> Dict[str, bool]:
        """Verify which migrations have been applied."""
        logger.info("Checking migration status...")

        async with self.async_engine.begin() as conn:
            # Check if alembic_version table exists
            table_exists = await conn.execute(
                text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = 'alembic_version'
                )
            """)
            )

            if not table_exists.scalar():
                logger.warning("Alembic version table not found - database may not be initialized")
                return {"migration_008": False, "migration_009": False}

            # Check current migration version
            version_result = await conn.execute(
                text("""
                SELECT version_num FROM alembic_version
            """)
            )

            current_version = version_result.scalar()
            logger.info(f"Current migration version: {current_version}")

            return {
                "migration_008": current_version and current_version >= "008",
                "migration_009": current_version and current_version >= "009",
            }

    def apply_migrations(self) -> bool:
        """Apply pending migrations using Alembic."""
        try:
            logger.info("Applying database migrations...")

            # Create Alembic config
            alembic_cfg = Config("alembic.ini")

            # Apply all pending migrations
            command.upgrade(alembic_cfg, "head")

            logger.info("✅ Migrations applied successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error applying migrations: {str(e)}")
            return False

    async def create_backup_tables(self) -> bool:
        """Create backup tables before applying fixes."""
        try:
            logger.info("Creating backup tables...")

            async with self.async_engine.begin() as conn:
                # Backup assessment_sessions table
                await conn.execute(
                    text("""
                    CREATE TABLE IF NOT EXISTS assessment_sessions_backup_20250109
                    AS SELECT * FROM assessment_sessions
                """)
                )

                # Backup business_profiles table
                await conn.execute(
                    text("""
                    CREATE TABLE IF NOT EXISTS business_profiles_backup_20250109
                    AS SELECT * FROM business_profiles
                """)
                )

                await conn.commit()

            logger.info("✅ Backup tables created successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Error creating backup tables: {str(e)}")
            return False

    async def validate_fix_success(self) -> bool:
        """Validate that the schema fixes were successful."""
        logger.info("Validating schema fixes...")

        try:
            async with self.async_engine.begin() as conn:
                # Check that assessment_sessions has correct column names
                assessment_result = await conn.execute(
                    text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'assessment_sessions'
                    AND column_name IN ('business_profile_id', 'questions_answered', 'calculated_scores', 'recommended_frameworks')
                """)
                )

                fixed_assessment_columns = [row[0] for row in assessment_result.fetchall()]

                # Check that business_profiles has correct column names
                business_result = await conn.execute(
                    text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'business_profiles'
                    AND column_name IN ('handles_personal_data', 'processes_payments', 'stores_health_data')
                """)
                )

                fixed_business_columns = [row[0] for row in business_result.fetchall()]

                # Validate results
                expected_assessment = {
                    "business_profile_id",
                    "questions_answered",
                    "calculated_scores",
                    "recommended_frameworks",
                }
                expected_business = {
                    "handles_personal_data",
                    "processes_payments",
                    "stores_health_data",
                }

                assessment_success = set(fixed_assessment_columns) == expected_assessment
                business_success = set(fixed_business_columns) == expected_business

                if assessment_success and business_success:
                    logger.info("✅ Schema fixes validated successfully")
                    return True
                else:
                    logger.error("❌ Schema validation failed")
                    logger.error(f"Assessment columns: {fixed_assessment_columns}")
                    logger.error(f"Business columns: {fixed_business_columns}")
                    return False

        except Exception as e:
            logger.error(f"❌ Error validating schema fixes: {str(e)}")
            return False

    async def run_complete_fix(self) -> bool:
        """Run the complete database schema fix process."""
        logger.info("🔧 Starting database schema fix process...")

        # Step 1: Check current schema
        truncated_columns = await self.check_current_schema()
        logger.info(f"Found truncated columns: {truncated_columns}")

        # Step 2: Check migration status
        migration_status = await self.verify_migrations_applied()
        logger.info(f"Migration status: {migration_status}")

        # Step 3: Create backup tables
        if not await self.create_backup_tables():
            logger.error("Failed to create backup tables - aborting")
            return False

        # Step 4: Apply migrations
        if not self.apply_migrations():
            logger.error("Failed to apply migrations - aborting")
            return False

        # Step 5: Validate fixes
        if not await self.validate_fix_success():
            logger.error("Schema fixes validation failed")
            return False

        logger.info("🎉 Database schema fix completed successfully!")
        return True

    async def cleanup(self) -> None:
        """Clean up database connections."""
        await self.async_engine.dispose()
        self.engine.dispose()


async def main() -> None:
    """Main function to run the database schema fix."""
    from config.settings import get_settings

    # Get database configuration
    settings = get_settings()

    # Create database URLs
    database_url = settings.database_url
    async_database_url = settings.async_database_url

    # Initialize fixer
    fixer = DatabaseSchemaFixer(database_url, async_database_url)

    try:
        # Run complete fix
        success = await fixer.run_complete_fix()

        if success:
            print("\n✅ Database schema fix completed successfully!")
            print("🔧 All column name truncation issues resolved")
            print("📊 Database is now ready for production deployment")
        else:
            print("\n❌ Database schema fix failed")
            print("🔍 Check logs for details")

    except Exception as e:
        logger.error(f"❌ Unexpected error during schema fix: {str(e)}")

    finally:
        await fixer.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
