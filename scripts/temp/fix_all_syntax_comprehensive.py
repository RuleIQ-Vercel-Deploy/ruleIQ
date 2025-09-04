#!/usr/bin/env python3
"""Comprehensive fix for all Python syntax errors in the codebase"""
import os
import re
import ast
from pathlib import Path

def fix_file(filepath):
    """Fix syntax errors in a single file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Try to parse first
        try:
            ast.parse(content)
            return True, "Already valid"
        except:
            pass
        
        lines = content.split('\n')
        fixed_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Fix pattern: function signature with body on same line
            # Match: ") ->Type: statement" or ") -> Type: statement"
            match = re.match(r'^(\s*.*\))\s*->\s*([^:]+):\s+(.+)$', line)
            if match:
                indent = len(line) - len(line.lstrip())
                signature = match.group(1).strip()
                return_type = match.group(2).strip()
                body = match.group(3)
                
                # Reconstruct properly
                fixed_lines.append(' ' * indent + signature + ' -> ' + return_type + ':')
                fixed_lines.append(' ' * indent + '    ' + body)
                i += 1
                continue
            
            # Fix pattern: class definition with attribute on same line
            match = re.match(r'^(\s*class\s+\w+\([^)]+\)):\s+(.+)$', line)
            if match:
                indent = len(line) - len(line.lstrip())
                class_def = match.group(1).strip()
                first_attr = match.group(2)
                
                fixed_lines.append(' ' * indent + class_def + ':')
                fixed_lines.append(' ' * (indent + 4) + first_attr)
                i += 1
                continue
            
            # Fix excessive indentation after function signature fix
            # If previous line ends with ":", current line should be indented exactly 4 spaces more
            if i > 0 and fixed_lines and fixed_lines[-1].rstrip().endswith(':'):
                prev_indent = len(fixed_lines[-1]) - len(fixed_lines[-1].lstrip())
                curr_indent = len(line) - len(line.lstrip())
                
                # If current line is indented 8 spaces more, reduce to 4
                if curr_indent == prev_indent + 8:
                    fixed_lines.append(' ' * (prev_indent + 4) + line.lstrip())
                    i += 1
                    continue
            
            fixed_lines.append(line)
            i += 1
        
        # Write back
        fixed_content = '\n'.join(fixed_lines)
        
        # Verify it parses
        try:
            ast.parse(fixed_content)
            with open(filepath, 'w') as f:
                f.write(fixed_content)
            return True, "Fixed"
        except Exception as e:
            return False, str(e)
            
    except Exception as e:
        return False, str(e)

# Fix critical files
files_to_fix = [
    'api/routers/readiness.py',
    'api/routers/business_profiles.py',
    'api/routers/integrations.py',
    'api/routers/implementation.py',
    'api/utils/retry.py',
    'services/assessment_service.py',
    'services/readiness_service.py',
]

print("=== Fixing Python Syntax Errors ===\n")

for filepath in files_to_fix:
    if os.path.exists(filepath):
        success, msg = fix_file(filepath)
        if success:
            print(f"✓ {filepath}: {msg}")
        else:
            print(f"✗ {filepath}: {msg}")
    else:
        print(f"- {filepath}: Not found")

print("\n=== Verification ===")

# Try to collect tests again
import subprocess
result = subprocess.run(
    ['.venv/bin/python', '-m', 'pytest', '--collect-only'],
    capture_output=True,
    text=True,
    timeout=10
)

# Count collected tests
if 'collected' in result.stdout:
    for line in result.stdout.split('\n'):
        if 'collected' in line:
            print(line)
            break