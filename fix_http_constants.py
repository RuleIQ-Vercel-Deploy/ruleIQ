#!/usr/bin/env python3
import os
import re

# HTTP status constants
HTTP_CONSTANTS = """
# HTTP Status Constants
HTTP_OK = 200
HTTP_CREATED = 201
HTTP_ACCEPTED = 202
HTTP_NO_CONTENT = 204
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_METHOD_NOT_ALLOWED = 405
HTTP_CONFLICT = 409
HTTP_UNPROCESSABLE_ENTITY = 422
HTTP_TOO_MANY_REQUESTS = 429
HTTP_INTERNAL_SERVER_ERROR = 500
HTTP_NOT_IMPLEMENTED = 501
HTTP_BAD_GATEWAY = 502
HTTP_SERVICE_UNAVAILABLE = 503
HTTP_GATEWAY_TIMEOUT = 504
"""

def add_http_constants(file_path):
    """Add HTTP constants after imports if they're used but not defined"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if HTTP constants are used but not defined
    needs_constants = False
    for const in ['HTTP_OK', 'HTTP_INTERNAL_SERVER_ERROR', 'HTTP_SERVICE_UNAVAILABLE', 
                  'HTTP_UNAUTHORIZED', 'HTTP_NOT_FOUND']:
        if const in content and f'{const} =' not in content:
            needs_constants = True
            break
    
    if needs_constants:
        # Find where to insert (after imports)
        lines = content.split('\n')
        insert_line = 0
        
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith(('import ', 'from ')):
                if i > 0 and (lines[i-1].startswith('import ') or lines[i-1].startswith('from ')):
                    insert_line = i
                    break
        
        if insert_line > 0:
            lines.insert(insert_line, HTTP_CONSTANTS)
            new_content = '\n'.join(lines)
            
            with open(file_path, 'w') as f:
                f.write(new_content)
            return True
    
    return False

# Files that need HTTP constants
files = [
    'api/main.py',
    'api/routers/agentic_rag.py',
    'api/routers/admin/token_management.py',
]

for file_path in files:
    if os.path.exists(file_path):
        if add_http_constants(file_path):
            print(f"Added HTTP constants to: {file_path}")
        else:
            print(f"No constants needed in: {file_path}")
