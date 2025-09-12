#!/usr/bin/env python3
"""
JWT Coverage Audit Script
Part of SEC-005: Complete JWT Coverage Extension

This script inventories all API routes and checks their JWT authentication status.
"""
import os
import re
import ast
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum


class AuthStatus(Enum):
    """Authentication status for routes"""
    PROTECTED = "protected"  # Has JWT middleware/decorator
    UNPROTECTED = "unprotected"  # No authentication
    PUBLIC = "public"  # Intentionally public
    UNKNOWN = "unknown"  # Cannot determine


@dataclass
class RouteInfo:
    """Information about an API route"""
    file_path: str
    method: str
    path: str
    function_name: str
    auth_status: AuthStatus
    has_get_current_user: bool = False
    has_jwt_decorator: bool = False
    line_number: int = 0
    priority: str = ""  # Critical, High, Medium, Low


class RouteScanner:
    """Scans Python files for FastAPI routes and their authentication status"""
    
    # Public paths that don't need authentication
    PUBLIC_PATHS = {
        '/docs', '/redoc', '/openapi.json', '/health', '/',
        '/api/v1/auth/login', '/api/v1/auth/register', '/api/v1/auth/token',
        '/api/v1/auth/refresh', '/api/v1/auth/forgot-password', 
        '/api/v1/auth/reset-password', '/api/v1/auth/google/',
        '/api/v1/freemium/', '/api/test-utils/', '/metrics'
    }
    
    # Route priority based on sensitivity
    PRIORITY_PATTERNS = {
        'Critical': [r'admin', r'payment', r'api-key', r'secret', r'delete'],
        'High': [r'assessment', r'compliance', r'evidence', r'policies', r'user'],
        'Medium': [r'report', r'dashboard', r'monitoring', r'integration'],
        'Low': [r'health', r'ping', r'info']
    }
    
    def __init__(self, project_root: str = "/home/omar/Documents/ruleIQ"):
        self.project_root = Path(project_root)
        self.routes: List[RouteInfo] = []
    
    def is_public_path(self, path: str) -> bool:
        """Check if a path is intentionally public"""
        for public_path in self.PUBLIC_PATHS:
            if path.startswith(public_path):
                return True
        return False
    
    def get_priority(self, path: str, function_name: str) -> str:
        """Determine priority of a route based on its path and function"""
        combined = f"{path} {function_name}".lower()
        
        for priority, patterns in self.PRIORITY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, combined):
                    return priority
        
        return "Medium"  # Default priority
    
    def scan_file(self, file_path: Path) -> List[RouteInfo]:
        """Scan a Python file for FastAPI routes"""
        routes = []
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                tree = ast.parse(content)
            
            # Look for route decorators
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                    route_info = self.analyze_function(node, content, str(file_path))
                    if route_info:
                        routes.append(route_info)
        
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
        
        return routes
    
    def analyze_function(self, node, content: str, file_path: str) -> RouteInfo:
        """Analyze a function for route information and auth status"""
        # Check if this is a route function
        route_decorator = None
        has_jwt_decorator = False
        
        for decorator in node.decorator_list:
            decorator_str = ast.unparse(decorator) if hasattr(ast, 'unparse') else str(decorator)
            
            # Check for route decorators
            if 'router.' in decorator_str or 'app.' in decorator_str:
                if any(method in decorator_str for method in ['get', 'post', 'put', 'delete', 'patch']):
                    route_decorator = decorator_str
            
            # Check for JWT decorators
            if 'JWTMiddleware' in decorator_str or 'require_auth' in decorator_str:
                has_jwt_decorator = True
        
        if not route_decorator:
            return None
        
        # Extract method and path
        method_match = re.search(r'(get|post|put|delete|patch)', route_decorator.lower())
        path_match = re.search(r'["\']([^"\']+)["\']', route_decorator)
        
        if not method_match or not path_match:
            return None
        
        method = method_match.group(1).upper()
        path = path_match.group(1)
        
        # Check for get_current_user dependency
        has_get_current_user = 'get_current_user' in ast.unparse(node) if hasattr(ast, 'unparse') else False
        if not has_get_current_user:
            # Fallback to string search
            function_str = content[node.col_offset:node.end_col_offset] if hasattr(node, 'end_col_offset') else ""
            has_get_current_user = 'get_current_user' in function_str or 'Depends(get_current_user' in content
        
        # Determine auth status
        if self.is_public_path(path):
            auth_status = AuthStatus.PUBLIC
        elif has_jwt_decorator or has_get_current_user:
            auth_status = AuthStatus.PROTECTED
        else:
            auth_status = AuthStatus.UNPROTECTED
        
        # Get priority
        priority = self.get_priority(path, node.name)
        
        return RouteInfo(
            file_path=file_path,
            method=method,
            path=path,
            function_name=node.name,
            auth_status=auth_status,
            has_get_current_user=has_get_current_user,
            has_jwt_decorator=has_jwt_decorator,
            line_number=node.lineno,
            priority=priority
        )
    
    def scan_routers(self) -> None:
        """Scan all router files in the project"""
        router_dir = self.project_root / "api" / "routers"
        
        if router_dir.exists():
            for py_file in router_dir.rglob("*.py"):
                if py_file.name != "__init__.py":
                    routes = self.scan_file(py_file)
                    self.routes.extend(routes)
        
        # Also scan api/v1 directory
        v1_dir = self.project_root / "api" / "v1"
        if v1_dir.exists():
            for py_file in v1_dir.rglob("*.py"):
                if py_file.name != "__init__.py":
                    routes = self.scan_file(py_file)
                    self.routes.extend(routes)
    
    def generate_report(self) -> str:
        """Generate a report of route coverage"""
        total_routes = len(self.routes)
        protected_routes = [r for r in self.routes if r.auth_status == AuthStatus.PROTECTED]
        unprotected_routes = [r for r in self.routes if r.auth_status == AuthStatus.UNPROTECTED]
        public_routes = [r for r in self.routes if r.auth_status == AuthStatus.PUBLIC]
        
        report = []
        report.append("=" * 80)
        report.append("JWT COVERAGE AUDIT REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        report.append("SUMMARY")
        report.append("-" * 40)
        report.append(f"Total Routes: {total_routes}")
        report.append(f"Protected Routes: {len(protected_routes)} ({len(protected_routes)/total_routes*100:.1f}%)")
        report.append(f"Unprotected Routes: {len(unprotected_routes)} ({len(unprotected_routes)/total_routes*100:.1f}%)")
        report.append(f"Public Routes: {len(public_routes)} ({len(public_routes)/total_routes*100:.1f}%)")
        report.append("")
        
        # Unprotected routes by priority
        if unprotected_routes:
            report.append("UNPROTECTED ROUTES REQUIRING JWT")
            report.append("-" * 40)
            
            # Group by priority
            by_priority = {}
            for route in unprotected_routes:
                if route.priority not in by_priority:
                    by_priority[route.priority] = []
                by_priority[route.priority].append(route)
            
            for priority in ['Critical', 'High', 'Medium', 'Low']:
                if priority in by_priority:
                    report.append(f"\n{priority} Priority ({len(by_priority[priority])} routes):")
                    for route in by_priority[priority]:
                        file_name = Path(route.file_path).name
                        report.append(f"  - {route.method:6} {route.path:40} ({file_name}:{route.line_number})")
        
        # Protected routes summary
        report.append("")
        report.append("PROTECTED ROUTES")
        report.append("-" * 40)
        report.append(f"Total: {len(protected_routes)} routes")
        
        # Public routes summary
        report.append("")
        report.append("PUBLIC ROUTES")
        report.append("-" * 40)
        report.append(f"Total: {len(public_routes)} routes")
        
        return "\n".join(report)
    
    def generate_fix_script(self) -> str:
        """Generate a script to fix unprotected routes"""
        unprotected = [r for r in self.routes if r.auth_status == AuthStatus.UNPROTECTED]
        
        if not unprotected:
            return "# No unprotected routes found!"
        
        script = []
        script.append("#!/usr/bin/env python3")
        script.append('"""')
        script.append("Auto-generated script to add JWT protection to unprotected routes")
        script.append('"""')
        script.append("")
        script.append("# Routes to update:")
        
        # Group by file
        by_file = {}
        for route in unprotected:
            if route.file_path not in by_file:
                by_file[route.file_path] = []
            by_file[route.file_path].append(route)
        
        for file_path, routes in by_file.items():
            script.append(f"\n# File: {file_path}")
            script.append(f"# Routes to protect: {len(routes)}")
            for route in routes:
                script.append(f"#   - {route.method} {route.path} (line {route.line_number})")
        
        return "\n".join(script)


def main():
    """Main function to run the JWT coverage audit"""
    print("Starting JWT Coverage Audit...")
    
    scanner = RouteScanner()
    scanner.scan_routers()
    
    # Generate and print report
    report = scanner.generate_report()
    print(report)
    
    # Save report to file
    report_path = Path("/home/omar/Documents/ruleIQ/jwt_coverage_report.txt")
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")
    
    # Generate fix script
    fix_script = scanner.generate_fix_script()
    fix_path = Path("/home/omar/Documents/ruleIQ/jwt_coverage_fixes.py")
    with open(fix_path, 'w') as f:
        f.write(fix_script)
    print(f"Fix script saved to: {fix_path}")
    
    # Return statistics for validation
    unprotected_count = len([r for r in scanner.routes if r.auth_status == AuthStatus.UNPROTECTED])
    return unprotected_count == 0  # True if all routes are protected


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)