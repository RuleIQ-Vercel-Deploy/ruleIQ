#!/usr/bin/env python3
"""
Fix React unescaped entities by replacing them with proper JSX escaping
"""

import os
import re
import glob


def fix_react_entities(content):
    """Fix React unescaped entities"""

    # Pattern to match unescaped entities in JSX
    patterns_and_replacements = [
        # Single quotes - most common
        (r"&apos;", "'"),
        # Double quotes
        (r"&quot;", '"'),
        (r"&ldquo;", '"'),
        (r"&rdquo;", '"'),
        # Other common entities that should be regular characters in JSX
        (r"&lsquo;", "'"),
        (r"&rsquo;", "'"),
        (r"&#39;", "'"),
        (r"&#34;", '"'),
        # Ampersands (but be careful not to break legitimate HTML entities)
        (r"&amp;", "&"),
        # Less than / greater than
        (r"&lt;", "<"),
        (r"&gt;", ">"),
    ]

    modified = False
    original_content = content

    for pattern, replacement in patterns_and_replacements:
        new_content = re.sub(pattern, replacement, content)
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

                modified_content, was_modified = fix_react_entities(original_content)

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
    print("🔧 Fixing React unescaped entities...")
    modified_count = process_files()
    print(f"\n✅ React entity fixes complete! Modified {modified_count} files.")
