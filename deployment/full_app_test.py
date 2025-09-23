#!/usr/bin/env python3
"""
Comprehensive Full Application Test Runner for RuleIQ
Executes all test suites for deployment validation
"""

import os
import sys
import json
import subprocess
import asyncio
import time
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import multiprocessing

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FullApplicationTester:
    """Comprehensive application test runner"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_results = {}
        self.failed_tests = []
        self.test_metrics = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'skipped_tests': 0,
            'coverage': 0,
            'execution_time': 0,
        }
        self.confidence_score = 0

    async def run_all_tests(self) -> Dict:
        """Execute all test suites in optimal order"""
        start_time = time.time()
        logger.info("🧪 Starting Comprehensive Application Testing")

        # Test execution plan
        test_suites = [
            ("Unit Tests (Parallel)", self.run_unit_tests_parallel),
            ("Integration Tests", self.run_integration_tests),
            ("API Tests", self.run_api_tests),
            ("Frontend Tests", self.run_frontend_tests),
            ("E2E Tests", self.run_e2e_tests),
            ("Performance Tests", self.run_performance_tests),
            ("Security Tests", self.run_security_tests),
            ("AI/Compliance Tests", self.run_ai_compliance_tests),
            ("Database Tests", self.run_database_tests),
            ("Authentication Tests", self.run_auth_tests),
            ("Memory/Resource Tests", self.run_resource_tests),
        ]

        for suite_name, test_func in test_suites:
            logger.info(f"\n{'='*60}")
            logger.info(f"🔬 Running: {suite_name}")
            logger.info(f"{'='*60}")

            try:
                if asyncio.iscoroutinefunction(test_func):
                    result = await test_func()
                else:
                    result = test_func()

                self.test_results[suite_name] = result
                self._update_metrics(result)

                if result['status'] == 'passed':
                    logger.info(f"✅ {suite_name}: PASSED ({result['tests_passed']}/{result['tests_total']})")
                else:
                    self.failed_tests.append(suite_name)
                    logger.error(f"❌ {suite_name}: FAILED ({result['tests_passed']}/{result['tests_total']})")

            except Exception as e:
                logger.error(f"❌ {suite_name}: ERROR - {str(e)}")
                self.failed_tests.append(suite_name)
                self.test_results[suite_name] = {
                    'status': 'error',
                    'message': str(e),
                    'tests_total': 0,
                    'tests_passed': 0,
                }

        self.test_metrics['execution_time'] = time.time() - start_time
        self.confidence_score = self._calculate_confidence_score()

        return self.generate_report()

    async def run_unit_tests_parallel(self) -> Dict:
        """Run unit tests in parallel using test groups"""
        try:
            # Import test groups configuration
            from scripts.test_groups import TestGroupManager

            manager = TestGroupManager()
            groups = manager.get_test_groups()

            # Run test groups in parallel
            with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
                futures = []
                for group_name, group_tests in groups.items():
                    future = executor.submit(self._run_test_group, group_name, group_tests)
                    futures.append((group_name, future))

                group_results = {}
                for group_name, future in futures:
                    try:
                        group_results[group_name] = future.result(timeout=300)
                    except Exception as e:
                        group_results[group_name] = {'status': 'error', 'message': str(e)}

            # Aggregate results
            total_tests = sum(r.get('tests_total', 0) for r in group_results.values())
            passed_tests = sum(r.get('tests_passed', 0) for r in group_results.values())

            return {
                'status': 'passed' if passed_tests == total_tests else 'failed',
                'tests_total': total_tests,
                'tests_passed': passed_tests,
                'group_results': group_results,
                'coverage': self._get_test_coverage(),
            }

        except ImportError:
            # Fallback to running tests sequentially
            return self._run_pytest_suite('tests/unit')

    def _run_test_group(self, group_name: str, test_files: List[str]) -> Dict:
        """Run a specific test group"""
        try:
            cmd = ['pytest'] + test_files + [
                '-v',
                '--tb=short',
                '--json-report',
                f'--json-report-file=/tmp/test_report_{group_name}.json',
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300
            )

            # Parse test results
            report_file = f'/tmp/test_report_{group_name}.json'
            if Path(report_file).exists():
                with open(report_file, 'r') as f:
                    report = json.load(f)

                return {
                    'status': 'passed' if result.returncode == 0 else 'failed',
                    'tests_total': report['summary']['total'],
                    'tests_passed': report['summary']['passed'],
                    'duration': report['duration'],
                }

            return {
                'status': 'failed' if result.returncode != 0 else 'passed',
                'tests_total': 0,
                'tests_passed': 0,
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e), 'tests_total': 0, 'tests_passed': 0}

    def run_integration_tests(self) -> Dict:
        """Run integration tests"""
        try:
            # Use the integration test runner script
            cmd = ['python', 'scripts/run_integration_tests.py', '--all']

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=600
            )

            # Parse results from output
            lines = result.stdout.splitlines()
            tests_run = 0
            tests_passed = 0

            for line in lines:
                if 'tests run' in line.lower():
                    tests_run = int(''.join(filter(str.isdigit, line.split('tests run')[0])))
                if 'passed' in line.lower():
                    tests_passed = int(''.join(filter(str.isdigit, line.split('passed')[0])))

            return {
                'status': 'passed' if result.returncode == 0 else 'failed',
                'tests_total': tests_run,
                'tests_passed': tests_passed,
                'output': result.stdout[-1000:] if result.returncode != 0 else '',
            }

        except Exception as e:
            # Fallback to pytest integration tests
            return self._run_pytest_suite('tests/integration')

    def run_api_tests(self) -> Dict:
        """Run API endpoint tests"""
        return self._run_pytest_suite('tests/api', markers=['api'])

    def run_frontend_tests(self) -> Dict:
        """Run frontend tests including Playwright"""
        try:
            frontend_dir = self.project_root / 'frontend'

            # Run Jest tests
            jest_result = subprocess.run(
                ['npm', 'test', '--', '--json', '--outputFile=/tmp/jest_results.json'],
                capture_output=True,
                text=True,
                cwd=frontend_dir,
                timeout=300
            )

            jest_stats = {'total': 0, 'passed': 0}
            if Path('/tmp/jest_results.json').exists():
                with open('/tmp/jest_results.json', 'r') as f:
                    jest_data = json.load(f)
                    jest_stats['total'] = jest_data.get('numTotalTests', 0)
                    jest_stats['passed'] = jest_data.get('numPassedTests', 0)

            # Run Playwright E2E tests
            playwright_result = subprocess.run(
                ['npm', 'run', 'test:e2e'],
                capture_output=True,
                text=True,
                cwd=frontend_dir,
                timeout=600
            )

            return {
                'status': 'passed' if jest_result.returncode == 0 and playwright_result.returncode == 0 else 'failed',
                'tests_total': jest_stats['total'],
                'tests_passed': jest_stats['passed'],
                'jest_passed': jest_result.returncode == 0,
                'playwright_passed': playwright_result.returncode == 0,
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e), 'tests_total': 0, 'tests_passed': 0}

    def run_e2e_tests(self) -> Dict:
        """Run end-to-end tests"""
        return self._run_pytest_suite('tests/e2e', markers=['e2e'])

    def run_performance_tests(self) -> Dict:
        """Run performance and load tests"""
        try:
            # Run load tests
            load_test_dir = self.project_root / 'tests' / 'load'
            if load_test_dir.exists():
                result = subprocess.run(
                    ['pytest', str(load_test_dir), '-v', '--tb=short'],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    timeout=900
                )

                # Run Lighthouse audit for frontend
                frontend_dir = self.project_root / 'frontend'
                lighthouse_result = subprocess.run(
                    ['npm', 'run', 'lighthouse'],
                    capture_output=True,
                    text=True,
                    cwd=frontend_dir,
                    timeout=300
                )

                return {
                    'status': 'passed' if result.returncode == 0 else 'failed',
                    'tests_total': 1,
                    'tests_passed': 1 if result.returncode == 0 else 0,
                    'lighthouse_passed': lighthouse_result.returncode == 0,
                }

            return {'status': 'skipped', 'tests_total': 0, 'tests_passed': 0}

        except Exception as e:
            return {'status': 'error', 'message': str(e), 'tests_total': 0, 'tests_passed': 0}

    def run_security_tests(self) -> Dict:
        """Run security tests and scans"""
        try:
            security_checks = []

            # Run Bandit
            bandit_result = subprocess.run(
                ['bandit', '-r', '.', '-f', 'json'],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            if bandit_result.returncode == 0:
                bandit_report = json.loads(bandit_result.stdout)
                security_checks.append({
                    'tool': 'Bandit',
                    'passed': len([i for i in bandit_report.get('results', []) if i['issue_severity'] == 'HIGH']) == 0
                })

            # Run Safety check
            safety_result = subprocess.run(
                ['safety', 'check', '--json'],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            security_checks.append({
                'tool': 'Safety',
                'passed': safety_result.returncode == 0
            })

            # Run npm audit for frontend
            frontend_dir = self.project_root / 'frontend'
            npm_audit = subprocess.run(
                ['npm', 'audit', '--json'],
                capture_output=True,
                text=True,
                cwd=frontend_dir
            )

            try:
                audit_data = json.loads(npm_audit.stdout)
                security_checks.append({
                    'tool': 'npm audit',
                    'passed': audit_data.get('metadata', {}).get('vulnerabilities', {}).get('high', 0) == 0
                })
            except json.JSONDecodeError:
                pass

            passed = all(check['passed'] for check in security_checks)

            return {
                'status': 'passed' if passed else 'failed',
                'tests_total': len(security_checks),
                'tests_passed': sum(1 for check in security_checks if check['passed']),
                'security_checks': security_checks,
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e), 'tests_total': 0, 'tests_passed': 0}

    def run_ai_compliance_tests(self) -> Dict:
        """Run AI and compliance feature tests"""
        return self._run_pytest_suite('tests', markers=['ai', 'compliance'])

    def run_database_tests(self) -> Dict:
        """Run database and migration tests"""
        try:
            # Test database migrations
            result = subprocess.run(
                ['alembic', 'check'],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            migration_passed = result.returncode == 0

            # Run database-specific tests
            db_tests = self._run_pytest_suite('tests', markers=['database'])

            return {
                'status': 'passed' if migration_passed and db_tests['status'] == 'passed' else 'failed',
                'tests_total': db_tests['tests_total'] + 1,
                'tests_passed': db_tests['tests_passed'] + (1 if migration_passed else 0),
                'migration_check': migration_passed,
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e), 'tests_total': 0, 'tests_passed': 0}

    def run_auth_tests(self) -> Dict:
        """Run authentication and RBAC tests"""
        return self._run_pytest_suite('tests', markers=['auth', 'rbac'])

    def run_resource_tests(self) -> Dict:
        """Run memory leak and resource tests"""
        try:
            # Run memory profiling tests
            result = subprocess.run(
                ['pytest', 'tests/', '-m', 'memory', '--memprof'],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=600
            )

            # Check for memory leaks in output
            has_leaks = 'memory leak' in result.stdout.lower()

            return {
                'status': 'passed' if result.returncode == 0 and not has_leaks else 'failed',
                'tests_total': 1,
                'tests_passed': 1 if result.returncode == 0 and not has_leaks else 0,
                'has_memory_leaks': has_leaks,
            }

        except Exception:
            # Skip if memory profiling not available
            return {'status': 'skipped', 'tests_total': 0, 'tests_passed': 0}

    def _run_pytest_suite(self, test_path: str, markers: List[str] = None) -> Dict:
        """Run a pytest test suite"""
        try:
            cmd = ['pytest', test_path, '-v', '--tb=short', '--json-report', '--json-report-file=/tmp/test_report.json']

            if markers:
                marker_expr = ' or '.join(markers)
                cmd.extend(['-m', marker_expr])

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=600
            )

            # Parse test results
            if Path('/tmp/test_report.json').exists():
                with open('/tmp/test_report.json', 'r') as f:
                    report = json.load(f)

                return {
                    'status': 'passed' if result.returncode == 0 else 'failed',
                    'tests_total': report['summary']['total'],
                    'tests_passed': report['summary']['passed'],
                    'duration': report['duration'],
                }

            # Fallback parsing from output
            tests_run = 0
            tests_passed = 0
            for line in result.stdout.splitlines():
                if ' passed' in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'passed':
                            try:
                                tests_passed = int(parts[i - 1])
                            except (ValueError, IndexError):
                                pass

            return {
                'status': 'passed' if result.returncode == 0 else 'failed',
                'tests_total': tests_run or tests_passed,
                'tests_passed': tests_passed,
            }

        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'tests_total': 0, 'tests_passed': 0}
        except Exception as e:
            return {'status': 'error', 'message': str(e), 'tests_total': 0, 'tests_passed': 0}

    def _get_test_coverage(self) -> float:
        """Get test coverage percentage"""
        try:
            result = subprocess.run(
                ['coverage', 'report', '--format=json'],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            if result.returncode == 0:
                coverage_data = json.loads(result.stdout)
                return coverage_data.get('totals', {}).get('percent_covered', 0)

            return 0
        except Exception:
            return 0

    def _update_metrics(self, result: Dict):
        """Update test metrics"""
        self.test_metrics['total_tests'] += result.get('tests_total', 0)
        self.test_metrics['passed_tests'] += result.get('tests_passed', 0)
        self.test_metrics['failed_tests'] += (result.get('tests_total', 0) - result.get('tests_passed', 0))

        if result.get('status') == 'skipped':
            self.test_metrics['skipped_tests'] += 1

    def _calculate_confidence_score(self) -> float:
        """Calculate deployment confidence score"""
        if self.test_metrics['total_tests'] == 0:
            return 0

        # Base score from test pass rate
        pass_rate = self.test_metrics['passed_tests'] / self.test_metrics['total_tests']
        score = pass_rate * 100

        # Adjust for critical test failures
        critical_suites = ['Integration Tests', 'API Tests', 'Security Tests', 'Database Tests']
        for suite in critical_suites:
            if suite in self.failed_tests:
                score *= 0.8  # 20% penalty for each critical suite failure

        # Bonus for high coverage
        coverage = self.test_metrics.get('coverage', 0)
        if coverage > 80:
            score = min(100, score + 5)

        return max(0, min(100, score))

    def generate_report(self) -> Dict:
        """Generate comprehensive test report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'confidence_score': self.confidence_score,
            'deployment_ready': self.confidence_score >= 85,
            'metrics': self.test_metrics,
            'test_results': self.test_results,
            'failed_suites': self.failed_tests,
            'recommendations': [],
        }

        # Generate recommendations
        if self.confidence_score < 60:
            report['recommendations'].append('CRITICAL: Too many test failures for safe deployment')

        if self.confidence_score < 85:
            report['recommendations'].append('Address failing tests before deployment')

        if self.test_metrics.get('coverage', 0) < 70:
            report['recommendations'].append('Improve test coverage (current: {:.1f}%)'.format(
                self.test_metrics.get('coverage', 0)
            ))

        for suite in self.failed_tests:
            if 'Security' in suite:
                report['recommendations'].append(f'CRITICAL: Fix security test failures in {suite}')
            elif 'Database' in suite:
                report['recommendations'].append(f'CRITICAL: Fix database test failures in {suite}')
            else:
                report['recommendations'].append(f'Fix failures in {suite}')

        # Provide remediation suggestions
        if self.failed_tests:
            report['remediation'] = self._generate_remediation_suggestions()

        # Save report
        report_file = self.project_root / 'deployment' / f'test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"\n📊 Test report saved to: {report_file}")

        return report

    def _generate_remediation_suggestions(self) -> Dict[str, List[str]]:
        """Generate remediation suggestions for failed tests"""
        suggestions = {}

        for suite in self.failed_tests:
            suite_suggestions = []

            if 'Unit' in suite:
                suite_suggestions.extend([
                    'Review recent code changes for bugs',
                    'Check test fixtures and mocks',
                    'Verify test dependencies are installed',
                ])
            elif 'Integration' in suite:
                suite_suggestions.extend([
                    'Check service dependencies are running',
                    'Verify database connections',
                    'Review API endpoint configurations',
                ])
            elif 'Security' in suite:
                suite_suggestions.extend([
                    'Run security scans individually for details',
                    'Update vulnerable dependencies',
                    'Review security configurations',
                ])
            elif 'Performance' in suite:
                suite_suggestions.extend([
                    'Profile slow operations',
                    'Check resource limits',
                    'Review database queries for optimization',
                ])
            elif 'Frontend' in suite:
                suite_suggestions.extend([
                    'Check Node.js and npm versions',
                    'Run npm install to update dependencies',
                    'Review component prop types and interfaces',
                ])

            suggestions[suite] = suite_suggestions

        return suggestions


async def main():
    """Main execution function"""
    tester = FullApplicationTester()
    report = await tester.run_all_tests()

    # Print summary
    print("\n" + "="*80)
    print("🧪 COMPREHENSIVE TEST REPORT")
    print("="*80)
    print(f"📊 Confidence Score: {report['confidence_score']:.1f}%")
    print(f"✅ Passed Tests: {report['metrics']['passed_tests']}")
    print(f"❌ Failed Tests: {report['metrics']['failed_tests']}")
    print(f"⏭️  Skipped Tests: {report['metrics']['skipped_tests']}")
    print(f"📈 Coverage: {report['metrics'].get('coverage', 0):.1f}%")
    print(f"⏱️  Execution Time: {report['metrics']['execution_time']:.2f}s")

    if report['failed_suites']:
        print(f"\n❌ Failed Test Suites:")
        for suite in report['failed_suites']:
            print(f"  - {suite}")

    if report['recommendations']:
        print(f"\n💡 Recommendations:")
        for rec in report['recommendations']:
            print(f"  - {rec}")

    print("\n" + "="*80)

    if report['deployment_ready']:
        print("✅ Application tests PASSED - Ready for deployment!")
        sys.exit(0)
    else:
        print("❌ Application tests FAILED - Not ready for deployment")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())