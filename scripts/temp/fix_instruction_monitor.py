#!/usr/bin/env python3
"""Fix all syntax errors in instruction_monitor.py"""

import re

with open('services/ai/instruction_monitor.py', 'r') as f:
    lines = f.readlines()

fixed_lines = []
i = 0
while i < len(lines):
    line = lines[i].rstrip()
    
    # Check if this is a function def without : at the end
    if re.match(r'^\s*def\s+\w+.*[^:]$', line):
        # Look ahead for docstring
        if i + 1 < len(lines) and '"""' in lines[i + 1]:
            # We have a split function definition with docstring in between
            # Collect the full function signature
            sig_lines = [line]
            j = i + 1
            
            # Skip over the docstring lines and find the rest of the signature
            while j < len(lines):
                if '"""' in lines[j] and j > i + 1:  # Found closing docstring
                    # Look for the rest of the signature after docstring
                    k = j + 1
                    while k < len(lines) and not lines[k].strip().startswith('def '):
                        if ') ->' in lines[k] or ')-> ' in lines[k]:
                            # Found rest of signature
                            sig_lines.append(lines[k].rstrip())
                            
                            # Reconstruct the complete signature
                            full_sig = ' '.join(sig_lines).strip()
                            if not full_sig.endswith(':'):
                                full_sig += ':'
                            
                            # Add the fixed signature
                            fixed_lines.append(full_sig)
                            
                            # Now add the docstring starting from i+1
                            fixed_lines.append(lines[i + 1].rstrip())  # Opening docstring
                            
                            # Add docstring body
                            m = i + 2
                            while m <= j:
                                fixed_lines.append(lines[m].rstrip())
                                m += 1
                            
                            # Skip to after where we found the rest of signature
                            i = k + 1
                            break
                        k += 1
                    break
                j += 1
                
            if i == k + 1:  # We successfully fixed this
                continue
                
    # Also check for patterns like: def func() -> Type: body
    # These should have body on next line
    match = re.match(r'^(\s*def\s+.*\))\s*->\s*([^:]+):\s+(.+)$', line)
    if match:
        indent = len(line) - len(line.lstrip())
        signature = match.group(1).strip()
        return_type = match.group(2).strip()
        body = match.group(3)
        
        fixed_lines.append(' ' * indent + signature + ' -> ' + return_type + ':')
        fixed_lines.append(' ' * (indent + 4) + body)
        i += 1
        continue
    
    # Also fix patterns where docstring is between function parts
    if i + 2 < len(lines):
        if 'def ' in line and not line.rstrip().endswith(':'):
            if '"""' in lines[i + 1] and not '"""' in lines[i + 1].replace('"""', '', 1):
                # Single line in between
                next_part_idx = i + 2
                if ') ->' in lines[next_part_idx] or 'Optional[' in lines[next_part_idx]:
                    # Reconstruct
                    full_sig = line.rstrip() + ' ' + lines[next_part_idx].strip()
                    if not full_sig.endswith(':'):
                        full_sig += ':'
                    fixed_lines.append(full_sig)
                    fixed_lines.append(lines[i + 1].rstrip())  # Add docstring
                    i = next_part_idx + 1
                    continue
    
    fixed_lines.append(line)
    i += 1

# Write back
with open('services/ai/instruction_monitor.py', 'w') as f:
    f.write('\n'.join(fixed_lines))

print("Fixed instruction_monitor.py")