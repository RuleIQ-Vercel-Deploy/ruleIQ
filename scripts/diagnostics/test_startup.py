#!/usr/bin/env python3
"""
RuleIQ Startup Validation Script

This script validates that the FastAPI application can start successfully
and all critical components are properly initialized.
"""

import sys
import asyncio
import logging
from typing import Dict, List, Tuple
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class StartupValidator:
    """Validates application startup and critical components."""

    def __init__(self):
        self.results: Dict[str, Tuple[bool, str]] = {}
        self.critical_failures: List[str] = []

    async def check_environment_variables(self) -> bool:
        """Check that required environment variables are set."""
        try:
            from config.settings import settings

            required_vars = [
                'DATABASE_URL',
                'JWT_SECRET_KEY',
                'ENVIRONMENT'
            ]

            missing_vars = []
            for var in required_vars:
                if not os.getenv(var) and not hasattr(settings, var.lower()):
                    missing_vars.append(var)

            if missing_vars:
                self.results['environment'] = (False, f"Missing vars: {', '.join(missing_vars)}")
                return False

            self.results['environment'] = (True, "All required environment variables present")
            return True

        except Exception as e:
            self.results['environment'] = (False, f"Error checking environment: {str(e)}")
            return False

    async def check_database_connection(self) -> bool:
        """Verify database connectivity and initialization."""
        try:
            from database.db_setup import init_db, get_async_db
            from sqlalchemy import text

            # Initialize database
            if not init_db():
                self.results['database'] = (False, "Database initialization failed")
                self.critical_failures.append("Database initialization failed")
                return False

            # Test async connection
            async for db in get_async_db():
                try:
                    result = await db.execute(text("SELECT 1"))
                    if result.scalar() == 1:
                        self.results['database'] = (True, "Database connection successful")
                        return True
                finally:
                    await db.close()
                    break

            self.results['database'] = (False, "Could not establish database connection")
            return False

        except Exception as e:
            self.results['database'] = (False, f"Database error: {str(e)}")
            self.critical_failures.append(f"Database connection failed: {str(e)}")
            return False

    async def check_api_initialization(self) -> bool:
        """Check if the FastAPI application can be initialized."""
        try:
            # Import the main app
            from main import app

            if app:
                # Check that routers are registered
                routes = [route.path for route in app.routes]

                critical_endpoints = [
                    '/api/v1/health',
                    '/api/v1/auth/login',
                    '/api/v1/assessments',
                    '/api/v1/compliance'
                ]

                missing_endpoints = []
                for endpoint in critical_endpoints:
                    # Check if endpoint pattern exists in routes
                    found = any(endpoint in route or route.startswith(endpoint.rsplit('/', 1)[0])
                               for route in routes)
                    if not found:
                        missing_endpoints.append(endpoint)

                if missing_endpoints:
                    self.results['api'] = (False, f"Missing endpoints: {', '.join(missing_endpoints)}")
                    return False

                self.results['api'] = (True, f"API initialized with {len(routes)} routes")
                return True
            else:
                self.results['api'] = (False, "Failed to initialize FastAPI app")
                return False

        except Exception as e:
            self.results['api'] = (False, f"API initialization error: {str(e)}")
            self.critical_failures.append(f"API initialization failed: {str(e)}")
            return False

    async def check_redis_connection(self) -> bool:
        """Check Redis connectivity if configured."""
        try:
            redis_url = os.getenv('REDIS_URL')
            if not redis_url:
                self.results['redis'] = (True, "Redis not configured (optional)")
                return True

            from database.redis_client import get_redis_client

            redis = await get_redis_client()
            if redis:
                await redis.ping()
                self.results['redis'] = (True, "Redis connection successful")
                return True
            else:
                self.results['redis'] = (False, "Redis client initialization failed")
                return False

        except Exception as e:
            # Redis is optional, so don't treat as critical failure
            self.results['redis'] = (False, f"Redis error (non-critical): {str(e)}")
            return True  # Return True since Redis is optional

    async def check_service_initialization(self) -> bool:
        """Check that critical services can be initialized."""
        try:
            services_to_check = [
                ('auth_service', 'services.auth_service'),
                ('assessment_service', 'services.assessment_service'),
                ('compliance_service', 'services.compliance.uk_compliance_engine'),
                ('ai_service', 'services.ai.assistant')
            ]

            failed_services = []
            for service_name, module_path in services_to_check:
                try:
                    module_parts = module_path.rsplit('.', 1)
                    if len(module_parts) == 2:
                        module = __import__(module_parts[0], fromlist=[module_parts[1]])
                    else:
                        module = __import__(module_path)
                    logger.info(f"✓ Service {service_name} loaded")
                except Exception as e:
                    failed_services.append(f"{service_name}: {str(e)}")
                    logger.warning(f"✗ Service {service_name} failed: {str(e)}")

            if failed_services:
                self.results['services'] = (False, f"Failed: {', '.join(failed_services[:3])}")
                return False

            self.results['services'] = (True, "All critical services initialized")
            return True

        except Exception as e:
            self.results['services'] = (False, f"Service check error: {str(e)}")
            return False

    async def run_validation(self) -> bool:
        """Run all validation checks."""
        logger.info("=" * 60)
        logger.info("RuleIQ Startup Validation")
        logger.info("=" * 60)

        # Run checks in order of criticality
        checks = [
            ("Environment Variables", self.check_environment_variables),
            ("Database Connection", self.check_database_connection),
            ("API Initialization", self.check_api_initialization),
            ("Redis Connection", self.check_redis_connection),
            ("Service Initialization", self.check_service_initialization)
        ]

        all_passed = True
        for check_name, check_func in checks:
            logger.info(f"\nChecking {check_name}...")
            try:
                result = await check_func()
                if not result and check_name != "Redis Connection":  # Redis is optional
                    all_passed = False
            except Exception as e:
                logger.error(f"Check failed with error: {str(e)}")
                self.results[check_name.lower().replace(' ', '_')] = (False, str(e))
                all_passed = False

        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("VALIDATION SUMMARY")
        logger.info("=" * 60)

        for check_name, (passed, message) in self.results.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            logger.info(f"{status:8} | {check_name:15} | {message}")

        if self.critical_failures:
            logger.error("\n" + "!" * 60)
            logger.error("CRITICAL FAILURES DETECTED:")
            for failure in self.critical_failures:
                logger.error(f"  - {failure}")
            logger.error("!" * 60)

        if all_passed:
            logger.info("\n✓ All startup validation checks passed!")
        else:
            logger.error("\n✗ Startup validation failed. Please fix the issues above.")

        return all_passed


async def main():
    """Main entry point for the validation script."""
    validator = StartupValidator()
    success = await validator.run_validation()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())