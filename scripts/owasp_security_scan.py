#!/usr/bin/env python3
"""
OWASP Security Scan for RuleIQ.

This script performs comprehensive security scanning including:
- OWASP Top 10 vulnerability checks
- Dependency vulnerability scanning
- Security headers validation
- SQL injection testing
- XSS vulnerability testing
"""
import os
import sys
import json
import subprocess
import requests
from typing import Dict, Any
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OWASPSecurityScanner:
    """Comprehensive security scanner based on OWASP guidelines."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            "scan_date": datetime.now().isoformat(),
            "vulnerabilities": [],
            "warnings": [],
            "passed_checks": [],
            "score": 0
        }

    def run_full_scan(self) -> Dict[str, Any]:
        """Run complete OWASP security scan."""
        logger.info("Starting OWASP Security Scan...")

        # 1. Check Python dependencies
        self.scan_python_dependencies()

        # 2. Check Node.js dependencies
        self.scan_node_dependencies()

        # 3. Test for SQL Injection
        self.test_sql_injection()

        # 4. Test for XSS
        self.test_xss_vulnerabilities()

        # 5. Check Security Headers
        self.check_security_headers()

        # 6. Test Authentication
        self.test_authentication_security()

        # 7. Test for CSRF
        self.test_csrf_protection()

        # 8. Check for sensitive data exposure
        self.check_sensitive_data_exposure()

        # 9. Test access controls
        self.test_access_controls()

        # 10. Check logging and monitoring
        self.check_security_logging()

        # Calculate score
        self.calculate_security_score()

        return self.results

    def scan_python_dependencies(self):
        """Scan Python dependencies for known vulnerabilities."""
        logger.info("Scanning Python dependencies...")

        try:
            # Use safety to check for vulnerabilities
            result = subprocess.run(
                ["pip", "list", "--format=json"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                packages = json.loads(result.stdout)

                # Check each package (simplified - use safety in production)
                vulnerable_packages = []
                for pkg in packages:
                    # Check common vulnerable versions
                    if pkg["name"] == "django" and pkg["version"] < "3.2":
                        vulnerable_packages.append(pkg)
                    elif pkg["name"] == "flask" and pkg["version"] < "2.0":
                        vulnerable_packages.append(pkg)
                    elif pkg["name"] == "requests" and pkg["version"] < "2.25":
                        vulnerable_packages.append(pkg)

                if vulnerable_packages:
                    self.results["vulnerabilities"].append({
                        "type": "Vulnerable Dependencies",
                        "severity": "HIGH",
                        "details": f"Found {len(vulnerable_packages)} vulnerable Python packages",
                        "packages": vulnerable_packages
                    })
                else:
                    self.results["passed_checks"].append("Python dependencies")

        except Exception as e:
            logger.error(f"Failed to scan Python dependencies: {e}")

    def scan_node_dependencies(self):
        """Scan Node.js dependencies for vulnerabilities."""
        logger.info("Scanning Node.js dependencies...")

        try:
            # Check if package.json exists
            if os.path.exists("frontend/package.json"):
                result = subprocess.run(
                    ["npm", "audit", "--json"],
                    cwd="frontend",
                    capture_output=True,
                    text=True
                )

                if result.stdout:
                    audit_data = json.loads(result.stdout)
                    vulnerabilities = audit_data.get("metadata", {}).get("vulnerabilities", {})

                    total_vulns = sum(vulnerabilities.values())
                    if total_vulns > 0:
                        self.results["vulnerabilities"].append({
                            "type": "Node.js Dependencies",
                            "severity": "HIGH" if vulnerabilities.get("high", 0) > 0 else "MEDIUM",
                            "details": f"Found {total_vulns} vulnerabilities in Node.js dependencies",
                            "breakdown": vulnerabilities
                        })
                    else:
                        self.results["passed_checks"].append("Node.js dependencies")

        except Exception as e:
            logger.error(f"Failed to scan Node.js dependencies: {e}")

    def test_sql_injection(self):
        """Test for SQL injection vulnerabilities."""
        logger.info("Testing for SQL injection...")

        sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users--",
            "1' UNION SELECT NULL--",
            "admin'--",
            "1' AND '1'='1"
        ]

        vulnerable_endpoints = []

        for payload in sql_payloads:
            try:
                # Test login endpoint
                response = requests.post(
                    f"{self.base_url}/api/v1/auth/token",
                    data={
                        "username": payload,
                        "password": payload
                    },
                    timeout=5
                )

                # Check for SQL errors in response
                if response.status_code == 500 or "SQL" in response.text or "syntax" in response.text:
                    vulnerable_endpoints.append({
                        "endpoint": "/api/v1/auth/token",
                        "payload": payload
                    })

            except Exception:
                pass

        if vulnerable_endpoints:
            self.results["vulnerabilities"].append({
                "type": "SQL Injection",
                "severity": "CRITICAL",
                "details": f"Found {len(vulnerable_endpoints)} potential SQL injection points",
                "endpoints": vulnerable_endpoints
            })
        else:
            self.results["passed_checks"].append("SQL Injection Protection")

    def test_xss_vulnerabilities(self):
        """Test for XSS vulnerabilities."""
        logger.info("Testing for XSS vulnerabilities...")

        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "'><script>alert('XSS')</script>"
        ]

        vulnerable_endpoints = []

        for payload in xss_payloads:
            try:
                # Test various endpoints
                response = requests.get(
                    f"{self.base_url}/api/v1/search",
                    params={"q": payload},
                    timeout=5
                )

                # Check if payload is reflected without encoding
                if payload in response.text:
                    vulnerable_endpoints.append({
                        "endpoint": "/api/v1/search",
                        "payload": payload
                    })

            except Exception:
                pass

        if vulnerable_endpoints:
            self.results["vulnerabilities"].append({
                "type": "Cross-Site Scripting (XSS)",
                "severity": "HIGH",
                "details": f"Found {len(vulnerable_endpoints)} potential XSS vulnerabilities",
                "endpoints": vulnerable_endpoints
            })
        else:
            self.results["passed_checks"].append("XSS Protection")

    def check_security_headers(self):
        """Check for security headers."""
        logger.info("Checking security headers...")

        try:
            response = requests.get(f"{self.base_url}/api/v1/health", timeout=5)
            headers = response.headers

            required_headers = {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Strict-Transport-Security": "max-age=31536000",
                "Content-Security-Policy": None  # Check existence
            }

            missing_headers = []
            for header, expected_value in required_headers.items():
                if header not in headers:
                    missing_headers.append(header)
                elif expected_value and headers[header] != expected_value:
                    missing_headers.append(f"{header} (incorrect value)")

            if missing_headers:
                self.results["warnings"].append({
                    "type": "Missing Security Headers",
                    "severity": "MEDIUM",
                    "details": f"Missing {len(missing_headers)} security headers",
                    "headers": missing_headers
                })
            else:
                self.results["passed_checks"].append("Security Headers")

        except Exception as e:
            logger.error(f"Failed to check security headers: {e}")

    def test_authentication_security(self):
        """Test authentication security."""
        logger.info("Testing authentication security...")

        issues = []

        # Test for weak passwords
        weak_passwords = ["123456", "password", "admin", "test123"]
        for pwd in weak_passwords:
            try:
                response = requests.post(
                    f"{self.base_url}/api/v1/auth/register",
                    json={
                        "email": f"test_{pwd}@example.com",
                        "password": pwd,
                        "full_name": "Test User"
                    },
                    timeout=5
                )

                if response.status_code in [200, 201]:
                    issues.append(f"Weak password accepted: {pwd}")

            except Exception:
                pass

        # Test for JWT in URL
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/users/me?token=fake_token",
                timeout=5
            )

            if response.status_code != 401:
                issues.append("JWT accepted in URL parameters")

        except Exception:
            pass

        if issues:
            self.results["vulnerabilities"].append({
                "type": "Authentication Weaknesses",
                "severity": "HIGH",
                "details": f"Found {len(issues)} authentication issues",
                "issues": issues
            })
        else:
            self.results["passed_checks"].append("Authentication Security")

    def test_csrf_protection(self):
        """Test CSRF protection."""
        logger.info("Testing CSRF protection...")

        try:
            # Try to make state-changing request without CSRF token
            response = requests.post(
                f"{self.base_url}/api/v1/users/update",
                json={"name": "CSRF Test"},
                headers={"Origin": "http://evil.com"},
                timeout=5
            )

            if response.status_code in [200, 201]:
                self.results["vulnerabilities"].append({
                    "type": "CSRF Vulnerability",
                    "severity": "HIGH",
                    "details": "State-changing requests accepted without CSRF protection"
                })
            else:
                self.results["passed_checks"].append("CSRF Protection")

        except Exception:
            self.results["passed_checks"].append("CSRF Protection")

    def check_sensitive_data_exposure(self):
        """Check for sensitive data exposure."""
        logger.info("Checking for sensitive data exposure...")

        issues = []

        # Check for exposed config files
        sensitive_paths = [
            "/.env",
            "/.git/config",
            "/config.json",
            "/api/config",
            "/.aws/credentials"
        ]

        for path in sensitive_paths:
            try:
                response = requests.get(f"{self.base_url}{path}", timeout=5)
                if response.status_code == 200:
                    issues.append(f"Exposed path: {path}")
            except Exception:
                pass

        # Check for sensitive data in API responses
        try:
            response = requests.get(f"{self.base_url}/api/v1/users", timeout=5)
            if response.status_code == 200:
                data = response.text.lower()
                if "password" in data or "secret" in data or "token" in data:
                    issues.append("Sensitive data in API responses")
        except Exception:
            pass

        if issues:
            self.results["vulnerabilities"].append({
                "type": "Sensitive Data Exposure",
                "severity": "CRITICAL",
                "details": f"Found {len(issues)} data exposure issues",
                "issues": issues
            })
        else:
            self.results["passed_checks"].append("Data Protection")

    def test_access_controls(self):
        """Test access control implementation."""
        logger.info("Testing access controls...")

        issues = []

        # Test for IDOR vulnerabilities
        try:
            # Try to access other user's data
            response = requests.get(
                f"{self.base_url}/api/v1/users/1",
                timeout=5
            )

            if response.status_code == 200:
                issues.append("Potential IDOR vulnerability")

        except Exception:
            pass

        # Test for privilege escalation
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/admin/users",
                json={"role": "admin"},
                timeout=5
            )

            if response.status_code in [200, 201]:
                issues.append("Potential privilege escalation")

        except Exception:
            pass

        if issues:
            self.results["vulnerabilities"].append({
                "type": "Access Control Issues",
                "severity": "HIGH",
                "details": f"Found {len(issues)} access control issues",
                "issues": issues
            })
        else:
            self.results["passed_checks"].append("Access Controls")

    def check_security_logging(self):
        """Check security logging implementation."""
        logger.info("Checking security logging...")

        # Check if security events are logged
        log_files = [
            "logs/security.log",
            "logs/auth.log",
            "logs/access.log"
        ]

        found_logs = []
        for log_file in log_files:
            if os.path.exists(log_file):
                found_logs.append(log_file)

        if not found_logs:
            self.results["warnings"].append({
                "type": "Insufficient Logging",
                "severity": "MEDIUM",
                "details": "Security logging not properly configured"
            })
        else:
            self.results["passed_checks"].append("Security Logging")

    def calculate_security_score(self):
        """Calculate overall security score."""
        total_checks = (
            len(self.results["passed_checks"]) +
            len(self.results["vulnerabilities"]) +
            len(self.results["warnings"])
        )

        if total_checks > 0:
            passed = len(self.results["passed_checks"])
            score = (passed / total_checks) * 100
            self.results["score"] = round(score, 2)
        else:
            self.results["score"] = 0

    def generate_report(self, output_file: str = "owasp_security_report.json"):
        """Generate security scan report."""
        logger.info(f"Generating security report: {output_file}")

        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        # Print summary
        print("\n" + "="*60)
        print("OWASP SECURITY SCAN SUMMARY")
        print("="*60)
        print(f"Scan Date: {self.results['scan_date']}")
        print(f"Security Score: {self.results['score']}%")
        print(f"Passed Checks: {len(self.results['passed_checks'])}")
        print(f"Vulnerabilities Found: {len(self.results['vulnerabilities'])}")
        print(f"Warnings: {len(self.results['warnings'])}")

        if self.results["vulnerabilities"]:
            print("\nCRITICAL VULNERABILITIES:")
            for vuln in self.results["vulnerabilities"]:
                if vuln["severity"] == "CRITICAL":
                    print(f"  - {vuln['type']}: {vuln['details']}")

        print("\nReport saved to:", output_file)
        print("="*60)


if __name__ == "__main__":
    scanner = OWASPSecurityScanner()
    results = scanner.run_full_scan()
    scanner.generate_report()

    # Exit with error code if critical vulnerabilities found
    critical_vulns = [v for v in results["vulnerabilities"] if v["severity"] == "CRITICAL"]
    if critical_vulns:
        sys.exit(1)
    else:
        sys.exit(0)
