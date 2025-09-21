#!/usr/bin/env python3
"""
Script to secure GitHub Actions by pinning to specific SHA versions
and adding permission restrictions.
"""

import re
import sys
from pathlib import Path

# Mapping of action references to their pinned SHA versions (as of late 2024)
ACTION_SHA_MAP = {
    'actions/checkout@v5': 'actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683',  # v5.2.2
    'actions/checkout@v4': 'actions/checkout@692973e3d937129bcbf40652eb9f2f61becf3332',  # v4.1.7
    'actions/checkout@v3': 'actions/checkout@f43a0e5ff2bd294095638e18286ca9a3d1956744',  # v3.6.0
    'actions/upload-artifact@v4': 'actions/upload-artifact@b4b15b8c7c6ac21ea08fcf65892d2ee8f75cf882',  # v4.4.3
    'actions/upload-artifact@v3': 'actions/upload-artifact@a8a3f3ad30e3422c9c7b888a15615d19a852ae32',  # v3.1.3
    'actions/download-artifact@v4': 'actions/download-artifact@fa0a91b85d4f404e444e00e005971372dc801d16',  # v4.1.8
    'actions/download-artifact@v3': 'actions/download-artifact@9bc31d5ccc31df68ecc42ccf4149144866c47d8a',  # v3.0.2
    'actions/setup-node@v4': 'actions/setup-node@39370e3970a6d050c480ffad4ff0ed4d3fdee5af',  # v4.1.0
    'actions/setup-node@v3': 'actions/setup-node@5e21ff4d9bc1a8cf6de233a3057d20ec6b3fb69d',  # v3.8.1
    'actions/setup-python@v5': 'actions/setup-python@0b93645e9fea7318ecaed2b359559ac225c90a2b',  # v5.3.0
    'actions/setup-python@v4': 'actions/setup-python@82c7e631bb3cdc910f68e0081d67478d79c6982d',  # v4.7.1
    'actions/cache@v4': 'actions/cache@6849a6489940f00c2f30c0fb92c6274307ccb58a',  # v4.1.2
    'actions/cache@v3': 'actions/cache@704facf57e6136b1bc63b828d79edcd491f0ee84',  # v3.3.2
    'docker/setup-buildx-action@v3': 'docker/setup-buildx-action@c47758b77c9736f4b2ef4073d4d51994fabfe349',  # v3.7.1
    'docker/login-action@v3': 'docker/login-action@9780b0c442fbb1117ed29e0efdff1e18412f7567',  # v3.3.0
    'docker/build-push-action@v5': 'docker/build-push-action@4f58ea79222b3b9dc2c8bbdd6debcef730109a75',  # v5.4.0
    'docker/metadata-action@v5': 'docker/metadata-action@60c2040ba3b7618d270eca4b2f0a43cd55b39c96',  # v5.0.0
    'github/codeql-action/upload-sarif@v2': 'github/codeql-action/upload-sarif@4f3212b61783c3c68e8309a0f18a699764811cda',  # v2.23.1
    'github/codeql-action/analyze@v2': 'github/codeql-action/analyze@4f3212b61783c3c68e8309a0f18a699764811cda',
    'aquasecurity/trivy-action@master': 'aquasecurity/trivy-action@18f2510ee396bbf400402c1ae107f9c51b87bcba',  # 0.19.0
    'anchore/sbom-action@v0': 'anchore/sbom-action@fc46e51fd3cb168ffb36c6d1915723c47db58abb',  # v0.17.7
    'codecov/codecov-action@v4': 'codecov/codecov-action@b9fd7d16f6d7d1b5d2bec1a2887e65ceed900238',  # v4.6.0
    'codecov/codecov-action@v3': 'codecov/codecov-action@eaaf4bedf32dbdc6b720b63067d99c4d77d6047d',  # v3.1.4
    'cypress-io/github-action@v6': 'cypress-io/github-action@1b70233146622b69e789ccdd4f9452adc638d25a',  # v6.6.1
    'cypress-io/github-action@v5': 'cypress-io/github-action@97d526c9027e7b1c17b0a027f3bf71e33ba543c2',  # v5.8.3
}

def secure_workflow_file(filepath):
    """Secure a single workflow file."""
    print(f"Processing {filepath}...")

    with open(filepath, 'r') as f:
        content = f.read()

    original_content = content
    changes_made = []

    # Pin action versions
    for unpinned, pinned in ACTION_SHA_MAP.items():
        if unpinned in content:
            content = content.replace(unpinned, pinned)
            changes_made.append(f"  - Pinned {unpinned} to SHA")

    # Add permissions if not present
    if 'permissions:' not in content:
        # Add minimal permissions at the job level
        lines = content.split('\n')
        new_lines = []
        in_job = False
        job_indent = ''

        for i, line in enumerate(lines):
            new_lines.append(line)

            # Detect job definition
            if re.match(r'^[a-zA-Z0-9_-]+:', line) and i > 0 and 'jobs:' in '\n'.join(lines[:i]):
                in_job = True
                job_indent = ''
            elif in_job and line.strip().startswith('runs-on:'):
                # Insert permissions after runs-on
                indent = len(line) - len(line.lstrip())
                new_lines.append(' ' * indent + 'permissions:')
                new_lines.append(' ' * (indent + 2) + 'contents: read')
                changes_made.append(f"  - Added minimal permissions")
                in_job = False

        content = '\n'.join(new_lines)

    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ Secured {filepath.name}:")
        for change in changes_made:
            print(change)
        return True
    else:
        print(f"✓ {filepath.name} - No changes needed")
        return False

def add_global_permissions_to_deployment(filepath):
    """Add specific permissions for deployment.yml."""
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Find where to insert permissions (after env: section)
    insert_index = -1
    for i, line in enumerate(lines):
        if line.startswith('env:'):
            # Find the end of env section
            for j in range(i+1, len(lines)):
                if not lines[j].startswith(' ') and lines[j].strip():
                    insert_index = j
                    break
            break

    if insert_index > 0 and not any('permissions:' in line for line in lines):
        # Insert permissions
        permissions = [
            '\npermissions:\n',
            '  contents: read\n',
            '  packages: write  # For Docker registry\n',
            '  deployments: write  # For deployment status\n',
            '  id-token: write  # For OIDC authentication\n',
            '\n'
        ]
        lines[insert_index:insert_index] = permissions

        with open(filepath, 'w') as f:
            f.writelines(lines)
        print(f"✅ Added global permissions to {filepath.name}")
        return True
    return False

def main():
    """Main function."""
    workflows_dir = Path('.github/workflows')

    if not workflows_dir.exists():
        print(f"Error: {workflows_dir} directory not found")
        return 1

    workflow_files = list(workflows_dir.glob('*.yml')) + list(workflows_dir.glob('*.yaml'))

    if not workflow_files:
        print(f"No workflow files found in {workflows_dir}")
        return 1

    print(f"Found {len(workflow_files)} workflow files to process\n")

    modified_count = 0
    for workflow_file in workflow_files:
        if secure_workflow_file(workflow_file):
            modified_count += 1

        # Special handling for deployment.yml
        if workflow_file.name == 'deployment.yml':
            if add_global_permissions_to_deployment(workflow_file):
                modified_count += 1

    print(f"\n✅ Summary: Modified {modified_count} workflow files")
    print("⚠️  Remember to test these changes in a branch before merging to main")

    return 0

if __name__ == "__main__":
    sys.exit(main())