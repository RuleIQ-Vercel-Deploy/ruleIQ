#!/usr/bin/env python3
"""
Install missing dependencies and run tests.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, check=False):
    """Run a shell command and return output."""
    print(f"\n🔹 Running: {cmd}")
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            check=check
        )
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Stderr: {result.stderr}", file=sys.stderr)
        return result.returncode, result.stdout, result.stderr
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return e.returncode, e.stdout, e.stderr

def main():
    print("=" * 60)
    print("RuleIQ Test Suite Setup and Execution")
    print("=" * 60)
    
    # Step 1: Install missing dependencies
    print("\n📦 Step 1: Installing missing dependencies...")
    if Path("requirements-missing.txt").exists():
        code, stdout, stderr = run_command(".venv/bin/pip install -r requirements-missing.txt")
        if code != 0:
            print(f"⚠️  Failed to install some dependencies (code {code})")
    
    # Step 2: Run fix_test_imports.py
    print("\n🔧 Step 2: Running fix_test_imports.py...")
    if Path("fix_test_imports.py").exists():
        code, stdout, stderr = run_command(".venv/bin/python fix_test_imports.py")
        if code != 0:
            print(f"⚠️  Import fixer had issues (code {code})")
    
    # Step 3: Check Docker containers
    print("\n🐳 Step 3: Checking Docker containers...")
    
    # Check PostgreSQL
    code, stdout, _ = run_command("docker ps --format '{{.Names}}' | grep -q ruleiq-test-postgres && echo 'running' || echo 'not running'")
    postgres_status = stdout.strip()
    
    if postgres_status != 'running':
        print("Starting PostgreSQL test container...")
        run_command("""
            docker run -d \
                --name ruleiq-test-postgres \
                -e POSTGRES_DB=test_ruleiq \
                -e POSTGRES_USER=test_user \
                -e POSTGRES_PASSWORD=test_password \
                -p 5433:5432 \
                postgres:15-alpine
        """)
    else:
        print("✅ PostgreSQL test container is already running")
    
    # Check Redis
    code, stdout, _ = run_command("docker ps --format '{{.Names}}' | grep -q ruleiq-test-redis && echo 'running' || echo 'not running'")
    redis_status = stdout.strip()
    
    if redis_status != 'running':
        print("Starting Redis test container...")
        run_command("""
            docker run -d \
                --name ruleiq-test-redis \
                -p 6380:6379 \
                redis:7-alpine
        """)
    else:
        print("✅ Redis test container is already running")
    
    # Wait for containers
    print("\n⏳ Waiting for containers to be ready...")
    import time
    time.sleep(3)
    
    # Step 4: Count collectible tests first
    print("\n📊 Step 4: Counting collectible tests...")
    code, stdout, stderr = run_command(".venv/bin/python -m pytest --collect-only -q")
    
    # Parse test count
    test_count = 0
    error_count = 0
    for line in stdout.split('\n'):
        if 'collected' in line:
            import re
            match = re.search(r'collected (\d+)', line)
            if match:
                test_count = int(match.group(1))
        if 'error' in line.lower():
            error_count += 1
    
    print(f"\n📈 Tests collectible: {test_count}")
    print(f"📉 Collection errors: {error_count}")
    
    # Step 5: Run the full test suite
    print("\n🧪 Step 5: Running full test suite...")
    print("This may take a few minutes...")
    
    code, stdout, stderr = run_command(
        ".venv/bin/python -m pytest -v --tb=short --no-header -q"
    )
    
    # Parse results
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    # Look for the summary line
    summary = ""
    for line in stdout.split('\n'):
        if 'passed' in line or 'failed' in line or 'error' in line:
            if '==' in line or 'in' in line:
                summary = line
    
    if summary:
        print(f"\n{summary}")
        
        # Extract numbers
        import re
        passed = re.search(r'(\d+) passed', summary)
        failed = re.search(r'(\d+) failed', summary)
        errors = re.search(r'(\d+) error', summary)
        skipped = re.search(r'(\d+) skipped', summary)
        
        passed_count = int(passed.group(1)) if passed else 0
        failed_count = int(failed.group(1)) if failed else 0
        error_count = int(errors.group(1)) if errors else 0
        skipped_count = int(skipped.group(1)) if skipped else 0
        
        total = passed_count + failed_count + error_count + skipped_count
        
        print(f"\n✅ Passed:  {passed_count}/{total} ({passed_count*100/total if total else 0:.1f}%)")
        print(f"❌ Failed:  {failed_count}/{total}")
        print(f"💥 Errors:  {error_count}/{total}")
        print(f"⏭️  Skipped: {skipped_count}/{total}")
        
        # Categorize failures if any
        if failed_count > 0 or error_count > 0:
            print("\n" + "=" * 60)
            print("📋 FAILURE CATEGORIES")
            print("=" * 60)
            
            # Parse failure details
            failures = {}
            current_test = None
            
            for line in (stdout + stderr).split('\n'):
                if 'FAILED' in line or 'ERROR' in line:
                    # Extract test name and error type
                    if '::' in line:
                        parts = line.split('::')
                        if len(parts) >= 2:
                            test_file = parts[0].split()[-1] if parts[0].split() else 'unknown'
                            test_name = parts[1].split()[0] if parts[1].split() else 'unknown'
                            
                            # Get error type from the line
                            error_type = "General Error"
                            if 'AssertionError' in line:
                                error_type = "AssertionError"
                            elif 'ImportError' in line:
                                error_type = "ImportError"
                            elif 'AttributeError' in line:
                                error_type = "AttributeError"
                            elif 'KeyError' in line:
                                error_type = "KeyError"
                            elif 'TypeError' in line:
                                error_type = "TypeError"
                            elif 'ValueError' in line:
                                error_type = "ValueError"
                            elif 'fixture' in line.lower():
                                error_type = "Fixture Error"
                            
                            if error_type not in failures:
                                failures[error_type] = []
                            failures[error_type].append(f"{test_file}::{test_name}")
            
            # Print categorized failures
            for error_type, tests in sorted(failures.items()):
                print(f"\n{error_type} ({len(tests)} tests):")
                for test in tests[:5]:  # Show first 5
                    print(f"  - {test}")
                if len(tests) > 5:
                    print(f"  ... and {len(tests) - 5} more")
        
        print("\n" + "=" * 60)
        
        # Critical issues
        if error_count > 0 or failed_count > 100:
            print("\n⚠️  CRITICAL ISSUES DETECTED:")
            if error_count > 0:
                print(f"  - {error_count} tests have collection/import errors")
            if failed_count > 100:
                print(f"  - {failed_count} tests are failing (needs immediate attention)")
            
            # Suggest next steps
            print("\n🔧 RECOMMENDED ACTIONS:")
            if error_count > 0:
                print("  1. Fix import errors first (check test_output_detailed.log)")
            if failed_count > 50:
                print("  2. Focus on fixture errors and database connections")
            print("  3. Run tests for specific modules to isolate issues")
            print("     Example: .venv/bin/python -m pytest tests/unit/ -v")
    else:
        print("Could not parse test summary. Check output above for details.")
    
    # Save detailed output
    with open("test_output_detailed.log", "w") as f:
        f.write("STDOUT:\n")
        f.write(stdout)
        f.write("\n\nSTDERR:\n")
        f.write(stderr)
    
    print("\n📝 Detailed output saved to: test_output_detailed.log")
    print("=" * 60)

if __name__ == "__main__":
    main()