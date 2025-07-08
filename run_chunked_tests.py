#!/usr/bin/env python3
"""
Chunked Test Runner for ruleIQ Project

Organizes ~795 tests into 6 logical groups and runs them asynchronously
for better test execution efficiency and management.
"""

import asyncio
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Tuple
import sys

# Test group definitions - organized by functionality and dependencies
TEST_GROUPS = {
    "group1_core_backend": [
        "tests/unit/",
        "tests/test_services.py",
        "tests/test_integration.py",
        "tests/test_sanity_check.py",
        "tests/security/",
    ],
    "group2_ai_services": [
        "tests/ai/",
        "tests/integration/test_ai_error_handling.py",
        "tests/integration/test_ai_optimization_endpoints.py",
        "tests/test_ai_assessment_endpoints_integration.py",
        "tests/test_compliance_assistant_assessment.py",
        "tests/test_ai_ethics.py",
        "tests/test_ai_rate_limiting.py",
    ],
    "group3_api_endpoints": [
        "tests/integration/api/test_evidence_endpoints.py",
        "tests/integration/api/test_evidence_classification.py",
        "tests/integration/api/test_quality_analysis.py",
        "tests/integration/api/test_analytics_endpoints.py",
    ],
    "group4_chat_ai_endpoints": [
        "tests/integration/api/test_chat_endpoints.py",
        "tests/integration/api/test_enhanced_chat_endpoints.py",
        "tests/integration/api/test_ai_assessments.py",
    ],
    "group5_integration": [
        "tests/integration/test_evidence_flow.py",
        "tests/test_assessment_workflow_e2e.py",
        "tests/test_e2e_workflows.py",
        "tests/e2e/",
        "tests/monitoring/",
    ],
    "group6_performance": [
        "tests/performance/",
        "tests/test_performance.py",
        "tests/test_compliance_accuracy.py",
        "tests/test_usability.py",
        "tests/test_security.py",
    ]
}

class TestRunner:
    def __init__(self):
        self.results: Dict[str, Dict] = {}
        self.start_time = time.time()

    async def run_test_group(self, group_name: str, test_paths: List[str]) -> Dict:
        """Run a single test group and return results."""
        print(f"🚀 Starting {group_name}...")
        
        # Filter paths that actually exist
        existing_paths = []
        for path in test_paths:
            if Path(path).exists():
                existing_paths.append(path)
            else:
                print(f"⚠️  Path not found: {path}")
        
        if not existing_paths:
            return {
                "group": group_name,
                "status": "skipped",
                "reason": "No valid test paths found",
                "duration": 0,
                "passed": 0,
                "failed": 0,
                "total": 0
            }

        # Build pytest command
        cmd = [
            "python", "-m", "pytest",
            *existing_paths,
            "-v",
            "--tb=short",
            "--maxfail=50",  # Continue running even with failures
            "--durations=10",
            f"--junit-xml=test_results_{group_name}.xml"
        ]
        
        start_time = time.time()
        
        try:
            # Run the tests
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=Path.cwd()
            )
            
            stdout, stderr = await process.communicate()
            duration = time.time() - start_time
            
            # Parse results from output
            output = stdout.decode() + stderr.decode()
            passed, failed, total = self._parse_pytest_output(output)
            
            result = {
                "group": group_name,
                "status": "completed",
                "return_code": process.returncode,
                "duration": duration,
                "passed": passed,
                "failed": failed,
                "total": total,
                "output_file": f"test_results_{group_name}.xml"
            }
            
            status_emoji = "✅" if process.returncode == 0 else "❌"
            print(f"{status_emoji} {group_name} completed: {passed}/{total} passed in {duration:.1f}s")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            print(f"❌ {group_name} failed with exception: {e}")
            return {
                "group": group_name,
                "status": "error",
                "error": str(e),
                "duration": duration,
                "passed": 0,
                "failed": 0,
                "total": 0
            }

    def _parse_pytest_output(self, output: str) -> Tuple[int, int, int]:
        """Parse pytest output to extract test counts."""
        lines = output.split('\n')
        
        for line in lines:
            if 'passed' in line and ('failed' in line or 'error' in line):
                # Look for summary line like "5 failed, 10 passed in 30.2s"
                parts = line.split()
                passed = failed = 0
                
                for i, part in enumerate(parts):
                    if part == 'passed' and i > 0:
                        try:
                            passed = int(parts[i-1])
                        except ValueError:
                            pass
                    elif part in ['failed', 'error'] and i > 0:
                        try:
                            failed += int(parts[i-1])
                        except ValueError:
                            pass
                
                total = passed + failed
                return passed, failed, total
            
            elif 'passed' in line and 'failed' not in line and 'error' not in line:
                # Look for line like "10 passed in 30.2s"
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == 'passed' and i > 0:
                        try:
                            passed = int(parts[i-1])
                            return passed, 0, passed
                        except ValueError:
                            pass
        
        return 0, 0, 0

    async def run_all_groups(self):
        """Run all test groups concurrently."""
        print("🧪 Starting ruleIQ Chunked Test Execution")
        print(f"📊 Running {len(TEST_GROUPS)} test groups asynchronously")
        print("=" * 60)
        
        # Create tasks for all groups
        tasks = []
        for group_name, test_paths in TEST_GROUPS.items():
            task = asyncio.create_task(
                self.run_test_group(group_name, test_paths),
                name=group_name
            )
            tasks.append(task)
        
        # Wait for all groups to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Store results
        for result in results:
            if isinstance(result, dict):
                self.results[result["group"]] = result
            else:
                print(f"❌ Unexpected error: {result}")
        
        self._print_summary()

    def _print_summary(self):
        """Print comprehensive test execution summary."""
        total_duration = time.time() - self.start_time
        
        print("\n" + "=" * 60)
        print("📋 CHUNKED TEST EXECUTION SUMMARY")
        print("=" * 60)
        
        total_passed = total_failed = total_tests = 0
        
        for group_name, result in self.results.items():
            status_emoji = "✅" if result.get("return_code") == 0 else "❌"
            passed = result.get("passed", 0)
            failed = result.get("failed", 0)
            total = result.get("total", 0)
            duration = result.get("duration", 0)
            
            print(f"{status_emoji} {group_name:25} | {passed:3d}/{total:3d} passed | {duration:6.1f}s")
            
            total_passed += passed
            total_failed += failed
            total_tests += total
        
        print("-" * 60)
        print(f"🎯 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {total_passed} ({total_passed/total_tests*100:.1f}%)" if total_tests > 0 else "   Passed: 0")
        print(f"   Failed: {total_failed}")
        print(f"   Duration: {total_duration:.1f}s")
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        if success_rate >= 95:
            print("🎉 EXCELLENT: >95% pass rate achieved!")
        elif success_rate >= 90:
            print("🎊 GREAT: >90% pass rate achieved!")
        elif success_rate >= 80:
            print("👍 GOOD: >80% pass rate achieved!")
        else:
            print("⚠️  NEEDS WORK: <80% pass rate")
        
        print(f"\n📁 Test result files: test_results_group*.xml")
        print("=" * 60)

async def main():
    """Main execution function."""
    runner = TestRunner()
    await runner.run_all_groups()

if __name__ == "__main__":
    # Run the async test execution
    asyncio.run(main())
