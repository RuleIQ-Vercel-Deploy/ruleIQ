#!/usr/bin/env python3
"""
Security Fix: Security Headers and CORS Configuration
Task ID: eeb5d5b1
Priority: HIGH
"""

import os
from pathlib import Path
from typing import Dict, Any

class SecurityHeadersFixer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        
    def create_security_headers_middleware(self) -> Dict[str, Any]:
        """Create comprehensive security headers middleware"""
        
        headers_code = '''"""
Security Headers Middleware
Implements OWASP recommended security headers
"""

from fastapi import Request
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
import hashlib
import secrets
from config.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses"""
    
    def __init__(self, app, **kwargs):
        super().__init__(app)
        self.nonce_length = 16
        self.enable_hsts = settings.is_production or settings.force_https
        self.csp_report_uri = os.getenv("CSP_REPORT_URI", "/api/v1/security/csp-report")
        
    async def dispatch(self, request: Request, call_next):
        # Generate nonce for CSP
        nonce = secrets.token_urlsafe(self.nonce_length)
        request.state.csp_nonce = nonce
        
        # Process request
        response = await call_next(request)
        
        # Add security headers
        self._add_security_headers(response, nonce, request)
        
        return response
    
    def _add_security_headers(self, response: Response, nonce: str, request: Request):
        """Add comprehensive security headers"""
        
        # 1. Content Security Policy (CSP)
        csp_directives = self._build_csp(nonce)
        response.headers["Content-Security-Policy"] = csp_directives
        response.headers["X-Content-Security-Policy"] = csp_directives  # IE support
        
        # 2. X-Content-Type-Options
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # 3. X-Frame-Options (clickjacking protection)
        response.headers["X-Frame-Options"] = "DENY"
        
        # 4. X-XSS-Protection (for older browsers)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # 5. Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # 6. Permissions Policy (formerly Feature Policy)
        response.headers["Permissions-Policy"] = self._build_permissions_policy()
        
        # 7. HTTP Strict Transport Security (HSTS)
        if self.enable_hsts:
            response.headers["Strict-Transport-Security"] = (
                "max-age=63072000; includeSubDomains; preload"
            )
        
        # 8. Remove sensitive headers
        headers_to_remove = ["Server", "X-Powered-By", "X-AspNet-Version"]
        for header in headers_to_remove:
            response.headers.pop(header, None)
        
        # 9. Add custom security headers
        response.headers["X-Request-ID"] = getattr(request.state, "request_id", "unknown")
        response.headers["X-Content-Duration"] = "0"
        
        # 10. Cache Control for sensitive endpoints
        if self._is_sensitive_endpoint(request.url.path):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
    
    def _build_csp(self, nonce: str) -> str:
        """Build Content Security Policy directives"""
        
        # Development vs Production CSP
        if settings.is_production:
            directives = [
                "default-src 'self'",
                f"script-src 'self' 'nonce-{nonce}' https://cdn.jsdelivr.net",
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
                "font-src 'self' https://fonts.gstatic.com",
                "img-src 'self' data: https:",
                "connect-src 'self' https://api.ruleiq.com wss://api.ruleiq.com",
                "frame-ancestors 'none'",
                "base-uri 'self'",
                "form-action 'self'",
                "upgrade-insecure-requests",
                f"report-uri {self.csp_report_uri}"
            ]
        else:
            # More permissive for development
            directives = [
                "default-src 'self' 'unsafe-inline' 'unsafe-eval'",
                f"script-src 'self' 'unsafe-inline' 'nonce-{nonce}' http://localhost:*",
                "style-src 'self' 'unsafe-inline'",
                "font-src 'self' data:",
                "img-src 'self' data: http: https:",
                "connect-src 'self' ws://localhost:* http://localhost:*",
                "frame-ancestors 'self'",
                "base-uri 'self'",
                "form-action 'self'"
            ]
        
        return "; ".join(directives)
    
    def _build_permissions_policy(self) -> str:
        """Build Permissions Policy directives"""
        policies = [
            "geolocation=()",
            "microphone=()",
            "camera=()",
            "payment=()",
            "usb=()",
            "magnetometer=()",
            "gyroscope=()",
            "accelerometer=()",
            "ambient-light-sensor=()",
            "autoplay=(self)",
            "encrypted-media=(self)",
            "fullscreen=(self)",
            "picture-in-picture=(self)"
        ]
        
        return ", ".join(policies)
    
    def _is_sensitive_endpoint(self, path: str) -> bool:
        """Check if endpoint handles sensitive data"""
        sensitive_patterns = [
            "/auth/",
            "/users/",
            "/admin/",
            "/api/v1/auth",
            "/api/v1/users",
            "/payment",
            "/settings"
        ]
        
        return any(pattern in path for pattern in sensitive_patterns)

class CORSSecurityMiddleware(BaseHTTPMiddleware):
    """Secure CORS configuration"""
    
    def __init__(self, app, **kwargs):
        super().__init__(app)
        self.allowed_origins = self._get_allowed_origins()
        self.allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
        self.allowed_headers = [
            "Content-Type",
            "Authorization",
            "X-Request-ID",
            "X-API-Key"
        ]
        self.max_age = 86400  # 24 hours
        
    def _get_allowed_origins(self) -> list:
        """Get allowed origins based on environment"""
        if settings.is_production:
            return [
                "https://app.ruleiq.com",
                "https://www.ruleiq.com",
                "https://api.ruleiq.com"
            ]
        else:
            return [
                "http://localhost:3000",
                "http://localhost:8000",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:8000"
            ]
    
    async def dispatch(self, request: Request, call_next):
        # Handle preflight requests
        if request.method == "OPTIONS":
            return self._handle_preflight(request)
        
        response = await call_next(request)
        
        # Add CORS headers
        origin = request.headers.get("origin")
        if origin in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Vary"] = "Origin"
        
        return response
    
    def _handle_preflight(self, request: Request) -> Response:
        """Handle CORS preflight requests"""
        origin = request.headers.get("origin")
        
        if origin not in self.allowed_origins:
            return Response(status_code=403)
        
        response = Response(status_code=204)
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = ", ".join(self.allowed_methods)
        response.headers["Access-Control-Allow-Headers"] = ", ".join(self.allowed_headers)
        response.headers["Access-Control-Max-Age"] = str(self.max_age)
        response.headers["Access-Control-Allow-Credentials"] = "true"
        
        return response

class RateLimitingHeaders(BaseHTTPMiddleware):
    """Add rate limiting information headers"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add rate limit headers if available
        if hasattr(request.state, "rate_limit"):
            limit_info = request.state.rate_limit
            response.headers["X-RateLimit-Limit"] = str(limit_info.get("limit", 100))
            response.headers["X-RateLimit-Remaining"] = str(limit_info.get("remaining", 100))
            response.headers["X-RateLimit-Reset"] = str(limit_info.get("reset", 0))
            
            if limit_info.get("remaining", 100) <= 0:
                response.headers["Retry-After"] = str(limit_info.get("retry_after", 60))
        
        return response
'''
        
        headers_path = self.project_root / "middleware" / "security_headers_enhanced.py"
        headers_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(headers_path, 'w') as f:
            f.write(headers_code)
        
        return {
            "file": "middleware/security_headers_enhanced.py",
            "issue": "Missing security headers",
            "status": "Fixed",
            "changes": "Created comprehensive security headers middleware"
        }
    
    def create_csp_reporter(self) -> Dict[str, Any]:
        """Create CSP violation reporter endpoint"""
        
        reporter_code = '''"""
CSP Violation Reporter
Logs Content Security Policy violations for monitoring
"""

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from config.logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()

class CSPViolation(BaseModel):
    """CSP violation report model"""
    document_uri: Optional[str] = None
    referrer: Optional[str] = None
    violated_directive: Optional[str] = None
    effective_directive: Optional[str] = None
    original_policy: Optional[str] = None
    blocked_uri: Optional[str] = None
    status_code: Optional[int] = None
    source_file: Optional[str] = None
    line_number: Optional[int] = None
    column_number: Optional[int] = None

class CSPReport(BaseModel):
    """CSP report wrapper"""
    csp_report: CSPViolation = None

@router.post("/csp-report")
async def report_csp_violation(
    request: Request,
    report: Dict[str, Any]
) -> Response:
    """
    Receive and log CSP violation reports
    """
    try:
        # Extract violation details
        csp_report = report.get("csp-report", {})
        
        # Log violation with context
        logger.warning(
            f"CSP Violation Detected",
            extra={
                "document_uri": csp_report.get("document-uri"),
                "violated_directive": csp_report.get("violated-directive"),
                "blocked_uri": csp_report.get("blocked-uri"),
                "source_file": csp_report.get("source-file"),
                "line_number": csp_report.get("line-number"),
                "user_agent": request.headers.get("user-agent"),
                "ip_address": request.client.host if request.client else None,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # In production, you might want to:
        # 1. Store in database for analysis
        # 2. Send alerts for critical violations
        # 3. Update CSP policy based on legitimate violations
        
        return Response(status_code=204)
        
    except Exception as e:
        logger.error(f"Failed to process CSP report: {e}")
        return Response(status_code=204)  # Still return 204 to avoid retry

@router.get("/security-headers-test")
async def test_security_headers() -> Dict[str, str]:
    """
    Test endpoint to verify security headers are applied
    """
    return {
        "message": "Check response headers for security configuration",
        "expected_headers": [
            "Content-Security-Policy",
            "X-Content-Type-Options",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Referrer-Policy",
            "Permissions-Policy"
        ]
    }
'''
        
        reporter_path = self.project_root / "api" / "routers" / "security_headers.py"
        reporter_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(reporter_path, 'w') as f:
            f.write(reporter_code)
        
        return {
            "file": "api/routers/security_headers.py",
            "issue": "No CSP violation reporting",
            "status": "Fixed",
            "changes": "Created CSP violation reporter endpoint"
        }

def main():
    print("🔒 Implementing Security Headers and CORS Configuration\n")
    
    fixer = SecurityHeadersFixer()
    
    # Apply fixes
    fixes = []
    
    print("1. Creating security headers middleware...")
    fixes.append(fixer.create_security_headers_middleware())
    
    print("2. Creating CSP reporter endpoint...")
    fixes.append(fixer.create_csp_reporter())
    
    print("\n✅ Security Headers Implementation Complete!")
    print(f"   - Implemented {len(fixes)} security enhancements")
    print("\n📋 Summary:")
    for fix in fixes:
        print(f"   ✓ {fix['issue']} - {fix['status']}")
    
    print("\n📝 Next Steps:")
    print("   1. Add SecurityHeadersMiddleware to main.py")
    print("   2. Configure CSP policy for your domains")
    print("   3. Test headers with: curl -I http://localhost:8000")
    print("   4. Monitor CSP violations at /api/v1/security/csp-report")

if __name__ == "__main__":
    main()