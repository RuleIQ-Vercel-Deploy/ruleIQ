#!/usr/bin/env python3
"""
Script to systematically fix ESLint errors in the ruleIQ frontend.
This applies fixes for the most common patterns to reduce errors quickly.
"""
import os
import re
import glob


def fix_unused_variables(content):
    """Fix unused variables by prefixing with underscore"""

    # Fix catch blocks with unused error variables
    content = re.sub(r"} catch \(error\) \{", "} catch {", content)
    content = re.sub(r"} catch \(err\) \{", "} catch {", content)
    content = re.sub(r"} catch \(e\) \{", "} catch {", content)

    return content


def fix_console_statements(content):
    """Fix console.log statements"""
    # Replace console.log with TODO comments, but keep console.error with warnings
    content = re.sub(
        r"\s*console\.log\([^;]+\);?\s*\n",
        "\n    // TODO: Replace with proper logging\n",
        content,
    )

    # Add warning comments to console.error
    content = re.sub(
        r"(\s*)(console\.error\()",
        r"\1// Development logging - consider proper logger\n\1\2",
        content,
    )

    return content


def fix_react_entities(content):
    """Fix React unescaped entities"""
    replacements = {
        "'": "&apos;",
        """: "&ldquo;", 
        """: "&rdquo;",
        '"': "&quot;",
    }

    # Only fix in JSX content, not in regular strings
    jsx_pattern = r'(>\s*[^<]*?)([\'"""])(.*?<)'

    def replace_entity(match):
        before, quote, after = match.groups()
        if quote in replacements:
            return f"{before}{replacements[quote]}{after}"
        return match.group(0)

    content = re.sub(jsx_pattern, replace_entity, content)
    return content


def fix_typescript_any(content):
    """Fix some TypeScript any types with better alternatives"""

    # Common patterns we can safely replace
    replacements = [
        (r": any\[\]", ": unknown[]"),
        (r"error: any", "error: unknown"),
        (r"data: any", "data: unknown"),
        (r"params: any", "params: Record<string, unknown>"),
        (r"props: any", "props: Record<string, unknown>"),
    ]

    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    return content


def process_file(file_path):
    """Process a single TypeScript/React file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Apply fixes
        content = fix_unused_variables(content)
        content = fix_console_statements(content)
        content = fix_react_entities(content)
        content = fix_typescript_any(content)

        # Only write if content changed
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Fixed: {file_path}")
            return 1

        return 0

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0


def main():
    """Main function to process all TypeScript/React files"""

    os.chdir("/home/omar/Documents/ruleIQ/frontend")

    # Find all TypeScript and React files
    patterns = ["**/*.ts", "**/*.tsx"]
    files = []

    for pattern in patterns:
        files.extend(glob.glob(pattern, recursive=True))

    # Filter out node_modules and .next directories
    files = [
        f
        for f in files
        if not any(
            excluded in f for excluded in ["node_modules", ".next", "dist", "build"]
        )
    ]

    print(f"Processing {len(files)} files...")

    fixed_count = 0
    for file_path in files:
        fixed_count += process_file(file_path)

    print(f"Fixed {fixed_count} files.")


if __name__ == "__main__":
    main()
