#!/usr/bin/env python3
"""Fix all syntax errors in AI tools files"""

import os
import re

def fix_file(file_path):
    """Fix syntax errors in a single file"""
    print(f"Fixing {file_path}...")
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    fixed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for function definition that might have issues
        if 'def ' in line and '(' in line:
            # Collect the full function signature
            full_sig = line
            j = i + 1
            
            # Keep reading until we find the closing parenthesis
            while j < len(lines) and ') ->' not in full_sig and '):' not in full_sig:
                full_sig += lines[j]
                j += 1
            
            # Check if there's a docstring interrupting the signature
            if j < len(lines) and '"""' in lines[j]:
                # We have a docstring in the middle of the signature
                docstring_line = lines[j]
                j += 1
                
                # Check if the return type is on the next line
                if j < len(lines) and (') ->' in lines[j] or '):' in lines[j]):
                    return_line = lines[j].strip()
                    
                    # Reconstruct the function properly
                    # Remove the last line from full_sig if it's incomplete
                    full_sig_lines = full_sig.split('\n')
                    params_part = '\n'.join(full_sig_lines[:-1])
                    
                    # Fix the return type line
                    if 'try:' in return_line:
                        # Split at 'try:'
                        parts = return_line.split('try:')
                        return_part = parts[0].strip()
                        
                        # Reconstruct
                        fixed_lines.append(params_part)
                        fixed_lines.append(f"        {return_part}\n")
                        fixed_lines.append(f"        {docstring_line.strip()}\n")
                        fixed_lines.append("        try:\n")
                        i = j + 1
                    else:
                        # Normal case - just fix the order
                        fixed_lines.append(params_part)
                        fixed_lines.append(f"        {return_line}\n")
                        fixed_lines.append(f"        {docstring_line.strip()}\n")
                        i = j + 1
                else:
                    # No return type issue, keep as is
                    fixed_lines.append(line)
                    i += 1
            else:
                # Check for the ToolResult: try: pattern
                if '->ToolResult: try:' in line or '-> ToolResult: try:' in line:
                    # Fix this pattern
                    line = line.replace('->ToolResult: try:', '-> ToolResult:\n        try:')
                    line = line.replace('-> ToolResult: try:', '-> ToolResult:\n        try:')
                fixed_lines.append(line)
                i += 1
        else:
            fixed_lines.append(line)
            i += 1
    
    # Write back
    with open(file_path, 'w') as f:
        f.writelines(fixed_lines)
    
    print(f"Fixed {file_path}")

# Fix all AI tool files
ai_tools_dir = "services/ai"
tool_files = ["assessment_tools.py", "evidence_tools.py", "regulation_tools.py"]

for tool_file in tool_files:
    file_path = os.path.join(ai_tools_dir, tool_file)
    if os.path.exists(file_path):
        fix_file(file_path)