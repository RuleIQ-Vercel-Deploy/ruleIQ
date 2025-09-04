#!/usr/bin/env python3
"""Fix datetime.now(timezone.utc) usage - replace with timezone-aware datetime."""
import logging
logger = logging.getLogger(__name__)


from __future__ import annotations

from typing import Any
import os
import re

def fix_datetime_utcnow() -> Any:
    """Replace datetime.now(timezone.utc) with timezone-aware datetime.now(timezone.utc)."""
    
    # Find all Python files
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip virtual environments and node_modules
        if 'venv' in root or 'node_modules' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    files_fixed = 0
    total_replacements = 0
    
    for filepath in python_files:
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            original_content = content
            
            # Check if file uses datetime.now(timezone.utc)
            if 'datetime.now(timezone.utc)' in content or 'datetime.datetime.now(timezone.utc)' in content:
                # Add timezone import if needed
                if 'from datetime import' in content and 'timezone' not in content:
                    # Add timezone to existing datetime import
                    content = re.sub(
                        r'from datetime import ([^;\n]+)',
                        lambda m: f"from datetime import {m.group(1)}, timezone" if 'timezone' not in m.group(1) else m.group(0),  # noqa: E501
                        content,
                        count=1
                    )
                elif 'import datetime' in content and 'from datetime import timezone' not in content:
                    # Add timezone import after datetime import
                    content = re.sub(
                        r'(import datetime\n)',
                        r'\1from datetime import timezone\n',
                        content,
                        count=1
                    )
                
                # Replace datetime.now(timezone.utc) with datetime.now(timezone.utc)
                replacements = 0
                
                # Handle datetime.datetime.now(timezone.utc)
                content, n = re.subn(
                    r'datetime\.datetime\.utcnow\(\)',
                    'datetime.datetime.now(timezone.utc)',
                    content
                )
                replacements += n
                
                # Handle datetime.now(timezone.utc) (when datetime is imported as module)
                content, n = re.subn(
                    r'(?<!datetime\.)datetime\.utcnow\(\)',
                    'datetime.now(timezone.utc)',
                    content
                )
                replacements += n
                
                # Handle just datetime.now(timezone.utc) (when imported directly)
                content, n = re.subn(
                    r'(?<![.\w])utcnow\(\)',
                    'datetime.now(timezone.utc)',
                    content
                )
                replacements += n
                
                if content != original_content:
                    with open(filepath, 'w') as f:
                        f.write(content)
                    logger.info(f"✓ Fixed {filepath} ({replacements} replacements)")
                    files_fixed += 1
                    total_replacements += replacements
                    
        except Exception as e:
            logger.info(f"Error processing {filepath}: {e}")
    
    logger.info(f"\n✅ Fixed {files_fixed} files with {total_replacements} total replacements")

if __name__ == "__main__":
    logger.info("Fixing datetime.now(timezone.utc) usage...")
    fix_datetime_utcnow()
    logger.info("\n✅ Datetime fixes complete!")