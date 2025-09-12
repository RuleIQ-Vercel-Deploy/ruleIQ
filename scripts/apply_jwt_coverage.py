#!/usr/bin/env python3
"""
Apply JWT Coverage Script
Part of SEC-005: Complete JWT Coverage Extension

This script applies JWT middleware v2 to all unprotected routes.
"""
import os
import re
from pathlib import Path
from typing import List, Tuple, Set
import ast
import astor


class JWTCoverageApplier:
    """Applies JWT middleware to unprotected routes"""
    
    # Routes that should remain public
    PUBLIC_ROUTE_PATTERNS = [
        r'/docs', r'/redoc', r'/openapi\.json', r'/health', r'^/$',
        r'/api/v1/auth/login', r'/api/v1/auth/register', r'/api/v1/auth/token',
        r'/api/v1/auth/refresh', r'/api/v1/auth/forgot-password',
        r'/api/v1/auth/reset-password', r'/api/v1/auth/google/',
        r'/api/v1/freemium/', r'/api/test-utils/', r'/metrics',
        r'/api/v1/feature-flags/evaluate'
    ]
    
    def __init__(self, project_root: str = "/home/omar/Documents/ruleIQ"):
        self.project_root = Path(project_root)
        self.files_modified = []
        self.routes_protected = 0
    
    def is_public_route(self, path: str) -> bool:
        """Check if a route should remain public"""
        for pattern in self.PUBLIC_ROUTE_PATTERNS:
            if re.search(pattern, path):
                return True
        return False
    
    def update_imports(self, content: str, file_path: str) -> str:
        """Ensure the file has the necessary imports for JWT middleware"""
        lines = content.split('\n')
        
        # Check if imports already exist
        has_jwt_import = any('JWTMiddleware' in line for line in lines)
        has_depends_import = any('from fastapi import' in line and 'Depends' in line for line in lines)
        has_user_import = any('get_current_user' in line or 'get_current_active_user' in line for line in lines)
        
        # Find the last import line
        last_import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith('import ') or line.startswith('from '):
                last_import_idx = i
        
        # Add necessary imports
        new_imports = []
        
        if not has_jwt_import:
            new_imports.append('from middleware.jwt_decorators import JWTMiddleware')
        
        if not has_depends_import:
            # Update existing fastapi import or add new one
            fastapi_import_idx = None
            for i, line in enumerate(lines):
                if 'from fastapi import' in line:
                    fastapi_import_idx = i
                    break
            
            if fastapi_import_idx is not None:
                # Add Depends to existing import if not present
                if 'Depends' not in lines[fastapi_import_idx]:
                    lines[fastapi_import_idx] = lines[fastapi_import_idx].rstrip(')') + ', Depends)'
            else:
                new_imports.append('from fastapi import Depends')
        
        if not has_user_import:
            new_imports.append('from api.dependencies.auth import get_current_user')
        
        # Insert new imports after the last import
        if new_imports:
            for imp in reversed(new_imports):
                lines.insert(last_import_idx + 1, imp)
        
        return '\n'.join(lines)
    
    def add_jwt_decorator(self, content: str, route_path: str, function_name: str, line_number: int) -> str:
        """Add JWT middleware decorator to a route function"""
        lines = content.split('\n')
        
        # Find the function definition
        func_line_idx = None
        for i, line in enumerate(lines):
            if f'def {function_name}(' in line or f'async def {function_name}(' in line:
                # Make sure it's close to the expected line number
                if abs(i + 1 - line_number) < 10:
                    func_line_idx = i
                    break
        
        if func_line_idx is None:
            print(f"  Warning: Could not find function {function_name} around line {line_number}")
            return content
        
        # Find the route decorator above the function
        route_decorator_idx = None
        for i in range(func_line_idx - 1, max(0, func_line_idx - 10), -1):
            if '@router.' in lines[i] or '@app.' in lines[i]:
                route_decorator_idx = i
                break
        
        if route_decorator_idx is None:
            print(f"  Warning: Could not find route decorator for {function_name}")
            return content
        
        # Check if JWT decorator already exists
        has_jwt_decorator = False
        for i in range(route_decorator_idx, func_line_idx):
            if 'JWTMiddleware.require_auth' in lines[i] or '@require_auth' in lines[i]:
                has_jwt_decorator = True
                break
        
        if has_jwt_decorator:
            print(f"  Route already has JWT decorator: {function_name}")
            return content
        
        # Add JWT decorator after the route decorator
        indent = len(lines[route_decorator_idx]) - len(lines[route_decorator_idx].lstrip())
        jwt_decorator = ' ' * indent + '@JWTMiddleware.require_auth'
        lines.insert(route_decorator_idx + 1, jwt_decorator)
        
        # Check if function has current_user parameter
        func_signature = []
        i = func_line_idx
        while i < len(lines) and not lines[i].rstrip().endswith(':'):
            func_signature.append(lines[i])
            i += 1
        if i < len(lines):
            func_signature.append(lines[i])
        
        signature_str = ' '.join(func_signature)
        
        # Add current_user parameter if not present
        if 'current_user' not in signature_str and 'get_current_user' not in signature_str:
            # Find the closing parenthesis of the function signature
            for i in range(func_line_idx, min(func_line_idx + 10, len(lines))):
                if ')' in lines[i]:
                    # Add current_user parameter
                    if '()' in lines[i]:
                        # No parameters yet
                        lines[i] = lines[i].replace('()', '(current_user=Depends(get_current_user))')
                    else:
                        # Has parameters, add to the end
                        lines[i] = lines[i].replace(')', ', current_user=Depends(get_current_user))')
                    break
        
        self.routes_protected += 1
        return '\n'.join(lines)
    
    def process_file(self, file_path: Path) -> bool:
        """Process a single Python file to add JWT protection"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            original_content = content
            
            # Parse the file to find unprotected routes
            tree = ast.parse(content)
            
            functions_to_protect = []
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Check if this is a route function
                    is_route = False
                    has_auth = False
                    route_path = None
                    
                    for decorator in node.decorator_list:
                        decorator_str = ast.unparse(decorator) if hasattr(ast, 'unparse') else self.ast_to_string(decorator)
                        
                        # Check if it's a route decorator
                        if ('router.' in decorator_str or 'app.' in decorator_str) and \
                           any(method in decorator_str for method in ['get', 'post', 'put', 'delete', 'patch']):
                            is_route = True
                            # Extract route path
                            path_match = re.search(r'["\']([^"\']+)["\']', decorator_str)
                            if path_match:
                                route_path = path_match.group(1)
                        
                        # Check if it has auth decorator
                        if 'require_auth' in decorator_str or 'JWTMiddleware' in decorator_str:
                            has_auth = True
                    
                    # Check if function has get_current_user parameter
                    func_str = ast.unparse(node) if hasattr(ast, 'unparse') else ''
                    if 'get_current_user' in func_str or 'get_current_active_user' in func_str:
                        has_auth = True
                    
                    # Add to protection list if it's an unprotected non-public route
                    if is_route and not has_auth and route_path:
                        if not self.is_public_route(route_path):
                            functions_to_protect.append((route_path, node.name, node.lineno))
            
            # Apply protection to identified functions
            if functions_to_protect:
                print(f"\nProcessing {file_path.name}:")
                
                # Update imports first
                content = self.update_imports(content, str(file_path))
                
                # Add JWT decorators
                for route_path, func_name, line_num in functions_to_protect:
                    print(f"  Protecting: {func_name} ({route_path})")
                    content = self.add_jwt_decorator(content, route_path, func_name, line_num)
                
                # Write the modified content back
                if content != original_content:
                    with open(file_path, 'w') as f:
                        f.write(content)
                    self.files_modified.append(str(file_path))
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def ast_to_string(self, node) -> str:
        """Convert AST node to string (fallback for older Python versions)"""
        try:
            return astor.to_source(node).strip()
        except:
            return str(node)
    
    def apply_coverage(self) -> Tuple[int, int]:
        """Apply JWT coverage to all router files"""
        router_dirs = [
            self.project_root / "api" / "routers",
            self.project_root / "api" / "v1"
        ]
        
        total_files = 0
        
        for router_dir in router_dirs:
            if router_dir.exists():
                for py_file in router_dir.rglob("*.py"):
                    if py_file.name != "__init__.py":
                        total_files += 1
                        self.process_file(py_file)
        
        return len(self.files_modified), self.routes_protected


def main():
    """Main function to apply JWT coverage"""
    print("=" * 80)
    print("JWT COVERAGE APPLICATION SCRIPT")
    print("Part of SEC-005: Complete JWT Coverage Extension")
    print("=" * 80)
    print()
    
    applier = JWTCoverageApplier()
    
    print("Scanning and applying JWT protection to unprotected routes...")
    files_modified, routes_protected = applier.apply_coverage()
    
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Files modified: {files_modified}")
    print(f"Routes protected: {routes_protected}")
    
    if applier.files_modified:
        print("\nModified files:")
        for file_path in applier.files_modified:
            print(f"  - {file_path}")
    
    print()
    print("JWT coverage application complete!")
    
    return routes_protected > 0


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)