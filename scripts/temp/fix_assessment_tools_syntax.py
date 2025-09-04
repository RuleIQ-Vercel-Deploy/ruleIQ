#!/usr/bin/env python3
"""Fix syntax errors in assessment_tools.py"""

import re

file_path = "services/ai/assessment_tools.py"

# Read the file
with open(file_path, 'r') as f:
    content = f.read()

# Fix pattern 1: Return type split across lines with docstring in between
# Pattern: ->Type[\n    """docstring"""\n    remaining]:
pattern1 = r'(\s+def\s+\w+\([^)]*\))\s*->\s*([A-Za-z]+)\[\s*\n\s*"""([^"]+)"""\s*\n\s*([^]]+)\]:'
replacement1 = r'\1 -> \2[\4]:\n        """\3"""'

content = re.sub(pattern1, replacement1, content)

# Fix pattern 2: Return type split without docstring
# Pattern: ->Type[\n    remaining]:
pattern2 = r'(\s+def\s+\w+\([^)]*\))\s*->\s*([A-Za-z]+)\[\s*\n\s*([^]]+)\]:'
replacement2 = r'\1 -> \2[\3]:'

content = re.sub(pattern2, replacement2, content)

# Write back
with open(file_path, 'w') as f:
    f.write(content)

print(f"Fixed syntax errors in {file_path}")