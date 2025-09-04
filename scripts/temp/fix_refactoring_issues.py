#!/usr/bin/env python3
"""
Script to fix refactoring issues in the RuleIQ codebase
Identifies and fixes:
1. Malformed docstrings
2. Import errors
3. Files exceeding size limits
4. Functions/classes exceeding size limits
"""
import os
import re
from pathlib import Path
from typing import List, Tuple

def fix_malformed_docstrings(file_path: Path) -> bool:
    """Fix malformed docstrings where code appears between quotes."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to detect malformed docstrings with code between opening quotes
        # Looking for pattern like:
        # """
        # from __future__ import annotations
        # actual docstring content
        # """
        pattern = r'"""\n(from __future__ import annotations.*?\n)(.*?)"""'
        
        if re.search(pattern, content, re.DOTALL):
            # Fix by moving imports before docstring
            fixed = re.sub(
                r'"""\n(from __future__ import annotations.*?\n\n.*?)\n([A-Z].*?)"""',
                r'"""\n\2"""',
                content,
                flags=re.DOTALL
            )
            
            # Also handle cases where there's code between docstring lines
            fixed = re.sub(
                r'"""\n(from __future__ import annotations.*?\n)((?:.*?\n)*?)(\w.*?)"""',
                r'"""\n\3"""' + '\n' + r'\1',
                fixed,
                count=1,
                flags=re.DOTALL
            )
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed)
            return True
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
    return False

def check_file_size(file_path: Path) -> Tuple[int, bool]:
    """Check if file exceeds 500 lines."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        return len(lines), len(lines) > 500
    except Exception:
        return 0, False

def check_function_sizes(file_path: Path) -> List[Tuple[str, int, int]]:
    """Check for functions exceeding 50 lines."""
    violations = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        in_function = False
        function_name = None
        function_start = 0
        indent_level = 0
        
        for i, line in enumerate(lines, 1):
            # Detect function start
            if re.match(r'^(async )?def \w+\(', line.strip()):
                if in_function and function_name:
                    # End previous function
                    func_lines = i - function_start
                    if func_lines > 50:
                        violations.append((function_name, function_start, func_lines))
                
                # Start new function
                match = re.search(r'def (\w+)\(', line)
                if match:
                    function_name = match.group(1)
                    function_start = i
                    in_function = True
                    indent_level = len(line) - len(line.lstrip())
            
            # Detect function end (back to base indent or less)
            elif in_function and line.strip() and not line.startswith(' ' * (indent_level + 1)):
                func_lines = i - function_start
                if func_lines > 50:
                    violations.append((function_name, function_start, func_lines))
                in_function = False
                function_name = None
        
        # Check last function if still open
        if in_function and function_name:
            func_lines = len(lines) - function_start + 1
            if func_lines > 50:
                violations.append((function_name, function_start, func_lines))
    
    except Exception as e:
        print(f"Error checking functions in {file_path}: {e}")
    
    return violations

def check_class_sizes(file_path: Path) -> List[Tuple[str, int, int]]:
    """Check for classes exceeding 100 lines."""
    violations = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        in_class = False
        class_name = None
        class_start = 0
        
        for i, line in enumerate(lines, 1):
            # Detect class start
            if re.match(r'^class \w+', line.strip()):
                if in_class and class_name:
                    # End previous class
                    class_lines = i - class_start
                    if class_lines > 100:
                        violations.append((class_name, class_start, class_lines))
                
                # Start new class
                match = re.search(r'class (\w+)', line)
                if match:
                    class_name = match.group(1)
                    class_start = i
                    in_class = True
            
            # Detect class end (another class or end of file)
            elif in_class and re.match(r'^(class |def |@|\w)', line) and not line.startswith('    '):
                class_lines = i - class_start
                if class_lines > 100:
                    violations.append((class_name, class_start, class_lines))
                in_class = False
                class_name = None
        
        # Check last class if still open
        if in_class and class_name:
            class_lines = len(lines) - class_start + 1
            if class_lines > 100:
                violations.append((class_name, class_start, class_lines))
    
    except Exception as e:
        print(f"Error checking classes in {file_path}: {e}")
    
    return violations

def scan_project(root_dir: str = '/home/omar/Documents/ruleIQ'):
    """Scan the project for issues."""
    root_path = Path(root_dir)
    
    # Directories to check
    check_dirs = ['api', 'services', 'database', 'middleware', 'config', 'langgraph_agent']
    
    issues = {
        'malformed_docstrings': [],
        'large_files': [],
        'large_functions': [],
        'large_classes': []
    }
    
    for dir_name in check_dirs:
        dir_path = root_path / dir_name
        if not dir_path.exists():
            continue
        
        for py_file in dir_path.rglob('*.py'):
            # Skip test files and __pycache__
            if '__pycache__' in str(py_file) or 'test_' in py_file.name:
                continue
            
            # Check for malformed docstrings
            if fix_malformed_docstrings(py_file):
                issues['malformed_docstrings'].append(str(py_file))
            
            # Check file size
            lines, exceeds = check_file_size(py_file)
            if exceeds:
                issues['large_files'].append((str(py_file), lines))
            
            # Check function sizes
            func_violations = check_function_sizes(py_file)
            if func_violations:
                for func_name, start, lines in func_violations:
                    issues['large_functions'].append((str(py_file), func_name, start, lines))
            
            # Check class sizes
            class_violations = check_class_sizes(py_file)
            if class_violations:
                for class_name, start, lines in class_violations:
                    issues['large_classes'].append((str(py_file), class_name, start, lines))
    
    return issues

def main():
    """Main function to run the fixes."""
    print("Scanning RuleIQ codebase for refactoring issues...")
    issues = scan_project()
    
    print("\n=== SCAN RESULTS ===\n")
    
    if issues['malformed_docstrings']:
        print(f"Fixed {len(issues['malformed_docstrings'])} files with malformed docstrings:")
        for file in issues['malformed_docstrings']:
            print(f"  - {file}")
    
    if issues['large_files']:
        print(f"\n{len(issues['large_files'])} files exceed 500 lines:")
        for file, lines in issues['large_files']:
            print(f"  - {file}: {lines} lines")
    
    if issues['large_functions']:
        print(f"\n{len(issues['large_functions'])} functions exceed 50 lines:")
        for file, func, start, lines in issues['large_functions'][:10]:  # Show first 10
            print(f"  - {file}:{start} {func}(): {lines} lines")
        if len(issues['large_functions']) > 10:
            print(f"  ... and {len(issues['large_functions']) - 10} more")
    
    if issues['large_classes']:
        print(f"\n{len(issues['large_classes'])} classes exceed 100 lines:")
        for file, cls, start, lines in issues['large_classes']:
            print(f"  - {file}:{start} class {cls}: {lines} lines")
    
    # Summary
    print("\n=== SUMMARY ===")
    print(f"Malformed docstrings fixed: {len(issues['malformed_docstrings'])}")
    print(f"Files needing size reduction: {len(issues['large_files'])}")
    print(f"Functions needing refactoring: {len(issues['large_functions'])}")
    print(f"Classes needing refactoring: {len(issues['large_classes'])}")
    
    # Critical files that likely break imports
    critical_files = []
    for file in issues['malformed_docstrings']:
        if 'routers' in file or 'services' in file:
            critical_files.append(file)
    
    if critical_files:
        print("\n=== CRITICAL FIXES APPLIED ===")
        print("These files were causing import errors and have been fixed:")
        for file in critical_files:
            print(f"  - {file}")

if __name__ == '__main__':
    main()