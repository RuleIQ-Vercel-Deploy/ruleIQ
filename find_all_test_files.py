#!/usr/bin/env python3
"""Find all test files in the project"""
import os

def find_test_files():
    """Find all test files"""
    test_files = []
    
    for root, dirs, files in os.walk('.'):
        # Skip hidden directories and common non-test directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', 'venv', 'env']]
        
        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                test_files.append(os.path.join(root, file))
    
    return sorted(test_files)

if __name__ == "__main__":
    files = find_test_files()
    print(f"Found {len(files)} test files:")
    
    # Group by directory
    by_dir = {}
    for f in files:
        dir_name = os.path.dirname(f)
        if dir_name not in by_dir:
            by_dir[dir_name] = []
        by_dir[dir_name].append(os.path.basename(f))
    
    for dir_name in sorted(by_dir.keys()):
        print(f"\n{dir_name}/ ({len(by_dir[dir_name])} files)")
        for fname in by_dir[dir_name][:5]:  # Show first 5 files
            print(f"  - {fname}")
        if len(by_dir[dir_name]) > 5:
            print(f"  ... and {len(by_dir[dir_name]) - 5} more")