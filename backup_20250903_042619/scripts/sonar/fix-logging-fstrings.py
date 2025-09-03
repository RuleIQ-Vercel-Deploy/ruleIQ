#!/usr/bin/env python3
"""
Fix G004: Logging f-string violations
Converts f-strings in logging calls to % formatting with lazy evaluation
"""

import ast
import sys
from pathlib import Path
from typing import List, Optional, Tuple
import re

class LoggingFStringTransformer(ast.NodeTransformer):
    """Transform f-strings in logging calls to % formatting."""
    
    def __init__(self):
        self.modified = False
        self.logging_methods = {
            'debug', 'info', 'warning', 'warn', 'error', 
            'critical', 'exception', 'log'
        }
    
    def visit_Call(self, node: ast.Call) -> ast.Call:
        """Transform logging calls with f-strings."""
        self.generic_visit(node)
        
        # Check if this is a logging call
        if self._is_logging_call(node):
            # Process the arguments
            new_args = []
            for arg in node.args:
                if isinstance(arg, ast.JoinedStr):  # This is an f-string
                    new_arg = self._convert_fstring_to_percent(arg)
                    if new_arg:
                        new_args.append(new_arg)
                        self.modified = True
                    else:
                        new_args.append(arg)
                else:
                    new_args.append(arg)
            
            node.args = new_args
        
        return node
    
    def _is_logging_call(self, node: ast.Call) -> bool:
        """Check if this is a logging method call."""
        # Direct logging calls: logging.info(...)
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id == 'logging' and node.func.attr in self.logging_methods:
                    return True
                # Also check for logger instances
                if node.func.value.id in ('logger', 'log', '_logger', '_log', 'self.logger', 'self.log'):
                    return node.func.attr in self.logging_methods
            # Check for self.logger.info(...) patterns
            elif isinstance(node.func.value, ast.Attribute):
                if (hasattr(node.func.value, 'attr') and 
                    node.func.value.attr in ('logger', 'log', '_logger', '_log') and
                    node.func.attr in self.logging_methods):
                    return True
        
        return False
    
    def _convert_fstring_to_percent(self, fstring_node: ast.JoinedStr) -> Optional[ast.Call]:
        """Convert an f-string to % formatting."""
        format_str_parts = []
        format_args = []
        
        for value in fstring_node.values:
            if isinstance(value, ast.Constant):
                # This is a literal string part
                format_str_parts.append(value.value)
            elif isinstance(value, ast.FormattedValue):
                # This is a formatted value
                format_spec = self._get_format_spec(value)
                if format_spec:
                    format_str_parts.append(f'%{format_spec}')
                else:
                    # Default to string formatting
                    format_str_parts.append('%s')
                format_args.append(value.value)
        
        if not format_args:
            # No formatting needed, just return a constant
            return ast.Constant(value=''.join(format_str_parts))
        
        # Create the % formatting expression
        format_str = ''.join(format_str_parts)
        
        if len(format_args) == 1:
            # Single argument: "format" % arg
            return ast.BinOp(
                left=ast.Constant(value=format_str),
                op=ast.Mod(),
                right=format_args[0]
            )
        else:
            # Multiple arguments: "format" % (arg1, arg2, ...)
            return ast.BinOp(
                left=ast.Constant(value=format_str),
                op=ast.Mod(),
                right=ast.Tuple(elts=format_args, ctx=ast.Load())
            )
    
    def _get_format_spec(self, formatted_value: ast.FormattedValue) -> Optional[str]:
        """Extract format specification from a FormattedValue."""
        # Check the type of the value to determine appropriate format
        if isinstance(formatted_value.value, ast.Constant):
            if isinstance(formatted_value.value.value, (int, float)):
                return 'd' if isinstance(formatted_value.value.value, int) else 'f'
        elif isinstance(formatted_value.value, ast.Name):
            # We'll default to string for variables
            return 's'
        elif isinstance(formatted_value.value, ast.Call):
            # Function calls typically return strings
            return 's'
        
        return 's'  # Default to string


def fix_file(file_path: Path) -> bool:
    """Fix G004 violations in a single file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Skip if no logging imports
        if 'logging' not in content and 'logger' not in content:
            return False
        
        # Parse the file
        try:
            tree = ast.parse(content)
        except SyntaxError:
            print(f"Syntax error in {file_path}, skipping")
            return False
        
        # Transform the AST
        transformer = LoggingFStringTransformer()
        new_tree = transformer.visit(tree)
        
        if not transformer.modified:
            return False
        
        # Convert back to source code
        import astor
        new_content = astor.to_source(new_tree)
        
        # Write back
        file_path.write_text(new_content, encoding='utf-8')
        return True
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main function to fix G004 violations."""
    root_path = Path('/home/omar/Documents/ruleIQ')
    
    # Find all Python files
    python_files = []
    for pattern in ['api/**/*.py', 'services/**/*.py', 'utils/**/*.py', 
                    'core/**/*.py', 'database/**/*.py', 'tests/**/*.py',
                    'config/**/*.py', 'scripts/**/*.py']:
        python_files.extend(root_path.glob(pattern))
    
    print(f"Found {len(python_files)} Python files to check")
    
    # First install astor if needed
    import subprocess
    try:
        import astor
    except ImportError:
        print("Installing astor for AST to source conversion...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'astor'], check=True)
        import astor
    
    fixed_count = 0
    for file_path in python_files:
        if fix_file(file_path):
            fixed_count += 1
            print(f"Fixed: {file_path}")
    
    print(f"\n✅ Fixed G004 violations in {fixed_count} files")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())