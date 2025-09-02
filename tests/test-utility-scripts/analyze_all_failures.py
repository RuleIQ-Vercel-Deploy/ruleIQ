#!/usr/bin/env python
"""Analyze all test failures in the codebase."""

import subprocess
import json
import sys
from pathlib import Path


def run_tests_and_analyze():
    """Run tests and capture failures."""
    print("Running all tests to identify failures...")

    # Run pytest with json report
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "--tb=short",
        "--json-report",
        "--json-report-file=test_failure_report.json",
        "-v",
    ]

    # Run tests (allow it to fail)
    subprocess.run(cmd, capture_output=True, text=True)

    # Read the JSON report
    report_path = Path("test_failure_report.json")
    if not report_path.exists():
        print("No test report generated. Running with basic output...")
        # Fallback to basic run
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-v", "--tb=short"],
            capture_output=True,
            text=True,
        )

        # Parse output for failures
        failures = []
        for line in result.stdout.split("\n"):
            if "FAILED" in line:
                failures.append(line.strip())

        print(f"\nFound {len(failures)} test failures:")
        for i, failure in enumerate(failures[:20], 1):  # Show first 20
            print(f"{i}. {failure}")

        if len(failures) > 20:
            print(f"... and {len(failures) - 20} more failures")

        return failures

    with open(report_path, "r") as f:
        report = json.load(f)

    # Analyze failures
    failures = []
    for test in report.get("tests", []):
        if test["outcome"] == "failed":
            failures.append(
                {
                    "nodeid": test["nodeid"],
                    "error": test.get("call", {}).get("longrepr", "Unknown error"),
                }
            )

    print(f"\nTotal test failures: {len(failures)}")

    # Group by test file
    by_file = {}
    for failure in failures:
        file_path = failure["nodeid"].split("::")[0]
        if file_path not in by_file:
            by_file[file_path] = []
        by_file[file_path].append(failure)

    print("\nFailures by file:")
    for file_path, file_failures in sorted(by_file.items()):
        print(f"\n{file_path}: {len(file_failures)} failures")
        for f in file_failures[:3]:  # Show first 3 per file
            print(f"  - {f['nodeid'].split('::')[-1]}")

    return failures


if __name__ == "__main__":
    run_tests_and_analyze()
