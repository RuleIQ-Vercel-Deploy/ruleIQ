#!/usr/bin/env python3
"""
Migrate all endpoints from JWT authentication to Stack Auth
This script will update all 140+ endpoints automatically
"""
import os
import re
from pathlib import Path
from typing import List, Tuple

# Define the replacements we need to make
REPLACEMENTS = [
    # Import replacements
    (
        r'from api\.dependencies\.auth import get_current_active_user',
        'from api.dependencies.stack_auth import get_current_stack_user'
    ),
    (
        r'from api\.dependencies\.auth import get_current_user',
        'from api.dependencies.stack_auth import get_current_stack_user'
    ),
    # Dependency replacements
    (
        r'Depends\(get_current_active_user\)',
        'Depends(get_current_stack_user)'
    ),
    (
        r'Depends\(get_current_user\)',
        'Depends(get_current_stack_user)'
    ),
    # Type hint replacements
    (
        r'current_user: User = Depends',
        'current_user: dict = Depends'
    ),
    (
        r'user: User = Depends',
        'user: dict = Depends'
    ),
    # User model attribute access replacements
    (
        r'current_user\.id',
        'current_user["id"]'
    ),
    (
        r'user\.id',
        'user["id"]'
    ),
    (
        r'current_user\.email',
        'current_user.get("primaryEmail", current_user.get("email", ""))'
    ),
    (
        r'user\.email',
        'user.get("primaryEmail", user.get("email", ""))'
    ),
    (
        r'current_user\.username',
        'current_user.get("displayName", "")'
    ),
    (
        r'user\.username',
        'user.get("displayName", "")'
    ),
]

def get_router_files() -> List[Path]:
    """Get all router files that need migration"""
    router_dir = Path("api/routers")
    exclude_files = {"auth.py", "google_auth.py", "test_utils.py"}  # Already handled
    
    router_files = []
    for file in router_dir.glob("*.py"):
        if file.name not in exclude_files and not file.name.startswith("_"):
            router_files.append(file)
    
    return router_files

def backup_file(file_path: Path) -> None:
    """Create a backup of the file before modifying"""
    backup_path = file_path.with_suffix(f"{file_path.suffix}.backup")
    if not backup_path.exists():
        backup_path.write_text(file_path.read_text())
        print(f"✅ Backed up: {file_path} -> {backup_path}")

def migrate_file(file_path: Path, dry_run: bool = False) -> List[str]:
    """Migrate a single file from JWT to Stack Auth"""
    changes = []
    content = file_path.read_text()
    original_content = content
    
    for pattern, replacement in REPLACEMENTS:
        matches = list(re.finditer(pattern, content))
        if matches:
            for match in matches:
                changes.append(f"  - Line {content[:match.start()].count(chr(10)) + 1}: {match.group()} -> {replacement}")
            content = re.sub(pattern, replacement, content)
    
    # Special handling for User model imports
    if "from database import User" in content or "from database.models import User" in content:
        # Check if User is only used for type hints
        user_pattern = r'\bUser\b(?!\s*\()'  # Match User not followed by (
        if re.search(user_pattern, content):
            changes.append(f"  - Found User model references that may need manual review")
    
    if changes and not dry_run:
        backup_file(file_path)
        file_path.write_text(content)
        print(f"✅ Migrated: {file_path} ({len(changes)} changes)")
    elif changes:
        print(f"🔍 Would migrate: {file_path} ({len(changes)} changes)")
    
    return changes

def generate_migration_report(results: dict) -> None:
    """Generate a detailed migration report"""
    report_path = Path("STACK_AUTH_MIGRATION_REPORT.md")
    
    report = [
        "# Stack Auth Migration Report",
        "",
        "## Summary",
        f"- Total files analyzed: {len(results)}",
        f"- Files with changes: {sum(1 for changes in results.values() if changes)}",
        f"- Total changes: {sum(len(changes) for changes in results.values())}",
        "",
        "## Details by File",
        ""
    ]
    
    for file_path, changes in results.items():
        if changes:
            report.append(f"### {file_path}")
            report.extend(changes)
            report.append("")
    
    report_path.write_text("\n".join(report))
    print(f"\n📄 Migration report saved to: {report_path}")

def main():
    """Run the migration"""
    print("🚀 Stack Auth Migration Script")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("api/routers").exists():
        print("❌ Error: Must run from project root directory")
        return
    
    # Get confirmation
    response = input("\nThis will migrate all router files from JWT to Stack Auth.\nCreate backups and continue? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Migration cancelled")
        return
    
    # Dry run first
    print("\n📋 Performing dry run...")
    router_files = get_router_files()
    dry_run_results = {}
    
    for file_path in router_files:
        changes = migrate_file(file_path, dry_run=True)
        if changes:
            dry_run_results[str(file_path)] = changes
    
    if not dry_run_results:
        print("\n✅ No changes needed - all files already migrated!")
        return
    
    # Show summary
    print(f"\n📊 Dry run complete: {sum(len(c) for c in dry_run_results.values())} changes in {len(dry_run_results)} files")
    
    # Confirm actual migration
    response = input("\nProceed with actual migration? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Migration cancelled")
        return
    
    # Perform actual migration
    print("\n🔧 Performing migration...")
    results = {}
    
    for file_path in router_files:
        changes = migrate_file(file_path, dry_run=False)
        results[str(file_path)] = changes
    
    # Generate report
    generate_migration_report(results)
    
    print("\n✅ Migration complete!")
    print("\n⚠️  Important next steps:")
    print("1. Review the migration report: STACK_AUTH_MIGRATION_REPORT.md")
    print("2. Check for any User model references that need manual updates")
    print("3. Run tests: pytest tests/")
    print("4. Test each endpoint manually with Stack Auth tokens")
    print("5. Update any service layer functions that expect User models")

if __name__ == "__main__":
    main()