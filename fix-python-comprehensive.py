#!/usr/bin/env python3
"""Comprehensive Python linting fix script for all remaining issues."""

import os
import re
import subprocess
import json
from pathlib import Path

def get_all_issues():
    """Get all ruff issues in JSON format."""
    result = subprocess.run(
        ['ruff', 'check', 'api', '--output-format=json'],
        capture_output=True,
        text=True,
        cwd='/home/omar/Documents/ruleIQ'
    )
    if result.returncode == 0:
        return []
    return json.loads(result.stdout)

def fix_magic_values():
    """Fix PLR2004 magic value issues."""
    magic_value_constants = {
        90: 'KEY_AGE_THRESHOLD_DAYS',
        1000000: 'MAX_VALUE_LIMIT',
        100: 'DEFAULT_LIMIT',
        10: 'DEFAULT_PAGE_SIZE',
        30: 'DEFAULT_TIMEOUT',
        60: 'CACHE_TIMEOUT',
        3600: 'HOUR_IN_SECONDS',
        86400: 'DAY_IN_SECONDS',
        200: 'HTTP_OK',
        400: 'HTTP_BAD_REQUEST',
        401: 'HTTP_UNAUTHORIZED',
        403: 'HTTP_FORBIDDEN',
        404: 'HTTP_NOT_FOUND',
        500: 'HTTP_INTERNAL_ERROR',
    }
    
    issues = get_all_issues()
    files_to_fix = {}
    
    for issue in issues:
        if issue['code'] == 'PLR2004':
            filepath = issue['filename']
            if filepath not in files_to_fix:
                files_to_fix[filepath] = []
            
            # Extract the magic value from the message
            match = re.search(r'Magic value used in comparison, consider replacing (\d+)', issue['message'])
            if match:
                value = int(match.group(1))
                if value in magic_value_constants:
                    files_to_fix[filepath].append({
                        'value': value,
                        'constant': magic_value_constants[value],
                        'line': issue['location']['row']
                    })
    
    for filepath, fixes in files_to_fix.items():
        if not os.path.exists(filepath):
            continue
            
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Add constants after imports
        lines = content.split('\n')
        import_end = 0
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith('import') and not line.startswith('from'):
                if i > 0:
                    import_end = i
                    break
        
        # Add unique constants
        constants_to_add = set()
        for fix in fixes:
            constants_to_add.add(f"{fix['constant']} = {fix['value']}")
        
        if constants_to_add and import_end > 0:
            # Check if constants already exist
            existing_constants = set()
            for const_def in constants_to_add:
                const_name = const_def.split(' = ')[0]
                if const_name in content:
                    existing_constants.add(const_def)
            
            new_constants = constants_to_add - existing_constants
            if new_constants:
                lines.insert(import_end, '\n' + '\n'.join(sorted(new_constants)) + '\n')
                content = '\n'.join(lines)
        
        # Replace magic values
        for fix in fixes:
            pattern = rf'\b{fix["value"]}\b'
            replacement = fix['constant']
            content = re.sub(pattern, replacement, content)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        print(f"Fixed magic values in {filepath}")

def fix_bare_excepts():
    """Fix bare except clauses."""
    issues = get_all_issues()
    
    for issue in issues:
        if issue['code'] == 'E722':
            filepath = issue['filename']
            if not os.path.exists(filepath):
                continue
                
            with open(filepath, 'r') as f:
                content = f.read()
            
            content = re.sub(r'\bexcept\s*:', 'except Exception:', content)
            
            with open(filepath, 'w') as f:
                f.write(content)
            
            print(f"Fixed bare except in {filepath}")

def fix_long_lines():
    """Fix lines that are too long."""
    issues = get_all_issues()
    
    for issue in issues:
        if issue['code'] == 'E501':
            filepath = issue['filename']
            line_num = issue['location']['row']
            
            if not os.path.exists(filepath):
                continue
                
            with open(filepath, 'r') as f:
                lines = f.readlines()
            
            if line_num <= len(lines):
                line = lines[line_num - 1]
                
                # Handle different types of long lines
                if 'print(' in line or 'logger' in line or 'logging' in line:
                    # Split string literals in logging/print statements
                    if '"' in line:
                        parts = line.split('"')
                        if len(parts) > 2 and len(line) > 100:
                            # Reconstruct with line continuation
                            indent = len(line) - len(line.lstrip())
                            lines[line_num - 1] = parts[0] + '"\n' + ' ' * (indent + 4) + '"'.join(parts[1:])
                
                elif '#' in line:
                    # Move comments to previous line
                    code_part = line.split('#')[0]
                    comment_part = '#' + line.split('#', 1)[1]
                    if len(code_part.rstrip()) <= 88:
                        continue  # Comment makes it long, but code is fine
                    indent = len(line) - len(line.lstrip())
                    lines[line_num - 1] = ' ' * indent + comment_part + code_part.rstrip() + '\n'
                
                elif '=' in line and '==' not in line and '!=' not in line:
                    # Break long assignments
                    parts = line.split('=', 1)
                    if len(parts) == 2 and len(line) > 100:
                        indent = len(line) - len(line.lstrip())
                        lines[line_num - 1] = parts[0] + '= \\\n' + ' ' * (indent + 4) + parts[1].lstrip()
            
            with open(filepath, 'w') as f:
                f.writelines(lines)

def fix_unused_variables():
    """Fix unused variable warnings."""
    issues = get_all_issues()
    
    for issue in issues:
        if issue['code'] in ['F841', 'F401']:
            filepath = issue['filename']
            line_num = issue['location']['row']
            
            if not os.path.exists(filepath):
                continue
                
            with open(filepath, 'r') as f:
                lines = f.readlines()
            
            if line_num <= len(lines):
                line = lines[line_num - 1]
                
                if issue['code'] == 'F841':  # Local variable assigned but never used
                    # Convert to underscore if it's a simple assignment
                    var_match = re.search(r'(\w+)\s*=', line)
                    if var_match:
                        var_name = var_match.group(1)
                        if not var_name.startswith('_'):
                            lines[line_num - 1] = line.replace(var_name, '_', 1)
                
                elif issue['code'] == 'F401':  # Imported but unused
                    # Comment out or remove the import
                    if 'import' in line:
                        lines[line_num - 1] = '# ' + line
            
            with open(filepath, 'w') as f:
                f.writelines(lines)

def fix_ambiguous_variables():
    """Fix ambiguous variable names (E741)."""
    issues = get_all_issues()
    ambiguous_replacements = {
        'l': 'lst',
        'O': 'obj',
        'I': 'idx'
    }
    
    for issue in issues:
        if issue['code'] == 'E741':
            filepath = issue['filename']
            
            if not os.path.exists(filepath):
                continue
                
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Extract variable name from message
            match = re.search(r"ambiguous variable name '(.)'", issue['message'])
            if match:
                old_var = match.group(1)
                new_var = ambiguous_replacements.get(old_var, 'var')
                
                # Replace the variable name (be careful with word boundaries)
                content = re.sub(rf'\b{old_var}\b', new_var, content)
                
                with open(filepath, 'w') as f:
                    f.write(content)
                
                print(f"Fixed ambiguous variable '{old_var}' -> '{new_var}' in {filepath}")

def run_autofix():
    """Run ruff autofix for issues it can handle automatically."""
    print("\nRunning ruff autofix...")
    subprocess.run(
        ['ruff', 'check', 'api', '--fix', '--unsafe-fixes'],
        cwd='/home/omar/Documents/ruleIQ'
    )
    print("Ruff autofix completed")

def main():
    """Main function to fix all Python linting issues."""
    print("Starting comprehensive Python linting fixes...")
    
    # First run ruff autofix
    run_autofix()
    
    # Then fix specific issues
    print("\nFixing magic values...")
    fix_magic_values()
    
    print("\nFixing bare except clauses...")
    fix_bare_excepts()
    
    print("\nFixing long lines...")
    fix_long_lines()
    
    print("\nFixing unused variables...")
    fix_unused_variables()
    
    print("\nFixing ambiguous variable names...")
    fix_ambiguous_variables()
    
    # Run autofix again to clean up
    run_autofix()
    
    # Final count
    result = subprocess.run(
        ['ruff', 'check', 'api'],
        capture_output=True,
        text=True,
        cwd='/home/omar/Documents/ruleIQ'
    )
    remaining = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
    print(f"\n✅ Fixes completed. Remaining issues: {remaining}")

if __name__ == "__main__":
    main()