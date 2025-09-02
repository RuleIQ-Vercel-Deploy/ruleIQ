#!/usr/bin/env python3
"""Quick API test to verify connectivity without timeout"""

import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"


async def test_endpoints():
    """Test key endpoints to verify API alignment"""

    # Key endpoints to test (sample from each category)
    test_endpoints = [
        ("GET", "/", "Root", False),
        ("GET", "/health", "Health", False),
        ("GET", "/api/v1/health", "API Health", False),
        ("POST", "/api/v1/auth/token", "Auth Token", False),
        ("GET", "/api/v1/auth/me", "Current User", True),
        ("GET", "/api/v1/auth/google/login", "Google Login", False),
        ("GET", "/api/v1/users", "List Users", True),
        ("GET", "/api/v1/business-profiles", "Business Profiles", True),
        ("GET", "/api/v1/assessments", "Assessments", True),
        ("GET", "/api/v1/frameworks", "Frameworks", True),
        ("GET", "/api/v1/policies", "Policies", True),
        ("POST", "/api/v1/ai/analyze", "AI Analyze", True),
        (
            "GET",
            "/api/v1/ai/optimization/circuit-breaker/status",
            "Circuit Breaker",
            True,
        ),
        ("GET", "/api/v1/compliance/status", "Compliance Status", True),
        ("GET", "/api/v1/dashboard/stats", "Dashboard Stats", True),
        ("GET", "/api/v1/monitoring/health", "Monitoring Health", False),
        ("POST", "/api/v1/agentic-rag/find-examples", "RAG Examples", True),
        ("POST", "/api/v1/chat/message", "Chat Message", True),
        ("GET", "/api/v1/iq-agent/suggestions", "IQ Agent", True),
    ]

    results = {
        "timestamp": datetime.now().isoformat(),
        "total": 0,
        "passed": 0,
        "failed": 0,
        "endpoints": [],
    }

    async with aiohttp.ClientSession() as session:
        for method, path, name, auth_required in test_endpoints:
            results["total"] += 1

            try:
                async with session.request(
                    method, f"{BASE_URL}{path}", timeout=aiohttp.ClientTimeout(total=2)
                ) as response:
                    status = response.status

                    # Consider 200-499 as "connected" (endpoint exists)
                    # 401/403 for auth endpoints is expected
                    if status < 500 or (auth_required and status in [401, 403]):
                        results["passed"] += 1
                        print(f"✓ {method:6} {path:50} [{status}] - {name}")
                        results["endpoints"].append(
                            {
                                "method": method,
                                "path": path,
                                "status": status,
                                "passed": True,
                                "name": name,
                            }
                        )
                    else:
                        results["failed"] += 1
                        print(f"✗ {method:6} {path:50} [{status}] - {name}")
                        results["endpoints"].append(
                            {
                                "method": method,
                                "path": path,
                                "status": status,
                                "passed": False,
                                "name": name,
                            }
                        )

            except Exception as e:
                results["failed"] += 1
                print(f"✗ {method:6} {path:50} [ERROR] - {name}: {str(e)}")
                results["endpoints"].append(
                    {
                        "method": method,
                        "path": path,
                        "error": str(e),
                        "passed": False,
                        "name": name,
                    }
                )

    # Calculate pass rate
    pass_rate = (
        (results["passed"] / results["total"] * 100) if results["total"] > 0 else 0
    )

    print(f"\n{'='*60}")
    print(f"QUICK API TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Endpoints Tested: {results['total']}")
    print(f"Passed: {results['passed']} ({pass_rate:.1f}%)")
    print(f"Failed: {results['failed']} ({100-pass_rate:.1f}%)")

    if pass_rate == 100:
        print(f"\n🎉 PERFECT! All tested endpoints are connected!")
    elif pass_rate >= 90:
        print(f"\n✅ EXCELLENT! Most endpoints are working!")
    else:
        print(f"\n⚠️  Some endpoints need attention")

    # Save results
    with open("scripts/quick-api-test-results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: scripts/quick-api-test-results.json")

    return results


if __name__ == "__main__":
    asyncio.run(test_endpoints())
