#!/usr/bin/env python3
"""
Comprehensive Production Validation Script
Tests all critical infrastructure components before deployment
"""

import os
import sys
import json
import time
import requests
import subprocess
from typing import Dict, List, Tuple
import importlib.util
from pathlib import Path

# Load environment variables from .env file
def load_env_file(path='.env'):
    """Load environment variables from .env file"""
    if os.path.exists(path):
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

# Color codes for output
class Colors:
    PASS = '\033[92m'
    FAIL = '\033[91m'
    WARN = '\033[93m'
    INFO = '\033[94m'
    RESET = '\033[0m'

class ValidationResult:
    def __init__(self, test_name: str, passed: bool, message: str = "", details: Dict = None):
        self.test_name = test_name
        self.passed = passed
        self.message = message
        self.details = details or {}

class ProductionValidator:
    def __init__(self):
        # Load environment variables
        load_env_file()
        
        self.results = []
        self.base_url = os.getenv('API_BASE_URL', 'http://localhost:8000')
        self.db_url = os.getenv('DATABASE_URL', '')
        
    def log_result(self, result: ValidationResult):
        """Log validation result with appropriate formatting"""
        status = f"{Colors.PASS}PASS{Colors.RESET}" if result.passed else f"{Colors.FAIL}FAIL{Colors.RESET}"
        print(f"[{status}] {result.test_name}")
        if result.message:
            print(f"      {result.message}")
        if result.details:
            for key, value in result.details.items():
                print(f"      {key}: {value}")
        print()
        self.results.append(result)
        
    def test_fastapi_import(self) -> ValidationResult:
        """Test if FastAPI application can be imported and started"""
        try:
            # Test importing main FastAPI app
            spec = importlib.util.spec_from_file_location("main", "api/main.py")
            if spec is None or spec.loader is None:
                return ValidationResult(
                    "FastAPI Import",
                    False,
                    "Could not load api/main.py"
                )
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check if app exists
            if not hasattr(module, 'app'):
                return ValidationResult(
                    "FastAPI Import",
                    False,
                    "No 'app' variable found in main.py"
                )
                
            # Test basic app properties
            app = module.app
            if not hasattr(app, 'title'):
                return ValidationResult(
                    "FastAPI Import",
                    False,
                    "FastAPI app missing required properties"
                )
                
            return ValidationResult(
                "FastAPI Import",
                True,
                f"Successfully imported FastAPI app: {app.title}"
            )
            
        except Exception as e:
            return ValidationResult(
                "FastAPI Import",
                False,
                f"Failed to import FastAPI app: {str(e)}"
            )
    
    def test_database_initialization(self) -> ValidationResult:
        """Test database initialization works correctly"""
        try:
            # Test database setup module
            spec = importlib.util.spec_from_file_location("db_setup", "database/db_setup.py")
            if spec is None or spec.loader is None:
                return ValidationResult(
                    "Database Initialization",
                    False,
                    "Could not load database/db_setup.py"
                )
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Check for required functions based on actual db_setup.py
            required_functions = ['init_db', 'test_database_connection', 'create_all_tables']
            missing_functions = [f for f in required_functions if not hasattr(module, f)]
            
            if missing_functions:
                return ValidationResult(
                    "Database Initialization",
                    False,
                    f"Missing required functions: {', '.join(missing_functions)}"
                )
                
            return ValidationResult(
                "Database Initialization",
                True,
                "Database initialization module loaded successfully"
            )
            
        except Exception as e:
            return ValidationResult(
                "Database Initialization",
                False,
                f"Database initialization failed: {str(e)}"
            )
    
    def test_environment_variables(self) -> ValidationResult:
        """Test if all required environment variables are properly configured"""
        required_vars = [
            'DATABASE_URL',
            'SECRET_KEY',
            'API_BASE_URL',
            'ENVIRONMENT'
        ]
        
        optional_vars = [
            'REDIS_URL',
            'AWS_ACCESS_KEY_ID',
            'AWS_SECRET_ACCESS_KEY',
            'SENTRY_DSN'
        ]
        
        missing_required = [var for var in required_vars if not os.getenv(var)]
        missing_optional = [var for var in optional_vars if not os.getenv(var)]
        
        if missing_required:
            return ValidationResult(
                "Environment Variables",
                False,
                f"Missing required variables: {', '.join(missing_required)}"
            )
        
        message = "All required environment variables configured"
        if missing_optional:
            message += f" (missing optional: {', '.join(missing_optional)})"
            
        return ValidationResult(
            "Environment Variables",
            True,
            message,
            {
                "environment": os.getenv('ENVIRONMENT', 'development'),
                "database_configured": bool(os.getenv('DATABASE_URL')),
                "api_base_url": os.getenv('API_BASE_URL', 'http://localhost:8000')
            }
        )
    
    def test_critical_routes(self) -> ValidationResult:
        """Test if all critical routes are accessible"""
        critical_routes = [
            '/health',
            '/api/v1/health',
            '/api/v1/docs',
            '/api/v1/openapi.json'
        ]
        
        accessible_routes = []
        failed_routes = []
        
        for route in critical_routes:
            try:
                url = f"{self.base_url}{route}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    accessible_routes.append(route)
                else:
                    failed_routes.append(f"{route} (status: {response.status_code})")
            except requests.exceptions.RequestException as e:
                failed_routes.append(f"{route} (error: {str(e)})")
        
        if failed_routes:
            return ValidationResult(
                "Critical Routes",
                False,
                f"Failed routes: {', '.join(failed_routes)}",
                {"accessible": accessible_routes, "failed": failed_routes}
            )
        
        return ValidationResult(
            "Critical Routes",
            True,
            f"All {len(critical_routes)} critical routes accessible",
            {"routes": accessible_routes}
        )
    
    def test_database_connection(self) -> ValidationResult:
        """Test database connection establishment"""
        try:
            # Test database connection using db_setup
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            
            from database.db_setup import test_database_connection
            
            if test_database_connection():
                return ValidationResult(
                    "Database Connection",
                    True,
                    "Database connection established successfully"
                )
            else:
                return ValidationResult(
                    "Database Connection",
                    False,
                    "Database connection verification failed"
                )
                
        except ImportError as e:
            return ValidationResult(
                "Database Connection",
                False,
                f"Could not import database verification: {str(e)}"
            )
        except Exception as e:
            return ValidationResult(
                "Database Connection",
                False,
                f"Database connection test failed: {str(e)}"
            )
    
    def test_health_check_endpoints(self) -> ValidationResult:
        """Test health check endpoints respond correctly"""
        health_endpoints = [
            '/health',
            '/api/v1/health',
            '/api/v1/health/detailed'
        ]
        
        working_endpoints = []
        failed_endpoints = []
        
        for endpoint in health_endpoints:
            try:
                url = f"{self.base_url}{endpoint}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        working_endpoints.append({
                            "endpoint": endpoint,
                            "status": data.get('status', 'unknown'),
                            "details": data
                        })
                    except json.JSONDecodeError:
                        working_endpoints.append({
                            "endpoint": endpoint,
                            "status": "non-json response"
                        })
                else:
                    failed_endpoints.append(f"{endpoint} (status: {response.status_code})")
                    
            except requests.exceptions.RequestException as e:
                failed_endpoints.append(f"{endpoint} (error: {str(e)})")
        
        if failed_endpoints:
            return ValidationResult(
                "Health Check Endpoints",
                False,
                f"Failed endpoints: {', '.join(failed_endpoints)}",
                {"working": len(working_endpoints), "failed": len(failed_endpoints)}
            )
        
        return ValidationResult(
            "Health Check Endpoints",
            True,
            f"All {len(health_endpoints)} health endpoints responding",
            {"endpoints": working_endpoints}
        )
    
    def test_application_startup(self) -> ValidationResult:
        """Test if FastAPI application can be started"""
        try:
            # Test if we can start the application in a subprocess
            process = subprocess.Popen(
                ["python", "-c", "from api.main import app; print('App ready')"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(timeout=10)
            
            if "App ready" in stdout:
                return ValidationResult(
                    "Application Startup",
                    True,
                    "FastAPI application can be started successfully"
                )
            else:
                return ValidationResult(
                    "Application Startup",
                    False,
                    f"Application startup failed: {stderr}"
                )
                
        except subprocess.TimeoutExpired:
            if 'process' in locals():
                process.kill()
            return ValidationResult(
                "Application Startup",
                False,
                "Application startup timed out"
            )
        except Exception as e:
            return ValidationResult(
                "Application Startup",
                False,
                f"Application startup test failed: {str(e)}"
            )
    
    def run_all_tests(self) -> bool:
        """Run all validation tests"""
        print(f"{Colors.INFO}Starting Production Validation Tests{Colors.RESET}")
        print("=" * 50)
        print()
        
        tests = [
            self.test_fastapi_import,
            self.test_database_initialization,
            self.test_environment_variables,
            self.test_application_startup,
            self.test_database_connection,
            self.test_critical_routes,
            self.test_health_check_endpoints
        ]
        
        for test in tests:
            try:
                result = test()
                self.log_result(result)
            except Exception as e:
                error_result = ValidationResult(
                    test.__name__.replace('test_', '').replace('_', ' ').title(),
                    False,
                    f"Test execution failed: {str(e)}"
                )
                self.log_result(error_result)
        
        # Summary
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        
        print("=" * 50)
        print(f"{Colors.INFO}Validation Summary:{Colors.RESET}")
        print(f"Total Tests: {total}")
        print(f"Passed: {Colors.PASS}{passed}{Colors.RESET}")
        print(f"Failed: {Colors.FAIL}{total - passed}{Colors.RESET}")
        
        if total - passed > 0:
            print(f"\n{Colors.FAIL}Failed Tests:{Colors.RESET}")
            for result in self.results:
                if not result.passed:
                    print(f"  - {result.test_name}: {result.message}")
        
        return passed == total

def main():
    """Main validation function"""
    validator = ProductionValidator()
    all_passed = validator.run_all_tests()
    
    # Exit with appropriate status code
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()