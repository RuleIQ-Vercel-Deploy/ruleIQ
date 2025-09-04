#!/usr/bin/env python3
"""Fix all syntax errors related to misplaced docstrings and broken multi-line statements."""

import re
from pathlib import Path

def fix_file_syntax(file_path):
    """Fix syntax errors in a Python file."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except:
        return False
    
    lines = content.split('\n')
    fixed_lines = []
    i = 0
    changes_made = False
    
    while i < len(lines):
        line = lines[i]
        
        # Check for common problem patterns
        if i + 2 < len(lines):
            next_line = lines[i + 1] if i + 1 < len(lines) else ""
            next_next_line = lines[i + 2] if i + 2 < len(lines) else ""
            
            # Pattern 1: Multi-line dict/call with docstring in the middle
            # e.g., kwargs.update({'host': cfg['host'], 'port': cfg['port'], 'db':
            #       """Docstring"""
            #       cfg['db']})
            if (line.rstrip().endswith((':')) and 
                not line.strip().startswith('#') and
                ('(' in line or '{' in line or '[' in line) and
                next_line.strip().startswith('"""') and 
                next_line.strip().endswith('"""')):
                
                # Remove the misplaced docstring and join the lines
                fixed_line = line.rstrip()[:-1] + ' ' + next_next_line.lstrip()
                fixed_lines.append(fixed_line)
                i += 3
                changes_made = True
                continue
            
            # Pattern 2: Function/class definition with misplaced docstring
            if (re.match(r'^\s*(def |class )', line) and
                i + 1 < len(lines) and
                not lines[i + 1].strip().startswith('"""')):
                # Check if there's a docstring in wrong place within next 3 lines
                for j in range(i + 1, min(i + 4, len(lines))):
                    if lines[j].strip().startswith('"""') and lines[j].strip().endswith('"""'):
                        # Found misplaced docstring
                        indent = len(line) - len(line.lstrip())
                        proper_indent = ' ' * (indent + 4)
                        
                        # Add function/class line
                        fixed_lines.append(line)
                        # Add properly indented docstring
                        fixed_lines.append(proper_indent + lines[j].strip())
                        
                        # Add remaining lines (skip the misplaced docstring)
                        for k in range(i + 1, j):
                            fixed_lines.append(lines[k])
                        for k in range(j + 1, min(i + 4, len(lines))):
                            fixed_lines.append(lines[k])
                        
                        i = min(i + 4, len(lines))
                        changes_made = True
                        break
                else:
                    fixed_lines.append(line)
                    i += 1
            else:
                fixed_lines.append(line)
                i += 1
        else:
            fixed_lines.append(line)
            i += 1
    
    if changes_made:
        with open(file_path, 'w') as f:
            f.write('\n'.join(fixed_lines))
        return True
    return False

def main():
    """Fix syntax errors in all Python files."""
    # Focus on problem files first
    problem_files = [
        'tests/mock_service_proxy.py',
        'tests/fixtures/database.py',
        'tests/conftest_optimized.py',
        'database/report_schedule.py'
    ]
    
    for file_path in problem_files:
        if Path(file_path).exists():
            try:
                if fix_file_syntax(file_path):
                    print(f"Fixed: {file_path}")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
    
    # Then process all test files
    for pattern in ['tests/**/*.py', 'database/**/*.py', 'api/**/*.py']:
        for file_path in Path('.').glob(pattern):
            if str(file_path) not in problem_files:
                try:
                    if fix_file_syntax(file_path):
                        print(f"Fixed: {file_path}")
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

if __name__ == "__main__":
    main()