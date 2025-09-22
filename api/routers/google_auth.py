"""
from __future__ import annotations

Google OAuth2 authentication router
Handles Google Sign-In integration for the ruleIQ platform
"""

import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from urllib.parse import urlencode
from uuid import uuid4

import httpx
from fastapi import APIRouter, Body, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.dependencies.auth import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, create_refresh_token
from api.middleware.rate_limiter import auth_rate_limit
from api.schemas.models import Token, UserResponse
from config.cache import cache_manager
from config.settings import get_settings
from database.db_setup import get_db
from database.user import User
from services.auth_service import auth_service

settings = get_settings()
router = APIRouter(tags=["Google OAuth"])

# OAuth state storage - using cache for multi-process safety
OAUTH_STATE_PREFIX = "oauth:state:"
OAUTH_STATE_TTL = 600  # 10 minutes


class GoogleUserInfo(BaseModel):
    """Google user information from OAuth response"""

    id: str
    email: str
    verified_email: bool
    name: str
    given_name: str
    family_name: str
    picture: str


class GoogleAuthResponse(BaseModel):
    """Response from Google OAuth login"""

    user: UserResponse
    tokens: Token
    is_new_user: bool


class GoogleMobileLoginRequest(BaseModel):
    """Request body for mobile Google OAuth login"""

    google_token: str


@router.get("/login")
async def google_login(request: Request) -> Any:
    """
    Initiate Google OAuth2 login flow
    Redirects user to Google's authorization page
    """
    if not settings.google_client_id or settings.google_client_id == "your-dev-google-client-id":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured. Please contact support.",
        )

    # Generate secure state token
    state = secrets.token_urlsafe(32)

    # Store state in cache with expiry
    state_key = f"{OAUTH_STATE_PREFIX}{state}"
    state_data = {
        "created_at": datetime.utcnow().isoformat(),
        "request_url": str(request.url)
    }
    await cache_manager.set(state_key, state_data, ttl=OAUTH_STATE_TTL)

    # Build redirect URI dynamically
    # Use settings for base URL or derive from request
    base_url = getattr(settings, 'base_url', f"{request.url.scheme}://{request.url.netloc}")
    redirect_uri = f"{base_url}/api/v1/auth/google/callback"

    # Build Google OAuth URL using urlencode for proper escaping
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
        "state": state
    }

    google_auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
    return RedirectResponse(url=google_auth_url)


@router.get("/callback")
async def google_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db),
) -> Any:
    """
    Handle Google OAuth2 callback
    Exchanges authorization code for access token and user info
    """
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Google OAuth error: {error}")
    if not code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Authorization code not provided")

    # Validate state parameter using cache
    if not state:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="State parameter missing")

    state_key = f"{OAUTH_STATE_PREFIX}{state}"
    state_data = await cache_manager.get(state_key)

    if not state_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired state parameter")

    # Delete state from cache immediately after validation
    await cache_manager.delete(state_key)

    # Build redirect URI dynamically (same as in login)
    base_url = getattr(settings, 'base_url', f"{request.url.scheme}://{request.url.netloc}")
    redirect_uri = f"{base_url}/api/v1/auth/google/callback"

    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": redirect_uri,
                },
            )
            token_response.raise_for_status()
            token_data = token_response.json()
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )
            user_response.raise_for_status()
            user_info = GoogleUserInfo(**user_response.json())
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to authenticate with Google: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Authentication error: {str(e)}")
    if not user_info.verified_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not verified with Google")
    db_user = db.query(User).filter(User.email == user_info.email).first()
    is_new_user = False
    if not db_user:
        is_new_user = True
        # Security: Generate secure random password hash for OAuth users
        # This prevents authentication bypass vulnerabilities
        import hashlib

        random_password = secrets.token_urlsafe(32)
        secure_hash = hashlib.sha256(f"{random_password}{user_info.email}".encode()).hexdigest()

        db_user = User(
            id=uuid4(),
            email=user_info.email,
            hashed_password=secure_hash,  # Secure hash instead of empty string
            is_active=True,
            full_name=user_info.name,
            google_id=user_info.id,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    elif not db_user.google_id:
        db_user.google_id = user_info.id
        db.commit()
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(db_user.id)}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": str(db_user.id)})
    await auth_service.create_user_session(
        db_user, access_token, metadata={"login_method": "google_oauth", "google_id": user_info.id}
    )
    redirect_url = f"http://localhost:3000/auth/callback?access_token={access_token}&refresh_token={refresh_token}&new_user={is_new_user}"
    return RedirectResponse(url=redirect_url)


@router.post("/mobile-login", response_model=GoogleAuthResponse)
async def google_mobile_login(
    google_token: Optional[str] = None,
    body: Optional[GoogleMobileLoginRequest] = None,
    db: Session = Depends(get_db),
    _: None = Depends(auth_rate_limit())
) -> Any:
    """
    Handle Google OAuth for mobile apps
    Accepts Google ID token directly from mobile client
    Supports both JSON body (preferred) and query parameter for compatibility
    """
    # Accept token from body (preferred) or query parameter (legacy)
    token = body.google_token if body else google_token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google token must be provided in request body or as query parameter"
        )

    if not settings.google_client_id or settings.google_client_id == "your-dev-google-client-id":
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Google OAuth is not configured")
    try:
        async with httpx.AsyncClient() as client:
            verify_response = await client.get(
                f"https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={token}"
            )
            verify_response.raise_for_status()
            token_info = verify_response.json()
            if token_info.get("aud") != settings.google_client_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token audience")
            user_info = GoogleUserInfo(
                id=token_info["sub"],
                email=token_info["email"],
                verified_email=token_info.get("email_verified", False),
                name=token_info.get("name", ""),
                given_name=token_info.get("given_name", ""),
                family_name=token_info.get("family_name", ""),
                picture=token_info.get("picture", ""),
            )
    except httpx.HTTPError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Google token")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Token verification error: {str(e)}"
        )
    if not user_info.verified_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not verified with Google")
    db_user = db.query(User).filter(User.email == user_info.email).first()
    is_new_user = False
    if not db_user:
        is_new_user = True
        # Security: Generate secure random password hash for OAuth users
        # This prevents authentication bypass vulnerabilities
        import hashlib

        random_password = secrets.token_urlsafe(32)
        secure_hash = hashlib.sha256(f"{random_password}{user_info.email}".encode()).hexdigest()

        db_user = User(
            id=uuid4(),
            email=user_info.email,
            hashed_password=secure_hash,  # Secure hash instead of empty string
            is_active=True,
            full_name=user_info.name,
            google_id=user_info.id,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    elif not db_user.google_id:
        db_user.google_id = user_info.id
        db.commit()
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(db_user.id)}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": str(db_user.id)})
    await auth_service.create_user_session(
        db_user, access_token, metadata={"login_method": "google_oauth_mobile", "google_id": user_info.id}
    )
    return GoogleAuthResponse(
        user=UserResponse(
            id=db_user.id, email=db_user.email, is_active=db_user.is_active, created_at=db_user.created_at
        ),
        tokens=Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer"),
        is_new_user=is_new_user,
    )
