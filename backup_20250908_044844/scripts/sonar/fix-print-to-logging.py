"""
Fix T201: Replace print() statements with proper logging.
Converts print() calls to appropriate logging levels.
"""
import ast
import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional, Any

class PrintToLoggingTransformer(ast.NodeTransformer):
    """Transform print() calls to logging calls."""

    def __init__(self):
        self.has_logging_import = False
        self.needs_logging_import = False
        self.logger_name = None

    def visit_Import(self, node) -> Any:
        """Check for existing logging imports."""
        for alias in node.names:
            if alias.name == 'logging':
                self.has_logging_import = True
        return node

    def visit_ImportFrom(self, node) -> Any:
        """Check for existing logging imports."""
        if node.module == 'logging':
            self.has_logging_import = True
        elif node.module and 'logging' in node.module:
            self.has_logging_import = True
        return node

    def visit_Assign(self, node) -> Any:
        """Check for existing logger definitions."""
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Attribute):
                if isinstance(node.value.func.value, ast.Name) and node.value.func.value.id == 'logging' and (node.value.func.attr == 'getLogger'):
                    if isinstance(node.targets[0], ast.Name):
                        self.logger_name = node.targets[0].id
        return node

    def visit_Call(self, node) -> Any:
        """Transform print() calls to logging."""
        if isinstance(node.func, ast.Name) and node.func.id == 'print':
            self.needs_logging_import = True
            level = 'info'
            if node.args:
                first_arg_str = ast.unparse(node.args[0]) if hasattr(ast, 'unparse') else ''
                if any((keyword in first_arg_str.lower() for keyword in ['error', 'fail', 'exception'])):
                    level = 'error'
                elif any((keyword in first_arg_str.lower() for keyword in ['warn', 'warning', 'caution'])):
                    level = 'warning'
                elif any((keyword in first_arg_str.lower() for keyword in ['debug', 'trace', 'verbose'])):
                    level = 'debug'
            if self.logger_name:
                func = ast.Attribute(value=ast.Name(id=self.logger_name, ctx=ast.Load()), attr=level, ctx=ast.Load())
            else:
                func = ast.Attribute(value=ast.Name(id='logging', ctx=ast.Load()), attr=level, ctx=ast.Load())
            new_args = []
            if node.args:
                if len(node.args) > 1:
                    format_str = ' '.join(['%s'] * len(node.args))
                    new_args = [ast.Constant(value=format_str)] + node.args
                else:
                    new_args = node.args
            new_keywords = []
            for keyword in node.keywords:
                if keyword.arg not in ['file', 'end', 'sep', 'flush']:
                    new_keywords.append(keyword)
            return ast.Call(func=func, args=new_args, keywords=new_keywords)
        self.generic_visit(node)
        return node

def fix_print_statements(file_path: Path) -> bool:
    """Replace print() statements with logging in a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'print(' not in content:
            return False
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return False
        transformer = PrintToLoggingTransformer()
        new_tree = transformer.visit(tree)
        if not transformer.needs_logging_import:
            return False
        if not transformer.has_logging_import:
            import_node = ast.Import(names=[ast.alias(name='logging', asname=None)])
            insert_idx = 0
            for i, node in enumerate(tree.body):
                if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant):
                    insert_idx = i + 1
                elif isinstance(node, ast.ImportFrom) and node.module == '__future__':
                    insert_idx = i + 1
                else:
                    break
            tree.body.insert(insert_idx, import_node)
            if not transformer.logger_name:
                logger_node = ast.Assign(targets=[ast.Name(id='logger', ctx=ast.Store())], value=ast.Call(func=ast.Attribute(value=ast.Name(id='logging', ctx=ast.Load()), attr='getLogger', ctx=ast.Load()), args=[ast.Name(id='__name__', ctx=ast.Load())], keywords=[]))
                tree.body.insert(insert_idx + 1, logger_node)
        if hasattr(ast, 'unparse'):
            new_content = ast.unparse(tree)
        else:
            new_content = regex_replace_prints(content)
            if new_content == content:
                return False
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except (OSError, ValueError, KeyError) as e:
        try:
            return regex_fix_prints(file_path)
        except OSError:
            return False

def regex_replace_prints(content: str) -> str:
    """Regex-based print replacement as fallback."""
    lines = content.split('\n')
    new_lines = []
    has_logging_import = 'import logging' in content or 'from logging' in content
    added_import = False
    for line in lines:
        if 'logging.' in line or 'logger.' in line:
            new_lines.append(line)
            continue
        if not has_logging_import and (not added_import):
            if line.strip().startswith('from __future__ import'):
                new_lines.append(line)
                new_lines.append('import logging')
                new_lines.append('logger = logging.getLogger(__name__)')
                added_import = True
                continue
            elif not line.strip() and len(new_lines) > 0:
                new_lines.append('import logging')
                new_lines.append('logger = logging.getLogger(__name__)')
                new_lines.append('')
                added_import = True
        if 'print(' in line:
            line = re.sub('\\bprint\\s*\\((.*?)\\)', 'logger.info(\\1)', line)
        new_lines.append(line)
    return '\n'.join(new_lines)

def regex_fix_prints(file_path: Path) -> bool:
    """Regex-based fix as complete fallback."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'print(' not in content:
            return False
        new_content = regex_replace_prints(content)
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        return False
    except (OSError, ValueError):
        return False

def main() -> None:
    """Main function to replace print statements with logging."""
    print('Replacing print() statements with logging...')
    print('=' * 60)
    python_files = []
    exclude_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'build', 'dist', '.pytest_cache', '.mypy_cache', '.ruff_cache'}
    exclude_files = {'fix-print-to-logging.py', 'test_', 'conftest.py'}
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith('.py'):
                if any((exc in file for exc in exclude_files)):
                    continue
                file_path = Path(root) / file
                python_files.append(file_path)
    print(f'Found {len(python_files)} Python files')
    fixed_count = 0
    checked_count = 0
    for file_path in python_files:
        if fix_print_statements(file_path):
            fixed_count += 1
            print(f'✓ Fixed: {file_path}')
        checked_count += 1
        if checked_count % 100 == 0:
            print(f'  Processed {checked_count}/{len(python_files)} files...')
    print('\n' + '=' * 60)
    print(f'Results:')
    print(f'  Files checked: {len(python_files)}')
    print(f'  Files fixed: {fixed_count}')
    print(f'  Files already correct: {len(python_files) - fixed_count}')
    if fixed_count > 0:
        print(f'\n✓ Successfully replaced print() with logging in {fixed_count} files')
        print('  This improves production readiness and debugging capabilities')
    else:
        print('\n✓ No print() statements found that need replacement')
if __name__ == '__main__':
    main()