#!/usr/bin/env python3
"""
Environment Configuration Validator for RuleIQ
Ensures all deployment environments are properly configured
"""

import os
import sys
import json
import re
import secrets
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from urllib.parse import urlparse
import socket
import ssl

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EnvironmentValidator:
    """Comprehensive environment configuration validator"""

    def __init__(self, environment: str = 'production'):
        self.environment = environment
        self.project_root = Path(__file__).parent.parent
        self.env_file = self.project_root / '.env'
        self.env_example = self.project_root / '.env.example'
        self.validation_results = {}
        self.issues = []
        self.warnings = []
        self.security_recommendations = []

    def validate_all(self) -> Dict:
        """Run all environment validations"""
        logger.info(f"🔍 Validating {self.environment.upper()} Environment Configuration")

        validations = [
            ("Required Variables", self.validate_required_variables),
            ("Production Variables", self.validate_production_variables),
            ("Database Configuration", self.validate_database_config),
            ("Redis Configuration", self.validate_redis_config),
            ("Neo4j Configuration", self.validate_neo4j_config),
            ("API Keys & Secrets", self.validate_api_keys),
            ("CORS Settings", self.validate_cors_settings),
            ("SSL/TLS Configuration", self.validate_ssl_config),
            ("JWT Security", self.validate_jwt_security),
            ("Email Configuration", self.validate_email_config),
            ("File Storage", self.validate_file_storage),
            ("Monitoring & Logging", self.validate_monitoring),
            ("Rate Limiting", self.validate_rate_limiting),
            ("Feature Flags", self.validate_feature_flags),
            ("External Services", self.validate_external_services),
        ]

        for validation_name, validation_func in validations:
            logger.info(f"\n{'='*60}")
            logger.info(f"🔧 Checking: {validation_name}")
            logger.info(f"{'='*60}")

            try:
                result = validation_func()
                self.validation_results[validation_name] = result

                if result['status'] == 'valid':
                    logger.info(f"✅ {validation_name}: VALID")
                elif result['status'] == 'warning':
                    self.warnings.append(f"{validation_name}: {result['message']}")
                    logger.warning(f"⚠️  {validation_name}: WARNING - {result['message']}")
                else:
                    self.issues.append(f"{validation_name}: {result['message']}")
                    logger.error(f"❌ {validation_name}: INVALID - {result['message']}")

            except Exception as e:
                self.issues.append(f"{validation_name}: {str(e)}")
                logger.error(f"❌ {validation_name}: ERROR - {str(e)}")
                self.validation_results[validation_name] = {
                    'status': 'error',
                    'message': str(e)
                }

        return self.generate_report()

    def validate_required_variables(self) -> Dict:
        """Validate all required environment variables"""
        if not self.env_example.exists():
            return {'status': 'error', 'message': '.env.example not found'}

        required_vars = []
        with open(self.env_example, 'r') as f:
            for line in f:
                if '[REQUIRED]' in line:
                    match = re.match(r'^([A-Z_]+)=', line)
                    if match:
                        required_vars.append(match.group(1))

        missing_vars = []
        empty_vars = []

        for var in required_vars:
            value = os.getenv(var)
            if value is None:
                missing_vars.append(var)
            elif not value.strip():
                empty_vars.append(var)

        if missing_vars:
            return {
                'status': 'invalid',
                'message': f"Missing required variables: {', '.join(missing_vars)}"
            }

        if empty_vars:
            return {
                'status': 'warning',
                'message': f"Empty required variables: {', '.join(empty_vars)}"
            }

        return {
            'status': 'valid',
            'message': f"All {len(required_vars)} required variables present"
        }

    def validate_production_variables(self) -> Dict:
        """Validate production-specific variables"""
        if self.environment != 'production':
            return {'status': 'valid', 'message': 'Skipped for non-production environment'}

        production_vars = []
        with open(self.env_example, 'r') as f:
            for line in f:
                if '[PRODUCTION]' in line:
                    match = re.match(r'^([A-Z_]+)=', line)
                    if match:
                        production_vars.append(match.group(1))

        missing_vars = []
        for var in production_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            return {
                'status': 'warning',
                'message': f"Missing production variables: {', '.join(missing_vars)}"
            }

        # Check for development values in production
        dev_indicators = ['localhost', '127.0.0.1', 'debug', 'development']
        suspicious_vars = []

        for var in os.environ:
            value = os.getenv(var, '').lower()
            if any(indicator in value for indicator in dev_indicators):
                if var not in ['DATABASE_URL', 'REDIS_URL']:  # Some exceptions
                    suspicious_vars.append(var)

        if suspicious_vars:
            self.warnings.append(f"Development values in production: {', '.join(suspicious_vars)}")

        return {
            'status': 'valid',
            'message': f"Production variables configured"
        }

    def validate_database_config(self) -> Dict:
        """Validate database configuration and connectivity"""
        db_url = os.getenv('DATABASE_URL')

        if not db_url:
            return {'status': 'invalid', 'message': 'DATABASE_URL not configured'}

        try:
            # Parse database URL
            if db_url.startswith('postgresql://') or db_url.startswith('postgres://'):
                # Test connection
                import psycopg2
                conn = psycopg2.connect(db_url)

                # Check database settings for production
                if self.environment == 'production':
                    cur = conn.cursor()

                    # Check SSL mode
                    cur.execute("SHOW ssl;")
                    ssl_enabled = cur.fetchone()[0] == 'on'

                    if not ssl_enabled:
                        self.security_recommendations.append('Enable SSL for database connections')

                    # Check connection limit
                    cur.execute("SHOW max_connections;")
                    max_conn = int(cur.fetchone()[0])

                    if max_conn < 100:
                        self.warnings.append(f'Low database connection limit: {max_conn}')

                    cur.close()

                conn.close()

                return {'status': 'valid', 'message': 'Database connection verified'}

            else:
                return {'status': 'warning', 'message': 'Non-PostgreSQL database detected'}

        except Exception as e:
            return {'status': 'invalid', 'message': f'Database connection failed: {str(e)}'}

    def validate_redis_config(self) -> Dict:
        """Validate Redis configuration"""
        redis_url = os.getenv('REDIS_URL') or os.getenv('REDIS_HOST')

        if not redis_url:
            return {'status': 'warning', 'message': 'Redis not configured'}

        try:
            import redis

            if redis_url.startswith('redis://'):
                r = redis.from_url(redis_url)
            else:
                r = redis.Redis(host=redis_url, port=int(os.getenv('REDIS_PORT', 6379)))

            # Test connection
            r.ping()

            # Check Redis configuration
            info = r.info()

            # Check for password protection
            if not os.getenv('REDIS_PASSWORD') and self.environment == 'production':
                self.security_recommendations.append('Configure Redis password for production')

            # Check maxmemory policy
            config = r.config_get('maxmemory-policy')
            if config.get('maxmemory-policy') == 'noeviction':
                self.warnings.append('Redis maxmemory-policy is noeviction, may cause issues')

            r.close()

            return {'status': 'valid', 'message': 'Redis connection verified'}

        except Exception as e:
            return {'status': 'warning', 'message': f'Redis connection failed: {str(e)}'}

    def validate_neo4j_config(self) -> Dict:
        """Validate Neo4j configuration if enabled"""
        neo4j_uri = os.getenv('NEO4J_URI')

        if not neo4j_uri:
            return {'status': 'valid', 'message': 'Neo4j not configured (optional)'}

        try:
            from neo4j import GraphDatabase

            driver = GraphDatabase.driver(
                neo4j_uri,
                auth=(os.getenv('NEO4J_USER'), os.getenv('NEO4J_PASSWORD'))
            )

            # Test connection
            with driver.session() as session:
                result = session.run("RETURN 1")
                result.single()

            driver.close()

            return {'status': 'valid', 'message': 'Neo4j connection verified'}

        except Exception as e:
            return {'status': 'warning', 'message': f'Neo4j connection failed: {str(e)}'}

    def validate_api_keys(self) -> Dict:
        """Validate API keys and secrets"""
        critical_secrets = [
            'JWT_SECRET_KEY',
            'SECRET_KEY',
            'ENCRYPTION_KEY',
        ]

        weak_secrets = []
        missing_secrets = []

        for secret_name in critical_secrets:
            secret_value = os.getenv(secret_name)

            if not secret_value:
                missing_secrets.append(secret_name)
                continue

            # Check secret strength
            if len(secret_value) < 32:
                weak_secrets.append(f"{secret_name} (length: {len(secret_value)})")

            # Check for default/example values
            if secret_value in ['changeme', 'secret', 'default', 'example']:
                weak_secrets.append(f"{secret_name} (default value)")

        if missing_secrets:
            return {
                'status': 'invalid',
                'message': f"Missing secrets: {', '.join(missing_secrets)}"
            }

        if weak_secrets:
            if self.environment == 'production':
                return {
                    'status': 'invalid',
                    'message': f"Weak secrets for production: {', '.join(weak_secrets)}"
                }
            else:
                self.warnings.append(f"Weak secrets: {', '.join(weak_secrets)}")

        # Check API key configuration
        api_keys = {
            'STRIPE_API_KEY': 'Payment processing',
            'SENDGRID_API_KEY': 'Email service',
            'AWS_ACCESS_KEY_ID': 'AWS services',
            'OPENAI_API_KEY': 'AI services',
        }

        configured_services = []
        for key, service in api_keys.items():
            if os.getenv(key):
                configured_services.append(service)

        return {
            'status': 'valid',
            'message': f"Secrets validated. Services: {', '.join(configured_services) or 'None'}"
        }

    def validate_cors_settings(self) -> Dict:
        """Validate CORS configuration"""
        cors_origins = os.getenv('CORS_ORIGINS', '')

        if self.environment == 'production':
            if not cors_origins:
                return {
                    'status': 'invalid',
                    'message': 'CORS_ORIGINS not configured for production'
                }

            # Check for wildcard in production
            if '*' in cors_origins:
                return {
                    'status': 'invalid',
                    'message': 'Wildcard CORS origin (*) not allowed in production'
                }

            # Validate origin URLs
            origins = cors_origins.split(',')
            for origin in origins:
                try:
                    parsed = urlparse(origin.strip())
                    if not parsed.scheme or not parsed.netloc:
                        self.warnings.append(f"Invalid CORS origin: {origin}")
                except Exception:
                    self.warnings.append(f"Invalid CORS origin: {origin}")

        cors_methods = os.getenv('CORS_METHODS', 'GET,POST,PUT,DELETE')
        cors_headers = os.getenv('CORS_HEADERS', '')

        return {
            'status': 'valid',
            'message': f"CORS configured for {len(cors_origins.split(',')) if cors_origins else 0} origins"
        }

    def validate_ssl_config(self) -> Dict:
        """Validate SSL/TLS configuration"""
        if self.environment != 'production':
            return {'status': 'valid', 'message': 'SSL check skipped for non-production'}

        ssl_issues = []

        # Check HTTPS enforcement
        if os.getenv('FORCE_HTTPS', 'false').lower() != 'true':
            ssl_issues.append('HTTPS not enforced')

        # Check SSL certificate paths
        ssl_cert = os.getenv('SSL_CERT_PATH')
        ssl_key = os.getenv('SSL_KEY_PATH')

        if ssl_cert and ssl_key:
            if not Path(ssl_cert).exists():
                ssl_issues.append(f'SSL certificate not found: {ssl_cert}')
            if not Path(ssl_key).exists():
                ssl_issues.append(f'SSL key not found: {ssl_key}')
        else:
            self.warnings.append('SSL certificate paths not configured')

        # Check domain SSL
        domain = os.getenv('PRODUCTION_DOMAIN')
        if domain:
            try:
                context = ssl.create_default_context()
                with socket.create_connection((domain, 443), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=domain) as ssock:
                        cert = ssock.getpeercert()
                        # Certificate is valid if we get here
            except Exception as e:
                ssl_issues.append(f'Domain SSL check failed: {str(e)}')

        if ssl_issues:
            return {
                'status': 'warning',
                'message': f"SSL issues: {', '.join(ssl_issues)}"
            }

        return {'status': 'valid', 'message': 'SSL/TLS configuration validated'}

    def validate_jwt_security(self) -> Dict:
        """Validate JWT configuration"""
        jwt_secret = os.getenv('JWT_SECRET_KEY')
        jwt_algorithm = os.getenv('JWT_ALGORITHM', 'HS256')
        jwt_expiry = os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', '30')

        if not jwt_secret:
            return {'status': 'invalid', 'message': 'JWT_SECRET_KEY not configured'}

        issues = []

        # Check secret strength
        if len(jwt_secret) < 64:
            issues.append(f'JWT secret too short: {len(jwt_secret)} chars (recommend 64+)')

        # Check algorithm
        weak_algorithms = ['HS256', 'none']
        if jwt_algorithm in weak_algorithms and self.environment == 'production':
            self.security_recommendations.append(f'Use stronger JWT algorithm (current: {jwt_algorithm})')

        # Check token expiry
        try:
            expiry_minutes = int(jwt_expiry)
            if expiry_minutes > 60:
                self.warnings.append(f'Long JWT expiry: {expiry_minutes} minutes')
        except ValueError:
            issues.append(f'Invalid JWT expiry value: {jwt_expiry}')

        # Check refresh token configuration
        if not os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS'):
            self.warnings.append('JWT refresh token expiry not configured')

        if issues:
            return {'status': 'warning', 'message': ', '.join(issues)}

        return {'status': 'valid', 'message': 'JWT configuration validated'}

    def validate_email_config(self) -> Dict:
        """Validate email/SMTP configuration"""
        email_backend = os.getenv('EMAIL_BACKEND', 'smtp')

        if email_backend == 'smtp':
            smtp_host = os.getenv('SMTP_HOST')
            smtp_port = os.getenv('SMTP_PORT')
            smtp_user = os.getenv('SMTP_USER')

            if not all([smtp_host, smtp_port]):
                return {'status': 'warning', 'message': 'SMTP not fully configured'}

            # Check for TLS/SSL
            smtp_tls = os.getenv('SMTP_TLS', 'false').lower() == 'true'
            smtp_ssl = os.getenv('SMTP_SSL', 'false').lower() == 'true'

            if not (smtp_tls or smtp_ssl) and self.environment == 'production':
                self.security_recommendations.append('Enable TLS/SSL for SMTP in production')

        elif email_backend == 'sendgrid':
            if not os.getenv('SENDGRID_API_KEY'):
                return {'status': 'warning', 'message': 'SendGrid API key not configured'}

        # Check email settings
        from_email = os.getenv('DEFAULT_FROM_EMAIL')
        if not from_email:
            self.warnings.append('DEFAULT_FROM_EMAIL not configured')

        return {'status': 'valid', 'message': f'Email configured via {email_backend}'}

    def validate_file_storage(self) -> Dict:
        """Validate file upload and storage configuration"""
        storage_backend = os.getenv('FILE_STORAGE_BACKEND', 'local')

        if storage_backend == 'local':
            upload_dir = os.getenv('UPLOAD_DIR', 'uploads')
            upload_path = self.project_root / upload_dir

            if not upload_path.exists():
                self.warnings.append(f'Upload directory does not exist: {upload_dir}')

            # Check file size limits
            max_file_size = os.getenv('MAX_FILE_SIZE_MB', '10')
            try:
                max_size = int(max_file_size)
                if max_size > 100:
                    self.warnings.append(f'Large file size limit: {max_size}MB')
            except ValueError:
                self.warnings.append(f'Invalid MAX_FILE_SIZE_MB: {max_file_size}')

        elif storage_backend == 's3':
            s3_bucket = os.getenv('AWS_S3_BUCKET')
            s3_key = os.getenv('AWS_ACCESS_KEY_ID')

            if not all([s3_bucket, s3_key]):
                return {'status': 'invalid', 'message': 'S3 storage not properly configured'}

        # Check allowed file extensions
        allowed_extensions = os.getenv('ALLOWED_FILE_EXTENSIONS', '.pdf,.doc,.docx')
        if '.exe' in allowed_extensions or '.sh' in allowed_extensions:
            self.security_recommendations.append('Remove executable extensions from allowed files')

        return {'status': 'valid', 'message': f'File storage: {storage_backend}'}

    def validate_monitoring(self) -> Dict:
        """Validate monitoring and logging configuration"""
        monitoring_configs = []

        # Check logging
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        if log_level == 'DEBUG' and self.environment == 'production':
            self.warnings.append('DEBUG logging enabled in production')
        monitoring_configs.append(f'Logging: {log_level}')

        # Check error tracking
        if os.getenv('SENTRY_DSN'):
            monitoring_configs.append('Sentry error tracking')

        # Check metrics
        if os.getenv('PROMETHEUS_ENABLED', 'false').lower() == 'true':
            monitoring_configs.append('Prometheus metrics')

        # Check APM
        if os.getenv('DATADOG_API_KEY'):
            monitoring_configs.append('Datadog APM')
        elif os.getenv('NEW_RELIC_LICENSE_KEY'):
            monitoring_configs.append('New Relic APM')

        # Check audit logging
        if os.getenv('AUDIT_LOG_ENABLED', 'false').lower() == 'true':
            monitoring_configs.append('Audit logging')

        if not monitoring_configs:
            return {'status': 'warning', 'message': 'No monitoring configured'}

        if len(monitoring_configs) < 2 and self.environment == 'production':
            self.warnings.append('Limited monitoring for production environment')

        return {
            'status': 'valid',
            'message': f"Monitoring: {', '.join(monitoring_configs)}"
        }

    def validate_rate_limiting(self) -> Dict:
        """Validate rate limiting configuration"""
        rate_limit_enabled = os.getenv('RATE_LIMIT_ENABLED', 'false').lower() == 'true'

        if not rate_limit_enabled and self.environment == 'production':
            return {
                'status': 'warning',
                'message': 'Rate limiting not enabled for production'
            }

        if rate_limit_enabled:
            # Check rate limit values
            limits = {
                'RATE_LIMIT_PER_MINUTE': 60,
                'RATE_LIMIT_PER_HOUR': 1000,
                'RATE_LIMIT_PER_DAY': 10000,
            }

            configured_limits = []
            for limit_name, default in limits.items():
                value = os.getenv(limit_name, str(default))
                try:
                    limit_value = int(value)
                    configured_limits.append(f"{limit_name}: {limit_value}")
                except ValueError:
                    self.warnings.append(f"Invalid {limit_name}: {value}")

            return {
                'status': 'valid',
                'message': f"Rate limiting configured: {', '.join(configured_limits)}"
            }

        return {'status': 'valid', 'message': 'Rate limiting not enabled'}

    def validate_feature_flags(self) -> Dict:
        """Validate feature flags for environment"""
        feature_flags = {}

        # Collect all feature flags (FF_ prefix)
        for key in os.environ:
            if key.startswith('FF_') or key.startswith('FEATURE_'):
                feature_flags[key] = os.getenv(key)

        if not feature_flags:
            return {'status': 'valid', 'message': 'No feature flags configured'}

        # Check for development features in production
        if self.environment == 'production':
            dev_features = []
            for flag, value in feature_flags.items():
                if 'DEBUG' in flag or 'TEST' in flag or 'DEV' in flag:
                    if value.lower() in ['true', '1', 'enabled']:
                        dev_features.append(flag)

            if dev_features:
                self.warnings.append(f"Development features enabled in production: {', '.join(dev_features)}")

        return {
            'status': 'valid',
            'message': f"{len(feature_flags)} feature flags configured"
        }

    def validate_external_services(self) -> Dict:
        """Validate external service integrations"""
        services = {
            'Stripe': ['STRIPE_API_KEY', 'STRIPE_WEBHOOK_SECRET'],
            'SendGrid': ['SENDGRID_API_KEY'],
            'AWS': ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY'],
            'OpenAI': ['OPENAI_API_KEY'],
            'Google': ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET'],
            'GitHub': ['GITHUB_CLIENT_ID', 'GITHUB_CLIENT_SECRET'],
        }

        configured_services = []
        partial_services = []

        for service_name, required_vars in services.items():
            configured = [var for var in required_vars if os.getenv(var)]

            if configured:
                if len(configured) == len(required_vars):
                    configured_services.append(service_name)
                else:
                    partial_services.append(f"{service_name} ({len(configured)}/{len(required_vars)})")

        if partial_services:
            self.warnings.append(f"Partially configured services: {', '.join(partial_services)}")

        return {
            'status': 'valid',
            'message': f"External services: {', '.join(configured_services) or 'None'}"
        }

    def generate_report(self) -> Dict:
        """Generate environment validation report"""
        is_valid = len(self.issues) == 0

        report = {
            'timestamp': datetime.now().isoformat(),
            'environment': self.environment,
            'valid': is_valid,
            'issues': self.issues,
            'warnings': self.warnings,
            'security_recommendations': self.security_recommendations,
            'validation_results': self.validation_results,
            'summary': {
                'total_checks': len(self.validation_results),
                'passed': sum(1 for r in self.validation_results.values() if r['status'] == 'valid'),
                'warnings': sum(1 for r in self.validation_results.values() if r['status'] == 'warning'),
                'failed': sum(1 for r in self.validation_results.values() if r['status'] == 'invalid'),
            }
        }

        # Save report
        report_file = self.project_root / 'deployment' / f'env_validation_{self.environment}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"\n📊 Validation report saved to: {report_file}")

        return report


def main():
    """Main execution function"""
    import argparse

    parser = argparse.ArgumentParser(description='Validate environment configuration')
    parser.add_argument('--env', choices=['development', 'staging', 'production'],
                       default='production', help='Environment to validate')
    args = parser.parse_args()

    validator = EnvironmentValidator(environment=args.env)
    report = validator.validate_all()

    # Print summary
    print("\n" + "="*80)
    print(f"🔧 ENVIRONMENT VALIDATION REPORT ({args.env.upper()})")
    print("="*80)
    print(f"✅ Passed: {report['summary']['passed']}")
    print(f"⚠️  Warnings: {report['summary']['warnings']}")
    print(f"❌ Failed: {report['summary']['failed']}")

    if report['issues']:
        print(f"\n❌ Critical Issues:")
        for issue in report['issues']:
            print(f"  - {issue}")

    if report['warnings']:
        print(f"\n⚠️  Warnings:")
        for warning in report['warnings'][:5]:  # Show first 5
            print(f"  - {warning}")
        if len(report['warnings']) > 5:
            print(f"  ... and {len(report['warnings']) - 5} more")

    if report['security_recommendations']:
        print(f"\n🔒 Security Recommendations:")
        for rec in report['security_recommendations']:
            print(f"  - {rec}")

    print("\n" + "="*80)

    if report['valid']:
        print(f"✅ Environment configuration is VALID for {args.env}")
        sys.exit(0)
    else:
        print(f"❌ Environment configuration is INVALID for {args.env}")
        sys.exit(1)


if __name__ == '__main__':
    main()