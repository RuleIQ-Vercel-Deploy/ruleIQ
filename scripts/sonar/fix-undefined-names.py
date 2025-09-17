#!/usr/bin/env python3
"""
Fix F821: Undefined name violations
Adds missing imports and fixes undefined variable references
"""

import ast
import sys
from pathlib import Path

class UndefinedNameFixer(ast.NodeVisitor):
    """Find and fix undefined names in Python code."""

    def __init__(self):
        self.undefined_names = set()
        self.defined_names = set()
        self.imports_needed = {}

        # Common import mappings
        self.import_map = {
            # Type hints
            'Optional': 'from typing import Optional',
            'List': 'from typing import List',
            'Dict': 'from typing import Dict',
            'Set': 'from typing import Set',
            'Tuple': 'from typing import Tuple',
            'Union': 'from typing import Union',
            'Any': 'from typing import Any',
            'Type': 'from typing import Type',
            'Callable': 'from typing import Callable',
            'Literal': 'from typing import Literal',
            'TypeVar': 'from typing import TypeVar',
            'Generic': 'from typing import Generic',
            'Protocol': 'from typing import Protocol',
            'ClassVar': 'from typing import ClassVar',
            'Final': 'from typing import Final',
            'cast': 'from typing import cast',
            'overload': 'from typing import overload',

            # Common libraries
            'datetime': 'from datetime import datetime',
            'date': 'from datetime import date',
            'timedelta': 'from datetime import timedelta',
            'timezone': 'from datetime import timezone',
            'json': 'import json',
            'os': 'import os',
            'sys': 'import sys',
            're': 'import re',
            'Path': 'from pathlib import Path',
            'logging': 'import logging',
            'logger': 'import logging\nlogger = logging.getLogger(__name__)',
            'asyncio': 'import asyncio',
            'aiohttp': 'import aiohttp',
            'requests': 'import requests',
            'numpy': 'import numpy as np',
            'np': 'import numpy as np',
            'pandas': 'import pandas as pd',
            'pd': 'import pandas as pd',

            # FastAPI/Pydantic
            'BaseModel': 'from pydantic import BaseModel',
            'Field': 'from pydantic import Field',
            'validator': 'from pydantic import validator',
            'ValidationError': 'from pydantic import ValidationError',
            'HTTPException': 'from fastapi import HTTPException',
            'Depends': 'from fastapi import Depends',
            'APIRouter': 'from fastapi import APIRouter',
            'FastAPI': 'from fastapi import FastAPI',
            'Request': 'from fastapi import Request',
            'Response': 'from fastapi import Response',
            'status': 'from fastapi import status',
            'BackgroundTasks': 'from fastapi import BackgroundTasks',

            # SQLAlchemy
            'Column': 'from sqlalchemy import Column',
            'String': 'from sqlalchemy import String',
            'Integer': 'from sqlalchemy import Integer',
            'Boolean': 'from sqlalchemy import Boolean',
            'DateTime': 'from sqlalchemy import DateTime',
            'ForeignKey': 'from sqlalchemy import ForeignKey',
            'relationship': 'from sqlalchemy.orm import relationship',
            'Session': 'from sqlalchemy.orm import Session',
            'select': 'from sqlalchemy import select',
            'and_': 'from sqlalchemy import and_',
            'or_': 'from sqlalchemy import or_',
            'func': 'from sqlalchemy import func',

            # Common exceptions
            'ValueError': '',  # Built-in
            'TypeError': '',  # Built-in
            'KeyError': '',  # Built-in
            'AttributeError': '',  # Built-in
            'ImportError': '',  # Built-in
            'Exception': '',  # Built-in
            'RuntimeError': '',  # Built-in
            'NotImplementedError': '',  # Built-in
            'FileNotFoundError': '',  # Built-in
            'ConnectionError': '',  # Built-in
            'TimeoutError': '',  # Built-in

            # Project-specific
            'get_db': 'from database import get_db',
            'settings': 'from config.settings import settings',
            'Settings': 'from config.settings import Settings',
            'User': 'from database.models import User',
            'Evidence': 'from database.models import Evidence',
            'Assessment': 'from database.models import Assessment',
        }

    def visit_Name(self, node):
        """Visit name nodes to find undefined names."""
        if isinstance(node.ctx, ast.Load):
            # Check if this name is defined
            if node.id not in self.defined_names and node.id not in dir(__builtins__):
                self.undefined_names.add(node.id)
        elif isinstance(node.ctx, ast.Store):
            self.defined_names.add(node.id)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        """Track function definitions."""
        self.defined_names.add(node.name)
        # Add parameters as defined
        for arg in node.args.args:
            self.defined_names.add(arg.arg)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        """Track async function definitions."""
        self.defined_names.add(node.name)
        for arg in node.args.args:
            self.defined_names.add(arg.arg)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        """Track class definitions."""
        self.defined_names.add(node.name)
        self.generic_visit(node)

    def visit_Import(self, node):
        """Track imports."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.defined_names.add(name.split('.')[0])

    def visit_ImportFrom(self, node):
        """Track from imports."""
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.defined_names.add(name)

    def visit_ExceptHandler(self, node):
        """Track exception handler variables."""
        if node.name:
            self.defined_names.add(node.name)
        self.generic_visit(node)


def fix_file(file_path: Path) -> bool:
    """Fix undefined names in a single file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        lines = content.splitlines(keepends=True)

        # Parse the file
        try:
            tree = ast.parse(content)
        except SyntaxError:
            # Skip files with syntax errors
            return False

        # Find undefined names
        fixer = UndefinedNameFixer()
        fixer.visit(tree)

        if not fixer.undefined_names:
            return False

        # Determine needed imports
        imports_to_add = []
        for name in fixer.undefined_names:
            if name in fixer.import_map and fixer.import_map[name]:
                imports_to_add.append(fixer.import_map[name])

        if not imports_to_add:
            # No known fixes for these undefined names
            return False

        # Find where to insert imports
        insert_line = 0
        has_future_import = False
        has_docstring = False

        for i, line in enumerate(lines):
            if line.strip().startswith('"""') or line.strip().startswith("'''"):
                has_docstring = True
                # Find end of docstring
                if line.count('"""') == 2 or line.count("'''") == 2:
                    insert_line = i + 1
                else:
                    for j in range(i + 1, len(lines)):
                        if '"""' in lines[j] or "'''" in lines[j]:
                            insert_line = j + 1
                            break
                break
            elif line.strip().startswith('from __future__'):
                has_future_import = True
                insert_line = i + 1
            elif line.strip() and not line.strip().startswith('#'):
                if not has_docstring:
                    insert_line = i
                break

        # Add imports
        unique_imports = list(set(imports_to_add))
        unique_imports.sort()

        for import_stmt in unique_imports:
            if import_stmt not in content:
                lines.insert(insert_line, import_stmt + '\n')
                insert_line += 1

        # Add blank line after imports if needed
        if unique_imports and insert_line < len(lines) and lines[insert_line].strip():
            lines.insert(insert_line, '\n')

        # Write back
        new_content = ''.join(lines)
        file_path.write_text(new_content, encoding='utf-8')
        return True

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False


def main():
    """Main function to fix undefined names."""
    root_path = Path('/home/omar/Documents/ruleIQ')

    # Find all Python files
    python_files = []
    for pattern in ['api/**/*.py', 'services/**/*.py', 'utils/**/*.py',
                    'core/**/*.py', 'database/**/*.py', 'tests/**/*.py',
                    'config/**/*.py', 'scripts/**/*.py']:
        python_files.extend(root_path.glob(pattern))

    print(f"Found {len(python_files)} Python files to check")

    fixed_count = 0
    for file_path in python_files:
        if fix_file(file_path):
            fixed_count += 1
            print(f"Fixed: {file_path}")

    print(f"\n✅ Fixed undefined names in {fixed_count} files")

    return 0


if __name__ == '__main__':
    sys.exit(main())
