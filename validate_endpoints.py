#!/usr/bin/env python3
"""
API Endpoint Validation Script

This script validates API endpoints using an in-process TestClient.
It imports the FastAPI app directly and tests routes without starting an external server.

Environment Variables:
- AUTH_TOKEN: Optional authentication token for protected endpoints
- ENDPOINT_FILTER: Optional comma-separated list of endpoints to test
- BASE_URL: Optional external server URL (if set, uses external server instead of TestClient)
"""

import os
import sys
import json
import traceback
from typing import List, Dict, Any, Optional
import requests

try:
    from fastapi.testclient import TestClient
    from api.main import app
except ImportError as e:
    print(f"❌ Failed to import required modules: {e}")
    sys.exit(1)


def get_test_client() -> Optional[TestClient]:
    """Get TestClient or None if external BASE_URL is set."""
    base_url = os.environ.get("BASE_URL")
    if base_url:
        print(f"📡 Using external server: {base_url}")
        return None
    print("🔧 Using in-process TestClient")
    return TestClient(app)


def get_routes() -> List[Dict[str, Any]]:
    """Discover all routes from the FastAPI app."""
    routes = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else [],
                "name": getattr(route, "name", "unknown")
            })
    return routes


def validate_endpoint(
    client: Optional[TestClient],
    method: str,
    path: str,
    auth_token: Optional[str] = None
) -> Dict[str, Any]:
    """Validate a single endpoint."""
    result = {
        "path": path,
        "method": method,
        "status": "unknown",
        "status_code": None,
        "error": None
    }

    # Skip endpoints with required path parameters
    if "{" in path:
        result["status"] = "skipped"
        result["error"] = "Path parameters required"
        return result

    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    try:
        if client:
            # In-process TestClient
            if method == "GET":
                response = client.get(path, headers=headers)
            elif method == "POST":
                response = client.post(path, headers=headers, json={})
            elif method == "PUT":
                response = client.put(path, headers=headers, json={})
            elif method == "DELETE":
                response = client.delete(path, headers=headers)
            else:
                result["status"] = "skipped"
                result["error"] = f"Unsupported method: {method}"
                return result
        else:
            # External server
            base_url = os.environ.get("BASE_URL", "http://localhost:8000")
            url = f"{base_url.rstrip('/')}{path}"

            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json={}, timeout=10)
            elif method == "PUT":
                response = requests.put(url, headers=headers, json={}, timeout=10)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=10)
            else:
                result["status"] = "skipped"
                result["error"] = f"Unsupported method: {method}"
                return result

        result["status_code"] = response.status_code

        # Check for 5xx errors (server errors)
        if response.status_code >= 500:
            result["status"] = "failed"
            result["error"] = f"Server error: {response.status_code}"
        # 401/403 are expected for auth-protected routes without token
        elif response.status_code in [401, 403] and not auth_token:
            result["status"] = "auth_required"
        # 404 is tolerated for certain endpoints
        elif response.status_code == 404 and path in ["/ready", "/health/ready"] or 200 <= response.status_code < 400:
            result["status"] = "passed"
        # 4xx (except auth) are client errors but not server failures
        else:
            result["status"] = "client_error"
            result["error"] = f"Client error: {response.status_code}"

    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)

    return result


def validate_core_endpoints(client: Optional[TestClient], auth_token: Optional[str]) -> List[Dict[str, Any]]:
    """Validate core endpoints."""
    core_endpoints = [
        ("GET", "/health"),
        ("GET", "/ready"),
        ("GET", "/openapi.json"),
    ]

    results = []
    for method, path in core_endpoints:
        print(f"🔍 Testing {method} {path}")
        result = validate_endpoint(client, method, path, auth_token)
        results.append(result)

        # Special validation for openapi.json
        if path == "/openapi.json" and result["status"] == "passed":
            try:
                if client:
                    response = client.get(path)
                else:
                    base_url = os.environ.get("BASE_URL", "http://localhost:8000")
                    response = requests.get(f"{base_url.rstrip('/')}{path}", timeout=10)

                openapi_spec = response.json()
                if "openapi" in openapi_spec:
                    print(f"  ✅ Valid OpenAPI spec (version: {openapi_spec.get('openapi', 'unknown')})")
                else:
                    result["status"] = "failed"
                    result["error"] = "Invalid OpenAPI spec"
            except json.JSONDecodeError:
                result["status"] = "failed"
                result["error"] = "OpenAPI response is not valid JSON"
            except Exception as e:
                result["status"] = "failed"
                result["error"] = f"Failed to validate OpenAPI spec: {e}"

    return results


def validate_discovered_routes(
    client: Optional[TestClient],
    routes: List[Dict[str, Any]],
    auth_token: Optional[str],
    endpoint_filter: Optional[List[str]]
) -> List[Dict[str, Any]]:
    """Validate discovered routes."""
    results = []

    for route in routes:
        path = route["path"]

        # Skip if filter is set and path not in filter
        if endpoint_filter and not any(f in path for f in endpoint_filter):
            continue

        # Skip OpenAPI internal routes
        if path.startswith("/openapi") or path in {"/docs", "/redoc"}:
            continue

        # Only test GET endpoints without required path params
        if "GET" in route["methods"] and "{" not in path:
            print(f"🔍 Testing GET {path}")
            result = validate_endpoint(client, "GET", path, auth_token)
            results.append(result)

    return results


def print_summary(results: List[Dict[str, Any]]) -> bool:
    """Print validation summary and return success status."""
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)

    stats = {
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "auth_required": 0,
        "client_error": 0,
        "error": 0
    }

    for result in results:
        status = result["status"]
        stats[status] = stats.get(status, 0) + 1

        icon = {
            "passed": "✅",
            "failed": "❌",
            "skipped": "⏭️",
            "auth_required": "🔒",
            "client_error": "⚠️",
            "error": "💥"
        }.get(status, "❓")

        print(f"{icon} {result['method']} {result['path']}: {status}", end="")
        if result["status_code"]:
            print(f" ({result['status_code']})", end="")
        if result["error"]:
            print(f" - {result['error']}", end="")
        print()

    print("\n" + "-" * 60)
    print(f"✅ Passed: {stats['passed']}")
    print(f"❌ Failed: {stats['failed']}")
    print(f"⏭️  Skipped: {stats['skipped']}")
    print(f"🔒 Auth Required: {stats['auth_required']}")
    print(f"⚠️  Client Errors: {stats['client_error']}")
    print(f"💥 Errors: {stats['error']}")
    print("-" * 60)

    # Success if no failures or errors
    success = stats["failed"] == 0 and stats["error"] == 0

    if success:
        print("✅ All endpoint validations passed!")
    else:
        print("❌ Some endpoint validations failed!")

    return success


def main():
    """Main validation function."""
    print("🚀 Starting API Endpoint Validation")
    print("=" * 60)

    # Get configuration from environment
    auth_token = os.environ.get("AUTH_TOKEN")
    endpoint_filter = os.environ.get("ENDPOINT_FILTER")
    if endpoint_filter:
        endpoint_filter = [e.strip() for e in endpoint_filter.split(",")]
        print(f"📝 Filtering endpoints: {endpoint_filter}")

    if auth_token:
        print("🔑 Using authentication token")

    try:
        # Get test client or None for external server
        client = get_test_client()

        # Validate core endpoints
        results = validate_core_endpoints(client, auth_token)

        # Discover and validate additional routes
        if client:  # Only discover routes from in-process app
            routes = get_routes()
            print(f"\n📋 Discovered {len(routes)} routes")

            # Validate discovered routes
            route_results = validate_discovered_routes(
                client, routes, auth_token, endpoint_filter
            )
            results.extend(route_results)

        # Print summary and determine success
        success = print_summary(results)

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"\n💥 Fatal error during validation: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
