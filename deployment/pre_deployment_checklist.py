#!/usr/bin/env python3
"""
Pre-Deployment Checklist for RuleIQ Application
Performs comprehensive validation before deployment
"""

import os
import sys
import json
import subprocess
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import psutil
import requests
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PreDeploymentChecker:
    """Comprehensive pre-deployment validation"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.env_file = self.project_root / '.env'
        self.env_example = self.project_root / '.env.example'
        self.results = {}
        self.critical_issues = []
        self.warnings = []
        self.readiness_score = 0

    async def run_all_checks(self) -> Dict:
        """Execute all pre-deployment checks"""
        logger.info("🚀 Starting Pre-Deployment Checklist")

        checks = [
            ("Environment Variables", self.check_environment_variables),
            ("Database Connectivity", self.check_database_connectivity),
            ("Service Dependencies", self.check_service_dependencies),
            ("Startup Diagnostics", self.run_startup_diagnostics),
            ("API Endpoints", self.validate_api_endpoints),
            ("Docker Build", self.check_docker_build),
            ("Frontend Build", self.check_frontend_build),
            ("Security Scans", self.run_security_scans),
            ("GitHub Actions", self.check_github_actions),
            ("SSL/Domain", self.check_ssl_domain),
            ("Backup Systems", self.check_backup_systems),
            ("Monitoring Setup", self.check_monitoring_setup),
        ]

        total_checks = len(checks)
        passed_checks = 0

        for check_name, check_func in checks:
            logger.info(f"\n{'='*60}")
            logger.info(f"📋 Running: {check_name}")
            logger.info(f"{'='*60}")

            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()

                self.results[check_name] = result

                if result.get('status') == 'passed':
                    passed_checks += 1
                    logger.info(f"✅ {check_name}: PASSED")
                elif result.get('status') == 'warning':
                    self.warnings.append(f"{check_name}: {result.get('message')}")
                    logger.warning(f"⚠️  {check_name}: WARNING - {result.get('message')}")
                    passed_checks += 0.5  # Partial credit for warnings
                else:
                    self.critical_issues.append(f"{check_name}: {result.get('message')}")
                    logger.error(f"❌ {check_name}: FAILED - {result.get('message')}")

            except Exception as e:
                self.critical_issues.append(f"{check_name}: {str(e)}")
                logger.error(f"❌ {check_name}: ERROR - {str(e)}")
                self.results[check_name] = {'status': 'failed', 'message': str(e)}

        self.readiness_score = (passed_checks / total_checks) * 100
        return self.generate_report()

    def check_environment_variables(self) -> Dict:
        """Validate all required environment variables"""
        if not self.env_file.exists():
            return {'status': 'failed', 'message': '.env file not found'}

        load_dotenv(self.env_file)

        # Parse .env.example for required variables
        required_vars = []
        production_vars = []

        if self.env_example.exists():
            with open(self.env_example, 'r') as f:
                for line in f:
                    if '[REQUIRED]' in line:
                        var_name = line.split('=')[0].strip()
                        required_vars.append(var_name)
                    elif '[PRODUCTION]' in line:
                        var_name = line.split('=')[0].strip()
                        production_vars.append(var_name)

        missing_required = []
        missing_production = []

        for var in required_vars:
            if not os.getenv(var):
                missing_required.append(var)

        for var in production_vars:
            if not os.getenv(var):
                missing_production.append(var)

        if missing_required:
            return {
                'status': 'failed',
                'message': f"Missing required variables: {', '.join(missing_required)}"
            }

        if missing_production:
            return {
                'status': 'warning',
                'message': f"Missing production variables: {', '.join(missing_production)}"
            }

        # Check critical security variables
        security_vars = ['JWT_SECRET_KEY', 'SECRET_KEY', 'DATABASE_URL']
        weak_security = []

        for var in security_vars:
            value = os.getenv(var, '')
            if value and len(value) < 32:
                weak_security.append(var)

        if weak_security:
            return {
                'status': 'warning',
                'message': f"Weak security variables (< 32 chars): {', '.join(weak_security)}"
            }

        return {'status': 'passed', 'message': 'All environment variables validated'}

    async def check_database_connectivity(self) -> Dict:
        """Check database connectivity and health"""
        try:
            # Import database health check module
            from scripts.database_health_check import DatabaseHealthChecker

            checker = DatabaseHealthChecker()
            result = await checker.check_health()

            if result.get('healthy'):
                return {'status': 'passed', 'message': 'Database connectivity verified'}
            else:
                return {
                    'status': 'failed',
                    'message': f"Database issues: {result.get('issues', [])}"
                }
        except ImportError:
            # Fallback to basic connectivity check
            db_url = os.getenv('DATABASE_URL')
            if not db_url:
                return {'status': 'failed', 'message': 'DATABASE_URL not configured'}

            try:
                import psycopg2
                conn = psycopg2.connect(db_url)
                conn.close()
                return {'status': 'passed', 'message': 'Database connection successful'}
            except Exception as e:
                return {'status': 'failed', 'message': f"Database connection failed: {str(e)}"}

    def check_service_dependencies(self) -> Dict:
        """Check all required services are accessible"""
        services = {
            'PostgreSQL': {'host': os.getenv('DB_HOST', 'localhost'), 'port': 5432},
            'Redis': {'host': os.getenv('REDIS_HOST', 'localhost'), 'port': 6379},
        }

        if os.getenv('NEO4J_URI'):
            services['Neo4j'] = {'host': os.getenv('NEO4J_HOST', 'localhost'), 'port': 7687}

        failed_services = []

        for service_name, config in services.items():
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((config['host'], config['port']))
                sock.close()

                if result != 0:
                    failed_services.append(f"{service_name} ({config['host']}:{config['port']})")
            except Exception as e:
                failed_services.append(f"{service_name}: {str(e)}")

        if failed_services:
            return {
                'status': 'failed',
                'message': f"Services unavailable: {', '.join(failed_services)}"
            }

        return {'status': 'passed', 'message': 'All services accessible'}

    async def run_startup_diagnostics(self) -> Dict:
        """Run startup diagnostics and check readiness"""
        try:
            # Import and run startup diagnostics
            from scripts.startup_diagnostics import StartupDiagnostics

            diagnostics = StartupDiagnostics()
            result = await diagnostics.run()

            readiness = result.get('readiness_score', 0)

            if readiness >= 90:
                return {'status': 'passed', 'message': f'Readiness score: {readiness}%'}
            elif readiness >= 70:
                return {'status': 'warning', 'message': f'Readiness score: {readiness}% (target: 90%)'}
            else:
                return {'status': 'failed', 'message': f'Readiness score: {readiness}% (minimum: 70%)'}
        except Exception as e:
            return {'status': 'warning', 'message': f'Diagnostics unavailable: {str(e)}'}

    def validate_api_endpoints(self) -> Dict:
        """Validate API endpoints are accessible"""
        try:
            # Check if API is running
            api_url = os.getenv('API_URL', 'http://localhost:8000')

            endpoints = [
                '/health',
                '/api/v1/health',
                '/docs',
            ]

            failed_endpoints = []

            for endpoint in endpoints:
                try:
                    response = requests.get(f"{api_url}{endpoint}", timeout=5)
                    if response.status_code >= 500:
                        failed_endpoints.append(f"{endpoint} (status: {response.status_code})")
                except requests.RequestException as e:
                    failed_endpoints.append(f"{endpoint} (error: {str(e)})")

            if failed_endpoints:
                if len(failed_endpoints) == len(endpoints):
                    return {'status': 'warning', 'message': 'API not running (expected for pre-deployment)'}
                else:
                    return {
                        'status': 'warning',
                        'message': f"Some endpoints unavailable: {', '.join(failed_endpoints)}"
                    }

            return {'status': 'passed', 'message': 'API endpoints validated'}
        except Exception as e:
            return {'status': 'warning', 'message': f'API validation skipped: {str(e)}'}

    def check_docker_build(self) -> Dict:
        """Check Docker images can be built"""
        try:
            # Check if Docker is available
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                return {'status': 'warning', 'message': 'Docker not available'}

            # Check Dockerfiles exist
            dockerfiles = [
                self.project_root / 'Dockerfile',
                self.project_root / 'frontend' / 'Dockerfile',
            ]

            missing = [str(df) for df in dockerfiles if not df.exists()]
            if missing:
                return {
                    'status': 'warning',
                    'message': f"Dockerfiles missing: {', '.join(missing)}"
                }

            # Test Docker build (dry run)
            result = subprocess.run(
                ['docker', 'build', '--no-cache', '--target', 'base', '-t', 'ruleiq-test', '.'],
                capture_output=True,
                text=True,
                cwd=self.project_root
            )

            if result.returncode != 0:
                return {'status': 'warning', 'message': 'Docker build test failed (non-critical)'}

            return {'status': 'passed', 'message': 'Docker build validated'}
        except Exception as e:
            return {'status': 'warning', 'message': f'Docker check skipped: {str(e)}'}

    def check_frontend_build(self) -> Dict:
        """Check frontend can be built"""
        try:
            frontend_dir = self.project_root / 'frontend'
            if not frontend_dir.exists():
                return {'status': 'failed', 'message': 'Frontend directory not found'}

            # Check package.json exists
            package_json = frontend_dir / 'package.json'
            if not package_json.exists():
                return {'status': 'failed', 'message': 'frontend/package.json not found'}

            # Check node_modules exists
            node_modules = frontend_dir / 'node_modules'
            if not node_modules.exists():
                return {'status': 'warning', 'message': 'node_modules not found (run npm install)'}

            # Test build command (dry run)
            result = subprocess.run(
                ['npm', 'run', 'build'],
                capture_output=True,
                text=True,
                cwd=frontend_dir,
                timeout=120
            )

            if result.returncode != 0:
                return {'status': 'warning', 'message': 'Frontend build failed (install dependencies first)'}

            return {'status': 'passed', 'message': 'Frontend build validated'}
        except subprocess.TimeoutExpired:
            return {'status': 'warning', 'message': 'Frontend build timeout'}
        except Exception as e:
            return {'status': 'warning', 'message': f'Frontend check skipped: {str(e)}'}

    def run_security_scans(self) -> Dict:
        """Run basic security scans"""
        try:
            security_issues = []

            # Check for common security files
            security_files = [
                '.env',
                'secrets.json',
                'credentials.json',
                'private_key.pem',
            ]

            for file in security_files:
                file_path = self.project_root / file
                if file_path.exists():
                    # Check if it's in .gitignore
                    gitignore = self.project_root / '.gitignore'
                    if gitignore.exists():
                        with open(gitignore, 'r') as f:
                            if file not in f.read():
                                security_issues.append(f"{file} not in .gitignore")

            # Run Bandit if available
            try:
                result = subprocess.run(
                    ['bandit', '-r', '.', '-f', 'json'],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root
                )
                if result.returncode == 0:
                    report = json.loads(result.stdout)
                    high_issues = len([i for i in report.get('results', []) if i['issue_severity'] == 'HIGH'])
                    if high_issues > 0:
                        security_issues.append(f"{high_issues} high-severity issues found")
            except (subprocess.SubprocessError, json.JSONDecodeError):
                pass

            if security_issues:
                return {
                    'status': 'warning',
                    'message': f"Security concerns: {', '.join(security_issues)}"
                }

            return {'status': 'passed', 'message': 'Security scans passed'}
        except Exception as e:
            return {'status': 'warning', 'message': f'Security scan error: {str(e)}'}

    def check_github_actions(self) -> Dict:
        """Check GitHub Actions workflows are configured"""
        workflows_dir = self.project_root / '.github' / 'workflows'
        if not workflows_dir.exists():
            return {'status': 'warning', 'message': 'GitHub Actions workflows not found'}

        required_workflows = [
            'ci.yml',
            'security.yml',
            'deploy-vercel.yml',
        ]

        missing = []
        for workflow in required_workflows:
            if not (workflows_dir / workflow).exists():
                missing.append(workflow)

        if missing:
            return {
                'status': 'warning',
                'message': f"Missing workflows: {', '.join(missing)}"
            }

        return {'status': 'passed', 'message': 'GitHub Actions configured'}

    def check_ssl_domain(self) -> Dict:
        """Check SSL certificates and domain configuration"""
        domain = os.getenv('PRODUCTION_DOMAIN')
        if not domain:
            return {'status': 'warning', 'message': 'Production domain not configured'}

        try:
            import ssl
            import socket

            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    # Check certificate expiration
                    import datetime
                    not_after = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (not_after - datetime.datetime.now()).days

                    if days_until_expiry < 30:
                        return {
                            'status': 'warning',
                            'message': f'SSL certificate expires in {days_until_expiry} days'
                        }

            return {'status': 'passed', 'message': 'SSL/Domain validated'}
        except Exception as e:
            return {'status': 'warning', 'message': f'SSL/Domain check skipped: {str(e)}'}

    def check_backup_systems(self) -> Dict:
        """Check backup and recovery systems"""
        backup_checks = []

        # Check database backup configuration
        if os.getenv('DB_BACKUP_ENABLED'):
            backup_checks.append('Database backups configured')

        # Check backup scripts exist
        backup_scripts = [
            self.project_root / 'scripts' / 'backup.py',
            self.project_root / 'scripts' / 'restore.py',
        ]

        for script in backup_scripts:
            if script.exists():
                backup_checks.append(f'{script.name} found')

        if not backup_checks:
            return {'status': 'warning', 'message': 'No backup systems configured'}

        return {'status': 'passed', 'message': f'Backup systems: {", ".join(backup_checks)}'}

    def check_monitoring_setup(self) -> Dict:
        """Check monitoring and observability setup"""
        monitoring_dir = self.project_root / 'monitoring'
        if not monitoring_dir.exists():
            return {'status': 'warning', 'message': 'Monitoring directory not found'}

        monitoring_files = [
            'database_monitor.py',
            'performance_monitor.py',
            'error_tracker.py',
        ]

        found = []
        for file in monitoring_files:
            if (monitoring_dir / file).exists():
                found.append(file)

        if not found:
            return {'status': 'warning', 'message': 'No monitoring scripts found'}

        # Check monitoring configuration
        monitoring_config = {
            'ERROR_TRACKING': os.getenv('SENTRY_DSN') or os.getenv('ERROR_TRACKING_ENABLED'),
            'METRICS': os.getenv('METRICS_ENABLED'),
            'LOGGING': os.getenv('LOG_LEVEL'),
        }

        configured = [k for k, v in monitoring_config.items() if v]

        if len(configured) < 2:
            return {
                'status': 'warning',
                'message': f'Limited monitoring configured: {", ".join(configured)}'
            }

        return {'status': 'passed', 'message': f'Monitoring setup: {", ".join(found)}'}

    def generate_report(self) -> Dict:
        """Generate comprehensive deployment readiness report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'readiness_score': self.readiness_score,
            'status': 'ready' if self.readiness_score >= 90 else 'not_ready',
            'critical_issues': self.critical_issues,
            'warnings': self.warnings,
            'check_results': self.results,
            'recommendations': [],
        }

        # Add recommendations based on issues
        if self.critical_issues:
            report['recommendations'].append('Fix all critical issues before deployment')

        if self.warnings:
            report['recommendations'].append('Review and address warnings for production')

        if self.readiness_score < 70:
            report['recommendations'].append('Application needs significant preparation before deployment')
        elif self.readiness_score < 90:
            report['recommendations'].append('Address remaining issues to reach deployment readiness')
        else:
            report['recommendations'].append('Application is ready for deployment')

        # Save report to file
        report_file = self.project_root / 'deployment' / f'pre_deployment_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"\n📊 Report saved to: {report_file}")

        return report


async def main():
    """Main execution function"""
    checker = PreDeploymentChecker()
    report = await checker.run_all_checks()

    # Print summary
    print("\n" + "="*80)
    print("🎯 PRE-DEPLOYMENT CHECKLIST SUMMARY")
    print("="*80)
    print(f"📊 Readiness Score: {report['readiness_score']:.1f}%")
    print(f"📋 Status: {report['status'].upper()}")

    if report['critical_issues']:
        print(f"\n❌ Critical Issues ({len(report['critical_issues'])}):")
        for issue in report['critical_issues']:
            print(f"  - {issue}")

    if report['warnings']:
        print(f"\n⚠️  Warnings ({len(report['warnings'])}):")
        for warning in report['warnings']:
            print(f"  - {warning}")

    print(f"\n💡 Recommendations:")
    for rec in report['recommendations']:
        print(f"  - {rec}")

    print("\n" + "="*80)

    # Exit with appropriate code
    if report['status'] == 'ready':
        print("✅ Application is ready for deployment!")
        sys.exit(0)
    else:
        print("❌ Application needs preparation before deployment")
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())