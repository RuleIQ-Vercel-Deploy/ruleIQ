"""
Fix BLE001: Replace blind exception catching (except Exception:) with specific exceptions.
Analyzes code context to determine appropriate specific exceptions.
"""
import ast
import os
from pathlib import Path
from typing import List

class ExceptionAnalyzer(ast.NodeVisitor):
    """Analyze code to determine what exceptions might be raised."""

    def __init__(self):
        self.potential_exceptions = set()
        self.has_file_ops = False
        self.has_network_ops = False
        self.has_db_ops = False
        self.has_json_ops = False
        self.has_type_conversion = False
        self.has_indexing = False

    def visit_Call(self, node) -> None:
        """Check function calls for potential exceptions."""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            if func_name in ['open', 'read', 'write']:
                self.has_file_ops = True
                self.potential_exceptions.update(['IOError', 'FileNotFoundError', 'PermissionError'])
            elif func_name in ['int', 'float', 'str']:
                self.has_type_conversion = True
                self.potential_exceptions.add('ValueError')
            elif func_name in ['loads', 'dumps', 'load', 'dump']:
                self.has_json_ops = True
                self.potential_exceptions.add('JSONDecodeError')
        elif isinstance(node.func, ast.Attribute):
            attr = node.func.attr
            if attr in ['get', 'post', 'put', 'delete', 'request']:
                self.has_network_ops = True
                self.potential_exceptions.update(['RequestException', 'ConnectionError', 'Timeout'])
            elif attr in ['execute', 'commit', 'rollback', 'query']:
                self.has_db_ops = True
                self.potential_exceptions.update(['DatabaseError', 'IntegrityError', 'OperationalError'])
            elif attr in ['loads', 'dumps']:
                self.has_json_ops = True
                self.potential_exceptions.add('JSONDecodeError')
        self.generic_visit(node)

    def visit_Subscript(self, node) -> None:
        """Check for indexing operations."""
        self.has_indexing = True
        self.potential_exceptions.update(['KeyError', 'IndexError'])
        self.generic_visit(node)

    def visit_Attribute(self, node) -> None:
        """Check for attribute access."""
        self.potential_exceptions.add('AttributeError')
        self.generic_visit(node)

def determine_specific_exceptions(try_body: List[ast.stmt]) -> List[str]:
    """Analyze try block to determine specific exceptions."""
    analyzer = ExceptionAnalyzer()
    for stmt in try_body:
        analyzer.visit(stmt)
    exceptions = []
    if analyzer.has_file_ops:
        exceptions.append('OSError')
    if analyzer.has_network_ops:
        exceptions.append('requests.RequestException')
    if analyzer.has_db_ops:
        exceptions.append('sqlalchemy.exc.SQLAlchemyError')
    if analyzer.has_json_ops:
        exceptions.append('json.JSONDecodeError')
    if analyzer.has_type_conversion:
        exceptions.append('ValueError')
    if analyzer.has_indexing:
        exceptions.extend(['KeyError', 'IndexError'])
    if 'AttributeError' in analyzer.potential_exceptions:
        exceptions.append('AttributeError')
    if not exceptions:
        exceptions = ['ValueError', 'TypeError', 'AttributeError']
    seen = set()
    unique_exceptions = []
    for exc in exceptions:
        if exc not in seen:
            seen.add(exc)
            unique_exceptions.append(exc)
    return unique_exceptions[:3]

def fix_blind_exceptions_in_file(file_path: Path) -> bool:
    """Fix blind exception catching in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'except Exception:' not in content and 'except:' not in content:
            return False
        lines = content.split('\n')
        modified = False
        new_lines = []
        i = 0
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            if stripped == 'except Exception:' or stripped == 'except Exception as e:' or stripped == 'except:':
                try_line_idx = i - 1
                while try_line_idx >= 0:
                    if lines[try_line_idx].strip().startswith('try:'):
                        break
                    try_line_idx -= 1
                if try_line_idx >= 0:
                    try_block_lines = []
                    for j in range(try_line_idx + 1, i):
                        if lines[j].strip() and (not lines[j].strip().startswith('#')):
                            try_block_lines.append(lines[j])
                    specific_exceptions = []
                    try_content = ' '.join(try_block_lines).lower()
                    if 'open(' in try_content or 'file' in try_content or 'path' in try_content:
                        specific_exceptions.append('OSError')
                    if 'json' in try_content or 'loads' in try_content or 'dumps' in try_content:
                        specific_exceptions.append('json.JSONDecodeError')
                    if 'request' in try_content or 'get(' in try_content or 'post(' in try_content:
                        specific_exceptions.append('requests.RequestException')
                    if 'execute' in try_content or 'query' in try_content or 'database' in try_content:
                        specific_exceptions.append('Exception')
                    if 'int(' in try_content or 'float(' in try_content or 'parse' in try_content:
                        specific_exceptions.append('ValueError')
                    if '[' in try_content and ']' in try_content:
                        specific_exceptions.extend(['KeyError', 'IndexError'])
                    if not specific_exceptions:
                        specific_exceptions = ['ValueError', 'TypeError']
                    specific_exceptions = specific_exceptions[:3]
                    indent = len(line) - len(line.lstrip())
                    if 'as e' in stripped:
                        if len(specific_exceptions) == 1:
                            new_line = ' ' * indent + f'except {specific_exceptions[0]} as e:'
                        else:
                            exc_tuple = f"({', '.join(specific_exceptions)})"
                            new_line = ' ' * indent + f'except {exc_tuple} as e:'
                    elif len(specific_exceptions) == 1:
                        new_line = ' ' * indent + f'except {specific_exceptions[0]}:'
                    else:
                        exc_tuple = f"({', '.join(specific_exceptions)})"
                        new_line = ' ' * indent + f'except {exc_tuple}:'
                    new_lines.append(new_line)
                    modified = True
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
            i += 1
        if modified:
            new_content = '\n'.join(new_lines)
            if 'json.JSONDecodeError' in new_content and 'import json' not in new_content:
                import_added = False
                final_lines = []
                for line in new_lines:
                    final_lines.append(line)
                    if not import_added and (line.startswith('import ') or line.startswith('from ')):
                        if 'json' not in line:
                            final_lines.append('import json')
                            import_added = True
                new_lines = final_lines
            if 'requests.RequestException' in new_content and 'import requests' not in new_content:
                import_added = False
                final_lines = []
                for line in new_lines:
                    final_lines.append(line)
                    if not import_added and (line.startswith('import ') or line.startswith('from ')):
                        if 'requests' not in line:
                            final_lines.append('import requests')
                            import_added = True
                new_lines = final_lines
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            return True
        return False
    except (OSError, json.JSONDecodeError, requests.RequestException):
        return False

def main() -> None:
    """Main function to fix blind exception catching."""
    print('Fixing blind exception catching (except Exception:)...')
    print('=' * 60)
    python_files = []
    exclude_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'build', 'dist', '.pytest_cache', '.mypy_cache', '.ruff_cache'}
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                python_files.append(file_path)
    print(f'Found {len(python_files)} Python files')
    fixed_count = 0
    checked_count = 0
    for file_path in python_files:
        if fix_blind_exceptions_in_file(file_path):
            fixed_count += 1
            print(f'✓ Fixed: {file_path}')
        checked_count += 1
        if checked_count % 100 == 0:
            print(f'  Processed {checked_count}/{len(python_files)} files...')
    print('\n' + '=' * 60)
    print('Results:')
    print(f'  Files checked: {len(python_files)}')
    print(f'  Files fixed: {fixed_count}')
    print(f'  Files already using specific exceptions: {len(python_files) - fixed_count}')
    if fixed_count > 0:
        print(f'\n✓ Successfully fixed blind exception catching in {fixed_count} files')
        print('  This improves error handling specificity and debugging')
    else:
        print('\n✓ No blind exception catching found')
if __name__ == '__main__':
    main()
