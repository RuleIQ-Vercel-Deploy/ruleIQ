#!/usr/bin/env python3
"""Quick script to check test collection status"""
import subprocess
import sys

def check_test_collection():
    """Check pytest collection status"""
    print("Checking test collection...")
    
    cmd = ["pytest", "--collect-only", "-q", "2>&1"]
    result = subprocess.run(" ".join(cmd), shell=True, capture_output=True, text=True)
    
    output = result.stdout + result.stderr
    
    # Count errors
    error_lines = [line for line in output.split('\n') if 'ERROR collecting' in line]
    
    # Extract final count
    for line in output.split('\n'):
        if 'error' in line.lower() and 'collected' in line.lower():
            print(f"Status: {line}")
        elif 'collected' in line:
            print(f"Status: {line}")
    
    if error_lines:
        print(f"\nFound {len(error_lines)} collection errors:")
        for error in error_lines[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(error_lines) > 10:
            print(f"  ... and {len(error_lines) - 10} more")
    
    # Check specific error files
    error_files = set()
    for line in output.split('\n'):
        if 'ERROR collecting' in line:
            parts = line.split('ERROR collecting')
            if len(parts) > 1:
                file_part = parts[1].strip().split(' ')[0]
                error_files.add(file_part)
    
    if error_files:
        print(f"\nFiles with errors ({len(error_files)}):")
        for f in sorted(error_files)[:20]:
            print(f"  - {f}")
    
    return len(error_lines) == 0

if __name__ == "__main__":
    success = check_test_collection()
    sys.exit(0 if success else 1)