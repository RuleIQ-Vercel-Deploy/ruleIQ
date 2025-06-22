"""
Asynchronous authentication dependencies for ComplianceGPT.
"""

import os
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional
from uuid import UUID

import redis.asyncio as redis
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.context import user_id_var
from config.settings import settings
from core.exceptions import NotAuthenticatedException
from database.db_setup import get_async_db
from database.user import User
from services.auth_service import auth_service

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token", auto_error=False)

# Redis client for token blacklisting
_redis_client: Optional[redis.Redis] = None
_redis_available: Optional[bool] = None

# Fallback in-memory blacklist for when Redis is unavailable
_fallback_blacklist: Dict[str, float] = {}

async def get_redis_client() -> Optional[redis.Redis]:
    """Get or create Redis client for token blacklisting."""
    global _redis_client, _redis_available

    if _redis_available is False:
        return None

    if _redis_client is None:
        try:
            _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
            # Test the connection
            await _redis_client.ping()
            _redis_available = True
        except Exception:
            _redis_available = False
            _redis_client = None
            return None

    return _redis_client

async def blacklist_token(token: str) -> None:
    """Add a token to the blacklist with TTL."""
    redis_client = await get_redis_client()

    if redis_client:
        try:
            # Set TTL to match token expiration (30 minutes for access tokens)
            await redis_client.setex(f"blacklist:{token}", ACCESS_TOKEN_EXPIRE_MINUTES * 60, "1")
            return
        except Exception:
            # Redis failed, fall back to in-memory
            pass

    # Fallback to in-memory blacklist
    import time
    expiry_time = time.time() + (ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    _fallback_blacklist[token] = expiry_time

async def is_token_blacklisted(token: str) -> bool:
    """Check if a token is blacklisted."""
    redis_client = await get_redis_client()

    if redis_client:
        try:
            result = await redis_client.get(f"blacklist:{token}")
            return result is not None
        except Exception:
            # Redis failed, fall back to in-memory
            pass

    # Fallback to in-memory blacklist
    import time
    current_time = time.time()

    # Clean up expired tokens
    expired_tokens = [t for t, exp in _fallback_blacklist.items() if exp < current_time]
    for token_to_remove in expired_tokens:
        _fallback_blacklist.pop(token_to_remove, None)

    return token in _fallback_blacklist

def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    # Add more checks (uppercase, lowercase, digit, special character) as needed
    # For now, basic length check
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit."
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter."
    # Example: check for special character (you might want a more robust check)
    special_characters = "!@#$%^&*()-+?_=,<>/"
    if not any(char in special_characters for char in password):
        return False, f"Password must contain at least one special character: {special_characters}"
    return True, "Password is valid."

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_token(data: dict, token_type: str, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire, "type": token_type, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    return create_token(
        data,
        "access",
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

def create_refresh_token(data: dict) -> str:
    return create_token(data, "refresh", timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))

def validate_token_expiry(payload: Dict) -> None:
    """Validate that token has not expired with additional checks."""
    exp = payload.get("exp")
    if not exp:
        raise NotAuthenticatedException("Token missing expiration time.")

    # Convert to datetime for comparison
    exp_datetime = datetime.fromtimestamp(exp)
    current_time = datetime.utcnow()

    if exp_datetime < current_time:
        raise NotAuthenticatedException("Token has expired. Please log in again.")

    # Optional: Check if token is about to expire (within 5 minutes)
    time_until_expiry = exp_datetime - current_time
    if time_until_expiry.total_seconds() < 300:  # 5 minutes
        # Log warning but don't reject the token
        import logging
        logging.warning(f"Token expires in {time_until_expiry.total_seconds()} seconds")

def decode_token(token: str) -> Optional[Dict]:
    """Decode JWT token with proper error handling for expiry."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Additional expiry validation
        validate_token_expiry(payload)
        return payload
    except jwt.ExpiredSignatureError:
        raise NotAuthenticatedException("Token has expired. Please log in again.")
    except JWTError as e:
        raise NotAuthenticatedException(f"Token validation failed: {str(e)}")

async def get_current_user(token: Optional[str] = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_db)) -> Optional[User]:
    if token is None:
        return None

    # Check if token is blacklisted (logged out)
    if await is_token_blacklisted(token):
        raise NotAuthenticatedException("Token has been invalidated.")

    try:
        payload = decode_token(token)
    except NotAuthenticatedException:
        # Re-raise specific token validation errors (including expiry)
        raise

    if not payload or payload.get("type") != "access":
        raise NotAuthenticatedException("Could not validate credentials.")

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise NotAuthenticatedException("User ID not found in token.")

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise NotAuthenticatedException("Invalid user ID format in token.")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if user is None:
        raise NotAuthenticatedException("User not found.")

    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user is None:
        raise NotAuthenticatedException("Not authenticated")

    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user")

    # Set user_id in contextvar for logging
    user_id_var.set(current_user.id)

    return current_user

async def get_current_user_from_refresh_token(token: Optional[str] = Depends(oauth2_scheme), db: AsyncSession = Depends(get_async_db)) -> Optional[User]:
    if token is None: # Refresh token might be passed in body or header, adjust if oauth2_scheme isn't right for it
        raise NotAuthenticatedException("Refresh token not provided.")

    try:
        payload = decode_token(token)
    except NotAuthenticatedException:
        # Re-raise specific token validation errors (including expiry)
        raise

    if not payload or payload.get("type") != "refresh":
        raise NotAuthenticatedException("Invalid refresh token.")

    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise NotAuthenticatedException("User ID not found in refresh token.")

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise NotAuthenticatedException("Invalid user ID format in refresh token.")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()

    if user is None:
        raise NotAuthenticatedException("User not found for refresh token.")

    # Optionally, check if user is active before allowing refresh
    # if not user.is_active:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user cannot refresh token")

    return user
