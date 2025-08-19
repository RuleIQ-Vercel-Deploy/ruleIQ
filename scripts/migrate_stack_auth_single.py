#!/usr/bin/env python3
"""
Single-file Stack Auth migration with mandatory dry run
Follows the migration plan schema exactly
"""

import argparse
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import sys

# Migration patterns based on our schema
MIGRATION_PATTERNS = [
    # Import replacements
    {
        "pattern": r"from api\.dependencies\.auth import get_current_active_user",
        "replacement": "from api.dependencies.stack_auth import get_current_stack_user",
        "description": "Import: get_current_active_user -> get_current_stack_user",
    },
    {
        "pattern": r"from api\.dependencies\.auth import get_current_user",
        "replacement": "from api.dependencies.stack_auth import get_current_stack_user",
        "description": "Import: get_current_user -> get_current_stack_user",
    },
    # Combined imports
    {
        "pattern": r"from api\.dependencies\.auth import get_current_active_user, get_current_user",
        "replacement": "from api.dependencies.stack_auth import get_current_stack_user",
        "description": "Import: Combined auth imports -> get_current_stack_user",
    },
    {
        "pattern": r"from api\.dependencies\.auth import get_current_user, get_current_active_user",
        "replacement": "from api.dependencies.stack_auth import get_current_stack_user",
        "description": "Import: Combined auth imports -> get_current_stack_user",
    },
    # Dependency replacements
    {
        "pattern": r"Depends\(get_current_active_user\)",
        "replacement": "Depends(get_current_stack_user)",
        "description": "Dependency: get_current_active_user -> get_current_stack_user",
    },
    {
        "pattern": r"Depends\(get_current_user\)",
        "replacement": "Depends(get_current_stack_user)",
        "description": "Dependency: get_current_user -> get_current_stack_user",
    },
]

# Type annotation patterns (need special handling)
TYPE_PATTERNS = [
    {
        "pattern": r"(\w+):\s*User\s*=\s*Depends",
        "replacement": r"\1: dict = Depends",
        "description": "Type hint: User -> dict",
    },
]

# Attribute access patterns (need context-aware replacement)
ATTRIBUTE_PATTERNS = [
    {
        "pattern": r"(\w+)\.id\b",
        "replacement": r'\1["id"]',
        "description": "Attribute: .id -> ['id']",
        "user_vars": ["current_user", "user", "auth_user", "authenticated_user"],
    },
    {
        "pattern": r"(\w+)\.email\b",
        "replacement": r'\1.get("primaryEmail", \1.get("email", ""))',
        "description": "Attribute: .email -> .get('primaryEmail', ...)",
        "user_vars": ["current_user", "user", "auth_user", "authenticated_user"],
    },
    {
        "pattern": r"(\w+)\.username\b",
        "replacement": r'\1.get("displayName", "")',
        "description": "Attribute: .username -> .get('displayName', '')",
        "user_vars": ["current_user", "user", "auth_user", "authenticated_user"],
    },
    {
        "pattern": r"(\w+)\.is_active\b",
        "replacement": r'\1.get("isActive", True)',
        "description": "Attribute: .is_active -> .get('isActive', True)",
        "user_vars": ["current_user", "user", "auth_user", "authenticated_user"],
    },
    {
        "pattern": r"(\w+)\.is_superuser\b",
        "replacement": r'any(r.get("name") == "admin" for r in \1.get("roles", []))',
        "description": "Attribute: .is_superuser -> role check",
        "user_vars": ["current_user", "user", "auth_user", "authenticated_user"],
    },
]


def analyze_file(file_path: Path) -> Dict[str, List[Dict]]:
    """Analyze a file and return all needed changes"""
    content = file_path.read_text()
    lines = content.split("\n")

    changes = {
        "imports": [],
        "dependencies": [],
        "type_hints": [],
        "attributes": [],
        "user_imports": [],
    }

    # Check for User model imports
    for i, line in enumerate(lines):
        if re.search(r"from database(?:\.models)? import.*\bUser\b", line):
            changes["user_imports"].append(
                {
                    "line": i + 1,
                    "content": line.strip(),
                    "action": "Review if User model is needed beyond type hints",
                }
            )

    # Apply migration patterns
    for pattern_info in MIGRATION_PATTERNS:
        pattern = pattern_info["pattern"]
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                category = "imports" if "import" in pattern else "dependencies"
                changes[category].append(
                    {
                        "line": i + 1,
                        "content": line.strip(),
                        "pattern": pattern,
                        "replacement": pattern_info["replacement"],
                        "description": pattern_info["description"],
                    }
                )

    # Apply type patterns
    for pattern_info in TYPE_PATTERNS:
        pattern = pattern_info["pattern"]
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                changes["type_hints"].append(
                    {
                        "line": i + 1,
                        "content": line.strip(),
                        "pattern": pattern,
                        "replacement": pattern_info["replacement"],
                        "description": pattern_info["description"],
                    }
                )

    # Apply attribute patterns (context-aware)
    for pattern_info in ATTRIBUTE_PATTERNS:
        pattern = pattern_info["pattern"]
        for i, line in enumerate(lines):
            matches = re.finditer(pattern, line)
            for match in matches:
                var_name = match.group(1)
                if var_name in pattern_info["user_vars"]:
                    changes["attributes"].append(
                        {
                            "line": i + 1,
                            "content": line.strip(),
                            "pattern": pattern,
                            "match": match.group(0),
                            "replacement": pattern_info["replacement"],
                            "description": pattern_info["description"],
                        }
                    )

    return changes


def print_dry_run_report(file_path: Path, changes: Dict[str, List[Dict]]) -> int:
    """Print detailed dry run report"""
    total_changes = sum(len(v) for v in changes.values())

    print(f"\n{'=' * 80}")
    print(f"DRY RUN REPORT: {file_path}")
    print(f"{'=' * 80}")
    print(f"Total changes needed: {total_changes}")

    if total_changes == 0:
        print("✅ No changes needed - file already migrated or doesn't use auth")
        return 0

    # Import changes
    if changes["imports"]:
        print(f"\n📦 Import Changes ({len(changes['imports'])})")
        print("-" * 40)
        for change in changes["imports"]:
            print(f"  Line {change['line']}: {change['description']}")
            print(f"    From: {change['content']}")
            print(f"    To:   {change['replacement']}")

    # User model imports
    if changes["user_imports"]:
        print(f"\n⚠️  User Model Imports ({len(changes['user_imports'])}) - Need Review")
        print("-" * 40)
        for change in changes["user_imports"]:
            print(f"  Line {change['line']}: {change['content']}")
            print(f"    Action: {change['action']}")

    # Dependency changes
    if changes["dependencies"]:
        print(f"\n🔗 Dependency Changes ({len(changes['dependencies'])})")
        print("-" * 40)
        for change in changes["dependencies"]:
            print(f"  Line {change['line']}: {change['description']}")

    # Type hint changes
    if changes["type_hints"]:
        print(f"\n📝 Type Hint Changes ({len(changes['type_hints'])})")
        print("-" * 40)
        for change in changes["type_hints"]:
            print(f"  Line {change['line']}: {change['description']}")
            print(f"    From: {change['content']}")

    # Attribute access changes
    if changes["attributes"]:
        print(f"\n🔍 Attribute Access Changes ({len(changes['attributes'])})")
        print("-" * 40)
        for change in changes["attributes"]:
            print(f"  Line {change['line']}: {change['description']}")
            print(f"    In: {change['content']}")
            print(
                f"    Change: {change['match']} -> {change['description'].split('->')[-1].strip()}"
            )

    return total_changes


def apply_migrations(file_path: Path, changes: Dict[str, List[Dict]]) -> str:
    """Apply all migrations to file content"""
    content = file_path.read_text()

    # Apply replacements in reverse line order to maintain line numbers
    all_changes = []
    for category, change_list in changes.items():
        if category != "user_imports":  # Skip user imports, they need manual review
            all_changes.extend(change_list)

    # Sort by line number in reverse
    all_changes.sort(key=lambda x: x["line"], reverse=True)

    lines = content.split("\n")

    for change in all_changes:
        line_idx = change["line"] - 1
        if line_idx < len(lines):
            old_line = lines[line_idx]

            if "pattern" in change and "replacement" in change:
                # For simple pattern replacements
                if isinstance(change["replacement"], str) and not change["replacement"].startswith(
                    r"\1"
                ):
                    new_line = re.sub(change["pattern"], change["replacement"], old_line)
                else:
                    # For backreference replacements
                    new_line = re.sub(change["pattern"], change["replacement"], old_line)
                lines[line_idx] = new_line

    return "\n".join(lines)


def create_backup(file_path: Path) -> Path:
    """Create timestamped backup"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = file_path.with_suffix(f".{timestamp}.jwt-backup")
    shutil.copy2(file_path, backup_path)
    return backup_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate single file to Stack Auth")
    parser.add_argument("--file", required=True, help="Path to file to migrate")
    parser.add_argument(
        "--dry-run", action="store_true", default=True, help="Perform dry run (default: True)"
    )
    parser.add_argument(
        "--execute", action="store_true", help="Execute migration (requires explicit flag)"
    )

    args = parser.parse_args()

    file_path = Path(args.file)
    if not file_path.exists():
        print(f"❌ Error: File not found: {file_path}")
        return 1

    # Analyze file
    changes = analyze_file(file_path)
    total_changes = print_dry_run_report(file_path, changes)

    if total_changes == 0:
        return 0

    # If only dry run, stop here
    if not args.execute:
        print(f"\n{'=' * 80}")
        print("ℹ️  This was a DRY RUN. No files were modified.")
        print("To execute migration, run with --execute flag")
        print(f"{'=' * 80}")
        return 0

    # Execute migration
    print(f"\n{'=' * 80}")
    print("🚀 EXECUTING MIGRATION")
    print(f"{'=' * 80}")

    # Create backup
    backup_path = create_backup(file_path)
    print(f"✅ Backup created: {backup_path}")

    # Apply migrations
    new_content = apply_migrations(file_path, changes)
    file_path.write_text(new_content)
    print(f"✅ Migration applied to: {file_path}")

    # Final instructions
    print("\n📋 Next Steps:")
    print(f"1. Run tests: pytest tests/test_{file_path.stem}.py -v")
    print(
        "2. Test with curl: curl -H 'Authorization: Bearer <stack-token>' http://localhost:8000/api/..."
    )
    print(f"3. If issues, restore: cp {backup_path} {file_path}")
    print(
        f"4. Commit: git add {file_path} && git commit -m 'feat: migrate {file_path.stem} to Stack Auth'"
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
