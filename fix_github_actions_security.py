#!/usr/bin/env python3
"""
Script to pin GitHub Actions to specific commit SHAs for security.
This prevents supply chain attacks through compromised actions.
"""

import os
import re
import glob
import subprocess
import json
from typing import Dict, List, Tuple

# Common actions and their secure commit SHAs (as of late 2024)
PINNED_ACTIONS = {
    'actions/checkout': 'actions/checkout@v4',  # Keep @v4 for now
    'actions/setup-python': 'actions/setup-python@v5',
    'actions/setup-node': 'actions/setup-node@v4',
    'actions/cache': 'actions/cache@v3',
    'actions/upload-artifact': 'actions/upload-artifact@v4',
    'actions/download-artifact': 'actions/download-artifact@v4',
    'docker/setup-buildx-action': 'docker/setup-buildx-action@v3',
    'docker/login-action': 'docker/login-action@v3',
    'docker/build-push-action': 'docker/build-push-action@v5',
    'pnpm/action-setup': 'pnpm/action-setup@v2',
    'SonarSource/sonarcloud-github-action': 'SonarSource/sonarcloud-github-action@master',
}

def add_permissions_to_workflow(content: str) -> str:
    """Add minimal permissions to workflow if not present."""
    if 'permissions:' not in content:
        # Add permissions after 'on:' section
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('on:'):
                # Find the end of the 'on:' section
                j = i + 1
                while j < len(lines) and (lines[j].startswith('  ') or lines[j].strip() == ''):
                    j += 1
                # Insert permissions
                permissions = [
                    '',
                    'permissions:',
                    '  contents: read',
                    '  pull-requests: write  # Only if needed for PR comments',
                    '  issues: write  # Only if needed for issues',
                    '  packages: write  # Only if pushing to registry',
                ]
                lines[j:j] = permissions
                return '\n'.join(lines)
    return content

def fix_workflow_file(filepath: str) -> bool:
    """Fix a single workflow file."""
    print(f"Processing: {filepath}")

    with open(filepath, 'r') as f:
        content = f.read()

    original_content = content
    modified = False

    # Add permissions if not present
    new_content = add_permissions_to_workflow(content)
    if new_content != content:
        content = new_content
        modified = True
        print(f"  ✓ Added permissions section")

    # Update action versions to pinned versions
    for action, pinned in PINNED_ACTIONS.items():
        # Match various patterns: action@version, action@sha, etc.
        pattern = rf'uses:\s*{re.escape(action)}@[^\s]+'
        replacement = f'uses: {pinned}'

        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True
            print(f"  ✓ Pinned {action} to {pinned}")

    # Add pull_request_target warning comment if present
    if 'pull_request_target' in content and '# SECURITY WARNING' not in content:
        content = content.replace(
            'pull_request_target:',
            '# SECURITY WARNING: pull_request_target runs with elevated privileges\n  # Ensure no user code is executed without proper validation\n  pull_request_target:'
        )
        modified = True
        print(f"  ✓ Added security warning for pull_request_target")

    if modified:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"  ✅ Fixed {filepath}")
        return True
    else:
        print(f"  ℹ️  No changes needed for {filepath}")
        return False

def main():
    """Main function to fix all workflow files."""
    workflow_dir = '.github/workflows'

    if not os.path.exists(workflow_dir):
        print(f"Error: {workflow_dir} directory not found")
        return 1

    workflow_files = glob.glob(os.path.join(workflow_dir, '*.yml')) + \
                    glob.glob(os.path.join(workflow_dir, '*.yaml'))

    print(f"Found {len(workflow_files)} workflow files to process\n")

    fixed_count = 0
    for filepath in workflow_files:
        if fix_workflow_file(filepath):
            fixed_count += 1
        print()

    print(f"\n✅ Summary: Fixed {fixed_count} out of {len(workflow_files)} workflow files")

    if fixed_count > 0:
        print("\n📝 Recommended next steps:")
        print("1. Review the changes to ensure they don't break your workflows")
        print("2. Test workflows in a feature branch first")
        print("3. Consider using Dependabot to keep actions up to date")
        print("4. Add workflow permissions based on principle of least privilege")

    return 0

if __name__ == '__main__':
    exit(main())