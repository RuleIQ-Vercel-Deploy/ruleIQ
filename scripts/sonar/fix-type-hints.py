"""Add basic type hints to Python functions."""
import logging
logger = logging.getLogger(__name__)
from __future__ import annotations
import os
import re

def infer_type_from_name(param_name: str) -> str:
    """Infer type hint from parameter name patterns."""
    param_lower = param_name.lower()
    if param_lower in ['id', 'user_id', 'item_id', 'order_id', 'session_id', 'company_id']:
        return 'str'
    elif param_lower in ['count', 'size', 'length', 'index', 'limit', 'offset', 'page']:
        return 'int'
    elif param_lower in ['amount', 'price', 'total', 'score', 'rate', 'percentage']:
        return 'float'
    elif param_lower in ['is_active', 'is_valid', 'enabled', 'disabled', 'success', 'error']:
        return 'bool'
    elif param_lower in ['data', 'config', 'settings', 'params', 'options', 'metadata']:
        return 'Dict[str, Any]'
    elif param_lower in ['items', 'users', 'results', 'errors', 'messages']:
        return 'List[Any]'
    elif param_lower in ['name', 'title', 'description', 'message', 'text', 'content']:
        return 'str'
    elif param_lower in ['email', 'url', 'path', 'filename', 'token', 'key']:
        return 'str'
    elif param_lower == 'db' or 'session' in param_lower:
        return 'Any'
    elif param_lower == 'request':
        return 'Any'
    elif param_lower == 'response':
        return 'Any'
    else:
        return 'Any'

def add_type_hints_to_file(filepath: str) -> bool:
    """Add type hints to a Python file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        if '-> ' in content and ': ' in content:
            return False
        lines = content.split('\n')
        new_lines = []
        modified = False
        imports_added = False
        for i, line in enumerate(lines):
            if not imports_added and (line.startswith('import ') or line.startswith('from ')):
                if 'from typing import' not in content:
                    imports_added = True
                    modified = True
            if line.strip().startswith('def '):
                match = re.match('^(\\s*)def\\s+(\\w+)\\s*\\(([^)]*)\\)\\s*:', line)
                if match:
                    indent = match.group(1)
                    func_name = match.group(2)
                    params = match.group(3)
                    if '->' in line or ':' in params:
                        new_lines.append(line)
                        continue
                    if params.strip():
                        param_list = [p.strip() for p in params.split(',')]
                        new_params = []
                        for param in param_list:
                            if param.startswith('*'):
                                new_params.append(param)
                            elif '=' in param:
                                param_name, default = param.split('=', 1)
                                param_name = param_name.strip()
                                default = default.strip()
                                if param_name in ['self', 'cls']:
                                    new_params.append(param)
                                else:
                                    type_hint = infer_type_from_name(param_name)
                                    if default == 'None':
                                        type_hint = f'Optional[{type_hint}]'
                                    new_params.append(f'{param_name}: {type_hint} = {default}')
                                    modified = True
                            else:
                                param_name = param.strip()
                                if param_name in ['self', 'cls']:
                                    new_params.append(param_name)
                                else:
                                    type_hint = infer_type_from_name(param_name)
                                    new_params.append(f'{param_name}: {type_hint}')
                                    modified = True
                        return_type = 'Any'
                        if func_name.startswith('is_') or func_name.startswith('has_') or func_name.startswith('can_'):
                            return_type = 'bool'
                        elif func_name.startswith('get_') and 'list' in func_name.lower():
                            return_type = 'List[Any]'
                        elif func_name.startswith('get_') and 'dict' in func_name.lower():
                            return_type = 'Dict[str, Any]'
                        elif func_name.startswith('count_') or func_name == 'len':
                            return_type = 'int'
                        elif func_name.startswith('calculate_') or 'score' in func_name:
                            return_type = 'float'
                        elif func_name.startswith('create_') or func_name.startswith('update_'):
                            return_type = 'Any'
                        elif func_name.startswith('delete_'):
                            return_type = 'bool'
                        elif func_name == '__init__':
                            return_type = 'None'
                        new_line = f"{indent}def {func_name}({', '.join(new_params)}) -> {return_type}:"
                        new_lines.append(new_line)
                    else:
                        return_type = 'None' if func_name == '__init__' else 'Any'
                        new_line = f'{indent}def {func_name}() -> {return_type}:'
                        new_lines.append(new_line)
                        modified = True
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        if modified:
            with open(filepath, 'w') as f:
                f.write('\n'.join(new_lines))
            return True
        return False
    except Exception as e:
        logger.info(f'Error processing {filepath}: {e}')
        return False

def main() -> None:
    """Main function to add type hints."""
    files_fixed = 0
    priority_files = ['./api/routers/auth.py', './api/routers/assessments.py', './api/routers/compliance.py', './api/routers/ai_assessments.py', './api/routers/chat.py', './services/auth_service.py', './services/ai/ai_service.py', './database.py', './utils/validators.py']
    for filepath in priority_files:
        if os.path.exists(filepath):
            if add_type_hints_to_file(filepath):
                logger.info(f'✓ Added type hints to {filepath}')
                files_fixed += 1
    for root, dirs, files in os.walk('.'):
        if 'venv' in root or 'node_modules' in root or '__pycache__' in root:
            continue
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if filepath not in priority_files and files_fixed < 50:
                    if add_type_hints_to_file(filepath):
                        logger.info(f'✓ Added type hints to {filepath}')
                        files_fixed += 1
    logger.info(f'\n✅ Added type hints to {files_fixed} files')
if __name__ == '__main__':
    logger.info('Adding type hints to Python files...')
    main()
