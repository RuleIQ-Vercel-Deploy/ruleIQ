#!/usr/bin/env python3
"""
Comprehensive API Connection Test Script
Tests all 99+ API endpoints to ensure frontend-backend connectivity
"""

import asyncio
import httpx
from typing import Dict, List, Tuple
import json
from datetime import datetime

# Base URL for API
BASE_URL = "http://localhost:8000/api/v1"

# Test authentication token (you'll need to get a real one)
TEST_TOKEN = "your-test-token-here"

class APIConnectionTester:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {TEST_TOKEN}",
            "Content-Type": "application/json"
        }
        self.results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        
    async def test_endpoint(self, method: str, path: str, data: dict = None) -> Tuple[bool, str]:
        """Test a single endpoint"""
        url = f"{BASE_URL}/{path}"
        
        try:
            async with httpx.AsyncClient() as client:
                if method == "GET":
                    response = await client.get(url, headers=self.headers, timeout=5.0)
                elif method == "POST":
                    response = await client.post(url, headers=self.headers, json=data or {}, timeout=5.0)
                elif method == "PATCH":
                    response = await client.patch(url, headers=self.headers, json=data or {}, timeout=5.0)
                elif method == "PUT":
                    response = await client.put(url, headers=self.headers, json=data or {}, timeout=5.0)
                elif method == "DELETE":
                    response = await client.delete(url, headers=self.headers, timeout=5.0)
                else:
                    return False, f"Unknown method: {method}"
                
                # Check if response is successful (2xx) or expected auth error (401/403)
                if response.status_code < 300 or response.status_code in [401, 403]:
                    return True, f"Status: {response.status_code}"
                else:
                    return False, f"Status: {response.status_code}"
                    
        except httpx.ConnectError:
            return False, "Connection refused - is the server running?"
        except httpx.TimeoutException:
            return False, "Request timeout"
        except Exception as e:
            return False, str(e)
    
    async def run_all_tests(self):
        """Run tests for all endpoints"""
        
        # All endpoints organized by router
        endpoints = [
            # Evidence endpoints (9)
            ("GET", "evidence/"),
            ("GET", "evidence/test-id"),
            ("POST", "evidence/", {"name": "test", "file": "test.pdf"}),
            ("PATCH", "evidence/test-id", {"status": "verified"}),
            ("POST", "evidence/test-id/automation", {"schedule": "daily"}),
            ("GET", "evidence/dashboard/gdpr"),
            ("POST", "evidence/test-id/classify", {"classification": "critical"}),
            ("GET", "evidence/requirements/gdpr"),
            ("GET", "evidence/test-id/quality"),
            
            # Compliance endpoints (8)
            ("GET", "compliance/status/gdpr"),
            ("POST", "compliance/tasks", {"title": "test task"}),
            ("PATCH", "compliance/tasks/task-123", {"status": "completed"}),
            ("POST", "compliance/risks", {"title": "test risk"}),
            ("PATCH", "compliance/risks/risk-123", {"severity": "high"}),
            ("GET", "compliance/timeline"),
            ("GET", "compliance/dashboard"),
            ("POST", "compliance/certificate/generate", {"framework": "gdpr"}),
            
            # Policies endpoints (8)
            ("GET", "policies/"),
            ("GET", "policies/policy-123"),
            ("PATCH", "policies/policy-123/status", {"status": "approved"}),
            ("PUT", "policies/policy-123/approve"),
            ("POST", "policies/policy-123/regenerate-section", {"section": "intro"}),
            ("GET", "policies/templates"),
            ("POST", "policies/policy-123/clone", {"name": "cloned policy"}),
            ("GET", "policies/policy-123/versions"),
            
            # Frameworks endpoints (7)
            ("GET", "frameworks/"),
            ("GET", "frameworks/gdpr"),
            ("GET", "frameworks/gdpr/controls"),
            ("GET", "frameworks/gdpr/implementation-guide"),
            ("GET", "frameworks/gdpr/compliance-status"),
            ("POST", "frameworks/compare", {"frameworks": ["gdpr", "iso27001"]}),
            ("GET", "frameworks/gdpr/maturity-assessment"),
            
            # Integrations endpoints (7)
            ("GET", "integrations/"),
            ("GET", "integrations/connected"),
            ("POST", "integrations/google-workspace/test"),
            ("GET", "integrations/google-workspace/sync-history"),
            ("POST", "integrations/google-workspace/webhooks", {"url": "test"}),
            ("GET", "integrations/google-workspace/logs"),
            ("POST", "integrations/oauth/callback", {"code": "test"}),
            
            # Monitoring endpoints (7)
            ("GET", "monitoring/database/status"),
            ("PATCH", "monitoring/alerts/alert-123/resolve"),
            ("GET", "monitoring/metrics"),
            ("GET", "monitoring/api-performance"),
            ("GET", "monitoring/error-logs"),
            ("GET", "monitoring/health"),
            ("GET", "monitoring/audit-logs"),
            
            # Payment endpoints (7)
            ("POST", "payments/subscription/cancel"),
            ("POST", "payments/subscription/reactivate"),
            ("POST", "payments/payment-methods", {"method": "card"}),
            ("GET", "payments/invoices"),
            ("GET", "payments/invoices/upcoming"),
            ("POST", "payments/coupons/apply", {"code": "TEST"}),
            ("GET", "payments/subscription/limits"),
            
            # Assessments endpoints (6)
            ("GET", "assessments/"),
            ("GET", "assessments/assess-123"),
            ("POST", "assessments/", {"title": "test"}),
            ("PATCH", "assessments/assess-123", {"status": "in_progress"}),
            ("POST", "assessments/assess-123/complete"),
            ("GET", "assessments/assess-123/results"),
            
            # Readiness endpoints (6)
            ("GET", "readiness/biz-123"),
            ("GET", "readiness/gaps/biz-123"),
            ("POST", "readiness/roadmap", {"profile_id": "biz-123"}),
            ("POST", "readiness/quick-assessment", {"data": {}}),
            ("GET", "readiness/trends/biz-123"),
            ("GET", "readiness/benchmarks"),
            
            # Reports endpoints (6)
            ("GET", "reports/history"),
            ("GET", "reports/report-123"),
            ("POST", "reports/schedule", {"schedule": "weekly"}),
            ("GET", "reports/scheduled"),
            ("POST", "reports/preview", {"type": "compliance"}),
            ("GET", "reports/analytics"),
            
            # Business Profiles endpoints (5)
            ("GET", "business-profiles/"),
            ("GET", "business-profiles/biz-123"),
            ("POST", "business-profiles/", {"name": "test"}),
            ("PUT", "business-profiles/biz-123", {"name": "updated"}),
            ("GET", "business-profiles/biz-123/compliance"),
            
            # Dashboard endpoints (5)
            ("GET", "dashboard/"),
            ("GET", "dashboard/widgets"),
            ("GET", "dashboard/notifications"),
            ("GET", "dashboard/quick-actions"),
            ("GET", "dashboard/recommendations"),
            
            # Foundation Evidence endpoints (5)
            ("POST", "foundation/evidence/aws/configure", {"config": {}}),
            ("POST", "foundation/evidence/okta/configure", {"config": {}}),
            ("POST", "foundation/evidence/google/configure", {"config": {}}),
            ("POST", "foundation/evidence/microsoft/configure", {"config": {}}),
            ("GET", "foundation/evidence/health"),
            
            # AI Assessments endpoints (4)
            ("POST", "ai/self-review", {"data": {}}),
            ("POST", "ai/quick-confidence-check", {"responses": {}}),
            ("POST", "ai/assessments/followup", {"question": "test"}),
            ("GET", "ai/assessments/metrics"),
            
            # Chat endpoints (4)
            ("GET", "chat/conversations/conv-123"),
            ("POST", "chat/compliance-gap-analysis", {"framework": "gdpr"}),
            ("GET", "chat/smart-compliance-guidance"),
            ("DELETE", "chat/cache/clear?pattern=test"),
            
            # Implementation endpoints (4)
            ("GET", "implementation/plans/plan-123"),
            ("GET", "implementation/recommendations"),
            ("GET", "implementation/resources/gdpr"),
            ("GET", "implementation/plans/plan-123/analytics"),
            
            # Evidence Collection endpoints (1)
            ("GET", "evidence-collection/plans"),
        ]
        
        print(f"\n{'='*60}")
        print("API CONNECTION TEST - COMPREHENSIVE")
        print(f"{'='*60}")
        print(f"Testing {len(endpoints)} endpoints...")
        print(f"Base URL: {BASE_URL}")
        print(f"{'='*60}\n")
        
        # Test each endpoint
        for method, path, *data in endpoints:
            self.results["total"] += 1
            data_dict = data[0] if data else None
            
            success, message = await self.test_endpoint(method, path, data_dict)
            
            if success:
                self.results["passed"] += 1
                status = "✅ PASS"
            else:
                self.results["failed"] += 1
                status = "❌ FAIL"
                self.results["errors"].append({
                    "endpoint": f"{method} /{path}",
                    "error": message
                })
            
            # Clean path for display
            display_path = path.replace("test-id", "{id}").replace("123", "{id}")
            print(f"{status} {method:6} /{display_path:50} {message}")
        
        # Print summary
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Total Endpoints: {self.results['total']}")
        print(f"Passed: {self.results['passed']} ({self.results['passed']/self.results['total']*100:.1f}%)")
        print(f"Failed: {self.results['failed']} ({self.results['failed']/self.results['total']*100:.1f}%)")
        
        if self.results["errors"]:
            print(f"\n{'='*60}")
            print("FAILED ENDPOINTS")
            print(f"{'='*60}")
            for error in self.results["errors"][:10]:  # Show first 10 errors
                print(f"- {error['endpoint']}: {error['error']}")
            
            if len(self.results["errors"]) > 10:
                print(f"... and {len(self.results['errors']) - 10} more")
        
        # Save results to file
        with open("api-connection-test-results.json", "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "results": self.results
            }, f, indent=2)
        
        print(f"\n✅ Results saved to scripts/api-connection-test-results.json")
        
        return self.results["failed"] == 0

async def main():
    """Main test runner"""
    tester = APIConnectionTester()
    
    # Check if server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/health", timeout=2.0)
            print(f"✅ Server is running (Health check: {response.status_code})")
    except:
        print("❌ Server is not running! Please start the server with:")
        print("   python main.py")
        return False
    
    # Run all tests
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! All API endpoints are properly connected.")
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
    
    return success

if __name__ == "__main__":
    asyncio.run(main())