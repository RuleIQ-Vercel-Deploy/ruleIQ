"""
Enhanced Authentication Module with Security Improvements
Implements OWASP best practices and addresses critical vulnerabilities
"""
from __future__ import annotations

import os
import secrets
import hashlib
import base64
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Any, Tuple
from uuid import UUID, uuid4

from fastapi import Depends, HTTPException, status, Request, Header
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

from api.context import user_id_var
from core.exceptions import NotAuthenticatedException
from database.db_setup import get_async_db
from database.user import User
from config.logging_config import get_logger
from config.settings import settings

logger = get_logger(__name__)

# Security Constants
MIN_PASSWORD_LENGTH = 10  # Increased from 8
MAX_PASSWORD_LENGTH = 128
TOKEN_EXPIRY_WARNING = 300
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30
BCRYPT_ROUNDS = 14  # Increased from 12 for 2025 standards

# Generate RSA key pair for JWT (RS256)
def generate_rsa_keys() -> Tuple[str, str]:
    """Generate RSA key pair for JWT signing"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Private key
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    
    # Public key
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    
    return private_pem, public_pem

def get_jwt_keys() -> Tuple[str, str]:
    """Get or generate JWT RSA keys with secure storage"""
    if settings.is_production:
        # In production, keys should be from environment/secrets manager
        private_key = os.getenv('JWT_PRIVATE_KEY')
        public_key = os.getenv('JWT_PUBLIC_KEY')
        
        if not private_key or not public_key:
            logger.error("CRITICAL: RSA keys not found in production environment")
            raise RuntimeError("JWT RSA keys not configured for production")
            
        return private_key, public_key
    else:
        # For development, generate keys (should be persistent in real deployment)
        logger.warning("Generating temporary RSA keys for development - DO NOT use in production")
        return generate_rsa_keys()

# Get RSA keys
try:
    PRIVATE_KEY, PUBLIC_KEY = get_jwt_keys()
except Exception as e:
    logger.error(f"Failed to load JWT keys: {e}")
    # Fallback to HS256 with strong secret
    PRIVATE_KEY = secrets.token_urlsafe(64)
    PUBLIC_KEY = PRIVATE_KEY
    ALGORITHM = 'HS256'
else:
    ALGORITHM = 'RS256'

# Token expiration settings (more secure defaults)
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Reduced from 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
SESSION_ABSOLUTE_TIMEOUT_HOURS = 12  # Force re-auth after 12 hours

# Password hashing with stronger settings
pwd_context = CryptContext(
    schemes=['bcrypt'],
    deprecated='auto',
    bcrypt__rounds=BCRYPT_ROUNDS
)

# OAuth2 with stricter settings
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='/api/v1/auth/token',
    auto_error=True  # Changed from False - enforce authentication
)

class EnhancedPasswordValidator:
    """Enhanced password validation with comprehensive rules"""
    
    @staticmethod
    def validate(password: str) -> Tuple[bool, str]:
        """Validate password against security requirements"""
        
        # Length check
        if len(password) < MIN_PASSWORD_LENGTH:
            return False, f'Password must be at least {MIN_PASSWORD_LENGTH} characters long.'
        
        if len(password) > MAX_PASSWORD_LENGTH:
            return False, f'Password must not exceed {MAX_PASSWORD_LENGTH} characters.'
        
        # Complexity requirements
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()-_=+[]{}|;:,.<>?/' for c in password)
        
        if not has_lower:
            return False, 'Password must contain at least one lowercase letter.'
        
        if not has_upper:
            return False, 'Password must contain at least one uppercase letter.'
        
        if not has_digit:
            return False, 'Password must contain at least one number.'
        
        if not has_special:
            return False, 'Password must contain at least one special character (!@#$%^&*()-_=+[]{}|;:,.<>?/).'
        
        # Check for common patterns
        if EnhancedPasswordValidator._has_common_patterns(password):
            return False, 'Password contains common patterns. Please choose a more unique password.'
        
        # Check against common passwords (would use a proper list in production)
        common_passwords = ['password', 'admin', 'letmein', 'welcome', 'monkey', 'dragon']
        if password.lower() in common_passwords:
            return False, 'This password is too common. Please choose a unique password.'
        
        # Entropy check (simplified)
        if len(set(password)) < 6:
            return False, 'Password lacks sufficient character variety.'
        
        return True, 'Password is valid.'
    
    @staticmethod
    def _has_common_patterns(password: str) -> bool:
        """Check for common patterns like sequences or repeated characters"""
        
        # Check for sequences
        sequences = ['1234', '2345', '3456', '4567', '5678', '6789', '7890',
                    'abcd', 'bcde', 'cdef', 'defg', 'efgh', 'fghi', 'ghij',
                    'qwer', 'wert', 'erty', 'rtyu', 'tyui', 'yuio', 'uiop',
                    'asdf', 'sdfg', 'dfgh', 'fghj', 'ghjk', 'hjkl',
                    'zxcv', 'xcvb', 'cvbn', 'vbnm']
        
        pwd_lower = password.lower()
        for seq in sequences:
            if seq in pwd_lower or seq[::-1] in pwd_lower:
                return True
        
        # Check for too many repeated characters
        for i in range(len(password) - 2):
            if password[i] == password[i + 1] == password[i + 2]:
                return True
        
        return False

def hash_password(password: str) -> str:
    """Hash password with strong settings"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_jti() -> str:
    """Create a unique JWT ID for token tracking and revocation"""
    return secrets.token_urlsafe(32)

def create_token(
    data: dict,
    token_type: str,
    expires_delta: Optional[timedelta] = None,
    jti: Optional[str] = None
) -> str:
    """Create JWT token with enhanced security features"""
    to_encode = data.copy()
    
    # Set expiration
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    # Add security claims
    to_encode.update({
        'exp': expire,
        'iat': datetime.now(timezone.utc),
        'nbf': datetime.now(timezone.utc),  # Not before
        'type': token_type,
        'jti': jti or create_jti(),  # JWT ID for revocation
        'iss': 'ruleiq-api',  # Issuer
        'aud': 'ruleiq-client'  # Audience
    })
    
    # Add fingerprint for token binding (optional)
    if 'fingerprint' in data:
        to_encode['fingerprint'] = data['fingerprint']
    
    # Encode token
    if ALGORITHM == 'RS256':
        return jwt.encode(to_encode, PRIVATE_KEY, algorithm=ALGORITHM)
    else:
        return jwt.encode(to_encode, PRIVATE_KEY, algorithm=ALGORITHM)

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    jti: Optional[str] = None
) -> str:
    """Create access token with short expiration"""
    return create_token(
        data,
        'access',
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        jti
    )

def create_refresh_token(
    data: dict,
    jti: Optional[str] = None
) -> str:
    """Create refresh token with longer expiration"""
    return create_token(
        data,
        'refresh',
        timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        jti
    )

def decode_token(token: str) -> Dict[str, Any]:
    """Decode and validate JWT token with comprehensive checks"""
    try:
        # Decode with appropriate key
        if ALGORITHM == 'RS256':
            payload = jwt.decode(
                token,
                PUBLIC_KEY,
                algorithms=[ALGORITHM],
                audience='ruleiq-client',
                issuer='ruleiq-api'
            )
        else:
            payload = jwt.decode(
                token,
                PRIVATE_KEY,
                algorithms=[ALGORITHM]
            )
        
        # Validate token type
        if 'type' not in payload:
            raise NotAuthenticatedException('Invalid token format.')
        
        # Validate JTI (would check against blacklist in production)
        if 'jti' not in payload:
            raise NotAuthenticatedException('Token missing JTI.')
        
        # Validate timestamps
        current_time = datetime.now(timezone.utc)
        
        # Check expiration
        if 'exp' in payload:
            exp_time = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
            if exp_time < current_time:
                raise NotAuthenticatedException('Token has expired.')
        
        # Check not before
        if 'nbf' in payload:
            nbf_time = datetime.fromtimestamp(payload['nbf'], tz=timezone.utc)
            if nbf_time > current_time:
                raise NotAuthenticatedException('Token not yet valid.')
        
        # Check issued at
        if 'iat' in payload:
            iat_time = datetime.fromtimestamp(payload['iat'], tz=timezone.utc)
            # Reject tokens issued in the future (clock skew tolerance: 30 seconds)
            if iat_time > current_time + timedelta(seconds=30):
                raise NotAuthenticatedException('Token issued in the future.')
            
            # Check absolute timeout (12 hours from issue)
            if current_time > iat_time + timedelta(hours=SESSION_ABSOLUTE_TIMEOUT_HOURS):
                raise NotAuthenticatedException('Session has expired. Please log in again.')
        
        return payload
        
    except ExpiredSignatureError:
        raise NotAuthenticatedException('Token has expired. Please log in again.')
    except JWTError as e:
        logger.warning(f"JWT validation failed: {e}")
        raise NotAuthenticatedException('Invalid token.')

async def blacklist_token(
    token: str,
    reason: str = 'logout',
    db: Optional[AsyncSession] = None
) -> None:
    """Add token to blacklist with enhanced tracking"""
    try:
        payload = decode_token(token)
        jti = payload.get('jti')
        
        if jti:
            # Store in Redis with TTL matching token expiration
            from services.redis_client import get_redis_client
            redis = await get_redis_client()
            
            ttl = ACCESS_TOKEN_EXPIRE_MINUTES * 60
            await redis.setex(
                f"blacklist:{jti}",
                ttl,
                json.dumps({
                    'reason': reason,
                    'user_id': payload.get('sub'),
                    'blacklisted_at': datetime.now(timezone.utc).isoformat()
                })
            )
            
            # Log security event
            logger.info(f"Token blacklisted: JTI={jti}, reason={reason}")
            
    except Exception as e:
        logger.error(f"Failed to blacklist token: {e}")

async def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted"""
    try:
        payload = decode_token(token)
        jti = payload.get('jti')
        
        if jti:
            from services.redis_client import get_redis_client
            redis = await get_redis_client()
            
            result = await redis.get(f"blacklist:{jti}")
            return result is not None
            
    except Exception:
        # If we can't validate, consider it blacklisted for safety
        return True
    
    return False

async def check_login_attempts(
    identifier: str,
    db: AsyncSession
) -> Tuple[bool, Optional[datetime]]:
    """Check if user is locked out due to failed login attempts"""
    from services.redis_client import get_redis_client
    redis = await get_redis_client()
    
    # Check lockout
    lockout_key = f"lockout:{identifier}"
    lockout_data = await redis.get(lockout_key)
    
    if lockout_data:
        lockout_until = datetime.fromisoformat(lockout_data.decode())
        if datetime.now(timezone.utc) < lockout_until:
            return False, lockout_until
    
    return True, None

async def record_failed_login(
    identifier: str,
    db: AsyncSession
) -> None:
    """Record failed login attempt and enforce lockout if needed"""
    from services.redis_client import get_redis_client
    redis = await get_redis_client()
    
    # Increment failure count
    attempts_key = f"login_attempts:{identifier}"
    attempts = await redis.incr(attempts_key)
    await redis.expire(attempts_key, 3600)  # Reset after 1 hour
    
    # Check if lockout needed
    if attempts >= MAX_LOGIN_ATTEMPTS:
        lockout_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
        lockout_key = f"lockout:{identifier}"
        await redis.setex(
            lockout_key,
            LOCKOUT_DURATION_MINUTES * 60,
            lockout_until.isoformat()
        )
        
        logger.warning(f"Account locked out due to failed attempts: {identifier}")

async def clear_login_attempts(
    identifier: str,
    db: AsyncSession
) -> None:
    """Clear failed login attempts on successful login"""
    from services.redis_client import get_redis_client
    redis = await get_redis_client()
    
    await redis.delete(f"login_attempts:{identifier}")
    await redis.delete(f"lockout:{identifier}")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
) -> User:
    """Get current user with enhanced security checks"""
    
    # Check if token is blacklisted
    if await is_token_blacklisted(token):
        raise NotAuthenticatedException('Token has been revoked.')
    
    # Decode and validate token
    try:
        payload = decode_token(token)
    except NotAuthenticatedException:
        raise
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise NotAuthenticatedException('Could not validate credentials.')
    
    # Verify token type
    if payload.get('type') != 'access':
        raise NotAuthenticatedException('Invalid token type.')
    
    # Get user ID
    user_id_str = payload.get('sub')
    if not user_id_str:
        raise NotAuthenticatedException('Invalid token payload.')
    
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise NotAuthenticatedException('Invalid user ID format.')
    
    # Get user from database
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalars().first()
    
    if not user:
        raise NotAuthenticatedException('User not found.')
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Account is inactive.'
        )
    
    # Set user context
    user_id_var.set(user.id)
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Ensure user is active with all security checks passed"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Inactive user'
        )
    
    return current_user

# Export enhanced functions
validate_password = EnhancedPasswordValidator.validate
get_password_hash = hash_password

# For backward compatibility
async def get_current_user_from_refresh_token(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db)
) -> User:
    """Get user from refresh token"""
    
    # Check if token is blacklisted
    if await is_token_blacklisted(token):
        raise NotAuthenticatedException('Token has been revoked.')
    
    # Decode token
    try:
        payload = decode_token(token)
    except NotAuthenticatedException:
        raise
    
    # Verify token type
    if payload.get('type') != 'refresh':
        raise NotAuthenticatedException('Invalid refresh token.')
    
    # Get user
    user_id_str = payload.get('sub')
    if not user_id_str:
        raise NotAuthenticatedException('Invalid token payload.')
    
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise NotAuthenticatedException('Invalid user ID format.')
    
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalars().first()
    
    if not user:
        raise NotAuthenticatedException('User not found.')
    
    return user

# Import JSON for blacklist operations
import json