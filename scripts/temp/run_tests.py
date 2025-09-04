#!/usr/bin/env python
"""
Script to run tests and capture errors for analysis.
"""

import subprocess
import sys

def run_tests():
    """Run pytest and capture output."""
    cmd = [
        ".venv/bin/python", "-m", "pytest",
        "-v",  # Verbose
        "--tb=short",  # Short traceback
        "--collect-only",  # Just collect tests first
        "-q",  # Less verbose for collection
    ]
    
    print("Collecting tests...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print("STDOUT:")
    print(result.stdout)
    print("\nSTDERR:")
    print(result.stderr)
    print(f"\nReturn code: {result.returncode}")
    
    if result.returncode != 0:
        print("\n" + "="*50)
        print("Collection errors found. Running with more details...")
        
        # Run again with more details
        cmd2 = [
            ".venv/bin/python", "-m", "pytest",
            "--tb=long",  # Long traceback
            "--collect-only",  # Just collect
            "-x",  # Stop on first error
        ]
        
        result2 = subprocess.run(cmd2, capture_output=True, text=True)
        print("\nDetailed output:")
        print(result2.stdout)
        print(result2.stderr)

if __name__ == "__main__":
    run_tests()