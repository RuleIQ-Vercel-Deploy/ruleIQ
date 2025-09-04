#!/usr/bin/env python3
"""Comprehensive script to fix common Python syntax errors in the codebase."""

import ast
import os
import re
from pathlib import Path
from typing import List, Tuple, Optional

def fix_function_signatures(content: str) -> str:
    """Fix malformed function signatures where body is on same line."""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Pattern 1: function definition with body on same line
        # Match: ") -> Type: body" or ") ->Type:body"
        pattern = r'(\)\s*->\s*[\w\[\]|,\s]+):\s*(.+)'
        match = re.search(pattern, line)
        
        if match:
            signature = match.group(1)
            body = match.group(2).strip()
            
            # Skip if it's a docstring or comment
            if body and not body.startswith('"""') and not body.startswith("'''") and not body.startswith('#'):
                # Get indentation
                indent = len(line) - len(line.lstrip())
                fixed_lines.append(line[:indent] + signature + ':')
                # Add proper indentation for body
                fixed_lines.append(' ' * (indent + 4) + body)
                continue
        
        # Pattern 2: property getter/setter with body on same line
        # Match: "def method(self) ->Type: return value"
        pattern2 = r'(def\s+\w+\s*\([^)]*\)\s*(?:->\s*[\w\[\]|,\s]+)?):\s*(.+)'
        match2 = re.search(pattern2, line)
        
        if match2:
            signature = match2.group(1)
            body = match2.group(2).strip()
            
            # Skip if it's a docstring or comment
            if body and not body.startswith('"""') and not body.startswith("'''") and not body.startswith('#'):
                # Get indentation
                indent = len(line) - len(line.lstrip())
                fixed_lines.append(line[:indent] + signature + ':')
                # Add proper indentation for body
                fixed_lines.append(' ' * (indent + 4) + body)
                continue
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_multiline_strings(content: str) -> str:
    """Fix issues with multiline strings and docstrings placement."""
    lines = content.split('\n')
    fixed_lines = []
    in_multiline = False
    multiline_char = None
    
    for i, line in enumerate(lines):
        # Check for start/end of multiline strings
        if '"""' in line or "'''" in line:
            if not in_multiline:
                # Starting a multiline string
                if '"""' in line:
                    multiline_char = '"""'
                else:
                    multiline_char = "'''"
                
                # Check if it closes on same line
                if line.count(multiline_char) >= 2:
                    # Single line docstring, leave as is
                    fixed_lines.append(line)
                else:
                    in_multiline = True
                    fixed_lines.append(line)
            else:
                # Ending a multiline string
                if multiline_char in line:
                    in_multiline = False
                    multiline_char = None
                fixed_lines.append(line)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_class_definitions(content: str) -> str:
    """Fix class definitions with attributes on same line."""
    lines = content.split('\n')
    fixed_lines = []
    
    for line in lines:
        # Pattern: class definition with attribute on same line
        # Match: "class Name: attribute = value"
        pattern = r'(class\s+\w+(?:\([^)]*\))?):\s*(\w+\s*=.+)'
        match = re.search(pattern, line)
        
        if match:
            class_def = match.group(1)
            attribute = match.group(2).strip()
            
            # Get indentation
            indent = len(line) - len(line.lstrip())
            fixed_lines.append(line[:indent] + class_def + ':')
            fixed_lines.append(' ' * (indent + 4) + attribute)
        else:
            fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def fix_file(filepath: Path) -> Tuple[bool, Optional[str], bool]:
    """
    Fix a Python file's syntax errors.
    Returns: (has_error, error_msg, was_fixed)
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Check if file already has valid syntax
        try:
            ast.parse(original_content)
            return False, None, False  # No errors
        except SyntaxError:
            pass  # Continue to fix
        
        # Apply fixes
        content = original_content
        content = fix_function_signatures(content)
        content = fix_multiline_strings(content)
        content = fix_class_definitions(content)
        
        # Check if fixes resolved the syntax error
        try:
            ast.parse(content)
            # Fixes worked!
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                return False, None, True  # Fixed successfully
            else:
                return True, "Syntax error not automatically fixable", False
        except SyntaxError as e:
            return True, f"{e.msg} at line {e.lineno}", False
            
    except Exception as e:
        return True, str(e), False

def main():
    root_dir = Path('/home/omar/Documents/ruleIQ')
    
    # Directories to exclude
    exclude_dirs = {
        'venv', '__pycache__', '.git', 'node_modules', '.venv', 'venv_linux',
        'backup_20250903_042619', 'backup_dead_code_20250903_044305', 'archive'
    }
    
    # Priority directories/files to fix first (commonly imported)
    priority_patterns = [
        'api/routers/*.py',
        'api/dependencies/*.py',
        'api/utils/*.py',
        'services/*.py',
        'database/*.py',
        'config/*.py'
    ]
    
    print("🔧 Starting comprehensive syntax fix...\n")
    
    total_files = 0
    fixed_files = 0
    error_files = []
    
    # Process files
    for root, dirs, files in os.walk(root_dir):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                total_files += 1
                
                has_error, error_msg, was_fixed = fix_file(filepath)
                
                if was_fixed:
                    fixed_files += 1
                    rel_path = filepath.relative_to(root_dir)
                    print(f"✓ Fixed: {rel_path}")
                elif has_error:
                    error_files.append((filepath.relative_to(root_dir), error_msg))
    
    print(f"\n📊 Summary:")
    print(f"  Total Python files: {total_files}")
    print(f"  Files fixed: {fixed_files}")
    print(f"  Files still with errors: {len(error_files)}")
    print(f"  Files now valid: {total_files - len(error_files)}")
    
    if error_files:
        print(f"\n⚠️ {len(error_files)} files still have errors:")
        for path, msg in error_files[:20]:  # Show first 20
            print(f"  {path}: {msg}")
        if len(error_files) > 20:
            print(f"  ... and {len(error_files) - 20} more")
    else:
        print("\n🎉 All Python files now have valid syntax!")
    
    # Run pytest collection check
    print("\n🧪 Checking test collection...")
    import subprocess
    result = subprocess.run(
        ['python', '-m', 'pytest', '--collect-only', '-q'],
        capture_output=True,
        text=True,
        cwd=str(root_dir)
    )
    
    output = result.stdout + result.stderr
    for line in output.split('\n'):
        if 'test' in line.lower() and 'collected' in line.lower():
            print(f"  {line}")
            # Try to extract count
            import re
            match = re.search(r'(\d+)\s+test', line.lower())
            if match:
                count = int(match.group(1))
                if count >= 2610:
                    print(f"\n🎉 SUCCESS! All {count} tests are now collecting!")
                else:
                    print(f"\n📈 Progress: {count}/2610 tests collecting ({count*100//2610}%)")
    
    return 0 if len(error_files) == 0 else 1

if __name__ == "__main__":
    import sys
    sys.exit(main())