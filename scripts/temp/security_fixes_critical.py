#!/usr/bin/env python3
"""
Critical Security Fixes Implementation Script
This script applies critical security fixes to the RuleIQ codebase
Run this to fix the most critical vulnerabilities immediately
"""

import os
import re
import sys
import json
import shutil
from pathlib import Path
from typing import List, Tuple, Dict, Any
from datetime import datetime

class CriticalSecurityFixer:
    """Apply critical security fixes to the codebase"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.fixes_applied = []
        self.backup_dir = self.project_root / ".security_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def backup_file(self, file_path: Path) -> None:
        """Create backup of file before modification"""
        if not file_path.exists():
            return
            
        relative_path = file_path.relative_to(self.project_root)
        backup_path = self.backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        
    def fix_cors_configuration(self) -> bool:
        """Fix CORS misconfiguration in main.py"""
        main_file = self.project_root / "main.py"
        
        if not main_file.exists():
            print("❌ main.py not found")
            return False
            
        self.backup_file(main_file)
        
        with open(main_file, 'r') as f:
            content = f.read()
        
        # Fix CORS allow_methods from ['*'] to specific methods
        old_cors = r"allow_methods=\['?\*'?\]"
        new_cors = 'allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]'
        
        content = re.sub(old_cors, new_cors, content)
        
        # Fix CORS allow_headers from ['*'] to specific headers
        old_headers = r"allow_headers=\['?\*'?\]"
        new_headers = 'allow_headers=["Authorization", "Content-Type", "Accept", "Origin", "X-Requested-With", "X-Request-ID"]'
        
        content = re.sub(old_headers, new_headers, content)
        
        # Ensure CORS origins are from settings, not wildcards
        if "allow_origins=['*']" in content or 'allow_origins=["*"]' in content:
            content = content.replace("allow_origins=['*']", "allow_origins=settings.cors_allowed_origins")
            content = content.replace('allow_origins=["*"]', "allow_origins=settings.cors_allowed_origins")
        
        with open(main_file, 'w') as f:
            f.write(content)
        
        self.fixes_applied.append("CORS configuration fixed in main.py")
        print("✅ Fixed CORS configuration")
        return True
    
    def fix_jwt_authentication(self) -> bool:
        """Fix JWT authentication issues"""
        auth_file = self.project_root / "api" / "dependencies" / "auth.py"
        
        if not auth_file.exists():
            print("❌ auth.py not found")
            return False
        
        self.backup_file(auth_file)
        
        with open(auth_file, 'r') as f:
            content = f.read()
        
        # Fix OAuth2PasswordBearer auto_error from False to True
        content = re.sub(
            r'OAuth2PasswordBearer\([^)]*auto_error\s*=\s*False[^)]*\)',
            lambda m: m.group(0).replace('auto_error=False', 'auto_error=True'),
            content
        )
        
        # Increase bcrypt rounds if it's less than 14
        content = re.sub(
            r"CryptContext\(schemes=\['bcrypt'\], deprecated='auto'\)",
            "CryptContext(schemes=['bcrypt'], deprecated='auto', bcrypt__rounds=14)",
            content
        )
        
        # Add JWT ID (jti) to tokens if not present
        if "'jti':" not in content and "jti" not in content:
            # Add jti generation in create_token function
            create_token_pattern = r"(to_encode\.update\(\{'exp': expire, 'type': token_type)"
            replacement = r"\1, 'jti': secrets.token_urlsafe(16)"
            content = re.sub(create_token_pattern, replacement, content)
        
        with open(auth_file, 'w') as f:
            f.write(content)
        
        self.fixes_applied.append("JWT authentication hardened in auth.py")
        print("✅ Fixed JWT authentication issues")
        return True
    
    def add_security_headers(self) -> bool:
        """Add security headers middleware to main.py"""
        main_file = self.project_root / "main.py"
        
        if not main_file.exists():
            print("❌ main.py not found")
            return False
        
        self.backup_file(main_file)
        
        with open(main_file, 'r') as f:
            content = f.read()
        
        # Check if enhanced security headers already imported
        if "security_headers_enhanced" in content:
            print("ℹ️  Enhanced security headers already configured")
            return True
        
        # Add import for enhanced security headers
        import_line = "from middleware.security_headers_enhanced import SecurityHeadersMiddleware as EnhancedSecurityHeaders\n"
        
        # Find where to add the import (after other middleware imports)
        import_pattern = r"(from middleware\.security_headers import SecurityHeadersMiddleware)"
        if re.search(import_pattern, content):
            content = re.sub(import_pattern, f"{import_line}\\1", content)
        else:
            # Add after other imports
            import_pattern = r"(from api\.middleware\..*?\n)"
            content = re.sub(import_pattern, f"\\1{import_line}", content, count=1)
        
        # Update the middleware usage to use enhanced version
        content = re.sub(
            r"app\.add_middleware\(SecurityHeadersMiddleware",
            "app.add_middleware(EnhancedSecurityHeaders",
            content
        )
        
        with open(main_file, 'w') as f:
            f.write(content)
        
        self.fixes_applied.append("Enhanced security headers added to main.py")
        print("✅ Added enhanced security headers")
        return True
    
    def fix_sql_injection_risks(self) -> bool:
        """Fix potential SQL injection vulnerabilities"""
        fixes_made = 0
        
        # Find all Python files
        for py_file in self.project_root.rglob("*.py"):
            # Skip test files and migrations
            if "test" in str(py_file) or "migration" in str(py_file) or ".venv" in str(py_file):
                continue
            
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                original_content = content
                
                # Look for f-strings in SQL queries
                sql_fstring_pattern = r'f".*(?:SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER).*\{[^}]+\}"'
                
                if re.search(sql_fstring_pattern, content, re.IGNORECASE):
                    # This needs manual review - add a comment
                    content = re.sub(
                        sql_fstring_pattern,
                        lambda m: f"# SECURITY: Review this SQL query for injection risk\n{m.group(0)}",
                        content,
                        flags=re.IGNORECASE
                    )
                    fixes_made += 1
                
                # Look for string formatting in SQL
                sql_format_pattern = r'\.format\([^)]+\).*(?:SELECT|INSERT|UPDATE|DELETE)'
                if re.search(sql_format_pattern, content, re.IGNORECASE):
                    # Add warning comment
                    content = re.sub(
                        sql_format_pattern,
                        lambda m: f"# SECURITY: Use parameterized queries instead\n{m.group(0)}",
                        content,
                        flags=re.IGNORECASE
                    )
                    fixes_made += 1
                
                if content != original_content:
                    self.backup_file(py_file)
                    with open(py_file, 'w') as f:
                        f.write(content)
                    
            except Exception as e:
                print(f"⚠️  Error processing {py_file}: {e}")
        
        if fixes_made > 0:
            self.fixes_applied.append(f"Added SQL injection warnings to {fixes_made} files")
            print(f"✅ Added SQL injection warnings to {fixes_made} files")
        
        return True
    
    def fix_settings_security(self) -> bool:
        """Fix security settings in config/settings.py"""
        settings_file = self.project_root / "config" / "settings.py"
        
        if not settings_file.exists():
            print("❌ settings.py not found")
            return False
        
        self.backup_file(settings_file)
        
        with open(settings_file, 'r') as f:
            content = f.read()
        
        # Update bcrypt rounds from 12 to 14
        content = re.sub(
            r"bcrypt_rounds:\s*int\s*=\s*Field\(default=12",
            "bcrypt_rounds: int = Field(default=14",
            content
        )
        
        # Update minimum password length from 8 to 10
        content = re.sub(
            r"password_min_length:\s*int\s*=\s*Field\(default=8",
            "password_min_length: int = Field(default=10",
            content
        )
        
        # Reduce JWT access token expiration from 30 to 15 minutes
        content = re.sub(
            r"jwt_access_token_expire_minutes:\s*int\s*=\s*Field\(default=30",
            "jwt_access_token_expire_minutes: int = Field(default=15",
            content
        )
        
        # Enable force_https in production
        content = re.sub(
            r"force_https:\s*bool\s*=\s*Field\(default=False",
            "force_https: bool = Field(default=True",
            content
        )
        
        # Enable secure_cookies in production
        content = re.sub(
            r"secure_cookies:\s*bool\s*=\s*Field\(default=False",
            "secure_cookies: bool = Field(default=True",
            content
        )
        
        with open(settings_file, 'w') as f:
            f.write(content)
        
        self.fixes_applied.append("Security settings updated in settings.py")
        print("✅ Updated security settings")
        return True
    
    def add_rate_limiting_to_endpoints(self) -> bool:
        """Add rate limiting to critical endpoints"""
        router_files = [
            self.project_root / "api" / "routers" / "auth.py",
            self.project_root / "api" / "routers" / "users.py",
            self.project_root / "api" / "routers" / "payment.py",
        ]
        
        fixes_made = 0
        
        for router_file in router_files:
            if not router_file.exists():
                continue
            
            self.backup_file(router_file)
            
            with open(router_file, 'r') as f:
                content = f.read()
            
            # Check if rate limiting already imported
            if "rate_limit" not in content:
                # Add import
                import_line = "from api.middleware.rate_limiter import rate_limit, auth_rate_limit\n"
                content = re.sub(
                    r"(from fastapi import.*?\n)",
                    f"\\1{import_line}",
                    content,
                    count=1
                )
            
            # Add rate limiting to POST endpoints without it
            post_pattern = r'@router\.post\([^)]+\)'
            matches = re.finditer(post_pattern, content)
            
            for match in matches:
                # Check if this endpoint already has dependencies
                if "dependencies=" not in match.group(0) and "Depends" not in match.group(0):
                    # Add rate limiting dependency
                    old_decorator = match.group(0)
                    new_decorator = old_decorator[:-1] + ", dependencies=[Depends(auth_rate_limit())])"
                    content = content.replace(old_decorator, new_decorator)
                    fixes_made += 1
            
            with open(router_file, 'w') as f:
                f.write(content)
        
        if fixes_made > 0:
            self.fixes_applied.append(f"Added rate limiting to {fixes_made} endpoints")
            print(f"✅ Added rate limiting to {fixes_made} endpoints")
        
        return True
    
    def fix_input_validation(self) -> bool:
        """Add input validation to endpoints missing it"""
        fixes_made = 0
        
        # Find router files
        routers_dir = self.project_root / "api" / "routers"
        
        for router_file in routers_dir.glob("*.py"):
            if "test" in router_file.name:
                continue
            
            try:
                with open(router_file, 'r') as f:
                    content = f.read()
                
                # Check for direct request access without validation
                direct_access_pattern = r'request\.(args|form|json|query_params)\[["\'][^"\']+["\']\]'
                
                if re.search(direct_access_pattern, content):
                    self.backup_file(router_file)
                    
                    # Add import for input sanitization
                    if "input_sanitization" not in content:
                        import_line = "from api.validators.input_sanitization import InputSanitizer, validate_input\n"
                        content = re.sub(
                            r"(from fastapi import.*?\n)",
                            f"\\1{import_line}",
                            content,
                            count=1
                        )
                    
                    # Add validation decorator to functions with direct access
                    content = re.sub(
                        r"(async def [^(]+\([^)]*request[^)]*\)[^:]*:)",
                        r"@validate_input(sanitize_sql=True)\n\1",
                        content
                    )
                    
                    with open(router_file, 'w') as f:
                        f.write(content)
                    
                    fixes_made += 1
                    
            except Exception as e:
                print(f"⚠️  Error processing {router_file}: {e}")
        
        if fixes_made > 0:
            self.fixes_applied.append(f"Added input validation to {fixes_made} files")
            print(f"✅ Added input validation to {fixes_made} files")
        
        return True
    
    def create_security_test_file(self) -> bool:
        """Create security test file to verify fixes"""
        test_file = self.project_root / "tests" / "test_security_fixes.py"
        
        test_content = '''"""
Security Tests to Verify Critical Fixes
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_cors_headers_restricted():
    """Test that CORS headers are properly restricted"""
    response = client.options("/api/v1/health")
    
    # Should not allow all origins
    assert response.headers.get("Access-Control-Allow-Origin") != "*"
    
    # Should not allow all methods
    allow_methods = response.headers.get("Access-Control-Allow-Methods", "")
    assert "*" not in allow_methods


def test_security_headers_present():
    """Test that security headers are present"""
    response = client.get("/api/v1/health")
    
    # Check for essential security headers
    assert "X-Content-Type-Options" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    
    assert "X-Frame-Options" in response.headers
    assert response.headers["X-Frame-Options"] in ["DENY", "SAMEORIGIN"]
    
    assert "X-XSS-Protection" in response.headers
    assert "Content-Security-Policy" in response.headers
    assert "Referrer-Policy" in response.headers


def test_rate_limiting_enforced():
    """Test that rate limiting is enforced on auth endpoints"""
    # Make multiple requests rapidly
    for i in range(10):
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "wrongpassword"}
        )
        
        # After 5 attempts, should get rate limited
        if i >= 5:
            assert response.status_code == 429  # Too Many Requests


def test_jwt_requires_authentication():
    """Test that protected endpoints require authentication"""
    # Try to access protected endpoint without token
    response = client.get("/api/v1/users/me")
    
    # Should get 401 Unauthorized
    assert response.status_code == 401


def test_input_validation_sql_injection():
    """Test that SQL injection attempts are blocked"""
    # Attempt SQL injection in search parameter
    response = client.get(
        "/api/v1/assessments",
        params={"search": "'; DROP TABLE users; --"}
    )
    
    # Should either sanitize or reject the input
    assert response.status_code in [400, 200]
    
    if response.status_code == 200:
        # If accepted, the dangerous SQL should be sanitized
        assert "DROP TABLE" not in str(response.json())


def test_password_requirements():
    """Test that strong password requirements are enforced"""
    # Try to register with weak password
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "weak"  # Too short and simple
        }
    )
    
    # Should reject weak password
    assert response.status_code == 400
    assert "password" in response.json()["detail"].lower()


def test_path_traversal_blocked():
    """Test that path traversal attempts are blocked"""
    # Attempt path traversal
    response = client.get("/api/v1/evidence/download?file=../../etc/passwd")
    
    # Should be blocked
    assert response.status_code in [400, 403, 404]


def test_xss_prevention():
    """Test that XSS attempts are sanitized"""
    # Attempt XSS in user input
    response = client.post(
        "/api/v1/policies",
        json={
            "name": "<script>alert('XSS')</script>",
            "content": "Test policy"
        },
        headers={"Authorization": "Bearer test_token"}
    )
    
    # Should either reject or sanitize
    if response.status_code == 200:
        assert "<script>" not in str(response.json())


def test_secure_headers_on_api_responses():
    """Test that API responses have secure cache headers"""
    response = client.get("/api/v1/health")
    
    # API responses should not be cached
    cache_control = response.headers.get("Cache-Control", "")
    assert "no-store" in cache_control or "no-cache" in cache_control


def test_authentication_timeout():
    """Test that tokens have reasonable expiration"""
    # This would require a valid login, but we check the configuration
    from config.settings import settings
    
    # Access tokens should expire in 15 minutes or less
    assert settings.jwt_access_token_expire_minutes <= 15
    
    # Refresh tokens should expire in reasonable time
    assert settings.jwt_refresh_token_expire_days <= 7
'''
        
        test_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        self.fixes_applied.append("Created security test file")
        print("✅ Created security test file")
        return True
    
    def generate_report(self) -> None:
        """Generate report of fixes applied"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "fixes_applied": self.fixes_applied,
            "backup_location": str(self.backup_dir),
            "total_fixes": len(self.fixes_applied),
            "status": "SUCCESS" if self.fixes_applied else "NO_FIXES_APPLIED"
        }
        
        report_file = self.project_root / "security_fixes_report.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📋 Security Fixes Report")
        print(f"{'='*50}")
        print(f"Timestamp: {report['timestamp']}")
        print(f"Total Fixes Applied: {report['total_fixes']}")
        print(f"Backup Location: {report['backup_location']}")
        print(f"\nFixes Applied:")
        for fix in self.fixes_applied:
            print(f"  ✓ {fix}")
        print(f"{'='*50}")
        print(f"Report saved to: {report_file}")


def main():
    """Main function to apply critical security fixes"""
    project_root = Path(__file__).parent
    
    print("🔒 Starting Critical Security Fixes")
    print(f"Project Root: {project_root}")
    print("="*50)
    
    fixer = CriticalSecurityFixer(str(project_root))
    
    # Apply fixes in order of priority
    fixes = [
        ("CORS Configuration", fixer.fix_cors_configuration),
        ("JWT Authentication", fixer.fix_jwt_authentication),
        ("Security Headers", fixer.add_security_headers),
        ("SQL Injection Prevention", fixer.fix_sql_injection_risks),
        ("Security Settings", fixer.fix_settings_security),
        ("Rate Limiting", fixer.add_rate_limiting_to_endpoints),
        ("Input Validation", fixer.fix_input_validation),
        ("Security Tests", fixer.create_security_test_file),
    ]
    
    for fix_name, fix_func in fixes:
        print(f"\n🔧 Applying: {fix_name}")
        try:
            fix_func()
        except Exception as e:
            print(f"❌ Error applying {fix_name}: {e}")
    
    # Generate report
    fixer.generate_report()
    
    print("\n✅ Critical security fixes applied!")
    print("⚠️  Please review the changes and run tests before deploying")
    print("📝 Run 'pytest tests/test_security_fixes.py' to verify fixes")


if __name__ == "__main__":
    main()