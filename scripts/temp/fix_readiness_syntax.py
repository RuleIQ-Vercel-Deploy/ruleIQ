#!/usr/bin/env python3
"""Fix syntax errors in api/routers/readiness.py"""
import re

with open('api/routers/readiness.py', 'r') as f:
    content = f.read()

# Split into lines for processing
lines = content.split('\n')
fixed_lines = []

for line in lines:
    # Pattern: function signature ending with ") ->Type: body"
    # Need to add newline after the colon
    match = re.match(r'^(.*\))\s*->\s*([^:]+):\s+(.+)$', line)
    if match:
        # Split into signature and body
        signature = f"{match.group(1)} ->{match.group(2)}:"
        body = match.group(3)
        
        # Get indentation of current line
        indent_match = re.match(r'^(\s*)', line)
        current_indent = indent_match.group(1) if indent_match else ''
        
        # Body should be indented 4 spaces more
        fixed_lines.append(signature)
        fixed_lines.append(current_indent + '    ' + body)
    else:
        fixed_lines.append(line)

# Write back the fixed content
with open('api/routers/readiness.py', 'w') as f:
    f.write('\n'.join(fixed_lines))

print("Fixed api/routers/readiness.py")