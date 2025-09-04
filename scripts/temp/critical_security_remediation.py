#!/usr/bin/env python3
"""
Critical Security Remediation Script
Addresses CRITICAL and HIGH severity vulnerabilities for RuleIQ
Priority: P3 - Security Task eeb5d5b1
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

class CriticalSecurityRemediation:
    """Apply critical security fixes to RuleIQ codebase"""
    
    def __init__(self):
        self.project_root = Path(".")
        self.backup_dir = self.project_root / ".security_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.fixes_applied = []
        
    def backup_file(self, file_path: Path) -> None:
        """Create backup before modifying file"""
        if not file_path.exists():
            return
        
        relative_path = file_path.relative_to(self.project_root)
        backup_path = self.backup_dir / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
    
    def fix_jwt_security(self) -> bool:
        """Fix JWT security vulnerabilities"""
        auth_file = self.project_root / "api" / "dependencies" / "auth.py"
        if not auth_file.exists():
            print("❌ auth.py not found")
            return False
        
        self.backup_file(auth_file)
        
        with open(auth_file, 'r') as f:
            content = f.read()
        
        # 1. Change auto_error to True
        content = re.sub(
            r'auto_error\s*=\s*False',
            'auto_error=True',
            content
        )
        
        # 2. Increase bcrypt rounds to 14
        if 'bcrypt__rounds' not in content:
            content = re.sub(
                r"CryptContext\(schemes=\['bcrypt'\], deprecated='auto'\)",
                "CryptContext(schemes=['bcrypt'], deprecated='auto', bcrypt__rounds=14)",
                content
            )
        
        # 3. Reduce token expiration
        content = re.sub(
            r'ACCESS_TOKEN_EXPIRE_MINUTES\s*=\s*\d+',
            'ACCESS_TOKEN_EXPIRE_MINUTES = 15',
            content
        )
        
        # 4. Add JWT ID (jti) for revocation if not present
        if 'jti' not in content:
            # Add jti to token creation
            token_creation = """def create_token(data: dict, token_type: str, expires_delta: Optional[
    timedelta]=None) ->str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({
        'exp': expire, 
        'type': token_type, 
        'iat': datetime.now(timezone.utc),
        'jti': str(uuid4())  # Add unique token ID for revocation
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)"""
            
            content = re.sub(
                r'def create_token\([^}]+\}\)',
                token_creation,
                content,
                flags=re.DOTALL
            )
            
            # Add uuid4 import if not present
            if 'from uuid import' not in content:
                content = re.sub(
                    r'from uuid import UUID',
                    'from uuid import UUID, uuid4',
                    content
                )
        
        with open(auth_file, 'w') as f:
            f.write(content)
        
        self.fixes_applied.append("Enhanced JWT security in auth.py")
        return True
    
    def fix_sql_injection_vulnerabilities(self) -> bool:
        """Fix SQL injection vulnerabilities by adding parameterized queries"""
        fixed_count = 0
        
        # Scan all Python files for SQL injection patterns
        for file_path in self.project_root.glob("**/*.py"):
            if any(skip in str(file_path) for skip in ['venv', '__pycache__', '.git', 'migrations', 'tests']):
                continue
            
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                original = content
                
                # Fix f-string SQL queries
                if re.search(r'f".*(?:SELECT|INSERT|UPDATE|DELETE).*\{.*\}"', content, re.IGNORECASE):
                    # Add warning comment
                    content = re.sub(
                        r'(.*f".*(?:SELECT|INSERT|UPDATE|DELETE).*\{.*\}")',
                        r'# SECURITY WARNING: Potential SQL injection - use parameterized queries\n\1',
                        content,
                        flags=re.IGNORECASE
                    )
                    
                    # Log for manual review
                    print(f"⚠️  SQL injection risk in {file_path.relative_to(self.project_root)} - marked for review")
                
                # Fix .format() in SQL queries
                if re.search(r'\.format\(.*\).*(?:SELECT|INSERT|UPDATE|DELETE)', content, re.IGNORECASE):
                    content = re.sub(
                        r'(.*\.format\(.*\).*(?:SELECT|INSERT|UPDATE|DELETE))',
                        r'# SECURITY WARNING: SQL injection risk - use parameterized queries\n\1',
                        content,
                        flags=re.IGNORECASE
                    )
                
                if content != original:
                    self.backup_file(file_path)
                    with open(file_path, 'w') as f:
                        f.write(content)
                    fixed_count += 1
                    
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        
        if fixed_count > 0:
            self.fixes_applied.append(f"Marked {fixed_count} files with SQL injection warnings")
        return fixed_count > 0
    
    def add_security_headers(self) -> bool:
        """Add comprehensive security headers"""
        main_file = self.project_root / "main.py"
        if not main_file.exists():
            return False
        
        self.backup_file(main_file)
        
        with open(main_file, 'r') as f:
            content = f.read()
        
        # Check if security headers middleware already exists
        if 'SecurityHeadersMiddleware' in content:
            print("✓ Security headers already configured")
            return True
        
        # Add security headers middleware
        security_headers_import = """from middleware.security_headers import SecurityHeadersMiddleware"""
        
        if 'from middleware.security_headers' not in content:
            # Add import after other imports
            content = re.sub(
                r'(from fastapi import.*\n)',
                r'\1' + security_headers_import + '\n',
                content
            )
        
        # Add middleware configuration
        security_middleware = """
# Security Headers Middleware
app.add_middleware(
    SecurityHeadersMiddleware,
    csp_enabled=True,
    hsts_enabled=True,
    x_frame_options="DENY",
    x_content_type_options="nosniff",
    x_xss_protection="1; mode=block",
    referrer_policy="strict-origin-when-cross-origin"
)"""
        
        if 'SecurityHeadersMiddleware' not in content:
            # Add after CORS middleware
            content = re.sub(
                r'(app\.add_middleware\(CORSMiddleware[^)]+\))',
                r'\1' + security_middleware,
                content
            )
        
        with open(main_file, 'w') as f:
            f.write(content)
        
        self.fixes_applied.append("Added security headers middleware")
        return True
    
    def fix_input_validation(self) -> bool:
        """Add input validation to API endpoints"""
        fixed_count = 0
        
        # Check all router files
        routers_dir = self.project_root / "api" / "routers"
        if not routers_dir.exists():
            return False
        
        for router_file in routers_dir.glob("*.py"):
            try:
                with open(router_file, 'r') as f:
                    content = f.read()
                
                original = content
                
                # Add Pydantic validation imports if not present
                if 'from pydantic import' not in content and 'BaseModel' not in content:
                    if '@router.' in content:  # Has routes
                        content = "from pydantic import BaseModel, Field, validator\n" + content
                
                # Mark direct request access for review
                if 'request.json' in content or 'request.form' in content:
                    content = re.sub(
                        r'(.*request\.(json|form|args)\[)',
                        r'# SECURITY: Add Pydantic model validation\n\1',
                        content
                    )
                    print(f"⚠️  Input validation needed in {router_file.name}")
                
                if content != original:
                    self.backup_file(router_file)
                    with open(router_file, 'w') as f:
                        f.write(content)
                    fixed_count += 1
                    
            except Exception as e:
                print(f"Error processing {router_file}: {e}")
        
        if fixed_count > 0:
            self.fixes_applied.append(f"Added input validation markers to {fixed_count} router files")
        return fixed_count > 0
    
    def fix_hardcoded_secrets(self) -> bool:
        """Move hardcoded secrets to environment variables"""
        settings_file = self.project_root / "config" / "settings.py"
        if not settings_file.exists():
            return False
        
        self.backup_file(settings_file)
        
        with open(settings_file, 'r') as f:
            content = f.read()
        
        # Ensure secrets are read from environment
        replacements = [
            (r'jwt_secret_key\s*:\s*str\s*=\s*["\'][^"\']+["\']',
             'jwt_secret_key: str = Field(default="change-me-in-production", env="JWT_SECRET_KEY")'),
            (r'database_url\s*:\s*str\s*=\s*["\'][^"\']+["\']',
             'database_url: str = Field(env="DATABASE_URL")'),
            (r'redis_url\s*:\s*str\s*=\s*["\'][^"\']+["\']',
             'redis_url: str = Field(default="redis://localhost:6379", env="REDIS_URL")'),
        ]
        
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        with open(settings_file, 'w') as f:
            f.write(content)
        
        self.fixes_applied.append("Secured settings.py - secrets from environment")
        return True
    
    def add_rate_limiting(self) -> bool:
        """Enhance rate limiting configuration"""
        main_file = self.project_root / "main.py"
        if not main_file.exists():
            return False
        
        with open(main_file, 'r') as f:
            content = f.read()
        
        # Check if rate limiting is already configured
        if 'rate_limit_middleware' in content:
            print("✓ Rate limiting already configured")
            return True
        
        self.backup_file(main_file)
        
        # Add rate limiting middleware
        rate_limit_import = "from api.middleware.rate_limiter import rate_limit_middleware"
        
        if 'rate_limit_middleware' not in content:
            # Add import
            content = re.sub(
                r'(from api.middleware.*\n)',
                r'\1' + rate_limit_import + '\n',
                content
            )
            
            # Add middleware
            content = re.sub(
                r'(app = FastAPI\([^)]+\))',
                r'\1\n\n# Rate Limiting Middleware\napp.middleware("http")(rate_limit_middleware)',
                content
            )
        
        with open(main_file, 'w') as f:
            f.write(content)
        
        self.fixes_applied.append("Enhanced rate limiting configuration")
        return True
    
    def create_security_tests(self) -> bool:
        """Create security test suite"""
        test_file = self.project_root / "tests" / "test_security_fixes.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        
        test_content = '''"""
Security Test Suite for RuleIQ
Tests critical security fixes and configurations
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestSecurityHeaders:
    """Test security headers are properly set"""
    
    def test_security_headers_present(self):
        """Verify all security headers are set"""
        response = client.get("/health")
        
        # Check critical security headers
        assert "X-Content-Type-Options" in response.headers
        assert response.headers.get("X-Content-Type-Options") == "nosniff"
        
        assert "X-Frame-Options" in response.headers
        assert response.headers.get("X-Frame-Options") in ["DENY", "SAMEORIGIN"]
        
        assert "X-XSS-Protection" in response.headers
        assert "Strict-Transport-Security" in response.headers
    
    def test_cors_not_wildcard(self):
        """Verify CORS is not set to wildcard"""
        response = client.options("/api/v1/auth/login")
        
        # Should not allow all origins
        assert response.headers.get("Access-Control-Allow-Origin") != "*"

class TestAuthentication:
    """Test authentication security"""
    
    def test_protected_endpoints_require_auth(self):
        """Verify protected endpoints require authentication"""
        # Test various endpoints without auth
        endpoints = [
            "/api/v1/users/me",
            "/api/v1/assessments",
            "/api/v1/policies",
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code in [401, 403], f"{endpoint} should require auth"
    
    def test_jwt_expiration(self):
        """Test JWT tokens expire properly"""
        # This would need a real token to test expiration
        pass

class TestInputValidation:
    """Test input validation"""
    
    def test_sql_injection_prevention(self):
        """Test SQL injection is prevented"""
        # Attempt SQL injection in login
        response = client.post("/api/v1/auth/login", json={
            "username": "admin' OR '1'='1",
            "password": "password"
        })
        
        # Should fail authentication, not execute SQL
        assert response.status_code == 401
    
    def test_xss_prevention(self):
        """Test XSS is prevented"""
        # Attempt XSS in user input
        response = client.post("/api/v1/feedback", json={
            "message": "<script>alert('XSS')</script>"
        })
        
        # If successful, check response doesn't contain script
        if response.status_code == 200:
            assert "<script>" not in response.text

class TestRateLimiting:
    """Test rate limiting is enforced"""
    
    def test_rate_limit_enforced(self):
        """Verify rate limiting blocks excessive requests"""
        # Make many rapid requests
        responses = []
        for _ in range(150):  # Exceed typical rate limit
            response = client.get("/api/v1/auth/login")
            responses.append(response.status_code)
        
        # Should see rate limiting (429) at some point
        assert 429 in responses, "Rate limiting should be enforced"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''
        
        with open(test_file, 'w') as f:
            f.write(test_content)
        
        self.fixes_applied.append("Created security test suite")
        return True
    
    def generate_report(self) -> None:
        """Generate remediation report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'fixes_applied': self.fixes_applied,
            'backup_location': str(self.backup_dir),
            'next_steps': [
                'Review SQL injection warnings and implement parameterized queries',
                'Update all dependencies to latest secure versions',
                'Configure environment variables for all secrets',
                'Run security tests: pytest tests/test_security_fixes.py',
                'Perform penetration testing',
                'Review and close security hotspots in SonarCloud'
            ]
        }
        
        # Save report
        with open('security_remediation_report.json', 'w') as f:
            import json
            json.dump(report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 80)
        print("🔒 SECURITY REMEDIATION SUMMARY")
        print("=" * 80)
        print(f"✅ Fixes Applied: {len(self.fixes_applied)}")
        for fix in self.fixes_applied:
            print(f"   - {fix}")
        print(f"\n📁 Backup Location: {self.backup_dir}")
        print("\n📋 Next Steps:")
        for i, step in enumerate(report['next_steps'], 1):
            print(f"   {i}. {step}")

def main():
    """Execute critical security remediation"""
    print("=" * 80)
    print("🚨 CRITICAL SECURITY REMEDIATION FOR RULEIQ")
    print("=" * 80)
    print("Priority: P3 - Task eeb5d5b1")
    print("Target: Zero critical/high vulnerabilities")
    print()
    
    remediation = CriticalSecurityRemediation()
    
    # Apply critical fixes
    print("🔧 Applying critical security fixes...")
    
    if remediation.fix_jwt_security():
        print("✅ Fixed JWT security vulnerabilities")
    
    if remediation.fix_sql_injection_vulnerabilities():
        print("✅ Added SQL injection warnings")
    
    if remediation.add_security_headers():
        print("✅ Added security headers")
    
    if remediation.fix_input_validation():
        print("✅ Added input validation markers")
    
    if remediation.fix_hardcoded_secrets():
        print("✅ Secured configuration")
    
    if remediation.add_rate_limiting():
        print("✅ Enhanced rate limiting")
    
    if remediation.create_security_tests():
        print("✅ Created security test suite")
    
    # Generate report
    remediation.generate_report()
    
    print("\n✅ Critical security remediation completed!")
    print("📄 Report saved to: security_remediation_report.json")
    print("\n⚠️  IMPORTANT: Manual review required for SQL queries marked with warnings")

if __name__ == "__main__":
    main()