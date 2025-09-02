#!/usr/bin/env python3
import os
import re
import subprocess

def fix_magic_values():
    """Replace magic values with constants"""
    files_to_fix = [
        ('api/clients/aws_client.py', 90, 'KEY_AGE_THRESHOLD_DAYS'),
        ('api/schemas/business_profiles.py', 1000000, 'MAX_EMPLOYEE_COUNT'),
    ]
    
    for filepath, value, const_name in files_to_fix:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            
            # Add constant definition at top of file after imports
            import_end = content.rfind('\n\n', 0, content.find('class')) if 'class' in content else content.find('\n\n')
            if import_end > 0:
                content = content[:import_end] + f'\n\n{const_name} = {value}\n' + content[import_end:]
            
            # Replace magic value with constant
            content = re.sub(f'(\\s)({value})(\\s|:)', f'\\1{const_name}\\3', content)
            
            with open(filepath, 'w') as f:
                f.write(content)
            print(f"Fixed magic value {value} in {filepath}")

def fix_long_lines():
    """Fix lines that are too long"""
    result = subprocess.run(['ruff', 'check', '.', '--select=E501'], 
                          capture_output=True, text=True, cwd='/home/omar/Documents/ruleIQ/api')
    
    for line in result.stdout.split('\n'):
        if 'E501' in line and '.py:' in line:
            parts = line.split(':')
            if len(parts) >= 3:
                filepath = parts[0].strip()
                line_num = int(parts[1])
                
                if os.path.exists(f'/home/omar/Documents/ruleIQ/api/{filepath}'):
                    with open(f'/home/omar/Documents/ruleIQ/api/{filepath}', 'r') as f:
                        lines = f.readlines()
                    
                    if line_num <= len(lines):
                        # Break long lines
                        long_line = lines[line_num - 1]
                        if 'print(' in long_line or 'logger' in long_line:
                            # For logging/print statements, break at logical points
                            lines[line_num - 1] = long_line[:80] + '"\n            "' + long_line[80:]
                        elif len(long_line) > 100:
                            # Generic line breaking
                            lines[line_num - 1] = long_line[:90] + ' \\\n        ' + long_line[90:]
                    
                    with open(f'/home/omar/Documents/ruleIQ/api/{filepath}', 'w') as f:
                        f.writelines(lines)

def fix_bare_excepts():
    """Replace bare except with specific exceptions"""
    result = subprocess.run(['grep', '-r', 'except:', '.', '--include=*.py'], 
                          capture_output=True, text=True, cwd='/home/omar/Documents/ruleIQ/api')
    
    for line in result.stdout.split('\n'):
        if line and ':except:' in line:
            filepath = line.split(':')[0]
            if os.path.exists(f'/home/omar/Documents/ruleIQ/api/{filepath}'):
                with open(f'/home/omar/Documents/ruleIQ/api/{filepath}', 'r') as f:
                    content = f.read()
                
                content = content.replace('except:', 'except Exception:')
                
                with open(f'/home/omar/Documents/ruleIQ/api/{filepath}', 'w') as f:
                    f.write(content)
                print(f"Fixed bare except in {filepath}")

if __name__ == "__main__":
    print("Fixing Python linting issues...")
    fix_magic_values()
    fix_bare_excepts()
    fix_long_lines()
    print("Done!")