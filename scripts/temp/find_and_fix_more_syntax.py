#!/usr/bin/env python3
"""Find and automatically fix common syntax errors in Python files."""

import ast
import os
import re
from pathlib import Path
from typing import List, Tuple, Optional

def find_malformed_function_signatures(content: str) -> List[Tuple[int, str]]:
    """Find lines with malformed function signatures where body is on same line as signature."""
    issues = []
    lines = content.split('\n')
    
    for i, line in enumerate(lines):
        # Pattern: function signature ending with ): followed by non-comment code
        # Match patterns like ") ->Type: code" or ") ->None: code"
        pattern = r'\)\s*->\s*[\w\[\]|, ]+:\s*\S'
        if re.search(pattern, line):
            # Check if it's not just a docstring or comment
            after_colon = line.split(':', 1)[-1].strip()
            if after_colon and not after_colon.startswith('"""') and not after_colon.startswith('#'):
                issues.append((i + 1, line))
    
    return issues

def fix_malformed_function_signatures(content: str) -> str:
    """Fix malformed function signatures."""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Pattern to fix: ") -> Type: body" becomes ") -> Type:\n    body"
        pattern = r'(\)\s*->\s*[\w\[\]|, ]+):\s*(.+)'
        match = re.search(pattern, line)
        if match:
            signature = match.group(1)
            body = match.group(2).strip()
            # Don't split if it's a docstring or comment
            if body and not body.startswith('"""') and not body.startswith('#'):
                # Get the current indentation
                indent = len(line) - len(line.lstrip())
                fixed_lines.append(line[:indent] + signature + ':')
                fixed_lines.append(' ' * (indent + 4) + body)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def check_and_fix_file(filepath: Path) -> Tuple[bool, Optional[str], bool]:
    """
    Check a Python file for syntax errors and attempt to fix common ones.
    Returns: (has_error, error_msg, was_fixed)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # First check if file has syntax errors
        try:
            ast.parse(original_content)
            return False, None, False  # No errors
        except SyntaxError:
            pass  # Continue to try fixing
        
        # Try to fix common issues
        fixed_content = fix_malformed_function_signatures(original_content)
        
        # Check if fixes resolved the syntax error
        try:
            ast.parse(fixed_content)
            # Fixes worked! Write back the fixed content
            if fixed_content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)
                return False, None, True  # Fixed successfully
            else:
                return True, "Syntax error not fixable automatically", False
        except SyntaxError as e:
            return True, f"{e.msg} at line {e.lineno}", False
            
    except Exception as e:
        return True, str(e), False

def process_directory(root_dir: Path, exclude_dirs: set = None) -> Tuple[int, int, int]:
    """
    Process all Python files in directory, fixing what we can.
    Returns: (total_files, files_with_errors, files_fixed)
    """
    if exclude_dirs is None:
        exclude_dirs = {'venv', '__pycache__', '.git', 'node_modules', '.venv', 'venv_linux',
                       'backup_20250903_042619', 'backup_dead_code_20250903_044305', 'archive'}
    
    total = 0
    errors = 0
    fixed = 0
    error_files = []
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                total += 1
                
                has_error, error_msg, was_fixed = check_and_fix_file(filepath)
                
                if was_fixed:
                    fixed += 1
                    print(f"✓ Fixed: {filepath.relative_to(root_dir)}")
                elif has_error:
                    errors += 1
                    error_files.append((filepath.relative_to(root_dir), error_msg))
    
    if error_files:
        print("\nFiles still with errors after fix attempts:")
        for path, msg in error_files[:20]:  # Show first 20
            print(f"  {path}: {msg}")
        if len(error_files) > 20:
            print(f"  ... and {len(error_files) - 20} more")
    
    return total, errors, fixed

def main():
    root_dir = Path('/home/omar/Documents/ruleIQ')
    
    print("Scanning and fixing Python syntax errors...")
    total, errors, fixed = process_directory(root_dir)
    
    print(f"\n📊 Summary:")
    print(f"  Total Python files: {total}")
    print(f"  Files fixed: {fixed}")
    print(f"  Files still with errors: {errors}")
    print(f"  Files now valid: {total - errors}")
    
    if errors == 0:
        print("\n🎉 All Python files now have valid syntax!")
    else:
        print(f"\n⚠️ {errors} files still need manual fixing")
    
    return 0 if errors == 0 else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())