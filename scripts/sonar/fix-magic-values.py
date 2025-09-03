#!/usr/bin/env python3
"""
Fix PLR2004: Magic value used in comparison
Replace magic values with named constants
"""

import ast
import sys
from pathlib import Path
from typing import Set, List, Dict, Any
import re

class MagicValueReplacer(ast.NodeTransformer):
    """Replace magic values with named constants."""
    
    def __init__(self):
        self.magic_values = {}
        self.constants_needed = set()
        self.modified = False
        
        # Common magic value mappings
        self.common_constants = {
            200: 'HTTP_OK',
            201: 'HTTP_CREATED',
            204: 'HTTP_NO_CONTENT',
            400: 'HTTP_BAD_REQUEST',
            401: 'HTTP_UNAUTHORIZED',
            403: 'HTTP_FORBIDDEN',
            404: 'HTTP_NOT_FOUND',
            409: 'HTTP_CONFLICT',
            422: 'HTTP_UNPROCESSABLE_ENTITY',
            500: 'HTTP_INTERNAL_SERVER_ERROR',
            502: 'HTTP_BAD_GATEWAY',
            503: 'HTTP_SERVICE_UNAVAILABLE',
            
            # Common limits
            100: 'DEFAULT_LIMIT',
            1000: 'MAX_ITEMS',
            10000: 'MAX_RECORDS',
            1024: 'KB_SIZE',
            1048576: 'MB_SIZE',
            
            # Common timeouts
            30: 'DEFAULT_TIMEOUT',
            60: 'MINUTE_SECONDS',
            300: 'FIVE_MINUTES_SECONDS',
            3600: 'HOUR_SECONDS',
            86400: 'DAY_SECONDS',
            
            # Common retry values
            3: 'MAX_RETRIES',
            5: 'DEFAULT_RETRIES',
            
            # Percentages
            0.95: 'HIGH_CONFIDENCE_THRESHOLD',
            0.8: 'CONFIDENCE_THRESHOLD',
            0.5: 'HALF_RATIO',
        }
    
    def visit_Compare(self, node):
        """Visit comparison nodes to find magic values."""
        self.generic_visit(node)
        
        # Check for magic values in comparisons
        for comparator in node.comparators:
            if isinstance(comparator, ast.Constant):
                value = comparator.value
                if isinstance(value, (int, float)) and value != 0 and value != 1:
                    if value in self.common_constants:
                        # Replace with constant
                        const_name = self.common_constants[value]
                        self.constants_needed.add((const_name, value))
                        new_node = ast.Name(id=const_name, ctx=ast.Load())
                        self.modified = True
                        return node.__class__(
                            left=node.left,
                            ops=node.ops,
                            comparators=[new_node if c is comparator else c for c in node.comparators]
                        )
        
        return node
    
    def visit_Call(self, node):
        """Check function calls for magic values."""
        self.generic_visit(node)
        
        # Special handling for status codes in HTTPException
        if isinstance(node.func, ast.Name) and node.func.id == 'HTTPException':
            for keyword in node.keywords:
                if keyword.arg == 'status_code' and isinstance(keyword.value, ast.Constant):
                    value = keyword.value.value
                    if value in self.common_constants:
                        const_name = self.common_constants[value]
                        self.constants_needed.add((const_name, value))
                        keyword.value = ast.Name(id=const_name, ctx=ast.Load())
                        self.modified = True
        
        # Check for range() calls with magic values
        if isinstance(node.func, ast.Name) and node.func.id == 'range':
            new_args = []
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, int):
                    value = arg.value
                    if value > 10 and value in self.common_constants:
                        const_name = self.common_constants[value]
                        self.constants_needed.add((const_name, value))
                        new_args.append(ast.Name(id=const_name, ctx=ast.Load()))
                        self.modified = True
                    else:
                        new_args.append(arg)
                else:
                    new_args.append(arg)
            if self.modified:
                node.args = new_args
        
        return node

def add_constants_to_file(file_path: Path, constants: Set[tuple]) -> bool:
    """Add constant definitions to the top of the file."""
    if not constants:
        return False
    
    content = file_path.read_text(encoding='utf-8')
    lines = content.splitlines(keepends=True)
    
    # Find where to insert constants
    insert_line = 0
    has_future_import = False
    has_imports = False
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('from __future__'):
            has_future_import = True
            insert_line = i + 1
        elif stripped.startswith('import ') or stripped.startswith('from '):
            has_imports = True
            insert_line = i + 1
        elif stripped and not stripped.startswith('#') and not stripped.startswith('"""'):
            if not has_imports and not has_future_import:
                insert_line = i
            break
    
    # Add blank line if needed
    if insert_line > 0 and lines[insert_line - 1].strip():
        lines.insert(insert_line, '\n')
        insert_line += 1
    
    # Add constants section
    lines.insert(insert_line, '# Constants\n')
    insert_line += 1
    
    # Sort constants by name
    sorted_constants = sorted(constants, key=lambda x: x[0])
    
    # Group by type
    http_constants = [(name, val) for name, val in sorted_constants if name.startswith('HTTP_')]
    time_constants = [(name, val) for name, val in sorted_constants if 'SECONDS' in name or 'TIMEOUT' in name]
    size_constants = [(name, val) for name, val in sorted_constants if 'SIZE' in name or 'KB' in name or 'MB' in name]
    other_constants = [(name, val) for name, val in sorted_constants 
                       if not any([name.startswith('HTTP_'), 'SECONDS' in name, 'TIMEOUT' in name, 
                                  'SIZE' in name, 'KB' in name, 'MB' in name])]
    
    # Add HTTP constants
    if http_constants:
        for name, value in http_constants:
            lines.insert(insert_line, f'{name} = {value}\n')
            insert_line += 1
    
    # Add time constants
    if time_constants:
        if http_constants:
            lines.insert(insert_line, '\n')
            insert_line += 1
        for name, value in time_constants:
            lines.insert(insert_line, f'{name} = {value}\n')
            insert_line += 1
    
    # Add size constants
    if size_constants:
        if http_constants or time_constants:
            lines.insert(insert_line, '\n')
            insert_line += 1
        for name, value in size_constants:
            lines.insert(insert_line, f'{name} = {value}\n')
            insert_line += 1
    
    # Add other constants
    if other_constants:
        if http_constants or time_constants or size_constants:
            lines.insert(insert_line, '\n')
            insert_line += 1
        for name, value in other_constants:
            lines.insert(insert_line, f'{name} = {value}\n')
            insert_line += 1
    
    # Add blank line after constants
    lines.insert(insert_line, '\n')
    
    # Write back
    new_content = ''.join(lines)
    file_path.write_text(new_content, encoding='utf-8')
    return True

def fix_file(file_path: Path) -> bool:
    """Fix magic values in a single file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Parse the file
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return False
        
        # Find and replace magic values
        replacer = MagicValueReplacer()
        new_tree = replacer.visit(tree)
        
        if not replacer.modified:
            return False
        
        # Convert back to source code
        import astor
        new_content = astor.to_source(new_tree)
        
        # Write the modified content
        file_path.write_text(new_content, encoding='utf-8')
        
        # Add constant definitions
        if replacer.constants_needed:
            add_constants_to_file(file_path, replacer.constants_needed)
        
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main function to fix magic values."""
    root_path = Path('/home/omar/Documents/ruleIQ')
    
    # Find all Python files
    python_files = []
    for pattern in ['api/**/*.py', 'services/**/*.py', 'utils/**/*.py', 
                    'core/**/*.py', 'database/**/*.py', 'tests/**/*.py',
                    'config/**/*.py', 'scripts/**/*.py']:
        python_files.extend(root_path.glob(pattern))
    
    print(f"Found {len(python_files)} Python files to check")
    
    # Check if astor is installed
    try:
        import astor
    except ImportError:
        print("astor already installed")
        import astor
    
    fixed_count = 0
    for file_path in python_files:
        if fix_file(file_path):
            fixed_count += 1
            print(f"Fixed: {file_path}")
    
    print(f"\n✅ Fixed magic values in {fixed_count} files")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())