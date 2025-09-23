#!/usr/bin/env python3
"""Fix broken multiline f-strings in Python files."""

import os
import re
from pathlib import Path

def fix_broken_fstrings(filepath):
    """Fix broken multiline f-strings in a file."""
    with open(filepath, 'r') as f:
        lines = f.readlines()

    fixed = False
    i = 0
    while i < len(lines):
        line = lines[i]

        # Check if this line has an f-string that opens but doesn't close
        if re.match(r'\s*f"[^"]*\{$', line.strip()):
            # Found a broken f-string, collect the full string
            start_i = i
            indent = len(line) - len(line.lstrip())
            parts = [line.rstrip()]

            i += 1
            while i < len(lines):
                next_line = lines[i]
                parts.append(next_line.strip())

                # Check if this line closes the f-string
                if '")' in next_line or '}"' in next_line:
                    # Found the end, join all parts
                    full_string = ''.join(parts)
                    # Remove extra whitespace and newlines
                    full_string = re.sub(r'\s+', ' ', full_string)

                    # Replace the multiline broken string with a single line
                    lines[start_i] = ' ' * indent + full_string + '\n'

                    # Remove the extra lines
                    for j in range(start_i + 1, i + 1):
                        lines[j] = ''

                    fixed = True
                    break
                i += 1
        else:
            i += 1

    if fixed:
        with open(filepath, 'w') as f:
            f.writelines([line for line in lines if line])
        return True
    return False

def main():
    """Find and fix all Python files with broken f-strings."""
    problematic_files = [
        'services/ai/instruction_monitor.py',
        'api/middleware/rate_limiter.py',
        'config/cache.py',
    ]

    for filepath in problematic_files:
        if os.path.exists(filepath):
            print(f"Checking {filepath}...")
            if fix_broken_fstrings(filepath):
                print(f"  Fixed broken f-strings in {filepath}")
            else:
                print(f"  No broken f-strings found in {filepath}")

    # Also search for other files with potential issues
    for path in Path('.').rglob('*.py'):
        if str(path) not in problematic_files:
            try:
                with open(path, 'r') as f:
                    content = f.read()
                    if re.search(r'f"[^"]*\{$', content, re.MULTILINE):
                        print(f"Found potential issue in {path}")
                        if fix_broken_fstrings(str(path)):
                            print(f"  Fixed {path}")
            except:
                pass

if __name__ == "__main__":
    main()