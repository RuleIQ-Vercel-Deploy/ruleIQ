#!/usr/bin/env python3
"""
Comprehensive syntax checker to find all Python files with syntax errors.
This will help us identify any remaining issues from the refactoring incident.
"""

import ast
import os
import sys
from pathlib import Path
import traceback

def check_syntax(file_path):
    """Check if a Python file has valid syntax."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source, filename=str(file_path))
        return True, None
    except SyntaxError as e:
        return False, e
    except Exception as e:
        # Other errors like encoding issues
        return None, e

def find_syntax_errors(root_dir='.'):
    """Find all Python files with syntax errors in the project."""
    
    root_path = Path(root_dir)
    syntax_errors = []
    other_errors = []
    checked_files = 0
    
    # Directories to skip
    skip_dirs = {
        '.venv', 'venv', 'env', '__pycache__', '.git', 'node_modules',
        'venv_linux', '.pytest_cache', 'htmlcov', '.mypy_cache',
        'backup_20250903_042619', '.scannerwork', 'archive'
    }
    
    print("Scanning for Python files with syntax errors...")
    print("=" * 70)
    
    for py_file in root_path.rglob('*.py'):
        # Skip files in excluded directories
        if any(skip_dir in py_file.parts for skip_dir in skip_dirs):
            continue
            
        checked_files += 1
        is_valid, error = check_syntax(py_file)
        
        if is_valid is False:
            syntax_errors.append((py_file, error))
        elif is_valid is None:
            other_errors.append((py_file, error))
    
    # Report results
    print(f"Checked {checked_files} Python files")
    print("-" * 70)
    
    if syntax_errors:
        print(f"\n❌ FOUND {len(syntax_errors)} FILES WITH SYNTAX ERRORS:\n")
        for file_path, error in syntax_errors:
            print(f"  File: {file_path}")
            print(f"  Line {error.lineno}: {error.msg}")
            if error.text:
                print(f"  Code: {error.text.strip()}")
            print(f"  Offset: {' ' * (error.offset - 1 if error.offset else 0)}^")
            print()
    else:
        print("\n✅ NO SYNTAX ERRORS FOUND!")
    
    if other_errors:
        print(f"\n⚠️  {len(other_errors)} files had other issues (encoding, etc):")
        for file_path, error in other_errors:
            print(f"  {file_path}: {error}")
    
    print("\n" + "=" * 70)
    print("SUMMARY:")
    print(f"  Total files checked: {checked_files}")
    print(f"  Syntax errors: {len(syntax_errors)}")
    print(f"  Other errors: {len(other_errors)}")
    print(f"  Valid files: {checked_files - len(syntax_errors) - len(other_errors)}")
    print("=" * 70)
    
    return len(syntax_errors) == 0

if __name__ == "__main__":
    success = find_syntax_errors()
    
    if success:
        print("\n🎉 All Python files have valid syntax!")
        print("You should now be able to run your test suite.")
    else:
        print("\n⚠️  Fix the syntax errors above before running tests.")
    
    sys.exit(0 if success else 1)