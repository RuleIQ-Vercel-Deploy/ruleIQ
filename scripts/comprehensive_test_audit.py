#!/usr/bin/env python3
"""
from __future__ import annotations

Comprehensive Backend Test Suite Audit
=======================================
This script analyzes and executes the complete test suite to identify gaps
and achieve the required 95% pass rate across ALL tests.
"""

import os
import sys
import json
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime
from collections import defaultdict

class TestSuiteAuditor:
    """Comprehensive test suite analysis and execution."""

    def __init__(self):
        self.project_root = Path.cwd()
        self.test_results = {}
        self.test_files = []
        self.test_categories = defaultdict(list)
        self.execution_stats = {
            "total_files": 0,
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "collection_errors": 0,
            "execution_time": 0,
        }

    def discover_all_test_files(self) -> List[Path]:
        """Discover all test files in the project."""
        test_patterns = ["test_*.py", "*_test.py"]
        exclude_dirs = {".venv", "venv", "__pycache__", ".git", "node_modules"}

        test_files = []

        # Primary test directory
        tests_dir = self.project_root / "tests"
        if tests_dir.exists():
            for pattern in test_patterns:
                test_files.extend(tests_dir.rglob(pattern))

        # Look for tests in other directories
        for root_item in self.project_root.iterdir():
            if root_item.is_dir() and root_item.name not in exclude_dirs:
                if root_item.name in ["scripts", "app"]:
                    for pattern in test_patterns:
                        test_files.extend(root_item.rglob(pattern))

        # Filter out excluded paths
        filtered_files = []
        for test_file in test_files:
            path_str = str(test_file)
            if not any(exclude in path_str for exclude in exclude_dirs):
                filtered_files.append(test_file)

        return sorted(set(filtered_files))

    def categorize_tests(self, test_files: List[Path]) -> Dict[str, List[Path]]:
        """Categorize tests by type/module."""
        categories = defaultdict(list)

        for test_file in test_files:
            parts = test_file.parts

            # Determine category based on path
            if "tests" in parts:
                idx = parts.index("tests")
                if idx + 1 < len(parts):
                    category = parts[idx + 1]
                    if category.endswith(".py"):
                        category = "root"
                else:
                    category = "root"
            elif "scripts" in parts:
                category = "scripts"
            elif "app" in parts:
                category = "app"
            elif "historical" in parts:
                category = "historical"
            else:
                category = "other"

            categories[category].append(test_file)

        return dict(categories)

    def collect_tests_from_file(self, test_file: Path) -> Tuple[int, List[str]]:
        """Collect tests from a single file without executing."""
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    str(test_file),
                    "--collect-only",
                    "-q",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # Parse output to count tests
            lines = result.stdout.split("\n")
            test_count = 0
            test_names = []

            for line in lines:
                if "<Function" in line or "<Method" in line:
                    test_count += 1
                    # Extract test name
                    if "test_" in line:
                        parts = line.split("test_")
                        if len(parts) > 1:
                            test_name = "test_" + parts[1].split(">")[0]
                            test_names.append(test_name)
                elif "error" in line.lower() or "failed" in line.lower():
                    return -1, []

            return test_count, test_names

        except subprocess.TimeoutExpired:
            return -1, []
        except (OSError, KeyError, IndexError) as e:
            print(f"Error collecting from {test_file}: {e}")
            return -1, []

    def run_test_file(self, test_file: Path) -> Dict:
        """Run tests in a single file and collect results."""
        result = {
            "file": str(test_file.relative_to(self.project_root)),
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "total": 0,
            "execution_time": 0,
            "failures": [],
        }

        start_time = time.time()

        try:
            # Run pytest with JSON output
            proc_result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    str(test_file),
                    "-v",
                    "--tb=short",
                    "--no-header",
                    "-q",
                ],
                capture_output=True,
                text=True,
                timeout=60,
                env={**os.environ, "TESTING": "true"},
            )

            execution_time = time.time() - start_time
            result["execution_time"] = execution_time

            # Parse output
            output_lines = proc_result.stdout.split("\n")

            for line in output_lines:
                if "::test_" in line:
                    result["total"] += 1
                    if "PASSED" in line:
                        result["passed"] += 1
                    elif "FAILED" in line:
                        result["failed"] += 1
                        # Extract failure info
                        test_name = line.split("::")[1].split(" ")[0]
                        result["failures"].append(test_name)
                    elif "SKIPPED" in line:
                        result["skipped"] += 1
                    elif "ERROR" in line:
                        result["errors"] += 1
                elif "passed" in line and "failed" in line:
                    # Summary line
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if "passed" in part and i > 0:
                            try:
                                result["passed"] = int(parts[i - 1])
                            except (ValueError, KeyError, IndexError):
                                pass
                        elif "failed" in part and i > 0:
                            try:
                                result["failed"] = int(parts[i - 1])
                            except (ValueError, KeyError, IndexError):
                                pass
                        elif "skipped" in part and i > 0:
                            try:
                                result["skipped"] = int(parts[i - 1])
                            except (ValueError, KeyError, IndexError):
                                pass

            # If no tests were found in parsing, check return code
            if result["total"] == 0 and proc_result.returncode != 0:
                result["errors"] = 1

        except subprocess.TimeoutExpired:
            result["errors"] = 1
            result["execution_time"] = 60

        except (ValueError, KeyError, IndexError) as e:
            result["errors"] = 1
            result["execution_time"] = time.time() - start_time
            print(f"Error running {test_file}: {e}")

        return result

    def run_category_tests(self, category: str, test_files: List[Path]) -> Dict:
        """Run all tests in a category."""
        category_results = {
            "category": category,
            "total_files": len(test_files),
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "files": [],
        }

        print(f"\n{'='*60}")
        print(f"Testing Category: {category}")
        print(f"{'='*60}")

        for test_file in test_files:
            print(f"  Running: {test_file.name}...", end=" ")

            # First collect to see if file is valid
            test_count, _ = self.collect_tests_from_file(test_file)

            if test_count == -1:
                print("❌ Collection Error")
                category_results["errors"] += 1
                self.execution_stats["collection_errors"] += 1
                continue
            elif test_count == 0:
                print("⚠️ No tests found")
                continue

            # Run the tests
            result = self.run_test_file(test_file)

            # Update category stats
            category_results["total_tests"] += result["total"]
            category_results["passed"] += result["passed"]
            category_results["failed"] += result["failed"]
            category_results["skipped"] += result["skipped"]
            category_results["errors"] += result["errors"]
            category_results["files"].append(result)

            # Print result
            if result["errors"] > 0:
                print(f"❌ {result['errors']} errors")
            elif result["failed"] > 0:
                print(f"❌ {result['failed']} failed")
            elif result["passed"] == result["total"]:
                print(f"✅ {result['passed']} passed")
            else:
                print(f"⚠️ {result['passed']}/{result['total']} passed")

        return category_results

    def generate_report(self, results: Dict) -> str:
        """Generate comprehensive test report."""
        report = f"""# Backend Test Suite Audit Report

**Generated**: {datetime.now().isoformat()}
**Project**: RuleIQ

## Executive Summary

- **Total Test Files**: {results['total_files']}
- **Total Tests Discovered**: {results['total_tests']}
- **Tests Executed**: {results['executed_tests']}
- **Passed**: {results['passed']} ({results['pass_rate']:.1f}%)
- **Failed**: {results['failed']}
- **Skipped**: {results['skipped']}
- **Errors**: {results['errors']}
- **Collection Errors**: {results['collection_errors']}

### Pass Rate Analysis
- **Current Pass Rate**: {results['pass_rate']:.1f}%
- **Target Pass Rate**: 95.0%
- **Gap**: {95.0 - results['pass_rate']:.1f}%
- **Tests Needed to Pass**: {results['tests_needed_to_pass']}

## Category Breakdown

| Category | Files | Tests | Passed | Failed | Errors | Pass Rate |
|----------|-------|-------|--------|--------|--------|-----------|
"""

        for category, data in results["categories"].items():
            total_tests = data["total_tests"]
            if total_tests > 0:
                pass_rate = (data["passed"] / total_tests) * 100
            else:
                pass_rate = 0

            report += f"| {category} | {data['total_files']} | {total_tests} | "
            report += f"{data['passed']} | {data['failed']} | {data['errors']} | "
            report += f"{pass_rate:.1f}% |\n"

        # Failed tests section
        report += "\n## Failed Tests Requiring Attention\n\n"

        failed_by_category = defaultdict(list)
        for category, data in results["categories"].items():
            for file_result in data.get("files", []):
                if file_result["failures"]:
                    for failure in file_result["failures"]:
                        failed_by_category[category].append(
                            {"file": file_result["file"], "test": failure},
                        )

        if failed_by_category:
            for category, failures in failed_by_category.items():
                report += f"\n### {category}\n\n"
                for failure in failures[:10]:  # Limit to first 10
                    report += f"- `{failure['file']}::{failure['test']}`\n"
                if len(failures) > 10:
                    report += f"- ... and {len(failures) - 10} more\n"
        else:
            report += "No test failures recorded.\n"

        # Problematic files
        report += "\n## Files with Collection Errors\n\n"

        error_files = []
        for category, data in results["categories"].items():
            for file_result in data.get("files", []):
                if file_result.get("errors", 0) > 0:
                    error_files.append(file_result["file"])

        if error_files:
            for error_file in error_files[:20]:
                report += f"- `{error_file}`\n"
            if len(error_files) > 20:
                report += f"- ... and {len(error_files) - 20} more\n"
        else:
            report += "No collection errors.\n"

        # Recommendations
        report += "\n## Recommendations\n\n"

        if results["pass_rate"] < 95:
            report += (
                f"1. **Fix {results['failed']} failing tests** to improve pass rate\n",
            )
            report += f"2. **Resolve {results['collection_errors']} collection errors** to enable more tests\n"
            report += f"3. **Review {results['skipped']} skipped tests** - enable if possible\n"

        if results["collection_errors"] > 0:
            report += (
                "4. **Fix import errors and missing dependencies** in test files\n",
            )

        report += "\n## Next Steps\n\n"
        report += "1. Fix collection errors to discover all tests\n"
        report += "2. Address failing tests by category priority\n"
        report += "3. Remove or update historical/deprecated tests\n"
        report += "4. Ensure proper test isolation and fixtures\n"
        report += "5. Add missing test coverage for critical paths\n"

        return report

    def execute_full_audit(self) -> Dict:
        """Execute comprehensive test suite audit."""
        print("🔍 Starting Comprehensive Test Suite Audit")
        print("=" * 60)

        # Discover all test files
        print("\n📁 Discovering test files...")
        self.test_files = self.discover_all_test_files()
        print(f"  Found {len(self.test_files)} test files")

        # Categorize tests
        self.test_categories = self.categorize_tests(self.test_files)

        print(f"\n📊 Test Distribution:")
        for category, files in self.test_categories.items():
            print(f"  - {category}: {len(files)} files")

        # Run tests by category
        category_results = {}
        total_passed = 0
        total_failed = 0
        total_skipped = 0
        total_errors = 0
        total_tests = 0

        for category, files in self.test_categories.items():
            if category in ["historical"]:  # Skip historical tests
                print(f"\n⏭️ Skipping {category} tests")
                continue

            results = self.run_category_tests(category, files)
            category_results[category] = results

            total_tests += results["total_tests"]
            total_passed += results["passed"]
            total_failed += results["failed"]
            total_skipped += results["skipped"]
            total_errors += results["errors"]

        # Calculate pass rate
        executed_tests = total_passed + total_failed
        if executed_tests > 0:
            pass_rate = (total_passed / executed_tests) * 100
        else:
            pass_rate = 0

        # Calculate tests needed to reach 95%
        tests_needed = max(0, int(0.95 * executed_tests - total_passed))

        # Compile final results
        final_results = {
            "total_files": len(self.test_files),
            "total_tests": total_tests,
            "executed_tests": executed_tests,
            "passed": total_passed,
            "failed": total_failed,
            "skipped": total_skipped,
            "errors": total_errors,
            "collection_errors": self.execution_stats["collection_errors"],
            "pass_rate": pass_rate,
            "tests_needed_to_pass": tests_needed,
            "categories": category_results,
        }

        return final_results

def main():
    """Main execution function."""
    auditor = TestSuiteAuditor()

    # Run full audit
    results = auditor.execute_full_audit()

    # Generate report
    report = auditor.generate_report(results)

    # Save report
    report_file = "backend_test_audit_report.md"
    with open(report_file, "w") as f:
        f.write(report)

    print(f"\n📄 Report saved to {report_file}")

    # Save detailed results
    results_file = "backend_test_results.json"
    with open(results_file, "w") as f:
        # Convert Path objects to strings for JSON serialization
        json_results = json.dumps(results, default=str, indent=2)
        f.write(json_results)

    print(f"📊 Detailed results saved to {results_file}")

    # Print summary
    print("\n" + "=" * 60)
    print("AUDIT SUMMARY")
    print("=" * 60)
    print(f"Total Tests Discovered: {results['total_tests']}")
    print(f"Tests Executed: {results['executed_tests']}")
    print(f"Pass Rate: {results['pass_rate']:.1f}%")
    print(f"Target: 95.0%")

    if results["pass_rate"] >= 95:
        print("✅ Target achieved!")
        return 0
    else:
        print(f"❌ Need to fix {results['tests_needed_to_pass']} more tests")
        return 1

if __name__ == "__main__":
    sys.exit(main())
