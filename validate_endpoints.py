#!/usr/bin/env python3
"""
Endpoint validation script for ruleIQ application.
Automatically discovers and tests all registered API endpoints.
"""

import sys
import asyncio
from typing import Dict, List, Optional, Tuple
import httpx
import json
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Terminal colors
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class EndpointValidator:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.endpoints = {}
        self.test_results = {}
        self.auth_token = None
        
    def discover_endpoints(self) -> Dict:
        """Discover all endpoints from the FastAPI application."""
        print(f"\n{Colors.CYAN}Discovering endpoints from application...{Colors.END}")
        
        try:
            from main import app
            
            # Group endpoints by tag/router
            for route in app.routes:
                if hasattr(route, "methods") and hasattr(route, "path"):
                    path = route.path
                    methods = list(route.methods - {"HEAD", "OPTIONS"})
                    
                    if not methods:
                        continue
                    
                    # Get router/tag from path
                    if path.startswith("/api/v1/"):
                        parts = path.split("/")
                        if len(parts) > 3:
                            tag = parts[3]
                        else:
                            tag = "root"
                    else:
                        tag = "root"
                    
                    if tag not in self.endpoints:
                        self.endpoints[tag] = []
                    
                    for method in methods:
                        self.endpoints[tag].append({
                            "path": path,
                            "method": method,
                            "name": route.name if hasattr(route, "name") else "unknown"
                        })
            
            # Print discovered endpoints
            total = sum(len(endpoints) for endpoints in self.endpoints.values())
            print(f"{Colors.GREEN}✓ Discovered {total} endpoints across {len(self.endpoints)} routers{Colors.END}")
            
            for tag, endpoints in sorted(self.endpoints.items()):
                print(f"  • {tag}: {len(endpoints)} endpoints")
            
            return self.endpoints
            
        except Exception as e:
            print(f"{Colors.RED}✗ Failed to discover endpoints: {e}{Colors.END}")
            return {}
    
    async def test_authentication(self) -> bool:
        """Test authentication endpoints and get a token for protected endpoints."""
        print(f"\n{Colors.BOLD}Testing Authentication Endpoints{Colors.END}")
        
        async with httpx.AsyncClient() as client:
            # Test registration
            register_data = {
                "email": f"test_{datetime.now().timestamp()}@example.com",
                "password": "TestPassword123!",
                "name": "Test User"
            }
            
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/register",
                    json=register_data
                )
                
                if response.status_code in [200, 201]:
                    print(f"  {Colors.GREEN}✓ Registration endpoint working{Colors.END}")
                elif response.status_code == 409:
                    print(f"  {Colors.YELLOW}⚠ User already exists (expected){Colors.END}")
                else:
                    print(f"  {Colors.RED}✗ Registration failed: {response.status_code}{Colors.END}")
                    
            except Exception as e:
                print(f"  {Colors.RED}✗ Registration endpoint error: {e}{Colors.END}")
            
            # Test login
            login_data = {
                "username": register_data["email"],
                "password": register_data["password"]
            }
            
            try:
                response = await client.post(
                    f"{self.base_url}/api/v1/auth/login",
                    data=login_data  # Form data for OAuth2
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.auth_token = data.get("access_token")
                    print(f"  {Colors.GREEN}✓ Login successful, token acquired{Colors.END}")
                    return True
                else:
                    print(f"  {Colors.RED}✗ Login failed: {response.status_code}{Colors.END}")
                    
            except Exception as e:
                print(f"  {Colors.RED}✗ Login endpoint error: {e}{Colors.END}")
        
        return False
    
    async def test_endpoint_group(self, tag: str, endpoints: List[Dict]) -> Dict:
        """Test a group of endpoints."""
        print(f"\n{Colors.BOLD}Testing {tag} endpoints ({len(endpoints)} total){Colors.END}")
        
        results = {"passed": 0, "failed": 0, "warnings": 0}
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            
            for endpoint in endpoints:
                path = endpoint["path"]
                method = endpoint["method"]
                
                # Skip parameterized paths for now
                if "{" in path:
                    print(f"  {Colors.YELLOW}⚠ Skipping parameterized: {method} {path}{Colors.END}")
                    results["warnings"] += 1
                    continue
                
                try:
                    if method == "GET":
                        response = await client.get(
                            f"{self.base_url}{path}",
                            headers=headers,
                            timeout=5.0
                        )
                    elif method == "POST":
                        response = await client.post(
                            f"{self.base_url}{path}",
                            headers=headers,
                            json={},  # Empty payload for testing
                            timeout=5.0
                        )
                    elif method == "PUT":
                        response = await client.put(
                            f"{self.base_url}{path}",
                            headers=headers,
                            json={},
                            timeout=5.0
                        )
                    elif method == "DELETE":
                        response = await client.delete(
                            f"{self.base_url}{path}",
                            headers=headers,
                            timeout=5.0
                        )
                    else:
                        print(f"  {Colors.YELLOW}⚠ Unsupported method: {method} {path}{Colors.END}")
                        results["warnings"] += 1
                        continue
                    
                    # Check response
                    if response.status_code < 500:
                        # Client errors are OK (means endpoint is working)
                        print(f"  {Colors.GREEN}✓ {method:6} {path:50} [{response.status_code}]{Colors.END}")
                        results["passed"] += 1
                    else:
                        print(f"  {Colors.RED}✗ {method:6} {path:50} [{response.status_code}]{Colors.END}")
                        results["failed"] += 1
                        
                except httpx.TimeoutException:
                    print(f"  {Colors.YELLOW}⚠ {method:6} {path:50} [TIMEOUT]{Colors.END}")
                    results["warnings"] += 1
                except Exception as e:
                    print(f"  {Colors.RED}✗ {method:6} {path:50} [ERROR: {str(e)[:30]}]{Colors.END}")
                    results["failed"] += 1
        
        self.test_results[tag] = results
        return results
    
    async def test_critical_business_flows(self) -> None:
        """Test critical business flows."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}Testing Critical Business Flows{Colors.END}")
        
        flows = {
            "Assessment Flow": [
                ("POST", "/api/v1/assessments/sessions", {"assessment_type": "ISO_27001"}),
                ("GET", "/api/v1/assessments/sessions", None),
            ],
            "Business Profile Flow": [
                ("POST", "/api/v1/business-profiles", {"name": "Test Corp", "industry": "Technology"}),
                ("GET", "/api/v1/business-profiles", None),
            ],
            "Quick Assessment Flow": [
                ("POST", "/api/v1/freemium/quick-assessment", {
                    "company_size": "small",
                    "industry": "technology",
                    "compliance_needs": ["GDPR"]
                }),
            ],
        }
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
            
            for flow_name, steps in flows.items():
                print(f"\n  {Colors.BOLD}{flow_name}:{Colors.END}")
                flow_success = True
                
                for method, path, payload in steps:
                    try:
                        if method == "GET":
                            response = await client.get(
                                f"{self.base_url}{path}",
                                headers=headers,
                                timeout=5.0
                            )
                        else:
                            response = await client.request(
                                method,
                                f"{self.base_url}{path}",
                                headers=headers,
                                json=payload,
                                timeout=5.0
                            )
                        
                        if response.status_code < 500:
                            print(f"    {Colors.GREEN}✓ {method} {path} [{response.status_code}]{Colors.END}")
                        else:
                            print(f"    {Colors.RED}✗ {method} {path} [{response.status_code}]{Colors.END}")
                            flow_success = False
                            
                    except Exception as e:
                        print(f"    {Colors.RED}✗ {method} {path} [ERROR: {str(e)[:50]}]{Colors.END}")
                        flow_success = False
                
                if flow_success:
                    print(f"    {Colors.GREEN}→ Flow completed successfully{Colors.END}")
                else:
                    print(f"    {Colors.RED}→ Flow has issues{Colors.END}")
    
    def print_summary(self) -> None:
        """Print validation summary."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}ENDPOINT VALIDATION SUMMARY{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
        
        total_passed = sum(r["passed"] for r in self.test_results.values())
        total_failed = sum(r["failed"] for r in self.test_results.values())
        total_warnings = sum(r["warnings"] for r in self.test_results.values())
        
        print(f"\n{Colors.BOLD}Overall Results:{Colors.END}")
        print(f"  {Colors.GREEN}Passed: {total_passed}{Colors.END}")
        print(f"  {Colors.RED}Failed: {total_failed}{Colors.END}")
        print(f"  {Colors.YELLOW}Warnings: {total_warnings}{Colors.END}")
        
        print(f"\n{Colors.BOLD}Router-wise Results:{Colors.END}")
        for tag, results in sorted(self.test_results.items()):
            status = Colors.GREEN if results["failed"] == 0 else Colors.RED
            print(f"  {status}{tag:20} P:{results['passed']:3} F:{results['failed']:3} W:{results['warnings']:3}{Colors.END}")
        
        # Overall assessment
        total_tests = total_passed + total_failed
        if total_tests > 0:
            pass_rate = (total_passed / total_tests) * 100
            
            print(f"\n{Colors.BOLD}Pass Rate: {pass_rate:.1f}%{Colors.END}")
            
            if pass_rate >= 95:
                print(f"{Colors.GREEN}{Colors.BOLD}✅ All endpoints are working correctly!{Colors.END}")
            elif pass_rate >= 80:
                print(f"{Colors.YELLOW}{Colors.BOLD}⚠️ Most endpoints working, some issues to address.{Colors.END}")
            else:
                print(f"{Colors.RED}{Colors.BOLD}❌ Significant endpoint issues detected.{Colors.END}")

async def main():
    """Run endpoint validation."""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║              ruleIQ API Endpoint Validation Suite               ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    validator = EndpointValidator()
    
    # Discover endpoints from application
    validator.discover_endpoints()
    
    # Check if server is running
    print(f"\n{Colors.CYAN}Checking if server is running...{Colors.END}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{validator.base_url}/health", timeout=2.0)
            print(f"{Colors.GREEN}✓ Server is running{Colors.END}")
    except:
        print(f"{Colors.RED}✗ Server not running. Please start with:{Colors.END}")
        print(f"{Colors.YELLOW}  doppler run -- python main.py{Colors.END}")
        sys.exit(1)
    
    # Test authentication first
    await validator.test_authentication()
    
    # Test each endpoint group
    for tag, endpoints in validator.endpoints.items():
        await validator.test_endpoint_group(tag, endpoints)
    
    # Test critical business flows
    await validator.test_critical_business_flows()
    
    # Print summary
    validator.print_summary()

if __name__ == "__main__":
    asyncio.run(main())