#!/usr/bin/env python3
"""Fix resource leaks - unclosed files, database connections, etc."""
import logging
logger = logging.getLogger(__name__)

from __future__ import annotations

from typing import Any
import os
import re

def fix_unclosed_files() -> Any:
    """Fix unclosed file handlers by using context managers."""
    
    files_fixed = 0
    issues_fixed = 0
    
    for root, dirs, files in os.walk('.'):
        # Skip virtual environments and node_modules
        if 'venv' in root or 'node_modules' in root or '__pycache__' in root:
            continue
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        lines = f.readlines()
                    
                    modified = False
                    new_lines = []
                    i = 0
                    
                    while i < len(lines):
                        line = lines[i]
                        
                        # Pattern 1: f = open(...) followed by operations
                        if re.match(r'^\s*(\w+)\s*=\s*open\([^)]+\)', line):
                            # Check if it's already in a with statement
                            prev_line = lines[i-1] if i > 0 else ''
                            if 'with' not in prev_line:
                                # Extract variable name and open statement
                                match = re.match(r'^(\s*)(\w+)\s*=\s*open\(([^)]+)\)', line)
                                if match:
                                    indent = match.group(1)
                                    var_name = match.group(2)
                                    open_args = match.group(3)
                                    
                                    # Convert to context manager
                                    new_lines.append(f"{indent}with open({open_args}) as {var_name}:\n")
                                    
                                    # Indent following lines that use this file
                                    i += 1
                                    while i < len(lines):
                                        next_line = lines[i]
                                        # Check if line uses the file variable
                                        if var_name in next_line and not next_line.strip().startswith('#'):
                                            # Add extra indentation
                                            if next_line.startswith(indent):
                                                new_lines.append('    ' + next_line)
                                            else:
                                                new_lines.append(next_line)
                                            i += 1
                                        elif next_line.strip() == '' or next_line.strip().startswith('#'):
                                            new_lines.append(next_line)
                                            i += 1
                                        else:
                                            # End of file operations
                                            break
                                    
                                    # Skip close() if present
                                    if i < len(lines) and f'{var_name}.close()' in lines[i]:
                                        i += 1
                                    
                                    modified = True
                                    issues_fixed += 1
                                    continue
                        
                        # Pattern 2: urllib.urlopen without context manager
                        if 'urlopen(' in line and 'with' not in line:
                            match = re.match(r'^(\s*)(\w+)\s*=\s*(.*urlopen\([^)]+\))', line)
                            if match:
                                indent = match.group(1)
                                var_name = match.group(2)
                                urlopen_call = match.group(3)
                                
                                new_lines.append(f"{indent}with {urlopen_call} as {var_name}:\n")
                                
                                # Indent following lines
                                i += 1
                                while i < len(lines) and lines[i].startswith(indent) and lines[i].strip():
                                    new_lines.append('    ' + lines[i])
                                    i += 1
                                
                                modified = True
                                issues_fixed += 1
                                continue
                        
                        new_lines.append(line)
                        i += 1
                    
                    if modified:
                        with open(filepath, 'w') as f:
                            f.writelines(new_lines)
                        files_fixed += 1
                        logger.info(f"✓ Fixed {filepath}")
                        
                except Exception as e:
                    logger.info(f"Error processing {filepath}: {e}")
    
    logger.info(f"\n✅ Fixed {issues_fixed} resource leaks in {files_fixed} files")

def fix_session_issues() -> Any:
    """Fix database session issues - ensure proper closing."""
    
    files_fixed = 0
    
    for root, dirs, files in os.walk('.'):
        if 'venv' in root or 'node_modules' in root or '__pycache__' in root:
            continue
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                    
                    original_content = content
                    
                    # Pattern: Session() without context manager or try/finally
                    # Look for patterns like: session = Session() without proper cleanup
                    
                    # Add session.close() in finally blocks where missing
                    content = re.sub(
                        r'(try:\s*\n.*?session\s*=\s*[^)]+\(\).*?)(\n\s*except.*?:.*?)(\n\s*finally:(?!\s*session\.close))',  # noqa: E501
                        r'\1\2\3\n        session.close()',
                        content,
                        flags=re.DOTALL
                    )
                    
                    if content != original_content:
                        with open(filepath, 'w') as f:
                            f.write(content)
                        files_fixed += 1
                        logger.info(f"✓ Fixed session management in {filepath}")
                        
                except Exception as e:
                    pass
    
    if files_fixed > 0:
        logger.info(f"✅ Fixed session management in {files_fixed} files")

if __name__ == "__main__":
    logger.info("Fixing resource leaks...")
    fix_unclosed_files()
    fix_session_issues()