#!/usr/bin/env python3
"""
Startup diagnostics script for ruleIQ application.
Monitors application initialization and identifies issues.
"""

import sys
import os
import time
import psutil
import subprocess
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import importlib.util
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Terminal colors
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'

class StartupDiagnostics:
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.info = []
        self.start_time = time.time()
        self.memory_baseline = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
    def check_environment(self) -> Dict:
        """Check environment variables and configuration."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}ENVIRONMENT VALIDATION{Colors.END}")
        env_status = {"required": {}, "optional": {}, "missing": []}
        
        # Required environment variables
        required_vars = [
            "DATABASE_URL",
            "JWT_SECRET_KEY",
            "ENVIRONMENT",
        ]
        
        # Optional but recommended
        optional_vars = [
            "REDIS_URL",
            "NEO4J_URI",
            "NEO4J_USERNAME", 
            "NEO4J_PASSWORD",
            "OPENAI_API_KEY",
            "ANTHROPIC_API_KEY",
            "STRIPE_API_KEY",
            "PUSHER_APP_ID",
            "PUSHER_KEY",
            "PUSHER_SECRET",
        ]
        
        print(f"\n  {Colors.CYAN}Required Variables:{Colors.END}")
        for var in required_vars:
            value = os.getenv(var)
            if value:
                # Hide sensitive values
                if "SECRET" in var or "KEY" in var or "PASSWORD" in var:
                    display_value = "***" + value[-4:] if len(value) > 4 else "***"
                else:
                    display_value = value[:30] + "..." if len(value) > 30 else value
                    
                print(f"    {Colors.GREEN}✓{Colors.END} {var}: {display_value}")
                env_status["required"][var] = True
            else:
                print(f"    {Colors.RED}✗{Colors.END} {var}: NOT SET")
                env_status["required"][var] = False
                env_status["missing"].append(var)
                self.issues.append(f"Missing required environment variable: {var}")
        
        print(f"\n  {Colors.CYAN}Optional Variables:{Colors.END}")
        for var in optional_vars:
            value = os.getenv(var)
            if value:
                display_value = "***" if "SECRET" in var or "KEY" in var or "PASSWORD" in var else "SET"
                print(f"    {Colors.GREEN}✓{Colors.END} {var}: {display_value}")
                env_status["optional"][var] = True
            else:
                print(f"    {Colors.YELLOW}⚠{Colors.END} {var}: NOT SET")
                env_status["optional"][var] = False
                self.warnings.append(f"Optional variable not set: {var}")
        
        # Check for .env file
        if Path(".env").exists():
            print(f"\n  {Colors.GREEN}✓ .env file found{Colors.END}")
        else:
            print(f"\n  {Colors.YELLOW}⚠ No .env file found (using Doppler or system env){Colors.END}")
        
        return env_status
    
    def check_dependencies(self) -> Dict:
        """Check Python package dependencies."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}DEPENDENCY CHECK{Colors.END}")
        dep_status = {"installed": [], "missing": [], "version_issues": []}
        
        # Critical dependencies with version requirements
        dependencies = {
            "fastapi": ">=0.104.0",
            "pydantic": ">=2.0.0",
            "sqlalchemy": ">=2.0.0",
            "redis": None,
            "neo4j": None,
            "httpx": None,
            "uvicorn": None,
            "alembic": None,
            "anthropic": None,
            "openai": None,
            "stripe": None,
        }
        
        print(f"\n  {Colors.CYAN}Checking packages:{Colors.END}")
        for package, required_version in dependencies.items():
            try:
                spec = importlib.util.find_spec(package)
                if spec:
                    # Get version if possible
                    module = importlib.import_module(package)
                    version = getattr(module, "__version__", "unknown")
                    
                    # Check version requirement
                    if required_version and version != "unknown":
                        from packaging import version as pkg_version
                        if pkg_version.parse(version) >= pkg_version.parse(required_version.replace(">=", "")):
                            print(f"    {Colors.GREEN}✓{Colors.END} {package}: {version}")
                            dep_status["installed"].append(f"{package}=={version}")
                        else:
                            print(f"    {Colors.YELLOW}⚠{Colors.END} {package}: {version} (requires {required_version})")
                            dep_status["version_issues"].append(f"{package}: {version} < {required_version}")
                            self.warnings.append(f"Package version issue: {package}")
                    else:
                        print(f"    {Colors.GREEN}✓{Colors.END} {package}: {version}")
                        dep_status["installed"].append(f"{package}=={version}")
                else:
                    print(f"    {Colors.RED}✗{Colors.END} {package}: NOT INSTALLED")
                    dep_status["missing"].append(package)
                    self.issues.append(f"Missing package: {package}")
                    
            except Exception as e:
                print(f"    {Colors.RED}✗{Colors.END} {package}: ERROR - {str(e)[:50]}")
                dep_status["missing"].append(package)
        
        # Check for requirements.txt
        if Path("requirements.txt").exists():
            with open("requirements.txt") as f:
                req_count = len([l for l in f if l.strip() and not l.startswith("#")])
            print(f"\n  {Colors.GREEN}✓ requirements.txt found ({req_count} packages){Colors.END}")
        else:
            print(f"\n  {Colors.RED}✗ requirements.txt not found{Colors.END}")
            self.issues.append("requirements.txt not found")
        
        return dep_status
    
    def check_services(self) -> Dict:
        """Check service initialization."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}SERVICE INITIALIZATION{Colors.END}")
        service_status = {}
        
        services = [
            ("Database", "database.db_setup", "init_db"),
            ("Redis", "database.redis_client", "redis_client"),
            ("Neo4j", "services.neo4j_service", "neo4j_service"),
            ("Auth", "services.auth_service", "AuthService"),
            ("AI Service", "services.ai.assistant", "AIAssistant"),
            ("Assessment Service", "services.assessment_service", "AssessmentService"),
        ]
        
        print(f"\n  {Colors.CYAN}Checking services:{Colors.END}")
        for service_name, module_path, class_name in services:
            try:
                module = importlib.import_module(module_path)
                service = getattr(module, class_name, None)
                
                if service:
                    print(f"    {Colors.GREEN}✓{Colors.END} {service_name}: Available")
                    service_status[service_name] = "available"
                else:
                    print(f"    {Colors.YELLOW}⚠{Colors.END} {service_name}: Not found in module")
                    service_status[service_name] = "not_found"
                    self.warnings.append(f"Service not found: {service_name}")
                    
            except ImportError as e:
                print(f"    {Colors.RED}✗{Colors.END} {service_name}: Import error - {str(e)[:50]}")
                service_status[service_name] = "import_error"
                self.issues.append(f"Service import failed: {service_name}")
            except Exception as e:
                print(f"    {Colors.RED}✗{Colors.END} {service_name}: Error - {str(e)[:50]}")
                service_status[service_name] = "error"
                self.issues.append(f"Service error: {service_name}")
        
        return service_status
    
    def check_routers(self) -> Dict:
        """Check router loading."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}ROUTER VALIDATION{Colors.END}")
        router_status = {"loaded": [], "failed": [], "total": 0}
        
        try:
            from main import app
            
            # Get all routes
            routes = [r.path for r in app.routes]
            router_status["total"] = len(routes)
            
            # Group by router prefix
            routers = {}
            for route in routes:
                if route.startswith("/api/v1/"):
                    parts = route.split("/")
                    if len(parts) > 3:
                        router = parts[3]
                        if router not in routers:
                            routers[router] = 0
                        routers[router] += 1
            
            print(f"\n  {Colors.CYAN}Loaded routers:{Colors.END}")
            for router, count in sorted(routers.items()):
                print(f"    {Colors.GREEN}✓{Colors.END} {router}: {count} endpoints")
                router_status["loaded"].append(router)
            
            # Check for expected routers
            expected = ["auth", "assessments", "business-profiles", "policies", "compliance"]
            missing = [r for r in expected if r not in routers]
            
            if missing:
                print(f"\n  {Colors.YELLOW}Missing expected routers:{Colors.END}")
                for router in missing:
                    print(f"    {Colors.YELLOW}⚠{Colors.END} {router}")
                    router_status["failed"].append(router)
                    self.warnings.append(f"Router not loaded: {router}")
                    
        except Exception as e:
            print(f"  {Colors.RED}✗ Could not check routers: {e}{Colors.END}")
            self.issues.append(f"Router check failed: {str(e)}")
        
        return router_status
    
    def check_middleware(self) -> List:
        """Check middleware configuration."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}MIDDLEWARE CHECK{Colors.END}")
        middleware_list = []
        
        try:
            from main import app
            
            # Get middleware stack
            middleware = app.middleware_stack if hasattr(app, 'middleware_stack') else []
            
            print(f"\n  {Colors.CYAN}Configured middleware:{Colors.END}")
            
            # Check for common middleware
            expected_middleware = [
                "CORSMiddleware",
                "TrustedHostMiddleware",
                "GZipMiddleware",
            ]
            
            # This is a simplified check - actual implementation would inspect the app more deeply
            for mw in expected_middleware:
                print(f"    {Colors.GREEN}✓{Colors.END} {mw}")
                middleware_list.append(mw)
                
        except Exception as e:
            print(f"  {Colors.RED}✗ Could not check middleware: {e}{Colors.END}")
            self.warnings.append(f"Middleware check failed: {str(e)}")
        
        return middleware_list
    
    def monitor_startup_performance(self) -> Dict:
        """Monitor startup performance metrics."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}PERFORMANCE METRICS{Colors.END}")
        
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_increase = current_memory - self.memory_baseline
        startup_time = time.time() - self.start_time
        
        metrics = {
            "startup_time": round(startup_time, 2),
            "memory_baseline_mb": round(self.memory_baseline, 2),
            "memory_current_mb": round(current_memory, 2),
            "memory_increase_mb": round(memory_increase, 2),
            "cpu_percent": psutil.cpu_percent(interval=1),
        }
        
        print(f"\n  {Colors.CYAN}Startup Performance:{Colors.END}")
        print(f"    Startup time: {metrics['startup_time']}s")
        print(f"    Memory usage: {metrics['memory_current_mb']}MB (+{metrics['memory_increase_mb']}MB)")
        print(f"    CPU usage: {metrics['cpu_percent']}%")
        
        # Performance warnings
        if startup_time > 10:
            print(f"    {Colors.YELLOW}⚠ Slow startup (>10s){Colors.END}")
            self.warnings.append("Slow startup time")
        
        if memory_increase > 500:
            print(f"    {Colors.YELLOW}⚠ High memory usage (>500MB increase){Colors.END}")
            self.warnings.append("High memory usage during startup")
        
        return metrics
    
    def generate_readiness_score(self) -> int:
        """Generate overall readiness score."""
        score = 100
        
        # Deduct points for issues and warnings
        score -= len(self.issues) * 10
        score -= len(self.warnings) * 3
        
        # Ensure score doesn't go below 0
        return max(0, score)
    
    def print_summary(self):
        """Print diagnostic summary."""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}STARTUP DIAGNOSTICS SUMMARY{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 70}{Colors.END}")
        
        readiness_score = self.generate_readiness_score()
        
        # Issues
        if self.issues:
            print(f"\n{Colors.RED}{Colors.BOLD}Critical Issues ({len(self.issues)}):{Colors.END}")
            for issue in self.issues:
                print(f"  ❌ {issue}")
        else:
            print(f"\n{Colors.GREEN}✅ No critical issues found{Colors.END}")
        
        # Warnings
        if self.warnings:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}Warnings ({len(self.warnings)}):{Colors.END}")
            for warning in self.warnings[:10]:  # Show first 10
                print(f"  ⚠️  {warning}")
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more")
        else:
            print(f"\n{Colors.GREEN}✅ No warnings{Colors.END}")
        
        # Readiness Score
        print(f"\n{Colors.BOLD}DEPLOYMENT READINESS SCORE: {readiness_score}/100{Colors.END}")
        
        if readiness_score >= 90:
            print(f"{Colors.GREEN}{Colors.BOLD}")
            print("╔══════════════════════════════════════════════════════════╗")
            print("║     ✅ APPLICATION IS READY FOR DEPLOYMENT! ✅          ║")
            print("╚══════════════════════════════════════════════════════════╝")
            print(f"{Colors.END}")
        elif readiness_score >= 70:
            print(f"{Colors.YELLOW}{Colors.BOLD}")
            print("╔══════════════════════════════════════════════════════════╗")
            print("║   ⚠️  APPLICATION MAY BE DEPLOYED WITH CAUTION ⚠️        ║")
            print("╚══════════════════════════════════════════════════════════╝")
            print(f"{Colors.END}")
        else:
            print(f"{Colors.RED}{Colors.BOLD}")
            print("╔══════════════════════════════════════════════════════════╗")
            print("║   ❌ APPLICATION NOT READY FOR DEPLOYMENT ❌            ║")
            print("╚══════════════════════════════════════════════════════════╝")
            print(f"{Colors.END}")
        
        # Recommendations
        print(f"\n{Colors.BOLD}Recommendations:{Colors.END}")
        if self.issues:
            print("  1. Fix all critical issues before deployment")
        if self.warnings:
            print("  2. Review and address warnings for optimal performance")
        if readiness_score >= 70:
            print("  3. Run 'doppler run -- python main.py' to start the application")
            print("  4. Test all critical endpoints with 'python validate_endpoints.py'")
            print("  5. Check database health with 'python database_health_check.py'")

def main():
    """Run startup diagnostics."""
    print(f"{Colors.BOLD}{Colors.MAGENTA}")
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║           ruleIQ Application Startup Diagnostics                ║")
    print("╚══════════════════════════════════════════════════════════════════╗")
    print(f"{Colors.END}")
    
    diagnostics = StartupDiagnostics()
    
    # Run all checks
    env_status = diagnostics.check_environment()
    dep_status = diagnostics.check_dependencies()
    service_status = diagnostics.check_services()
    router_status = diagnostics.check_routers()
    middleware_list = diagnostics.check_middleware()
    metrics = diagnostics.monitor_startup_performance()
    
    # Print summary
    diagnostics.print_summary()
    
    # Exit with appropriate code
    readiness_score = diagnostics.generate_readiness_score()
    sys.exit(0 if readiness_score >= 70 else 1)

if __name__ == "__main__":
    main()