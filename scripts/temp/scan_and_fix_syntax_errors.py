#!/usr/bin/env python3
"""
Comprehensive script to scan and fix Python syntax errors in the codebase.
"""
import os
import ast
import re
from pathlib import Path
from typing import List, Tuple, Dict

def find_python_files(directory: str) -> List[Path]:
    """Find all Python files in the directory."""
    path = Path(directory)
    if not path.exists():
        return []
    return list(path.rglob("*.py"))

def check_syntax(filepath: Path) -> Tuple[bool, str, int]:
    """Check if a Python file has valid syntax, return error line number."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True, "", 0
    except SyntaxError as e:
        return False, str(e), e.lineno if e.lineno else 0
    except Exception as e:
        return False, f"Error reading file: {e}", 0

def fix_function_body_on_same_line(lines: List[str]) -> Tuple[List[str], int]:
    """Fix function signatures where body is on the same line as the signature."""
    fixed_lines = []
    fixes_count = 0
    
    for i, line in enumerate(lines):
        # Pattern: function signature ending with ") -> Type: statement"
        match = re.match(r'^(.*\))\s*->\s*([^:]+):\s+(.+)$', line)
        if match and ('def ' in line or (i > 0 and 'def ' in lines[i-1])):
            groups = match.groups()
            # Fix by splitting into signature and body
            fixed_lines.append(f"{groups[0]} -> {groups[1]}:")
            # Add proper indentation for body
            indent = len(line) - len(line.lstrip())
            fixed_lines.append(f"{' ' * (indent + 4)}{groups[2]}")
            fixes_count += 1
        else:
            fixed_lines.append(line)
    
    return fixed_lines, fixes_count

def fix_multiline_function_signature(lines: List[str]) -> Tuple[List[str], int]:
    """Fix multiline function signatures that have body on same line."""
    fixed_lines = []
    fixes_count = 0
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check for function definition that spans multiple lines
        if ('async def ' in line or 'def ' in line) and ') ->' in line:
            # Check if the line has both signature and body
            match = re.match(r'^(.*\)\s*->\s*[^:]+):\s+(.+)$', line)
            if match:
                signature = match.group(1)
                body = match.group(2)
                
                # Only fix if body is not a docstring or comment
                if not body.strip().startswith('"""') and not body.strip().startswith('#'):
                    fixed_lines.append(signature + ":")
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(f"{' ' * (indent + 4)}{body}")
                    fixes_count += 1
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
        i += 1
    
    return fixed_lines, fixes_count

def scan_directory(directory: str) -> Dict[str, List[Tuple[Path, str, int]]]:
    """Scan directory for Python files with syntax errors."""
    results = {
        'errors': [],
        'fixed': [],
        'failed': []
    }
    
    python_files = find_python_files(directory)
    
    for filepath in python_files:
        # Skip test files, migrations, and backup directories
        if any(skip in str(filepath) for skip in ['test', 'migration', 'backup', '__pycache__']):
            continue
        
        valid, error, line_no = check_syntax(filepath)
        if not valid:
            results['errors'].append((filepath, error, line_no))
    
    return results

def fix_file(filepath: Path) -> Tuple[bool, int, str]:
    """Attempt to fix syntax errors in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        # Apply various fixes
        lines, fix1 = fix_function_body_on_same_line(lines)
        lines, fix2 = fix_multiline_function_signature(lines)
        
        total_fixes = fix1 + fix2
        
        if total_fixes > 0:
            # Write fixed content
            fixed_content = '\n'.join(lines)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            # Verify the fix
            valid, error, _ = check_syntax(filepath)
            if valid:
                return True, total_fixes, ""
            else:
                # Revert if fix failed
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                return False, 0, error
        
        return False, 0, "No fixes applied"
    
    except Exception as e:
        return False, 0, str(e)

def main():
    """Main function to scan and fix syntax errors."""
    directories = [
        "api",
        "services",
        "utils",
        "database",
        "config",
        "middleware",
        "langgraph_agent",
        "infrastructure",
        "monitoring"
    ]
    
    print("=== Scanning for Python Syntax Errors ===\n")
    
    all_errors = []
    for directory in directories:
        results = scan_directory(directory)
        if results['errors']:
            print(f"\n{directory}/ - Found {len(results['errors'])} files with errors:")
            for filepath, error, line_no in results['errors']:
                all_errors.append((filepath, error, line_no))
                print(f"  - {filepath} (line {line_no})")
                # Show first part of error
                error_msg = error.split('\n')[0][:100]
                print(f"    Error: {error_msg}...")
    
    if not all_errors:
        print("\n✓ No syntax errors found!")
        return True
    
    print(f"\n=== Attempting to fix {len(all_errors)} files ===\n")
    
    fixed_count = 0
    failed_fixes = []
    
    for filepath, original_error, line_no in all_errors:
        print(f"Fixing {filepath}...")
        success, fixes, error = fix_file(filepath)
        if success:
            print(f"  ✓ Fixed {fixes} issues")
            fixed_count += 1
        else:
            print(f"  ✗ Failed to fix: {error[:100]}...")
            failed_fixes.append((filepath, error))
    
    print(f"\n=== Summary ===")
    print(f"Total files with errors: {len(all_errors)}")
    print(f"Successfully fixed: {fixed_count}")
    print(f"Failed to fix: {len(failed_fixes)}")
    
    if failed_fixes:
        print(f"\nFiles that still need manual fixing:")
        for filepath, error in failed_fixes:
            print(f"  - {filepath}")
    
    # Final verification
    print("\n=== Final Verification ===")
    remaining_errors = 0
    for directory in directories:
        results = scan_directory(directory)
        remaining_errors += len(results['errors'])
    
    if remaining_errors == 0:
        print("✓ All syntax errors have been fixed!")
        return True
    else:
        print(f"✗ {remaining_errors} files still have syntax errors")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)