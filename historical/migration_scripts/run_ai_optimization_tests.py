#!/usr/bin/env python3
"""
Test runner script for AI Optimization tests.

Runs comprehensive test suite for the AI optimization implementation
including unit tests, integration tests, and performance tests.
"""

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List


class AIOptimizationTestRunner:
    """Test runner for AI optimization implementation."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_results = {}

    def run_unit_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run unit tests for AI optimization."""
        print("🧪 Running AI Optimization Unit Tests...")

        test_files = [
            "tests/unit/services/test_ai_circuit_breaker.py",
            "tests/unit/services/test_ai_model_selection.py",
            "tests/unit/services/test_ai_streaming.py",
        ]

        cmd = [
            "python",
            "-m",
            "pytest",
            *test_files,
            "-v" if verbose else "-q",
            "--tb=short",
            "--durations=10",
            "--cov=services.ai",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov/ai_optimization",
        ]

        start_time = time.time()
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        duration = time.time() - start_time

        return {
            "name": "Unit Tests",
            "success": result.returncode == 0,
            "duration": duration,
            "output": result.stdout,
            "errors": result.stderr,
        }

    def run_integration_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run integration tests for AI optimization."""
        print("🔗 Running AI Optimization Integration Tests...")

        test_files = ["tests/integration/test_ai_optimization_endpoints.py"]

        cmd = [
            "python",
            "-m",
            "pytest",
            *test_files,
            "-v" if verbose else "-q",
            "--tb=short",
            "--durations=10",
        ]

        start_time = time.time()
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        duration = time.time() - start_time

        return {
            "name": "Integration Tests",
            "success": result.returncode == 0,
            "duration": duration,
            "output": result.stdout,
            "errors": result.stderr,
        }

    def run_performance_tests(self, verbose: bool = False) -> Dict[str, Any]:
        """Run performance tests for AI optimization."""
        print("⚡ Running AI Optimization Performance Tests...")

        test_files = ["tests/performance/test_ai_optimization_performance.py"]

        cmd = [
            "python",
            "-m",
            "pytest",
            *test_files,
            "-v" if verbose else "-q",
            "--tb=short",
            "--durations=10",
            "-m",
            "not slow",  # Skip slow tests by default
        ]

        start_time = time.time()
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        duration = time.time() - start_time

        return {
            "name": "Performance Tests",
            "success": result.returncode == 0,
            "duration": duration,
            "output": result.stdout,
            "errors": result.stderr,
        }

    def run_specific_test(self, test_path: str, verbose: bool = False) -> Dict[str, Any]:
        """Run a specific test file."""
        print(f"🎯 Running specific test: {test_path}")

        cmd = ["python", "-m", "pytest", test_path, "-v" if verbose else "-q", "--tb=short"]

        start_time = time.time()
        result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True)
        duration = time.time() - start_time

        return {
            "name": f"Specific Test: {test_path}",
            "success": result.returncode == 0,
            "duration": duration,
            "output": result.stdout,
            "errors": result.stderr,
        }

    def run_all_tests(
        self, verbose: bool = False, include_performance: bool = False
    ) -> List[Dict[str, Any]]:
        """Run all AI optimization tests."""
        print("🚀 Running Complete AI Optimization Test Suite...")
        print("=" * 60)

        results = []

        # Run unit tests
        unit_result = self.run_unit_tests(verbose)
        results.append(unit_result)
        self._print_test_result(unit_result)

        # Run integration tests
        integration_result = self.run_integration_tests(verbose)
        results.append(integration_result)
        self._print_test_result(integration_result)

        # Run performance tests if requested
        if include_performance:
            performance_result = self.run_performance_tests(verbose)
            results.append(performance_result)
            self._print_test_result(performance_result)

        return results

    def _print_test_result(self, result: Dict[str, Any]):
        """Print test result summary."""
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        duration = f"{result['duration']:.2f}s"

        print(f"{status} {result['name']} ({duration})")

        if not result["success"] and result["errors"]:
            print(f"   Errors: {result['errors'][:200]}...")

        print()

    def generate_test_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate comprehensive test report."""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r["success"])
        total_duration = sum(r["duration"] for r in results)

        report = f"""
AI Optimization Test Report
==========================

Summary:
- Total Test Suites: {total_tests}
- Passed: {passed_tests}
- Failed: {total_tests - passed_tests}
- Total Duration: {total_duration:.2f}s
- Success Rate: {(passed_tests / total_tests) * 100:.1f}%

Detailed Results:
"""

        for result in results:
            status = "PASSED" if result["success"] else "FAILED"
            report += f"""
{result["name"]}: {status} ({result["duration"]:.2f}s)
"""
            if not result["success"]:
                report += f"  Errors: {result['errors']}\n"

        return report

    def check_test_dependencies(self) -> bool:
        """Check if all test dependencies are available."""
        print("🔍 Checking test dependencies...")

        required_packages = ["pytest", "pytest-asyncio", "pytest-cov", "httpx", "psutil"]

        missing_packages = []

        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            print(f"❌ Missing packages: {', '.join(missing_packages)}")
            print("Install with: pip install " + " ".join(missing_packages))
            return False

        print("✅ All test dependencies available")
        return True

    def setup_test_environment(self):
        """Setup test environment variables."""
        os.environ["TESTING"] = "true"
        os.environ["AI_TESTING_MODE"] = "true"
        os.environ["CIRCUIT_BREAKER_TESTING"] = "true"

        # Disable actual AI API calls during testing
        os.environ["MOCK_AI_RESPONSES"] = "true"


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="AI Optimization Test Runner")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--performance", "-p", action="store_true", help="Include performance tests"
    )
    parser.add_argument("--unit", "-u", action="store_true", help="Run only unit tests")
    parser.add_argument(
        "--integration", "-i", action="store_true", help="Run only integration tests"
    )
    parser.add_argument("--perf-only", action="store_true", help="Run only performance tests")
    parser.add_argument("--test", "-t", type=str, help="Run specific test file")
    parser.add_argument("--report", "-r", action="store_true", help="Generate detailed report")
    parser.add_argument("--check-deps", action="store_true", help="Check test dependencies only")

    args = parser.parse_args()

    # Get project root
    project_root = Path(__file__).parent.parent

    # Initialize test runner
    runner = AIOptimizationTestRunner(project_root)

    # Check dependencies if requested
    if args.check_deps:
        runner.check_test_dependencies()
        return

    # Setup test environment
    runner.setup_test_environment()

    # Check dependencies
    if not runner.check_test_dependencies():
        sys.exit(1)

    results = []

    try:
        if args.test:
            # Run specific test
            result = runner.run_specific_test(args.test, args.verbose)
            results.append(result)
        elif args.unit:
            # Run only unit tests
            result = runner.run_unit_tests(args.verbose)
            results.append(result)
        elif args.integration:
            # Run only integration tests
            result = runner.run_integration_tests(args.verbose)
            results.append(result)
        elif args.perf_only:
            # Run only performance tests
            result = runner.run_performance_tests(args.verbose)
            results.append(result)
        else:
            # Run all tests
            results = runner.run_all_tests(args.verbose, args.performance)

        # Print summary
        print("=" * 60)
        total_passed = sum(1 for r in results if r["success"])
        total_tests = len(results)

        if total_passed == total_tests:
            print(f"🎉 All {total_tests} test suite(s) PASSED!")
        else:
            print(f"⚠️  {total_passed}/{total_tests} test suite(s) passed")

        # Generate report if requested
        if args.report:
            report = runner.generate_test_report(results)
            report_file = project_root / "test_reports" / "ai_optimization_report.txt"
            report_file.parent.mkdir(exist_ok=True)
            report_file.write_text(report)
            print(f"📄 Detailed report saved to: {report_file}")

        # Exit with appropriate code
        sys.exit(0 if total_passed == total_tests else 1)

    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Test runner error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
