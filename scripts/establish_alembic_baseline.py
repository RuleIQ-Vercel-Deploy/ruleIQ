#!/usr/bin/env python3
"""
Establish proper Alembic baseline by consolidating migrations.

This script:
1. Removes the empty initial migration
2. Makes the comprehensive migration the new baseline
3. Ensures clean migration history for production deployment
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


def main() -> bool:
    """Establish Alembic baseline."""
    print("🔧 Establishing Alembic baseline...")

    # Change to project root
    os.chdir(project_root)

    # Step 1: Check current Alembic status
    print("📋 Checking current Alembic status...")
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "current"], capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"❌ Failed to check Alembic status: {result.stderr}")
        return False

    print(f"Current revision: {result.stdout.strip()}")

    # Step 2: Remove the empty initial migration file
    empty_migration = (
        project_root
        / "alembic"
        / "versions"
        / "cdd9337435cf_initial_empty_migration.py"
    )
    if empty_migration.exists():
        print("🗑️ Removing empty initial migration...")
        empty_migration.unlink()
        print("✅ Empty migration removed")

    # Step 3: Update the comprehensive migration to be the baseline
    comprehensive_migration = (
        project_root
        / "alembic"
        / "versions"
        / "802adb6d1be8_add_check_constraint_to_compliance_.py"
    )
    if comprehensive_migration.exists():
        print("📝 Updating comprehensive migration to be baseline...")

        # Read the current migration content
        with open(comprehensive_migration, "r") as f:
            content = f.read()

        # Update the down_revision to None to make it the baseline
        updated_content = content.replace(
            "down_revision = 'cdd9337435cf'", "down_revision = None"
        )

        # Update the revision message to indicate it's the baseline
        updated_content = updated_content.replace(
            '"Add check constraint to compliance_frameworks"',
            '"Baseline schema - comprehensive database structure"',
        )

        # Write back the updated content
        with open(comprehensive_migration, "w") as f:
            f.write(updated_content)

        print("✅ Comprehensive migration updated as baseline")

    # Step 4: Generate fresh Alembic revision history
    print("🔄 Updating Alembic revision history...")
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "stamp", "head"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"❌ Failed to stamp Alembic head: {result.stderr}")
        return False

    print("✅ Alembic baseline established successfully!")

    # Step 5: Verify the setup
    print("🔍 Verifying baseline setup...")
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "current"], capture_output=True, text=True
    )

    if result.returncode == 0:
        print(f"✅ Current revision: {result.stdout.strip()}")
        print("🎉 Alembic baseline establishment complete!")
        return True
    else:
        print(f"❌ Verification failed: {result.stderr}")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
