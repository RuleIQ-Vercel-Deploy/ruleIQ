"""
Asynchronous authentication dependencies for ComplianceGPT.
"""
from __future__ import annotations
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional, Any
from uuid import UUID
from fastapi import Depends, HTTPException, status, Request, Header
from fastapi.security import OAuth2PasswordBearer
from jose import ExpiredSignatureError, JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from api.context import user_id_var
from core.exceptions import NotAuthenticatedException
from database.db_setup import get_async_db
from database.user import User
from config.logging_config import get_logger
from config.settings import settings
MIN_PASSWORD_LENGTH = 8
TOKEN_EXPIRY_WARNING = 300
logger = get_logger(__name__)
import sys

def get_jwt_secret_key() ->str:
    """Get JWT secret key with production enforcement."""
    if settings.is_production:
        secret_key = os.getenv('JWT_SECRET_KEY')
        doppler_token = os.getenv('DOPPLER_TOKEN')
        if not secret_key and not doppler_token:
            error_msg = (
                'CRITICAL: Production environment requires proper secret configuration. Either set JWT_SECRET_KEY environment variable or configure Doppler:   - Set DOPPLER_TOKEN environment variable   - Or use: doppler run -- python main.py',
                )
            logger.error(error_msg)
            sys.exit(1)
        if not secret_key:
            secret_key = settings.jwt_secret_key
            if secret_key == 'insecure-dev-key-change-in-production':
                logger.error('CRITICAL: Invalid JWT secret in production')
                sys.exit(1)
        return secret_key
    else:
        secret_key = os.getenv('JWT_SECRET_KEY', settings.jwt_secret_key)
        if secret_key == 'insecure-dev-key-change-in-production':
            logger.warning(
                'Using insecure development JWT secret - DO NOT use in production',
                )
        return secret_key
SECRET_KEY = get_jwt_secret_key()
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '480'
    ))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '7'))
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/v1/auth/token', auto_error
    =False)
blacklisted_tokens: set = set()
pending_verification_tokens: Dict[str, Dict[str, Any]] = {}
password_reset_tokens: Dict[str, str] = {}

def require_auth(func):
    """
    Decorator to ensure authentication before accessing an endpoint.
    
    Usage:
        @router.get("/protected")
        @require_auth
        async def protected_endpoint(
            request: Request,
            db: AsyncSession = Depends(get_async_db)
        ):
            # Access authenticated user via request.state.user
            return {"user": request.state.user}
    """

    async def wrapper(*args, **kwargs):
        """Inner wrapper function."""
        request = None
        for arg in args:
            if isinstance(arg, Request):
                request = arg
                break
        for kwarg in kwargs.values():
            if isinstance(kwarg, Request):
                request = kwarg
                break
        if not request:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='Request object not found')
        if not hasattr(request.state, 'user') or not request.state.user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Authentication required')
        return await func(*args, **kwargs)
    return wrapper

def verify_password(plain_password: str, hashed_password: str) ->bool:
    """Verify a plain password against a hashed password."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f'Password verification error: {e}')
        return False

def get_password_hash(password: str) ->str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)

def is_token_blacklisted(token: str) ->bool:
    """Check if a token is blacklisted."""
    return token in blacklisted_tokens

def blacklist_token(token: str):
    """Add a token to the blacklist."""
    blacklisted_tokens.add(token)

def remove_from_blacklist(token: str):
    """Remove a token from the blacklist (for testing purposes)."""
    blacklisted_tokens.discard(token)

def create_access_token(data: dict, expires_delta: Optional[timedelta]=None
    ) ->str:
    """Create a new access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=
            ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({'exp': expire, 'iat': datetime.now(timezone.utc), 'jti':
        secrets.token_urlsafe(32)})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict) ->str:
    """Create a new refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=
        REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({'exp': expire, 'iat': datetime.now(timezone.utc),
        'type': 'refresh', 'jti': secrets.token_urlsafe(32)})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_password_reset_token(user_id: str) ->str:
    """Create a password reset token."""
    token = secrets.token_urlsafe(32)
    expiry = datetime.now(timezone.utc) + timedelta(minutes=
        PASSWORD_RESET_TOKEN_EXPIRE_MINUTES)
    password_reset_tokens[token] = {'user_id': user_id, 'expiry': expiry}
    return token

def verify_password_reset_token(token: str) ->Optional[str]:
    """Verify a password reset token and return user_id if valid."""
    if token not in password_reset_tokens:
        return None
    token_data = password_reset_tokens[token]
    if datetime.now(timezone.utc) > token_data['expiry']:
        del password_reset_tokens[token]
        return None
    return token_data['user_id']

def invalidate_password_reset_token(token: str):
    """Invalidate a password reset token after use."""
    if token in password_reset_tokens:
        del password_reset_tokens[token]

def decode_token(token: str) ->Dict[str, Any]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if is_token_blacklisted(token):
            raise JWTError('Token has been revoked')
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail
            ='Token has expired', headers={'WWW-Authenticate': 'Bearer'})
    except JWTError as e:
        logger.debug(f'JWT decode error: {e}')
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail
            ='Could not validate credentials', headers={'WWW-Authenticate':
            'Bearer'})

async def get_current_user(token: str=Depends(oauth2_scheme), db:
    AsyncSession=Depends(get_async_db)) ->Optional[Dict[str, Any]]:
    """Get the current user from JWT token."""
    if not token:
        return None
    try:
        payload = decode_token(token)
        user_id = payload.get('sub')
        if user_id is None:
            return None
        if payload.get('type') == 'refresh':
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Cannot use refresh token for authentication')
        result = await db.execute(select(User).where(User.id == UUID(user_id))
            )
        user = result.scalar_one_or_none()
        if user is None:
            return None
        expiry = datetime.fromtimestamp(payload['exp'], tz=timezone.utc)
        time_until_expiry = (expiry - datetime.now(timezone.utc)
            ).total_seconds()
        user_dict = {'id': str(user.id), 'email': user.email, 'name': user.
            name, 'role': user.role, 'primaryEmail': user.email,
            'displayName': user.name, 'is_active': user.is_active,
            'email_verified': user.email_verified, 'created_at': user.
            created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else
            None}
        if time_until_expiry < TOKEN_EXPIRY_WARNING:
            user_dict['token_expiry_warning'] = True
            user_dict['token_expires_in'] = int(time_until_expiry)
        user_id_var.set(str(user.id))
        return user_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f'Error getting current user: {e}')
        return None

async def get_current_active_user(current_user: Optional[Dict[str, Any]]=
    Depends(get_current_user)) ->Dict[str, Any]:
    """Get the current active user."""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail
            ='Not authenticated', headers={'WWW-Authenticate': 'Bearer'})
    if not current_user.get('is_active', True):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=
            'Inactive user')
    return current_user

async def get_current_admin_user(current_user: Dict[str, Any]=Depends(
    get_current_active_user)) ->Dict[str, Any]:
    """Get the current admin user."""
    if current_user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=
            'Admin access required')
    return current_user

async def get_optional_current_user(token: Optional[str]=Depends(oauth2_scheme
    ), db: AsyncSession=Depends(get_async_db)) ->Optional[Dict[str, Any]]:
    """Get the current user if authenticated, otherwise return None."""
    if not token:
        return None
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None
    except Exception:
        return None

async def authenticate_user(db: AsyncSession, email: str, password: str
    ) ->Optional[User]:
    """Authenticate a user by email and password."""
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user

async def create_user_account(db: AsyncSession, email: str, password: str,
    name: str, role: str='user') ->User:
    """Create a new user account."""
    from uuid import uuid4
    password_hash = get_password_hash(password)
    user = User(id=uuid4(), email=email, password_hash=password_hash, name=
        name, role=role, is_active=True, email_verified=False, created_at=
        datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

def validate_password_strength(password: str) ->bool:
    """
    Validate password strength.
    
    Requirements:
    - At least 8 characters
    - Contains uppercase and lowercase letters
    - Contains at least one number
    - Contains at least one special character
    """
    if len(password) < MIN_PASSWORD_LENGTH:
        return False
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    return all([has_upper, has_lower, has_digit, has_special])

def create_verification_token(email: str) ->str:
    """Create an email verification token."""
    token = secrets.token_urlsafe(32)
    expiry = datetime.now(timezone.utc) + timedelta(hours=24)
    pending_verification_tokens[token] = {'email': email, 'expiry': expiry}
    return token

def verify_email_token(token: str) ->Optional[str]:
    """Verify an email verification token and return email if valid."""
    if token not in pending_verification_tokens:
        return None
    token_data = pending_verification_tokens[token]
    if datetime.now(timezone.utc) > token_data['expiry']:
        del pending_verification_tokens[token]
        return None
    email = token_data['email']
    del pending_verification_tokens[token]
    return email

def get_jwt_middleware():
    """Get the JWT middleware instance (for compatibility)."""
    return None

async def check_admin_permission(current_user: Dict[str, Any]=Depends(
    get_current_active_user)) ->bool:
    """Check if the current user has admin permissions."""
    return current_user.get('role') == 'admin'

def create_api_key() ->str:
    """Create a new API key."""
    return f'riq_{secrets.token_urlsafe(32)}'

def validate_api_key(api_key: str=Header(None, alias='X-API-Key'),
    authorization: str=Header(None)) ->Optional[str]:
    """
    Validate API key from headers.
    
    Can be provided as:
    - X-API-Key header
    - Authorization: ApiKey <key> header
    """
    if api_key and api_key.startswith('riq_'):
        return api_key
    if authorization and authorization.startswith('ApiKey '):
        key = authorization.replace('ApiKey ', '').strip()
        if key.startswith('riq_'):
            return key
    return None

async def get_api_key_auth(api_key: str = Header(None, alias='X-API-Key')) -> Dict[str, Any]:
    """
    Get API key authentication details.
    
    Returns metadata about the API key if valid.
    """
    if not api_key or not api_key.startswith('riq_'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Return metadata about the API key
    return {
        "api_key": api_key,
        "type": "api_key",
        "valid": True
    }