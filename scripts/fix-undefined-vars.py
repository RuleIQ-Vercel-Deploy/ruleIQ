#!/usr/bin/env python3
"""
Script to fix undefined variables in catch blocks and similar patterns.
"""
import os
import re
import glob


def fix_undefined_error_vars(content):
    """Fix undefined error variables in catch blocks"""

    # Pattern 1: } catch { ... console.error('...', err); ...
    # Fix by adding (err) to catch
    patterns = [
        # Pattern: } catch { followed by usage of 'err'
        (
            r"(\s*}\s*catch\s*{\s*[^}]*?)(console\.error\([^,]+,\s*err\))",
            lambda m: m.group(1).replace("catch {", "catch (err) {") + m.group(2),
        ),
        # Pattern: } catch { followed by setError(err
        (
            r"(\s*}\s*catch\s*{\s*[^}]*?)(setError\(err)",
            lambda m: m.group(1).replace("catch {", "catch (err) {") + m.group(2),
        ),
        # Pattern: } catch { followed by usage of 'error'
        (
            r"(\s*}\s*catch\s*{\s*[^}]*?)(console\.error\([^,]+,\s*error\))",
            lambda m: m.group(1).replace("catch {", "catch (error) {") + m.group(2),
        ),
        # Pattern: } catch { followed by setError(error
        (
            r"(\s*}\s*catch\s*{\s*[^}]*?)(setError\(error)",
            lambda m: m.group(1).replace("catch {", "catch (error) {") + m.group(2),
        ),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)

    return content


def fix_parsing_issues(content):
    """Fix common parsing issues"""

    # Fix mismatched quotes in JSX
    content = re.sub(r"getValues\(&apos;([^']*)'&apos;\)", r"getValues('\1')", content)
    content = re.sub(r"&apos;([^']*&apos;)", r"'\1'", content)

    # Fix raw HTML entities in array strings
    content = re.sub(
        r"^\s*&apos;([^']*)',", r"      '\1',", content, flags=re.MULTILINE
    )

    return content


def process_file(file_path):
    """Process a single TypeScript/React file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Apply fixes
        content = fix_undefined_error_vars(content)
        content = fix_parsing_issues(content)

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

    print(f"Processing {len(files)} files for undefined variable fixes...")

    fixed_count = 0
    for file_path in files:
        fixed_count += process_file(file_path)

    print(f"Fixed {fixed_count} files.")


if __name__ == "__main__":
    main()
