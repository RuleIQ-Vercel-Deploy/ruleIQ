#!/usr/bin/env python3
"""
Validate Postman collection setup for RuleIQ API
"""

import json
import os
import sys


def validate_collection(filename):
    """Validate Postman collection file"""
    if not os.path.exists(filename):
        return False, f"Collection file not found: {filename}"

    try:
        with open(filename, "r") as f:
            collection = json.load(f)

        # Check required fields
        if "info" not in collection or "item" not in collection:
            return False, "Invalid collection structure"

        # Count endpoints
        total_endpoints = 0
        for folder in collection.get("item", []):
            if "item" in folder:
                total_endpoints += len(folder["item"])

        # Check authentication
        has_auth = "auth" in collection

        return True, {
            "name": collection["info"].get("name", "Unknown"),
            "folders": len(collection.get("item", [])),
            "endpoints": total_endpoints,
            "has_auth": has_auth,
        }
    except Exception as e:
        return False, f"Error reading collection: {str(e)}"


def validate_environment(filename):
    """Validate Postman environment file"""
    if not os.path.exists(filename):
        return False, f"Environment file not found: {filename}"

    try:
        with open(filename, "r") as f:
            env = json.load(f)

        # Check required variables
        required_vars = [
            "base_url",
            "api_version",
            "test_user_email",
            "test_user_password",
        ]

        env_vars = {v["key"]: v["value"] for v in env.get("values", [])}
        missing = [v for v in required_vars if v not in env_vars]

        if missing:
            return False, f"Missing environment variables: {', '.join(missing)}"

        return True, {
            "name": env.get("name", "Unknown"),
            "variables": len(env_vars),
            "has_credentials": env_vars.get("test_user_email") == "test@ruleiq.dev",
        }
    except Exception as e:
        return False, f"Error reading environment: {str(e)}"


def main():
    print("RuleIQ Postman Setup Validation")
    print("=" * 60)

    # Check consolidated collection
    print("\n📦 Checking Consolidated Collection...")
    success, result = validate_collection("ruleiq_postman_collection_consolidated.json")
    if success:
        print(f"  ✅ Collection: {result['name']}")
        print(f"  ✅ Folders: {result['folders']}")
        print(f"  ✅ Endpoints: {result['endpoints']}")
        print(
            f"  ✅ Authentication: {'Configured' if result['has_auth'] else 'Not configured'}"
        )
    else:
        print(f"  ❌ {result}")

    # Check environment
    print("\n🔧 Checking Environment...")
    success, result = validate_environment("ruleiq_postman_environment.json")
    if success:
        print(f"  ✅ Environment: {result['name']}")
        print(f"  ✅ Variables: {result['variables']}")
        print(
            f"  ✅ Test Credentials: {'Correct' if result['has_credentials'] else 'Incorrect'}"
        )
    else:
        print(f"  ❌ {result}")

    # Check backend connectivity
    print("\n🌐 Checking Backend...")
    try:
        import requests

        response = requests.get("http://localhost:8000/api/v1/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Backend Status: {data.get('status', 'Unknown')}")
            print(f"  ✅ Version: {data.get('version', 'Unknown')}")
        else:
            print(f"  ⚠️ Backend returned status {response.status_code}")
    except Exception as e:
        print(f"  ❌ Backend not accessible: {str(e)}")

    # Test authentication
    print("\n🔐 Testing Authentication...")
    try:
        import requests

        login_data = {"username": "test@ruleiq.dev", "password": "TestPassword123!"}
        response = requests.post(
            "http://localhost:8000/api/v1/auth/token", data=login_data, timeout=5
        )
        if response.status_code == 200:
            print(f"  ✅ Login successful")
            token = response.json().get("access_token", "")[:30] + "..."
            print(f"  ✅ Token received: {token}")
        else:
            print(f"  ❌ Login failed with status {response.status_code}")
    except Exception as e:
        print(f"  ❌ Authentication test failed: {str(e)}")

    print("\n" + "=" * 60)
    print("✨ Postman Setup Validation Complete!")
    print("\nNext Steps:")
    print("1. Import 'ruleiq_postman_collection_consolidated.json' into Postman")
    print("2. Import 'ruleiq_postman_environment.json' as environment")
    print("3. Select 'RuleIQ Development' environment")
    print("4. Start testing with the Authentication folder!")


if __name__ == "__main__":
    main()
