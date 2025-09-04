#!/usr/bin/env python3
"""Fix duplicated string literals by creating constants."""
import logging
logger = logging.getLogger(__name__)


from __future__ import annotations

from typing import Any
import os
import re
from collections import defaultdict

def fix_duplicated_literals() -> Any:
    """Find and fix duplicated string literals in Python files."""
    
    # Common strings that should be constants
    common_duplicates = {
        'users.id': 'USER_ID_COLUMN',
        'business_profiles.id': 'BUSINESS_PROFILE_ID_COLUMN',
        'created_at': 'CREATED_AT_COLUMN',
        'updated_at': 'UPDATED_AT_COLUMN',
        'status': 'STATUS_COLUMN',
        'user_id': 'USER_ID_FIELD',
        'company_id': 'COMPANY_ID_FIELD',
        'session_id': 'SESSION_ID_FIELD',
        'compliance_score': 'COMPLIANCE_SCORE_FIELD',
        'risk_level': 'RISK_LEVEL_FIELD',
    }
    
    files_to_fix = [
        'alembic/versions/8b656f197a19_add_rbac_system_database_schema.py',
        'api/routers/assessments.py',
        'api/routers/auth.py',
        'api/routers/compliance.py',
        'services/compliance_service.py',
        'services/assessment_service.py',
    ]
    
    for filepath in files_to_fix:
        if not os.path.exists(filepath):
            logger.info(f"Skipping {filepath} - file not found")
            continue
        
        try:
            with open(filepath, 'r') as f:
                lines = f.readlines()
            
            # Count string occurrences
            string_counts = defaultdict(int)
            for line in lines:
                # Find quoted strings
                strings = re.findall(r'"([^"]+)"|\'([^\']+)\'', line)
                for match in strings:
                    string_val = match[0] or match[1]
                    if string_val in common_duplicates:
                        string_counts[string_val] += 1
            
            # If we have duplicated strings, add constants
            if any(count > 3 for count in string_counts.values()):
                # Add constants at the top of the file
                constants_added = False
                new_lines = []
                
                for i, line in enumerate(lines):
                    # Add constants after imports
                    if not constants_added and (line.startswith('from ') or line.startswith('import ')):
                        # Find end of imports
                        j = i
                        while j < len(lines) and (lines[j].startswith('from ') or 
                                                 lines[j].startswith('import ') or 
                                                 lines[j].strip() == ''):
                            j += 1
                        
                        # Add constants
                        new_lines.extend(lines[:j])
                        new_lines.append('\n# Constants for commonly used strings\n')
                        
                        for string_val, count in string_counts.items():
                            if count > 3:
                                const_name = common_duplicates.get(string_val, 
                                    string_val.upper().replace('.', '_').replace(' ', '_'))
                                new_lines.append(f'{const_name} = "{string_val}"\n')
                        
                        new_lines.append('\n')
                        
                        # Replace strings in rest of file
                        for k in range(j, len(lines)):
                            modified_line = lines[k]
                            for string_val, count in string_counts.items():
                                if count > 3:
                                    const_name = common_duplicates.get(string_val,
                                        string_val.upper().replace('.', '_').replace(' ', '_'))
                                    # Replace quoted strings with constant
                                    modified_line = re.sub(
                                        f'["\']({re.escape(string_val)})["\']',
                                        const_name,
                                        modified_line
                                    )
                            new_lines.append(modified_line)
                        
                        constants_added = True
                        break
                
                if constants_added:
                    with open(filepath, 'w') as f:
                        f.writelines(new_lines)
                    logger.info(f"✓ Fixed {filepath}")
                    
        except Exception as e:
            logger.info(f"Error processing {filepath}: {e}")

if __name__ == "__main__":
    logger.info("Fixing duplicated string literals...")
    fix_duplicated_literals()
    logger.info("\n✅ Duplicated literals fixes complete!")