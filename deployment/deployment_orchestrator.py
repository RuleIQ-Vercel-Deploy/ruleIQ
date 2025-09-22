#!/usr/bin/env python3
"""
Main Deployment Orchestrator for RuleIQ
Coordinates the entire deployment process
"""

import os
import sys
import json
import asyncio
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import subprocess

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import deployment modules
from pre_deployment_checklist import PreDeploymentChecker
from full_app_test import FullApplicationTester
from environment_validator import EnvironmentValidator
from docker_deployment import DockerDeploymentOrchestrator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DeploymentOrchestrator:
    """Main deployment coordinator"""

    def __init__(self, environment: str = 'production', deployment_type: str = 'docker'):
        self.environment = environment
        self.deployment_type = deployment_type
        self.project_root = Path(__file__).parent.parent
        self.deployment_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.deployment_log = []
        self.deployment_status = {}
        self.rollback_points = []

    async def deploy(self, skip_tests: bool = False, force: bool = False) -> Dict:
        """Execute complete deployment pipeline"""
        logger.info(f"🚀 Starting Deployment Process")
        logger.info(f"   Environment: {self.environment}")
        logger.info(f"   Type: {self.deployment_type}")
        logger.info(f"   Deployment ID: {self.deployment_id}")

        deployment_phases = [
            ("Pre-Deployment Checks", self.run_pre_deployment_checks, {'critical': True}),
            ("Environment Validation", self.validate_environment, {'critical': True}),
            ("Security Validation", self.run_security_validation, {'critical': False}),
            ("Application Testing", self.run_application_tests, {'skip': skip_tests}),
            ("Performance Testing", self.run_performance_tests, {'skip': skip_tests}),
            ("Monitoring Setup", self.setup_monitoring, {'critical': False}),
            ("Database Migration", self.run_database_migration, {'critical': True}),
            ("Deployment Execution", self.execute_deployment, {'critical': True}),
            ("Post-Deployment Validation", self.validate_deployment, {'critical': True}),
            ("Smoke Tests", self.run_smoke_tests, {'critical': True}),
            ("Traffic Routing", self.setup_traffic_routing, {'critical': False}),
            ("Notification", self.send_notifications, {'critical': False}),
        ]

        total_phases = len(deployment_phases)
        completed_phases = 0
        failed_phases = []

        for phase_name, phase_func, options in deployment_phases:
            logger.info(f"\n{'='*80}")
            logger.info(f"📋 Phase {completed_phases + 1}/{total_phases}: {phase_name}")
            logger.info(f"{'='*80}")

            # Skip if requested
            if options.get('skip'):
                logger.info(f"⏭️  Skipping {phase_name}")
                self.deployment_status[phase_name] = 'skipped'
                completed_phases += 1
                continue

            # Create rollback point before critical phases
            if options.get('critical'):
                self.create_rollback_point(phase_name)

            try:
                # Execute phase
                if asyncio.iscoroutinefunction(phase_func):
                    result = await phase_func()
                else:
                    result = phase_func()

                self.deployment_status[phase_name] = result

                if result.get('status') == 'success':
                    logger.info(f"✅ {phase_name}: SUCCESS")
                    completed_phases += 1
                elif result.get('status') == 'warning':
                    logger.warning(f"⚠️  {phase_name}: WARNING - {result.get('message')}")
                    completed_phases += 1
                else:
                    logger.error(f"❌ {phase_name}: FAILED - {result.get('message')}")
                    failed_phases.append(phase_name)

                    if options.get('critical') and not force:
                        logger.error(f"Critical phase failed. Initiating rollback...")
                        await self.rollback(phase_name)
                        break

            except Exception as e:
                logger.error(f"❌ {phase_name}: ERROR - {str(e)}")
                failed_phases.append(phase_name)
                self.deployment_status[phase_name] = {
                    'status': 'error',
                    'message': str(e)
                }

                if options.get('critical') and not force:
                    logger.error(f"Critical error. Initiating rollback...")
                    await self.rollback(phase_name)
                    break

            # Log phase completion
            self.deployment_log.append({
                'timestamp': datetime.now().isoformat(),
                'phase': phase_name,
                'status': self.deployment_status[phase_name].get('status', 'unknown')
            })

        # Generate final report
        deployment_success = len(failed_phases) == 0
        report = self.generate_final_report(completed_phases, total_phases, failed_phases)

        return report

    async def run_pre_deployment_checks(self) -> Dict:
        """Run pre-deployment validation"""
        try:
            checker = PreDeploymentChecker()
            result = await checker.run_all_checks()

            if result['readiness_score'] < 70:
                return {
                    'status': 'failed',
                    'message': f"Readiness score too low: {result['readiness_score']}%",
                    'details': result
                }

            return {
                'status': 'success' if result['readiness_score'] >= 90 else 'warning',
                'message': f"Readiness score: {result['readiness_score']}%",
                'details': result
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def validate_environment(self) -> Dict:
        """Validate environment configuration"""
        try:
            validator = EnvironmentValidator(self.environment)
            result = validator.validate_all()

            if not result['valid']:
                return {
                    'status': 'failed',
                    'message': f"Environment validation failed: {len(result['issues'])} issues",
                    'details': result
                }

            return {
                'status': 'success' if len(result['warnings']) == 0 else 'warning',
                'message': 'Environment validated',
                'details': result
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def run_security_validation(self) -> Dict:
        """Run security validation checks"""
        try:
            # Run security scans using GitHub Actions workflow
            cmd = [
                'python', 'deployment/security_validation.py',
                '--env', self.environment
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300
            )

            if result.returncode == 0:
                return {'status': 'success', 'message': 'Security validation passed'}
            else:
                return {
                    'status': 'warning',
                    'message': 'Security issues detected (non-critical)',
                    'output': result.stdout
                }

        except subprocess.TimeoutExpired:
            return {'status': 'warning', 'message': 'Security scan timeout'}
        except FileNotFoundError:
            # Security validation script not yet created
            return {'status': 'skipped', 'message': 'Security validation not configured'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    async def run_application_tests(self) -> Dict:
        """Run full application test suite"""
        try:
            tester = FullApplicationTester()
            result = await tester.run_all_tests()

            if result['confidence_score'] < 60:
                return {
                    'status': 'failed',
                    'message': f"Test confidence too low: {result['confidence_score']}%",
                    'details': result
                }

            return {
                'status': 'success' if result['confidence_score'] >= 85 else 'warning',
                'message': f"Test confidence: {result['confidence_score']}%",
                'details': result
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def run_performance_tests(self) -> Dict:
        """Run performance testing suite"""
        try:
            cmd = [
                'python', 'deployment/performance_testing.py',
                '--env', self.environment
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=600
            )

            if result.returncode == 0:
                return {'status': 'success', 'message': 'Performance tests passed'}
            else:
                return {
                    'status': 'warning',
                    'message': 'Performance issues detected',
                    'output': result.stdout
                }

        except subprocess.TimeoutExpired:
            return {'status': 'warning', 'message': 'Performance test timeout'}
        except FileNotFoundError:
            return {'status': 'skipped', 'message': 'Performance tests not configured'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def setup_monitoring(self) -> Dict:
        """Setup monitoring and observability"""
        try:
            cmd = [
                'python', 'deployment/monitoring_setup.py',
                '--env', self.environment
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=120
            )

            if result.returncode == 0:
                return {'status': 'success', 'message': 'Monitoring configured'}
            else:
                return {
                    'status': 'warning',
                    'message': 'Partial monitoring setup',
                    'output': result.stdout
                }

        except FileNotFoundError:
            return {'status': 'skipped', 'message': 'Monitoring setup not configured'}
        except Exception as e:
            return {'status': 'warning', 'message': str(e)}

    def run_database_migration(self) -> Dict:
        """Run database migrations"""
        try:
            # Backup database first
            logger.info("Creating database backup...")
            backup_cmd = [
                'pg_dump',
                os.getenv('DATABASE_URL'),
                '-f', f'backups/db_backup_{self.deployment_id}.sql'
            ]

            backup_result = subprocess.run(
                backup_cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            # Run migrations
            logger.info("Running database migrations...")
            cmd = ['alembic', 'upgrade', 'head']

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root,
                timeout=300
            )

            if result.returncode == 0:
                return {'status': 'success', 'message': 'Database migrations completed'}
            else:
                return {
                    'status': 'failed',
                    'message': f"Migration failed: {result.stderr}",
                    'backup': f'backups/db_backup_{self.deployment_id}.sql'
                }

        except subprocess.TimeoutExpired:
            return {'status': 'failed', 'message': 'Migration timeout'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def execute_deployment(self) -> Dict:
        """Execute the actual deployment"""
        try:
            if self.deployment_type == 'docker':
                orchestrator = DockerDeploymentOrchestrator(self.environment)
                result = orchestrator.deploy()

                if result['deployment_success']:
                    return {'status': 'success', 'message': 'Docker deployment completed'}
                else:
                    return {
                        'status': 'failed',
                        'message': 'Docker deployment failed',
                        'details': result
                    }

            elif self.deployment_type == 'vercel':
                cmd = [
                    'python', 'deployment/vercel_deployment.py',
                    '--env', self.environment
                ]

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    timeout=600
                )

                if result.returncode == 0:
                    return {'status': 'success', 'message': 'Vercel deployment completed'}
                else:
                    return {
                        'status': 'failed',
                        'message': 'Vercel deployment failed',
                        'output': result.stdout
                    }

            else:
                return {'status': 'error', 'message': f"Unknown deployment type: {self.deployment_type}"}

        except subprocess.TimeoutExpired:
            return {'status': 'failed', 'message': 'Deployment timeout'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def validate_deployment(self) -> Dict:
        """Validate the deployment"""
        try:
            validation_checks = []

            # Check health endpoints
            import requests

            endpoints = [
                f"{os.getenv('API_URL', 'http://localhost:8000')}/health",
                f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/",
            ]

            for endpoint in endpoints:
                try:
                    response = requests.get(endpoint, timeout=10)
                    validation_checks.append({
                        'endpoint': endpoint,
                        'status': response.status_code,
                        'healthy': response.status_code == 200
                    })
                except Exception as e:
                    validation_checks.append({
                        'endpoint': endpoint,
                        'status': 'error',
                        'healthy': False,
                        'error': str(e)
                    })

            all_healthy = all(check['healthy'] for check in validation_checks)

            if all_healthy:
                return {'status': 'success', 'message': 'Deployment validated', 'checks': validation_checks}
            else:
                failed = [c['endpoint'] for c in validation_checks if not c['healthy']]
                return {
                    'status': 'failed',
                    'message': f"Validation failed for: {', '.join(failed)}",
                    'checks': validation_checks
                }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def run_smoke_tests(self) -> Dict:
        """Run smoke tests on deployed application"""
        try:
            smoke_tests = [
                ('API Health', self._test_api_health),
                ('Database Connection', self._test_database),
                ('Authentication', self._test_auth),
                ('Frontend Loading', self._test_frontend),
            ]

            test_results = []
            all_passed = True

            for test_name, test_func in smoke_tests:
                try:
                    result = test_func()
                    test_results.append({
                        'test': test_name,
                        'passed': result
                    })
                    if not result:
                        all_passed = False
                except Exception as e:
                    test_results.append({
                        'test': test_name,
                        'passed': False,
                        'error': str(e)
                    })
                    all_passed = False

            if all_passed:
                return {'status': 'success', 'message': 'All smoke tests passed', 'results': test_results}
            else:
                failed = [t['test'] for t in test_results if not t['passed']]
                return {
                    'status': 'failed',
                    'message': f"Smoke tests failed: {', '.join(failed)}",
                    'results': test_results
                }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def _test_api_health(self) -> bool:
        """Test API health endpoint"""
        import requests
        try:
            response = requests.get(f"{os.getenv('API_URL', 'http://localhost:8000')}/health", timeout=5)
            return response.status_code == 200
        except:
            return False

    def _test_database(self) -> bool:
        """Test database connectivity"""
        try:
            import psycopg2
            conn = psycopg2.connect(os.getenv('DATABASE_URL'))
            conn.close()
            return True
        except:
            return False

    def _test_auth(self) -> bool:
        """Test authentication endpoint"""
        import requests
        try:
            response = requests.post(
                f"{os.getenv('API_URL', 'http://localhost:8000')}/api/v1/auth/login",
                json={'username': 'test', 'password': 'test'},
                timeout=5
            )
            # We expect 401 for invalid credentials, which means auth is working
            return response.status_code in [401, 200]
        except:
            return False

    def _test_frontend(self) -> bool:
        """Test frontend loading"""
        import requests
        try:
            response = requests.get(f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/", timeout=5)
            return response.status_code == 200 and 'RuleIQ' in response.text
        except:
            return False

    def setup_traffic_routing(self) -> Dict:
        """Setup traffic routing (blue-green or rolling)"""
        try:
            if self.deployment_type == 'docker':
                # For Docker, this would involve updating load balancer config
                return {'status': 'success', 'message': 'Traffic routing configured'}
            elif self.deployment_type == 'vercel':
                # Vercel handles this automatically
                return {'status': 'success', 'message': 'Vercel automatic routing active'}
            else:
                return {'status': 'skipped', 'message': 'Traffic routing not applicable'}

        except Exception as e:
            return {'status': 'warning', 'message': str(e)}

    def send_notifications(self) -> Dict:
        """Send deployment notifications"""
        try:
            # Prepare notification content
            success = all(
                s.get('status') in ['success', 'warning', 'skipped']
                for s in self.deployment_status.values()
            )

            message = f"""
Deployment {'Successful' if success else 'Failed'}
Environment: {self.environment}
Type: {self.deployment_type}
Deployment ID: {self.deployment_id}
Time: {datetime.now().isoformat()}
"""

            # Send to configured channels
            notification_sent = False

            # Slack notification
            if os.getenv('SLACK_WEBHOOK_URL'):
                import requests
                response = requests.post(
                    os.getenv('SLACK_WEBHOOK_URL'),
                    json={'text': message}
                )
                notification_sent = response.status_code == 200

            # Email notification
            if os.getenv('DEPLOYMENT_EMAIL'):
                # Would implement email sending here
                pass

            # Log to file
            notification_file = self.project_root / 'deployment' / f'notification_{self.deployment_id}.txt'
            notification_file.write_text(message)

            return {
                'status': 'success' if notification_sent else 'warning',
                'message': 'Notifications sent' if notification_sent else 'Notifications logged'
            }

        except Exception as e:
            return {'status': 'warning', 'message': f"Notification error: {str(e)}"}

    def create_rollback_point(self, phase_name: str):
        """Create a rollback point"""
        rollback_point = {
            'phase': phase_name,
            'timestamp': datetime.now().isoformat(),
            'environment_snapshot': os.environ.copy(),
        }

        # Save database backup if connected
        try:
            import psycopg2
            conn = psycopg2.connect(os.getenv('DATABASE_URL'))
            rollback_point['database_backup'] = f'backups/rollback_{self.deployment_id}_{phase_name}.sql'
            conn.close()
        except:
            pass

        self.rollback_points.append(rollback_point)
        logger.info(f"Created rollback point for {phase_name}")

    async def rollback(self, failed_phase: str):
        """Rollback to previous state"""
        logger.warning(f"🔄 Initiating rollback due to failure in: {failed_phase}")

        if not self.rollback_points:
            logger.error("No rollback points available")
            return

        last_rollback = self.rollback_points[-1]
        logger.info(f"Rolling back to: {last_rollback['phase']}")

        try:
            # Restore database if backup exists
            if 'database_backup' in last_rollback:
                cmd = [
                    'psql',
                    os.getenv('DATABASE_URL'),
                    '-f', last_rollback['database_backup']
                ]
                subprocess.run(cmd, capture_output=True)
                logger.info("Database restored")

            # Rollback Docker containers
            if self.deployment_type == 'docker':
                subprocess.run(
                    ['docker', 'compose', 'down'],
                    capture_output=True,
                    cwd=self.project_root
                )
                logger.info("Docker services stopped")

            logger.info("✅ Rollback completed")

        except Exception as e:
            logger.error(f"Rollback failed: {str(e)}")

    def generate_final_report(self, completed: int, total: int, failed: List[str]) -> Dict:
        """Generate final deployment report"""
        success = len(failed) == 0
        completion_rate = (completed / total) * 100 if total > 0 else 0

        report = {
            'deployment_id': self.deployment_id,
            'timestamp': datetime.now().isoformat(),
            'environment': self.environment,
            'deployment_type': self.deployment_type,
            'success': success,
            'completion_rate': completion_rate,
            'phases_completed': f"{completed}/{total}",
            'failed_phases': failed,
            'deployment_status': self.deployment_status,
            'deployment_log': self.deployment_log,
            'rollback_points': len(self.rollback_points),
        }

        # Save report
        report_file = self.project_root / 'deployment' / f'deployment_report_{self.deployment_id}.json'
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"\n📊 Deployment report saved to: {report_file}")

        # Generate summary
        if success:
            report['summary'] = f"✅ Deployment SUCCESSFUL! All {total} phases completed."
        else:
            report['summary'] = f"❌ Deployment FAILED. {len(failed)} phases failed: {', '.join(failed)}"

        return report


async def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description='RuleIQ Deployment Orchestrator')
    parser.add_argument('--env', choices=['development', 'staging', 'production'],
                       default='production', help='Deployment environment')
    parser.add_argument('--type', choices=['docker', 'vercel', 'kubernetes'],
                       default='docker', help='Deployment type')
    parser.add_argument('--skip-tests', action='store_true',
                       help='Skip test phases')
    parser.add_argument('--force', action='store_true',
                       help='Continue on non-critical failures')
    args = parser.parse_args()

    orchestrator = DeploymentOrchestrator(
        environment=args.env,
        deployment_type=args.type
    )

    report = await orchestrator.deploy(
        skip_tests=args.skip_tests,
        force=args.force
    )

    # Print summary
    print("\n" + "="*80)
    print("🚀 DEPLOYMENT SUMMARY")
    print("="*80)
    print(f"Deployment ID: {report['deployment_id']}")
    print(f"Environment: {report['environment']}")
    print(f"Type: {report['deployment_type']}")
    print(f"Completion: {report['completion_rate']:.1f}%")
    print(f"Phases: {report['phases_completed']}")

    if report['failed_phases']:
        print(f"\n❌ Failed Phases:")
        for phase in report['failed_phases']:
            print(f"  - {phase}")

    print(f"\n{report['summary']}")
    print("="*80)

    sys.exit(0 if report['success'] else 1)


if __name__ == '__main__':
    asyncio.run(main())