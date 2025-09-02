#!/usr/bin/env python3
"""
Fix console statements by replacing them with TODO comments or proper logging patterns
"""

import os
import re
import glob


def fix_console_statements(content):
    """Replace console statements with appropriate alternatives"""

    # Pattern 1: Development/debug console statements with context
    patterns_and_replacements = [
        # Console error in catch blocks - already has proper comments
        (
            r"(\s*)// Development logging - consider proper logger\s*\n\s*console\.error\([^;]+\);",
            r"\1// TODO: Replace with proper logging\n\1// console.error(...);",
        ),
        # Simple console.log statements
        (r"(\s*)console\.log\([^;]+\);", r"\1// TODO: Replace with proper logging"),
        # Console.error statements
        (r"(\s*)console\.error\([^;]+\);", r"\1// TODO: Replace with proper logging"),
        # Console.warn statements
        (r"(\s*)console\.warn\([^;]+\);", r"\1// TODO: Replace with proper logging"),
        # Console.info statements
        (r"(\s*)console\.info\([^;]+\);", r"\1// TODO: Replace with proper logging"),
        # Console.debug statements
        (r"(\s*)console\.debug\([^;]+\);", r"\1// TODO: Replace with proper logging"),
    ]

    modified = False
    for pattern, replacement in patterns_and_replacements:
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        if new_content != content:
            modified = True
            content = new_content

    return content, modified


def process_files():
    """Process all TypeScript/JavaScript files in the frontend directory"""

    # File patterns to process
    patterns = [
        "app/**/*.tsx",
        "app/**/*.ts",
        "components/**/*.tsx",
        "components/**/*.ts",
        "lib/**/*.tsx",
        "lib/**/*.ts",
    ]

    files_processed = 0
    files_modified = 0

    for pattern in patterns:
        for file_path in glob.glob(pattern, recursive=True):
            try:
                # Skip node_modules and build directories
                if "node_modules" in file_path or ".next" in file_path:
                    continue

                with open(file_path, "r", encoding="utf-8") as f:
                    original_content = f.read()

                modified_content, was_modified = fix_console_statements(
                    original_content
                )

                if was_modified:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(modified_content)
                    print(f"✓ Fixed: {file_path}")
                    files_modified += 1

                files_processed += 1

            except Exception as e:
                print(f"✗ Error processing {file_path}: {e}")

    print(f"\nProcessed {files_processed} files")
    print(f"Modified {files_modified} files")
    return files_modified


if __name__ == "__main__":
    print("🔧 Fixing console statements...")
    modified_count = process_files()
    print(f"\n✅ Console statement fixes complete! Modified {modified_count} files.")
