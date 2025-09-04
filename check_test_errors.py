#!/usr/bin/env python3
"""Quick script to identify collection errors in the final 10 test files."""

import subprocess
import sys

# The 10 files with collection errors
problem_files = [
    "tests/integration/test_assessment_workflow.py",
    "tests/test_critical_auth.py",
    "tests/test_golden_dataset_validators.py",
    "tests/test_integration.py",
    "tests/test_jwt_authentication.py",
    "tests/test_notification_basic.py",
    "tests/test_phase1_fastapi.py",
    "tests/test_phase2_fastapi.py",
    "tests/test_phase3_fastapi.py",
    "tests/test_security_integration_e2e.py"
]

def check_file(filepath):
    """Check a single test file for collection errors."""
    print(f"\n{'='*60}")
    print(f"Checking: {filepath}")
    print('='*60)
    
    try:
        # Try to collect tests from the file
        result = subprocess.run(
            ["python", "-m", "pytest", filepath, "--collect-only", "--quiet"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            print(f"❌ COLLECTION ERROR:")
            # Extract the error message
            error_lines = result.stdout.split('\n') + result.stderr.split('\n')
            for line in error_lines:
                if 'ERROR' in line or 'ImportError' in line or 'SyntaxError' in line or 'ModuleNotFoundError' in line:
                    print(f"   {line}")
            return False
        else:
            # Count collected tests
            collected = 0
            for line in result.stdout.split('\n'):
                if 'collected' in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == 'collected' and i > 0:
                            try:
                                collected = int(parts[i-1])
                            except:
                                pass
            print(f"✅ OK: {collected} tests collected")
            return True
            
    except subprocess.TimeoutExpired:
        print(f"⚠️ TIMEOUT: Collection took too long")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False

def main():
    """Check all problem files."""
    print("Checking Final 10 Test Files for Collection Errors")
    print("="*60)
    
    success_count = 0
    failed_files = []
    
    for filepath in problem_files:
        if check_file(filepath):
            success_count += 1
        else:
            failed_files.append(filepath)
    
    print(f"\n{'='*60}")
    print("SUMMARY")
    print('='*60)
    print(f"✅ Successful: {success_count}/{len(problem_files)}")
    print(f"❌ Failed: {len(failed_files)}/{len(problem_files)}")
    
    if failed_files:
        print("\nFailed files:")
        for f in failed_files:
            print(f"  - {f}")
    
    return 0 if len(failed_files) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())