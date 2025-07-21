#!/usr/bin/env python3
"""
AI Service Testing Script for ruleIQ
Comprehensive testing of AI functionality
"""

import os
import sys
import json
import subprocess
from datetime import datetime

# Add project root to path
sys.path.insert(0, "/home/omar/Documents/ruleIQ")

# Attempt to load dotenv if available
try:
    from dotenv import load_dotenv

    load_dotenv("/home/omar/Documents/ruleIQ/.env.local")
    print("✅ Loaded environment variables from .env.local")
except ImportError:
    print("⚠️ `python-dotenv` not found. Assuming environment variables are set.")


def test_environment_setup():
    """Test Phase 1: Environment & Configuration"""
    print("=== AI Service Testing - Phase 1: Environment & Configuration ===")
    print()

    results = {"phase": "environment", "timestamp": datetime.utcnow().isoformat(), "tests": []}

    # Test 1: Google API Key
    google_key = os.getenv("GOOGLE_AI_API_KEY")
    if google_key and len(google_key) > 10:
        results["tests"].append(
            {
                "test": "google_api_key",
                "status": "pass",
                "message": "Google API Key present and valid format",
                "details": {"key_length": len(google_key)},
            }
        )
        print("✅ Google API Key: Present and valid format")
    else:
        results["tests"].append(
            {
                "test": "google_api_key",
                "status": "fail",
                "message": "Google API Key missing or invalid",
                "details": {"has_key": bool(google_key)},
            }
        )
        print("❌ Google API Key: Missing or invalid")
        print("   Please set GOOGLE_AI_API_KEY environment variable in .env.local")

    # Test 2: Mock AI Mode
    use_mock = os.getenv("USE_MOCK_AI", "false").lower() == "true"
    results["tests"].append(
        {
            "test": "mock_ai_mode",
            "status": "pass",
            "message": f"Mock AI mode: {'Enabled' if use_mock else 'Disabled'}",
            "details": {"use_mock": use_mock},
        }
    )
    print(f"{'ℹ️'} Mock AI Mode: {'Enabled' if use_mock else 'Disabled'}")

    return results


def test_api_endpoints():
    """Test Phase 2: API Endpoints (using curl)"""
    print("\n=== AI Service Testing - Phase 2: API Endpoints ===")
    print()

    results = {"phase": "api_endpoints", "timestamp": datetime.utcnow().isoformat(), "tests": []}

    base_url = "http://localhost:8000"

    # Test 1: Detailed Health endpoint for better diagnostics
    try:
        health_url = f"{base_url}/api/v1/health/detailed"
        result = subprocess.run(
            ["curl", "-s", health_url], capture_output=True, text=True, timeout=10
        )
        response_text = result.stdout.strip()

        if result.returncode == 0 and response_text:
            try:
                response_json = json.loads(response_text)
                status = response_json.get("status")
                if status in ["healthy", "degraded"]:
                    results["tests"].append(
                        {
                            "test": "backend_health",
                            "status": "pass",
                            "message": f"Backend is responding. Overall status: {status}",
                            "details": response_json,
                        }
                    )
                    print(f"✅ Backend Health: Responding with status '{status}'")
                    if status == "degraded":
                        print("   Component Status:")
                        for component, comp_status in response_json.get("components", {}).items():
                            print(f"   - {component}: {comp_status}")
                else:
                    results["tests"].append(
                        {
                            "test": "backend_health",
                            "status": "fail",
                            "message": f"Backend health check returned unexpected status: {status}",
                            "details": response_json,
                        }
                    )
                    print(f"❌ Backend Health: Unexpected status '{status}'")
                    return results
            except json.JSONDecodeError:
                results["tests"].append(
                    {
                        "test": "backend_health",
                        "status": "fail",
                        "message": "Backend health check responded with invalid JSON.",
                        "details": {"response": response_text},
                    }
                )
                print("❌ Backend Health: Invalid JSON response")
                return results
        else:
            results["tests"].append(
                {
                    "test": "backend_health",
                    "status": "fail",
                    "message": "Backend health check failed. No response.",
                    "details": {"error": result.stderr.strip()},
                }
            )
            print("❌ Backend Health: Failed with no response")
            return results
    except Exception as e:
        results["tests"].append(
            {
                "test": "backend_health",
                "status": "error",
                "message": f"Could not connect to backend: {e}",
            }
        )
        print(f"❌ Backend Health: Connection error - {e}")
        return results

    # Test 2: AI Help Endpoint
    try:
        payload = {
            "question_id": "test-question-1",
            "question_text": "How do I implement access controls for SOC 2?",
            "framework_id": "soc2",
            "user_context": {"business_type": "SaaS Startup"},
        }
        # Corrected URL with trailing slash
        url = f"{base_url}/api/v1/ai-assessments/soc2/help/"
        result = subprocess.run(
            [
                "curl",
                "-s",
                "-X",
                "POST",
                url,
                "-H",
                "Content-Type: application/json",
                "-d",
                json.dumps(payload),
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )

        response_text = result.stdout.strip()
        if result.returncode == 0 and response_text:
            try:
                response_json = json.loads(response_text)
                results["tests"].append(
                    {
                        "test": "ai_help_endpoint",
                        "status": "pass",
                        "message": "AI help endpoint responded successfully.",
                        "details": {"response_length": len(response_text)},
                    }
                )
                print("✅ AI Help Endpoint: Success")
            except json.JSONDecodeError:
                results["tests"].append(
                    {
                        "test": "ai_help_endpoint",
                        "status": "fail",
                        "message": "AI help endpoint responded with invalid JSON.",
                        "details": {"response": response_text},
                    }
                )
                print("❌ AI Help Endpoint: Invalid JSON response")
        else:
            results["tests"].append(
                {
                    "test": "ai_help_endpoint",
                    "status": "fail",
                    "message": "AI help endpoint failed.",
                    "details": {"error": result.stderr.strip(), "response": response_text},
                }
            )
            print("❌ AI Help Endpoint: Failed")

    except Exception as e:
        results["tests"].append(
            {
                "test": "ai_help_endpoint",
                "status": "error",
                "message": f"Error testing AI help endpoint: {e}",
            }
        )
        print(f"❌ AI Help Endpoint: Error - {e}")

    return results


def run_all_tests():
    """Run all test phases and save the report."""
    print("🚀 Starting AI Service Test Suite")
    print("=" * 40)

    all_results = {"summary": {}, "phases": [], "timestamp": datetime.utcnow().isoformat()}

    # Phase 1
    env_results = test_environment_setup()
    all_results["phases"].append(env_results)

    # Phase 2
    api_results = test_api_endpoints()
    all_results["phases"].append(api_results)

    # Summary
    total_tests = sum(len(phase["tests"]) for phase in all_results["phases"])
    passed_tests = sum(
        1 for phase in all_results["phases"] for test in phase["tests"] if test["status"] == "pass"
    )

    all_results["summary"] = {
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": total_tests - passed_tests,
        "success_rate": f"{(passed_tests / total_tests * 100):.2f}%" if total_tests > 0 else "N/A",
    }

    print("\n" + "=" * 40)
    print("📊 Test Summary")
    print("=" * 40)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")

    # Save report
    report_path = "ai_test_report.json"
    with open(report_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n✅ Test report saved to {report_path}")


if __name__ == "__main__":
    run_all_tests()
