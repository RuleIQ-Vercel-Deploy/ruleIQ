"""
Deployment script and operational readiness checker for ComplianceGPT.

This script helps ensure all components are properly configured and
ready for production deployment.
"""

import os
import sys
import subprocess
import requests
import time
import json
from typing import Dict, List, Tuple
from datetime import datetime
import psycopg2
import redis

class DeploymentChecker:
    """Comprehensive deployment readiness checker."""
    
    def __init__(self):
        self.checks_passed = 0
        self.checks_failed = 0
        self.warnings = []
        self.errors = []
    
    def log_success(self, message: str):
        """Log a successful check."""
        print(f"✅ {message}")
        self.checks_passed += 1
    
    def log_error(self, message: str):
        """Log a failed check."""
        print(f"❌ {message}")
        self.checks_failed += 1
        self.errors.append(message)
    
    def log_warning(self, message: str):
        """Log a warning."""
        print(f"⚠️  {message}")
        self.warnings.append(message)
    
    def check_environment_variables(self) -> bool:
        """Check that all required environment variables are set."""
        print("\n🔍 Checking Environment Variables...")
        
        required_vars = [
            'DATABASE_URL',
            'REDIS_URL', 
            'SECRET_KEY',
            'GOOGLE_API_KEY',
        ]
        
        optional_vars = [
            'OPENAI_API_KEY',
            'SMTP_SERVER',
            'SMTP_USERNAME',
            'SMTP_PASSWORD',
            'FROM_EMAIL',
            'ENCRYPTION_KEY',
            'ALLOWED_ORIGINS'
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
        """Check database connectivity and schema."""
        print("\n🗄️  Checking Database Connection...")
        
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            self.log_error("DATABASE_URL not set")
            return False
        
        try:
            # Test basic connection
            conn = psycopg2.connect(database_url)
            cursor = conn.cursor()
            
            # Check if main tables exist
            required_tables = [
                'users',
                'business_profiles', 
                'evidence_items',
                'compliance_frameworks',
                'generated_policies'
            ]
            
            for table in required_tables:
                cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}');")
                exists = cursor.fetchone()[0]
                
                if exists:
                    self.log_success(f"Table {table} exists")
                else:
                    self.log_error(f"Table {table} missing")
            
            # Check new tables for Phase 5-6 features
            new_tables = ['chat_conversations', 'chat_messages']
            for table in new_tables:
                cursor.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}');")
                exists = cursor.fetchone()[0]
                
                if exists:
                    self.log_success(f"New table {table} exists")
                else:
                    self.log_warning(f"New table {table} missing (run migrations)")
            
            cursor.close()
            conn.close()
            self.log_success("Database connection successful")
            return True
            
        except Exception as e:
            self.log_error(f"Database connection failed: {e}")
            return False
    
    def check_redis_connection(self) -> bool:
        """Check Redis connectivity."""
        print("\n📦 Checking Redis Connection...")
        
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
        
        try:
            r = redis.from_url(redis_url)
            r.ping()
            
            # Test basic operations
            r.set('deployment_test', 'success')
            result = r.get('deployment_test')
            r.delete('deployment_test')
            
            if result == b'success':
                self.log_success("Redis connection and operations successful")
                return True
            else:
                self.log_error("Redis operations failed")
                return False
                
        except Exception as e:
            self.log_error(f"Redis connection failed: {e}")
            return False
    
    def check_ai_service_configuration(self) -> bool:
        """Check AI service configuration."""
        print("\n🤖 Checking AI Service Configuration...")
        
        google_api_key = os.getenv('GOOGLE_API_KEY')
        openai_api_key = os.getenv('OPENAI_API_KEY')
        
        if google_api_key:
            self.log_success("Google AI API key configured")
            # Could add actual API test here
        else:
            self.log_error("Google AI API key missing")
        
        if openai_api_key:
            self.log_success("OpenAI API key configured")
        else:
            self.log_warning("OpenAI API key not configured (using Google AI only)")
        
        return bool(google_api_key)
    
    def check_celery_configuration(self) -> bool:
        """Check Celery worker configuration."""
        print("\n⚙️  Checking Celery Configuration...")
        
        try:
            # Import celery app
            from celery_app import celery_app
            
            # Check if beat schedule is configured
            beat_schedule = celery_app.conf.beat_schedule
            if beat_schedule:
                self.log_success(f"Celery beat schedule configured with {len(beat_schedule)} tasks")
                
                # List configured tasks
                for task_name in beat_schedule.keys():
                    print(f"   📅 {task_name}")
            else:
                self.log_warning("No Celery beat schedule configured")
            
            # Check task routing
            task_routes = celery_app.conf.task_routes
            if task_routes:
                self.log_success(f"Task routing configured for {len(task_routes)} patterns")
            else:
                self.log_warning("No task routing configured")
            
            return True
            
        except Exception as e:
            self.log_error(f"Celery configuration check failed: {e}")
            return False
    
    def check_application_startup(self) -> bool:
        """Check if the FastAPI application can start."""
        print("\n🚀 Checking Application Startup...")
        
        try:
            # Try to import the main app
            from main import app
            self.log_success("FastAPI application imports successfully")
            
            # Check router registration
            routes = [route.path for route in app.routes]
            expected_routes = [
                '/api/auth',
                '/api/evidence', 
                '/api/reports',
                '/api/chat',
                '/api/integrations'
            ]
            
            for route_prefix in expected_routes:
                matching_routes = [r for r in routes if r.startswith(route_prefix)]
                if matching_routes:
                    self.log_success(f"Routes for {route_prefix} registered")
                else:
                    self.log_warning(f"No routes found for {route_prefix}")
            
            return True
            
        except Exception as e:
            self.log_error(f"Application startup check failed: {e}")
            return False
    
    def check_dependencies(self) -> bool:
        """Check that all required Python packages are installed."""
        print("\n📦 Checking Python Dependencies...")
        
        required_packages = [
            'fastapi',
            'uvicorn',
            'sqlalchemy',
            'celery',
            'redis',
            'reportlab',
            'google-generativeai',
            'psycopg2',
            'alembic',
            'pytest'
        ]
        
        all_installed = True
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                self.log_success(f"Package {package} is installed")
            except ImportError:
                self.log_error(f"Package {package} is missing")
                all_installed = False
        
        return all_installed
    
    def check_file_permissions(self) -> bool:
        """Check file permissions for key files."""
        print("\n🔐 Checking File Permissions...")
        
        executable_files = [
            'start_workers.sh',
            'scripts/migrate_evidence.py'
        ]
        
        all_correct = True
        
        for file_path in executable_files:
            if os.path.exists(file_path):
                if os.access(file_path, os.X_OK):
                    self.log_success(f"{file_path} is executable")
                else:
                    self.log_warning(f"{file_path} is not executable")
                    # Fix the permission
                    try:
                        os.chmod(file_path, 0o755)
                        self.log_success(f"Fixed permissions for {file_path}")
                    except Exception as e:
                        self.log_error(f"Could not fix permissions for {file_path}: {e}")
                        all_correct = False
            else:
                self.log_warning(f"{file_path} does not exist")
        
        return all_correct
    
    def run_basic_health_check(self, host: str = "http://localhost:8000") -> bool:
        """Run a basic health check against the running application."""
        print(f"\n🏥 Running Health Check against {host}...")
        
        try:
            # Check basic health endpoint
            response = requests.get(f"{host}/health", timeout=10)
            if response.status_code == 200:
                self.log_success("Health endpoint responding")
            else:
                self.log_error(f"Health endpoint returned {response.status_code}")
                return False
            
            # Check API info endpoint  
            response = requests.get(f"{host}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('message') == 'ComplianceGPT API':
                    self.log_success("API info endpoint responding correctly")
                else:
                    self.log_warning("API info endpoint response unexpected")
            else:
                self.log_error(f"API info endpoint returned {response.status_code}")
            
            return True
            
        except requests.exceptions.ConnectionError:
            self.log_warning("Application not running (connection refused)")
            return False
        except Exception as e:
            self.log_error(f"Health check failed: {e}")
            return False
    
    def generate_deployment_report(self) -> Dict:
        """Generate a comprehensive deployment report."""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "warnings": self.warnings,
            "errors": self.errors,
            "overall_status": "READY" if self.checks_failed == 0 else "NOT_READY",
            "readiness_score": (self.checks_passed / (self.checks_passed + self.checks_failed)) * 100 if (self.checks_passed + self.checks_failed) > 0 else 0
        }
        
        return report
    
    def run_all_checks(self, include_health_check: bool = False, host: str = "http://localhost:8000") -> Dict:
        """Run all deployment readiness checks."""
        print("🔍 ComplianceGPT Deployment Readiness Check")
        print("=" * 50)
        
        # Run all checks
        self.check_environment_variables()
        self.check_dependencies()
        self.check_database_connection()
        self.check_redis_connection()
        self.check_ai_service_configuration()
        self.check_celery_configuration()
        self.check_application_startup()
        self.check_file_permissions()
        
        if include_health_check:
            self.run_basic_health_check(host)
        
        # Generate report
        report = self.generate_deployment_report()
        
        print("\n" + "=" * 50)
        print("📊 DEPLOYMENT READINESS SUMMARY")
        print("=" * 50)
        print(f"✅ Checks Passed: {report['checks_passed']}")
        print(f"❌ Checks Failed: {report['checks_failed']}")
        print(f"⚠️  Warnings: {len(report['warnings'])}")
        print(f"📈 Readiness Score: {report['readiness_score']:.1f}%")
        print(f"🎯 Overall Status: {report['overall_status']}")
        
        if report['errors']:
            print("\n❌ CRITICAL ISSUES TO FIX:")
            for error in report['errors']:
                print(f"   • {error}")
        
        if report['warnings']:
            print("\n⚠️  WARNINGS TO REVIEW:")
            for warning in report['warnings']:
                print(f"   • {warning}")
        
        if report['overall_status'] == 'READY':
            print("\n🎉 ComplianceGPT is ready for deployment!")
        else:
            print("\n🔧 Please fix the critical issues before deploying.")
        
        return report

def create_docker_environment_file():
    """Create a .env file for Docker deployment."""
    env_template = """# ComplianceGPT Environment Configuration
# Copy this file to .env and update with your actual values

# Database Configuration
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/compliancegpt

# Redis Configuration  
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ENCRYPTION_KEY=your-32-character-encryption-key

# AI Services
GOOGLE_API_KEY=your-google-ai-api-key
OPENAI_API_KEY=your-openai-api-key-optional

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@yourcompany.com

# Application Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
DEBUG=false
ENV=production

# OAuth Configuration (for integrations)
GOOGLE_CLIENT_ID=your-google-oauth-client-id
GOOGLE_CLIENT_SECRET=your-google-oauth-client-secret
MICROSOFT_CLIENT_ID=your-microsoft-oauth-client-id
MICROSOFT_CLIENT_SECRET=your-microsoft-oauth-client-secret
"""
    
    env_file = ".env.example"
    with open(env_file, 'w') as f:
        f.write(env_template)
    
    print(f"✅ Created {env_file}")
    print("   Copy this to .env and update with your actual values")

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
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Report saved to {args.output}")
    
    # Exit with appropriate code
    sys.exit(0 if report['overall_status'] == 'READY' else 1)

if __name__ == "__main__":
    main()