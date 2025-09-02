#!/usr/bin/env python3
"""
Test Phase 1 Stack Auth endpoints using FastAPI TestClient
"""
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from main import app


def test_phase1_endpoints():
    """Test Phase 1 endpoints with FastAPI TestClient"""
    client = TestClient(app)

    print("🚀 Phase 1 Stack Auth Endpoint Test")
    print("=" * 60)

    # Test endpoints without authentication - should return 401
    endpoints = [
        ("/api/users/me", "Get current user"),
        ("/api/users/profile", "Get user profile"),
        ("/api/users/dashboard", "Get user dashboard"),
        ("/api/business-profiles/", "Get business profile"),
    ]

    results = []

    for endpoint, description in endpoints:
        print(f"\n🧪 Testing {description}")
        print(f"   Endpoint: {endpoint}")
        print("-" * 50)

        try:
            response = client.get(endpoint)
            print(f"   Status: {response.status_code}")

            if response.status_code == 401:
                print("   ✅ Correctly protected - returns 401")
                results.append((endpoint, True))
            else:
                print(f"   ❌ Expected 401, got {response.status_code}")
                if response.status_code == 500:
                    print(f"   Error: {response.text[:200]}")
                results.append((endpoint, False))

        except Exception as e:
            # Check if it's a 401 HTTPException (which is what we want)
            if "401" in str(e) and "Authentication required" in str(e):
                print("   ✅ Correctly protected - returns 401")
                results.append((endpoint, True))
            else:
                print(f"   ❌ Unexpected error: {e}")
                results.append((endpoint, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for endpoint, result in results:
        status = "✅ PROTECTED" if result else "❌ UNPROTECTED"
        print(f"   {endpoint:35} {status}")

    print(f"\n   Results: {passed}/{total} endpoints properly protected")

    return passed == total


if __name__ == "__main__":
    success = test_phase1_endpoints()

    if success:
        print("\n🎉 Phase 1 migration successful!")
        print("   All endpoints are properly protected by Stack Auth")
    else:
        print("\n⚠️  Phase 1 migration needs attention")
        print("   Some endpoints are not properly protected")

    sys.exit(0 if success else 1)
