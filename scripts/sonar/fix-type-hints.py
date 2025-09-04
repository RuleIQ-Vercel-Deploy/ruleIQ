"""Add basic type hints to Python functions."""
import logging
import os
import re
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)
from __future__ import annotations


# Type mapping dictionaries
ID_TYPES = ['id', 'user_id', 'item_id', 'order_id', 'session_id', 'company_id']
COUNT_TYPES = ['count', 'size', 'length', 'index', 'limit', 'offset', 'page']
AMOUNT_TYPES = ['amount', 'price', 'total', 'score', 'rate', 'percentage']
BOOL_TYPES = ['is_active', 'is_valid', 'enabled', 'disabled', 'success', 'error']
DICT_TYPES = ['data', 'config', 'settings', 'params', 'options', 'metadata']
LIST_TYPES = ['items', 'users', 'results', 'errors', 'messages']
TEXT_TYPES = ['name', 'title', 'description', 'message', 'text', 'content']
STRING_TYPES = ['email', 'url', 'path', 'filename', 'token', 'key']


def _get_type_from_list(param_lower: str, type_list: List[str], return_type: str) -> Optional[str]:
    """Check if param matches any in the list and return the type."""
    if param_lower in type_list:
        return return_type
    return None


def _infer_special_param_type(param_lower: str) -> Optional[str]:
    """Infer type for special parameters."""
    if param_lower == 'db' or 'session' in param_lower:
        return 'Any'
    elif param_lower == 'request':
        return 'Any'
    elif param_lower == 'response':
        return 'Any'
    return None


def infer_type_from_name(param_name: str) -> str:
    """Infer type hint from parameter name patterns."""
    param_lower = param_name.lower()
    
    # Check type lists
    type_checks = [
        (ID_TYPES, 'str'),
        (COUNT_TYPES, 'int'),
        (AMOUNT_TYPES, 'float'),
        (BOOL_TYPES, 'bool'),
        (DICT_TYPES, 'Dict[str, Any]'),
        (LIST_TYPES, 'List[Any]'),
        (TEXT_TYPES, 'str'),
        (STRING_TYPES, 'str'),
    ]
    
    for type_list, return_type in type_checks:
        if result := _get_type_from_list(param_lower, type_list, return_type):
            return result
    
    # Check special params
    if special_type := _infer_special_param_type(param_lower):
        return special_type
    
    return 'Any'


def _parse_function_signature(line: str) -> Optional[Tuple[str, str, str]]:
    """Parse a function definition line."""
    match = re.match(r'^(\s*)def\s+(\w+)\s*\(([^)]*)\)\s*:', line)
    if not match:
        return None
    return match.group(1), match.group(2), match.group(3)


def _should_skip_function(func_name: str, params: str, line: str) -> bool:
    """Check if function should be skipped for type hints."""
    return '->' in line or ':' in params


def _process_parameter(param: str) -> str:
    """Process a single parameter and add type hint."""
    param = param.strip()
    
    # Handle special params
    if param.startswith('*'):
        return param
    
    # Handle default values
    if '=' in param:
        return _process_param_with_default(param)
    
    # Handle regular params
    return _process_regular_param(param)


def _process_param_with_default(param: str) -> str:
    """Process parameter with default value."""
    param_name, default = param.split('=', 1)
    param_name = param_name.strip()
    default = default.strip()
    
    if param_name in ['self', 'cls']:
        return param
    
    type_hint = infer_type_from_name(param_name)
    if default == 'None':
        type_hint = f'Optional[{type_hint}]'
    
    return f'{param_name}: {type_hint} = {default}'


def _process_regular_param(param: str) -> str:
    """Process regular parameter without default."""
    param_name = param.strip()
    
    if param_name in ['self', 'cls']:
        return param_name
    
    type_hint = infer_type_from_name(param_name)
    return f'{param_name}: {type_hint}'


def _infer_return_type(func_name: str) -> str:
    """Infer return type from function name."""
    if func_name == '__init__':
        return 'None'
    
    # Check prefixes
    prefix_checks = [
        ('is_', 'bool'),
        ('has_', 'bool'),
        ('can_', 'bool'),
        ('count_', 'int'),
        ('calculate_', 'float'),
        ('delete_', 'bool'),
    ]
    
    for prefix, return_type in prefix_checks:
        if func_name.startswith(prefix):
            return return_type
    
    # Check complex prefixes
    if func_name.startswith('get_'):
        if 'list' in func_name.lower():
            return 'List[Any]'
        elif 'dict' in func_name.lower():
            return 'Dict[str, Any]'
    
    if func_name.startswith(('create_', 'update_')):
        return 'Any'
    
    if func_name == 'len' or 'score' in func_name:
        return 'float' if 'score' in func_name else 'int'
    
    return 'Any'


def _build_function_line(indent: str, func_name: str, params: List[str]) -> str:
    """Build the complete function definition line."""
    return_type = _infer_return_type(func_name)
    
    if params:
        params_str = ', '.join(params)
        return f"{indent}def {func_name}({params_str}) -> {return_type}:"
    else:
        return_type = 'None' if func_name == '__init__' else 'Any'
        return f'{indent}def {func_name}() -> {return_type}:'


def _process_function_line(line: str) -> Tuple[str, bool]:
    """Process a single function definition line."""
    parsed = _parse_function_signature(line)
    if not parsed:
        return line, False
    
    indent, func_name, params = parsed
    
    if _should_skip_function(func_name, params, line):
        return line, False
    
    if not params.strip():
        new_line = _build_function_line(indent, func_name, [])
        return new_line, True
    
    # Process parameters
    param_list = [p.strip() for p in params.split(',')]
    new_params = [_process_parameter(p) for p in param_list]
    
    new_line = _build_function_line(indent, func_name, new_params)
    return new_line, True


def _should_add_imports(content: str) -> bool:
    """Check if typing imports should be added."""
    return 'from typing import' not in content


def _process_file_lines(lines: List[str]) -> Tuple[List[str], bool]:
    """Process all lines in a file."""
    new_lines = []
    modified = False
    imports_added = False
    
    for line in lines:
        # Add imports if needed
        if not imports_added and (line.startswith('import ') or line.startswith('from ')):
            if _should_add_imports('\n'.join(lines)):
                imports_added = True
                modified = True
        
        # Process function definitions
        if line.strip().startswith('def '):
            new_line, was_modified = _process_function_line(line)
            new_lines.append(new_line)
            if was_modified:
                modified = True
        else:
            new_lines.append(line)
    
    return new_lines, modified


def add_type_hints_to_file(filepath: str) -> bool:
    """Add type hints to a Python file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Skip if already has type hints
        if '-> ' in content and ': ' in content:
            return False
        
        lines = content.split('\n')
        new_lines, modified = _process_file_lines(lines)
        
        if not modified:
            return False
        
        # Write back
        with open(filepath, 'w') as f:
            f.write('\n'.join(new_lines))
        
        return True
    except Exception as e:
        logger.info(f'Error processing {filepath}: {e}')
        return False


def _get_priority_files() -> List[str]:
    """Get priority files for type hint addition."""
    return [
        './api/routers/auth.py',
        './api/routers/assessments.py',
        './api/routers/compliance.py',
        './api/routers/ai_assessments.py',
        './api/routers/chat.py',
        './services/auth_service.py',
        './services/ai/ai_service.py',
        './database.py',
        './utils/validators.py'
    ]


def _should_skip_directory(root: str) -> bool:
    """Check if directory should be skipped."""
    skip_dirs = ['venv', 'node_modules', '__pycache__']
    return any(skip_dir in root for skip_dir in skip_dirs)


def _process_priority_files(priority_files: List[str]) -> int:
    """Process priority files first."""
    files_fixed = 0
    for filepath in priority_files:
        if os.path.exists(filepath):
            if add_type_hints_to_file(filepath):
                logger.info(f'✓ Added type hints to {filepath}')
                files_fixed += 1
    return files_fixed


def _process_remaining_files(priority_files: List[str], max_files: int = 50) -> int:
    """Process remaining Python files."""
    files_fixed = 0
    
    for root, dirs, files in os.walk('.'):
        if _should_skip_directory(root):
            continue
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                
                # Skip if already processed or limit reached
                if filepath in priority_files or files_fixed >= max_files:
                    continue
                
                if add_type_hints_to_file(filepath):
                    logger.info(f'✓ Added type hints to {filepath}')
                    files_fixed += 1
    
    return files_fixed


def main() -> None:
    """Main function to add type hints."""
    priority_files = _get_priority_files()
    
    # Process priority files
    fixed_count = _process_priority_files(priority_files)
    
    # Process remaining files
    fixed_count += _process_remaining_files(priority_files)
    
    logger.info(f'\n✅ Added type hints to {fixed_count} files')


if __name__ == '__main__':
    logger.info('Adding type hints to Python files...')
    main()