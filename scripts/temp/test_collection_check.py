#!/usr/bin/env python3
"""
Simple script to check test collection and report exact import errors.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Check test collection status."""
    print("=== Test Collection Status Check ===\n")
    
    # First, just try to collect tests and see what happens
    print("Running pytest collection...\n")
    result = subprocess.run(
        [".venv/bin/python", "-m", "pytest", "--collect-only", "-v"],
        capture_output=True,
        text=True
    )
    
    print("STDOUT:")
    print(result.stdout)
    print("\nSTDERR:")
    print(result.stderr)
    print(f"\nReturn code: {result.returncode}")
    
    # Count collected tests
    collected = 0
    errors = []
    
    for line in result.stdout.split('\n'):
        if '<Function' in line or '<Method' in line or '<TestCase' in line:
            collected += 1
        elif '::test_' in line:
            collected += 1
    
    for line in result.stderr.split('\n'):
        if 'ImportError' in line or 'ModuleNotFoundError' in line:
            errors.append(line)
    
    print(f"\n=== SUMMARY ===")
    print(f"Tests collected: {collected}")
    print(f"Import errors: {len(errors)}")
    
    if errors:
        print("\nImport errors found:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
    
    return collected

if __name__ == "__main__":
    collected = main()
    sys.exit(0 if collected > 0 else 1)