#!/usr/bin/env python3
"""
Script to update all router files from Stack Auth to JWT authentication
"""

import re
from pathlib import Path


def update_file(file_path) -> bool:
    """Update a single file to use JWT auth instead of Stack Auth"""
    print(f"Updating {file_path}...")

    with open(file_path, "r") as f:
        content = f.read()

    # Track if we made changes
    original_content = content

    # Replace Stack Auth import with JWT auth import
    content = re.sub(
        r"from api\.dependencies\.stack_auth import get_current_stack_user(?:, get_current_user)?(?:, User)?",
        "from api.dependencies.auth import get_current_active_user\nfrom database.user import User",
        content,
    )

    # Replace Stack Auth dependency usage
    content = re.sub(
        r"current_user: dict = Depends\(get_current_stack_user\)",
        "current_user: User = Depends(get_current_active_user)",
        content,
    )

    # Replace other Stack Auth dependency patterns
    content = re.sub(
        r"Depends\(get_current_stack_user\)", "Depends(get_current_active_user)", content
    )

    # Handle cases where current_user is used as dict
    # We need to update access patterns from current_user["id"] to current_user.id
    content = re.sub(r'current_user\["id"\]', "str(current_user.id)", content)

    content = re.sub(r"current_user\[\"email\"\]", "current_user.email", content)

    content = re.sub(r'current_user\.get\("id"\)', "str(current_user.id)", content)

    content = re.sub(r'current_user\.get\("email"\)', "current_user.email", content)

    # Write back if changed
    if content != original_content:
        with open(file_path, "w") as f:
            f.write(content)
        print(f"✅ Updated {file_path}")
        return True
    else:
        print(f"⏭️  No changes needed for {file_path}")
        return False


def main() -> None:
    """Main function to update all router files"""
    router_dir = Path("api/routers")

    # Get all Python files that contain Stack Auth references
    files_to_update = []

    for py_file in router_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue

        with open(py_file, "r") as f:
            content = f.read()
            if "get_current_stack_user" in content:
                files_to_update.append(py_file)

    print(f"Found {len(files_to_update)} files to update:")
    for file_path in files_to_update:
        print(f"  - {file_path}")

    print("\nStarting updates...")
    updated_count = 0

    for file_path in files_to_update:
        if update_file(file_path):
            updated_count += 1

    print(f"\n✅ Successfully updated {updated_count} files")
    print("🔧 Manual review may be needed for complex usage patterns")


if __name__ == "__main__":
    main()
