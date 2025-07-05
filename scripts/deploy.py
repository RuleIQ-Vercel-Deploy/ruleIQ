"""
Deployment script and operational readiness checker for ComplianceGPT.

This script helps ensure all components are properly configured and
ready for production deployment.
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict

import psycopg2  # Keep for direct DB check if needed, or remove if fully ORM-based
import redis  # Keep for direct Redis check
import requests

# Add the project root to Python path for sibling imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.logging_config import get_logger, setup_logging

# Setup logging first
setup_logging()
logger = get_logger(__name__) # Global logger for the script

class DeploymentChecker:
    """Comprehensive deployment readiness checker."""
    
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = []
        self.errors = []
        # No need for self.logger if using global logger, or self.logger = get_logger(self.__class__.__name__)
    
    def log_success(self, message: str):
        """Log a successful check."""
        logger.info(f"✅ {message}")
        self.checks_passed += 1
    
    def log_error(self, message: str, exc_info_flag: bool = False):
        """Log a failed check."""
        logger.error(f"❌ {message}", exc_info=exc_info_flag)
        self.checks_failed += 1
        self.errors.append(message)
    
    def log_warning(self, message: str):
        """Log a warning."""
        logger.warning(f"⚠️  {message}")
        self.warnings.append(message)
    
    def check_environment_variables(self) -> bool:
        """Check that all required environment variables are set."""
        logger.info("\n🔍 Checking Environment Variables...")
        
        required_vars = [
            'DATABASE_URL',
            'REDIS_URL', 
            'SECRET_KEY',
            # 'GOOGLE_API_KEY', # Assuming this might be optional for core functionality
        ]
        
        optional_vars = [
            'GOOGLE_API_KEY',
            'OPENAI_API_KEY',
            'SMTP_SERVER',
            'SMTP_PORT',
            'SMTP_USERNAME',
            'SMTP_PASSWORD',
            'FROM_EMAIL',
            'ENCRYPTION_KEY',
            'ALLOWED_ORIGINS',
            'LOG_LEVEL'
        ]
        
        all_present = True
        
        for var in required_vars:
            if os.getenv(var):
                self.log_success(f"Required variable {var} is set")
            else:
                self.log_error(f"Required variable {var} is missing")
                all_present = False
        
        for var in optional_vars:
            if os.getenv(var):
                self.log_success(f"Optional variable {var} is set")
            else:
                self.log_warning(f"Optional variable {var} is not set")
        return all_present

    def check_database_connection(self) -> bool:
        """Check connection to the PostgreSQL database."""
        logger.info("\n🔍 Checking Database Connection...")
        db_url = os.getenv('DATABASE_URL')
        if not db_url:
            self.log_error("DATABASE_URL not set, cannot check DB connection.")
            return False
        try:
            conn = psycopg2.connect(db_url)
            conn.close()
            self.log_success("Database connection successful")
            return True
        except Exception as e:
            self.log_error(f"Database connection failed: {e}", exc_info_flag=True)
            return False

    def check_redis_connection(self) -> bool:
        """Check connection to Redis."""
        logger.info("\n🔍 Checking Redis Connection...")
        redis_url = os.getenv('REDIS_URL')
        if not redis_url:
            self.log_error("REDIS_URL not set, cannot check Redis connection.")
            return False
        try:
            r = redis.from_url(redis_url)
            r.ping()
            self.log_success("Redis connection successful")
            return True
        except Exception as e:
            self.log_error(f"Redis connection failed: {e}", exc_info_flag=True)
            return False

    def check_celery_workers_status(self) -> bool:
        """Check if Celery workers are running (basic check)."""
        logger.info("\n🔍 Checking Celery Workers Status (basic)...")
        try:
            # This is a very basic check. For a more robust check, you might need
            # to use Celery's remote control commands or inspect broker queues.
            result = subprocess.run(['celery', '-A', 'workers.celery_app', 'status'], capture_output=True, text=True, timeout=15)
            if result.returncode == 0 and 'online' in result.stdout.lower():
                self.log_success(f"Celery workers appear to be running. Output: {result.stdout.strip()}")
                return True
            else:
                self.log_error(f"Celery workers might not be running or status check failed. Return code: {result.returncode}, Output: {result.stderr.strip()} {result.stdout.strip()}")
                return False
        except FileNotFoundError:
            self.log_warning("Celery command not found. Skipping Celery worker check. Ensure Celery is installed and in PATH on the deployment server.")
            return True # Warning, not a failure for the script's purpose if celery CLI isn't there
        except subprocess.TimeoutExpired:
            self.log_error("Celery status check timed out.")
            return False
        except Exception as e:
            self.log_error(f"Error checking Celery workers: {e}", exc_info_flag=True)
            return False

    def check_api_health(self, host: str) -> bool:
        """Check the health of the running API."""
        logger.info(f"\n🔍 Checking API Health at {host}...")
        health_endpoint = f"{host}/health"
        try:
            response = requests.get(health_endpoint, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "Healthy":
                    self.log_success(f"API health check passed: {data}")
                    # You can add more checks here based on the health endpoint response
                    db_status = data.get("dependencies", {}).get("database")
                    redis_status = data.get("dependencies", {}).get("redis")
                    if db_status == "Healthy":
                        self.log_success("API reports Database is Healthy")
                    else:
                        self.log_warning(f"API reports Database status: {db_status}")
                    if redis_status == "Healthy":
                        self.log_success("API reports Redis is Healthy")
                    else:
                        self.log_warning(f"API reports Redis status: {redis_status}")
                    return True
                else:
                    self.log_error(f"API health check reported unhealthy: {data}")
                    return False
            else:
                self.log_error(f"API health check failed with status {response.status_code}: {response.text}")
                return False
        except requests.exceptions.ConnectionError:
            self.log_error(f"API health check failed: Could not connect to {health_endpoint}")
            return False
        except Exception as e:
            self.log_error(f"Error during API health check: {e}", exc_info_flag=True)
            return False

    def run_all_checks(self, include_health_check: bool = False, host: str = "http://localhost:8000") -> Dict:
        """Run all deployment checks and return a summary report."""
        logger.info("🚀 Starting ComplianceGPT Deployment Readiness Checks...")
        start_time = time.time()

        self.check_environment_variables()
        self.check_database_connection()
        self.check_redis_connection()
        self.check_celery_workers_status()
        
        if include_health_check:
            self.check_api_health(host)
        else:
            self.log_warning("API health check skipped by command-line flag.")

        end_time = time.time()
        duration = end_time - start_time

        logger.info("\n🏁 Deployment Checks Summary:")
        logger.info(f"   Checks Passed: {self.checks_passed}")
        logger.info(f"   Checks Failed: {self.checks_failed}")
        logger.info(f"   Warnings: {len(self.warnings)}")
        logger.info(f"   Duration: {duration:.2f} seconds")

        overall_status = "READY" if self.checks_failed == 0 else "NOT_READY"
        if self.checks_failed == 0 and self.warnings:
            overall_status = "READY_WITH_WARNINGS"
            
        logger.info(f"   Overall Status: {overall_status}")

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": overall_status,
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "warnings_count": len(self.warnings),
            "duration_seconds": duration,
            "errors": self.errors,
            "warnings": self.warnings
        }

def create_docker_environment_file():
    """Create an example .env file for Docker Compose."""
    logger.info("\n📄 Creating example .env file for Docker ('.env.example')...")
    env_template = """# ComplianceGPT Environment Variables Example
# Copy this to .env and fill in your actual values

# Core Application Settings
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/compliancegpt
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-very-strong-secret-key-here # Generate with: openssl rand -hex 32

# External Service API Keys (Optional but recommended for full functionality)
# GOOGLE_API_KEY=your-google-api-key-for-nlp-or-other-services
# OPENAI_API_KEY=your-openai-api-key-optional

# Email Configuration (Optional)
# SMTP_SERVER=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USERNAME=your-email@gmail.com
# SMTP_PASSWORD=your-app-password
# FROM_EMAIL=noreply@yourcompany.com

# Application Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,https://your-frontend-domain.com
DEBUG=false
ENV=production # or 'development', 'staging'
LOG_LEVEL=INFO # DEBUG, INFO, WARNING, ERROR, CRITICAL

# OAuth Configuration (for integrations, if used)
# GOOGLE_CLIENT_ID=your-google-oauth-client-id
# GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
# MICROSOFT_CLIENT_ID=your-microsoft-oauth-client-id
# MICROSOFT_CLIENT_SECRET=your-microsoft-oauth-client-secret
"""
    
    env_file = ".env.example"
    try:
        with open(env_file, 'w') as f:
            f.write(env_template)
        logger.info(f"✅ Created {env_file}")
        logger.info("   Copy this to .env and update with your actual values")
    except OSError as e:
        logger.error(f"Failed to create {env_file}: {e}", exc_info_flag=True)

def main():
    """Main deployment preparation function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ComplianceGPT Deployment Checker")
    parser.add_argument("--health-check", action="store_true", help="Include health check against running application")
    parser.add_argument("--host", default="http://localhost:8000", help="Host for health check")
    parser.add_argument("--create-env", action="store_true", help="Create example environment file")
    parser.add_argument("--output", help="Save report to JSON file")
    
    args = parser.parse_args()
    
    if args.create_env:
        create_docker_environment_file()
        return
    
    # Run deployment checks
    checker = DeploymentChecker()
    report = checker.run_all_checks(
        include_health_check=args.health_check,
        host=args.host
    )
    
    # Save report if requested
    if args.output:
        try:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"\n📄 Report saved to {args.output}")
        except OSError as e:
            logger.error(f"Failed to save report to {args.output}: {e}", exc_info_flag=True)
    
    # Exit with appropriate code
    sys.exit(0 if report['overall_status'] in ['READY', 'READY_WITH_WARNINGS'] else 1)

if __name__ == "__main__":
    main()
