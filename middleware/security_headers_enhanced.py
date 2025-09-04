"""
Enhanced Security Headers Middleware
Implements comprehensive security headers based on OWASP recommendations
"""
from __future__ import annotations

import hashlib
import secrets
from typing import Optional, List, Dict, Any
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from config.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive security headers middleware implementing OWASP best practices
    """
    
    def __init__(
        self,
        app: ASGIApp,
        csp_enabled: bool = True,
        cors_enabled: bool = False,
        nonce_enabled: bool = True,
        report_uri: Optional[str] = None,
        hsts_max_age: int = 31536000,  # 1 year
        frame_options: str = "DENY",
        content_type_options: str = "nosniff",
        xss_protection: str = "1; mode=block",
        referrer_policy: str = "strict-origin-when-cross-origin",
        permissions_policy: Optional[str] = None,
        custom_headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize security headers middleware
        
        Args:
            app: FastAPI/Starlette application
            csp_enabled: Enable Content Security Policy
            cors_enabled: Whether CORS is handled elsewhere
            nonce_enabled: Enable CSP nonce for inline scripts
            report_uri: URI for CSP violation reports
            hsts_max_age: HSTS max age in seconds
            frame_options: X-Frame-Options value
            content_type_options: X-Content-Type-Options value
            xss_protection: X-XSS-Protection value
            referrer_policy: Referrer-Policy value
            permissions_policy: Permissions-Policy value
            custom_headers: Additional custom security headers
        """
        super().__init__(app)
        self.csp_enabled = csp_enabled
        self.cors_enabled = cors_enabled
        self.nonce_enabled = nonce_enabled
        self.report_uri = report_uri or "/api/v1/security/csp-report"
        self.hsts_max_age = hsts_max_age
        self.frame_options = frame_options
        self.content_type_options = content_type_options
        self.xss_protection = xss_protection
        self.referrer_policy = referrer_policy
        self.permissions_policy = permissions_policy or self._default_permissions_policy()
        self.custom_headers = custom_headers or {}
    
    def _default_permissions_policy(self) -> str:
        """Generate default restrictive permissions policy"""
        policies = [
            "accelerometer=()",
            "ambient-light-sensor=()",
            "autoplay=(self)",
            "battery=()",
            "camera=()",
            "display-capture=()",
            "document-domain=()",
            "encrypted-media=(self)",
            "execution-while-not-rendered=()",
            "execution-while-out-of-viewport=()",
            "fullscreen=(self)",
            "gamepad=()",
            "geolocation=()",
            "gyroscope=()",
            "hid=()",
            "idle-detection=()",
            "local-fonts=()",
            "magnetometer=()",
            "microphone=()",
            "midi=()",
            "payment=()",
            "picture-in-picture=(self)",
            "publickey-credentials-get=()",
            "screen-wake-lock=()",
            "serial=()",
            "speaker-selection=()",
            "sync-xhr=()",
            "usb=()",
            "web-share=()",
            "xr-spatial-tracking=()"
        ]
        return ", ".join(policies)
    
    def _generate_nonce(self) -> str:
        """Generate cryptographic nonce for CSP"""
        return base64.b64encode(secrets.token_bytes(16)).decode('utf-8')
    
    def _build_csp_header(self, nonce: Optional[str] = None) -> str:
        """Build Content Security Policy header"""
        directives = []
        
        # Default source - very restrictive
        directives.append("default-src 'self'")
        
        # Script source
        if nonce and self.nonce_enabled:
            directives.append(f"script-src 'self' 'nonce-{nonce}' 'strict-dynamic'")
        else:
            # Still restrictive but allows inline scripts with hash
            directives.append("script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net")
        
        # Style source
        if nonce and self.nonce_enabled:
            directives.append(f"style-src 'self' 'nonce-{nonce}'")
        else:
            # Allow inline styles for now (can be tightened)
            directives.append("style-src 'self' 'unsafe-inline' https://fonts.googleapis.com")
        
        # Image source
        directives.append("img-src 'self' data: https: blob:")
        
        # Font source
        directives.append("font-src 'self' data: https://fonts.gstatic.com")
        
        # Connect source (for API calls)
        directives.append("connect-src 'self' https://api.ruleiq.com wss://api.ruleiq.com")
        
        # Media source
        directives.append("media-src 'self'")
        
        # Object source (plugins)
        directives.append("object-src 'none'")
        
        # Frame ancestors (who can embed us)
        directives.append("frame-ancestors 'none'")
        
        # Base URI
        directives.append("base-uri 'self'")
        
        # Form action
        directives.append("form-action 'self'")
        
        # Upgrade insecure requests in production
        if settings.is_production:
            directives.append("upgrade-insecure-requests")
        
        # Block all mixed content
        directives.append("block-all-mixed-content")
        
        # Require SRI for scripts and styles
        if settings.is_production:
            directives.append("require-sri-for script style")
        
        # Report URI
        if self.report_uri:
            directives.append(f"report-uri {self.report_uri}")
            directives.append(f"report-to csp-endpoint")
        
        return "; ".join(directives)
    
    def _build_report_to_header(self) -> str:
        """Build Report-To header for CSP reporting"""
        import json
        report_to = {
            "group": "csp-endpoint",
            "max_age": 10886400,
            "endpoints": [
                {"url": self.report_uri}
            ],
            "include_subdomains": True
        }
        return json.dumps(report_to)
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Add security headers to response"""
        
        # Generate nonce for this request if needed
        nonce = None
        if self.csp_enabled and self.nonce_enabled:
            nonce = self._generate_nonce()
            request.state.csp_nonce = nonce
        
        # Process request
        response = await call_next(request)
        
        # Skip headers for certain paths
        skip_paths = ['/docs', '/redoc', '/openapi.json', '/health']
        if request.url.path in skip_paths:
            return response
        
        # HSTS (HTTP Strict Transport Security)
        if settings.is_production or settings.force_https:
            hsts_header = f"max-age={self.hsts_max_age}; includeSubDomains; preload"
            response.headers["Strict-Transport-Security"] = hsts_header
        
        # Content Security Policy
        if self.csp_enabled:
            csp_header = self._build_csp_header(nonce)
            response.headers["Content-Security-Policy"] = csp_header
            
            # Report-To header for CSP reporting
            if self.report_uri:
                response.headers["Report-To"] = self._build_report_to_header()
        
        # X-Content-Type-Options
        response.headers["X-Content-Type-Options"] = self.content_type_options
        
        # X-Frame-Options (being replaced by CSP frame-ancestors)
        response.headers["X-Frame-Options"] = self.frame_options
        
        # X-XSS-Protection (legacy but still useful for older browsers)
        response.headers["X-XSS-Protection"] = self.xss_protection
        
        # Referrer-Policy
        response.headers["Referrer-Policy"] = self.referrer_policy
        
        # Permissions-Policy (formerly Feature-Policy)
        response.headers["Permissions-Policy"] = self.permissions_policy
        
        # Cache-Control for sensitive content
        if request.url.path.startswith('/api/'):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        
        # Additional security headers
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        
        # Remove potentially dangerous headers
        headers_to_remove = [
            "Server",
            "X-Powered-By",
            "X-AspNet-Version",
            "X-AspNetMvc-Version",
            "X-Runtime",
            "X-Version"
        ]
        
        for header in headers_to_remove:
            response.headers.pop(header, None)
        
        # Add custom headers
        for header, value in self.custom_headers.items():
            response.headers[header] = value
        
        # Add security context headers for debugging (only in development)
        if settings.debug and not settings.is_production:
            response.headers["X-Security-Headers-Version"] = "2.0"
            response.headers["X-CSP-Nonce"] = nonce or "disabled"
        
        return response


class CSPViolationReporter:
    """Handle CSP violation reports"""
    
    @staticmethod
    async def handle_csp_report(request: Request) -> JSONResponse:
        """
        Handle CSP violation reports
        
        Args:
            request: FastAPI request containing CSP violation report
            
        Returns:
            JSON response acknowledging receipt
        """
        try:
            # Parse CSP report
            report_data = await request.json()
            
            # Log the violation
            if 'csp-report' in report_data:
                violation = report_data['csp-report']
                logger.warning(
                    f"CSP Violation: {violation.get('violated-directive', 'unknown')} "
                    f"- Document: {violation.get('document-uri', 'unknown')} "
                    f"- Blocked: {violation.get('blocked-uri', 'unknown')} "
                    f"- Line: {violation.get('line-number', 'unknown')}"
                )
                
                # In production, you might want to:
                # - Store in database for analysis
                # - Send alerts for critical violations
                # - Update CSP policy based on legitimate violations
                
                # Check for potential attacks
                if CSPViolationReporter._is_potential_attack(violation):
                    logger.error(f"Potential XSS attack detected: {violation}")
                    # Trigger security alert
                    
            return JSONResponse(
                status_code=204,
                content=None
            )
            
        except Exception as e:
            logger.error(f"Error processing CSP report: {e}")
            return JSONResponse(
                status_code=204,
                content=None
            )
    
    @staticmethod
    def _is_potential_attack(violation: Dict[str, Any]) -> bool:
        """Check if CSP violation indicates potential attack"""
        
        blocked_uri = violation.get('blocked-uri', '').lower()
        
        # Check for suspicious patterns
        suspicious_patterns = [
            'javascript:',
            'data:text/html',
            'data:application/javascript',
            'vbscript:',
            'file://',
            'about:blank',
            'blob:'
        ]
        
        for pattern in suspicious_patterns:
            if pattern in blocked_uri:
                return True
        
        # Check for inline script violations
        if violation.get('violated-directive', '').startswith('script-src') and \
           blocked_uri in ['inline', 'eval', 'unsafe-inline']:
            return True
        
        return False


# Import base64 for nonce generation
import base64


def create_security_headers_middleware(
    app: ASGIApp,
    config: Optional[Dict[str, Any]] = None
) -> SecurityHeadersMiddleware:
    """
    Factory function to create configured security headers middleware
    
    Args:
        app: FastAPI application
        config: Optional configuration dictionary
        
    Returns:
        Configured SecurityHeadersMiddleware instance
    """
    config = config or {}
    
    return SecurityHeadersMiddleware(
        app=app,
        csp_enabled=config.get('csp_enabled', True),
        cors_enabled=config.get('cors_enabled', False),
        nonce_enabled=config.get('nonce_enabled', True),
        report_uri=config.get('report_uri', '/api/v1/security/csp-report'),
        hsts_max_age=config.get('hsts_max_age', 31536000),
        frame_options=config.get('frame_options', 'DENY'),
        content_type_options=config.get('content_type_options', 'nosniff'),
        xss_protection=config.get('xss_protection', '1; mode=block'),
        referrer_policy=config.get('referrer_policy', 'strict-origin-when-cross-origin'),
        permissions_policy=config.get('permissions_policy'),
        custom_headers=config.get('custom_headers', {})
    )