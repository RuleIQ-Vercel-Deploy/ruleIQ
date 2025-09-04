#!/usr/bin/env python3
"""Script to find and report Python files with syntax errors."""

import ast
import os
import sys
from pathlib import Path
from typing import List, Tuple

def check_python_file(filepath: Path) -> Tuple[bool, str]:
    """Check if a Python file has valid syntax."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
        ast.parse(source)
        return True, ""
    except SyntaxError as e:
        return False, f"{e.msg} at line {e.lineno}"
    except Exception as e:
        return False, str(e)

def find_python_files_with_errors(root_dir: Path, exclude_dirs: set = None) -> List[Tuple[Path, str]]:
    """Find all Python files with syntax errors in a directory tree."""
    if exclude_dirs is None:
        exclude_dirs = {'venv', '__pycache__', '.git', 'node_modules', '.venv', 'venv_linux', 
                       'backup_20250903_042619', 'backup_dead_code_20250903_044305', 'archive'}
    
    error_files = []
    python_files_count = 0
    
    for root, dirs, files in os.walk(root_dir):
        # Remove excluded directories from search
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                python_files_count += 1
                is_valid, error_msg = check_python_file(filepath)
                if not is_valid:
                    error_files.append((filepath, error_msg))
    
    return error_files, python_files_count

def main():
    root_dir = Path('/home/omar/Documents/ruleIQ')
    
    print("Scanning for Python files with syntax errors...")
    error_files, total_files = find_python_files_with_errors(root_dir)
    
    if error_files:
        print(f"\nFound {len(error_files)} files with syntax errors out of {total_files} Python files:\n")
        for filepath, error_msg in error_files[:50]:  # Limit to first 50 to avoid too much output
            rel_path = filepath.relative_to(root_dir)
            print(f"  {rel_path}: {error_msg}")
        
        if len(error_files) > 50:
            print(f"\n  ... and {len(error_files) - 50} more files with errors")
    else:
        print(f"\n✓ All {total_files} Python files have valid syntax!")
    
    print(f"\nSummary: {total_files - len(error_files)} valid / {len(error_files)} with errors / {total_files} total")
    
    # Return exit code based on whether errors were found
    return 1 if error_files else 0

if __name__ == "__main__":
    sys.exit(main())