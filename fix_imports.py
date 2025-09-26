#!/usr/bin/env python3
"""Script to fix common import issues in Python files."""

import os

def fix_file_imports(filepath):
    """Fix common import issues in a Python file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        original = content
        lines = content.split('\n')

        # Check if file uses logger but doesn't import it
        if 'logger.' in content or 'logger =' in content:
            if 'import logging' not in content:
                # Find the right place to add import
                import_idx = 0
                for i, line in enumerate(lines):
                    if line.startswith('from ') or line.startswith('import '):
                        import_idx = i + 1
                    elif import_idx > 0 and not line.startswith(('from ', 'import ')):
                        break

                if import_idx == 0:
                    # No imports found, add after docstring
                    for i, line in enumerate(lines):
                        if i > 0 and (lines[i-1].endswith('"""') or lines[i-1].endswith("'''")):
                            import_idx = i
                            break

                lines.insert(import_idx, 'import logging')

                # Add logger definition if not present
                if 'logger = logging.getLogger' not in content:
                    # Add after imports
                    for i in range(import_idx, len(lines)):
                        if not lines[i].startswith(('from ', 'import ')) and lines[i].strip():
                            lines.insert(i, '')
                            lines.insert(i+1, 'logger = logging.getLogger(__name__)')
                            break

        # Check for json usage without import
        if 'json.' in content and 'import json' not in content:
            import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('import '):
                    import_idx = i + 1
            if import_idx > 0:
                lines.insert(import_idx, 'import json')

        # Check for requests usage without import
        if 'requests.' in content and 'import requests' not in content:
            import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith('import '):
                    import_idx = i + 1
            if import_idx > 0:
                lines.insert(import_idx, 'import requests')

        new_content = '\n'.join(lines)

        if new_content != original:
            with open(filepath, 'w') as f:
                f.write(new_content)
            return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    return False

def main():
    """Main function to process all Python files."""
    fixed_count = 0

    for root, dirs, files in os.walk('.'):
        # Skip virtual env and other directories
        if any(skip in root for skip in ['.venv', '__pycache__', '.git', 'node_modules']):
            continue

        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if fix_file_imports(filepath):
                    fixed_count += 1
                    print(f"Fixed: {filepath}")

    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    main()
