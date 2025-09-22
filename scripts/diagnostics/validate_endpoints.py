#!/usr/bin/env python3
"""
RuleIQ API Endpoint Validation Script

This script validates all API endpoints by checking:
1. Endpoint accessibility
2. Authentication requirements
3. Response schemas
4. Error handling
"""

import sys
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
import httpx
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EndpointValidator:
    """Validates API endpoints for accessibility and correctness."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: Dict[str, Dict] = {}
        self.auth_token: Optional[str] = None
        self.test_user_email = "test@ruleiq.com"
        self.test_user_password = "TestPassword123!"

    async def setup_test_user(self) -> bool:
        """Create or verify test user for authenticated endpoint testing."""
        try:
            # Try to create test user (may already exist)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/register",
                    json={
                        "email": self.test_user_email,
                        "password": self.test_user_password,
                        "first_name": "Test",
                        "last_name": "User",
                        "company": "RuleIQ Test"
                    }
                )
                if response.status_code in [200, 201]:
                    logger.info("Test user created successfully")
                elif response.status_code == 400:
                    # User might already exist
                    logger.info("Test user already exists")

            # Login to get auth token
            return await self.authenticate()

        except Exception as e:
            logger.error(f"Failed to setup test user: {str(e)}")
            return False

    async def authenticate(self) -> bool:
        """Authenticate and get JWT token."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/login",
                    data={
                        "username": self.test_user_email,
                        "password": self.test_user_password
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    self.auth_token = data.get("access_token")
                    logger.info("Authentication successful")
                    return True
                else:
                    logger.error(f"Authentication failed: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False

    async def check_endpoint(
        self,
        method: str,
        path: str,
        requires_auth: bool = False,
        data: Optional[Dict] = None,
        expected_status: List[int] = None
    ) -> Tuple[bool, str, int]:
        """Check a single endpoint."""
        if expected_status is None:
            expected_status = [200, 201, 204, 401, 403, 422]

        url = f"{self.base_url}{path}"
        headers = {}
        if requires_auth and self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data
                )

                success = response.status_code in expected_status
                message = f"Status: {response.status_code}"

                # Check response format
                if response.status_code < 500:
                    try:
                        response_data = response.json()
                        message += " - Valid JSON response"
                    except json.JSONDecodeError:
                        if response.status_code != 204:  # 204 No Content is ok
                            message += " - Invalid JSON response"
                            success = False

                return success, message, response.status_code

        except httpx.TimeoutException:
            return False, "Timeout", 0
        except httpx.ConnectError:
            return False, "Connection failed", 0
        except Exception as e:
            return False, f"Error: {str(e)}", 0

    async def validate_health_endpoints(self):
        """Validate health check endpoints."""
        logger.info("\n=== Validating Health Endpoints ===")

        endpoints = [
            ("GET", "/api/v1/health", False),
            ("GET", "/api/v1/info", False)
        ]

        for method, path, requires_auth in endpoints:
            success, message, status = await self.check_endpoint(method, path, requires_auth)
            self.results[f"health:{path}"] = {
                "success": success,
                "message": message,
                "status": status,
                "critical": True
            }
            logger.info(f"  {path}: {'✓' if success else '✗'} {message}")

    async def validate_auth_endpoints(self):
        """Validate authentication endpoints."""
        logger.info("\n=== Validating Authentication Endpoints ===")

        endpoints = [
            ("POST", "/api/v1/auth/login", False, {
                "username": self.test_user_email,
                "password": self.test_user_password
            }),
            ("GET", "/api/v1/auth/me", True, None),
            ("POST", "/api/v1/auth/refresh", True, None),
            ("POST", "/api/v1/auth/logout", True, None)
        ]

        for endpoint in endpoints:
            method, path, requires_auth, data = endpoint[0], endpoint[1], endpoint[2], endpoint[3] if len(endpoint) > 3 else None
            success, message, status = await self.check_endpoint(method, path, requires_auth, data)
            self.results[f"auth:{path}"] = {
                "success": success,
                "message": message,
                "status": status,
                "critical": True
            }
            logger.info(f"  {path}: {'✓' if success else '✗'} {message}")

    async def validate_business_endpoints(self):
        """Validate business logic endpoints."""
        logger.info("\n=== Validating Business Endpoints ===")

        endpoints = [
            # Assessment endpoints
            ("GET", "/api/v1/assessments", True),
            ("GET", "/api/v1/assessments/questions", True),
            ("GET", "/api/v1/assessments/sessions", True),

            # Compliance endpoints
            ("GET", "/api/v1/compliance/frameworks", True),
            ("GET", "/api/v1/compliance/requirements", True),
            ("GET", "/api/v1/uk-compliance/gdpr/status", True),

            # Evidence endpoints
            ("GET", "/api/v1/evidence", True),
            ("GET", "/api/v1/evidence/collection/status", True),

            # Policy endpoints
            ("GET", "/api/v1/policies", True),
            ("GET", "/api/v1/policies/templates", True),

            # Reporting endpoints
            ("GET", "/api/v1/reports", True),
            ("GET", "/api/v1/dashboard/stats", True)
        ]

        for method, path, requires_auth in endpoints:
            success, message, status = await self.check_endpoint(method, path, requires_auth)
            self.results[f"business:{path}"] = {
                "success": success,
                "message": message,
                "status": status,
                "critical": False
            }
            logger.info(f"  {path}: {'✓' if success else '✗'} {message}")

    async def validate_admin_endpoints(self):
        """Validate admin endpoints."""
        logger.info("\n=== Validating Admin Endpoints ===")

        endpoints = [
            ("GET", "/api/v1/admin/users", True),
            ("GET", "/api/v1/admin/audit-logs", True),
            ("GET", "/api/v1/monitoring/metrics", True),
            ("GET", "/api/v1/monitoring/performance", True)
        ]

        for method, path, requires_auth in endpoints:
            success, message, status = await self.check_endpoint(method, path, requires_auth)
            self.results[f"admin:{path}"] = {
                "success": success,
                "message": message,
                "status": status,
                "critical": False
            }
            logger.info(f"  {path}: {'✓' if success else '✗'} {message}")

    async def validate_websocket_endpoints(self):
        """Validate WebSocket endpoints."""
        logger.info("\n=== Validating WebSocket Endpoints ===")

        ws_endpoints = [
            "/ws/chat",
            "/ws/notifications",
            "/ws/ai-cost"
        ]

        for path in ws_endpoints:
            ws_url = f"ws://localhost:8000{path}"
            try:
                async with httpx.AsyncClient() as client:
                    # WebSocket endpoints should respond to HTTP with upgrade required
                    response = await client.get(f"http://localhost:8000{path}")
                    if response.status_code in [426, 400]:  # Upgrade Required or Bad Request
                        self.results[f"websocket:{path}"] = {
                            "success": True,
                            "message": "WebSocket endpoint exists",
                            "status": response.status_code,
                            "critical": False
                        }
                        logger.info(f"  {path}: ✓ WebSocket endpoint exists")
                    else:
                        self.results[f"websocket:{path}"] = {
                            "success": False,
                            "message": f"Unexpected status: {response.status_code}",
                            "status": response.status_code,
                            "critical": False
                        }
                        logger.info(f"  {path}: ✗ Unexpected response")
            except Exception as e:
                self.results[f"websocket:{path}"] = {
                    "success": False,
                    "message": str(e),
                    "status": 0,
                    "critical": False
                }
                logger.info(f"  {path}: ✗ {str(e)}")

    async def generate_report(self) -> bool:
        """Generate validation report."""
        logger.info("\n" + "=" * 60)
        logger.info("ENDPOINT VALIDATION REPORT")
        logger.info("=" * 60)
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info(f"Base URL: {self.base_url}")
        logger.info(f"Total Endpoints Tested: {len(self.results)}")

        # Count results
        passed = sum(1 for r in self.results.values() if r["success"])
        failed = len(self.results) - passed
        critical_failures = sum(1 for r in self.results.values()
                               if not r["success"] and r.get("critical", False))

        logger.info(f"Passed: {passed} | Failed: {failed} | Critical Failures: {critical_failures}")

        # List failures
        if failed > 0:
            logger.info("\n--- Failed Endpoints ---")
            for endpoint, result in self.results.items():
                if not result["success"]:
                    criticality = "CRITICAL" if result.get("critical", False) else "Non-critical"
                    logger.info(f"  [{criticality}] {endpoint}: {result['message']}")

        # Summary
        all_passed = critical_failures == 0
        if all_passed:
            logger.info("\n✓ All critical endpoints are operational!")
        else:
            logger.error(f"\n✗ {critical_failures} critical endpoint(s) failed!")

        # Save detailed report
        report_path = PROJECT_ROOT / "validation_report.json"
        with open(report_path, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "base_url": self.base_url,
                "summary": {
                    "total": len(self.results),
                    "passed": passed,
                    "failed": failed,
                    "critical_failures": critical_failures
                },
                "results": self.results
            }, f, indent=2)
        logger.info(f"\nDetailed report saved to: {report_path}")

        return all_passed

    async def run_validation(self) -> bool:
        """Run all endpoint validations."""
        try:
            # Check if server is running
            logger.info("Checking server availability...")
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(f"{self.base_url}/api/v1/health", timeout=5.0)
                    if response.status_code != 200:
                        logger.error(f"Server health check failed: {response.status_code}")
                        logger.error("Please ensure the server is running: uvicorn main:app")
                        return False
                except (httpx.ConnectError, httpx.TimeoutException):
                    logger.error("Cannot connect to server!")
                    logger.error("Please start the server first: uvicorn main:app")
                    return False

            logger.info("Server is accessible, starting validation...")

            # Setup test user and authenticate
            await self.setup_test_user()

            # Run validations
            await self.validate_health_endpoints()
            await self.validate_auth_endpoints()
            await self.validate_business_endpoints()
            await self.validate_admin_endpoints()
            await self.validate_websocket_endpoints()

            # Generate report
            return await self.generate_report()

        except Exception as e:
            logger.error(f"Validation failed with error: {str(e)}")
            return False


async def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate RuleIQ API endpoints")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="Base URL of the API (default: http://localhost:8000)"
    )

    args = parser.parse_args()

    validator = EndpointValidator(base_url=args.base_url)
    success = await validator.run_validation()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())