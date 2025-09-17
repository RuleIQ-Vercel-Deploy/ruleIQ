#!/usr/bin/env python3
"""Quick dead code removal - focuses on safe removals only"""

import shutil
from pathlib import Path
from datetime import datetime

def main():
    project_root = Path("/home/omar/Documents/ruleIQ")

    # Create backup first
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = project_root / f"backup_deadcode_{timestamp}"

    print("=" * 80)
    print("QUICK DEAD CODE REMOVAL")
    print("=" * 80)

    print(f"\n📦 Creating backup at: {backup_dir}")
    backup_dir.mkdir(exist_ok=True)

    # Track changes
    files_deleted = 0
    lines_removed = 0

    # 1. Remove backup files
    print("\n🔍 Removing backup and temporary files...")
    backup_patterns = [
        "*.backup", "*.bak", "*.tmp", "*.old",
        "*_backup.py", "*_old.py", "*.orig"
    ]

    for pattern in backup_patterns:
        for file in project_root.rglob(pattern):
            if 'venv' in str(file) or '__pycache__' in str(file):
                continue
            if 'backup_deadcode' in str(file):  # Don't delete our own backup
                continue

            # Backup before deletion
            rel_path = file.relative_to(project_root)
            backup_file = backup_dir / rel_path
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file, backup_file)

            # Delete
            file.unlink()
            files_deleted += 1
            print(f"  ✅ Deleted: {rel_path}")

    # 2. Remove empty files
    print("\n🔍 Removing empty files...")
    for py_file in project_root.rglob("*.py"):
        if 'venv' in str(py_file) or '__pycache__' in str(py_file):
            continue

        if py_file.stat().st_size == 0:
            rel_path = py_file.relative_to(project_root)

            # Backup
            backup_file = backup_dir / rel_path
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(py_file, backup_file)

            # Delete
            py_file.unlink()
            files_deleted += 1
            print(f"  ✅ Deleted empty file: {rel_path}")

    # 3. Remove specific known dead files
    print("\n🔍 Removing known dead files...")
    known_dead = [
        "api/integrations/xero_integration.py",
        "frontend/.env.local.backup",
        "frontend/eslint.config.mjs.backup",
        "frontend/tsconfig.json.backup",
        "pytest.ini.backup",
    ]

    for dead_file in known_dead:
        file_path = project_root / dead_file
        if file_path.exists():
            # Backup
            backup_file = backup_dir / dead_file
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_file)

            # Delete
            file_path.unlink()
            files_deleted += 1
            print(f"  ✅ Deleted: {dead_file}")

    # 4. Clean up commented code in specific files
    print("\n🔍 Removing large commented code blocks...")
    files_to_clean = [
        "tests/test_graph_execution.py",
        "api/routers/chat.py",
    ]

    for file_path in files_to_clean:
        full_path = project_root / file_path
        if not full_path.exists():
            continue

        with open(full_path, 'r') as f:
            lines = f.readlines()

        # Backup
        backup_file = backup_dir / file_path
        backup_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(full_path, backup_file)

        # Remove consecutive comment blocks (more than 5 lines)
        new_lines = []
        comment_block = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith('#') and not stripped.startswith('#!'):
                comment_block.append(line)
            else:
                if len(comment_block) > 5:
                    # Large comment block - remove it
                    lines_removed += len(comment_block)
                    print(f"  ✅ Removed {len(comment_block)} lines of comments from {file_path}")
                else:
                    # Small comment block - keep it
                    new_lines.extend(comment_block)
                comment_block = []
                new_lines.append(line)

        # Handle final block
        if len(comment_block) <= 5:
            new_lines.extend(comment_block)
        else:
            lines_removed += len(comment_block)

        # Write cleaned file
        with open(full_path, 'w') as f:
            f.writelines(new_lines)

    # Summary
    print("\n" + "=" * 80)
    print("DEAD CODE REMOVAL COMPLETE")
    print("=" * 80)
    print("\n📊 Results:")
    print(f"  • Files deleted: {files_deleted}")
    print(f"  • Lines removed: {lines_removed}")
    print(f"  • Backup location: {backup_dir}")
    print("\n✅ Safe cleanup completed successfully!")
    print("Please review changes and run tests to verify functionality.")

if __name__ == "__main__":
    main()
