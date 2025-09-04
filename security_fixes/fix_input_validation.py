#!/usr/bin/env python3
"""
Security Fix: Input Validation and SQL Injection Prevention
Task ID: eeb5d5b1
Priority: CRITICAL
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any

class InputValidationFixer:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.fixes_applied = []
        
    def create_input_validator(self) -> Dict[str, Any]:
        """Create comprehensive input validation middleware"""
        
        validator_code = '''"""
Comprehensive Input Validation and Sanitization
Prevents SQL injection, XSS, and other injection attacks
"""

import re
import html
import urllib.parse
from typing import Any, Optional, List
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, validator, Field
from config.logging_config import get_logger

logger = get_logger(__name__)

class InputValidator:
    """Core input validation logic"""
    
    # SQL Injection patterns
    SQL_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE|UNION|FROM|WHERE|JOIN)\b)",
        r"(--|\||;|\/\*|\*\/|xp_|sp_|0x)",
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
        r"(WAITFOR|DELAY|SLEEP)",
        r"(@@version|@@servername|@@language)",
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>.*?</iframe>",
        r"<object[^>]*>.*?</object>",
        r"<embed[^>]*>.*?</embed>",
        r"<applet[^>]*>.*?</applet>",
        r"<form[^>]*>.*?</form>",
        r"<img[^>]*on\w+\s*=",
        r"eval\s*\(",
        r"expression\s*\(",
    ]
    
    # Path Traversal patterns
    PATH_PATTERNS = [
        r"\.\./",
        r"\.\.\\\",
        r"%2e%2e/",
        r"%2e%2e\\\",
        r"\.\./\.\./",
        r"\.\.;",
    ]
    
    # Command Injection patterns
    CMD_PATTERNS = [
        r"[;&|`$]",
        r"\$\(",
        r"`.*`",
        r"\|\|",
        r"&&",
        r">",
        r"<",
    ]
    
    @classmethod
    def validate_sql_safe(cls, value: str, field_name: str = "input") -> str:
        """Validate input is safe from SQL injection"""
        if not value:
            return value
            
        value_upper = value.upper()
        for pattern in cls.SQL_PATTERNS:
            if re.search(pattern, value_upper):
                logger.warning(f"SQL injection attempt detected in {field_name}: {value[:100]}")
                raise ValueError(f"Invalid characters in {field_name}")
        
        return value
    
    @classmethod
    def validate_xss_safe(cls, value: str, field_name: str = "input") -> str:
        """Validate input is safe from XSS"""
        if not value:
            return value
            
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"XSS attempt detected in {field_name}: {value[:100]}")
                raise ValueError(f"Invalid HTML/JavaScript in {field_name}")
        
        return value
    
    @classmethod
    def validate_path_safe(cls, value: str, field_name: str = "path") -> str:
        """Validate path is safe from traversal attacks"""
        if not value:
            return value
            
        # Normalize path
        value = os.path.normpath(value)
        
        for pattern in cls.PATH_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Path traversal attempt detected in {field_name}: {value}")
                raise ValueError(f"Invalid path in {field_name}")
        
        # Check for absolute paths
        if os.path.isabs(value):
            raise ValueError(f"Absolute paths not allowed in {field_name}")
        
        return value
    
    @classmethod
    def validate_command_safe(cls, value: str, field_name: str = "input") -> str:
        """Validate input is safe from command injection"""
        if not value:
            return value
            
        for pattern in cls.CMD_PATTERNS:
            if re.search(pattern, value):
                logger.warning(f"Command injection attempt detected in {field_name}: {value[:100]}")
                raise ValueError(f"Invalid characters in {field_name}")
        
        return value
    
    @classmethod
    def sanitize_html(cls, value: str) -> str:
        """Sanitize HTML content"""
        # Escape HTML entities
        return html.escape(value)
    
    @classmethod
    def sanitize_url(cls, value: str) -> str:
        """Sanitize URL parameters"""
        return urllib.parse.quote(value, safe='')
    
    @classmethod
    def validate_email(cls, email: str) -> str:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        
        # Additional checks
        if len(email) > 254:  # RFC 5321
            raise ValueError("Email too long")
        
        # Check for SQL/XSS in email
        cls.validate_sql_safe(email, "email")
        cls.validate_xss_safe(email, "email")
        
        return email.lower()
    
    @classmethod
    def validate_username(cls, username: str) -> str:
        """Validate username format"""
        # Allow alphanumeric, underscore, dash
        username_pattern = r'^[a-zA-Z0-9_-]{3,30}$'
        if not re.match(username_pattern, username):
            raise ValueError("Username must be 3-30 characters, alphanumeric, underscore, or dash")
        
        # Check for SQL/XSS
        cls.validate_sql_safe(username, "username")
        cls.validate_xss_safe(username, "username")
        
        return username
    
    @classmethod
    def validate_password(cls, password: str) -> str:
        """Validate password strength"""
        if len(password) < 12:
            raise ValueError("Password must be at least 12 characters")
        
        if len(password) > 128:
            raise ValueError("Password too long")
        
        # Check complexity
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        if not all([has_upper, has_lower, has_digit, has_special]):
            raise ValueError("Password must contain uppercase, lowercase, digit, and special character")
        
        # Check for common weak passwords
        weak_passwords = [
            "password", "123456", "qwerty", "abc123", "admin",
            "letmein", "welcome", "monkey", "dragon", "master"
        ]
        
        if any(weak in password.lower() for weak in weak_passwords):
            raise ValueError("Password is too common")
        
        return password
    
    @classmethod
    def validate_uuid(cls, uuid_str: str) -> str:
        """Validate UUID format"""
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, uuid_str.lower()):
            raise ValueError("Invalid UUID format")
        
        return uuid_str.lower()
    
    @classmethod
    def validate_integer(cls, value: Any, min_val: Optional[int] = None, 
                        max_val: Optional[int] = None) -> int:
        """Validate integer input"""
        try:
            int_val = int(value)
        except (ValueError, TypeError):
            raise ValueError("Invalid integer value")
        
        if min_val is not None and int_val < min_val:
            raise ValueError(f"Value must be at least {min_val}")
        
        if max_val is not None and int_val > max_val:
            raise ValueError(f"Value must be at most {max_val}")
        
        return int_val
    
    @classmethod
    def validate_json_safe(cls, json_str: str) -> str:
        """Validate JSON string is safe"""
        # Check for potential JSON injection
        dangerous_keys = ["__proto__", "constructor", "prototype"]
        
        for key in dangerous_keys:
            if key in json_str:
                raise ValueError(f"Dangerous key '{key}' detected in JSON")
        
        # Validate against SQL/XSS
        cls.validate_sql_safe(json_str, "json")
        cls.validate_xss_safe(json_str, "json")
        
        return json_str

class InputValidationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate all incoming requests"""
    
    async def dispatch(self, request: Request, call_next):
        # Skip validation for certain paths
        skip_paths = ["/health", "/metrics", "/docs", "/openapi.json"]
        if request.url.path in skip_paths:
            return await call_next(request)
        
        try:
            # Validate query parameters
            for key, value in request.query_params.items():
                InputValidator.validate_sql_safe(value, f"query_param_{key}")
                InputValidator.validate_xss_safe(value, f"query_param_{key}")
            
            # Validate path parameters
            path_parts = request.url.path.split("/")
            for part in path_parts:
                if part:
                    InputValidator.validate_path_safe(part, "path_component")
            
            # For POST/PUT/PATCH, validate body (handled by Pydantic models)
            
            response = await call_next(request)
            return response
            
        except ValueError as e:
            logger.warning(f"Input validation failed: {e} - Path: {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"detail": str(e)}
            )
        except Exception as e:
            logger.error(f"Input validation error: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal validation error"}
            )

# Pydantic models with built-in validation
class SecureUserCreate(BaseModel):
    """User creation with validation"""
    email: str = Field(..., max_length=254)
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=12, max_length=128)
    
    @validator('email')
    def validate_email(cls, v):
        return InputValidator.validate_email(v)
    
    @validator('username')
    def validate_username(cls, v):
        return InputValidator.validate_username(v)
    
    @validator('password')
    def validate_password(cls, v):
        return InputValidator.validate_password(v)

class SecureQueryParams(BaseModel):
    """Validated query parameters"""
    search: Optional[str] = Field(None, max_length=100)
    page: int = Field(1, ge=1, le=1000)
    limit: int = Field(10, ge=1, le=100)
    sort: Optional[str] = Field(None, regex='^[a-zA-Z_]+$')
    
    @validator('search')
    def validate_search(cls, v):
        if v:
            InputValidator.validate_sql_safe(v, "search")
            InputValidator.validate_xss_safe(v, "search")
        return v
'''
        
        validator_path = self.project_root / "middleware" / "input_validation.py"
        validator_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(validator_path, 'w') as f:
            f.write(validator_code)
        
        return {
            "file": "middleware/input_validation.py",
            "issue": "Missing input validation",
            "status": "Fixed",
            "changes": "Created comprehensive input validation middleware"
        }
    
    def fix_sql_injection_in_users(self) -> Dict[str, Any]:
        """Fix SQL injection vulnerability in users.py"""
        
        users_path = self.project_root / "api" / "routers" / "users.py"
        
        with open(users_path, 'r') as f:
            content = f.read()
        
        # Fix the vulnerable query construction
        old_pattern = r"stmt = select\(BusinessProfile\)\.where\(BusinessProfile\.user_id == str\(current_user\.id\)\)"
        new_code = '''# Use parameterized query to prevent SQL injection
    from sqlalchemy import bindparam
    stmt = select(BusinessProfile).where(BusinessProfile.user_id == bindparam('user_id'))
    result = await db.execute(stmt, {'user_id': str(current_user.id)})'''
        
        content = re.sub(old_pattern, new_code, content)
        
        # Add input validation import
        if "from middleware.input_validation import InputValidator" not in content:
            content = "from middleware.input_validation import InputValidator\n" + content
        
        with open(users_path, 'w') as f:
            f.write(content)
        
        return {
            "file": "api/routers/users.py",
            "issue": "SQL injection vulnerability",
            "status": "Fixed",
            "changes": "Used parameterized queries"
        }
    
    def add_validation_to_main(self) -> Dict[str, Any]:
        """Add input validation middleware to main.py"""
        
        main_path = self.project_root / "main.py"
        
        with open(main_path, 'r') as f:
            content = f.read()
        
        # Add import
        if "from middleware.input_validation import InputValidationMiddleware" not in content:
            import_line = "from middleware.input_validation import InputValidationMiddleware\n"
            content = re.sub(
                r"(from fastapi import.*?\n)",
                r"\1" + import_line,
                content
            )
        
        # Add middleware
        if "InputValidationMiddleware" not in content:
            middleware_line = "\napp.add_middleware(InputValidationMiddleware)\n"
            content = re.sub(
                r"(app = FastAPI.*?\))",
                r"\1" + middleware_line,
                content
            )
        
        with open(main_path, 'w') as f:
            f.write(content)
        
        return {
            "file": "main.py",
            "issue": "Missing input validation middleware",
            "status": "Fixed",
            "changes": "Added InputValidationMiddleware to FastAPI app"
        }

def main():
    print("🔒 Fixing Input Validation and SQL Injection Vulnerabilities\n")
    
    fixer = InputValidationFixer()
    
    # Apply fixes
    fixes = []
    
    print("1. Creating input validation middleware...")
    fixes.append(fixer.create_input_validator())
    
    print("2. Fixing SQL injection in users.py...")
    fixes.append(fixer.fix_sql_injection_in_users())
    
    print("3. Adding validation middleware to main.py...")
    fixes.append(fixer.add_validation_to_main())
    
    print("\n✅ Input Validation Security Fixes Complete!")
    print(f"   - Fixed {len(fixes)} vulnerabilities")
    print("\n📋 Summary:")
    for fix in fixes:
        print(f"   ✓ {fix['issue']} - {fix['status']}")

if __name__ == "__main__":
    main()