"""
Input Validation and Sanitization Module
Implements comprehensive input validation to prevent injection attacks
"""
from __future__ import annotations

import re
import html
import urllib.parse
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import bleach
from pydantic import BaseModel, Field, validator, constr, conint
from email_validator import validate_email, EmailNotValidError

from config.logging_config import get_logger

logger = get_logger(__name__)


class InputSanitizer:
    """Comprehensive input sanitization utilities"""
    
    # SQL injection patterns
    SQL_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|EXEC|EXECUTE)\b)",
        r"(--|\#|\/\*|\*\/)",  # SQL comments
        r"(\bUNION\b.*\bSELECT\b)",  # UNION attacks
        r"(\bOR\b\s+\d+\s*=\s*\d+)",  # OR 1=1 attacks
        r"(\bAND\b\s+\d+\s*=\s*\d+)",  # AND 1=1 attacks
        r"(;.*?(SELECT|INSERT|UPDATE|DELETE|DROP))",  # Stacked queries
        r"(\bSLEEP\b\s*\()",  # Time-based attacks
        r"(\bBENCHMARK\b\s*\()",  # MySQL benchmark
        r"(\bWAITFOR\b\s+\bDELAY\b)",  # SQL Server delay
        r"(xp_cmdshell)",  # SQL Server command execution
        r"(\bLOAD_FILE\b\s*\()",  # File reading
        r"(\bINTO\b\s+\bOUTFILE\b)",  # File writing
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r"(<script[^>]*>.*?</script>)",
        r"(javascript:)",
        r"(on\w+\s*=)",  # Event handlers
        r"(<iframe[^>]*>)",
        r"(<object[^>]*>)",
        r"(<embed[^>]*>)",
        r"(<svg[^>]*on)",
        r"(data:text/html)",
        r"(vbscript:)",
        r"(<img[^>]*on)",
        r"(<body[^>]*on)",
        r"(<link[^>]*href.*javascript)",
        r"(<meta[^>]*http-equiv)",
        r"(document\.cookie)",
        r"(document\.write)",
        r"(\.innerHTML\s*=)",
        r"(eval\s*\()",
        r"(setTimeout\s*\()",
        r"(setInterval\s*\()",
        r"(Function\s*\()",
    ]
    
    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"(\.\./)",  # Unix path traversal
        r"(\.\.\\)",  # Windows path traversal
        r"(%2e%2e[/\\])",  # URL encoded
        r"(%252e%252e[/\\])",  # Double encoded
        r"(\.\.%2f)",  # Mixed encoding
        r"(\.\.%5c)",  # Mixed encoding Windows
        r"(/etc/passwd)",  # Common target
        r"(C:\\windows)",  # Windows target
        r"(/proc/self)",  # Linux proc
        r"(file://)",  # File protocol
    ]
    
    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r"([;&|`$])",  # Shell metacharacters
        r"(\$\(.*\))",  # Command substitution
        r"(`.*`)",  # Backticks
        r"(\|\|)",  # OR operator
        r"(&&)",  # AND operator
        r"(>|>>|<)",  # Redirection
        r"(\bping\b|\bnetstat\b|\bwhoami\b|\bls\b|\bdir\b)",  # Common commands
    ]
    
    # LDAP injection patterns
    LDAP_PATTERNS = [
        r"(\*\s*\))",  # Wildcard with closing parenthesis
        r"(\(\s*\|)",  # OR filter
        r"(\(\s*&)",  # AND filter
        r"(\)\s*\()",  # Filter bypass
        r"(cn=|uid=|ou=)",  # Common LDAP attributes
    ]
    
    # NoSQL injection patterns
    NOSQL_PATTERNS = [
        r"(\$gt|\$gte|\$lt|\$lte|\$ne|\$eq)",  # MongoDB operators
        r"(\$in|\$nin|\$exists)",  # More MongoDB operators
        r"(\$where|\$regex)",  # Dangerous MongoDB operators
        r"({.*:.*})",  # JSON injection
        r"(\\x00|\\0)",  # Null byte injection
    ]
    
    @staticmethod
    def sanitize_sql_input(input_value: str, strict: bool = True) -> str: Sanitize input to prevent SQL injection
        
        Args:
            input_value: Raw input string
            strict: If True, reject suspicious input; if False, escape it
            
        Returns:
            Sanitized string
            
        Raises:
            ValueError: If suspicious pattern detected and strict=True
        """
        if not input_value:
            return input_value
        
        # Check for SQL injection patterns
        for pattern in InputSanitizer.SQL_PATTERNS:
            if re.search(pattern, input_value, re.IGNORECASE):
                if strict:
                    logger.warning(f"SQL injection pattern detected: {pattern}")
                    raise ValueError("Invalid input detected")
                else:
                    # Escape special characters
                    input_value = input_value.replace("'", "''")
                    input_value = input_value.replace('"', '""')
                    input_value = input_value.replace("\\", "\\\\")
                    input_value = input_value.replace("%", "\\%")
                    input_value = input_value.replace("_", "\\_")
        
        return input_value
    
    @staticmethod
    def sanitize_html_input(
        input_value: str,
        allowed_tags: Optional[List[str]] = None,
        allowed_attributes: Optional[Dict[str, List[str]]] = None
    ) -> str:
        """
        Sanitize HTML input to prevent XSS
        
        Args:
            input_value: Raw HTML input
            allowed_tags: List of allowed HTML tags
            allowed_attributes: Dict of allowed attributes per tag
            
        Returns:
            Sanitized HTML string
        """
        if not input_value:
            return input_value
        
        # Default allowed tags for basic formatting
        if allowed_tags is None:
            allowed_tags = [
                'p', 'br', 'span', 'div', 'strong', 'em', 'u', 's',
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'ul', 'ol', 'li', 'blockquote', 'code', 'pre',
                'a', 'img'
            ]
        
        # Default allowed attributes
        if allowed_attributes is None:
            allowed_attributes = {
                'a': ['href', 'title', 'target'],
                'img': ['src', 'alt', 'width', 'height'],
                '*': ['class', 'id']
            }
        
        # Use bleach for HTML sanitization
        cleaned = bleach.clean(
            input_value,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True,
            strip_comments=True
        )
        
        # Additional XSS pattern check
        for pattern in InputSanitizer.XSS_PATTERNS:
            if re.search(pattern, cleaned, re.IGNORECASE):
                logger.warning(f"XSS pattern still present after bleach: {pattern}")
                # Remove the entire suspicious content
                cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        return cleaned
    
    @staticmethod
    def sanitize_path(input_path: str, base_path: Optional[str] = None) -> str: Sanitize file path to prevent path traversal attacks
        
        Args:
            input_path: User-provided path
            base_path: Base directory to restrict access to
            
        Returns:
            Sanitized path
            
        Raises:
            ValueError: If path traversal attempt detected
        """
        if not input_path:
            return input_path
        
        # Check for path traversal patterns
        for pattern in InputSanitizer.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, input_path, re.IGNORECASE):
                logger.warning(f"Path traversal pattern detected: {pattern}")
                raise ValueError("Invalid path")
        
        # Resolve and validate path
        try:
            # Remove any URL encoding
            input_path = urllib.parse.unquote(input_path)
            
            # Create Path object
            path = Path(input_path)
            
            # Resolve to absolute path
            if base_path:
                base = Path(base_path).resolve()
                full_path = (base / path).resolve()
                
                # Ensure path is within base directory
                if not str(full_path).startswith(str(base)):
                    logger.warning(f"Path escape attempt: {full_path} not in {base}")
                    raise ValueError("Invalid path")
                
                return str(full_path.relative_to(base))
            else:
                # Just normalize the path
                return str(path.name)  # Return only filename, no directory
                
        except Exception as e:
            logger.error(f"Path validation error: {e}")
            raise ValueError("Invalid path")
    
    @staticmethod
    def sanitize_command_input(input_value: str) -> str: Sanitize input to prevent command injection
        
        Args:
            input_value: User input that might be used in commands
            
        Returns:
            Sanitized string
            
        Raises:
            ValueError: If command injection pattern detected
        """
        if not input_value:
            return input_value
        
        # Check for command injection patterns
        for pattern in InputSanitizer.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, input_value):
                logger.warning(f"Command injection pattern detected: {pattern}")
                raise ValueError("Invalid input")
        
        # Escape shell metacharacters
        escaped = re.sub(r'([;&|`$<>\\])', r'\\\1', input_value)
        
        # Remove newlines and carriage returns
        escaped = escaped.replace('\n', '').replace('\r', '')
        
        return escaped
    
    @staticmethod
    def sanitize_json_input(input_value: str) -> str: Sanitize JSON input to prevent NoSQL injection
        
        Args:
            input_value: JSON string input
            
        Returns:
            Sanitized JSON string
            
        Raises:
            ValueError: If NoSQL injection pattern detected
        """
        if not input_value:
            return input_value
        
        # Check for NoSQL injection patterns
        for pattern in InputSanitizer.NOSQL_PATTERNS:
            if re.search(pattern, input_value):
                logger.warning(f"NoSQL injection pattern detected: {pattern}")
                raise ValueError("Invalid JSON input")
        
        # Escape special characters
        input_value = input_value.replace('$', '\\$')
        input_value = input_value.replace('.', '\\.')
        
        return input_value
    
    @staticmethod
    def validate_email_address(email: str) -> str: Validate and normalize email address
        
        Args:
            email: Email address to validate
            
        Returns:
            Normalized email address
            
        Raises:
            ValueError: If email is invalid
        """
        try:
            # Validate email
            validation = validate_email(email, check_deliverability=False)
            
            # Return normalized email
            return validation.email
            
        except EmailNotValidError as e:
            logger.warning(f"Invalid email: {e}")
            raise ValueError(f"Invalid email address: {e}")
    
    @staticmethod
    def validate_url(url: str, allowed_schemes: Optional[List[str]] = None) -> str: Validate and sanitize URL
        
        Args:
            url: URL to validate
            allowed_schemes: List of allowed URL schemes
            
        Returns:
            Validated URL
            
        Raises:
            ValueError: If URL is invalid or uses disallowed scheme
        """
        if not url:
            return url
        
        # Default allowed schemes
        if allowed_schemes is None:
            allowed_schemes = ['http', 'https']
        
        # Parse URL
        parsed = urllib.parse.urlparse(url)
        
        # Check scheme
        if parsed.scheme not in allowed_schemes:
            raise ValueError(f"Invalid URL scheme: {parsed.scheme}")
        
        # Check for JavaScript URLs
        if 'javascript:' in url.lower() or 'data:' in url.lower():
            raise ValueError("Invalid URL")
        
        # Check for local file access
        if parsed.hostname in ['localhost', '127.0.0.1', '0.0.0.0', '::1']:
            logger.warning(f"Local URL access attempt: {url}")
            raise ValueError("Local URLs not allowed")
        
        # Check for private IP ranges
        import ipaddress
        try:
            ip = ipaddress.ip_address(parsed.hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                raise ValueError("Private IP addresses not allowed")
        except ValueError:
            # Not an IP address, that's fine
            pass
        
        return url
    
    @staticmethod
    def sanitize_filename(filename: str, max_length: int = 255) -> str: Sanitize filename to prevent security issues
        
        Args:
            filename: Original filename
            max_length: Maximum allowed length
            
        Returns:
            Sanitized filename
        """
        if not filename:
            return "unnamed"
        
        # Remove path components
        filename = Path(filename).name
        
        # Remove dangerous characters
        filename = re.sub(r'[^\w\s\-\.]', '', filename)
        
        # Remove multiple dots (prevent extension confusion)
        filename = re.sub(r'\.+', '.', filename)
        
        # Remove leading/trailing dots and spaces
        filename = filename.strip('. ')
        
        # Limit length
        if len(filename) > max_length:
            # Preserve extension if possible
            name, ext = Path(filename).stem, Path(filename).suffix
            max_name_length = max_length - len(ext)
            filename = name[:max_name_length] + ext
        
        # Ensure filename is not empty
        if not filename:
            filename = "unnamed"
        
        return filename


# Pydantic models with built-in validation

class SecureStringField(constr): min_length = 1
    max_length = 1000
    strip_whitespace = True


class SecureEmailField(BaseModel): email: str
    
    @validator('email')
    def validate_email(cls, v):
        """Validate Email"""
        return InputSanitizer.validate_email_address(v)


class SecurePathField(BaseModel): path: str
    
    @validator('path')
    def validate_path(cls, v):
        """Validate Path"""
        return InputSanitizer.sanitize_path(v)


class SecureURLField(BaseModel): url: str
    
    @validator('url')
    def validate_url(cls, v):
        """Validate Url"""
        return InputSanitizer.validate_url(v)


class SecureIntegerField(conint): ge = 0  # Greater than or equal to 0
    le = 2147483647  # Max 32-bit integer


class PaginationParams(BaseModel): page: SecureIntegerField = Field(1, ge=1, le=10000)
    limit: SecureIntegerField = Field(20, ge=1, le=100)
    offset: SecureIntegerField = Field(0, ge=0, le=1000000)
    
    @validator('limit')
    def validate_limit(cls, v):
        """Validate Limit"""
        if v > 100:
            raise ValueError("Limit cannot exceed 100")
        return v


class SearchParams(BaseModel): query: str = Field(..., min_length=1, max_length=200)
    filters: Optional[Dict[str, Any]] = None
    
    @validator('query')
    def sanitize_query(cls, v):
        """Sanitize Query"""
        # Remove SQL injection patterns
        return InputSanitizer.sanitize_sql_input(v, strict=False)
    
    @validator('filters')
    def validate_filters(cls, v):
        """Validate Filters"""
        if v:
            # Validate each filter value
            for key, value in v.items():
                if isinstance(value, str):
                    v[key] = InputSanitizer.sanitize_sql_input(value, strict=False)
        return v


class FileUploadParams(BaseModel): filename: str
    content_type: str
    size: int
    
    @validator('filename')
    def sanitize_filename(cls, v):
        """Sanitize Filename"""
        return InputSanitizer.sanitize_filename(v)
    
    @validator('content_type')
    def validate_content_type(cls, v):
        """Validate Content Type"""
        allowed_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'text/csv',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/json',
            'image/jpeg',
            'image/png',
            'image/gif'
        ]
        
        if v not in allowed_types:
            raise ValueError(f"File type not allowed: {v}")
        
        return v
    
    @validator('size')
    def validate_size(cls, v):
        """Validate Size"""
        max_size = 10 * 1024 * 1024  # 10MB
        if v > max_size:
            raise ValueError(f"File size exceeds maximum of {max_size} bytes")
        return v


# Request validation decorator
from functools import wraps
from fastapi import HTTPException


def validate_input(sanitize_sql: bool = True, sanitize_html: bool = False): Decorator to automatically validate and sanitize input
    
    Args:
        sanitize_sql: Apply SQL injection prevention
        sanitize_html: Apply XSS prevention
    """
    def decorator(func):
        """Decorator"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                """Wrapper"""
                # Process kwargs for string inputs
                for key, value in kwargs.items():
                    if isinstance(value, str):
                        if sanitize_sql:
                            kwargs[key] = InputSanitizer.sanitize_sql_input(value, strict=False)
                        if sanitize_html:
                            kwargs[key] = InputSanitizer.sanitize_html_input(value)
                
                return await func(*args, **kwargs)
                
            except ValueError as e:
                logger.warning(f"Input validation failed: {e}")
                raise HTTPException(status_code=400, detail=str(e))
        
        return wrapper
    return decorator