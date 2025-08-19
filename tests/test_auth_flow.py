#!/usr/bin/env python3
"""
Test complete Stack Auth flow with actual server
"""

import requests
import subprocess
import time
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_auth_flow():
    """Test the complete authentication flow"""

    print("🚀 Testing Complete Stack Auth Flow")
    print("=" * 50)

    # Start server
    print("\n1. Starting server...")
    server = None
    try:
        server = subprocess.Popen(
            [sys.executable, "main.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

        # Wait for server to start
        time.sleep(4)

        # Test 1: Health endpoint (should work without auth)
        print("\n2. Testing public endpoints...")
        try:
            response = requests.get("http://localhost:8000/health", timeout=10)
            print(
                f"   Health endpoint: {response.status_code} ({'✅ PASS' if response.status_code == 200 else '❌ FAIL'})"
            )
        except Exception as e:
            print(f"   Health endpoint: ❌ FAIL - {e}")
            return False

        # Test 2: Root endpoint (should work without auth)
        try:
            response = requests.get("http://localhost:8000/", timeout=10)
            print(
                f"   Root endpoint: {response.status_code} ({'✅ PASS' if response.status_code == 200 else '❌ FAIL'})"
            )
        except Exception as e:
            print(f"   Root endpoint: ❌ FAIL - {e}")

        # Test 3: Protected endpoint without auth (should return 401)
        print("\n3. Testing protected endpoints without auth...")
        protected_endpoints = [
            "/api/dashboard",
            "/api/business-profiles",
            "/api/assessments",
            "/api/users/me",
        ]

        auth_working = True
        for endpoint in protected_endpoints:
            try:
                response = requests.get(f"http://localhost:8000{endpoint}", timeout=10)
                status = response.status_code
                expected = status == 401
                result = "✅ PASS" if expected else f"❌ FAIL (got {status}, expected 401)"
                print(f"   {endpoint}: {status} ({result})")
                if not expected:
                    auth_working = False
                    # Print response details for debugging
                    print(f"      Response: {response.text[:200]}")
            except Exception as e:
                print(f"   {endpoint}: ❌ ERROR - {e}")
                auth_working = False

        # Test 4: Protected endpoint with invalid token (should return 401)
        print("\n4. Testing protected endpoints with invalid token...")
        headers = {"Authorization": "Bearer invalid_token_12345"}

        for endpoint in protected_endpoints[:2]:  # Test first 2 endpoints
            try:
                response = requests.get(
                    f"http://localhost:8000{endpoint}", headers=headers, timeout=10
                )
                status = response.status_code
                expected = status == 401
                result = "✅ PASS" if expected else f"❌ FAIL (got {status}, expected 401)"
                print(f"   {endpoint}: {status} ({result})")
                if not expected:
                    auth_working = False
                    print(f"      Response: {response.text[:200]}")
            except Exception as e:
                print(f"   {endpoint}: ❌ ERROR - {e}")

        # Summary
        print(f"\n🎯 Authentication Status: {'✅ WORKING' if auth_working else '❌ NOT WORKING'}")

        if not auth_working:
            print("\n🔍 Debugging Info:")
            print("   - Check if Stack Auth middleware is properly configured")
            print("   - Verify middleware is being applied to protected routes")
            print("   - Check server logs for authentication errors")
        else:
            print("\n✅ Stack Auth backend integration is working correctly!")
            print("   - Public endpoints accessible without auth")
            print("   - Protected endpoints require authentication")
            print("   - Invalid tokens are properly rejected")

        return auth_working

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

    finally:
        # Clean up server
        if server:
            try:
                server.terminate()
                server.wait(timeout=5)
                print("\n🛑 Server stopped")
            except:
                server.kill()
                print("\n🛑 Server killed")


if __name__ == "__main__":
    success = test_auth_flow()
    print(f"\n{'✅ All tests passed!' if success else '❌ Some tests failed!'}")
    sys.exit(0 if success else 1)
