#!/usr/bin/env python3
"""
Security Audit Script for RuleIQ
Identifies and prioritizes security vulnerabilities based on OWASP Top 10
Author: Security Auditor
Date: January 2025
"""

import os
import re
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
import ast

class Severity(Enum):
    CRITICAL = "CRITICAL"
    """Class for Severity"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class VulnerabilityType(Enum):
    SQL_INJECTION = "SQL Injection"
    """Class for VulnerabilityType"""
    XSS = "Cross-Site Scripting (XSS)"
    AUTH_BYPASS = "Authentication Bypass"
    HARDCODED_SECRET = "Hardcoded Secrets"
    INSECURE_RANDOM = "Insecure Random"
    PATH_TRAVERSAL = "Path Traversal"
    XXE = "XML External Entity"
    SSRF = "Server-Side Request Forgery"
    WEAK_CRYPTO = "Weak Cryptography"
    MISSING_HEADERS = "Missing Security Headers"
    CORS_MISCONFIGURATION = "CORS Misconfiguration"
    RATE_LIMITING = "Missing Rate Limiting"
    INPUT_VALIDATION = "Insufficient Input Validation"
    SESSION_MANAGEMENT = "Session Management Issue"
    INSECURE_DESERIALIZATION = "Insecure Deserialization"
    LOGGING_ISSUE = "Security Logging Issue"
    FILE_UPLOAD = "Insecure File Upload"
    CSRF = "Cross-Site Request Forgery"
    OPEN_REDIRECT = "Open Redirect"
    LDAP_INJECTION = "LDAP Injection"
    JWT_WEAKNESS = "JWT Security Weakness"
    MISSING_AUTH = "Missing Authentication"

@dataclass
class Vulnerability:
    file_path: str
    """Class for Vulnerability"""
    line_number: int
    vulnerability_type: VulnerabilityType
    severity: Severity
    description: str
    code_snippet: str
    recommendation: str
    owasp_category: str
    cwe_id: Optional[str] = None
    confidence: float = 1.0

class SecurityAuditor:
    def __init__(self, project_root: str):
        """Class for SecurityAuditor"""
        self.project_root = Path(project_root)
        self.vulnerabilities: List[Vulnerability] = []
        self.patterns = self._load_security_patterns()
        self.stats = {
            "total_files_scanned": 0,
            "total_lines_scanned": 0,
            "vulnerabilities_by_severity": {},
            "vulnerabilities_by_type": {},
            "security_hotspots": []
        }
    
    def _load_security_patterns(self) -> Dict[VulnerabilityType, List[Tuple[re.Pattern, Severity, str, str, str]]]:
        """Load security vulnerability patterns with CWE mappings"""
        return {
            VulnerabilityType.SQL_INJECTION: [
                (re.compile(r'f".*(?:SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER).*\{.*\}"', re.IGNORECASE), 
                 Severity.CRITICAL,
                 "SQL query constructed with f-string interpolation",
                 "Use parameterized queries with SQLAlchemy or prepared statements",
                 "CWE-89"),
                (re.compile(r'\.format\(.*\).*(?:SELECT|INSERT|UPDATE|DELETE)', re.IGNORECASE),
                 Severity.CRITICAL,
                 "SQL query constructed with .format()",
                 "Use parameterized queries instead of string formatting",
                 "CWE-89"),
                (re.compile(r'execute\(["\'].*%[sd].*["\'].*%', re.IGNORECASE),
                 Severity.HIGH,
                 "Potential SQL injection with string interpolation",
                 "Ensure proper parameterization with SQLAlchemy",
                 "CWE-89"),
                (re.compile(r'\.raw\(["\'][^"\']*(?:SELECT|INSERT|UPDATE|DELETE)[^"\']*["\'].*\+', re.IGNORECASE),
                 Severity.CRITICAL,
                 "Raw SQL with string concatenation",
                 "Use ORM methods or parameterized queries",
                 "CWE-89"),
                (re.compile(r'db\.execute\(.*\+.*request\.', re.IGNORECASE),
                 Severity.CRITICAL,
                 "Database query with direct user input concatenation",
                 "Never concatenate user input in queries",
                 "CWE-89"),
            ],
            
            VulnerabilityType.XSS: [
                (re.compile(r'\.innerHTML\s*=\s*[^\'"]'), 
                 Severity.HIGH,
                 "Direct innerHTML assignment without sanitization",
                 "Use textContent or sanitize with bleach/DOMPurify",
                 "CWE-79"),
                (re.compile(r'document\.write\([^)]*\)'),
                 Severity.HIGH,
                 "document.write usage can lead to XSS",
                 "Use safer DOM manipulation methods",
                 "CWE-79"),
                (re.compile(r'eval\([^)]*request\.'),
                 Severity.CRITICAL,
                 "eval() with user input is extremely dangerous",
                 "Never use eval with user input",
                 "CWE-95"),
                (re.compile(r'dangerouslySetInnerHTML.*request'),
                 Severity.HIGH,
                 "React dangerouslySetInnerHTML with user input",
                 "Sanitize content with DOMPurify before rendering",
                 "CWE-79"),
                (re.compile(r'render_template_string\(.*request\.'),
                 Severity.HIGH,
                 "Template injection vulnerability",
                 "Use render_template with proper escaping",
                 "CWE-1336"),
            ],
            
            VulnerabilityType.HARDCODED_SECRET: [
                (re.compile(r'(?:password|passwd|pwd|secret|api_key|apikey|token|auth)\s*=\s*["\'][A-Za-z0-9+/=]{10,}["\']', re.IGNORECASE),
                 Severity.CRITICAL,
                 "Hardcoded credential or secret detected",
                 "Use environment variables or Doppler secrets management",
                 "CWE-798"),
                (re.compile(r'(?:AWS|AZURE|GCP|GOOGLE)_[A-Z_]*(?:KEY|SECRET|TOKEN)\s*=\s*["\'][^"\']+["\']'),
                 Severity.CRITICAL,
                 "Cloud provider credentials hardcoded",
                 "Use IAM roles or environment variables",
                 "CWE-798"),
                (re.compile(r'(?:sk_live|pk_live|sk_test|pk_test)_[a-zA-Z0-9]+'),
                 Severity.CRITICAL,
                 "Stripe API key detected in code",
                 "Move to environment variables immediately",
                 "CWE-798"),
                (re.compile(r'mongodb://[^:]+:[^@]+@'),
                 Severity.CRITICAL,
                 "MongoDB connection string with credentials",
                 "Use environment variables for connection strings",
                 "CWE-798"),
                (re.compile(r'JWT_SECRET.*=.*["\'][^"\']+["\']'),
                 Severity.CRITICAL,
                 "JWT secret hardcoded",
                 "Generate secure random JWT secrets and store in environment",
                 "CWE-798"),
            ],
            
            VulnerabilityType.AUTH_BYPASS: [
                (re.compile(r'verify\s*=\s*False'),
                 Severity.HIGH,
                 "SSL/TLS verification disabled",
                 "Enable SSL/TLS verification in production",
                 "CWE-295"),
                (re.compile(r'@app\.(?:route|get|post|put|delete).*\n(?!.*(?:@require|Depends|get_current))'),
                 Severity.HIGH,
                 "Endpoint without authentication check",
                 "Add authentication requirement with Depends(get_current_active_user)",
                 "CWE-306"),
                (re.compile(r'if\s+.*==\s*["\'](?:admin|root|superuser)["\']'),
                 Severity.MEDIUM,
                 "Hardcoded privilege check",
                 "Use proper RBAC with database roles",
                 "CWE-285"),
                (re.compile(r'auto_error\s*=\s*False'),
                 Severity.MEDIUM,
                 "Authentication auto_error disabled",
                 "Enable auto_error for proper 401 responses",
                 "CWE-287"),
            ],
            
            VulnerabilityType.INSECURE_RANDOM: [
                (re.compile(r'random\.(?:random|randint|choice)\([^)]*\).*(?:token|session|password|key)'),
                 Severity.HIGH,
                 "Insecure random for security-critical values",
                 "Use secrets module for cryptographic randomness",
                 "CWE-330"),
                (re.compile(r'uuid\.uuid1\(\)'),
                 Severity.MEDIUM,
                 "UUID1 may leak MAC address",
                 "Use uuid4() for random UUIDs",
                 "CWE-330"),
                (re.compile(r'random\.seed\('),
                 Severity.HIGH,
                 "Fixed random seed makes values predictable",
                 "Remove seed or use secrets module",
                 "CWE-335"),
            ],
            
            VulnerabilityType.PATH_TRAVERSAL: [
                (re.compile(r'open\([^,)]*request\.[^,)]*\)'),
                 Severity.HIGH,
                 "File path from user input",
                 "Validate and sanitize file paths with pathlib",
                 "CWE-22"),
                (re.compile(r'\.\.\/|\.\.\\\\'),
                 Severity.HIGH,
                 "Path traversal sequence detected",
                 "Use os.path.join and validate paths",
                 "CWE-22"),
                (re.compile(r'send_file\([^)]+request\.'),
                 Severity.HIGH,
                 "send_file with user input",
                 "Validate paths against whitelist",
                 "CWE-22"),
            ],
            
            VulnerabilityType.WEAK_CRYPTO: [
                (re.compile(r'hashlib\.(?:md5|sha1)\('),
                 Severity.HIGH,
                 "Weak hashing algorithm for security",
                 "Use SHA-256 minimum, bcrypt for passwords",
                 "CWE-327"),
                (re.compile(r'(?:DES|3DES|RC4)'),
                 Severity.HIGH,
                 "Weak encryption algorithm",
                 "Use AES-256-GCM for encryption",
                 "CWE-327"),
                (re.compile(r'bcrypt.*rounds\s*=\s*[1-9]\b'),
                 Severity.MEDIUM,
                 "Weak bcrypt cost factor",
                 "Use at least 12 rounds for bcrypt",
                 "CWE-916"),
                (re.compile(r'ALGORITHM\s*=\s*["\']HS256["\']'),
                 Severity.MEDIUM,
                 "JWT using symmetric algorithm",
                 "Consider RS256 for better security",
                 "CWE-327"),
            ],
            
            VulnerabilityType.CORS_MISCONFIGURATION: [
                (re.compile(r'allow_origins\s*=\s*\[["\']?\*["\']?\]'),
                 Severity.HIGH,
                 "CORS allows all origins",
                 "Restrict CORS to specific trusted domains",
                 "CWE-346"),
                (re.compile(r'Access-Control-Allow-Origin.*\*'),
                 Severity.HIGH,
                 "Wildcard CORS header",
                 "Specify allowed origins explicitly",
                 "CWE-346"),
                (re.compile(r'allow_credentials\s*=\s*True.*allow_origins.*\*'),
                 Severity.CRITICAL,
                 "Credentials allowed with wildcard origin",
                 "Never combine credentials with wildcard origins",
                 "CWE-346"),
            ],
            
            VulnerabilityType.INPUT_VALIDATION: [
                (re.compile(r'request\.(?:args|form|json|query_params)\[["\'][^"\']+["\']\]'),
                 Severity.MEDIUM,
                 "Direct request data access without validation",
                 "Use Pydantic models for input validation",
                 "CWE-20"),
                (re.compile(r'int\(request\.'),
                 Severity.MEDIUM,
                 "Type casting without error handling",
                 "Add try-except blocks and validation",
                 "CWE-20"),
                (re.compile(r'pickle\.loads?\('),
                 Severity.CRITICAL,
                 "Pickle deserialization of untrusted data",
                 "Use JSON or other safe serialization formats",
                 "CWE-502"),
                (re.compile(r'yaml\.load\([^,)]*\)(?!.*Loader)'),
                 Severity.HIGH,
                 "Unsafe YAML loading",
                 "Use yaml.safe_load() instead",
                 "CWE-502"),
            ],
            
            VulnerabilityType.SESSION_MANAGEMENT: [
                (re.compile(r'session\[.*\]\s*=.*(?:user|password|token)'),
                 Severity.MEDIUM,
                 "Sensitive data stored in session",
                 "Store only user ID in session, fetch data from database",
                 "CWE-384"),
                (re.compile(r'expire.*=.*\d+.*#.*days'),
                 Severity.LOW,
                 "Long session expiry time",
                 "Use shorter session expiry for security",
                 "CWE-613"),
            ],
            
            VulnerabilityType.FILE_UPLOAD: [
                (re.compile(r'save\([^)]*filename\s*=\s*[^)]*request'),
                 Severity.HIGH,
                 "File saved with user-provided filename",
                 "Generate safe UUIDs for filenames",
                 "CWE-434"),
                (re.compile(r'UPLOAD.*EXTENSIONS.*\*'),
                 Severity.HIGH,
                 "All file extensions allowed",
                 "Whitelist specific safe extensions",
                 "CWE-434"),
                (re.compile(r'MAX_CONTENT_LENGTH.*>.*10.*\*.*1024.*\*.*1024'),
                 Severity.MEDIUM,
                 "Large file upload limit",
                 "Restrict file size to prevent DoS",
                 "CWE-400"),
            ],
            
            VulnerabilityType.SSRF: [
                (re.compile(r'requests\.(?:get|post)\([^)]*request\.'),
                 Severity.HIGH,
                 "HTTP request with user-controlled URL",
                 "Validate URLs against whitelist",
                 "CWE-918"),
                (re.compile(r'urllib.*urlopen\([^)]*request'),
                 Severity.HIGH,
                 "URL fetch with user input",
                 "Implement SSRF protection with URL validation",
                 "CWE-918"),
            ],
            
            VulnerabilityType.LOGGING_ISSUE: [
                (re.compile(r'logger\.(?:info|debug)\(.*password'),
                 Severity.HIGH,
                 "Password logged in plaintext",
                 "Never log passwords or sensitive data",
                 "CWE-532"),
                (re.compile(r'print\(.*(?:token|key|secret)'),
                 Severity.MEDIUM,
                 "Sensitive data in print statement",
                 "Remove debug print statements",
                 "CWE-532"),
            ],
        }
    
    def scan_file(self, file_path: Path) -> List[Vulnerability]:
        """Scan a single file for vulnerabilities"""
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.splitlines()
                self.stats["total_lines_scanned"] += len(lines)
                
                # Pattern-based scanning
                for line_num, line in enumerate(lines, 1):
                    for vuln_type, patterns in self.patterns.items():
                        for pattern, severity, description, recommendation, cwe in patterns:
                            if pattern.search(line):
                                # Get context (3 lines before and after)
                                start = max(0, line_num - 4)
                                end = min(len(lines), line_num + 3)
                                context = '\n'.join(lines[start:end])
                                
                                vuln = Vulnerability(
                                    file_path=str(file_path.relative_to(self.project_root)),
                                    line_number=line_num,
                                    vulnerability_type=vuln_type,
                                    severity=severity,
                                    description=description,
                                    code_snippet=context[:500],
                                    recommendation=recommendation,
                                    owasp_category=self._get_owasp_category(vuln_type),
                                    cwe_id=cwe,
                                    confidence=0.9
                                )
                                vulnerabilities.append(vuln)
                
                # Additional Python-specific checks
                if file_path.suffix == '.py':
                    vulnerabilities.extend(self._scan_python_ast(file_path, content))
        
        except Exception as e:
            print(f"Error scanning {file_path}: {e}")
        
        return vulnerabilities
    
    def _scan_python_ast(self, file_path: Path, content: str) -> List[Vulnerability]:
        """Advanced Python AST-based vulnerability scanning"""
        vulnerabilities = []
        try:
            tree = ast.parse(content)
            
            # Check for missing authentication on routes
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if it's a route handler
                    has_route_decorator = any(
                        isinstance(d, ast.Call) and 
                        hasattr(d.func, 'attr') and 
                        d.func.attr in ['route', 'get', 'post', 'put', 'delete', 'patch']
                        for d in node.decorator_list if isinstance(d, ast.Call)
                    )
                    
                    if has_route_decorator:
                        # Check for authentication dependency
                        has_auth = any(
                            'get_current' in ast.unparse(arg) or 'Depends' in ast.unparse(arg)
                            for arg in node.args.args
                        ) if hasattr(ast, 'unparse') else False
                        
                        if not has_auth and not any(exempt in node.name for exempt in ['health', 'login', 'register', 'docs']):
                            vulnerabilities.append(Vulnerability(
                                file_path=str(file_path.relative_to(self.project_root)),
                                line_number=node.lineno,
                                vulnerability_type=VulnerabilityType.MISSING_AUTH,
                                severity=Severity.HIGH,
                                description=f"Route handler '{node.name}' lacks authentication",
                                code_snippet=f"Function: {node.name}",
                                recommendation="Add Depends(get_current_active_user) parameter",
                                owasp_category="A07:2021 - Identification and Authentication Failures",
                                cwe_id="CWE-306",
                                confidence=0.8
                            ))
        except:
            pass  # AST parsing failed, skip advanced checks
        
        return vulnerabilities
    
    def _get_owasp_category(self, vuln_type: VulnerabilityType) -> str:
        """Map vulnerability types to OWASP Top 10 2021 categories"""
        mapping = {
            VulnerabilityType.SQL_INJECTION: "A03:2021 - Injection",
            VulnerabilityType.XSS: "A03:2021 - Injection",
            VulnerabilityType.AUTH_BYPASS: "A07:2021 - Identification and Authentication Failures",
            VulnerabilityType.HARDCODED_SECRET: "A02:2021 - Cryptographic Failures",
            VulnerabilityType.INSECURE_RANDOM: "A02:2021 - Cryptographic Failures",
            VulnerabilityType.PATH_TRAVERSAL: "A01:2021 - Broken Access Control",
            VulnerabilityType.XXE: "A05:2021 - Security Misconfiguration",
            VulnerabilityType.SSRF: "A10:2021 - Server-Side Request Forgery",
            VulnerabilityType.WEAK_CRYPTO: "A02:2021 - Cryptographic Failures",
            VulnerabilityType.MISSING_HEADERS: "A05:2021 - Security Misconfiguration",
            VulnerabilityType.CORS_MISCONFIGURATION: "A05:2021 - Security Misconfiguration",
            VulnerabilityType.RATE_LIMITING: "A04:2021 - Insecure Design",
            VulnerabilityType.INPUT_VALIDATION: "A03:2021 - Injection",
            VulnerabilityType.SESSION_MANAGEMENT: "A07:2021 - Identification and Authentication Failures",
            VulnerabilityType.INSECURE_DESERIALIZATION: "A08:2021 - Software and Data Integrity Failures",
            VulnerabilityType.LOGGING_ISSUE: "A09:2021 - Security Logging and Monitoring Failures",
            VulnerabilityType.FILE_UPLOAD: "A01:2021 - Broken Access Control",
            VulnerabilityType.CSRF: "A01:2021 - Broken Access Control",
            VulnerabilityType.OPEN_REDIRECT: "A01:2021 - Broken Access Control",
            VulnerabilityType.LDAP_INJECTION: "A03:2021 - Injection",
            VulnerabilityType.JWT_WEAKNESS: "A02:2021 - Cryptographic Failures",
            VulnerabilityType.MISSING_AUTH: "A07:2021 - Identification and Authentication Failures",
        }
        return mapping.get(vuln_type, "Unknown")
    
    def scan_directory(self, directory: Path = None) -> None:
        """Scan entire directory for vulnerabilities"""
        if directory is None:
            directory = self.project_root
        
        # Define file extensions to scan
        extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.html', '.sql', '.yaml', '.yml', '.json', '.env']
        
        # Directories to skip
        skip_dirs = {'node_modules', 'venv', 'env', '.git', '__pycache__', 'build', 'dist', '.pytest_cache', '.venv', 'venv_linux'}
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and (file_path.suffix in extensions or file_path.name == '.env'):
                # Skip files in ignored directories
                if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                    continue
                
                self.stats["total_files_scanned"] += 1
                vulnerabilities = self.scan_file(file_path)
                self.vulnerabilities.extend(vulnerabilities)
    
    def identify_security_hotspots(self) -> List[Dict[str, Any]]:
        """Identify security hotspots that need review"""
        hotspots = []
        
        # Group vulnerabilities by file
        file_vulns = {}
        for vuln in self.vulnerabilities:
            if vuln.file_path not in file_vulns:
                file_vulns[vuln.file_path] = []
            file_vulns[vuln.file_path].append(vuln)
        
        # Identify files with multiple vulnerabilities
        for file_path, vulns in file_vulns.items():
            if len(vulns) >= 3:
                critical_count = sum(1 for v in vulns if v.severity == Severity.CRITICAL)
                high_count = sum(1 for v in vulns if v.severity == Severity.HIGH)
                
                hotspots.append({
                    "file": file_path,
                    "total_issues": len(vulns),
                    "critical": critical_count,
                    "high": high_count,
                    "risk_score": critical_count * 10 + high_count * 5 + len(vulns),
                    "top_issues": [v.vulnerability_type.value for v in vulns[:3]]
                })
        
        # Sort by risk score
        hotspots.sort(key=lambda x: x["risk_score"], reverse=True)
        self.stats["security_hotspots"] = hotspots[:10]  # Top 10 hotspots
        
        return hotspots
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive security audit report"""
        # Update statistics
        for vuln in self.vulnerabilities:
            severity = vuln.severity.value
            vuln_type = vuln.vulnerability_type.value
            
            self.stats["vulnerabilities_by_severity"][severity] = \
                self.stats["vulnerabilities_by_severity"].get(severity, 0) + 1
            
            self.stats["vulnerabilities_by_type"][vuln_type] = \
                self.stats["vulnerabilities_by_type"].get(vuln_type, 0) + 1
        
        # Sort vulnerabilities by severity
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
            Severity.INFO: 4
        }
        
        sorted_vulns = sorted(self.vulnerabilities, key=lambda v: (severity_order[v.severity], v.file_path))
        
        # Identify security hotspots
        self.identify_security_hotspots()
        
        report = {
            "scan_date": datetime.now().isoformat(),
            "project_root": str(self.project_root),
            "statistics": self.stats,
            "total_vulnerabilities": len(self.vulnerabilities),
            "vulnerabilities": [asdict(v) for v in sorted_vulns],
            "owasp_coverage": self._get_owasp_coverage(),
            "security_score": self._calculate_security_score(),
            "remediation_priority": self._get_remediation_priority(),
            "compliance_status": self._check_compliance_status()
        }
        
        return report
    
    def _get_owasp_coverage(self) -> Dict[str, int]:
        """Get OWASP Top 10 2021 coverage"""
        coverage = {}
        for vuln in self.vulnerabilities:
            category = vuln.owasp_category
            coverage[category] = coverage.get(category, 0) + 1
        return dict(sorted(coverage.items(), key=lambda x: x[1], reverse=True))
    
    def _calculate_security_score(self) -> str:
        """Calculate security score based on vulnerabilities"""
        if not self.vulnerabilities:
            return "A"
        
        critical_count = self.stats["vulnerabilities_by_severity"].get("CRITICAL", 0)
        high_count = self.stats["vulnerabilities_by_severity"].get("HIGH", 0)
        medium_count = self.stats["vulnerabilities_by_severity"].get("MEDIUM", 0)
        
        if critical_count > 0:
            return "E"  # Worst - Critical vulnerabilities present
        elif high_count > 10:
            return "D"  # Many high vulnerabilities
        elif high_count > 5:
            return "C"  # Some high vulnerabilities
        elif medium_count > 20:
            return "C"  # Many medium vulnerabilities
        elif medium_count > 10:
            return "B"  # Some medium vulnerabilities
        else:
            return "B"  # Good security posture
    
    def _get_remediation_priority(self) -> List[Dict[str, Any]]:
        """Get prioritized list of remediation tasks"""
        priority_tasks = []
        
        # Group by vulnerability type and severity
        type_severity_groups = {}
        for vuln in self.vulnerabilities:
            key = (vuln.vulnerability_type, vuln.severity)
            if key not in type_severity_groups:
                type_severity_groups[key] = []
            type_severity_groups[key].append(vuln)
        
        # Create priority tasks
        for (vuln_type, severity), vulns in type_severity_groups.items():
            if severity in [Severity.CRITICAL, Severity.HIGH]:
                priority_tasks.append({
                    "type": vuln_type.value,
                    "severity": severity.value,
                    "count": len(vulns),
                    "estimated_effort": self._estimate_effort(vuln_type, len(vulns)),
                    "files_affected": list(set(v.file_path for v in vulns))[:5],  # Top 5 files
                    "recommendation": vulns[0].recommendation
                })
        
        # Sort by severity and count
        priority_tasks.sort(key=lambda x: (0 if x["severity"] == "CRITICAL" else 1, -x["count"]))
        
        return priority_tasks[:20]  # Top 20 priority tasks
    
    def _estimate_effort(self, vuln_type: VulnerabilityType, count: int) -> str:
        """Estimate remediation effort"""
        effort_map = {
            VulnerabilityType.HARDCODED_SECRET: "Low",
            VulnerabilityType.MISSING_HEADERS: "Low",
            VulnerabilityType.WEAK_CRYPTO: "Medium",
            VulnerabilityType.SQL_INJECTION: "High",
            VulnerabilityType.XSS: "Medium",
            VulnerabilityType.AUTH_BYPASS: "High",
            VulnerabilityType.INPUT_VALIDATION: "Medium",
        }
        
        base_effort = effort_map.get(vuln_type, "Medium")
        
        if count > 10:
            if base_effort == "Low":
                return "Medium"
            elif base_effort == "Medium":
                return "High"
        
        return base_effort
    
    def _check_compliance_status(self) -> Dict[str, bool]:
        """Check compliance with various standards"""
        critical_count = self.stats["vulnerabilities_by_severity"].get("CRITICAL", 0)
        high_count = self.stats["vulnerabilities_by_severity"].get("HIGH", 0)
        
        return {
            "OWASP_Top_10": critical_count == 0 and high_count < 5,
            "PCI_DSS": critical_count == 0 and high_count == 0,
            "GDPR": not any(v.vulnerability_type in [
                VulnerabilityType.LOGGING_ISSUE,
                VulnerabilityType.WEAK_CRYPTO,
                VulnerabilityType.HARDCODED_SECRET
            ] for v in self.vulnerabilities if v.severity in [Severity.CRITICAL, Severity.HIGH]),
            "SOC2": critical_count == 0 and high_count < 3,
            "ISO_27001": self._calculate_security_score() in ["A", "B"]
        }
    
    def print_summary(self, report: Dict[str, Any]) -> None:
        """Print detailed summary of findings"""
        print("\n" + "="*80)
        print("🔒 SECURITY AUDIT REPORT - RuleIQ")
        print("="*80)
        print(f"📅 Scan Date: {report['scan_date']}")
        print(f"📁 Files Scanned: {self.stats['total_files_scanned']}")
        print(f"📝 Lines Scanned: {self.stats['total_lines_scanned']:,}")
        print(f"⚠️  Total Vulnerabilities: {report['total_vulnerabilities']}")
        print(f"📊 Security Score: {report['security_score']} ", end="")
        
        score_emoji = {"A": "🟢", "B": "🟡", "C": "🟠", "D": "🔴", "E": "🚨"}
        print(score_emoji.get(report['security_score'], "❓"))
        
        print("\n" + "-"*40)
        print("🎯 VULNERABILITIES BY SEVERITY:")
        print("-"*40)
        for severity in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]:
            count = self.stats["vulnerabilities_by_severity"].get(severity.value, 0)
            if count > 0:
                severity_emoji = {
                    "CRITICAL": "🚨",
                    "HIGH": "🔴",
                    "MEDIUM": "🟠",
                    "LOW": "🟡",
                    "INFO": "ℹ️"
                }
                print(f"{severity_emoji.get(severity.value, '')} {severity.value:12} : {count:4} issues")
        
        print("\n" + "-"*40)
        print("📊 TOP VULNERABILITY TYPES:")
        print("-"*40)
        sorted_types = sorted(self.stats["vulnerabilities_by_type"].items(), 
                            key=lambda x: x[1], reverse=True)[:10]
        for vuln_type, count in sorted_types:
            print(f"  {vuln_type:35} : {count:4} issues")
        
        print("\n" + "-"*40)
        print("🎯 OWASP TOP 10 (2021) COVERAGE:")
        print("-"*40)
        for category, count in report["owasp_coverage"].items():
            print(f"  {category:45} : {count:4} issues")
        
        # Print security hotspots
        if self.stats.get("security_hotspots"):
            print("\n" + "-"*40)
            print("🔥 SECURITY HOTSPOTS (Files with most issues):")
            print("-"*40)
            for i, hotspot in enumerate(self.stats["security_hotspots"][:5], 1):
                print(f"\n  {i}. {hotspot['file']}")
                print(f"     Total: {hotspot['total_issues']} | Critical: {hotspot['critical']} | High: {hotspot['high']}")
                print(f"     Top Issues: {', '.join(hotspot['top_issues'])}")
        
        # Print compliance status
        print("\n" + "-"*40)
        print("✅ COMPLIANCE STATUS:")
        print("-"*40)
        for standard, compliant in report["compliance_status"].items():
            status = "✅ Compliant" if compliant else "❌ Non-Compliant"
            print(f"  {standard:15} : {status}")
        
        # Print critical and high priority issues
        critical_and_high = [v for v in self.vulnerabilities 
                            if v.severity in [Severity.CRITICAL, Severity.HIGH]]
        
        if critical_and_high:
            print("\n" + "="*80)
            print("🚨 CRITICAL AND HIGH PRIORITY ISSUES (Top 15):")
            print("="*80)
            for i, vuln in enumerate(critical_and_high[:15], 1):
                print(f"\n{i}. [{vuln.severity.value}] {vuln.vulnerability_type.value}")
                print(f"   📁 File: {vuln.file_path}:{vuln.line_number}")
                print(f"   📝 Description: {vuln.description}")
                print(f"   💡 Fix: {vuln.recommendation}")
                print(f"   🏷️  OWASP: {vuln.owasp_category}")
                if vuln.cwe_id:
                    print(f"   🔖 CWE: {vuln.cwe_id}")
        
        # Print remediation priority
        print("\n" + "="*80)
        print("🔧 REMEDIATION PRIORITY (Top 10):")
        print("="*80)
        for i, task in enumerate(report["remediation_priority"][:10], 1):
            print(f"\n{i}. {task['type']} ({task['count']} issues)")
            print(f"   Severity: {task['severity']} | Effort: {task['estimated_effort']}")
            print(f"   Fix: {task['recommendation']}")
            print(f"   Files: {', '.join(task['files_affected'][:3])}{'...' if len(task['files_affected']) > 3 else ''}")

def main():
    # Get project root
    """Main"""
    project_root = Path(__file__).parent.parent
    
    print(f"🔍 Starting security audit of {project_root}")
    print("⏳ This may take a few minutes...")
    
    # Create auditor and run scan
    auditor = SecurityAuditor(str(project_root))
    auditor.scan_directory()
    
    # Generate and save report
    report = auditor.generate_report()
    
    # Save detailed JSON report
    report_path = project_root / "security_audit_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n💾 Detailed report saved to: {report_path}")
    
    # Save prioritized fix list
    fix_list_path = project_root / "security_fixes_priority.json"
    fix_list = {
        "generated": datetime.now().isoformat(),
        "total_issues": report["total_vulnerabilities"],
        "security_score": report["security_score"],
        "priority_fixes": report["remediation_priority"],
        "hotspots": auditor.stats.get("security_hotspots", [])
    }
    with open(fix_list_path, 'w') as f:
        json.dump(fix_list, f, indent=2)
    
    print(f"📋 Priority fix list saved to: {fix_list_path}")
    
    # Print summary
    auditor.print_summary(report)
    
    # Print final recommendation
    print("\n" + "="*80)
    print("📋 RECOMMENDED NEXT STEPS:")
    print("="*80)
    print("1. Fix all CRITICAL vulnerabilities immediately")
    print("2. Address HIGH severity issues within 24 hours")
    print("3. Review and fix security hotspots")
    print("4. Implement security headers and CORS properly")
    print("5. Replace hardcoded secrets with environment variables")
    print("6. Add input validation using Pydantic models")
    print("7. Enable rate limiting on all endpoints")
    print("8. Review and fix all authentication gaps")
    print("9. Run this audit again after fixes")
    print("10. Set up continuous security scanning in CI/CD")
    
    # Exit with appropriate code
    if report["security_score"] in ["D", "E"]:
        print("\n❌ Build failed due to critical security issues")
        sys.exit(1)
    else:
        print("\n✅ Security audit completed")
        sys.exit(0)

if __name__ == "__main__":
    main()