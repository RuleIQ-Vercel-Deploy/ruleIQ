from __future__ import annotations
from typing import Any, Dict, List, Optional
from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime, timezone

async def security_headers_middleware(request: Request, call_next) -> Dict[str, Any]:
    """Add security headers to all responses"""
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    if 'Server' in response.headers:
        del response.headers['Server']
    return response

class CSPViolationHandler:
    """Handler for CSP violation reports"""

    def __init__(self, storage_backend: Optional[Any] = None):
        """
        Initialize CSP violation handler

        Args:
            storage_backend: Optional storage backend for violations
        """
        self.storage_backend = storage_backend
        self.violations: List[Dict[str, Any]] = []

    async def handle_violation(self, request: Request) -> JSONResponse:
        """
        Handle CSP violation report

        Args:
            request: HTTP request containing violation report

        Returns:
            JSON response acknowledging receipt
        """
        try:
            # Parse violation report
            violation_data = await request.json()

            # Extract CSP report
            csp_report = violation_data.get("csp-report", {})

            # Create violation record
            violation = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "document_uri": csp_report.get("document-uri"),
                "blocked_uri": csp_report.get("blocked-uri"),
                "violated_directive": csp_report.get("violated-directive"),
                "effective_directive": csp_report.get("effective-directive"),
                "original_policy": csp_report.get("original-policy"),
                "disposition": csp_report.get("disposition"),
                "script_sample": csp_report.get("script-sample"),
                "status_code": csp_report.get("status-code"),
                "referrer": csp_report.get("referrer"),
                "source_file": csp_report.get("source-file"),
                "line_number": csp_report.get("line-number"),
                "column_number": csp_report.get("column-number"),
            }

            # Store violation
            self.violations.append(violation)

            # Persist if storage backend available
            if self.storage_backend:
                await self._persist_violation(violation)

            # Log violation
            self._log_violation(violation)

            return JSONResponse(status_code=204, content={"status": "received"})

        except Exception as e:
            return JSONResponse(status_code=400, content={"error": str(e)})

    async def _persist_violation(self, violation: Dict[str, Any]) -> None:
        """
        Persist violation to storage backend
        
        Args:
            violation: Violation data to persist
        """
        if self.storage_backend:
            # Implementation depends on storage backend
            pass

    def _log_violation(self, violation: Dict[str, Any]) -> None:
        """
        Log CSP violation for monitoring
        
        Args:
            violation: Violation data to log
        """
        import logging

        logger = logging.getLogger(__name__)

        logger.warning(
            f"CSP Violation: {violation['violated_directive']} - "
            f"Blocked: {violation['blocked_uri']} - "
            f"Document: {violation['document_uri']}"
        )

    def get_violations_summary(self) -> Dict[str, Any]:
        """
        Get summary of CSP violations

        Returns:
            Dictionary with violation statistics
        """
        if not self.violations:
            return {"total": 0, "violations": []}

        # Group by directive
        by_directive = {}
        for violation in self.violations:
            directive = violation.get("violated_directive", "unknown")
            if directive not in by_directive:
                by_directive[directive] = 0
            by_directive[directive] += 1

        # Group by blocked URI
        by_blocked = {}
        for violation in self.violations:
            blocked = violation.get("blocked_uri", "unknown")
            if blocked not in by_blocked:
                by_blocked[blocked] = 0
            by_blocked[blocked] += 1

        return {
            "total": len(self.violations),
            "by_directive": by_directive,
            "by_blocked_uri": by_blocked,
            "recent": (
                self.violations[-10:] if len(self.violations) > 10 else self.violations
            ),
        }

class SecurityHeadersMiddleware:
    """Basic security headers middleware"""
    
    def __init__(self, app=None):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        response = await call_next(request)
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
