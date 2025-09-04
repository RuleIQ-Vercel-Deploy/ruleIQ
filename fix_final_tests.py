#!/usr/bin/env python3
"""Script to fix the final 10 test files with collection errors."""

import re
import os

def fix_docstring_syntax(content):
    """Fix misplaced docstrings that cause syntax errors."""
    # Pattern 1: Docstring after imports/constants but before actual docstring location
    pattern1 = r'"""[\s\S]*?# Constants.*?"""([\s\S]*?)"""'
    if re.search(pattern1, content):
        # Move constants before docstring
        lines = content.split('\n')
        docstring_lines = []
        constant_lines = []
        other_lines = []
        
        in_docstring = False
        found_constants = False
        
        for line in lines:
            if line.strip().startswith('"""') and not in_docstring:
                in_docstring = True
                docstring_lines.append(line)
            elif line.strip().endswith('"""') and in_docstring:
                docstring_lines.append(line)
                in_docstring = False
            elif in_docstring:
                docstring_lines.append(line)
            elif line.strip().startswith('# Constants') or (found_constants and line.startswith(('HTTP_', 'DEFAULT_'))):
                found_constants = True
                constant_lines.append(line)
            else:
                other_lines.append(line)
        
        # Reorder: docstring first, then imports, then constants, then rest
        fixed_lines = []
        # Add docstring at the very top
        for line in docstring_lines[:3]:  # First docstring
            fixed_lines.append(line)
        
        # Add imports
        for line in other_lines:
            if line.startswith('import ') or line.startswith('from '):
                fixed_lines.append(line)
        
        # Add constants
        fixed_lines.append('')
        for line in constant_lines:
            fixed_lines.append(line)
        
        # Add rest
        fixed_lines.append('')
        for line in other_lines:
            if not (line.startswith('import ') or line.startswith('from ')):
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    return content

def fix_import_paths(content):
    """Fix common import path issues."""
    replacements = [
        # Fix middleware imports
        ('from middleware.jwt_auth import', 'from api.middleware.jwt_auth import'),
        ('from api.dependencies.token_blacklist import', 'from services.token_blacklist import'),
        
        # Fix service imports
        ('from services.ai.cost_monitoring import CostEntry', 
         'from services.ai_services.cost_monitoring import AIUsageMetrics'),
         
        # Fix database imports
        ('from database.audit import AuditLog', 'from database.models import AuditLog'),
        ('from database.rbac import', 'from database.models import'),
        ('from database.user import User', 'from database.models import User'),
    ]
    
    for old, new in replacements:
        content = content.replace(old, new)
    
    return content

def fix_class_references(content):
    """Fix references to renamed/moved classes."""
    replacements = [
        ('CostEntry', 'AIUsageMetrics'),
        ('TokenBlacklistService', 'TokenBlacklist'),
    ]
    
    for old, new in replacements:
        # Only replace if it's not in an import statement
        lines = content.split('\n')
        fixed_lines = []
        for line in lines:
            if 'import' not in line and old in line:
                line = line.replace(old, new)
            fixed_lines.append(line)
        content = '\n'.join(fixed_lines)
    
    return content

def process_file(filepath):
    """Process a single test file to fix common issues."""
    print(f"Processing: {filepath}")
    
    if not os.path.exists(filepath):
        print(f"  ❌ File not found")
        return False
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        original_content = content
        
        # Apply fixes
        content = fix_docstring_syntax(content)
        content = fix_import_paths(content)
        content = fix_class_references(content)
        
        if content != original_content:
            # Create backup
            backup_path = filepath + '.bak'
            with open(backup_path, 'w') as f:
                f.write(original_content)
            
            # Write fixed content
            with open(filepath, 'w') as f:
                f.write(content)
            
            print(f"  ✅ Fixed and saved (backup at {backup_path})")
            return True
        else:
            print(f"  ℹ️ No changes needed")
            return True
            
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Fix all problem files."""
    # Files already fixed
    fixed_files = [
        "tests/test_phase1_fastapi.py",
        "tests/test_phase2_fastapi.py", 
        "tests/test_phase3_fastapi.py",
        "tests/test_security_integration_e2e.py"
    ]
    
    # Files that may still need fixing
    remaining_files = [
        "tests/integration/test_assessment_workflow.py",
        "tests/test_critical_auth.py",
        "tests/test_golden_dataset_validators.py",
        "tests/test_integration.py",
        "tests/test_jwt_authentication.py",
        "tests/test_notification_basic.py"
    ]
    
    print("Fixing Remaining Test Files")
    print("="*60)
    
    for filepath in remaining_files:
        process_file(filepath)
    
    print("\n" + "="*60)
    print("All files processed!")
    print("\nNow run: python check_test_errors.py")
    print("to verify all issues are resolved")

if __name__ == "__main__":
    main()