#!/usr/bin/env python3
"""
Comprehensive startup test script for ruleIQ application.
Tests import validation, database connections, router functionality, and API endpoints.
"""

import sys
import asyncio
import time
from typing import Dict, List, Tuple, Optional
import httpx
import json
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Terminal colors for output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title: str):
    """Print a formatted section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")

def print_test_result(test_name: str, passed: bool, details: str = ""):
    """Print a formatted test result."""
    status = f"{Colors.GREEN}✅ PASSED{Colors.END}" if passed else f"{Colors.RED}❌ FAILED{Colors.END}"
    print(f"  {test_name:.<50} {status}")
    if details and not passed:
        print(f"    {Colors.YELLOW}→ {details}{Colors.END}")

class StartupTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.results = {"passed": 0, "failed": 0, "warnings": 0}
        self.issues = []
        
    async def test_imports(self) -> bool:
        """Test that all critical modules can be imported."""
        print_header("IMPORT VALIDATION")
        all_passed = True
        
        critical_imports = [
            ("FastAPI", "from fastapi import FastAPI"),
            ("Pydantic", "from pydantic import BaseModel"),
            ("SQLAlchemy", "from sqlalchemy import create_engine"),
            ("Database Models", "from database.models import User, BusinessProfile"),
            ("API Schemas", "from api.schemas.models import AssessmentSessionCreate"),
            ("Main App", "from main import app"),
            ("Settings", "from config.settings import settings"),
            ("Database Setup", "from database.db_setup import init_db"),
        ]
        
        for name, import_statement in critical_imports:
            try:
                exec(import_statement)
                print_test_result(f"Import {name}", True)
                self.results["passed"] += 1
            except Exception as e:
                print_test_result(f"Import {name}", False, str(e))
                self.results["failed"] += 1
                all_passed = False
                self.issues.append(f"Import failed: {name} - {str(e)}")
        
        return all_passed
    
    async def test_database_connections(self) -> bool:
        """Test database connections."""
        print_header("DATABASE CONNECTION TESTS")
        all_passed = True
        
        # Test PostgreSQL
        try:
            from database.db_setup import get_db, async_get_db
            from database.session import SessionLocal
            
            # Test sync connection
            db = SessionLocal()
            db.execute("SELECT 1")
            db.close()
            print_test_result("PostgreSQL Sync Connection", True)
            self.results["passed"] += 1
            
            # Test async connection
            async with async_get_db() as db:
                await db.execute("SELECT 1")
            print_test_result("PostgreSQL Async Connection", True)
            self.results["passed"] += 1
        except Exception as e:
            print_test_result("PostgreSQL Connection", False, str(e))
            self.results["failed"] += 1
            all_passed = False
            self.issues.append(f"PostgreSQL connection failed: {str(e)}")
        
        # Test Redis
        try:
            from database.redis_client import redis_client
            await redis_client.ping()
            print_test_result("Redis Connection", True)
            self.results["passed"] += 1
        except Exception as e:
            print_test_result("Redis Connection", False, str(e))
            self.results["failed"] += 1
            all_passed = False
            self.issues.append(f"Redis connection failed: {str(e)}")
        
        # Test Neo4j
        try:
            from services.neo4j_service import neo4j_service
            if neo4j_service and neo4j_service.driver:
                with neo4j_service.driver.session() as session:
                    result = session.run("RETURN 1 as num")
                    result.single()
                print_test_result("Neo4j Connection", True)
                self.results["passed"] += 1
            else:
                print_test_result("Neo4j Connection", False, "Service not initialized")
                self.results["warnings"] += 1
        except Exception as e:
            print_test_result("Neo4j Connection", False, str(e))
            self.results["warnings"] += 1
        
        return all_passed
    
    async def test_application_startup(self) -> bool:
        """Test that the FastAPI application starts correctly."""
        print_header("APPLICATION STARTUP TEST")
        
        try:
            # Import the app
            from main import app
            from config.settings import settings
            
            print_test_result("FastAPI App Import", True)
            self.results["passed"] += 1
            
            # Check app configuration
            if app.title == "ruleIQ API":
                print_test_result("App Title Configuration", True)
                self.results["passed"] += 1
            else:
                print_test_result("App Title Configuration", False, f"Title is {app.title}")
                self.results["failed"] += 1
            
            # Check routers are included
            routes = [route.path for route in app.routes]
            expected_prefixes = ["/api/v1/auth", "/api/v1/assessments", "/api/v1/business-profiles"]
            
            for prefix in expected_prefixes:
                found = any(route.startswith(prefix) for route in routes)
                if found:
                    print_test_result(f"Router {prefix}", True)
                    self.results["passed"] += 1
                else:
                    print_test_result(f"Router {prefix}", False, "Not found in routes")
                    self.results["failed"] += 1
                    self.issues.append(f"Router not found: {prefix}")
            
            return True
        except Exception as e:
            print_test_result("Application Startup", False, str(e))
            self.results["failed"] += 1
            self.issues.append(f"Application startup failed: {str(e)}")
            return False
    
    async def test_health_endpoints(self) -> bool:
        """Test health check endpoints."""
        print_header("HEALTH ENDPOINT TESTS")
        all_passed = True
        
        health_endpoints = [
            "/health",
            "/api/v1/health",
            "/api/v1/health/detailed"
        ]
        
        async with httpx.AsyncClient() as client:
            for endpoint in health_endpoints:
                try:
                    response = await client.get(f"{self.base_url}{endpoint}")
                    if response.status_code == 200:
                        print_test_result(f"Health Check {endpoint}", True)
                        self.results["passed"] += 1
                    else:
                        print_test_result(f"Health Check {endpoint}", False, f"Status {response.status_code}")
                        self.results["failed"] += 1
                        all_passed = False
                except Exception as e:
                    print_test_result(f"Health Check {endpoint}", False, str(e))
                    self.results["failed"] += 1
                    all_passed = False
                    self.issues.append(f"Health endpoint failed: {endpoint}")
        
        return all_passed
    
    async def test_api_documentation(self) -> bool:
        """Test API documentation endpoints."""
        print_header("API DOCUMENTATION TESTS")
        all_passed = True
        
        doc_endpoints = [
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
        
        async with httpx.AsyncClient() as client:
            for endpoint in doc_endpoints:
                try:
                    response = await client.get(f"{self.base_url}{endpoint}")
                    if response.status_code == 200:
                        print_test_result(f"Documentation {endpoint}", True)
                        self.results["passed"] += 1
                        
                        # For OpenAPI, check schema validity
                        if endpoint == "/openapi.json":
                            schema = response.json()
                            if "paths" in schema and len(schema["paths"]) > 0:
                                print_test_result(f"  → Schema contains {len(schema['paths'])} paths", True)
                            else:
                                print_test_result("  → Schema validation", False, "No paths found")
                                all_passed = False
                    else:
                        print_test_result(f"Documentation {endpoint}", False, f"Status {response.status_code}")
                        self.results["failed"] += 1
                        all_passed = False
                except Exception as e:
                    print_test_result(f"Documentation {endpoint}", False, str(e))
                    self.results["failed"] += 1
                    all_passed = False
                    self.issues.append(f"Documentation endpoint failed: {endpoint}")
        
        return all_passed
    
    async def test_critical_endpoints(self) -> bool:
        """Test critical API endpoints."""
        print_header("CRITICAL ENDPOINT TESTS")
        all_passed = True
        
        # Test endpoints that should be accessible without auth
        public_endpoints = [
            ("/api/v1/auth/register", "POST"),
            ("/api/v1/auth/login", "POST"),
            ("/api/v1/freemium/quick-assessment", "POST"),
        ]
        
        async with httpx.AsyncClient() as client:
            for endpoint, method in public_endpoints:
                try:
                    if method == "GET":
                        response = await client.get(f"{self.base_url}{endpoint}")
                    else:
                        # Send minimal valid payload
                        response = await client.post(
                            f"{self.base_url}{endpoint}",
                            json={"test": "data"}
                        )
                    
                    # We expect 400/422 for invalid data, but not 404 or 500
                    if response.status_code in [200, 400, 422]:
                        print_test_result(f"{method} {endpoint}", True)
                        self.results["passed"] += 1
                    else:
                        print_test_result(f"{method} {endpoint}", False, f"Status {response.status_code}")
                        self.results["failed"] += 1
                        all_passed = False
                        if response.status_code >= 500:
                            self.issues.append(f"Server error on {endpoint}: {response.status_code}")
                except Exception as e:
                    print_test_result(f"{method} {endpoint}", False, str(e))
                    self.results["failed"] += 1
                    all_passed = False
                    self.issues.append(f"Endpoint failed: {endpoint}")
        
        return all_passed
    
    def print_summary(self):
        """Print test summary."""
        print_header("TEST SUMMARY")
        
        total = self.results["passed"] + self.results["failed"]
        pass_rate = (self.results["passed"] / total * 100) if total > 0 else 0
        
        print(f"{Colors.BOLD}Results:{Colors.END}")
        print(f"  {Colors.GREEN}Passed: {self.results['passed']}{Colors.END}")
        print(f"  {Colors.RED}Failed: {self.results['failed']}{Colors.END}")
        print(f"  {Colors.YELLOW}Warnings: {self.results['warnings']}{Colors.END}")
        print(f"  {Colors.BOLD}Pass Rate: {pass_rate:.1f}%{Colors.END}")
        
        if self.issues:
            print(f"\n{Colors.BOLD}{Colors.RED}Issues Found:{Colors.END}")
            for issue in self.issues:
                print(f"  • {issue}")
        
        if pass_rate >= 90:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ Application is ready for deployment!{Colors.END}")
        elif pass_rate >= 70:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️ Application has some issues but may be deployable.{Colors.END}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ Application has critical issues that need to be fixed.{Colors.END}")
        
        return pass_rate >= 90

async def main():
    """Run all startup tests."""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║          ruleIQ Application Startup Test Suite          ║")
    print("║                    Validating All Systems                ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    tester = StartupTester()
    
    # Run tests
    await tester.test_imports()
    await tester.test_database_connections()
    await tester.test_application_startup()
    
    # Test running application endpoints (if server is running)
    print(f"\n{Colors.YELLOW}Testing live endpoints (requires server running)...{Colors.END}")
    try:
        await tester.test_health_endpoints()
        await tester.test_api_documentation()
        await tester.test_critical_endpoints()
    except httpx.ConnectError:
        print(f"{Colors.YELLOW}  → Server not running. Start with: doppler run -- python main.py{Colors.END}")
        tester.results["warnings"] += 1
    
    # Print summary
    success = tester.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())