#!/usr/bin/env python3
"""
API Route Analysis and Debugging Tool for ruleIQ

Analyzes the current API routes, identifies missing endpoints,
and provides debugging information for frontend API integration issues.
"""

import sys
import json
import asyncio
import requests
import time
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

# Add the project root to path
sys.path.insert(0, str(Path(__file__).parent))

@dataclass
class APIEndpoint:
    """Represents an API endpoint"""
    path: str
    method: str
    router: str
    exists: bool
    status_code: Optional[int] = None
    response_time_ms: Optional[float] = None
    error: Optional[str] = None

@dataclass
class APIAnalysisResult:
    """Results of API analysis"""
    total_endpoints: int
    working_endpoints: int
    missing_endpoints: int
    error_endpoints: int
    endpoints: List[APIEndpoint]
    router_mapping: Dict[str, List[str]]
    issues_found: List[str]
    recommendations: List[str]

class APIRouteAnalyzer:
    """Analyzes API routes and tests connectivity"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.expected_endpoints = self._get_expected_endpoints()
        self.actual_routes = {}

    def _get_expected_endpoints(self) -> List[Dict[str, str]]:
        """Get list of expected endpoints based on test file analysis"""
        return [
            # Auth endpoints
            {"path": "/api/v1/auth/register", "method": "POST", "router": "auth"},
            {"path": "/api/v1/auth/login", "method": "POST", "router": "auth"},
            {"path": "/api/v1/auth/me", "method": "GET", "router": "auth"},
            {"path": "/api/v1/auth/refresh", "method": "POST", "router": "auth"},

            # Assessment endpoints
            {"path": "/api/v1/assessments", "method": "GET", "router": "assessments"},
            {"path": "/api/v1/assessments", "method": "POST", "router": "assessments"},
            {"path": "/api/v1/assessments/readiness", "method": "GET", "router": "assessments"},

            # Business profiles
            {"path": "/api/v1/business-profiles", "method": "GET", "router": "business_profiles"},
            {"path": "/api/v1/business-profiles", "method": "POST", "router": "business_profiles"},

            # Framework endpoints
            {"path": "/api/v1/frameworks", "method": "GET", "router": "frameworks"},

            # Policy endpoints
            {"path": "/api/v1/policies", "method": "GET", "router": "policies"},
            {"path": "/api/v1/policies/generate", "method": "POST", "router": "policies"},

            # AI endpoints (these seem to be incorrectly mapped in tests)
            {"path": "/api/v1/ai/assessments", "method": "POST", "router": "ai_assessments"},
            {"path": "/api/v1/ai/health", "method": "GET", "router": "ai_assessments"},
            {"path": "/api/v1/ai/policies/generate", "method": "POST", "router": "ai_policy"},
            {"path": "/api/v1/ai/policies/templates", "method": "GET", "router": "ai_policy"},
            {"path": "/api/v1/ai/costs", "method": "GET", "router": "ai_cost_monitoring"},

            # Chat endpoints
            {"path": "/api/v1/chat/messages", "method": "POST", "router": "chat"},

            # Compliance endpoints
            {"path": "/api/v1/compliance/status", "method": "GET", "router": "compliance"},
            {"path": "/api/v1/compliance/score", "method": "GET", "router": "compliance"},
            {"path": "/api/v1/compliance/check", "method": "POST", "router": "compliance"},

            # Monitoring endpoints
            {"path": "/api/v1/monitoring/health", "method": "GET", "router": "monitoring"},
            {"path": "/api/v1/monitoring/metrics", "method": "GET", "router": "monitoring"},

            # Integration endpoints
            {"path": "/api/v1/integrations", "method": "GET", "router": "integrations"},

            # Report endpoints
            {"path": "/api/v1/reporting/reports", "method": "GET", "router": "reporting"},
        ]

    async def analyze_routes(self) -> APIAnalysisResult:
        """Analyze all API routes and test connectivity"""
        print("🔍 Starting comprehensive API route analysis...")

        endpoints = []
        router_mapping = {}
        issues_found = []
        recommendations = []

        # Test basic connectivity first
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code != 200:
                issues_found.append(f"Health endpoint failed: {response.status_code}")
            else:
                print("✅ Basic connectivity confirmed")
        except Exception as e:
            issues_found.append(f"Cannot connect to backend: {str(e)}")
            print(f"❌ Backend connection failed: {e}")
            return APIAnalysisResult(0, 0, 0, 1, [], {}, issues_found, recommendations)

        # Get OpenAPI schema to see actual routes
        try:
            response = requests.get(f"{self.base_url}/api/v1/openapi.json", timeout=5)
            if response.status_code == 200:
                openapi_data = response.json()
                actual_paths = set(openapi_data.get("paths", {}).keys())
                print(f"📋 Found {len(actual_paths)} documented API paths")
            else:
                actual_paths = set()
                issues_found.append("OpenAPI documentation not available")
        except Exception as e:
            actual_paths = set()
            issues_found.append(f"Failed to fetch OpenAPI spec: {str(e)}")

        # Test each expected endpoint
        for endpoint_info in self.expected_endpoints:
            path = endpoint_info["path"]
            method = endpoint_info["method"]
            router = endpoint_info["router"]

            # Track router mapping
            if router not in router_mapping:
                router_mapping[router] = []
            router_mapping[router].append(f"{method} {path}")

            # Test the endpoint
            endpoint_result = await self._test_endpoint(path, method, router)
            endpoints.append(endpoint_result)

            if not endpoint_result.exists:
                print(f"❌ {method} {path} - Not found (router: {router})")
            elif endpoint_result.error:
                print(f"⚠️ {method} {path} - Error: {endpoint_result.error}")
            else:
                print(f"✅ {method} {path} - Working ({endpoint_result.response_time_ms:.0f}ms)")

        # Analyze results
        working_endpoints = len([e for e in endpoints if e.exists and not e.error])
        missing_endpoints = len([e for e in endpoints if not e.exists])
        error_endpoints = len([e for e in endpoints if e.exists and e.error])

        # Generate issues and recommendations
        issues_found.extend(self._identify_issues(endpoints, actual_paths))
        recommendations.extend(self._generate_recommendations(endpoints, router_mapping))

        return APIAnalysisResult(
            total_endpoints=len(endpoints),
            working_endpoints=working_endpoints,
            missing_endpoints=missing_endpoints,
            error_endpoints=error_endpoints,
            endpoints=endpoints,
            router_mapping=router_mapping,
            issues_found=issues_found,
            recommendations=recommendations
        )

    async def _test_endpoint(self, path: str, method: str, router: str) -> APIEndpoint:
        """Test a specific endpoint"""
        url = f"{self.base_url}{path}"
        start_time = time.perf_counter()

        try:
            # For testing, we'll use GET for all or minimal POST data
            if method == "GET":
                response = requests.get(url, timeout=5)
            elif method == "POST":
                # Use minimal test data
                test_data = self._get_test_data_for_endpoint(path)
                response = requests.post(url, json=test_data, timeout=5)
            else:
                # Skip other methods for now
                return APIEndpoint(path, method, router, False, error="Method not tested")

            response_time_ms = (time.perf_counter() - start_time) * 1000

            # Consider 2xx, 4xx as "exists" (server responded)
            # Only 404 and connection errors mean "doesn't exist"
            if response.status_code == 404:
                return APIEndpoint(path, method, router, False, response.status_code, response_time_ms)

            exists = True
            error = None
            if response.status_code >= 500:
                error = f"Server error: {response.status_code}"
            elif response.status_code >= 400 and response.status_code != 404:
                # Client errors (except 404) still mean the endpoint exists
                error = f"Client error: {response.status_code}"

            return APIEndpoint(path, method, router, exists, response.status_code, response_time_ms, error)

        except requests.exceptions.ConnectTimeout:
            return APIEndpoint(path, method, router, False, error="Connection timeout")
        except requests.exceptions.ConnectionError:
            return APIEndpoint(path, method, router, False, error="Connection failed")
        except Exception as e:
            return APIEndpoint(path, method, router, False, error=str(e))

    def _get_test_data_for_endpoint(self, path: str) -> Dict[str, Any]:
        """Get minimal test data for POST endpoints"""
        test_data_map = {
            "/api/v1/auth/register": {
                "email": "test@example.com",
                "password": "testpass123"
            },
            "/api/v1/auth/login": {
                "email": "test@example.com",
                "password": "testpass123"
            },
            "/api/v1/assessments": {
                "assessment_type": "compliance_readiness",
                "company_name": "Test Company"
            },
            "/api/v1/business-profiles": {
                "company_name": "Test Company",
                "industry": "Technology"
            },
            "/api/v1/policies/generate": {
                "policy_type": "privacy_policy",
                "company_name": "Test Company"
            },
            "/api/v1/ai/assessments": {
                "assessment_type": "compliance_check",
                "context": "test"
            },
            "/api/v1/ai/policies/generate": {
                "policy_type": "privacy_policy",
                "company_info": {"name": "Test Company"}
            },
            "/api/v1/chat/messages": {
                "message": "Hello, test message"
            },
            "/api/v1/compliance/check": {
                "framework_id": "gdpr"
            }
        }

        return test_data_map.get(path, {})

    def _identify_issues(self, endpoints: List[APIEndpoint], actual_paths: set) -> List[str]:
        """Identify issues with API endpoints"""
        issues = []

        # Check for missing endpoints
        missing_endpoints = [e for e in endpoints if not e.exists]
        if missing_endpoints:
            issues.append(f"Found {len(missing_endpoints)} missing endpoints")

            # Check if it's a routing issue
            for endpoint in missing_endpoints:
                # Check if similar paths exist
                similar_paths = [p for p in actual_paths if endpoint.path.split('/')[-1] in p]
                if similar_paths:
                    issues.append(f"Endpoint {endpoint.path} not found, but similar paths exist: {similar_paths}")

        # Check for error endpoints
        error_endpoints = [e for e in endpoints if e.exists and e.error and "Server error" in e.error]
        if error_endpoints:
            issues.append(f"Found {len(error_endpoints)} endpoints with server errors")

        # Check for slow endpoints
        slow_endpoints = [e for e in endpoints if e.response_time_ms and e.response_time_ms > 2000]
        if slow_endpoints:
            issues.append(f"Found {len(slow_endpoints)} slow endpoints (>2s response time)")

        # Check specific routing mismatches
        ai_endpoints = [e for e in endpoints if "/api/v1/ai/" in e.path and not e.exists]
        if ai_endpoints:
            issues.append("AI endpoints using '/api/v1/ai/' prefix are not found - likely mounted at '/api/v1/ai-*' instead")

        return issues

    def _generate_recommendations(self, endpoints: List[APIEndpoint], router_mapping: Dict[str, List[str]]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        # Check for routing issues
        missing_endpoints = [e for e in endpoints if not e.exists]
        if missing_endpoints:
            recommendations.append("Check api/main.py router mounting - some endpoints may be mounted with different prefixes")

            # Specific AI endpoint recommendations
            ai_missing = [e for e in missing_endpoints if "/api/v1/ai/" in e.path]
            if ai_missing:
                recommendations.append("AI endpoints: Update frontend to use '/api/v1/ai-assessments' instead of '/api/v1/ai-assessments'")
                recommendations.append("AI endpoints: Update frontend to use appropriate AI router prefixes as defined in main.py")

        # Check for authentication issues
        auth_errors = [e for e in endpoints if e.exists and e.error and ("401" in e.error or "403" in e.error)]
        if auth_errors:
            recommendations.append("Some endpoints require authentication - ensure test suite includes valid JWT tokens")

        # Check for validation issues
        validation_errors = [e for e in endpoints if e.exists and e.error and "422" in e.error]
        if validation_errors:
            recommendations.append("Some endpoints have validation errors - check request schemas and required fields")
            recommendations.append("Consider adding Pydantic model validation to ensure proper request format")

        # Performance recommendations
        slow_endpoints = [e for e in endpoints if e.response_time_ms and e.response_time_ms > 1000]
        if slow_endpoints:
            recommendations.append("Consider adding caching or database query optimization for slow endpoints")

        # Router organization recommendations
        if len(router_mapping) > 15:
            recommendations.append("Consider consolidating related routers to reduce complexity")

        return recommendations

def print_analysis_report(result: APIAnalysisResult):
    """Print a comprehensive analysis report"""
    print("\n" + "="*80)
    print("🚀 ruleIQ API ROUTE ANALYSIS REPORT")
    print("="*80)

    # Summary
    print("\n📊 SUMMARY:")
    print(f"   Total endpoints tested: {result.total_endpoints}")
    print(f"   ✅ Working endpoints: {result.working_endpoints}")
    print(f"   ❌ Missing endpoints: {result.missing_endpoints}")
    print(f"   ⚠️  Error endpoints: {result.error_endpoints}")

    # Success rate
    if result.total_endpoints > 0:
        success_rate = (result.working_endpoints / result.total_endpoints) * 100
        print(f"   📈 Success rate: {success_rate:.1f}%")

    # Router breakdown
    print("\n🗂️  ROUTER BREAKDOWN:")
    for router, endpoints in result.router_mapping.items():
        working_count = len([e for e in result.endpoints if e.router == router and e.exists and not e.error])
        total_count = len([e for e in result.endpoints if e.router == router])
        print(f"   {router}: {working_count}/{total_count} working")

    # Issues found
    if result.issues_found:
        print("\n🚨 ISSUES FOUND:")
        for i, issue in enumerate(result.issues_found, 1):
            print(f"   {i}. {issue}")

    # Recommendations
    if result.recommendations:
        print("\n💡 RECOMMENDATIONS:")
        for i, rec in enumerate(result.recommendations, 1):
            print(f"   {i}. {rec}")

    # Detailed endpoint status
    print("\n📋 DETAILED ENDPOINT STATUS:")

    # Group by status
    working = [e for e in result.endpoints if e.exists and not e.error]
    missing = [e for e in result.endpoints if not e.exists]
    errors = [e for e in result.endpoints if e.exists and e.error]

    if working:
        print(f"\n✅ WORKING ENDPOINTS ({len(working)}):")
        for endpoint in working:
            response_time = f" ({endpoint.response_time_ms:.0f}ms)" if endpoint.response_time_ms else ""
            print(f"   {endpoint.method} {endpoint.path}{response_time}")

    if missing:
        print(f"\n❌ MISSING ENDPOINTS ({len(missing)}):")
        for endpoint in missing:
            print(f"   {endpoint.method} {endpoint.path} (router: {endpoint.router})")

    if errors:
        print(f"\n⚠️  ERROR ENDPOINTS ({len(errors)}):")
        for endpoint in errors:
            print(f"   {endpoint.method} {endpoint.path} - {endpoint.error}")

    print("\n" + "="*80)

async def main():
    """Main analysis function"""
    print("🔧 ruleIQ API Route Analyzer")
    print("Analyzing API endpoints and identifying issues...")

    analyzer = APIRouteAnalyzer()
    result = await analyzer.analyze_routes()

    print_analysis_report(result)

    # Save results to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"api_analysis_{timestamp}.json"

    # Convert result to dict for JSON serialization
    result_dict = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_endpoints": result.total_endpoints,
            "working_endpoints": result.working_endpoints,
            "missing_endpoints": result.missing_endpoints,
            "error_endpoints": result.error_endpoints
        },
        "endpoints": [
            {
                "path": e.path,
                "method": e.method,
                "router": e.router,
                "exists": e.exists,
                "status_code": e.status_code,
                "response_time_ms": e.response_time_ms,
                "error": e.error
            }
            for e in result.endpoints
        ],
        "router_mapping": result.router_mapping,
        "issues_found": result.issues_found,
        "recommendations": result.recommendations
    }

    try:
        with open(filename, 'w') as f:
            json.dump(result_dict, f, indent=2)
        print(f"\n💾 Analysis results saved to {filename}")
    except Exception as e:
        print(f"\n⚠️  Could not save results: {e}")

if __name__ == "__main__":
    asyncio.run(main())
