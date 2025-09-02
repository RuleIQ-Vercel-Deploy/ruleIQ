#!/usr/bin/env python3
"""
Comprehensive test runner for all 32 failing tests.
Runs tests with proper error reporting and summary.
"""

import subprocess
import sys
import os
from pathlib import Path

# Test categories
TEST_CATEGORIES = {
    "Cache Strategy & Content": [
        "tests/unit/services/test_cache_strategy_optimization.py",
        "tests/unit/services/test_cached_content.py",
    ],
    "AI Compliance Accuracy": [
        "tests/ai/test_compliance_accuracy.py",
    ],
    "AI Optimization Performance": [
        "tests/performance/test_ai_optimization_performance.py",
    ],
    "Database Performance": [
        "tests/performance/test_database_performance.py",
    ],
}


def run_test_category(category_name, test_files):
    """Run tests in a category."""
    print(f"\n{'=' * 60}")
    print(f"Running {category_name} Tests")
    print("=" * 60)

    results = []
    for test_file in test_files:
        if not Path(test_file).exists():
            print(f"\n❌ {test_file} - FILE NOT FOUND")
            results.append(
                {"file": test_file, "passed": False, "error": "File not found"}
            )
            continue

        print(f"\n▶ Running {test_file}...")

        cmd = [
            sys.executable,
            "-m",
            "pytest",
            test_file,
            "-v",
            "--tb=short",
            "--no-header",
            "--no-summary",
            "-q",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        # Parse results
        output = result.stdout + result.stderr
        passed = result.returncode == 0

        if passed:
            # Count passed tests
            passed_count = output.count(" PASSED")
            print(f"  ✅ All tests passed ({passed_count} tests)")
        else:
            # Extract failure info
            failed_count = output.count(" FAILED")
            error_count = output.count(" ERROR")

            print(f"  ❌ Tests failed (Failed: {failed_count}, Errors: {error_count})")

            # Show first few error lines
            error_lines = [
                line
                for line in output.split("\n")
                if "FAILED" in line or "ERROR" in line
            ][:3]
            for line in error_lines:
                print(f"     {line.strip()}")

        results.append({"file": test_file, "passed": passed, "output": output})

    return results


def main():
    """Run all test categories and provide summary."""
    print("🧪 Running All Failing Tests")
    print("=" * 60)

    all_results = {}

    # Set environment
    os.environ["ENV"] = "testing"
    os.environ["USE_MOCK_AI"] = "true"
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"

    # Run each category
    for category, test_files in TEST_CATEGORIES.items():
        results = run_test_category(category, test_files)
        all_results[category] = results

    # Summary
    print(f"\n{'=' * 60}")
    print("📊 TEST SUMMARY")
    print("=" * 60)

    total_files = 0
    passed_files = 0

    for category, results in all_results.items():
        category_passed = sum(1 for r in results if r["passed"])
        category_total = len(results)
        total_files += category_total
        passed_files += category_passed

        status = "✅" if category_passed == category_total else "❌"
        print(f"{status} {category}: {category_passed}/{category_total} files passed")

    print(f"\n📈 Overall: {passed_files}/{total_files} test files passed")

    if passed_files < total_files:
        print("\n❌ Failed test files:")
        for category, results in all_results.items():
            for result in results:
                if not result["passed"]:
                    print(f"  - {result['file']}")

    return passed_files == total_files


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
