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

# Configuration for major version bumps
ALLOWED_MAJOR_UPGRADES = {
    # 'actions/cache': [4],  # Example: Allow upgrading to v4 for actions/cache
}
ALLOW_MAJOR_BUMPS = os.getenv('ALLOW_MAJOR_BUMPS', 'false').lower() in ('1', 'true', 'yes')

# Common actions and their secure commit SHAs (as of December 2024)
# Normalize to a map keyed by base action to avoid duplicate processing
_RAW_PINNINGS = [
    ('actions/checkout@v4', '11bd71901bbe5b1630ceea73d27597364c9af683', 'v4.2.2'),
    ('actions/setup-python@v5', '0b93645e9fea7318ecaed2b359559ac225c90a2b', 'v5.3.0'),
    ('actions/setup-node@v4', '39370e3970a6d050c480ffad4ff0ed4d3fdee5af', 'v4.1.0'),
    ('actions/cache@v4', '1bd1e32a3bdc45362d1e726936510720a7c30a57', 'v4.2.0'),
    ('actions/cache@v3', '1bd1e32a3bdc45362d1e726936510720a7c30a57', 'v4.2.0'),  # Upgrade v3 to v4
    ('actions/upload-artifact@v4', '6f51ac03b9356f520e9adb1b1b7802705f340c2b', 'v4.5.0'),
    ('actions/download-artifact@v4', 'fa0a91b85d4f404e444e00e005971372dc801d16', 'v4.1.8'),
    ('docker/setup-buildx-action@v3', '6524bf65af31da8d45b59e8c27de4bd072b392f5', 'v3.8.0'),
    ('docker/login-action@v3', '9780b0c442fbb1117ed29e0efdff1e18412f7567', 'v3.3.0'),
    ('docker/build-push-action@v5', 'ca052bb54ab0790a636c9b5f226502c73d547a25', 'v5.4.0'),
    ('pnpm/action-setup@v4', 'fe02b34f77f8bc703788d5817da081398fad5dd2', 'v4.0.0'),
    ('pnpm/action-setup@v2', 'fe02b34f77f8bc703788d5817da081398fad5dd2', 'v4.0.0'),  # Upgrade v2 to v4
    ('github/codeql-action/init@v3', '9278e421667d5d90a2839487a482448c4ec7df4d', 'v3.27.2'),
    ('github/codeql-action/analyze@v3', '9278e421667d5d90a2839487a482448c4ec7df4d', 'v3.27.2'),
    ('github/codeql-action/autobuild@v3', '9278e421667d5d90a2839487a482448c4ec7df4d', 'v3.27.2'),
    ('gitleaks/gitleaks-action@v2', '83373cf2f8c4db6e24b41c1a9b086bb9619e9cd3', 'v2.3.7'),
    ('dependency-check/Dependency-Check_Action@main', '3102a65fd5f36d0000297576acc56a475b0de98d', 'main'),
    ('codecov/codecov-action@v4', 'b9fd7d16f6d7d1b5d2bec1a2887e65ceed900238', 'v4.6.0'),
    ('actions/github-script@v7', '60a0d83039c74a4aee543508d2ffcb1c3799cdea', 'v7.0.1'),
    ('SonarSource/sonarcloud-github-action@master', '02ef91109b2d589e757aefcfb2854c2783fd7b19', 'v4.0.0'),
    ('SonarSource/sonarcloud-github-action@v4', '02ef91109b2d589e757aefcfb2854c2783fd7b19', 'v4.0.0'),
]

# Build the PINNED_ACTIONS dict, keyed by base action
PINNED_ACTIONS = {}
for action_pattern, sha, version in _RAW_PINNINGS:
    if '@' in action_pattern:
        base_action = action_pattern.split('@')[0]
        input_version = action_pattern.split('@')[1]
    else:
        base_action = action_pattern
        input_version = None

    # Store with the base action as key, including version patterns for matching
    if base_action not in PINNED_ACTIONS:
        PINNED_ACTIONS[base_action] = []

    PINNED_ACTIONS[base_action].append({
        'pattern': action_pattern,
        'sha': sha,
        'version': version,
        'input_version': input_version
    })

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
                # Insert minimal permissions - only contents: read by default
                permissions = [
                    '',
                    'permissions:',
                    '  contents: read',
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

    # Update action versions to pinned versions - process each base action once
    for base_action, action_configs in PINNED_ACTIONS.items():
        # Find the best match for this action in the file
        for config in action_configs:
            action_pattern = config['pattern']
            sha = config['sha']
            version = config['version']
            input_version = config['input_version']

            # Build regex that matches the entire line including any existing comments
            # This prevents duplicate version comments
            if input_version:
                # Match action@version followed by anything to end of line
                pattern = rf'(?m)^(\s*uses:\s*{re.escape(base_action)}@){re.escape(input_version)}[^\s]*.*$'
            else:
                # Match action@anything to end of line
                pattern = rf'(?m)^(\s*uses:\s*{re.escape(base_action)}@)\S+.*$'

            # Build the replacement - just the SHA and version comment
            replacement = rf'\1{sha} # {version}'

            # Check if we should skip major version upgrades
            if input_version and version:
                # Extract major versions
                input_major = input_version.lstrip('v').split('.')[0] if input_version.lstrip('v')[0].isdigit() else None
                target_major = version.lstrip('v').split('.')[0] if version.lstrip('v')[0].isdigit() else None

                if input_major and target_major and input_major != target_major:
                    # Check if this major upgrade is allowed
                    allow_upgrade = ALLOW_MAJOR_BUMPS or (base_action in ALLOWED_MAJOR_UPGRADES and int(target_major) in ALLOWED_MAJOR_UPGRADES[base_action])

                    if not allow_upgrade:
                        print(f"  ⚠️  Skipping major upgrade for {base_action} from v{input_major} to v{target_major} (not allowed)")
                        continue  # Skip this config and try the next one
                    else:
                        print(f"  ℹ️  Allowing major upgrade for {base_action} from v{input_major} to v{target_major} (permitted by configuration)")

            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                modified = True
                print(f"  ✓ Pinned {action_pattern} to secure SHA")
                break  # Don't process other patterns for this base action

    # Fix pull_request_target warning with proper indentation (Comment 2)
    if 'pull_request_target' in content and '# SECURITY WARNING' not in content:
        pattern = re.compile(r'(?m)^(\s*)pull_request_target:\s*$')
        replacement = r'\1# SECURITY WARNING: pull_request_target runs with elevated privileges\n\1# Ensure no user code is executed without proper validation\n\1pull_request_target:'

        new_content = pattern.sub(replacement, content)
        if new_content != content:
            content = new_content
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