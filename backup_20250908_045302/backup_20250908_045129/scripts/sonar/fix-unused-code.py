"""Remove unused imports and variables."""
import logging
logger = logging.getLogger(__name__)
from __future__ import annotations
import os
import re
import ast
from typing import List

def get_unused_imports(filepath: str) -> List[str]:
    """Find unused imports in a Python file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        tree = ast.parse(content)
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.asname or alias.name)
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    imports.add(alias.asname or alias.name)
        used_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)
        unused = []
        for imp in imports:
            base_name = imp.split('.')[0]
            if base_name not in used_names and imp not in used_names:
                if imp not in ['typing', '__future__', 'annotations']:
                    unused.append(imp)
        return unused
    except (OSError, ValueError, KeyError):
        return []

def remove_unused_imports(filepath: str) -> bool:
    """Remove unused imports from a Python file."""
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
        unused = get_unused_imports(filepath)
        if not unused:
            return False
        new_lines = []
        modified = False
        for line in lines:
            skip_line = False
            for imp in unused:
                if f'import {imp}' in line or f'from {imp}' in line:
                    skip_line = True
                    modified = True
                    break
                if re.search(f'\\bimport\\s+.*\\b{imp}\\b', line):
                    line = re.sub(f',?\\s*{imp}\\s*,?', '', line)
                    line = re.sub(',\\s*,', ',', line)
                    line = re.sub(',\\s*\\)', ')', line)
                    line = re.sub('\\(\\s*,', '(', line)
                    modified = True
            if not skip_line:
                new_lines.append(line)
        if modified:
            with open(filepath, 'w') as f:
                f.writelines(new_lines)
            return True
        return False
    except (OSError, KeyError, IndexError) as e:
        logger.info(f'Error processing {filepath}: {e}')
        return False

def remove_unused_variables(filepath: str) -> bool:
    """Remove or comment out unused variables."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        tree = ast.parse(content)
        assignments = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if hasattr(node, 'lineno'):
                            assignments[target.id] = node.lineno
        used_vars = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and (not isinstance(node.ctx, ast.Store)):
                used_vars.add(node.id)
        unused_vars = []
        for var, line_no in assignments.items():
            if var not in used_vars and (not var.startswith('_')):
                if var not in ['app', 'logger', 'db', 'config']:
                    unused_vars.append((var, line_no))
        if not unused_vars:
            return False
        lines = content.split('\n')
        for var, line_no in unused_vars:
            if line_no - 1 < len(lines):
                line = lines[line_no - 1]
                if f'{var} =' in line and (not line.strip().startswith('#')):
                    lines[line_no - 1] = f'# {line}  # Unused variable'
        with open(filepath, 'w') as f:
            f.write('\n'.join(lines))
        return len(unused_vars) > 0
    except (OSError, ValueError, KeyError):
        return False

def main() -> None:
    """Main function to remove unused code."""
    import_files_fixed = 0
    var_files_fixed = 0
    priority_files = ['./api/routers/auth.py', './api/routers/assessments.py', './api/routers/compliance.py', './api/routers/ai_assessments.py', './api/routers/chat.py', './services/auth_service.py', './services/ai/ai_service.py', './database.py']
    for filepath in priority_files:
        if os.path.exists(filepath):
            if remove_unused_imports(filepath):
                logger.info(f'✓ Removed unused imports from {filepath}')
                import_files_fixed += 1
            if remove_unused_variables(filepath):
                logger.info(f'✓ Removed unused variables from {filepath}')
                var_files_fixed += 1
    count = 0
    for root, dirs, files in os.walk('.'):
        if 'venv' in root or 'node_modules' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py') and count < 30:
                filepath = os.path.join(root, file)
                if filepath not in priority_files:
                    if remove_unused_imports(filepath):
                        logger.info(f'✓ Removed unused imports from {filepath}')
                        import_files_fixed += 1
                        count += 1
                    if remove_unused_variables(filepath):
                        logger.info(f'✓ Removed unused variables from {filepath}')
                        var_files_fixed += 1
    logger.info(f'\n✅ Fixed unused imports in {import_files_fixed} files')
    logger.info(f'✅ Fixed unused variables in {var_files_fixed} files')
if __name__ == '__main__':
    logger.info('Removing unused imports and variables...')
    main()