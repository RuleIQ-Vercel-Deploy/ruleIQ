#!/usr/bin/env python3
"""
Dry run of Stack Auth migration to show what changes would be made
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
    exclude_files = {"auth.py", "google_auth.py", "test_utils.py", "stack_auth.py"}  # Already handled
    
    router_files = []
    for file in router_dir.glob("*.py"):
        if file.name not in exclude_files and not file.name.startswith("_"):
            router_files.append(file)
    
    return router_files

def analyze_file(file_path: Path) -> List[str]:
    """Analyze a single file for needed changes"""
    changes = []
    content = file_path.read_text()
    
    # Track line numbers for better reporting
    lines = content.split('\n')
    
    for pattern, replacement in REPLACEMENTS:
        for line_num, line in enumerate(lines, 1):
            if re.search(pattern, line):
                changes.append(f"  Line {line_num}: {line.strip()} -> would change to use Stack Auth")
    
    # Special handling for User model imports
    for line_num, line in enumerate(lines, 1):
        if "from database import User" in line or "from database.models import User" in line:
            changes.append(f"  Line {line_num}: {line.strip()} -> User model import found, needs review")
    
    # Check for User type hints
    user_type_pattern = r':\s*User\s*[=\)]'
    for line_num, line in enumerate(lines, 1):
        if re.search(user_type_pattern, line):
            changes.append(f"  Line {line_num}: {line.strip()} -> User type hint needs updating to dict")
    
    return changes

def main():
    """Run the dry-run analysis"""
    print("🔍 Stack Auth Migration Dry Run")
    print("=" * 70)
    print("\nThis is a DRY RUN - no files will be modified")
    print("\nAnalyzing router files for needed changes...")
    print("-" * 70)
    
    # Check if we're in the right directory
    if not Path("api/routers").exists():
        print("❌ Error: Must run from project root directory")
        return
    
    router_files = sorted(get_router_files())
    total_changes = 0
    files_needing_changes = 0
    
    results = {}
    
    for file_path in router_files:
        changes = analyze_file(file_path)
        if changes:
            results[file_path] = changes
            files_needing_changes += 1
            total_changes += len(changes)
            print(f"\n📄 {file_path}")
            print(f"   Found {len(changes)} changes needed:")
            for change in changes[:5]:  # Show first 5 changes
                print(f"   {change}")
            if len(changes) > 5:
                print(f"   ... and {len(changes) - 5} more changes")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 DRY RUN SUMMARY")
    print("=" * 70)
    print(f"Total files analyzed: {len(router_files)}")
    print(f"Files needing changes: {files_needing_changes}")
    print(f"Total changes needed: {total_changes}")
    
    if files_needing_changes > 0:
        print("\n📋 Files that need migration:")
        for file_path in results:
            print(f"  - {file_path} ({len(results[file_path])} changes)")
    
    print("\n✅ Dry run complete - no files were modified")
    print("\nTo perform the actual migration, you would need to:")
    print("1. Back up all router files")
    print("2. Run the migration script with confirmation")
    print("3. Test all endpoints with Stack Auth tokens")
    print("4. Update any service layer code that expects User models")

if __name__ == "__main__":
    main()