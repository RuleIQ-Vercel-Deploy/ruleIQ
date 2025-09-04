#!/usr/bin/env python3
"""
QA Test Runner - Systematic test execution and analysis
Mission: Achieve 80% test pass rate for RuleIQ
"""

import subprocess
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple
import re

def run_pytest_collect() -> Tuple[int, List[str]]:
    """Collect all tests without running them."""
    print("\n🔍 Collecting tests...")
    result = subprocess.run(
        ["python", "-m", "pytest", "--collect-only", "-q"],
        capture_output=True,
        text=True
    )
    
    # Parse collected tests
    lines = result.stdout.strip().split('\n')
    test_count = 0
    test_files = set()
    
    for line in lines:
        if "test" in line.lower() and ".py" in line:
            # Extract file path
            match = re.search(r'(tests/[^:]+\.py)', line)
            if match:
                test_files.add(match.group(1))
        # Look for summary line
        if "collected" in line.lower():
            match = re.search(r'collected (\d+)', line)
            if match:
                test_count = int(match.group(1))
    
    return test_count, list(test_files)

def run_quick_test_assessment() -> Dict:
    """Run a quick test to assess current state."""
    print("\n📊 Running quick test assessment...")
    
    # First try with minimal options to see basic failures
    result = subprocess.run(
        ["python", "-m", "pytest", 
         "--tb=no",  # No tracebacks for initial scan
         "--no-header",
         "-q",
         "--maxfail=100",  # Stop after 100 failures to get a sample
         "--json-report",
         "--json-report-file=test_results.json"
        ],
        capture_output=True,
        text=True,
        timeout=300  # 5 minute timeout
    )
    
    # Parse results
    stats = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "error": 0,
        "skipped": 0,
        "collection_errors": []
    }
    
    # Try to parse JSON report if created
    json_report = Path("test_results.json")
    if json_report.exists():
        try:
            with open(json_report) as f:
                report = json.load(f)
                summary = report.get("summary", {})
                stats["total"] = summary.get("total", 0)
                stats["passed"] = summary.get("passed", 0)
                stats["failed"] = summary.get("failed", 0)
                stats["error"] = summary.get("error", 0)
                stats["skipped"] = summary.get("skipped", 0)
        except:
            pass
    
    # Parse stdout for summary
    for line in result.stdout.split('\n'):
        if "passed" in line or "failed" in line or "error" in line:
            # Extract numbers from summary line
            numbers = re.findall(r'(\d+)\s+(\w+)', line)
            for count, status in numbers:
                if status in ["passed", "failed", "error", "skipped"]:
                    stats[status] = int(count)
    
    # Check for collection errors
    if "ERROR collecting" in result.stderr or "ERROR collecting" in result.stdout:
        stats["collection_errors"].append("Collection errors detected")
    
    return stats

def identify_failure_patterns() -> Dict:
    """Identify common failure patterns across tests."""
    print("\n🔎 Analyzing failure patterns...")
    
    # Run with verbose output to capture failure details
    result = subprocess.run(
        ["python", "-m", "pytest", 
         "--tb=line",  # Single line tracebacks
         "-v",
         "--maxfail=50",  # Sample of failures
         "-x"  # Stop on first failure to analyze
        ],
        capture_output=True,
        text=True,
        timeout=120
    )
    
    patterns = {
        "api_validation": [],
        "missing_fixtures": [],
        "import_errors": [],
        "database_errors": [],
        "environment_errors": [],
        "async_errors": [],
        "authentication_errors": [],
        "other": []
    }
    
    error_text = result.stdout + result.stderr
    
    # Pattern matching for common issues
    if "fixture" in error_text and "not found" in error_text:
        matches = re.findall(r"fixture '([^']+)' not found", error_text)
        patterns["missing_fixtures"].extend(set(matches))
    
    if "ImportError" in error_text or "ModuleNotFoundError" in error_text:
        matches = re.findall(r"(?:ImportError|ModuleNotFoundError): ([^\n]+)", error_text)
        patterns["import_errors"].extend(matches[:5])  # First 5 unique
    
    if "AttributeError" in error_text and "Settings" in error_text:
        patterns["environment_errors"].append("Settings/Environment configuration issues")
    
    if "ValidationError" in error_text or "422" in error_text or "400" in error_text:
        patterns["api_validation"].append("API validation/request format issues")
    
    if "asyncio" in error_text or "coroutine" in error_text:
        patterns["async_errors"].append("Async/await issues")
    
    if "psycopg2" in error_text or "sqlalchemy" in error_text or "database" in error_text.lower():
        patterns["database_errors"].append("Database connectivity/query issues")
    
    if "401" in error_text or "403" in error_text or "authentication" in error_text.lower():
        patterns["authentication_errors"].append("Auth/permission issues")
    
    return patterns

def run_targeted_test_group(test_path: str) -> Dict:
    """Run a specific test file or directory."""
    print(f"\n🎯 Testing: {test_path}")
    
    result = subprocess.run(
        ["python", "-m", "pytest", 
         test_path,
         "--tb=short",
         "-v",
         "--maxfail=10"
        ],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    # Parse results
    passed = len(re.findall(r"PASSED", result.stdout))
    failed = len(re.findall(r"FAILED", result.stdout))
    error = len(re.findall(r"ERROR", result.stdout))
    
    return {
        "path": test_path,
        "passed": passed,
        "failed": failed,
        "error": error,
        "total": passed + failed + error
    }

def main():
    """Main QA test runner."""
    print("=" * 80)
    print("🚀 RuleIQ QA Test Runner - Mission: 80% Pass Rate")
    print("=" * 80)
    
    # Step 1: Collect tests
    total_tests, test_files = run_pytest_collect()
    print(f"✅ Found {total_tests} tests across {len(test_files)} files")
    
    # Step 2: Quick assessment
    print("\nRunning initial assessment...")
    stats = run_quick_test_assessment()
    
    if stats["total"] > 0:
        pass_rate = (stats["passed"] / stats["total"]) * 100
        print(f"\n📈 Current Status:")
        print(f"  Total Tests: {stats['total']}")
        print(f"  Passed: {stats['passed']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Errors: {stats['error']}")
        print(f"  Skipped: {stats['skipped']}")
        print(f"  Pass Rate: {pass_rate:.1f}%")
        print(f"  Target: 80% ({int(stats['total'] * 0.8)} tests)")
        print(f"  Gap: {int(stats['total'] * 0.8) - stats['passed']} tests to fix")
    
    # Step 3: Identify patterns
    patterns = identify_failure_patterns()
    print("\n🔍 Failure Patterns Detected:")
    for category, issues in patterns.items():
        if issues:
            print(f"\n  {category.replace('_', ' ').title()}:")
            for issue in issues[:3]:  # Show first 3
                print(f"    - {issue}")
    
    # Step 4: Test high-impact areas
    print("\n📦 Testing Key Areas:")
    key_areas = [
        "tests/unit",
        "tests/integration", 
        "tests/test_fixtures.py",
        "tests/conftest.py"
    ]
    
    for area in key_areas:
        if Path(area).exists():
            results = run_targeted_test_group(area)
            if results["total"] > 0:
                area_pass_rate = (results["passed"] / results["total"]) * 100
                print(f"  {area}: {results['passed']}/{results['total']} ({area_pass_rate:.1f}%)")
    
    print("\n" + "=" * 80)
    print("📋 Next Steps:")
    print("1. Fix missing fixtures (high impact)")
    print("2. Resolve API validation issues")
    print("3. Fix environment configuration")
    print("4. Address import errors")
    print("5. Fix async/database issues")
    print("=" * 80)

if __name__ == "__main__":
    main()