#!/usr/bin/env python3
"""Final comprehensive syntax fix - targets all remaining syntax errors."""

import ast
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Known files with persistent issues based on common patterns
KNOWN_PROBLEM_PATTERNS = {
    'api/routers/': 'Router files with malformed function signatures',
    'services/': 'Service files with improper indentation',
    'database/': 'Database models with syntax issues',
    'tests/': 'Test files with various syntax problems'
}

def fix_malformed_return_types(content: str) -> str:
    """Fix function signatures with malformed return types and body on same line."""
    lines = content.split('\n')
    fixed = []
    
    for line in lines:
        # Multiple patterns to catch various malformations
        patterns = [
            # Pattern 1: ) -> Type: body
            (r'(\)\s*->\s*[\w\[\]|,\s\(\)]+):\s+([^#\s].+)', r'\1:\n    \2'),
            # Pattern 2: ) ->Type:body (no space)
            (r'(\)\s*->[\w\[\]|,\s\(\)]+):\s*([^#\s].+)', r'\1:\n    \2'),
            # Pattern 3: def func() ->Type: return
            (r'(def\s+\w+\([^)]*\)\s*->\s*[\w\[\]|,\s\(\)]+):\s+([^#\s].+)', r'\1:\n    \2'),
        ]
        
        fixed_line = line
        for pattern, replacement in patterns:
            if re.search(pattern, line):
                # Get indentation
                indent = len(line) - len(line.lstrip())
                # Apply fix with proper indentation
                fixed_line = re.sub(pattern, lambda m: line[:indent] + m.group(1) + ':\n' + ' ' * (indent + 4) + m.group(2), line)
                if fixed_line != line:
                    # Split and add both lines
                    parts = fixed_line.split('\n')
                    fixed.extend(parts)
                    break
        else:
            fixed.append(line)
    
    return '\n'.join(fixed)

def fix_docstring_placement(content: str) -> str:
    """Fix docstrings that are incorrectly placed."""
    lines = content.split('\n')
    fixed = []
    i = 0
    
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a function/class definition
        if re.match(r'\s*(def|class)\s+\w+', line):
            # Check if docstring is on same line after colon
            if '"""' in line and line.strip().endswith(':'):
                # Split into definition and docstring
                parts = line.split('"""')
                if len(parts) >= 2:
                    # Get indentation
                    indent = len(line) - len(line.lstrip())
                    fixed.append(parts[0].rstrip() + ':')
                    fixed.append(' ' * (indent + 4) + '"""' + '"""'.join(parts[1:]))
                else:
                    fixed.append(line)
            else:
                fixed.append(line)
        else:
            fixed.append(line)
        i += 1
    
    return '\n'.join(fixed)

def fix_class_attributes(content: str) -> str:
    """Fix class definitions with attributes on the same line."""
    lines = content.split('\n')
    fixed = []
    
    for line in lines:
        # Pattern: class Name: attribute = value
        match = re.match(r'(\s*class\s+\w+(?:\([^)]*\))?):\s*(\w+.+)', line)
        if match:
            indent = len(line) - len(line.lstrip())
            class_def = match.group(1)
            attributes = match.group(2)
            fixed.append(' ' * indent + class_def + ':')
            fixed.append(' ' * (indent + 4) + attributes)
        else:
            fixed.append(line)
    
    return '\n'.join(fixed)

def fix_improper_indentation(content: str) -> str:
    """Fix common indentation issues."""
    lines = content.split('\n')
    fixed = []
    expected_indent = 0
    
    for line in lines:
        stripped = line.lstrip()
        current_indent = len(line) - len(stripped)
        
        # Skip empty lines
        if not stripped:
            fixed.append(line)
            continue
        
        # Adjust expected indentation based on previous line
        if fixed and fixed[-1].rstrip().endswith(':'):
            expected_indent = current_indent + 4
        elif stripped.startswith(('return', 'pass', 'continue', 'break', 'raise')):
            # These statements typically end a block
            if current_indent > expected_indent:
                line = ' ' * expected_indent + stripped
        
        fixed.append(line)
        
        # Update expected indent for next line
        if not line.rstrip().endswith(':'):
            expected_indent = current_indent
    
    return '\n'.join(fixed)

def apply_all_fixes(filepath: Path) -> bool:
    """Apply all fix strategies to a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already valid
        try:
            ast.parse(content)
            return False  # Already valid
        except:
            pass
        
        # Apply all fixes in sequence
        fixed = content
        fixed = fix_malformed_return_types(fixed)
        fixed = fix_docstring_placement(fixed)
        fixed = fix_class_attributes(fixed)
        fixed = fix_improper_indentation(fixed)
        
        # Check if fixes worked
        try:
            ast.parse(fixed)
            # Success! Write the fixed content
            if fixed != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(fixed)
                return True
        except:
            pass
        
        return False
        
    except Exception:
        return False

def get_import_errors() -> List[str]:
    """Get list of modules with import errors from pytest."""
    result = subprocess.run(
        ['python', '-m', 'pytest', '--collect-only', '-q'],
        capture_output=True,
        text=True,
        cwd='/home/omar/Documents/ruleIQ'
    )
    
    errors = []
    for line in result.stderr.split('\n'):
        if 'ImportError' in line or 'SyntaxError' in line:
            # Try to extract module name
            match = re.search(r'from\s+(\S+)|import\s+(\S+)|in\s+"([^"]+)"', line)
            if match:
                module = match.group(1) or match.group(2) or match.group(3)
                if module:
                    errors.append(module)
    
    return errors

def main():
    root_dir = Path('/home/omar/Documents/ruleIQ')
    
    exclude_dirs = {
        'venv', '__pycache__', '.git', 'node_modules', '.venv', 'venv_linux',
        'backup_20250903_042619', 'backup_dead_code_20250903_044305', 'archive',
        '.pytest_cache', 'htmlcov', '.mypy_cache'
    }
    
    print("🚀 Final comprehensive syntax fix starting...\n")
    
    # First, get modules with import errors
    print("📋 Checking for import errors...")
    import_errors = get_import_errors()
    if import_errors:
        print(f"Found {len(import_errors)} modules with import errors")
    
    # Fix all Python files
    total = 0
    fixed = 0
    still_broken = []
    
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                total += 1
                
                if apply_all_fixes(filepath):
                    fixed += 1
                    print(f"✓ Fixed: {filepath.relative_to(root_dir)}")
                else:
                    # Check if still has errors
                    try:
                        with open(filepath, 'r') as f:
                            ast.parse(f.read())
                    except SyntaxError as e:
                        still_broken.append((filepath.relative_to(root_dir), f"Line {e.lineno}: {e.msg}"))
    
    # Final report
    print(f"\n📊 Final Summary:")
    print(f"  Total Python files: {total}")
    print(f"  Files fixed in this run: {fixed}")
    print(f"  Files still with syntax errors: {len(still_broken)}")
    print(f"  Files now valid: {total - len(still_broken)}")
    
    if still_broken:
        print(f"\n⚠️ {len(still_broken)} files still need manual fixing:")
        for path, error in still_broken[:10]:
            print(f"  {path}: {error}")
        if len(still_broken) > 10:
            print(f"  ... and {len(still_broken) - 10} more")
    
    # Final test collection check
    print("\n🧪 Final test collection check...")
    result = subprocess.run(
        ['python', '-m', 'pytest', '--collect-only', '-q'],
        capture_output=True,
        text=True,
        cwd=str(root_dir)
    )
    
    output = result.stdout + result.stderr
    
    # Look for collection count
    for line in output.split('\n'):
        if 'collected' in line.lower():
            print(f"  {line}")
            match = re.search(r'(\d+)\s+test', line.lower())
            if match:
                count = int(match.group(1))
                print(f"\n{'🎉' if count >= 2610 else '📈'} Test collection: {count}/2610 ({count*100//2610}%)")
                if count >= 2610:
                    print("✅ SUCCESS! All tests are now collecting!")
                    return 0
    
    # If we didn't find a count, show errors
    if 'error' in output.lower() or 'failed' in output.lower():
        print("\n❌ Some errors remain:")
        error_lines = [l for l in output.split('\n') if 'error' in l.lower()][:5]
        for line in error_lines:
            print(f"  {line}")
    
    return 1 if still_broken else 0

if __name__ == "__main__":
    sys.exit(main())