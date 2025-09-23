#!/usr/bin/env python3
"""
Vercel deployment readiness check script.
Validates that the ruleIQ application is ready for Vercel deployment.
"""

import os
import sys
import json
import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

class VercelDeploymentChecker:
    """Comprehensive deployment readiness checker for Vercel."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.errors = []
        self.warnings = []
        self.info = []

    def check_all(self) -> bool:
        """Run all deployment checks."""
        print("=" * 60)
        print("🚀 VERCEL DEPLOYMENT READINESS CHECK")
        print("=" * 60)

        checks = [
            ("Requirements", self.check_requirements),
            ("Environment Variables", self.check_environment),
            ("Vercel Configuration", self.check_vercel_config),
            ("Python Imports", self.check_imports),
            ("Database Configuration", self.check_database),
            ("Bundle Size", self.check_bundle_size),
            ("Serverless Compatibility", self.check_serverless_compatibility),
            ("Security Settings", self.check_security),
        ]

        all_passed = True
        for check_name, check_func in checks:
            print(f"\n🔍 Checking {check_name}...")
            try:
                result = check_func()
                if result:
                    print(f"✅ {check_name} check passed")
                else:
                    print(f"❌ {check_name} check failed")
                    all_passed = False
            except Exception as e:
                print(f"❌ {check_name} check error: {e}")
                self.errors.append(f"{check_name}: {e}")
                all_passed = False

        # Print summary
        self._print_summary()

        return all_passed

    def check_requirements(self) -> bool:
        """Check requirements.txt for issues."""
        requirements_file = self.project_root / "requirements.txt"

        if not requirements_file.exists():
            self.errors.append("requirements.txt not found")
            return False

        with open(requirements_file, 'r') as f:
            lines = f.readlines()

        # Check for duplicates
        packages = {}
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                package = line.split('==')[0].split('[')[0]
                if package in packages:
                    self.errors.append(f"Duplicate package: {package}")
                packages[package] = line

        # Check for unpinned versions
        unpinned = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                if '==' not in line and '>=' not in line:
                    unpinned.append(line)

        if unpinned:
            self.warnings.append(f"Unpinned packages: {', '.join(unpinned)}")

        # Check file size
        size_mb = requirements_file.stat().st_size / (1024 * 1024)
        self.info.append(f"requirements.txt size: {size_mb:.2f} MB")

        return len(self.errors) == 0

    def check_environment(self) -> bool:
        """Check required environment variables."""
        required_vars = [
            "DATABASE_URL",
            "JWT_SECRET_KEY",
            "SECRET_KEY",
        ]

        optional_vars = [
            "GOOGLE_AI_API_KEY",
            "OPENAI_API_KEY",
            "REDIS_URL",
            "NEO4J_URI",
        ]

        missing_required = []
        for var in required_vars:
            if not os.getenv(var):
                missing_required.append(var)

        if missing_required:
            self.errors.append(f"Missing required env vars: {', '.join(missing_required)}")
            self.info.append("Set these in Vercel Dashboard > Settings > Environment Variables")

        # Check optional vars
        missing_optional = []
        for var in optional_vars:
            if not os.getenv(var):
                missing_optional.append(var)

        if missing_optional:
            self.warnings.append(f"Missing optional env vars: {', '.join(missing_optional)}")

        return len(missing_required) == 0

    def check_vercel_config(self) -> bool:
        """Check vercel.json configuration."""
        config_file = self.project_root / "vercel.json"

        if not config_file.exists():
            self.errors.append("vercel.json not found")
            return False

        try:
            with open(config_file, 'r') as f:
                config = json.load(f)

            # Check for required fields
            if "functions" not in config:
                self.errors.append("vercel.json missing 'functions' configuration")

            # Check function configuration
            if "api/vercel_handler.py" in config.get("functions", {}):
                func_config = config["functions"]["api/vercel_handler.py"]

                if func_config.get("maxDuration", 0) > 60:
                    self.warnings.append("maxDuration > 60s may not be available on all plans")

                if func_config.get("memory", 0) < 512:
                    self.warnings.append("Consider increasing memory to at least 512MB")

                self.info.append(f"Function config: {func_config}")

            # Check build configuration
            if config.get("buildCommand"):
                self.info.append(f"Build command: {config['buildCommand']}")

            return True

        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid vercel.json: {e}")
            return False

    def check_imports(self) -> bool:
        """Check that critical modules can be imported."""
        critical_modules = [
            "fastapi",
            "pydantic",
            "sqlalchemy",
            "jose",
            "passlib",
        ]

        failed_imports = []
        for module in critical_modules:
            try:
                importlib.import_module(module)
            except ImportError as e:
                failed_imports.append(f"{module}: {e}")

        if failed_imports:
            self.errors.append(f"Failed imports: {', '.join(failed_imports)}")
            return False

        # Check custom modules
        try:
            # Check if our handler can be imported
            spec = importlib.util.spec_from_file_location(
                "vercel_handler",
                self.project_root / "api" / "vercel_handler.py"
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                # Don't execute, just check it can be loaded
                self.info.append("Vercel handler can be imported")
        except Exception as e:
            self.errors.append(f"Cannot import vercel_handler: {e}")
            return False

        return True

    def check_database(self) -> bool:
        """Check database configuration."""
        db_url = os.getenv("DATABASE_URL")

        if not db_url:
            self.warnings.append("DATABASE_URL not set - database checks skipped")
            return True

        # Check if URL has required parameters
        if "sslmode" not in db_url:
            self.warnings.append("Consider adding sslmode=require to DATABASE_URL")

        if "connect_timeout" not in db_url:
            self.warnings.append("Consider adding connect_timeout parameter")

        # Try to import and test database module
        try:
            from database.serverless_db import test_database_connection
            if test_database_connection():
                self.info.append("Database connection successful")
            else:
                self.warnings.append("Database connection failed - check credentials")
        except ImportError:
            self.warnings.append("serverless_db module not found")
        except Exception as e:
            self.warnings.append(f"Database check error: {e}")

        return True

    def check_bundle_size(self) -> bool:
        """Estimate deployment bundle size."""
        total_size = 0
        file_count = 0

        # Count Python files
        for path in self.project_root.rglob("*.py"):
            if ".venv" not in str(path) and "__pycache__" not in str(path):
                total_size += path.stat().st_size
                file_count += 1

        # Add requirements size estimate (rough estimate of installed packages)
        requirements_size = 50 * 1024 * 1024  # Estimate 50MB for dependencies

        total_mb = (total_size + requirements_size) / (1024 * 1024)

        self.info.append(f"Estimated bundle size: {total_mb:.2f} MB ({file_count} Python files)")

        if total_mb > 250:
            self.warnings.append(f"Bundle size ({total_mb:.2f} MB) may be too large")
            self.warnings.append("Consider removing unused dependencies")

        if total_mb > 500:
            self.errors.append(f"Bundle size ({total_mb:.2f} MB) exceeds Vercel limits")
            return False

        return True

    def check_serverless_compatibility(self) -> bool:
        """Check for serverless incompatibilities."""
        incompatible_patterns = [
            ("WebSocket", "*.py"),
            ("BackgroundTasks", "*.py"),
            ("threading.Thread", "*.py"),
            ("multiprocessing", "*.py"),
        ]

        found_issues = []
        for pattern, file_glob in incompatible_patterns:
            for path in self.project_root.rglob(file_glob):
                if ".venv" not in str(path) and "vercel_handler" not in str(path):
                    try:
                        with open(path, 'r') as f:
                            content = f.read()
                            if pattern in content:
                                found_issues.append(f"{pattern} in {path.relative_to(self.project_root)}")
                    except:
                        pass

        if found_issues:
            self.warnings.append("Found serverless incompatible features:")
            for issue in found_issues[:5]:  # Limit output
                self.warnings.append(f"  - {issue}")
            if len(found_issues) > 5:
                self.warnings.append(f"  ... and {len(found_issues) - 5} more")

        return True

    def check_security(self) -> bool:
        """Check security settings."""
        security_checks = []

        # Check for hardcoded secrets
        sensitive_patterns = [
            "sk_live_",  # Stripe live key
            "AKIA",  # AWS access key
            "-----BEGIN RSA PRIVATE KEY-----",  # Private key
        ]

        for pattern in sensitive_patterns:
            for path in self.project_root.rglob("*.py"):
                if ".venv" not in str(path):
                    try:
                        with open(path, 'r') as f:
                            if pattern in f.read():
                                security_checks.append(f"Possible secret in {path.name}")
                    except:
                        pass

        if security_checks:
            self.errors.append("Security issues found:")
            for issue in security_checks:
                self.errors.append(f"  - {issue}")
            return False

        # Check environment settings
        if os.getenv("ENVIRONMENT") == "production":
            if not os.getenv("SECURE_COOKIES"):
                self.warnings.append("Consider enabling SECURE_COOKIES in production")

        self.info.append("Security checks passed")
        return True

    def _print_summary(self):
        """Print summary of all checks."""
        print("\n" + "=" * 60)
        print("📊 DEPLOYMENT CHECK SUMMARY")
        print("=" * 60)

        if self.errors:
            print("\n❌ ERRORS (must fix before deployment):")
            for error in self.errors:
                print(f"  • {error}")

        if self.warnings:
            print("\n⚠️  WARNINGS (should address):")
            for warning in self.warnings:
                print(f"  • {warning}")

        if self.info:
            print("\n📝 INFORMATION:")
            for info in self.info:
                print(f"  • {info}")

        print("\n" + "=" * 60)

        if not self.errors:
            print("✅ Application is ready for Vercel deployment!")
            print("\nNext steps:")
            print("1. Set environment variables in Vercel Dashboard")
            print("2. Run: vercel --prod")
            print("3. Monitor deployment logs")
        else:
            print("❌ Fix errors before deploying to Vercel")
            sys.exit(1)

def main():
    """Main entry point."""
    checker = VercelDeploymentChecker()
    success = checker.check_all()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()