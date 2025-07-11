#!/usr/bin/env python3
"""
Test Group Runner for ruleIQ
Organizes tests into 6 independent groups for parallel execution
"""

import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Test Groups Configuration - Optimized for ~600 tests across 6 balanced groups
TEST_GROUPS = {
    "group1_unit": {
        "name": "Unit Tests - Core Business Logic",
        "description": "Fast unit tests for services, models, and utilities (192 tests)",
        "patterns": [
            "tests/unit/",
        ],
        "estimated_time": "2-3 minutes",
        "test_count": 192,
    },
    "group2_integration_api": {
        "name": "Integration Tests - API Endpoints",
        "description": "API integration tests for all endpoints (128 tests)",
        "patterns": [
            "tests/integration/",
        ],
        "estimated_time": "4-5 minutes",
        "test_count": 128,
    },
    "group3_ai_comprehensive": {
        "name": "AI Tests - Comprehensive Suite",
        "description": "All AI-related tests: core, ethics, accuracy, rate limiting (65 tests)",
        "patterns": [
            "tests/ai/",
            "tests/test_ai_assessment_endpoints_integration.py",
            "tests/test_ai_ethics.py",
            "tests/test_ai_rate_limiting.py",
            "tests/test_compliance_accuracy.py",
            "tests/test_compliance_assistant_assessment.py",
        ],
        "estimated_time": "3-4 minutes",
        "test_count": 65,
    },
    "group4_workflows_e2e": {
        "name": "Workflows & E2E Tests",
        "description": "End-to-end workflows, integration flows, and user journeys (46 tests)",
        "patterns": [
            "tests/e2e/",
            "tests/test_e2e_workflows.py",
            "tests/test_integration.py",
            "tests/test_services.py",
            "tests/test_usability.py",
        ],
        "estimated_time": "5-6 minutes",
        "test_count": 46,
    },
    "group5_performance_security": {
        "name": "Performance & Security Tests",
        "description": "Performance benchmarks, security audits, and monitoring (100 tests)",
        "patterns": [
            "tests/performance/",
            "tests/security/",
            "tests/monitoring/",
            "tests/test_performance.py",
            "tests/test_security.py",
        ],
        "estimated_time": "4-5 minutes",
        "test_count": 100,
    },
    "group6_specialized": {
        "name": "Specialized & Load Tests",
        "description": "Load tests, database tests, and specialized workflows (66 tests)",
        "patterns": [
            "tests/load/",
            "tests/integration/database/",
            "tests/integration/workers/",
            "tests/test_assessment_workflow_e2e.py",
            "tests/test_sanity_check.py",
        ],
        "estimated_time": "3-4 minutes",
        "test_count": 66,
    },
}


def run_test_group(group_name, group_config):
    """Run a single test group"""
    print(f"\n🚀 Starting {group_config['name']} ({group_name})")
    print(f"📝 {group_config['description']}")
    print(f"⏱️  Estimated time: {group_config['estimated_time']}")

    # Build pytest command
    patterns = " ".join(group_config["patterns"])
    cmd = f"python -m pytest {patterns} -v --tb=short -q"

    start_time = time.time()

    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=Path.cwd())

        duration = time.time() - start_time

        if result.returncode == 0:
            print(f"✅ {group_config['name']} PASSED ({duration:.1f}s)")
            return {
                "group": group_name,
                "name": group_config["name"],
                "status": "PASSED",
                "duration": duration,
                "output": result.stdout,
            }
        else:
            print(f"❌ {group_config['name']} FAILED ({duration:.1f}s)")
            print(f"Error output:\n{result.stderr}")
            return {
                "group": group_name,
                "name": group_config["name"],
                "status": "FAILED",
                "duration": duration,
                "output": result.stdout,
                "error": result.stderr,
            }

    except Exception as e:
        duration = time.time() - start_time
        print(f"💥 {group_config['name']} ERROR ({duration:.1f}s): {e}")
        return {
            "group": group_name,
            "name": group_config["name"],
            "status": "ERROR",
            "duration": duration,
            "error": str(e),
        }


def run_single_group(group_name):
    """Run a single test group by name"""
    if group_name not in TEST_GROUPS:
        print(f"❌ Unknown test group: {group_name}")
        print(f"Available groups: {', '.join(TEST_GROUPS.keys())}")
        return False

    result = run_test_group(group_name, TEST_GROUPS[group_name])
    return result["status"] == "PASSED"


def run_all_groups_parallel():
    """Run all test groups in parallel"""
    print("🎯 Running ALL test groups in parallel...")
    print(f"📊 Total groups: {len(TEST_GROUPS)}")

    start_time = time.time()
    results = []

    with ThreadPoolExecutor(max_workers=6) as executor:
        # Submit all groups
        future_to_group = {
            executor.submit(run_test_group, name, config): name
            for name, config in TEST_GROUPS.items()
        }

        # Collect results as they complete
        for future in as_completed(future_to_group):
            result = future.result()
            results.append(result)

    # Print summary
    total_duration = time.time() - start_time
    passed = sum(1 for r in results if r["status"] == "PASSED")
    failed = sum(1 for r in results if r["status"] == "FAILED")
    errors = sum(1 for r in results if r["status"] == "ERROR")

    print("\n📊 PARALLEL EXECUTION SUMMARY")
    print(f"⏱️  Total time: {total_duration:.1f}s")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"💥 Errors: {errors}")
    print(f"📈 Success rate: {passed / len(results) * 100:.1f}%")

    return passed == len(results)


def run_all_groups_sequential():
    """Run all test groups sequentially"""
    print("🎯 Running ALL test groups sequentially...")

    start_time = time.time()
    results = []

    for group_name, group_config in TEST_GROUPS.items():
        result = run_test_group(group_name, group_config)
        results.append(result)

        if result["status"] != "PASSED":
            print(f"⚠️  Group {group_name} failed, continuing...")

    # Print summary
    total_duration = time.time() - start_time
    passed = sum(1 for r in results if r["status"] == "PASSED")
    failed = sum(1 for r in results if r["status"] == "FAILED")
    errors = sum(1 for r in results if r["status"] == "ERROR")

    print("\n📊 SEQUENTIAL EXECUTION SUMMARY")
    print(f"⏱️  Total time: {total_duration:.1f}s")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"💥 Errors: {errors}")
    print(f"📈 Success rate: {passed / len(results) * 100:.1f}%")

    return passed == len(results)


def list_groups():
    """List all available test groups"""
    print("📋 Available Test Groups (597 total tests):")
    print("=" * 80)
    total_tests = 0
    for name, config in TEST_GROUPS.items():
        test_count = config.get("test_count", 0)
        total_tests += test_count
        print(f"\n🔹 {name}")
        print(f"   Name: {config['name']}")
        print(f"   Description: {config['description']}")
        print(f"   Test Count: {test_count} tests")
        print(f"   Estimated time: {config['estimated_time']}")
        print(f"   Patterns: {', '.join(config['patterns'])}")

    print("=" * 80)
    print(f"📊 TOTAL: {total_tests} tests across {len(TEST_GROUPS)} groups")
    print("⚡ Parallel execution: ~6-8 minutes total")
    print("🔄 Sequential execution: ~20-25 minutes total")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python test_groups.py list                    # List all groups")
        print("  python test_groups.py <group_name>            # Run single group")
        print("  python test_groups.py all                     # Run all groups sequentially")
        print("  python test_groups.py parallel                # Run all groups in parallel")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        list_groups()
    elif command == "all":
        success = run_all_groups_sequential()
        sys.exit(0 if success else 1)
    elif command == "parallel":
        success = run_all_groups_parallel()
        sys.exit(0 if success else 1)
    elif command in TEST_GROUPS:
        success = run_single_group(command)
        sys.exit(0 if success else 1)
    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)
