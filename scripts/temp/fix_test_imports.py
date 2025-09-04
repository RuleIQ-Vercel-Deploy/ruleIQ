#!/usr/bin/env python3
"""
Script to fix import errors and ensure all tests can be collected.
"""

import subprocess
import sys
import os
import re
from pathlib import Path

def run_command(cmd, capture=True):
    """Run a shell command and return output."""
    print(f"Running: {cmd}")
    if capture:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout, result.stderr, result.returncode
    else:
        result = subprocess.run(cmd, shell=True)
        return None, None, result.returncode

def install_missing_packages():
    """Install missing packages."""
    print("\n=== Installing missing packages ===")
    
    # Install from requirements-missing.txt
    stdout, stderr, code = run_command(".venv/bin/pip install -r requirements-missing.txt")
    if code != 0:
        print(f"Error installing packages: {stderr}")
    else:
        print("Missing packages installed successfully")
    
    # Also ensure all main requirements are installed
    print("\n=== Ensuring all requirements are installed ===")
    stdout, stderr, code = run_command(".venv/bin/pip install -r requirements.txt")
    if code != 0:
        print(f"Error installing requirements: {stderr}")

def collect_test_errors():
    """Collect all import errors from pytest."""
    print("\n=== Collecting test errors ===")
    
    # Run pytest collection and capture errors
    stdout, stderr, code = run_command(".venv/bin/python -m pytest --collect-only -q 2>&1")
    
    # Parse import errors
    import_errors = []
    lines = (stdout + stderr).split('\n')
    
    current_error = None
    for line in lines:
        if 'ImportError' in line or 'ModuleNotFoundError' in line:
            if current_error:
                import_errors.append(current_error)
            current_error = {'type': 'import', 'message': line, 'details': []}
        elif current_error and (line.strip().startswith('from') or line.strip().startswith('import')):
            current_error['details'].append(line.strip())
        elif 'cannot import name' in line:
            if current_error:
                current_error['details'].append(line.strip())
        elif 'No module named' in line:
            if current_error:
                import_errors.append(current_error)
            current_error = {'type': 'module', 'message': line, 'details': []}
    
    if current_error:
        import_errors.append(current_error)
    
    return import_errors

def fix_import_errors(errors):
    """Attempt to fix import errors."""
    print(f"\n=== Found {len(errors)} import errors to fix ===")
    
    modules_to_install = set()
    
    for error in errors:
        msg = error['message']
        
        # Extract module names from error messages
        if "No module named" in msg:
            match = re.search(r"No module named ['\"]([^'\"]+)['\"]", msg)
            if match:
                module = match.group(1)
                # Convert module path to package name
                package = module.split('.')[0].replace('_', '-')
                modules_to_install.add(package)
        
        # Handle specific import errors
        if "cannot import name" in msg:
            match = re.search(r"cannot import name ['\"]([^'\"]+)['\"]", msg)
            if match:
                name = match.group(1)
                print(f"  Import error for: {name}")
    
    # Install missing modules
    if modules_to_install:
        print(f"\n=== Installing missing modules: {modules_to_install} ===")
        for module in modules_to_install:
            stdout, stderr, code = run_command(f".venv/bin/pip install {module}")
            if code == 0:
                print(f"  ✓ Installed {module}")
            else:
                print(f"  ✗ Failed to install {module}")

def count_tests():
    """Count the number of tests that can be collected."""
    print("\n=== Counting collectible tests ===")
    
    stdout, stderr, code = run_command(".venv/bin/python -m pytest --collect-only -q 2>&1")
    
    # Count test functions
    test_count = 0
    error_count = 0
    
    for line in stdout.split('\n'):
        if '<Function' in line or '<Method' in line:
            test_count += 1
        elif 'error' in line.lower() or 'failed' in line.lower():
            error_count += 1
    
    # Also try to get the summary line
    for line in stdout.split('\n'):
        if 'collected' in line:
            match = re.search(r'collected (\d+)', line)
            if match:
                test_count = int(match.group(1))
    
    return test_count, error_count

def main():
    """Main function to fix all import errors."""
    print("=== RuleIQ Test Import Fixer ===")
    print(f"Working directory: {os.getcwd()}")
    
    # Ensure we're in the right directory
    if not Path("tests").exists():
        print("Error: tests directory not found. Please run from project root.")
        sys.exit(1)
    
    # Install missing packages first
    install_missing_packages()
    
    # Collect initial test count
    initial_count, initial_errors = count_tests()
    print(f"\nInitial state: {initial_count} tests collectible, {initial_errors} errors")
    
    # Collect and fix import errors iteratively
    max_iterations = 5
    for i in range(max_iterations):
        print(f"\n=== Iteration {i+1}/{max_iterations} ===")
        
        errors = collect_test_errors()
        if not errors:
            print("No import errors found!")
            break
        
        fix_import_errors(errors)
        
        # Check progress
        current_count, current_errors = count_tests()
        print(f"Progress: {current_count} tests collectible, {current_errors} errors")
        
        if current_count >= 2600:  # Target is 2610 tests
            print("\n✓ Success! Most tests are now collectible.")
            break
    
    # Final count
    final_count, final_errors = count_tests()
    
    print("\n=== FINAL REPORT ===")
    print(f"Initial tests collectible: {initial_count}")
    print(f"Final tests collectible: {final_count}")
    print(f"Tests fixed: {final_count - initial_count}")
    print(f"Remaining errors: {final_errors}")
    
    if final_count >= 2600:
        print("\n✓ SUCCESS: Target of 2610 tests nearly reached!")
    else:
        print(f"\n⚠ Need to fix more imports. Only {final_count}/2610 tests collecting.")
        
        # List specific test files with errors
        print("\n=== Test files with import errors ===")
        stdout, stderr, _ = run_command(".venv/bin/python -m pytest --collect-only 2>&1")
        
        current_file = None
        for line in (stdout + stderr).split('\n'):
            if line.startswith('tests/') and '.py' in line:
                current_file = line.split(':')[0]
            elif 'ImportError' in line or 'ModuleNotFoundError' in line:
                if current_file:
                    print(f"  {current_file}: {line.strip()}")

if __name__ == "__main__":
    main()