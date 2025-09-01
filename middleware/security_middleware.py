"""
Integrated Security Middleware combining all security services
"""

from typing import Optional, Dict, Any, List
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging
import re
from datetime import datetime

from services.security.authentication import AuthenticationService, get_auth_service
from services.security.authorization import AuthorizationService, get_authz_service
from services.security.encryption import EncryptionService, get_encryption_service
from services.security.audit_logging import AuditLoggingService, get_audit_service
from services.security.audit_logging import AuditEventType, AuditEventAction
from middleware.security_headers import SecurityHeadersMiddleware
from database.db_setup import get_db
from services.cache_service import CacheService

logger = logging.getLogger(__name__)


class SecurityMiddleware:
    """Comprehensive security middleware integrating all security services"""
    
    def __init__(
        self,
        app,
        auth_service: Optional[AuthenticationService] = None,
        authz_service: Optional[AuthorizationService] = None,
        encryption_service: Optional[EncryptionService] = None,
        audit_service: Optional[AuditLoggingService] = None,
        enable_auth: bool = True,
        enable_authz: bool = True,
        enable_audit: bool = True,
        enable_encryption: bool = True,
        enable_sql_protection: bool = True,
        public_paths: Optional[List[str]] = None
    ):
        """
        Initialize security middleware
        
        Args:
            app: FastAPI application instance
            auth_service: Authentication service instance
            authz_service: Authorization service instance
            encryption_service: Encryption service instance
            audit_service: Audit logging service instance
            enable_auth: Enable authentication checks
            enable_authz: Enable authorization checks
            enable_audit: Enable audit logging
            enable_encryption: Enable field encryption
            enable_sql_protection: Enable SQL injection protection
            public_paths: List of paths that don't require authentication
        """
        self.app = app
        self.auth_service = auth_service or get_auth_service()
        self.authz_service = authz_service or get_authz_service()
        self.encryption_service = encryption_service or get_encryption_service()
        self.audit_service = audit_service or get_audit_service()
        
        self.enable_auth = enable_auth
        self.enable_authz = enable_authz
        self.enable_audit = enable_audit
        self.enable_encryption = enable_encryption
        self.enable_sql_protection = enable_sql_protection
        
        self.public_paths = public_paths or [
            "/docs",
            "/openapi.json",
            "/health",
            "/auth/login",
            "/auth/register",
            "/auth/forgot-password",
            "/auth/reset-password"
        ]
        
        # SQL injection patterns
        self.sql_patterns = [
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|UNION|CREATE|ALTER|EXEC|EXECUTE|SCRIPT|JAVASCRIPT)\b)",
            r"(--|#|\/\*|\*\/)",
            r"(\bOR\b\s*\d+\s*=\s*\d+)",
            r"(\bAND\b\s*\d+\s*=\s*\d+)",
            r"(;.*?(SELECT|INSERT|UPDATE|DELETE|DROP))",
            r"(<script.*?>.*?</script>)",
            r"(javascript:)",
            r"(on\w+\s*=)"
        ]
    
    async def __call__(self, request: Request, call_next):
        """
        Process request through security middleware
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware in chain
            
        Returns:
            Response after security processing
        """
        # Get database session
        db = next(get_db())
        
        try:
            # Check if path is public
            if not self._is_public_path(request.url.path):
                # Perform authentication
                if self.enable_auth:
                    user = await self._authenticate_request(request, db)
                    if not user:
                        return self._unauthorized_response()
                    request.state.user = user
                    request.state.user_id = user.get("id")
                
                # Perform authorization
                if self.enable_authz and hasattr(request.state, "user_id"):
                    authorized = await self._authorize_request(request, db)
                    if not authorized:
                        return self._forbidden_response()
            
            # SQL injection protection
            if self.enable_sql_protection:
                if await self._detect_sql_injection(request):
                    await self._log_security_alert(request, "SQL_INJECTION_ATTEMPT", db)
                    return self._bad_request_response("Invalid input detected")
            
            # Process request
            response = await call_next(request)
            
            # Audit logging
            if self.enable_audit:
                await self._log_request(request, response, db)
            
            # Handle field encryption for responses
            if self.enable_encryption:
                response = await self._handle_response_encryption(request, response)
            
            return response
            
        except HTTPException as e:
            # Re-raise HTTP exceptions
            raise e
        except Exception as e:
            logger.error(f"Security middleware error: {str(e)}")
            return self._internal_error_response()
        finally:
            db.close()
    
    async def _authenticate_request(self, request: Request, db: Session) -> Optional[Dict[str, Any]]:
        """
        Authenticate the incoming request
        
        Args:
            request: HTTP request
            db: Database session
            
        Returns:
            User information if authenticated, None otherwise
        """
        # Extract token from headers
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.replace("Bearer ", "")
        
        # Validate token
        user = await self.auth_service.validate_token(token, db)
        
        if user:
            # Check session validity
            session_valid = await self.auth_service.validate_session(
                user_id=user["id"],
                session_token=token,
                db=db
            )
            
            if not session_valid:
                return None
        
        return user
    
    async def _authorize_request(self, request: Request, db: Session) -> bool:
        """
        Authorize the request based on user permissions
        
        Args:
            request: HTTP request
            db: Database session
            
        Returns:
            True if authorized, False otherwise
        """
        user_id = request.state.user_id
        resource = self._extract_resource(request)
        action = self._map_method_to_action(request.method)
        
        # Check permission
        has_permission = await self.authz_service.check_permission(
            user_id=user_id,
            resource=resource,
            action=action,
            db=db
        )
        
        # Log authorization attempt
        if self.enable_audit:
            await self.audit_service.log_authorization(
                user_id=user_id,
                resource=resource,
                permission=f"{action}:{resource}",
                granted=has_permission,
                db=db
            )
        
        return has_permission
    
    async def _detect_sql_injection(self, request: Request) -> bool:
        """
        Detect potential SQL injection attempts
        
        Args:
            request: HTTP request
            
        Returns:
            True if SQL injection detected, False otherwise
        """
        # Check query parameters
        for param, value in request.query_params.items():
            if self._contains_sql_pattern(str(value)):
                logger.warning(f"Potential SQL injection in query param {param}: {value}")
                return True
        
        # Check body for POST/PUT requests
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if body:
                    body_str = body.decode("utf-8")
                    if self._contains_sql_pattern(body_str):
                        logger.warning(f"Potential SQL injection in request body")
                        return True
            except:
                pass
        
        # Check path parameters
        path = request.url.path
        if self._contains_sql_pattern(path):
            logger.warning(f"Potential SQL injection in path: {path}")
            return True
        
        return False
    
    def _contains_sql_pattern(self, text: str) -> bool:
        """
        Check if text contains SQL injection patterns
        
        Args:
            text: Text to check
            
        Returns:
            True if SQL pattern detected, False otherwise
        """
        for pattern in self.sql_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    async def _log_request(self, request: Request, response: Response, db: Session) -> None:
        """
        Log the request for audit purposes
        
        Args:
            request: HTTP request
            response: HTTP response
            db: Database session
        """
        user_id = getattr(request.state, "user_id", None)
        
        # Determine action based on method and path
        action = self._determine_audit_action(request)
        
        # Log the event
        await self.audit_service.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            action=action,
            user_id=user_id,
            resource=request.url.path,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            result="SUCCESS" if response.status_code < 400 else "FAILURE",
            metadata={
                "method": request.method,
                "status_code": response.status_code,
                "path": request.url.path
            },
            db=db
        )
    
    async def _log_security_alert(self, request: Request, alert_type: str, db: Session) -> None:
        """
        Log security alert
        
        Args:
            request: HTTP request
            alert_type: Type of security alert
            db: Database session
        """
        user_id = getattr(request.state, "user_id", None)
        
        await self.audit_service.log_event(
            event_type=AuditEventType.SECURITY_ALERT,
            action=AuditEventAction.CREATE,
            user_id=user_id,
            resource=request.url.path,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("User-Agent"),
            result="BLOCKED",
            metadata={
                "alert_type": alert_type,
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params)
            },
            db=db
        )
    
    async def _handle_response_encryption(self, request: Request, response: Response) -> Response:
        """
        Handle field encryption for response data
        
        Args:
            request: HTTP request
            response: HTTP response
            
        Returns:
            Response with encrypted fields if applicable
        """
        # Only process JSON responses
        if response.headers.get("content-type", "").startswith("application/json"):
            # This would integrate with the encryption service
            # to encrypt sensitive fields in the response
            pass
        
        return response
    
    def _is_public_path(self, path: str) -> bool:
        """
        Check if path is public
        
        Args:
            path: Request path
            
        Returns:
            True if public, False otherwise
        """
        for public_path in self.public_paths:
            if path.startswith(public_path):
                return True
        return False
    
    def _extract_resource(self, request: Request) -> str:
        """
        Extract resource from request path
        
        Args:
            request: HTTP request
            
        Returns:
            Resource identifier
        """
        path_parts = request.url.path.strip("/").split("/")
        if len(path_parts) > 0:
            return path_parts[0]
        return "unknown"
    
    def _map_method_to_action(self, method: str) -> str:
        """
        Map HTTP method to action
        
        Args:
            method: HTTP method
            
        Returns:
            Action string
        """
        method_map = {
            "GET": "read",
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete"
        }
        return method_map.get(method, "read")
    
    def _determine_audit_action(self, request: Request) -> AuditEventAction:
        """
        Determine audit action from request
        
        Args:
            request: HTTP request
            
        Returns:
            Audit event action
        """
        method = request.method
        if method == "GET":
            return AuditEventAction.READ
        elif method == "POST":
            return AuditEventAction.CREATE
        elif method in ["PUT", "PATCH"]:
            return AuditEventAction.UPDATE
        elif method == "DELETE":
            return AuditEventAction.DELETE
        else:
            return AuditEventAction.READ
    
    def _unauthorized_response(self) -> JSONResponse:
        """Return 401 Unauthorized response"""
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized", "message": "Authentication required"}
        )
    
    def _forbidden_response(self) -> JSONResponse:
        """Return 403 Forbidden response"""
        return JSONResponse(
            status_code=403,
            content={"error": "Forbidden", "message": "Insufficient permissions"}
        )
    
    def _bad_request_response(self, message: str) -> JSONResponse:
        """Return 400 Bad Request response"""
        return JSONResponse(
            status_code=400,
            content={"error": "Bad Request", "message": message}
        )
    
    def _internal_error_response(self) -> JSONResponse:
        """Return 500 Internal Server Error response"""
        return JSONResponse(
            status_code=500,
            content={"error": "Internal Server Error", "message": "An error occurred processing your request"}
        )


def create_security_middleware(
    app,
    config: Optional[Dict[str, Any]] = None
) -> SecurityMiddleware:
    """
    Factory function to create configured security middleware
    
    Args:
        app: FastAPI application
        config: Optional configuration dictionary
        
    Returns:
        Configured SecurityMiddleware instance
    """
    config = config or {}
    
    return SecurityMiddleware(
        app=app,
        enable_auth=config.get("enable_auth", True),
        enable_authz=config.get("enable_authz", True),
        enable_audit=config.get("enable_audit", True),
        enable_encryption=config.get("enable_encryption", True),
        enable_sql_protection=config.get("enable_sql_protection", True),
        public_paths=config.get("public_paths")
    )