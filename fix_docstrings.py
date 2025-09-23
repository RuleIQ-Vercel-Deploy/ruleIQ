#!/usr/bin/env python3
import re
import os

def fix_docstring(file_path):
    """Fix malformed docstrings that contain code"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Pattern to match docstrings with code inside
    pattern = r'^"""[\s\S]*?"""'
    
    match = re.match(pattern, content)
    if not match:
        return False
        
    docstring = match.group(0)
    
    # Check if there's code inside the docstring (imports, constants, etc.)
    if 'import ' in docstring or '=' in docstring and docstring.count('\n') > 3:
        # Extract the actual documentation part
        lines = docstring.split('\n')
        doc_lines = []
        code_lines = []
        in_code = False
        
        for line in lines[1:-1]:  # Skip the """ markers
            if not in_code and (line.strip().startswith('import ') or 
                               line.strip().startswith('from ') or
                               '=' in line or
                               line.strip().startswith('#')):
                in_code = True
            
            if in_code:
                code_lines.append(line)
            elif line.strip() and not line.strip().startswith(('import', 'from', '#')):
                doc_lines.append(line)
        
        # Rebuild the file
        if code_lines:
            new_docstring = '"""'
            for line in doc_lines:
                if line.strip():
                    new_docstring += '\n' + line
            new_docstring += '\n"""'
            
            # Add extracted code after docstring
            code_part = '\n'.join(code_lines)
            
            new_content = new_docstring + '\n\n' + code_part + content[len(match.group(0)):]
            
            with open(file_path, 'w') as f:
                f.write(new_content)
            return True
    return False

# Files to fix
files_to_fix = [
    'api/middleware/cost_tracking_middleware.py',
    'api/middleware/ai_rate_limiter.py',
    'api/middleware/rbac_middleware.py',
    'api/middleware/security_middleware.py',
    'services/session_management.py',
    'services/webhook_verification.py',
    'services/performance_monitor.py',
    'services/rag_fact_checker.py',
]

for file_path in files_to_fix:
    if os.path.exists(file_path):
        if fix_docstring(file_path):
            print(f"Fixed: {file_path}")
        else:
            print(f"No fix needed: {file_path}")
    else:
        print(f"Not found: {file_path}")
