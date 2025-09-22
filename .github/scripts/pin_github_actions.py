#!/usr/bin/env python3
"""
Pin GitHub Actions to specific commit hashes for security.
This prevents supply chain attacks through compromised actions.
"""

import os
import sys
import re
import yaml
import argparse
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Known official actions and their pinned versions (as of Jan 2025)
KNOWN_ACTIONS = {
    # GitHub official actions
    "actions/checkout@v4": "actions/checkout@b4ffde65f46336ab88eb53be808477a3936bae11",  # v4.1.1
    "actions/checkout@v3": "actions/checkout@8e5e7e5ab8b370d6c329ec480221332ada57f0ab",  # v3.5.2
    "actions/setup-python@v5": "actions/setup-python@0b93645e9fea7318ecaed2b359559ac225c90a2b",  # v5.0.0
    "actions/setup-python@v4": "actions/setup-python@61a6322f88396a6271a6ee3565807d608ecaddd1",  # v4.7.0
    "actions/setup-node@v5": "actions/setup-node@1e60f620b9541d16bece96c5465dc8ee9832be0b",  # v5.0.0
    "actions/setup-node@v4": "actions/setup-node@8f152de45cc393bb48ce5d89d36b731f54556e65",  # v4.0.0
    "actions/cache@v4": "actions/cache@13aacd865c20de90d75de3b17ebe84f7a17d57d2",  # v4.0.0
    "actions/cache@v3": "actions/cache@704facf57e6136b1bc63b828d79edcd491f0ee84",  # v3.3.2
    "actions/upload-artifact@v4": "actions/upload-artifact@1eb3cb2b3e0f29609092a73eb033bb759a334595",  # v4.1.0
    "actions/upload-artifact@v3": "actions/upload-artifact@a8a3f3ad30e3422c9c7b888a15615d19a852ae32",  # v3.1.3
    "actions/download-artifact@v4": "actions/download-artifact@c850b930e6ba138125429b7e5c93fc707a7f8427",  # v4.1.0
    "actions/download-artifact@v3": "actions/download-artifact@9bc31d5ccc31df68ecc42ccf4149144866c47d8a",  # v3.0.2

    # GitHub CodeQL actions
    "github/codeql-action/analyze@v3": "github/codeql-action/analyze@e8893c57a1f3a2b659b6b55564fdfdbbd2982911",  # v3.24.0
    "github/codeql-action/init@v3": "github/codeql-action/init@e8893c57a1f3a2b659b6b55564fdfdbbd2982911",  # v3.24.0
    "github/codeql-action/autobuild@v3": "github/codeql-action/autobuild@e8893c57a1f3a2b659b6b55564fdfdbbd2982911",  # v3.24.0

    # Docker actions
    "docker/setup-buildx-action@v3": "docker/setup-buildx-action@2ad185228a349d19414702819e06df9fa4314287",  # v3.0.0
    "docker/login-action@v3": "docker/login-action@9780b0c442fbb1117ed29e0efdff1e18412f7567",  # v3.0.0
    "docker/build-push-action@v5": "docker/build-push-action@4f58ea79222b3b9dc2c8bbdd6debcef730109a75",  # v5.1.0

    # Third-party actions that were missing
    "pnpm/action-setup@v2": "pnpm/action-setup@d882d12c64e032187b2edb46d3a0d003b7a43598",  # v2.4.0
    "gitleaks/gitleaks-action@v2": "gitleaks/gitleaks-action@cb7149a9b57195524f8a5f0c0f3e9e5d3e3e3c24",  # v2.3.2

    # Security scanning actions
    "anchore/scan-action@v3": "anchore/scan-action@d43cc1dfea6a99ed123bf8f3133f1797c9b44492",  # v3.6.4
    "anchore/scan-action@v7": "anchore/scan-action@3343887d815d7b07465f6fdcd395bd66508d486a",  # v7.0.0

    # Code coverage actions
    "codecov/codecov-action@v4": "codecov/codecov-action@e28ff129e5465c2c0dcc6f003fc735cb6ae0c673",  # v4.0.1
    "codecov/codecov-action@v3": "codecov/codecov-action@ab904c41d6ece82784817410c45d8b8c02684457",  # v3.1.6
}


def pin_action(action: str) -> str:
    """Pin an action to its commit hash."""
    # Check if already pinned (contains @ followed by 40 hex chars)
    if re.match(r'.*@[a-f0-9]{40}$', action):
        return action

    # Look up in known actions
    for known, pinned in KNOWN_ACTIONS.items():
        if action.startswith(known.split('@')[0]):
            # Extract version tag if present
            if '@' in action:
                version = action.split('@')[1]
                # Try to match with our known versions
                if known.endswith(f"@{version}"):
                    # Extract the version comment from the known action
                    version_comment = known.split('@')[1]
                    pinned_with_comment = f"{pinned}  # {version_comment}"
                    logger.info(f"  Pinning {action} → {pinned} ({version_comment})")
                    return pinned_with_comment

            # Default to latest known version
            base_action = action.split('@')[0]
            for k, v in KNOWN_ACTIONS.items():
                if k.startswith(base_action):
                    version_comment = k.split('@')[1]
                    pinned_with_comment = f"{v}  # {version_comment}"
                    logger.info(f"  Pinning {action} → {v} ({version_comment})")
                    return pinned_with_comment

    # If not found, log warning
    logger.warning(f"  ⚠️  Unknown action: {action} - please pin manually")
    return action


def process_workflow_file(file_path: Path) -> bool:
    """Process a single workflow file."""
    logger.info(f"\nProcessing: {file_path}")

    try:
        with open(file_path, 'r') as f:
            content = f.read()
            original_content = content
    except IOError as e:
        logger.error(f"  ❌ Error reading file: {e}")
        return False

    # Parse YAML
    try:
        workflow = yaml.safe_load(content)
    except yaml.YAMLError as e:
        logger.error(f"  ❌ Error parsing YAML: {e}")
        return False

    if not workflow:
        logger.warning(f"  ⚠️  Empty workflow file")
        return False

    modified = False

    # Process jobs
    if 'jobs' in workflow:
        for job_name, job in workflow.get('jobs', {}).items():
            if not job:
                continue

            # Process steps
            for step in job.get('steps', []):
                if 'uses' in step:
                    original_action = step['uses']
                    pinned_action = pin_action(original_action)
                    if original_action != pinned_action:
                        # Replace in original content to preserve formatting
                        content = content.replace(f"uses: {original_action}", f"uses: {pinned_action}")
                        modified = True

    # Process reusable workflows
    for job_name, job in workflow.get('jobs', {}).items():
        if job and 'uses' in job:
            original_action = job['uses']
            if not original_action.startswith('.'):  # Skip local workflows
                pinned_action = pin_action(original_action)
                if original_action != pinned_action:
                    content = content.replace(f"uses: {original_action}", f"uses: {pinned_action}")
                    modified = True

    if modified:
        try:
            with open(file_path, 'w') as f:
                f.write(content)
            logger.info(f"  ✅ Updated workflow file")
            return True
        except IOError as e:
            logger.error(f"  ❌ Error writing file: {e}")
            return False
    else:
        logger.info(f"  ℹ️  No changes needed")
        return False


def add_permissions_block(file_path: Path) -> bool:
    """Add minimal permissions block to workflow if missing."""
    try:
        with open(file_path, 'r') as f:
            content = f.read()
    except IOError as e:
        logger.error(f"  ❌ Error reading file: {e}")
        return False

    # Check if permissions already exist at workflow level
    if re.search(r'^\s*permissions:', content, re.MULTILINE):
        return False

    # Add minimal permissions after name/on block
    lines = content.split('\n')
    insert_index = -1

    for i, line in enumerate(lines):
        if line.startswith('jobs:'):
            insert_index = i
            break

    if insert_index > 0:
        permissions_block = [
            "",
            "# Minimal permissions for security",
            "permissions:",
            "  contents: read",
            ""
        ]
        lines[insert_index:insert_index] = permissions_block

        try:
            with open(file_path, 'w') as f:
                f.write('\n'.join(lines))
            logger.info(f"  ✅ Added minimal permissions block")
            return True
        except IOError as e:
            logger.error(f"  ❌ Error writing file: {e}")
            return False

    return False


def main(repo_path: Optional[str] = None) -> int:
    """Main function to process all workflow files."""
    # Use provided path or current directory
    if repo_path:
        try:
            os.chdir(repo_path)
        except OSError as e:
            logger.error(f"❌ Cannot change to directory {repo_path}: {e}")
            return 1

    workflows_dir = Path(".github/workflows")

    if not workflows_dir.exists():
        logger.error("❌ .github/workflows directory not found")
        logger.info(f"   Current directory: {os.getcwd()}")
        return 1

    try:
        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    except Exception as e:
        logger.error(f"❌ Error listing workflow files: {e}")
        return 1

    if not workflow_files:
        logger.error("❌ No workflow files found")
        return 1

    logger.info(f"Found {len(workflow_files)} workflow files")

    updated_count = 0
    error_count = 0

    for workflow_file in workflow_files:
        try:
            if process_workflow_file(workflow_file):
                updated_count += 1

            # Also add permissions if missing
            if add_permissions_block(workflow_file):
                updated_count += 1
        except Exception as e:
            logger.error(f"❌ Unexpected error processing {workflow_file}: {e}")
            error_count += 1

    logger.info(f"\n✅ Updated {updated_count} workflow files")
    if error_count > 0:
        logger.warning(f"⚠️  {error_count} files had errors")

    logger.info("\n⚠️  Important: Review all changes and test workflows before merging")
    logger.info("📝 Note: Some actions may need manual verification")

    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pin GitHub Actions to specific commit hashes for security")
    parser.add_argument(
        "--repo-path",
        "-p",
        help="Path to the repository root (default: current directory)",
        default=None
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')

    sys.exit(main(args.repo_path))