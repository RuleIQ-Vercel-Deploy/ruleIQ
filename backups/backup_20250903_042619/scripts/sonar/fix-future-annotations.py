"""
Fix FA100: Add 'from __future__ import annotations' to all Python files.
This enables postponed evaluation of type annotations (PEP 563).
"""
import logging
logger = logging.getLogger(__name__)
import ast
import os
import sys
from pathlib import Path
from typing import List, Tuple

def needs_future_annotations(file_path: Path) -> bool:
    """Check if file needs future annotations import."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'from __future__ import annotations' in content:
            return False
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return False
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.returns or any((arg.annotation for arg in node.args.args)):
                    return True
            elif isinstance(node, ast.AnnAssign):
                return True
            elif isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.AnnAssign):
                        return True
        return False
    except ValueError:
        return False

def add_future_annotations(file_path: Path) -> bool:
    """Add future annotations import to the file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        if not lines:
            return False
        insert_index = 0
        has_docstring = False
        has_shebang = False
        has_encoding = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            if i == 0 and stripped.startswith('#!'):
                has_shebang = True
                insert_index = 1
                continue
            if i <= 1 and ('coding:' in stripped or 'coding=' in stripped):
                has_encoding = True
                insert_index = i + 1
                continue
            if not has_docstring and (stripped.startswith('"""') or stripped.startswith("'''")):
                quote = '"""' if stripped.startswith('"""') else "'''"
                if stripped.count(quote) >= 2:
                    has_docstring = True
                    insert_index = i + 1
                else:
                    for j in range(i + 1, len(lines)):
                        if quote in lines[j]:
                            has_docstring = True
                            insert_index = j + 1
                            break
                continue
            if stripped and (not stripped.startswith('#')):
                insert_index = i
                break
        import_line = 'from __future__ import annotations\n'
        if insert_index < len(lines) and lines[insert_index].strip():
            import_line += '\n'
        lines.insert(insert_index, import_line)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        return True
    except (OSError, KeyError, IndexError) as e:
        logger.info(f'Error processing {file_path}: {e}')
        return False

def main() -> None:
    """Main function to fix future annotations in all Python files."""
    logger.info("Adding 'from __future__ import annotations' to Python files...")
    logger.info('=' * 60)
    python_files = []
    exclude_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'build', 'dist', '.pytest_cache', '.mypy_cache', '.ruff_cache'}
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                python_files.append(file_path)
    logger.info(f'Found {len(python_files)} Python files')
    fixed_count = 0
    checked_count = 0
    for file_path in python_files:
        if needs_future_annotations(file_path):
            if add_future_annotations(file_path):
                fixed_count += 1
                logger.info(f'✓ Fixed: {file_path}')
        checked_count += 1
        if checked_count % 100 == 0:
            logger.info(f'  Processed {checked_count}/{len(python_files)} files...')
    logger.info('\n' + '=' * 60)
    logger.info(f'Results:')
    logger.info(f'  Files checked: {len(python_files)}')
    logger.info(f'  Files fixed: {fixed_count}')
    logger.info(f'  Files already correct: {len(python_files) - fixed_count}')
    if fixed_count > 0:
        logger.info(f'\n✓ Successfully added future annotations to {fixed_count} files')
        logger.info('  This enables postponed evaluation of type annotations (PEP 563)')
    else:
        logger.info('\n✓ No files needed future annotations import')
if __name__ == '__main__':
    main()