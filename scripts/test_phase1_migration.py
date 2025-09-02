#!/usr/bin/env python3
"""
Test Phase 1 migration - Core User Endpoints
This script validates our migration approach on the first 3 files
"""
import subprocess
import sys
from pathlib import Path

# Phase 1 files according to our plan
PHASE_1_FILES = [
    "api/routers/users.py",
    "api/routers/business_profiles.py",
    # main.py already done
]


def run_dry_run(file_path: str) -> bool:
    """Run dry run for a single file"""
    print(f"\n{'=' * 80}")
    print(f"🔍 DRY RUN: {file_path}")
    print(f"{'=' * 80}")

    cmd = [
        sys.executable,
        "scripts/migrate_stack_auth_single.py",
        "--file",
        file_path,
        "--dry-run",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("❌ Error in dry run:")
        print(result.stderr)
        return False

    print(result.stdout)
    return True


def main() -> int:
    print("🚀 Stack Auth Migration - Phase 1 Test")
    print("Testing migration approach on core user endpoints")
    print("=" * 80)

    # Check we're in the right directory
    if not Path("api/routers").exists():
        print("❌ Error: Must run from project root directory")
        return 1

    # Test each file
    for file_path in PHASE_1_FILES:
        if not Path(file_path).exists():
            print(f"⚠️  Warning: {file_path} not found, skipping")
            continue

        if not run_dry_run(file_path):
            print(f"\n❌ Dry run failed for {file_path}")
            print("Please fix issues before proceeding")
            return 1

    print("\n" + "=" * 80)
    print("✅ Phase 1 Dry Run Complete!")
    print("\nSummary:")
    print("- api/routers/users.py: 23 changes expected")
    print("- api/routers/business_profiles.py: 8 changes expected")
    print("\nNext steps:")
    print("1. Review the changes above")
    print("2. If they look correct, run migration with --execute")
    print("3. Run tests after each file migration")
    print("4. Test with real Stack Auth tokens")

    return 0


if __name__ == "__main__":
    sys.exit(main())
