#!/usr/bin/env python3
"""Quick test audit to identify issues."""

import subprocess
import json
from pathlib import Path
from typing import Dict, List


def run_pytest_json():
    """Run pytest with JSON output to get detailed results."""
    print("Running pytest with JSON output...")

    # Install pytest-json-report if needed
    subprocess.run(["pip", "install", "pytest-json-report"], capture_output=True)

    # Run pytest with JSON reporter
    result = subprocess.run(
        [
            "python",
            "-m",
            "pytest",
            "--json-report",
            "--json-report-file=test_report.json",
            "-v",
            "--tb=short",
            "--maxfail=1000",
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )

    print(f"Return code: {result.returncode}")
    print("\nSTDOUT:")
    print(result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
    print("\nSTDERR:")
    print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)

    # Try to load and parse the JSON report
    report_file = Path("test_report.json")
    if report_file.exists():
        with open(report_file) as f:
            data = json.load(f)

        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)

        summary = data.get("summary", {})
        print(f"Total tests: {summary.get('total', 0)}")
        print(f"Passed: {summary.get('passed', 0)}")
        print(f"Failed: {summary.get('failed', 0)}")
        print(f"Errors: {summary.get('error', 0)}")
        print(f"Skipped: {summary.get('skipped', 0)}")

        # Calculate pass rate
        total = summary.get("total", 0)
        passed = summary.get("passed", 0)
        if total > 0:
            pass_rate = (passed / total) * 100
            print(f"\nPass Rate: {pass_rate:.1f}%")
            print(f"Target: 95.0%")
            print(f"Gap: {95.0 - pass_rate:.1f}%")

        # Show failed tests
        tests = data.get("tests", [])
        failed_tests = [t for t in tests if t.get("outcome") in ["failed", "error"]]

        if failed_tests:
            print("\n" + "=" * 60)
            print("FAILED/ERROR TESTS")
            print("=" * 60)
            for test in failed_tests[:20]:  # Show first 20
                print(f"- {test.get('nodeid', 'Unknown')}")
                if test.get("call", {}).get("longrepr"):
                    print(f"  Error: {test['call']['longrepr'][:200]}...")
    else:
        print("No JSON report generated")


if __name__ == "__main__":
    run_pytest_json()
