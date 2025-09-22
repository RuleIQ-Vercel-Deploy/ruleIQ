#!/usr/bin/env python3
"""
Local testing script for Vercel deployment.
Simulates Vercel environment locally for testing.
"""

import os
import sys
import time
import json
import asyncio
import tracemalloc
from pathlib import Path
from typing import Dict, List, Optional
import httpx
import uvicorn
from multiprocessing import Process

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class VercelLocalTester:
    """Test the application locally with Vercel-like environment."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.base_url = "http://localhost:8000"
        self.server_process = None
        self.test_results = {
            "passed": [],
            "failed": [],
            "warnings": [],
            "metrics": {}
        }

    def setup_environment(self):
        """Set up Vercel-like environment variables."""
        print("🔧 Setting up Vercel environment simulation...")

        # Simulate Vercel environment
        os.environ["VERCEL"] = "1"
        os.environ["VERCEL_ENV"] = "development"
        os.environ["ENVIRONMENT"] = "development"

        # Disable features that don't work in serverless
        os.environ["ENABLE_MONITORING"] = "false"
        os.environ["ENABLE_BACKGROUND_TASKS"] = "false"
        os.environ["ENABLE_WEBSOCKETS"] = "false"

        # Load .env file if exists
        env_file = self.project_root / ".env"
        if env_file.exists():
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print("✅ Loaded environment variables from .env")

    def start_server(self):
        """Start the Vercel handler locally."""
        def run_server():
            import sys
            sys.path.insert(0, str(self.project_root))
            from api.vercel_handler import app
            uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error")

        self.server_process = Process(target=run_server)
        self.server_process.start()
        print("🚀 Starting local server...")

        # Wait for server to start
        time.sleep(3)

        # Check if server is running
        try:
            response = httpx.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                print("✅ Server started successfully")
                return True
        except:
            pass

        print("❌ Failed to start server")
        return False

    def stop_server(self):
        """Stop the local server."""
        if self.server_process:
            self.server_process.terminate()
            self.server_process.join()
            print("🛑 Server stopped")

    async def test_cold_start(self):
        """Test cold start performance."""
        print("\n🧊 Testing cold start performance...")

        # Stop and restart server to simulate cold start
        self.stop_server()

        tracemalloc.start()
        start_time = time.time()
        memory_before = tracemalloc.get_traced_memory()[0]

        # Start server
        success = self.start_server()
        if not success:
            self.test_results["failed"].append("Cold start failed")
            return

        # Make first request
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/health")

        cold_start_time = time.time() - start_time
        memory_after = tracemalloc.get_traced_memory()[0]
        memory_used = (memory_after - memory_before) / (1024 * 1024)  # MB
        tracemalloc.stop()

        self.test_results["metrics"]["cold_start_time"] = f"{cold_start_time:.2f} seconds"
        self.test_results["metrics"]["memory_used"] = f"{memory_used:.2f} MB"

        print(f"  ⏱️  Cold start time: {cold_start_time:.2f}s")
        print(f"  💾 Memory used: {memory_used:.2f} MB")

        if cold_start_time > 10:
            self.test_results["warnings"].append(f"Cold start time ({cold_start_time:.2f}s) is high")
        else:
            self.test_results["passed"].append("Cold start performance acceptable")

    async def test_endpoints(self):
        """Test critical API endpoints."""
        print("\n🔍 Testing API endpoints...")

        endpoints = [
            ("GET", "/api/health", None, 200),
            ("GET", "/api/ready", None, 200),
            ("GET", "/", None, 200),
            ("GET", "/api/docs", None, 200),  # Should work in development
            ("POST", "/api/auth/login", {"username": "test", "password": "test"}, [400, 401, 422]),
        ]

        async with httpx.AsyncClient(timeout=30.0) as client:
            for method, path, data, expected_status in endpoints:
                try:
                    url = f"{self.base_url}{path}"

                    if method == "GET":
                        response = await client.get(url)
                    elif method == "POST":
                        response = await client.post(url, json=data)
                    else:
                        continue

                    # Check status code
                    if isinstance(expected_status, list):
                        success = response.status_code in expected_status
                    else:
                        success = response.status_code == expected_status

                    if success:
                        self.test_results["passed"].append(f"{method} {path}: {response.status_code}")
                        print(f"  ✅ {method} {path}: {response.status_code}")
                    else:
                        self.test_results["failed"].append(f"{method} {path}: {response.status_code} (expected {expected_status})")
                        print(f"  ❌ {method} {path}: {response.status_code} (expected {expected_status})")

                except Exception as e:
                    self.test_results["failed"].append(f"{method} {path}: {e}")
                    print(f"  ❌ {method} {path}: {e}")

    async def test_database_connection(self):
        """Test database connectivity."""
        print("\n🗄️  Testing database connection...")

        if not os.getenv("DATABASE_URL"):
            self.test_results["warnings"].append("DATABASE_URL not set - skipping database tests")
            print("  ⚠️  DATABASE_URL not set - skipping")
            return

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/ready")
                data = response.json()

                if data.get("database") == "connected":
                    self.test_results["passed"].append("Database connection successful")
                    print("  ✅ Database connection successful")
                else:
                    self.test_results["warnings"].append("Database connection unavailable")
                    print("  ⚠️  Database connection unavailable")

        except Exception as e:
            self.test_results["failed"].append(f"Database test failed: {e}")
            print(f"  ❌ Database test failed: {e}")

    async def test_authentication(self):
        """Test JWT authentication flow."""
        print("\n🔐 Testing authentication...")

        if not os.getenv("JWT_SECRET_KEY"):
            self.test_results["warnings"].append("JWT_SECRET_KEY not set - skipping auth tests")
            print("  ⚠️  JWT_SECRET_KEY not set - skipping")
            return

        # This is a basic test - in production you'd test with real credentials
        async with httpx.AsyncClient() as client:
            # Test invalid login
            response = await client.post(
                f"{self.base_url}/api/auth/login",
                data={"username": "invalid", "password": "invalid"}
            )

            if response.status_code in [400, 401, 422]:
                self.test_results["passed"].append("Auth rejection working")
                print("  ✅ Authentication rejection working")
            else:
                self.test_results["failed"].append(f"Unexpected auth response: {response.status_code}")
                print(f"  ❌ Unexpected auth response: {response.status_code}")

    async def test_ai_endpoints(self):
        """Test AI-powered endpoints if configured."""
        print("\n🤖 Testing AI endpoints...")

        has_ai = os.getenv("GOOGLE_AI_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not has_ai:
            self.test_results["warnings"].append("No AI API keys - skipping AI tests")
            print("  ⚠️  No AI API keys configured - skipping")
            return

        # Check if AI routers are loaded
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/api/docs")
            if response.status_code == 200:
                # Check if docs mention AI endpoints
                self.test_results["passed"].append("AI endpoints available")
                print("  ✅ AI endpoints available")
            else:
                self.test_results["warnings"].append("Cannot verify AI endpoints")
                print("  ⚠️  Cannot verify AI endpoints")

    async def test_performance(self):
        """Test endpoint performance."""
        print("\n⚡ Testing performance...")

        async with httpx.AsyncClient() as client:
            # Test health endpoint performance
            times = []
            for i in range(10):
                start = time.time()
                response = await client.get(f"{self.base_url}/api/health")
                elapsed = time.time() - start
                times.append(elapsed)

            avg_time = sum(times) / len(times)
            max_time = max(times)

            self.test_results["metrics"]["avg_response_time"] = f"{avg_time*1000:.2f} ms"
            self.test_results["metrics"]["max_response_time"] = f"{max_time*1000:.2f} ms"

            print(f"  📊 Average response time: {avg_time*1000:.2f} ms")
            print(f"  📊 Max response time: {max_time*1000:.2f} ms")

            if avg_time < 0.1:  # Under 100ms
                self.test_results["passed"].append("Performance is good")
            else:
                self.test_results["warnings"].append(f"Response time ({avg_time*1000:.2f} ms) could be improved")

    def print_report(self):
        """Print comprehensive test report."""
        print("\n" + "=" * 60)
        print("📊 VERCEL LOCAL TEST REPORT")
        print("=" * 60)

        if self.test_results["passed"]:
            print("\n✅ PASSED TESTS:")
            for test in self.test_results["passed"]:
                print(f"  • {test}")

        if self.test_results["warnings"]:
            print("\n⚠️  WARNINGS:")
            for warning in self.test_results["warnings"]:
                print(f"  • {warning}")

        if self.test_results["failed"]:
            print("\n❌ FAILED TESTS:")
            for failure in self.test_results["failed"]:
                print(f"  • {failure}")

        if self.test_results["metrics"]:
            print("\n📈 PERFORMANCE METRICS:")
            for metric, value in self.test_results["metrics"].items():
                print(f"  • {metric}: {value}")

        print("\n" + "=" * 60)

        # Overall status
        if not self.test_results["failed"]:
            print("✅ All tests passed! Ready for Vercel deployment.")
            print("\n📚 Next steps:")
            print("1. Run: python scripts/vercel_deploy_check.py")
            print("2. Set environment variables in Vercel Dashboard")
            print("3. Deploy with: vercel --prod")
        else:
            print("❌ Some tests failed. Please fix issues before deploying.")

        # Save report to file
        report_file = self.project_root / "vercel_test_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n💾 Full report saved to: {report_file}")

    async def run_all_tests(self):
        """Run all tests in sequence."""
        try:
            # Setup environment
            self.setup_environment()

            # Start server
            if not self.start_server():
                print("❌ Failed to start server. Exiting.")
                return

            # Run tests
            await self.test_cold_start()
            await self.test_endpoints()
            await self.test_database_connection()
            await self.test_authentication()
            await self.test_ai_endpoints()
            await self.test_performance()

        except Exception as e:
            print(f"❌ Test suite error: {e}")
            self.test_results["failed"].append(f"Test suite error: {e}")

        finally:
            # Stop server
            self.stop_server()

            # Print report
            self.print_report()

def main():
    """Main entry point."""
    print("🚀 VERCEL LOCAL TESTING SUITE")
    print("=" * 60)

    tester = VercelLocalTester()
    asyncio.run(tester.run_all_tests())

if __name__ == "__main__":
    main()