#!/usr/bin/env python3
"""
GitHub Actions Validation and Troubleshooting Script

This script validates GitHub Actions workflows and diagnoses common issues including:
- Pydantic dependency conflicts
- PNPM workspace configuration
- Environment variable setup
- Workflow syntax validation
"""

import os
import sys
import yaml
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse


class Colors:
    """Terminal color codes for output formatting"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(message: str):
    """Print a formatted header message"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")


def print_success(message: str):
    """Print a success message in green"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")


def print_warning(message: str):
    """Print a warning message in yellow"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")


def print_error(message: str):
    """Print an error message in red"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")


def print_info(message: str):
    """Print an info message in blue"""
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.END}")


class GitHubActionsValidator:
    """Main validator class for GitHub Actions workflows"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.workflows_dir = project_root / ".github" / "workflows"
        self.issues = []
        self.warnings = []
        self.successes = []

    def validate_all(self) -> bool:
        """Run all validation checks"""
        print_header("GitHub Actions Validation Starting")

        # Check if workflows directory exists
        if not self.workflows_dir.exists():
            print_error(f"Workflows directory not found: {self.workflows_dir}")
            print_info("Creating .github/workflows directory...")
            self.workflows_dir.mkdir(parents=True, exist_ok=True)
            print_success("Created workflows directory")

        # Run all validation checks
        self.validate_workflow_syntax()
        self.check_python_dependencies()
        self.check_pnpm_workspace()
        self.check_environment_variables()
        self.check_service_configurations()
        self.check_security_best_practices()
        self.generate_report()

        return len(self.issues) == 0

    def validate_workflow_syntax(self):
        """Validate YAML syntax in all workflow files"""
        print_header("Validating Workflow Syntax")

        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(self.workflows_dir.glob("*.yaml"))

        if not workflow_files:
            print_warning("No workflow files found")
            self.warnings.append("No workflow files found in .github/workflows")
            return

        for workflow_file in workflow_files:
            try:
                with open(workflow_file, 'r') as f:
                    workflow = yaml.safe_load(f)

                # Basic validation checks
                if 'name' not in workflow:
                    self.warnings.append(f"{workflow_file.name}: Missing 'name' field")

                if 'on' not in workflow:
                    self.issues.append(f"{workflow_file.name}: Missing 'on' trigger")

                if 'jobs' not in workflow:
                    self.issues.append(f"{workflow_file.name}: Missing 'jobs' section")
                else:
                    self.validate_jobs(workflow['jobs'], workflow_file.name)

                print_success(f"Syntax valid: {workflow_file.name}")
                self.successes.append(f"Workflow syntax valid: {workflow_file.name}")

            except yaml.YAMLError as e:
                print_error(f"YAML error in {workflow_file.name}: {e}")
                self.issues.append(f"YAML syntax error in {workflow_file.name}")
            except Exception as e:
                print_error(f"Error validating {workflow_file.name}: {e}")
                self.issues.append(f"Validation error in {workflow_file.name}")

    def validate_jobs(self, jobs: dict, filename: str):
        """Validate job configurations"""
        for job_name, job_config in jobs.items():
            if 'runs-on' not in job_config:
                self.issues.append(f"{filename}: Job '{job_name}' missing 'runs-on'")

            if 'steps' not in job_config:
                self.warnings.append(f"{filename}: Job '{job_name}' has no steps")

    def check_python_dependencies(self):
        """Check for Python dependency conflicts, especially pydantic"""
        print_header("Checking Python Dependencies")

        requirements_files = [
            self.project_root / "requirements.txt",
            self.project_root / "visualization-backend" / "requirements.txt",
            self.project_root / "frontend" / "requirements-dev.txt"
        ]

        pydantic_versions = {}

        for req_file in requirements_files:
            if req_file.exists():
                print_info(f"Checking {req_file.relative_to(self.project_root)}")
                with open(req_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('pydantic'):
                            if '==' in line:
                                package, version = line.split('==')
                                package = package.strip()
                                version = version.strip().split('[')[0]  # Remove extras
                                pydantic_versions[str(req_file)] = version

        if pydantic_versions:
            unique_versions = set(pydantic_versions.values())
            if len(unique_versions) > 1:
                print_warning(f"Multiple pydantic versions found: {pydantic_versions}")
                self.issues.append(f"Pydantic version conflict: {pydantic_versions}")
                print_info("Resolution: Use 'pip install --force-reinstall pydantic==2.9.2' in CI")
            else:
                print_success(f"Pydantic version consistent: {list(unique_versions)[0]}")
                self.successes.append(f"Pydantic version consistent across files")

        # Check if pipdeptree is available for deeper analysis
        try:
            result = subprocess.run(
                ["pip", "list"],
                capture_output=True,
                text=True,
                check=False
            )
            if "pydantic" in result.stdout:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'pydantic' in line.lower():
                        print_info(f"Installed: {line.strip()}")
        except Exception as e:
            print_warning(f"Could not check installed packages: {e}")

    def check_pnpm_workspace(self):
        """Check pnpm workspace configuration"""
        print_header("Checking PNPM Workspace Configuration")

        frontend_dir = self.project_root / "frontend"
        pnpm_workspace = self.project_root / "pnpm-workspace.yaml"
        pnpm_lock = frontend_dir / "pnpm-lock.yaml"
        package_json = frontend_dir / "package.json"

        # Check if frontend directory exists
        if not frontend_dir.exists():
            print_warning("Frontend directory not found")
            self.warnings.append("Frontend directory not found")
            return

        # Check pnpm-workspace.yaml
        if pnpm_workspace.exists():
            try:
                with open(pnpm_workspace, 'r') as f:
                    workspace = yaml.safe_load(f)
                    print_success("pnpm-workspace.yaml found and valid")
                    self.successes.append("pnpm workspace configuration valid")
            except Exception as e:
                print_error(f"Error reading pnpm-workspace.yaml: {e}")
                self.issues.append("Invalid pnpm-workspace.yaml")
        else:
            print_warning("pnpm-workspace.yaml not found - creating default")
            with open(pnpm_workspace, 'w') as f:
                f.write("packages:\n  - 'frontend'\n")
            print_success("Created default pnpm-workspace.yaml")

        # Check pnpm-lock.yaml
        if not pnpm_lock.exists():
            print_error("pnpm-lock.yaml not found in frontend directory")
            self.issues.append("Missing pnpm-lock.yaml in frontend/")
            print_info("Fix: Run 'cd frontend && pnpm install' to generate lock file")
        else:
            print_success("pnpm-lock.yaml found")
            self.successes.append("pnpm lock file present")

        # Check package.json
        if package_json.exists():
            try:
                with open(package_json, 'r') as f:
                    package = json.load(f)
                    if 'scripts' in package:
                        print_success(f"package.json found with {len(package['scripts'])} scripts")
                        self.successes.append("Frontend package.json valid")
            except Exception as e:
                print_error(f"Error reading package.json: {e}")
                self.issues.append("Invalid frontend/package.json")

    def check_environment_variables(self):
        """Check for required environment variables in workflows"""
        print_header("Checking Environment Variables")

        required_env_vars = [
            "DATABASE_URL",
            "JWT_SECRET_KEY",
            "REDIS_URL",
            "TESTING",
            "DISABLE_EXTERNAL_APIS"
        ]

        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(self.workflows_dir.glob("*.yaml"))

        for workflow_file in workflow_files:
            with open(workflow_file, 'r') as f:
                content = f.read()

            missing_vars = []
            for var in required_env_vars:
                if var not in content:
                    missing_vars.append(var)

            if missing_vars and 'test' in workflow_file.name.lower():
                print_warning(f"{workflow_file.name}: Missing env vars: {missing_vars}")
                self.warnings.append(f"{workflow_file.name}: Consider adding {missing_vars}")
            else:
                print_success(f"{workflow_file.name}: Environment variables checked")

    def check_service_configurations(self):
        """Check service container configurations"""
        print_header("Checking Service Configurations")

        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(self.workflows_dir.glob("*.yaml"))

        for workflow_file in workflow_files:
            try:
                with open(workflow_file, 'r') as f:
                    workflow = yaml.safe_load(f)

                if 'jobs' in workflow:
                    for job_name, job_config in workflow['jobs'].items():
                        if 'services' in job_config:
                            services = job_config['services']
                            if 'postgres' in services:
                                print_success(f"{workflow_file.name}/{job_name}: PostgreSQL service configured")
                                self.successes.append(f"PostgreSQL service in {workflow_file.name}")
                            if 'redis' in services:
                                print_success(f"{workflow_file.name}/{job_name}: Redis service configured")
                                self.successes.append(f"Redis service in {workflow_file.name}")
            except Exception as e:
                print_warning(f"Could not check services in {workflow_file.name}: {e}")

    def check_security_best_practices(self):
        """Check for security best practices in workflows"""
        print_header("Checking Security Best Practices")

        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(self.workflows_dir.glob("*.yaml"))

        for workflow_file in workflow_files:
            try:
                with open(workflow_file, 'r') as f:
                    workflow = yaml.safe_load(f)

                # Check for permissions
                if 'permissions' in workflow:
                    print_success(f"{workflow_file.name}: Permissions explicitly defined")
                    self.successes.append(f"Permissions defined in {workflow_file.name}")
                else:
                    print_warning(f"{workflow_file.name}: Consider adding explicit permissions")
                    self.warnings.append(f"No permissions in {workflow_file.name}")

                # Check for pin versions
                with open(workflow_file, 'r') as f:
                    content = f.read()
                    if '@v' in content and '@main' not in content and '@master' not in content:
                        print_success(f"{workflow_file.name}: Actions are version-pinned")
                    else:
                        print_warning(f"{workflow_file.name}: Some actions may not be version-pinned")

            except Exception as e:
                print_warning(f"Could not check security in {workflow_file.name}: {e}")

    def generate_report(self):
        """Generate final validation report"""
        print_header("Validation Report")

        print(f"\n{Colors.BOLD}Summary:{Colors.END}")
        print(f"  ✅ Successes: {len(self.successes)}")
        print(f"  ⚠️  Warnings: {len(self.warnings)}")
        print(f"  ❌ Issues: {len(self.issues)}")

        if self.issues:
            print(f"\n{Colors.BOLD}Critical Issues to Fix:{Colors.END}")
            for issue in self.issues:
                print(f"  • {issue}")

        if self.warnings:
            print(f"\n{Colors.BOLD}Warnings to Review:{Colors.END}")
            for warning in self.warnings:
                print(f"  • {warning}")

        if self.successes:
            print(f"\n{Colors.BOLD}Validated Successfully:{Colors.END}")
            for success in self.successes[:5]:  # Show first 5
                print(f"  • {success}")
            if len(self.successes) > 5:
                print(f"  ... and {len(self.successes) - 5} more")

        # Generate fixes script
        if self.issues:
            self.generate_fixes_script()

    def generate_fixes_script(self):
        """Generate a script with fixes for common issues"""
        fixes_script = self.project_root / "fix_github_actions.sh"

        with open(fixes_script, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("# Auto-generated script to fix GitHub Actions issues\n\n")

            f.write("echo 'Fixing GitHub Actions issues...'\n\n")

            # Fix for missing workflows directory
            f.write("# Ensure workflows directory exists\n")
            f.write("mkdir -p .github/workflows\n\n")

            # Fix for pnpm workspace
            f.write("# Fix pnpm workspace configuration\n")
            f.write("if [ ! -f pnpm-workspace.yaml ]; then\n")
            f.write("  echo 'packages:' > pnpm-workspace.yaml\n")
            f.write("  echo '  - frontend' >> pnpm-workspace.yaml\n")
            f.write("fi\n\n")

            # Fix for pnpm lock file
            f.write("# Generate pnpm lock file if missing\n")
            f.write("if [ -d frontend ] && [ ! -f frontend/pnpm-lock.yaml ]; then\n")
            f.write("  cd frontend && pnpm install && cd ..\n")
            f.write("fi\n\n")

            # Fix for pydantic conflicts
            f.write("# Fix pydantic version conflicts\n")
            f.write("pip install --force-reinstall pydantic==2.9.2\n\n")

            f.write("echo 'Fixes applied! Please commit the changes.'\n")

        os.chmod(fixes_script, 0o755)
        print_info(f"Generated fixes script: {fixes_script}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Validate GitHub Actions workflows")
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically apply fixes where possible"
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path.cwd(),
        help="Project root path (default: current directory)"
    )

    args = parser.parse_args()

    validator = GitHubActionsValidator(args.path)
    success = validator.validate_all()

    if args.fix and not success:
        print_info("\nApplying automatic fixes...")
        fixes_script = args.path / "fix_github_actions.sh"
        if fixes_script.exists():
            subprocess.run(["bash", str(fixes_script)], check=False)
            print_success("Fixes applied. Please re-run validation.")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()