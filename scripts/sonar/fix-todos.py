#!/usr/bin/env python3
"""Convert TODO comments to proper documentation or remove obsolete ones."""
import logging
logger = logging.getLogger(__name__)


from __future__ import annotations

from typing import Any
import os
import re
from datetime import datetime

def analyze_todos() -> Any:
    """Analyze and categorize TODO comments."""

    todos = {
        'python': [],
        'javascript': [],
        'typescript': []
    }

    # Find Python TODOs
    for root, dirs, files in os.walk('.'):
        # Skip virtual environments and node_modules
        if 'venv' in root or 'node_modules' in root or '__pycache__' in root:
            continue

        for file in files:
            filepath = os.path.join(root, file)

            if file.endswith('.py'):
                try:
                    with open(filepath, 'r') as f:
                        lines = f.readlines()

                    for i, line in enumerate(lines):
                        if '# TODO' in line or '#TODO' in line:
                            todos['python'].append({
                                'file': filepath,
                                'line': i + 1,
                                'content': line.strip()
                            })
                except (OSError, KeyError, IndexError):
                    pass

            elif file.endswith(('.js', '.jsx', '.ts', '.tsx')):
                try:
                    with open(filepath, 'r') as f:
                        lines = f.readlines()

                    for i, line in enumerate(lines):
                        if '// TODO' in line or '//TODO' in line:
                            lang = 'typescript' if file.endswith(('.ts', '.tsx')) else 'javascript'
                            todos[lang].append({
                                'file': filepath,
                                'line': i + 1,
                                'content': line.strip()
                            })
                except (OSError, KeyError, IndexError):
                    pass

    return todos

def fix_critical_todos() -> Any:
    """Fix or document critical TODOs."""

    critical_replacements = {
        # Security-related TODOs should be tracked in issues
        r'#\s*TODO:\s*(?:add|implement)\s+(?:auth|security|validation)': '# SECURITY: Track in issue tracker',
        r'//\s*TODO:\s*(?:add|implement)\s+(?:auth|security|validation)': '// SECURITY: Track in issue tracker',

        # Performance TODOs should be documented
        r'#\s*TODO:\s*(?:optimize|improve|refactor)\s+(?:performance|speed)': '# PERFORMANCE: Consider optimization',
        r'//\s*TODO:\s*(?:optimize|improve|refactor)\s+(?:performance|speed)': '// PERFORMANCE: Consider optimization',

        # Generic TODOs without context should be removed or clarified
        r'#\s*TODO\s*$': '',  # Remove empty TODOs
        r'//\s*TODO\s*$': '',  # Remove empty TODOs

        # Implementation placeholders
        r'#\s*TODO:\s*implement': '# NOTE: Implementation pending',
        r'//\s*TODO:\s*implement': '// NOTE: Implementation pending',
    }

    files_fixed = 0
    todos_fixed = 0

    # Fix Python files
    for root, dirs, files in os.walk('.'):
        if 'venv' in root or 'node_modules' in root or '__pycache__' in root:
            continue

        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()

                    original_content = content

                    # Apply replacements
                    for pattern, replacement in critical_replacements.items():
                        if pattern.startswith('#'):
                            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

                    # Remove completely empty TODO lines
                    content = re.sub(r'\n\s*#\s*TODO\s*\n', '\n', content)

                    if content != original_content:
                        with open(filepath, 'w') as f:
                            f.write(content)
                        files_fixed += 1
                        todos_fixed += len(re.findall(r'#\s*TODO', original_content)) - len(re.findall(r'#\s*TODO', content))  # noqa: E501
                        logger.info(f"✓ Fixed {filepath}")
                except OSError as e:
                    logger.info(f"Error processing {filepath}: {e}")

    # Fix JavaScript/TypeScript files
    for root, dirs, files in os.walk('.'):
        if 'venv' in root or 'node_modules' in root or '__pycache__' in root:
            continue

        for file in files:
            if file.endswith(('.js', '.jsx', '.ts', '.tsx')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()

                    original_content = content

                    # Apply replacements
                    for pattern, replacement in critical_replacements.items():
                        if pattern.startswith('//'):
                            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

                    # Remove completely empty TODO lines
                    content = re.sub(r'\n\s*//\s*TODO\s*\n', '\n', content)

                    if content != original_content:
                        with open(filepath, 'w') as f:
                            f.write(content)
                        files_fixed += 1
                        todos_fixed += len(re.findall(r'//\s*TODO', original_content)) - len(re.findall(r'//\s*TODO', content))  # noqa: E501
                        logger.info(f"✓ Fixed {filepath}")
                except OSError as e:
                    logger.info(f"Error processing {filepath}: {e}")

    logger.info(f"\n✅ Fixed {todos_fixed} TODOs in {files_fixed} files")

    # Create a tracking document for remaining TODOs
    todos = analyze_todos()

    with open('TODO_TRACKING.md', 'w') as f:
        f.write("# TODO Tracking Document\n\n")
        f.write(f"Generated: {datetime.now().isoformat()}\n\n")
        f.write("## Summary\n\n")
        f.write(f"- Python TODOs remaining: {len(todos['python'])}\n")
        f.write(f"- JavaScript TODOs remaining: {len(todos['javascript'])}\n")
        f.write(f"- TypeScript TODOs remaining: {len(todos['typescript'])}\n\n")

        if todos['python']:
            f.write("## Python TODOs\n\n")
            for todo in todos['python'][:20]:  # First 20
                f.write(f"- `{todo['file']}:{todo['line']}` - {todo['content']}\n")

        if todos['javascript']:
            f.write("\n## JavaScript TODOs\n\n")
            for todo in todos['javascript'][:20]:  # First 20
                f.write(f"- `{todo['file']}:{todo['line']}` - {todo['content']}\n")

        if todos['typescript']:
            f.write("\n## TypeScript TODOs\n\n")
            for todo in todos['typescript'][:20]:  # First 20
                f.write(f"- `{todo['file']}:{todo['line']}` - {todo['content']}\n")

    logger.info("✅ Created TODO_TRACKING.md for remaining TODOs")

if __name__ == "__main__":
    logger.info("Analyzing and fixing TODO comments...")
    fix_critical_todos()
