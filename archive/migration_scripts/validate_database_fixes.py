#!/usr/bin/env python3
"""
Database Validation Script for ruleIQ Platform
Validates that database schema fixes have been applied correctly
"""

import asyncio
import logging
from typing import Dict, List, Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseValidator:
    """Validates database schema fixes and integrity."""

    def __init__(self, async_database_url: str) -> None:
        self.async_database_url = async_database_url
        self.async_engine = create_async_engine(async_database_url)

    async def check_table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database."""
        async with self.async_engine.begin() as conn:
            result = await conn.execute(
                text(
                    """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = :table_name
                )
            """
                ),
                {"table_name": table_name},
            )

            return result.scalar()

    async def get_table_columns(self, table_name: str) -> List[str]:
        """Get all column names for a table."""
        async with self.async_engine.begin() as conn:
            result = await conn.execute(
                text(
                    """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = :table_name
                ORDER BY ordinal_position
            """
                ),
                {"table_name": table_name},
            )

            return [row[0] for row in result.fetchall()]

    async def validate_assessment_sessions_schema(self) -> Dict[str, Any]:
        """Validate assessment_sessions table schema."""
        logger.info("Validating assessment_sessions table schema...")

        # Expected columns (fixed names)
        expected_columns = {
            "business_profile_id",
            "questions_answered",
            "calculated_scores",
            "recommended_frameworks",
        }

        # Truncated columns that should NOT exist
        truncated_columns = {
            "business_profil",
            "questions_answe",
            "calculated_scor",
            "recommended_fra",
        }

        if not await self.check_table_exists("assessment_sessions"):
            return {
                "status": "ERROR",
                "message": "assessment_sessions table does not exist",
            }

        all_columns = set(await self.get_table_columns("assessment_sessions"))

        # Check for expected columns
        missing_expected = expected_columns - all_columns
        found_truncated = truncated_columns.intersection(all_columns)

        if missing_expected:
            return {
                "status": "ERROR",
                "message": f"Missing expected columns: {missing_expected}",
                "missing_columns": list(missing_expected),
                "truncated_columns_found": list(found_truncated),
            }

        if found_truncated:
            return {
                "status": "ERROR",
                "message": f"Found truncated columns that should be fixed: {found_truncated}",
                "truncated_columns_found": list(found_truncated),
            }

        return {
            "status": "SUCCESS",
            "message": "assessment_sessions table schema is correct",
            "columns_found": list(expected_columns),
        }

    async def validate_business_profiles_schema(self) -> Dict[str, Any]:
        """Validate business_profiles table schema."""
        logger.info("Validating business_profiles table schema...")

        # Expected columns (fixed names)
        expected_columns = {
            "handles_personal_data",
            "processes_payments",
            "stores_health_data",
            "provides_financial_services",
            "operates_critical_infrastructure",
            "has_international_operations",
        }

        # Truncated columns that should NOT exist
        truncated_columns = {
            "handles_persona",
            "processes_payme",
            "stores_health_d",
            "provides_financ",
            "operates_critic",
            "has_internation",
        }

        if not await self.check_table_exists("business_profiles"):
            return {
                "status": "ERROR",
                "message": "business_profiles table does not exist",
            }

        all_columns = set(await self.get_table_columns("business_profiles"))

        # Check for expected columns
        missing_expected = expected_columns - all_columns
        found_truncated = truncated_columns.intersection(all_columns)

        if missing_expected:
            return {
                "status": "ERROR",
                "message": f"Missing expected columns: {missing_expected}",
                "missing_columns": list(missing_expected),
                "truncated_columns_found": list(found_truncated),
            }

        if found_truncated:
            return {
                "status": "ERROR",
                "message": f"Found truncated columns that should be fixed: {found_truncated}",
                "truncated_columns_found": list(found_truncated),
            }

        return {
            "status": "SUCCESS",
            "message": "business_profiles table schema is correct",
            "columns_found": list(expected_columns),
        }

    async def validate_foreign_key_constraints(self) -> Dict[str, Any]:
        """Validate foreign key constraints are working correctly."""
        logger.info("Validating foreign key constraints...")

        async with self.async_engine.begin() as conn:
            # Check assessment_sessions -> business_profiles foreign key
            fk_result = await conn.execute(
                text(
                    """
                SELECT
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints AS tc
                JOIN information_schema.key_column_usage AS kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage AS ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_name = 'assessment_sessions'
                    AND kcu.column_name = 'business_profile_id'
            """
                )
            )

            fk_constraints = fk_result.fetchall()

            if not fk_constraints:
                return {
                    "status": "WARNING",
                    "message": "No foreign key constraint found for assessment_sessions.business_profile_id",
                }

            return {
                "status": "SUCCESS",
                "message": "Foreign key constraints are correct",
                "constraints_found": len(fk_constraints),
            }

    async def test_basic_queries(self) -> Dict[str, Any]:
        """Test basic queries to ensure schema works correctly."""
        logger.info("Testing basic database queries...")

        try:
            async with self.async_engine.begin() as conn:
                # Test assessment_sessions query
                await conn.execute(
                    text(
                        """
                    SELECT
                        business_profile_id,
                        questions_answered,
                        calculated_scores,
                        recommended_frameworks
                    FROM assessment_sessions
                    LIMIT 1
                """
                    )
                )

                # Test business_profiles query
                await conn.execute(
                    text(
                        """
                    SELECT
                        handles_personal_data,
                        processes_payments,
                        stores_health_data
                    FROM business_profiles
                    LIMIT 1
                """
                    )
                )

                return {
                    "status": "SUCCESS",
                    "message": "Basic queries executed successfully",
                    "queries_tested": 2,
                }

        except Exception as e:
            return {"status": "ERROR", "message": f"Query execution failed: {str(e)}"}

    async def check_migration_version(self) -> Dict[str, Any]:
        """Check current Alembic migration version."""
        logger.info("Checking migration version...")

        try:
            async with self.async_engine.begin() as conn:
                result = await conn.execute(
                    text(
                        """
                    SELECT version_num FROM alembic_version
                """
                    )
                )

                version = result.scalar()

                if version and version >= "009":
                    return {
                        "status": "SUCCESS",
                        "message": f"Migration version {version} is current",
                        "version": version,
                    }
                else:
                    return {
                        "status": "WARNING",
                        "message": f"Migration version {version} may be outdated",
                        "version": version,
                    }

        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Could not check migration version: {str(e)}",
            }

    async def run_full_validation(self) -> Dict[str, Any]:
        """Run complete database validation."""
        logger.info("🔍 Starting full database validation...")

        results = {}

        # Check migration version
        results["migration_version"] = await self.check_migration_version()

        # Validate assessment_sessions schema
        results["assessment_sessions"] = (
            await self.validate_assessment_sessions_schema()
        )

        # Validate business_profiles schema
        results["business_profiles"] = await self.validate_business_profiles_schema()

        # Validate foreign key constraints
        results["foreign_keys"] = await self.validate_foreign_key_constraints()

        # Test basic queries
        results["basic_queries"] = await self.test_basic_queries()

        # Determine overall status
        all_success = all(result["status"] == "SUCCESS" for result in results.values())

        has_errors = any(result["status"] == "ERROR" for result in results.values())

        if all_success:
            overall_status = "SUCCESS"
            overall_message = "✅ All database validations passed!"
        elif has_errors:
            overall_status = "ERROR"
            overall_message = "❌ Database validation failed with errors"
        else:
            overall_status = "WARNING"
            overall_message = "⚠️ Database validation completed with warnings"

        results["overall"] = {"status": overall_status, "message": overall_message}

        return results

    async def cleanup(self) -> None:
        """Clean up database connections."""
        await self.async_engine.dispose()


def print_validation_results(results: Dict[str, Any]) -> None:
    """Print validation results in a formatted way."""
    print("\n" + "=" * 60)
    print("🔍 DATABASE VALIDATION RESULTS")
    print("=" * 60)

    for test_name, result in results.items():
        if test_name == "overall":
            continue

        status = result["status"]
        message = result["message"]

        status_icon = {"SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}.get(status, "❓")

        print(f"\n{status_icon} {test_name.upper()}:")
        print(f"   Status: {status}")
        print(f"   Message: {message}")

        # Print additional details if available
        if "missing_columns" in result:
            print(f"   Missing columns: {result['missing_columns']}")
        if "truncated_columns_found" in result:
            print(f"   Truncated columns found: {result['truncated_columns_found']}")
        if "version" in result:
            print(f"   Version: {result['version']}")

    # Print overall result
    overall = results.get("overall", {})
    print(f"\n{'=' * 60}")
    print(f"{overall.get('message', 'Unknown status')}")
    print(f"{'=' * 60}\n")


async def main() -> None:
    """Main function to run database validation."""
    from config.settings import get_settings

    # Get database configuration
    settings = get_settings()
    async_database_url = settings.async_database_url

    # Initialize validator
    validator = DatabaseValidator(async_database_url)

    try:
        # Run full validation
        results = await validator.run_full_validation()

        # Print results
        print_validation_results(results)

        # Return appropriate exit code
        if results["overall"]["status"] == "ERROR":
            sys.exit(1)
        elif results["overall"]["status"] == "WARNING":
            sys.exit(2)
        else:
            sys.exit(0)

    except Exception as e:
        logger.error(f"❌ Unexpected error during validation: {str(e)}")
        sys.exit(1)

    finally:
        await validator.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
