"""
Fix ANN201: Add missing return type annotations for public functions.
Analyzes function bodies to infer appropriate return types.
"""
import ast
import os
import sys
from pathlib import Path
from typing import List, Optional, Set, Dict, Any, Union


class ReturnTypeFinder(ast.NodeVisitor):
    """Find return statements in a function to infer return type."""

    def __init__(self):
        self.returns: List[ast.Return] = []
        self.yields: List[ast.Yield] = []
        self.yield_froms: List[ast.YieldFrom] = []

    def visit_Return(self, node) -> None:
        self.returns.append(node)
        """Visit Return"""

    def visit_Yield(self, node) -> None:
        self.yields.append(node)
        """Visit Yield"""

    def visit_YieldFrom(self, node) -> None:
        self.yield_froms.append(node)
        """Visit Yieldfrom"""

    def visit_FunctionDef(self, node) -> None:
        pass
        """Visit Functiondef"""

    def visit_AsyncFunctionDef(self, node) -> None:
        pass
        """Visit Asyncfunctiondef"""


def _should_skip_function(func_node: ast.FunctionDef) -> bool:
    """Check if function should be skipped for annotation."""
    if func_node.returns:
        return True
    if func_node.name.startswith('_') and not func_node.name.startswith('__'):
        return True
    if func_node.name == '__init__':
        return True
    return False


def _get_magic_method_return_type(name: str) -> Optional[str]:
    """Get return type for Python magic methods."""
    magic_returns = {
        '__str__': 'str',
        '__repr__': 'str',
        '__len__': 'int',
        '__bool__': 'bool',
        '__enter__': 'Self',
        '__exit__': 'None',
    }
    return magic_returns.get(name)


def _infer_generator_type(func_node: ast.FunctionDef, finder: ReturnTypeFinder) -> Optional[str]:
    """Infer generator return type."""
    if not (finder.yields or finder.yield_froms):
        return None
    
    if isinstance(func_node, ast.AsyncFunctionDef):
        return 'AsyncGenerator[Any, None]'
    return 'Generator[Any, None, None]'


def _infer_constant_type(value: Any) -> str:
    """Infer type from constant value."""
    if value is None:
        return 'None'
    elif isinstance(value, bool):
        return 'bool'
    elif isinstance(value, int):
        return 'int'
    elif isinstance(value, float):
        return 'float'
    elif isinstance(value, str):
        return 'str'
    return 'Any'


def _infer_name_type(name: str) -> str:
    """Infer type from variable name."""
    if name in ('True', 'False'):
        return 'bool'
    elif name == 'None':
        return 'None'
    
    name_lower = name.lower()
    if 'result' in name_lower or 'response' in name_lower:
        return 'Dict[str, Any]'
    elif 'count' in name_lower or 'size' in name_lower:
        return 'int'
    elif 'flag' in name_lower or name_lower.startswith('is_'):
        return 'bool'
    return 'Any'


def _infer_container_type(node: ast.AST) -> str:
    """Infer type for container literals."""
    if isinstance(node, ast.Dict):
        return 'Dict[str, Any]'
    elif isinstance(node, ast.List):
        return 'List[Any]'
    elif isinstance(node, ast.Tuple):
        return 'Tuple[Any, ...]'
    return 'Any'


def _infer_call_type(func_name: str) -> str:
    """Infer type from function call."""
    type_constructors = {
        'dict': 'Dict[str, Any]',
        'Dict': 'Dict[str, Any]',
        'list': 'List[Any]',
        'List': 'List[Any]',
        'tuple': 'Tuple[Any, ...]',
        'Tuple': 'Tuple[Any, ...]',
        'set': 'Set[Any]',
        'Set': 'Set[Any]',
        'str': 'str',
        'int': 'int',
        'float': 'float',
        'bool': 'bool',
    }
    return type_constructors.get(func_name, 'Any')


def _infer_return_value_type(ret_value: Optional[ast.AST]) -> str:
    """Infer type from a single return value."""
    if ret_value is None:
        return 'None'
    
    if isinstance(ret_value, ast.Constant):
        return _infer_constant_type(ret_value.value)
    
    if isinstance(ret_value, ast.Name):
        return _infer_name_type(ret_value.id)
    
    if isinstance(ret_value, (ast.Dict, ast.List, ast.Tuple)):
        return _infer_container_type(ret_value)
    
    if isinstance(ret_value, ast.Call):
        if isinstance(ret_value.func, ast.Name):
            return _infer_call_type(ret_value.func.id)
    
    return 'Any'


def _combine_return_types(return_types: Set[str]) -> str:
    """Combine multiple return types into a single type hint."""
    if not return_types:
        return 'None'
    
    if len(return_types) == 1:
        return list(return_types)[0]
    
    if 'None' in return_types:
        other_types = return_types - {'None'}
        if len(other_types) == 1:
            other_type = list(other_types)[0]
            return f'Optional[{other_type}]'
        return 'Optional[Any]'
    
    if len(return_types) == 2 and 'Any' not in return_types:
        types_list = sorted(list(return_types))
        return f"Union[{', '.join(types_list)}]"
    
    return 'Any'


def infer_return_type(func_node: ast.FunctionDef) -> Optional[str]:
    """Infer return type from function body."""
    if _should_skip_function(func_node):
        return None
    
    # Check for magic methods
    magic_type = _get_magic_method_return_type(func_node.name)
    if magic_type:
        return magic_type
    
    # Analyze function body
    finder = ReturnTypeFinder()
    for node in func_node.body:
        finder.visit(node)
    
    # Check for generators
    generator_type = _infer_generator_type(func_node, finder)
    if generator_type:
        return generator_type
    
    # No returns means None
    if not finder.returns:
        return 'None'
    
    # Collect all return types
    return_types = set()
    for ret in finder.returns:
        return_type = _infer_return_value_type(ret.value)
        return_types.add(return_type)
    
    # Combine return types
    return _combine_return_types(return_types)


class ReturnAnnotationAdder(ast.NodeTransformer):
    """Add return type annotations to functions."""

    def __init__(self):
        self.added_annotations = 0
        self.needs_imports = set()

    def _extract_required_imports(self, return_type: str) -> None:
        """Extract typing imports needed for return type."""
        import_keywords = [
            'Optional', 'Union', 'Dict', 'List', 'Tuple', 
            'Set', 'Generator', 'AsyncGenerator', 'Any'
        ]
        for keyword in import_keywords:
            if keyword in return_type:
                self.needs_imports.add(keyword)

    def visit_FunctionDef(self, node) -> Any:
        self.generic_visit(node)
        """Visit Functiondef"""
        
        if node.returns or (node.name.startswith('_') and not node.name.startswith('__')):
            return node
        
        return_type = infer_return_type(node)
        if return_type:
            self._extract_required_imports(return_type)
            node.returns = ast.Name(id=return_type, ctx=ast.Load())
            self.added_annotations += 1
        
        return node

    def visit_AsyncFunctionDef(self, node) -> Any:
        return self.visit_FunctionDef(node)
        """Visit Asyncfunctiondef"""


def _get_existing_typing_imports(tree: ast.AST) -> Set[str]:
    """Get existing typing imports from AST."""
    typing_imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == 'typing':
            for alias in node.names:
                typing_imports.add(alias.name)
    return typing_imports


def _find_import_position(tree: ast.AST) -> int:
    """Find the position to insert typing imports."""
    insert_idx = 0
    for i, node in enumerate(tree.body):
        if isinstance(node, ast.ImportFrom) and node.module == '__future__':
            insert_idx = i + 1
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            if not (isinstance(node, ast.ImportFrom) and node.module == '__future__'):
                insert_idx = i
                break
    return insert_idx


def _update_typing_imports(tree: ast.AST, transformer: ReturnAnnotationAdder) -> None:
    """Update typing imports in the AST."""
    existing_imports = _get_existing_typing_imports(tree)
    missing_imports = transformer.needs_imports - existing_imports
    
    if not missing_imports:
        return
    
    # Find existing typing import
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == 'typing':
            for imp in missing_imports:
                node.names.append(ast.alias(name=imp, asname=None))
            return
    
    # Add new typing import
    insert_idx = _find_import_position(tree)
    import_node = ast.ImportFrom(
        module='typing',
        names=[ast.alias(name=imp, asname=None) for imp in sorted(missing_imports)],
        level=0
    )
    tree.body.insert(insert_idx, import_node)


def add_return_annotations(file_path: Path) -> bool:
    """Add return type annotations to a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        transformer = ReturnAnnotationAdder()
        new_tree = transformer.visit(tree)
        
        if transformer.added_annotations == 0:
            return False
        
        _update_typing_imports(tree, transformer)
        
        if hasattr(ast, 'unparse'):
            new_content = ast.unparse(tree)
        else:
            return False
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        return True
    except (SyntaxError, Exception):
        return False


def _get_python_files() -> List[Path]:
    """Get all Python files to process."""
    python_files = []
    exclude_dirs = {
        '.git', '__pycache__', 'node_modules', '.venv', 'venv', 
        'build', 'dist', '.pytest_cache', '.mypy_cache', '.ruff_cache', 
        'tests', 'test'
    }
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith('.py') and 'test' not in file.lower():
                python_files.append(Path(root) / file)
    
    return python_files


def _print_progress(checked: int, total: int) -> None:
    """Print progress indicator."""
    if checked % 100 == 0:
        print(f'  Processed {checked}/{total} files...')


def _print_summary(total_files: int, fixed_count: int) -> None:
    """Print summary of changes."""
    print('\n' + '=' * 60)
    print(f'Results:')
    print(f'  Files checked: {total_files}')
    print(f'  Files with annotations added: {fixed_count}')
    print(f'  Files already annotated: {total_files - fixed_count}')
    
    if fixed_count > 0:
        print(f'\n✓ Successfully added return type annotations to {fixed_count} files')
        print('  This improves type safety and IDE support')
    else:
        print('\n✓ No functions needed return type annotations')


def main() -> None:
    """Main function to add return type annotations."""
    print('Adding return type annotations to public functions...')
    print('=' * 60)
    
    python_files = _get_python_files()
    print(f'Found {len(python_files)} Python files')
    
    fixed_count = 0
    for i, file_path in enumerate(python_files, 1):
        if add_return_annotations(file_path):
            fixed_count += 1
            print(f'✓ Fixed: {file_path}')
        _print_progress(i, len(python_files))
    
    _print_summary(len(python_files), fixed_count)


if __name__ == '__main__':
    main()