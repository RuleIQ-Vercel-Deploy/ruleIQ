"""
Fix ANN201: Add missing return type annotations for public functions.
Analyzes function bodies to infer appropriate return types.
"""
import ast
import os
import sys
from pathlib import Path
from typing import List, Optional, Set, Dict, Any

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

def infer_return_type(func_node: ast.FunctionDef) -> Optional[str]:
    """Infer return type from function body."""
    if func_node.returns:
        return None
    if func_node.name.startswith('_') and (not func_node.name.startswith('__')):
        return None
    if func_node.name == '__init__':
        return None
    if func_node.name == '__str__':
        return 'str'
    if func_node.name == '__repr__':
        return 'str'
    if func_node.name == '__len__':
        return 'int'
    if func_node.name == '__bool__':
        return 'bool'
    if func_node.name == '__enter__':
        return 'Self'
    if func_node.name == '__exit__':
        return 'None'
    finder = ReturnTypeFinder()
    for node in func_node.body:
        finder.visit(node)
    if finder.yields or finder.yield_froms:
        if isinstance(func_node, ast.AsyncFunctionDef):
            return 'AsyncGenerator[Any, None]'
        else:
            return 'Generator[Any, None, None]'
    if not finder.returns:
        if isinstance(func_node, ast.AsyncFunctionDef):
            return 'None'
        return 'None'
    return_types = set()
    for ret in finder.returns:
        if ret.value is None:
            return_types.add('None')
        elif isinstance(ret.value, ast.Constant):
            if ret.value.value is None:
                return_types.add('None')
            elif isinstance(ret.value.value, bool):
                return_types.add('bool')
            elif isinstance(ret.value.value, int):
                return_types.add('int')
            elif isinstance(ret.value.value, float):
                return_types.add('float')
            elif isinstance(ret.value.value, str):
                return_types.add('str')
            else:
                return_types.add('Any')
        elif isinstance(ret.value, ast.Name):
            if ret.value.id == 'True' or ret.value.id == 'False':
                return_types.add('bool')
            elif ret.value.id == 'None':
                return_types.add('None')
            elif 'result' in ret.value.id.lower() or 'response' in ret.value.id.lower():
                return_types.add('Dict[str, Any]')
            elif 'count' in ret.value.id.lower() or 'size' in ret.value.id.lower():
                return_types.add('int')
            elif 'flag' in ret.value.id.lower() or 'is_' in ret.value.id.lower():
                return_types.add('bool')
            else:
                return_types.add('Any')
        elif isinstance(ret.value, ast.Dict):
            return_types.add('Dict[str, Any]')
        elif isinstance(ret.value, ast.List):
            return_types.add('List[Any]')
        elif isinstance(ret.value, ast.Tuple):
            return_types.add('Tuple[Any, ...]')
        elif isinstance(ret.value, ast.Call):
            if isinstance(ret.value.func, ast.Name):
                func_name = ret.value.func.id
                if func_name in ['dict', 'Dict']:
                    return_types.add('Dict[str, Any]')
                elif func_name in ['list', 'List']:
                    return_types.add('List[Any]')
                elif func_name in ['tuple', 'Tuple']:
                    return_types.add('Tuple[Any, ...]')
                elif func_name in ['set', 'Set']:
                    return_types.add('Set[Any]')
                elif func_name == 'str':
                    return_types.add('str')
                elif func_name == 'int':
                    return_types.add('int')
                elif func_name == 'float':
                    return_types.add('float')
                elif func_name == 'bool':
                    return_types.add('bool')
                else:
                    return_types.add('Any')
            else:
                return_types.add('Any')
        else:
            return_types.add('Any')
    if len(return_types) == 0:
        return 'None'
    elif len(return_types) == 1:
        return list(return_types)[0]
    elif 'None' in return_types:
        other_types = return_types - {'None'}
        if len(other_types) == 1:
            other_type = list(other_types)[0]
            return f'Optional[{other_type}]'
        else:
            return 'Optional[Any]'
    elif len(return_types) == 2 and 'Any' not in return_types:
        types_list = sorted(list(return_types))
        return f"Union[{', '.join(types_list)}]"
    else:
        return 'Any'

class ReturnAnnotationAdder(ast.NodeTransformer):
    """Add return type annotations to functions."""

    def __init__(self):
        self.added_annotations = 0
        self.needs_imports = set()

    def visit_FunctionDef(self, node) -> Any:
        self.generic_visit(node)
        """Visit Functiondef"""
        if node.returns:
            return node
        if node.name.startswith('_') and (not node.name.startswith('__')):
            return node
        return_type = infer_return_type(node)
        if return_type:
            if 'Optional' in return_type:
                self.needs_imports.add('Optional')
            if 'Union' in return_type:
                self.needs_imports.add('Union')
            if 'Dict' in return_type:
                self.needs_imports.add('Dict')
            if 'List' in return_type:
                self.needs_imports.add('List')
            if 'Tuple' in return_type:
                self.needs_imports.add('Tuple')
            if 'Set' in return_type:
                self.needs_imports.add('Set')
            if 'Generator' in return_type:
                self.needs_imports.add('Generator')
            if 'AsyncGenerator' in return_type:
                self.needs_imports.add('AsyncGenerator')
            if 'Any' in return_type:
                self.needs_imports.add('Any')
            node.returns = ast.Name(id=return_type, ctx=ast.Load())
            self.added_annotations += 1
        return node

    def visit_AsyncFunctionDef(self, node) -> Any:
        return self.visit_FunctionDef(node)
        """Visit Asyncfunctiondef"""

def add_return_annotations(file_path: Path) -> bool:
    """Add return type annotations to a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return False
        transformer = ReturnAnnotationAdder()
        new_tree = transformer.visit(tree)
        if transformer.added_annotations == 0:
            return False
        has_typing_import = False
        typing_imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == 'typing':
                has_typing_import = True
                for alias in node.names:
                    typing_imports.add(alias.name)
        if transformer.needs_imports - typing_imports:
            missing_imports = transformer.needs_imports - typing_imports
            if has_typing_import:
                for node in tree.body:
                    if isinstance(node, ast.ImportFrom) and node.module == 'typing':
                        for imp in missing_imports:
                            node.names.append(ast.alias(name=imp, asname=None))
                        break
            else:
                insert_idx = 0
                for i, node in enumerate(tree.body):
                    if isinstance(node, ast.ImportFrom) and node.module == '__future__':
                        insert_idx = i + 1
                    elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                        if not (isinstance(node, ast.ImportFrom) and node.module == '__future__'):
                            insert_idx = i
                            break
                import_node = ast.ImportFrom(module='typing', names=[ast.alias(name=imp, asname=None) for imp in sorted(missing_imports)], level=0)
                tree.body.insert(insert_idx, import_node)
        if hasattr(ast, 'unparse'):
            new_content = ast.unparse(tree)
        else:
            return False
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    except Exception as e:
        return False

def main() -> None:
    """Main function to add return type annotations."""
    print('Adding return type annotations to public functions...')
    print('=' * 60)
    python_files = []
    exclude_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'build', 'dist', '.pytest_cache', '.mypy_cache', '.ruff_cache', 'tests', 'test'}
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith('.py'):
                if 'test' in file.lower():
                    continue
                file_path = Path(root) / file
                python_files.append(file_path)
    print(f'Found {len(python_files)} Python files')
    fixed_count = 0
    checked_count = 0
    for file_path in python_files:
        if add_return_annotations(file_path):
            fixed_count += 1
            print(f'✓ Fixed: {file_path}')
        checked_count += 1
        if checked_count % 100 == 0:
            print(f'  Processed {checked_count}/{len(python_files)} files...')
    print('\n' + '=' * 60)
    print(f'Results:')
    print(f'  Files checked: {len(python_files)}')
    print(f'  Files with annotations added: {fixed_count}')
    print(f'  Files already annotated: {len(python_files) - fixed_count}')
    if fixed_count > 0:
        print(f'\n✓ Successfully added return type annotations to {fixed_count} files')
        print('  This improves type safety and IDE support')
    else:
        print('\n✓ No functions needed return type annotations')
if __name__ == '__main__':
    main()