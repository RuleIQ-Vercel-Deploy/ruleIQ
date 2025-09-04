#!/usr/bin/env python3
"""
Security vulnerability scanner and fixer for RuleIQ codebase
Refactored to reduce cognitive complexity and improve code quality
"""

import re
import json
import ast
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime

class SecurityScanner:
    """Scans codebase for security vulnerabilities"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.vulnerability_patterns = self._get_vulnerability_patterns()
        
    def _get_vulnerability_patterns(self) -> Dict[str, List[Tuple[str, str, str]]]:
        """Get vulnerability patterns for scanning"""
        return {
            'sql_injection': [
                (r'f".*SELECT.*{.*}.*"', "SQL query with f-string formatting", "CRITICAL"),
                (r'f".*INSERT.*{.*}.*"', "SQL query with f-string formatting", "CRITICAL"),
                (r'f".*UPDATE.*{.*}.*"', "SQL query with f-string formatting", "CRITICAL"),
                (r'f".*DELETE.*{.*}.*"', "SQL query with f-string formatting", "CRITICAL"),
                (r'\.format\(.*\).*(?:SELECT|INSERT|UPDATE|DELETE)', "SQL query with .format()", "CRITICAL"),
                (r'%.*(?:SELECT|INSERT|UPDATE|DELETE)', "SQL query with % formatting", "HIGH"),
                (r'\+.*(?:SELECT|INSERT|UPDATE|DELETE)', "SQL query concatenation", "HIGH"),
            ],
            'hardcoded_secrets': [
                (r'(?:password|passwd|pwd)\s*=\s*["\'][^"\']+["\']', "Hardcoded password", "CRITICAL"),
                (r'(?:api[_-]?key|apikey)\s*=\s*["\'][^"\']+["\']', "Hardcoded API key", "CRITICAL"),
                (r'(?:secret[_-]?key|secret)\s*=\s*["\'][^"\']+["\']', "Hardcoded secret", "CRITICAL"),
                (r'(?:token|access[_-]?token)\s*=\s*["\'][^"\']+["\']', "Hardcoded token", "HIGH"),
                (r'(?:private[_-]?key)\s*=\s*["\'][^"\']+["\']', "Hardcoded private key", "CRITICAL"),
                (r'Bearer\s+[A-Za-z0-9\-._~+/]+', "Hardcoded bearer token", "HIGH"),
            ],
            'input_validation': [
                (r'request\.(?:args|form|json|query_params)\[', "Direct request access without validation", "MEDIUM"),
                (r'int\(request\.', "Type casting without error handling", "MEDIUM"),
                (r'float\(request\.', "Type casting without error handling", "MEDIUM"),
                (r'eval\(', "Dangerous eval() usage", "CRITICAL"),
                (r'exec\(', "Dangerous exec() usage", "CRITICAL"),
                (r'pickle\.loads?\(', "Unsafe deserialization", "HIGH"),
                (r'yaml\.load\([^)]*\)(?!.*Loader)', "Unsafe YAML loading", "HIGH"),
            ]
        }
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped"""
        skip_dirs = ['venv', '__pycache__', '.git', 'node_modules', '.pytest_cache']
        return any(skip in str(file_path) for skip in skip_dirs)
    
    def _scan_file_content(self, file_path: Path, content: str, 
                          patterns: List[Tuple[str, str, str]]) -> List[Dict[str, Any]]:
        """Scan file content for patterns"""
        issues = []
        lines = content.splitlines()
        
        for line_num, line in enumerate(lines, 1):
            for pattern, issue_type, severity in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    issues.append({
                        'file': str(file_path.relative_to(self.project_root)),
                        'line': line_num,
                        'type': issue_type,
                        'severity': severity,
                        'code': line.strip()[:100]
                    })
        return issues
    
    def scan_sql_injection(self) -> List[Dict[str, Any]]:
        """Scan for SQL injection vulnerabilities"""
        sql_issues = []
        patterns = self.vulnerability_patterns['sql_injection']
        
        for file_path in self.project_root.glob("**/*.py"):
            if self._should_skip_file(file_path):
                continue
                
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    issues = self._scan_file_content(file_path, content, patterns)
                    sql_issues.extend(issues)
            except Exception as e:
                print(f"Error scanning {file_path}: {e}")
                
        return sql_issues
    
    def scan_hardcoded_secrets(self) -> List[Dict[str, Any]]:
        """Scan for hardcoded secrets and credentials"""
        secret_issues = []
        patterns = self.vulnerability_patterns['hardcoded_secrets']
        excluded_files = ['config.example.py', '.env.example', 'test_', '_test.py']
        
        for file_path in self.project_root.glob("**/*.py"):
            if self._should_skip_file(file_path):
                continue
            
            # Skip example and test files
            if any(exc in str(file_path) for exc in excluded_files):
                continue
                
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    issues = self._scan_file_content(file_path, content, patterns)
                    secret_issues.extend(issues)
            except Exception as e:
                print(f"Error scanning {file_path}: {e}")
                
        return secret_issues
    
    def _check_route_authentication(self, node: ast.FunctionDef, 
                                   public_endpoints: List[str]) -> bool:
        """Check if route has proper authentication"""
        # Check for authentication dependency
        for arg in node.args.args:
            arg_str = ast.unparse(arg) if hasattr(ast, 'unparse') else str(arg)
            if 'get_current' in arg_str or 'Depends' in arg_str:
                return True
        
        # Check if it's a public endpoint
        return any(pub in node.name.lower() for pub in public_endpoints)
    
    def _analyze_route_handlers(self, tree: ast.AST, file_path: Path) -> List[Dict[str, Any]]:
        """Analyze route handlers for authentication issues"""
        auth_issues = []
        public_endpoints = ['health', 'login', 'register', 'docs', 'openapi', 'token']
        route_decorators = ['get', 'post', 'put', 'delete', 'patch']
        
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
                
            # Check if it's a route handler
            is_route = self._is_route_handler(node, route_decorators)
            
            if not is_route:
                continue
                
            # Check authentication
            has_auth = self._check_route_authentication(node, public_endpoints)
            
            if not has_auth:
                auth_issues.append({
                    'file': str(file_path.relative_to(self.project_root)),
                    'line': node.lineno,
                    'type': 'Missing authentication',
                    'severity': 'HIGH',
                    'code': f"Function: {node.name}"
                })
        
        return auth_issues
    
    def _is_route_handler(self, node: ast.FunctionDef, route_decorators: List[str]) -> bool:
        """Check if function is a route handler"""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id in route_decorators:
                return True
            if isinstance(decorator, ast.Attribute) and decorator.attr in route_decorators:
                return True
        return False
    
    def scan_authentication_issues(self) -> List[Dict[str, Any]]:
        """Scan for authentication and authorization issues"""
        auth_issues = []
        
        for file_path in self.project_root.glob("api/routers/*.py"):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # Parse AST to find route handlers
                tree = ast.parse(content)
                issues = self._analyze_route_handlers(tree, file_path)
                auth_issues.extend(issues)
                
            except Exception as e:
                print(f"Error scanning {file_path}: {e}")
                
        return auth_issues
    
    def scan_input_validation(self) -> List[Dict[str, Any]]:
        """Scan for input validation issues"""
        validation_issues = []
        patterns = self.vulnerability_patterns['input_validation']
        
        for file_path in self.project_root.glob("**/*.py"):
            if self._should_skip_file(file_path):
                continue
                
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    issues = self._scan_file_content(file_path, content, patterns)
                    validation_issues.extend(issues)
            except Exception as e:
                print(f"Error scanning {file_path}: {e}")
                
        return validation_issues
    
    def _calculate_summary(self, results: Dict[str, Any]) -> Dict[str, int]:
        """Calculate summary statistics from scan results"""
        summary = {
            'total_critical': 0,
            'total_high': 0,
            'total_medium': 0,
            'total_issues': 0
        }
        
        for category, issues in results.items():
            if not isinstance(issues, list):
                continue
                
            for issue in issues:
                severity = issue.get('severity', '')
                if severity == 'CRITICAL':
                    summary['total_critical'] += 1
                elif severity == 'HIGH':
                    summary['total_high'] += 1
                elif severity == 'MEDIUM':
                    summary['total_medium'] += 1
                summary['total_issues'] += 1
        
        return summary
    
    def scan_all(self) -> Dict[str, Any]:
        """Run all security scans"""
        print("🔍 Starting comprehensive security scan...")
        
        results = {
            'scan_date': datetime.now().isoformat(),
            'sql_injection': self.scan_sql_injection(),
            'hardcoded_secrets': self.scan_hardcoded_secrets(),
            'authentication': self.scan_authentication_issues(),
            'input_validation': self.scan_input_validation(),
        }
        
        # Calculate totals
        results['summary'] = self._calculate_summary(results)
        
        return results


class SecurityFixer:
    """Automatically fixes common security issues"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.fixes_applied = []
    
    def fix_cors_configuration(self) -> bool:
        """Fix CORS configuration to be more restrictive"""
        cors_file = self.project_root / "middleware" / "cors.py"
        
        if not cors_file.exists():
            self._create_cors_file(cors_file)
            return True
            
        try:
            with open(cors_file, 'r') as f:
                content = f.read()
                
            # Replace permissive CORS with secure configuration
            secure_cors = self._get_secure_cors_config()
            
            with open(cors_file, 'w') as f:
                f.write(secure_cors)
                
            self.fixes_applied.append("CORS configuration secured")
            return True
            
        except Exception as e:
            print(f"Error fixing CORS: {e}")
            return False
    
    def _create_cors_file(self, cors_file: Path) -> None:
        """Create CORS configuration file"""
        cors_file.parent.mkdir(parents=True, exist_ok=True)
        secure_cors = self._get_secure_cors_config()
        
        with open(cors_file, 'w') as f:
            f.write(secure_cors)
    
    def _get_secure_cors_config(self) -> str:
        """Get secure CORS configuration"""
        return '''from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os

def get_allowed_origins() -> List[str]:
    """Get allowed origins from environment"""
    env_origins = os.getenv("ALLOWED_ORIGINS", "")
    if env_origins:
        return [origin.strip() for origin in env_origins.split(",")]
    
    # Default for development only
    if os.getenv("ENVIRONMENT") == "development":
        return ["http://localhost:3000", "http://localhost:8000"]
    
    return []

def setup_cors(app):
    """Setup CORS middleware with security best practices"""
    allowed_origins = get_allowed_origins()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        max_age=3600,  # Cache preflight requests for 1 hour
    )
'''
    
    def apply_sql_injection_fixes(self, issues: List[Dict[str, Any]]) -> int:
        """Fix SQL injection vulnerabilities by using parameterized queries"""
        fixed_count = 0
        
        for issue in issues:
            if issue['severity'] != 'CRITICAL':
                continue
                
            file_path = self.project_root / issue['file']
            fixed = self._fix_sql_injection_in_file(file_path, issue['line'])
            if fixed:
                fixed_count += 1
                
        return fixed_count
    
    def _fix_sql_injection_in_file(self, file_path: Path, line_num: int) -> bool:
        """Fix SQL injection in specific file and line"""
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
                
            if line_num <= len(lines):
                original_line = lines[line_num - 1]
                fixed_line = self._convert_to_parameterized_query(original_line)
                
                if fixed_line != original_line:
                    lines[line_num - 1] = fixed_line
                    
                    with open(file_path, 'w') as f:
                        f.writelines(lines)
                    
                    self.fixes_applied.append(f"Fixed SQL injection in {file_path}:{line_num}")
                    return True
                    
        except Exception as e:
            print(f"Error fixing {file_path}:{line_num}: {e}")
            
        return False
    
    def _convert_to_parameterized_query(self, line: str) -> str:
        """Convert SQL query to use parameterized format"""
        # This is a simplified example - real implementation would be more complex
        if 'f"' in line or 'f\'' in line:
            # Replace f-string with parameterized query
            line = re.sub(r'f(["\'])(.*?)\1', r'\1\2\1', line)
            line = line.replace('{', '%s').replace('}', '')
            
        return line


def print_scan_summary(results: Dict[str, Any]) -> None:
    """Print scan summary"""
    print(f"\n📊 Security Scan Results:")
    print(f"   🚨 Critical: {results['summary']['total_critical']}")
    print(f"   🔴 High: {results['summary']['total_high']}")
    print(f"   🟡 Medium: {results['summary']['total_medium']}")
    print(f"   📝 Total Issues: {results['summary']['total_issues']}")


def print_critical_issues(results: Dict[str, Any]) -> None:
    """Print critical issues found"""
    if results['summary']['total_critical'] == 0:
        return
        
    print("\n🚨 CRITICAL ISSUES FOUND:")
    for category, issues in results.items():
        if not isinstance(issues, list):
            continue
            
        critical = [i for i in issues if i.get('severity') == 'CRITICAL']
        if not critical:
            continue
            
        print(f"\n   {category.upper()}:")
        for issue in critical[:5]:  # Show first 5
            print(f"      - {issue['file']}:{issue['line']} - {issue['type']}")


def determine_security_rating(summary: Dict[str, int]) -> str:
    """Determine security rating based on issues found"""
    if summary['total_critical'] > 0:
        return 'E'
    elif summary['total_high'] > 10:
        return 'D'
    elif summary['total_high'] > 5:
        return 'C'
    elif summary['total_medium'] > 20:
        return 'B'
    else:
        return 'A'


def main():
    """Main execution - refactored with reduced complexity"""
    print("=" * 80)
    print("🔒 RuleIQ Security Vulnerability Remediation")
    print("=" * 80)
    
    # Initialize scanner
    scanner = SecurityScanner()
    results = scanner.scan_all()
    
    # Save results
    with open('security_scan_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print_scan_summary(results)
    
    # Print critical issues
    print_critical_issues(results)
    
    # Apply automatic fixes
    print("\n🔧 Applying automatic fixes...")
    fixer = SecurityFixer()
    
    if fixer.fix_cors_configuration():
        print("   ✅ Fixed CORS configuration")
    
    # Generate detailed report
    print("\n📄 Detailed report saved to: security_scan_results.json")
    
    # Determine security rating
    rating = determine_security_rating(results['summary'])
    
    print(f"\n🎯 Current Security Rating: {rating}")
    
    if rating in ['D', 'E']:
        print("\n❌ Critical security issues detected. Immediate remediation required!")
        return 1
    else:
        print("\n✅ Security scan completed. Continue with remediation plan.")
        return 0


if __name__ == "__main__":
    exit(main())