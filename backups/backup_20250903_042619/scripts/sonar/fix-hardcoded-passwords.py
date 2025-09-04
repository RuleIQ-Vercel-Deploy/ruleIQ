#!/usr/bin/env python3
"""Fix hardcoded passwords in the codebase by replacing with environment variables."""

from typing import Anyimport os
import re

def fix_hardcoded_passwords() -> Any: 
    files_to_fix = [
        ('archive/scripts/capture_test_errors.py', [11, 34]),
        ('archive/test_configs/conftest_fixed.py', [45]),
        ('sonarcloud/fix_hardcoded_passwords.py', [28, 29]),
    ]
    
    for filepath, line_numbers in files_to_fix:
        if not os.path.exists(filepath):
            print(f"Skipping {filepath} - file not found")
            continue
            
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        modified = False
        for line_num in line_numbers:
            idx = line_num - 1  # Convert to 0-based index
            if idx < len(lines):
                # Replace hardcoded password patterns
                if 'password=' in lines[idx] or 'PASSWORD=' in lines[idx]:
                    # Replace with environment variable
                    lines[idx] = re.sub(
                        r'(password|PASSWORD)\s*=\s*["\'].*?["\']',
                        r'\1=os.getenv("DB_PASSWORD", "")',
                        lines[idx]
                    )
                    modified = True
                    print(f"Fixed line {line_num} in {filepath}")
        
        if modified:
            # Ensure os import is at the top
            if 'import os\n' not in lines[:10]:
                lines.insert(0, 'import os\n')
            
            with open(filepath, 'w') as f:
                f.writelines(lines)
            print(f"✓ Fixed {filepath}")

def remove_sonarqube_tokens() -> Any: 
    files_with_tokens = [
        'sonarcloud/get_blocker_issues.py',
        'sonarcloud/get_detailed_blockers.py', 
        'sonarcloud/check_sonar_results.py'
    ]
    
    for filepath in files_with_tokens:
        if not os.path.exists(filepath):
            print(f"Skipping {filepath} - file not found")
            continue
            
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Replace token with environment variable
        modified_content = re.sub(
            r'(SONARCLOUD_TOKEN|token)\s*=\s*["\']squ_[a-f0-9]+["\']',
            r'\1 = os.getenv("SONARCLOUD_TOKEN", "")',
            content
        )
        
        # Add import if needed
        if 'import os' not in modified_content and modified_content != content:
            modified_content = 'import os\n' + modified_content
        
        if modified_content != content:
            with open(filepath, 'w') as f:
                f.write(modified_content)
            print(f"✓ Removed token from {filepath}")

if __name__ == "__main__":
    print("Fixing hardcoded passwords...")
    fix_hardcoded_passwords()
    
    print("\nRemoving SonarQube tokens...")
    remove_sonarqube_tokens()
    
    print("\n✅ Security fixes complete!")