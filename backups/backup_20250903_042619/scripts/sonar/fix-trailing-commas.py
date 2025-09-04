#!/usr/bin/env python3
"""
Fix COM812: Missing trailing comma violations
Adds trailing commas to multi-line structures (lists, dicts, tuples, function calls)
"""

import ast
import sys
from pathlib import Path
from typing import List, Optional, Set, Tuple
import re

def fix_trailing_commas_in_file(file_path: Path) -> bool:
    """Fix trailing comma violations in a single file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content
        lines = content.splitlines(keepends=True)
        
        # Track modifications
        modified = False
        
        # Pattern to find multi-line structures
        # We'll use a simpler approach: look for lines ending with ) ] or } 
        # where the previous line doesn't have a trailing comma
        
        for i in range(1, len(lines)):
            line = lines[i].rstrip()
            prev_line = lines[i-1].rstrip()
            
            # Skip empty lines
            if not line or not prev_line:
                continue
            
            # Check if current line closes a structure
            if any(line.strip() == char for char in [']', ')', '}', '],', '),', '},']):
                # Check if previous line should have a trailing comma
                # Skip if it's a comment, already has comma, or is an opening bracket
                if (prev_line and 
                    not prev_line.endswith(',') and 
                    not prev_line.endswith((':', '(', '[', '{', '\\')) and
                    not prev_line.strip().startswith('#') and
                    not any(prev_line.strip() == char for char in ['(', '[', '{'])):
                    
                    # Check if it's a value that should have a comma
                    # Look for typical patterns that need trailing commas
                    if ('"' in prev_line or "'" in prev_line or 
                        prev_line.strip().endswith(')') or
                        prev_line.strip().endswith(']') or
                        prev_line.strip().endswith('}') or
                        any(char.isalnum() for char in prev_line.strip())):
                        
                        # Add trailing comma
                        lines[i-1] = prev_line + ',\n'
                        modified = True
        
        if modified:
            new_content = ''.join(lines)
            file_path.write_text(new_content, encoding='utf-8')
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def fix_with_ast_approach(file_path: Path) -> bool:
    """Alternative approach using AST for more accurate fixes."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        # Use regex to find and fix common patterns
        patterns_fixed = False
        
        # Pattern 1: Multi-line function calls without trailing comma
        pattern1 = re.compile(
            r'(\n\s+[^,\n]+)(\n\s*\))',  # Item followed by closing paren
            re.MULTILINE
        )
        
        # Pattern 2: Multi-line lists without trailing comma
        pattern2 = re.compile(
            r'(\n\s+[^,\n]+)(\n\s*\])',  # Item followed by closing bracket
            re.MULTILINE
        )
        
        # Pattern 3: Multi-line dicts without trailing comma
        pattern3 = re.compile(
            r'(\n\s+[^,\n]+)(\n\s*\})',  # Item followed by closing brace
            re.MULTILINE
        )
        
        # Apply fixes
        new_content = content
        for pattern in [pattern1, pattern2, pattern3]:
            matches = pattern.findall(new_content)
            if matches:
                # Replace with comma added
                new_content = pattern.sub(r'\1,\2', new_content)
                patterns_fixed = True
        
        if patterns_fixed and new_content != content:
            # Verify syntax is still valid
            try:
                compile(new_content, str(file_path), 'exec')
                file_path.write_text(new_content, encoding='utf-8')
                return True
            except SyntaxError:
                # If syntax error, don't apply changes
                return False
        
        return False
        
    except Exception as e:
        print(f"Error with AST approach for {file_path}: {e}")
        return False


def main():
    """Main function to fix COM812 violations."""
    root_path = Path('/home/omar/Documents/ruleIQ')
    
    # Find all Python files
    python_files = []
    for pattern in ['api/**/*.py', 'services/**/*.py', 'utils/**/*.py', 
                    'core/**/*.py', 'database/**/*.py', 'tests/**/*.py',
                    'config/**/*.py', 'scripts/**/*.py', '*.py']:
        python_files.extend(root_path.glob(pattern))
    
    # Filter out already processed fix scripts
    python_files = [f for f in python_files if not f.name.startswith('fix-')]
    
    print(f"Found {len(python_files)} Python files to check")
    
    fixed_count = 0
    for file_path in python_files:
        # Try the simple approach first
        if fix_trailing_commas_in_file(file_path):
            fixed_count += 1
            print(f"Fixed: {file_path}")
        # If simple approach didn't work, try AST approach
        elif fix_with_ast_approach(file_path):
            fixed_count += 1
            print(f"Fixed (AST): {file_path}")
    
    print(f"\n✅ Fixed COM812 violations in {fixed_count} files")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())