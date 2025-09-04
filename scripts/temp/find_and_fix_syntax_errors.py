#!/usr/bin/env python3
"""
Find and fix specific Python syntax error pattern where function body is on same line as signature.
"""
import os
import re
import ast
from pathlib import Path
from typing import List, Tuple

def scan_file_for_pattern(filepath: Path) -> List[Tuple[int, str]]:
    """Scan a file for the specific pattern of body on same line as signature."""
    issues = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, 1):
            # Pattern 1: Function definition with body on same line after ->Type:
            # Matches: ") -> Type: statement" where statement is not just whitespace or comment
            if re.search(r'\)\s*->\s*[^:]+:\s+\S', line):
                # Verify it's not a docstring or comment
                match = re.search(r'\)\s*->\s*[^:]+:\s+(.+)$', line)
                if match:
                    remainder = match.group(1).strip()
                    if not remainder.startswith('"""') and not remainder.startswith('#'):
                        issues.append((i, line.strip()))
            
            # Pattern 2: Look for specific known issue patterns
            # Where a function body starts immediately after the colon
            if 'Depends(get_db))' in line and '->' in line and ':' in line:
                # Check if there's non-whitespace after the colon
                colon_idx = line.rfind(':')
                if colon_idx != -1 and colon_idx < len(line) - 1:
                    remainder = line[colon_idx + 1:].strip()
                    if remainder and not remainder.startswith('#'):
                        issues.append((i, line.strip()))
    
    except Exception as e:
        print(f"Error scanning {filepath}: {e}")
    
    return issues

def fix_file_with_pattern(filepath: Path) -> bool:
    """Fix the specific pattern in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        fixed_lines = []
        changed = False
        
        for i, line in enumerate(lines):
            # Check for the pattern: function signature with body on same line
            match = re.match(r'^(.*\)\s*->\s*[^:]+):\s+(.+)$', line)
            
            if match:
                signature = match.group(1)
                body = match.group(2)
                
                # Check if body is actual code (not docstring or comment)
                if not body.strip().startswith('"""') and not body.strip().startswith('#'):
                    # Split into two lines
                    fixed_lines.append(signature + ':\n')
                    
                    # Calculate proper indentation
                    indent = len(line) - len(line.lstrip())
                    fixed_lines.append(' ' * (indent + 4) + body + '\n')
                    changed = True
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        
        if changed:
            # Write the fixed content
            with open(filepath, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)
            
            # Verify the file now parses correctly
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    ast.parse(f.read())
                return True
            except SyntaxError:
                # Revert if fix didn't work
                with open(filepath, 'r', encoding='utf-8') as f:
                    f.writelines(lines)
                return False
        
        return False
    
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False

def main():
    """Main function to find and fix syntax errors."""
    directories = [
        "api/routers",
        "api/utils",
        "api/dependencies",
        "api/middleware",
        "services",
        "services/ai",
        "utils",
        "database",
        "config",
        "middleware"
    ]
    
    print("=== Scanning for Function Body on Same Line Pattern ===\n")
    
    all_issues = []
    
    for directory in directories:
        if not os.path.exists(directory):
            continue
        
        python_files = list(Path(directory).rglob("*.py"))
        
        for filepath in python_files:
            # Skip test and backup files
            if any(skip in str(filepath) for skip in ['test', 'backup', '__pycache__']):
                continue
            
            issues = scan_file_for_pattern(filepath)
            if issues:
                print(f"\n{filepath}:")
                for line_no, line_content in issues:
                    all_issues.append((filepath, line_no))
                    print(f"  Line {line_no}: {line_content[:100]}...")
    
    if not all_issues:
        print("\n✓ No syntax pattern issues found!")
        return
    
    print(f"\n=== Found {len(all_issues)} potential issues ===")
    
    # Now try to fix them
    print("\n=== Attempting fixes ===\n")
    
    fixed_files = set()
    for filepath, _ in all_issues:
        if filepath not in fixed_files:
            print(f"Fixing {filepath}...")
            if fix_file_with_pattern(filepath):
                print(f"  ✓ Fixed")
                fixed_files.add(filepath)
            else:
                print(f"  ✗ Failed to fix")
    
    print(f"\n=== Summary ===")
    print(f"Files processed: {len(fixed_files)}")
    
    # Final check - verify all files parse
    print("\n=== Final Syntax Check ===")
    error_count = 0
    
    for directory in directories:
        if not os.path.exists(directory):
            continue
        
        python_files = list(Path(directory).rglob("*.py"))
        
        for filepath in python_files:
            if any(skip in str(filepath) for skip in ['test', 'backup', '__pycache__']):
                continue
            
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    ast.parse(f.read())
            except SyntaxError as e:
                error_count += 1
                print(f"  ✗ {filepath} - Line {e.lineno}: {e.msg}")
    
    if error_count == 0:
        print("\n✓ All files parse successfully!")
    else:
        print(f"\n✗ {error_count} files still have syntax errors")

if __name__ == "__main__":
    main()