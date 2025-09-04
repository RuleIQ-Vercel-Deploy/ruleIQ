"""
Comprehensive Security Scanner and Automatic Fixer
This script identifies and fixes security vulnerabilities across the RuleIQ codebase
Priority: P3 - Security Vulnerability Remediation
"""
import os
import re
import json
import ast
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime
import subprocess


class SecurityScanner:
    """Comprehensive security scanner for RuleIQ codebase"""

    def __init__(self, project_root: str='.'):
        self.project_root = Path(project_root)
        self.vulnerabilities = []
        self.fixes_applied = []

    def scan_sql_injection(self) ->List[Dict[str, Any]]:
        """Scan for SQL injection vulnerabilities"""
        sql_issues = []
        patterns = [('f".*(?:SELECT|INSERT|UPDATE|DELETE|DROP).*\\{.*\\}"',
            'F-string SQL injection'), (
            '\\.format\\(.*\\).*(?:SELECT|INSERT|UPDATE|DELETE)',
            'Format string SQL injection'), ('execute\\(["\\\'].*%[sd]',
            'String interpolation in execute'), ('\\+.*request\\.',
            'User input concatenation'), ('db\\.execute\\(.*\\+',
            'Direct concatenation in DB execute')]
        python_files = list(self.project_root.glob('**/*.py'))
        for file_path in python_files:
            if any(skip in str(file_path) for skip in ['venv',
                '__pycache__', '.git', 'migrations']):
                continue
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    lines = content.splitlines()
                for line_num, line in enumerate(lines, 1):
                    for pattern, issue_type in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            sql_issues.append({'file': str(file_path.
                                relative_to(self.project_root)), 'line':
                                line_num, 'type': issue_type, 'severity':
                                'CRITICAL', 'code': line.strip()[:100]})
            except Exception as e:
                print(f'Error scanning {file_path}: {e}')
        return sql_issues

    def scan_hardcoded_secrets(self) ->List[Dict[str, Any]]:
        """Scan for hardcoded secrets and credentials"""
        secret_issues = []
        patterns = [(
            '(?:password|passwd|pwd)\\s*=\\s*["\\\'][^"\\\']+["\\\']',
            'Hardcoded password'), (
            '(?:api_key|apikey|API_KEY)\\s*=\\s*["\\\'][^"\\\']+["\\\']',
            'Hardcoded API key'), (
            '(?:secret|SECRET)\\s*=\\s*["\\\'][^"\\\']+["\\\']',
            'Hardcoded secret'), (
            '(?:token|TOKEN)\\s*=\\s*["\\\'][^"\\\']+["\\\']',
            'Hardcoded token'), ('JWT_SECRET.*=.*["\\\'][^"\\\']+["\\\']',
            'Hardcoded JWT secret'), (
            '(?:aws|AWS)_.*(?:KEY|SECRET).*=.*["\\\'][^"\\\']+["\\\']',
            'AWS credentials')]
        _scan_hardcoded_secrets_part_1()
        return secret_issues

    def scan_authentication_issues(self) ->List[Dict[str, Any]]:
        """Scan for authentication and authorization issues"""
        auth_issues = []
        for file_path in self.project_root.glob('api/routers/*.py'):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        has_route = any(isinstance(d, ast.Name) and d.id in
                            ['get', 'post', 'put', 'delete', 'patch'] for d in
                            node.decorator_list) or any(isinstance(d, ast.
                            Attribute) and d.attr in ['get', 'post', 'put',
                            'delete', 'patch'] for d in node.decorator_list)
                        if has_route:
                            has_auth = False
                            for arg in node.args.args:
                                arg_str = ast.unparse(arg) if hasattr(ast,
                                    'unparse') else str(arg)
                                if ('get_current' in arg_str or 'Depends' in
                                    arg_str):
                                    has_auth = True
                                    break
                            public_endpoints = ['health', 'login',
                                'register', 'docs', 'openapi', 'token']
                            if not has_auth and not any(pub in node.name.
                                lower() for pub in public_endpoints):
                                auth_issues.append({'file': str(file_path.
                                    relative_to(self.project_root)), 'line':
                                    node.lineno, 'type':
                                    'Missing authentication', 'severity':
                                    'HIGH', 'code': f'Function: {node.name}'})
            except Exception as e:
                print(f'Error scanning {file_path}: {e}')
        return auth_issues

    def scan_input_validation(self) ->List[Dict[str, Any]]:
        """Scan for input validation issues"""
        validation_issues = []
        patterns = [('request\\.(?:args|form|json|query_params)\\[',
            'Direct request access without validation'), (
            'int\\(request\\.', 'Type casting without error handling'), (
            'float\\(request\\.', 'Type casting without error handling'), (
            'eval\\(', 'Dangerous eval() usage'), ('exec\\(',
            'Dangerous exec() usage'), ('pickle\\.loads?\\(',
            'Unsafe deserialization'), (
            'yaml\\.load\\([^)]*\\)(?!.*Loader)', 'Unsafe YAML loading')]
        for file_path in self.project_root.glob('**/*.py'):
            if any(skip in str(file_path) for skip in ['venv',
                '__pycache__', '.git']):
                continue
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    lines = content.splitlines()
                for line_num, line in enumerate(lines, 1):
                    for pattern, issue_type in patterns:
                        if re.search(pattern, line):
                            validation_issues.append({'file': str(file_path
                                .relative_to(self.project_root)), 'line':
                                line_num, 'type': issue_type, 'severity': 
                                'HIGH' if 'eval' in pattern or 'exec' in
                                pattern else 'MEDIUM', 'code': line.strip()
                                [:100]})
            except Exception as e:
                print(f'Error scanning {file_path}: {e}')
        return validation_issues

    def scan_all(self) ->Dict[str, Any]:
        """Run all security scans"""
        print('🔍 Starting comprehensive security scan...')
        results = {'scan_date': datetime.now().isoformat(), 'sql_injection':
            self.scan_sql_injection(), 'hardcoded_secrets': self.
            scan_hardcoded_secrets(), 'authentication': self.
            scan_authentication_issues(), 'input_validation': self.
            scan_input_validation()}
        total_critical = sum(len([v for v in vulns if v.get('severity') ==
            'CRITICAL']) for vulns in results.values() if isinstance(vulns,
            list))
        total_high = sum(len([v for v in vulns if v.get('severity') ==
            'HIGH']) for vulns in results.values() if isinstance(vulns, list))
        total_medium = sum(len([v for v in vulns if v.get('severity') ==
            'MEDIUM']) for vulns in results.values() if isinstance(vulns, list)
            )
        results['summary'] = {'total_critical': total_critical,
            'total_high': total_high, 'total_medium': total_medium,
            'total_issues': total_critical + total_high + total_medium}
        return results


class SecurityFixer:
    """Automatically fix security vulnerabilities"""

    def __init__(self, project_root: str='.'):
        self.project_root = Path(project_root)
        self.fixes_applied = []

    def fix_cors_configuration(self) ->bool:
        """Fix CORS misconfiguration"""
        main_file = self.project_root / 'main.py'
        if not main_file.exists():
            return False
        with open(main_file, 'r') as f:
            content = f.read()
        original = content
        content = re.sub("allow_methods=\\['?\\*'?\\]",
            'allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]'
            , content)
        content = re.sub("allow_headers=\\['?\\*'?\\]",
            'allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Request-ID"]'
            , content)
        if content != original:
            with open(main_file, 'w') as f:
                f.write(content)
            self.fixes_applied.append('Fixed CORS configuration in main.py')
            return True
        return False

    def add_input_validation(self, file_path: str, line_num: int) ->bool:
        """Add input validation to a specific line"""
        file = Path(file_path)
        if not file.exists():
            return False
        with open(file, 'r') as f:
            lines = f.readlines()
        if line_num <= len(lines):
            lines[line_num - 1] = f"""# SECURITY: Review and add input validation
{lines[line_num - 1]}"""
            with open(file, 'w') as f:
                f.writelines(lines)
            return True
        return False


def main():
    """Main execution"""
    print('=' * 80)
    print('🔒 RuleIQ Security Vulnerability Remediation')
    print('=' * 80)
    scanner = SecurityScanner()
    results = scanner.scan_all()
    with open('security_scan_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f'\n📊 Security Scan Results:')
    print(f"   🚨 Critical: {results['summary']['total_critical']}")
    print(f"   🔴 High: {results['summary']['total_high']}")
    print(f"   🟡 Medium: {results['summary']['total_medium']}")
    print(f"   📝 Total Issues: {results['summary']['total_issues']}")
    if results['summary']['total_critical'] > 0:
        print('\n🚨 CRITICAL ISSUES FOUND:')
        for category, issues in results.items():
            if isinstance(issues, list):
                critical = [i for i in issues if i.get('severity') ==
                    'CRITICAL']
                if critical:
                    print(f'\n   {category.upper()}:')
                    for issue in critical[:5]:
                        print(
                            f"      - {issue['file']}:{issue['line']} - {issue['type']}"
                            )
    print('\n🔧 Applying automatic fixes...')
    fixer = SecurityFixer()
    if fixer.fix_cors_configuration():
        print('   ✅ Fixed CORS configuration')
    print('\n📄 Detailed report saved to: security_scan_results.json')
    if results['summary']['total_critical'] > 0:
        rating = 'E'
    elif results['summary']['total_high'] > 10:
        rating = 'D'
    elif results['summary']['total_high'] > 5:
        rating = 'C'
    elif results['summary']['total_medium'] > 20:
        rating = 'B'
    else:
        rating = 'A'
    print(f'\n🎯 Current Security Rating: {rating}')
    if rating in ['D', 'E']:
        print(
            '\n❌ Critical security issues detected. Immediate remediation required!'
            )
        return 1
    else:
        print('\n✅ Security scan completed. Continue with remediation plan.')
        return 0


if __name__ == '__main__':
    exit(main())


def _scan_hardcoded_secrets_part_1(self):
    for file_path in self.project_root.glob('**/*.py'):
        if any(skip in str(file_path) for skip in ['venv', '__pycache__',
            '.git', 'tests']):
            continue
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                lines = content.splitlines()
            for line_num, line in enumerate(lines, 1):
                for pattern, issue_type in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        if ('os.getenv' in line or 'os.environ' in line or 
                            'settings.' in line):
                            continue
                        secret_issues.append({'file': str(file_path.
                            relative_to(self.project_root)), 'line':
                            line_num, 'type': issue_type, 'severity':
                            'CRITICAL', 'code': line.strip()[:100]})
        except Exception as e:
            print(f'Error scanning {file_path}: {e}')
