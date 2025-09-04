#!/usr/bin/env python3
"""
Count test functions directly from source files.
"""

import ast
import os
from pathlib import Path

def count_tests_in_file(filepath):
    """Count test functions in a Python file."""
    test_count = 0
    try:
        with open(filepath, 'r') as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            # Count functions that start with test_
            if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                test_count += 1
            # Count test methods in classes
            elif isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                        test_count += 1
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
    
    return test_count

def main():
    """Count all test functions in the tests directory."""
    print("=== Counting Test Functions in Source Files ===\n")
    
    tests_dir = Path("tests")
    if not tests_dir.exists():
        print("Error: tests directory not found")
        return 1
    
    total_tests = 0
    file_count = 0
    test_files = {}
    
    # Walk through all Python files in tests directory
    for root, dirs, files in os.walk(tests_dir):
        # Skip __pycache__ and other non-test directories
        dirs[:] = [d for d in dirs if not d.startswith('__') and not d.startswith('.')]
        
        for file in files:
            if file.endswith('.py') and (file.startswith('test_') or file.endswith('_test.py')):
                filepath = Path(root) / file
                test_count = count_tests_in_file(filepath)
                if test_count > 0:
                    total_tests += test_count
                    file_count += 1
                    test_files[str(filepath)] = test_count
    
    print(f"Found {file_count} test files with {total_tests} test functions\n")
    
    # Show top files with most tests
    sorted_files = sorted(test_files.items(), key=lambda x: x[1], reverse=True)
    print("Top 10 test files by test count:")
    for filepath, count in sorted_files[:10]:
        print(f"  {count:4d} tests in {filepath}")
    
    print(f"\nTotal test functions found in source: {total_tests}")
    
    # Now compare with pytest collection
    print("\n=== Comparing with pytest collection ===")
    import subprocess
    result = subprocess.run(
        [".venv/bin/python", "-m", "pytest", "--collect-only", "-q"],
        capture_output=True,
        text=True
    )
    
    collected = 0
    for line in result.stdout.split('\n'):
        if 'collected' in line:
            import re
            match = re.search(r'(\d+) ', line)
            if match:
                collected = int(match.group(1))
                break
    
    print(f"Tests collected by pytest: {collected}")
    print(f"Tests in source files: {total_tests}")
    print(f"Difference (not collecting): {total_tests - collected}")
    
    if collected < total_tests:
        print(f"\n⚠ {total_tests - collected} tests are not being collected due to import errors")
    else:
        print("\n✓ All tests are being collected!")
    
    return 0

if __name__ == "__main__":
    exit(main())