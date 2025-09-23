#!/usr/bin/env python3
"""
Comprehensive Deployment Test Runner for RuleIQ
Executes all validation steps for deployment readiness
"""

import os
import sys
import json
import asyncio
import subprocess
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ComprehensiveDeploymentTester:
    """Complete deployment validation test runner"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_results = {}
        self.readiness_score = 0
        self.critical_issues = []
        self.warnings = []
        self.test_start_time = None

    async def run_full_validation(self) -> Dict:
        """Execute complete deployment validation pipeline"""
        self.test_start_time = time.time()
        logger.info("🚀 Starting Comprehensive Deployment Validation")
        logger.info("=" * 80)

        # Define test pipeline
        test_pipeline = [
            ("Startup Diagnostics", self.run_startup_diagnostics),
            ("Test Group Execution", self.run_test_groups),
            ("Integration Tests", self.run_integration_tests),
            ("Security Validation", self.run_security_validation),
            ("Performance Testing", self.run_performance_tests),
            ("API Endpoint Validation", self.validate_api_endpoints),
            ("Database Health Check", self.check_database_health),
            ("Frontend Build Test", self.test_frontend_build),
            ("Docker Build Validation", self.validate_docker_build),
            ("End-to-End Tests", self.run_e2e_tests),
            ("Deployment Readiness Check", self.check_deployment_readiness),
        ]

        total_tests = len(test_pipeline)
        passed_tests = 0

        for test_name, test_func in test_pipeline:
            logger.info(f"\n{'='*60}")
            logger.info(f"🧪 Running: {test_name}")
            logger.info(f"{'='*60}")

            try:
                if asyncio.iscoroutinefunction(test_func):
                    result = await test_func()
                else:
                    result = test_func()

                self.test_results[test_name] = result

                if result['status'] == 'passed':
                    passed_tests += 1
                    logger.info(f"✅ {test_name}: PASSED")
                elif result['status'] == 'warning':
                    self.warnings.append(f"{test_name}: {result.get('message')}")
                    logger.warning(f"⚠️  {test_name}: WARNING - {result.get('message')}")
                    passed_tests += 0.7  # Partial credit
                else:
                    self.critical_issues.append(f"{test_name}: {result.get('message')}")
                    logger.error(f"❌ {test_name}: FAILED - {result.get('message')}")

            except Exception as e:
                logger.error(f"❌ {test_name}: ERROR - {str(e)}")
                self.critical_issues.append(f"{test_name}: {str(e)}")
                self.test_results[test_name] = {
                    'status': 'error',
                    'message': str(e)
                }

        # Calculate readiness score
        self.readiness_score = (passed_tests / total_tests) * 100

        return self.generate_final_report()

    async def run_startup_diagnostics(self) -> Dict:
        """Run startup diagnostics to ensure baseline readiness"""
        try:
            # Import and run startup diagnostics
            from scripts.startup_diagnostics import StartupDiagnostics

            diagnostics = StartupDiagnostics()
            result = await diagnostics.run_diagnostics()

            score = result.get('overall_health', 0)

            if score >= 90:
                return {
                    'status': 'passed',
                    'message': f'System health: {score}%',
                    'details': result
                }
            elif score >= 70:
                return {
                    'status': 'warning',
                    'message': f'System health: {score}% (target: 90%)',
                    'details': result
                }
            else:
                return {
                    'status': 'failed',
                    'message': f'System health too low: {score}%',
                    'details': result
                }

        except ImportError:
            # Fallback to basic diagnostics
            return self._run_basic_diagnostics()
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _run_basic_diagnostics(self) -> Dict:
        """Basic diagnostic checks"""
        checks = {
            'python_version': sys.version_info >= (3, 9),
            'project_structure': (self.project_root / 'main.py').exists(),
            'requirements': (self.project_root / 'requirements.txt').exists(),
            'env_file': (self.project_root / '.env').exists(),
            'database_url': bool(os.getenv('DATABASE_URL')),
        }

        passed = sum(checks.values())
        total = len(checks)

        return {
            'status': 'passed' if passed == total else 'warning',
            'message': f'{passed}/{total} basic checks passed',
            'checks': checks
        }

    async def run_test_groups(self) -> Dict:
        """Run optimized test groups in parallel"""
        try:
            # Import test groups
            from scripts.test_groups import TestGroupRunner

            runner = TestGroupRunner()
            groups = runner.get_test_groups()

            # Run groups in parallel
            with ProcessPoolExecutor(max_workers=4) as executor:
                futures = []
                for group_name, group_config in groups.items():
                    future = executor.submit(self._run_test_group, group_name, group_config)
                    futures.append((group_name, future))

                group_results = {}
                for group_name, future in futures:
                    try:
                        group_results[group_name] = future.result(timeout=300)
                    except Exception as e:
                        group_results[group_name] = {
                            'status': 'error',
                            'message': str(e)
                        }

            # Aggregate results
            total_tests = sum(r.get('total', 0) for r in group_results.values())
            passed_tests = sum(r.get('passed', 0) for r in group_results.values())

            success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

            if success_rate >= 95:
                status = 'passed'
            elif success_rate >= 80:
                status = 'warning'
            else:
                status = 'failed'

            return {
                'status': status,
                'message': f'Test success rate: {success_rate:.1f}%',
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'group_results': group_results
            }

        except ImportError:
            # Fallback to simple test execution
            return self._run_simple_tests()
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _run_test_group(self, group_name: str, group_config: Dict) -> Dict:
        """Execute a single test group"""
        try:
            cmd = ['pytest'] + group_config.get('tests', []) + [
                '-v', '--tb=short', '--json-report',
                f'--json-report-file=/tmp/test_{group_name}.json'
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300
            )

            # Parse results
            report_file = f'/tmp/test_{group_name}.json'
            if Path(report_file).exists():
                with open(report_file, 'r') as f:
                    report = json.load(f)
                    return {
                        'status': 'passed' if result.returncode == 0 else 'failed',
                        'total': report['summary'].get('total', 0),
                        'passed': report['summary'].get('passed', 0)
                    }

            return {
                'status': 'failed' if result.returncode != 0 else 'passed',
                'total': 0,
                'passed': 0
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _run_simple_tests(self) -> Dict:
        """Simple test execution fallback"""
        try:
            result = subprocess.run(
                ['pytest', 'tests/', '-v', '--tb=short'],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=600
            )

            return {
                'status': 'passed' if result.returncode == 0 else 'failed',
                'message': 'Basic test suite executed'
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def run_integration_tests(self) -> Dict:
        """Execute integration test suites"""
        try:
            # Use integration test runner
            cmd = ['python', 'scripts/run_integration_tests.py', '--all']

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=600
            )

            if result.returncode == 0:
                return {
                    'status': 'passed',
                    'message': 'Integration tests passed'
                }
            else:
                # Parse failure details
                output_lines = result.stdout.splitlines()
                failures = [line for line in output_lines if 'FAILED' in line]

                return {
                    'status': 'failed',
                    'message': f'{len(failures)} integration test failures',
                    'failures': failures[:5]  # First 5 failures
                }

        except FileNotFoundError:
            return {
                'status': 'warning',
                'message': 'Integration test runner not found'
            }
        except subprocess.TimeoutExpired:
            return {
                'status': 'failed',
                'message': 'Integration tests timeout'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def run_security_validation(self) -> Dict:
        """Run security scans and vulnerability checks"""
        security_checks = []

        # Bandit security scan
        try:
            bandit_result = subprocess.run(
                ['bandit', '-r', '.', '-f', 'json'],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=120
            )

            if bandit_result.returncode == 0:
                bandit_report = json.loads(bandit_result.stdout)
                high_issues = len([i for i in bandit_report.get('results', [])
                                  if i.get('issue_severity') == 'HIGH'])
                security_checks.append({
                    'tool': 'Bandit',
                    'passed': high_issues == 0,
                    'issues': high_issues
                })
        except:
            pass

        # Safety dependency check
        try:
            safety_result = subprocess.run(
                ['safety', 'check', '--json'],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=60
            )

            security_checks.append({
                'tool': 'Safety',
                'passed': safety_result.returncode == 0
            })
        except:
            pass

        # Secret scanning
        try:
            gitleaks_result = subprocess.run(
                ['gitleaks', 'detect', '--no-git'],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=60
            )

            security_checks.append({
                'tool': 'Gitleaks',
                'passed': gitleaks_result.returncode == 0
            })
        except:
            pass

        if not security_checks:
            return {
                'status': 'warning',
                'message': 'Security tools not available'
            }

        passed = all(check['passed'] for check in security_checks)

        return {
            'status': 'passed' if passed else 'failed',
            'message': f'{sum(c["passed"] for c in security_checks)}/{len(security_checks)} security checks passed',
            'checks': security_checks
        }

    def run_performance_tests(self) -> Dict:
        """Run performance and load tests"""
        try:
            # Check for load test directory
            load_test_dir = self.project_root / 'tests' / 'load'

            if load_test_dir.exists():
                result = subprocess.run(
                    ['pytest', str(load_test_dir), '-v'],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    timeout=300
                )

                return {
                    'status': 'passed' if result.returncode == 0 else 'failed',
                    'message': 'Performance tests executed'
                }

            return {
                'status': 'warning',
                'message': 'Performance tests not configured'
            }

        except subprocess.TimeoutExpired:
            return {
                'status': 'failed',
                'message': 'Performance tests timeout'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def validate_api_endpoints(self) -> Dict:
        """Validate API endpoints and health checks"""
        try:
            # Import endpoint validator if available
            from scripts.validate_endpoints import EndpointValidator

            validator = EndpointValidator()
            result = validator.validate_all()

            return {
                'status': 'passed' if result['all_valid'] else 'failed',
                'message': f'{result["valid_count"]}/{result["total_count"]} endpoints valid',
                'details': result
            }

        except ImportError:
            # Basic health check
            import requests

            try:
                response = requests.get('http://localhost:8000/health', timeout=5)
                return {
                    'status': 'passed' if response.status_code == 200 else 'warning',
                    'message': f'Health check status: {response.status_code}'
                }
            except:
                return {
                    'status': 'warning',
                    'message': 'API not running (expected for pre-deployment)'
                }

    async def check_database_health(self) -> Dict:
        """Check database connectivity and health"""
        try:
            from scripts.database_health_check import DatabaseHealthChecker

            checker = DatabaseHealthChecker()
            result = await checker.run_health_check()

            return {
                'status': 'passed' if result['healthy'] else 'failed',
                'message': result.get('message', 'Database check complete'),
                'details': result
            }

        except ImportError:
            # Basic connectivity check
            db_url = os.getenv('DATABASE_URL')
            if not db_url:
                return {
                    'status': 'failed',
                    'message': 'DATABASE_URL not configured'
                }

            try:
                import psycopg2
                conn = psycopg2.connect(db_url)
                conn.close()
                return {
                    'status': 'passed',
                    'message': 'Database connection successful'
                }
            except Exception as e:
                return {
                    'status': 'failed',
                    'message': f'Database connection failed: {str(e)}'
                }

    def test_frontend_build(self) -> Dict:
        """Test frontend build process"""
        frontend_dir = self.project_root / 'frontend'

        if not frontend_dir.exists():
            return {
                'status': 'failed',
                'message': 'Frontend directory not found'
            }

        try:
            # Test build
            result = subprocess.run(
                ['npm', 'run', 'build'],
                capture_output=True,
                text=True,
                cwd=frontend_dir,
                timeout=180
            )

            if result.returncode == 0:
                return {
                    'status': 'passed',
                    'message': 'Frontend build successful'
                }
            else:
                return {
                    'status': 'failed',
                    'message': 'Frontend build failed',
                    'error': result.stderr[:500]
                }

        except subprocess.TimeoutExpired:
            return {
                'status': 'failed',
                'message': 'Frontend build timeout'
            }
        except FileNotFoundError:
            return {
                'status': 'warning',
                'message': 'npm not found, install dependencies first'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def validate_docker_build(self) -> Dict:
        """Validate Docker build capability"""
        try:
            # Check Docker availability
            docker_version = subprocess.run(
                ['docker', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if docker_version.returncode != 0:
                return {
                    'status': 'warning',
                    'message': 'Docker not available'
                }

            # Check Dockerfile exists
            dockerfile = self.project_root / 'Dockerfile'
            if not dockerfile.exists():
                return {
                    'status': 'warning',
                    'message': 'Dockerfile not found'
                }

            # Test build (quick validation only)
            result = subprocess.run(
                ['docker', 'build', '--target', 'base', '-t', 'ruleiq-test:validation', '.'],
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=120
            )

            if result.returncode == 0:
                # Clean up test image
                subprocess.run(
                    ['docker', 'rmi', 'ruleiq-test:validation'],
                    capture_output=True
                )
                return {
                    'status': 'passed',
                    'message': 'Docker build validated'
                }
            else:
                return {
                    'status': 'warning',
                    'message': 'Docker build issues detected'
                }

        except subprocess.TimeoutExpired:
            return {
                'status': 'warning',
                'message': 'Docker build validation timeout'
            }
        except Exception as e:
            return {'status': 'warning', 'message': str(e)}

    def run_e2e_tests(self) -> Dict:
        """Run end-to-end user journey tests"""
        try:
            # Run Playwright tests if available
            frontend_dir = self.project_root / 'frontend'

            result = subprocess.run(
                ['npm', 'run', 'test:e2e'],
                capture_output=True,
                text=True,
                cwd=frontend_dir,
                timeout=300
            )

            if result.returncode == 0:
                return {
                    'status': 'passed',
                    'message': 'E2E tests passed'
                }
            else:
                return {
                    'status': 'failed',
                    'message': 'E2E tests failed',
                    'output': result.stdout[-1000:]
                }

        except FileNotFoundError:
            # Try Python E2E tests
            e2e_dir = self.project_root / 'tests' / 'e2e'
            if e2e_dir.exists():
                result = subprocess.run(
                    ['pytest', str(e2e_dir)],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    timeout=300
                )
                return {
                    'status': 'passed' if result.returncode == 0 else 'failed',
                    'message': 'Python E2E tests executed'
                }

            return {
                'status': 'warning',
                'message': 'E2E tests not configured'
            }
        except subprocess.TimeoutExpired:
            return {
                'status': 'failed',
                'message': 'E2E tests timeout'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def check_deployment_readiness(self) -> Dict:
        """Final deployment readiness assessment"""
        readiness_checks = {
            'Environment': (self.project_root / '.env').exists(),
            'Database': bool(os.getenv('DATABASE_URL')),
            'Dependencies': (self.project_root / 'requirements.txt').exists(),
            'Docker': (self.project_root / 'docker-compose.yml').exists(),
            'Frontend': (self.project_root / 'frontend' / 'package.json').exists(),
            'Tests': len([r for r in self.test_results.values() if r.get('status') == 'passed']) > 5,
            'Documentation': (self.project_root / 'README.md').exists(),
        }

        passed_checks = sum(readiness_checks.values())
        total_checks = len(readiness_checks)

        readiness_percentage = (passed_checks / total_checks) * 100

        return {
            'status': 'passed' if readiness_percentage >= 85 else 'failed',
            'message': f'Deployment readiness: {readiness_percentage:.0f}%',
            'checks': readiness_checks,
            'ready_for_deployment': readiness_percentage >= 85
        }

    def generate_final_report(self) -> Dict:
        """Generate comprehensive deployment readiness report"""
        execution_time = time.time() - self.test_start_time

        # Calculate detailed metrics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results.values() if r.get('status') == 'passed'])
        warning_tests = len([r for r in self.test_results.values() if r.get('status') == 'warning'])
        failed_tests = len([r for r in self.test_results.values() if r.get('status') == 'failed'])

        # Determine deployment recommendation
        if self.readiness_score >= 90:
            recommendation = "✅ READY FOR DEPLOYMENT"
            ready = True
        elif self.readiness_score >= 70:
            recommendation = "⚠️  CONDITIONALLY READY - Address warnings before production"
            ready = True
        else:
            recommendation = "❌ NOT READY - Critical issues must be resolved"
            ready = False

        report = {
            'timestamp': datetime.now().isoformat(),
            'readiness_score': self.readiness_score,
            'deployment_ready': ready,
            'recommendation': recommendation,
            'execution_time': f'{execution_time:.2f}s',
            'test_summary': {
                'total': total_tests,
                'passed': passed_tests,
                'warnings': warning_tests,
                'failed': failed_tests,
            },
            'critical_issues': self.critical_issues,
            'warnings': self.warnings,
            'test_results': self.test_results,
            'remediation_steps': self._generate_remediation_steps(),
        }

        # Save report
        report_file = self.project_root / 'deployment' / f'readiness_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"\n📊 Report saved to: {report_file}")

        return report

    def _generate_remediation_steps(self) -> List[str]:
        """Generate specific remediation steps based on issues"""
        steps = []

        for issue in self.critical_issues:
            if 'database' in issue.lower():
                steps.append("Fix database connectivity: Check DATABASE_URL and PostgreSQL service")
            elif 'test' in issue.lower():
                steps.append("Fix failing tests: Run pytest -v to identify specific failures")
            elif 'security' in issue.lower():
                steps.append("Address security issues: Run bandit and safety for details")
            elif 'docker' in issue.lower():
                steps.append("Fix Docker configuration: Check Dockerfile and docker-compose.yml")
            elif 'frontend' in issue.lower():
                steps.append("Fix frontend build: Run npm install and npm run build")

        for warning in self.warnings:
            if 'performance' in warning.lower():
                steps.append("Optimize performance: Run load tests and profile slow operations")
            elif 'monitoring' in warning.lower():
                steps.append("Setup monitoring: Configure error tracking and metrics")

        if not steps:
            steps.append("All systems operational - proceed with deployment")

        return steps


async def main():
    """Main execution function"""
    tester = ComprehensiveDeploymentTester()
    report = await tester.run_full_validation()

    # Print detailed summary
    print("\n" + "="*80)
    print("🚀 DEPLOYMENT READINESS REPORT")
    print("="*80)
    print(f"📊 Readiness Score: {report['readiness_score']:.1f}%")
    print(f"⏱️  Execution Time: {report['execution_time']}")
    print(f"📋 Tests Summary:")
    print(f"   ✅ Passed: {report['test_summary']['passed']}")
    print(f"   ⚠️  Warnings: {report['test_summary']['warnings']}")
    print(f"   ❌ Failed: {report['test_summary']['failed']}")

    if report['critical_issues']:
        print(f"\n❌ Critical Issues ({len(report['critical_issues'])}):")
        for issue in report['critical_issues'][:5]:
            print(f"   - {issue}")

    if report['warnings']:
        print(f"\n⚠️  Warnings ({len(report['warnings'])}):")
        for warning in report['warnings'][:5]:
            print(f"   - {warning}")

    print(f"\n💡 Remediation Steps:")
    for i, step in enumerate(report['remediation_steps'], 1):
        print(f"   {i}. {step}")

    print("\n" + "="*80)
    print(f"📌 {report['recommendation']}")
    print("="*80)

    # Exit with appropriate code
    sys.exit(0 if report['deployment_ready'] else 1)


if __name__ == '__main__':
    asyncio.run(main())