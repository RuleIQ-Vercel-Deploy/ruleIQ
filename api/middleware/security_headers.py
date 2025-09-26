"""
Security Headers Middleware for ruleIQ API.
Adds security headers to all HTTP responses to enhance application security.
"""

from __future__ import annotations

from typing import Any, Callable

from fastapi import Request
from starlette.responses import Response

# Import settings with fallback
try:
    from config.settings import settings
    is_production = getattr(settings, 'is_production', False)
    force_https = getattr(settings, 'force_https', False)
    debug = getattr(settings, 'debug', False)
except Exception:
    # Fallback if settings cannot be imported
    is_production = False
    force_https = False
    debug = False


async def security_headers_middleware(request: Request, call_next: Callable) -> Any:
    """
    Add security headers to all responses.
    
    This middleware adds various security headers to protect against
    common web vulnerabilities like XSS, clickjacking, and content sniffing.
    
    Args:
        request: The incoming HTTP request
        call_next: The next middleware or route handler
        
    Returns:
        The response with added security headers
    """
    # Process the request
    response = await call_next(request)
    
    # Common security headers for all environments
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = (
        'geolocation=(), microphone=(), camera=(), payment=(), usb=(), '
        'magnetometer=(), gyroscope=(), accelerometer=()'
    )
    
    # Cache control for security
    if request.url.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, private'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    
    # Environment-specific headers
    # HSTS header should only be set in production/HTTPS environments
    if is_production or force_https:
        # Check if the request is actually over HTTPS (direct or via proxy)
        is_https = (
            request.url.scheme == 'https' or 
            request.headers.get('x-forwarded-proto') == 'https' or
            request.headers.get('x-forwarded-ssl') == 'on'
        )
        
        if is_https:
            # Strict Transport Security for HTTPS
            response.headers['Strict-Transport-Security'] = (
                'max-age=31536000; includeSubDomains; preload'
            )
        
        # Stricter CSP in production
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://api.ruleiq.com wss://api.ruleiq.com; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
    else:
        # More permissive CSP for development
        response.headers['Content-Security-Policy'] = (
            "default-src 'self' 'unsafe-inline' 'unsafe-eval' http: https: ws: wss: data:; "
            "frame-ancestors 'none'"
        )
    
    # Cloud Run specific headers
    if request.headers.get('x-cloud-trace-context'):
        # Preserve Cloud Run trace context
        trace_context = request.headers.get('x-cloud-trace-context')
        if trace_context:
            response.headers['x-cloud-trace-context'] = trace_context
    
    # Remove potentially sensitive headers
    headers_to_remove = ['Server', 'X-Powered-By', 'X-AspNet-Version']
    for header in headers_to_remove:
        if header in response.headers:
            del response.headers[header]
    
    # Add custom security header for API version
    response.headers['X-API-Version'] = '1.0.0'
    
    # CORS preflight handling
    if request.method == 'OPTIONS':
        response.headers['Access-Control-Max-Age'] = '86400'  # 24 hours
    
    return response