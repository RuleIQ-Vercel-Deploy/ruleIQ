#!/usr/bin/env python3
"""Check test suite status and find runnable tests."""

import subprocess
import sys
from pathlib import Path

def check_test_collection():
    """Try to collect tests and report status."""
    test_dirs = ['tests/unit', 'tests/integration', 'tests']
    
    for test_dir in test_dirs:
        if Path(test_dir).exists():
            print(f"\n🔍 Checking {test_dir}...")
            result = subprocess.run(
                ['.venv/bin/python', '-m', 'pytest', test_dir, '--co', '-q'],
                capture_output=True,
                text=True
            )
            
            if "collected" in result.stdout:
                # Extract number of collected tests
                for line in result.stdout.split('\n'):
                    if 'collected' in line:
                        print(f"   ✓ {line.strip()}")
                        break
            elif result.returncode != 0:
                print(f"   ✗ Collection failed")
                if "ModuleNotFoundError" in result.stderr:
                    # Extract missing module
                    for line in result.stderr.split('\n'):
                        if "No module named" in line:
                            print(f"     Missing: {line.strip()}")
                            break

def find_standalone_tests():
    """Find test files that can run standalone."""
    test_files = list(Path('tests').rglob('test_*.py'))
    runnable = []
    
    print(f"\n📋 Found {len(test_files)} test files")
    print("🔧 Checking which ones can import...")
    
    for test_file in test_files[:20]:  # Check first 20
        # Try to import the test file
        result = subprocess.run(
            ['.venv/bin/python', '-c', f'import sys; sys.path.insert(0, "."); import {test_file.stem}'],
            capture_output=True,
            cwd=test_file.parent
        )
        
        if result.returncode == 0:
            runnable.append(test_file)
            print(f"   ✓ {test_file}")
    
    return runnable

def estimate_coverage():
    """Try to estimate code coverage with available tests."""
    print("\n📊 Attempting coverage measurement...")
    
    # Try to run any tests we can
    result = subprocess.run(
        ['.venv/bin/python', '-m', 'pytest', 
         '--cov=api', '--cov=services', '--cov=database',
         '--cov-report=term:skip-covered',
         '--tb=no', '-q', '--maxfail=5'],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    # Look for coverage percentage
    for line in result.stdout.split('\n'):
        if 'TOTAL' in line:
            print(f"   {line.strip()}")
            break
    
    # Count source files
    py_files = list(Path('.').glob('**/*.py'))
    py_files = [f for f in py_files if '.venv' not in str(f) and 'backup' not in str(f)]
    print(f"\n📁 Total Python files: {len(py_files)}")

if __name__ == "__main__":
    print("🧪 RuleIQ Test Suite Status Check\n")
    check_test_collection()
    # find_standalone_tests()
    estimate_coverage()
    print("\n✅ Status check complete")