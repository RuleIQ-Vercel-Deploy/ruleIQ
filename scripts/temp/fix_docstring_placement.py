#!/usr/bin/env python3
"""Fix misplaced docstrings after if/for/while statements."""

import re
import sys
from pathlib import Path

def fix_docstring_placement(file_path):
    """Fix misplaced docstrings in a Python file."""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    fixed_lines = []
    i = 0
    changes_made = False
    
    while i < len(lines):
        line = lines[i]
        
        # Check if current line is an if/for/while/def/class statement
        if re.match(r'^(\s*)(if |for |while |def |class |elif |else:|except |try:|finally:|with )', line):
            indent = len(line) - len(line.lstrip())
            
            # Check if next line exists and is a docstring at wrong indentation
            if i + 1 < len(lines):
                next_line = lines[i + 1]
                next_indent = len(next_line) - len(next_line.lstrip())
                
                # Check for misplaced docstring (same or less indentation)
                if (next_line.strip().startswith('"""') and 
                    next_indent <= indent):
                    
                    # This is a misplaced docstring
                    docstring = next_line
                    
                    # Add the current line
                    fixed_lines.append(line)
                    
                    # Skip the misplaced docstring and get the actual code
                    if i + 2 < len(lines):
                        actual_code = lines[i + 2]
                        
                        # Add properly indented docstring first
                        proper_indent = ' ' * (indent + 4)
                        fixed_docstring = proper_indent + docstring.strip() + '\n'
                        fixed_lines.append(fixed_docstring)
                        
                        # Then add the actual code
                        fixed_lines.append(actual_code)
                        
                        i += 3  # Skip all three lines we've processed
                        changes_made = True
                        continue
            
        fixed_lines.append(line)
        i += 1
    
    if changes_made:
        with open(file_path, 'w') as f:
            f.writelines(fixed_lines)
        return True
    return False

def main():
    """Fix docstring placement in all test files."""
    test_files = list(Path('tests').rglob('*.py'))
    test_files.extend(list(Path('database').rglob('*.py')))
    test_files.extend(list(Path('api').rglob('*.py')))
    
    fixed_count = 0
    for file_path in test_files:
        try:
            if fix_docstring_placement(file_path):
                print(f"Fixed: {file_path}")
                fixed_count += 1
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    main()