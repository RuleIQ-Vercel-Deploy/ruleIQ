"""
Google OAuth2 authentication router
Handles Google Sign-In integration for the ruleIQ platform
"""

import secrets
from datetime import timedelta
from uuid import uuid4
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
import httpx

from api.dependencies.auth import (
    create_access_token,
    create_refresh_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from api.middleware.rate_limiter import auth_rate_limit
from api.schemas.models import Token, UserResponse
from config.settings import get_settings
from database.db_setup import get_db
from database.user import User
from services.auth_service import auth_service

settings = get_settings()
router = APIRouter(tags=["Google OAuth"])


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


@router.get("/login")
async def google_login(request: Request):
    """
    Initiate Google OAuth2 login flow
    Redirects user to Google's authorization page
    """
    # Check if Google OAuth is configured
    if (
        not settings.google_client_id
        or settings.google_client_id == "your-dev-google-client-id"
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured. Please contact support.",
        )

    # Generate and store state parameter for CSRF protection
    state = secrets.token_urlsafe(32)

    # Store state in session or cache for validation
    # For now, we'll use a simple in-memory store (should use Redis in production)
    if not hasattr(google_login, "_states"):
        google_login._states = {}
    google_login._states[state] = True

    # Build Google OAuth URL
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={settings.google_client_id}"
        f"&redirect_uri=http://localhost:8000/api/v1/auth/google/callback"
        "&response_type=code"
        "&scope=openid email profile"
        "&access_type=offline"
        "&prompt=consent"
        f"&state={state}"
    )

    return RedirectResponse(url=google_auth_url)


@router.get("/callback")
async def google_callback(
    request: Request,
    code: Optional[str] = None,
    state: Optional[str] = None,
    error: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Handle Google OAuth2 callback
    Exchanges authorization code for access token and user info
    """
    # Check for OAuth errors
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google OAuth error: {error}",
        )

    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Authorization code not provided",
        )

    # Validate state parameter (CSRF protection)
    if not state or not getattr(google_login, "_states", {}).get(state):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state parameter"
        )

    # Clean up used state
    if hasattr(google_login, "_states"):
        google_login._states.pop(state, None)

    try:
        # Exchange authorization code for access token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": "http://localhost:8000/api/v1/auth/google/callback",
                },
            )
            token_response.raise_for_status()
            token_data = token_response.json()

            # Get user info from Google
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {token_data['access_token']}"},
            )
            user_response.raise_for_status()
            user_info = GoogleUserInfo(**user_response.json())

    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to authenticate with Google: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}",
        )

    # Check if email is verified
    if not user_info.verified_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified with Google",
        )

    # Check if user exists
    db_user = db.query(User).filter(User.email == user_info.email).first()
    is_new_user = False

    if not db_user:
        # Create new user
        is_new_user = True
        db_user = User(
            id=uuid4(),
            email=user_info.email,
            hashed_password="",  # No password for OAuth users
            is_active=True,
            full_name=user_info.name,
            google_id=user_info.id,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    # Update Google ID if not set
    elif not db_user.google_id:
        db_user.google_id = user_info.id
        db.commit()

    # Create JWT tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(db_user.id)})

    # Create session for tracking
    await auth_service.create_user_session(
        db_user,
        access_token,
        metadata={"login_method": "google_oauth", "google_id": user_info.id},
    )

    # Redirect to frontend with tokens (in production, use secure HTTP-only cookies)
    redirect_url = f"http://localhost:3000/auth/callback?access_token={access_token}&refresh_token={refresh_token}&new_user={is_new_user}"

    return RedirectResponse(url=redirect_url)


@router.post("/mobile-login", response_model=GoogleAuthResponse)
async def google_mobile_login(
    google_token: str,
    db: Session = Depends(get_db),
    _: None = Depends(auth_rate_limit()),
):
    """
    Handle Google OAuth for mobile apps
    Accepts Google ID token directly from mobile client
    """
    # Check if Google OAuth is configured
    if (
        not settings.google_client_id
        or settings.google_client_id == "your-dev-google-client-id"
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth is not configured",
        )

    try:
        # Verify Google ID token
        async with httpx.AsyncClient() as client:
            verify_response = await client.get(
                f"https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={google_token}"
            )
            verify_response.raise_for_status()
            token_info = verify_response.json()

            # Validate token audience
            if token_info.get("aud") != settings.google_client_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token audience",
                )

            # Get user info from token
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Google token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token verification error: {str(e)}",
        )

    # Check if email is verified
    if not user_info.verified_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not verified with Google",
        )

    # Check if user exists
    db_user = db.query(User).filter(User.email == user_info.email).first()
    is_new_user = False

    if not db_user:
        # Create new user
        is_new_user = True
        db_user = User(
            id=uuid4(),
            email=user_info.email,
            hashed_password="",  # No password for OAuth users
            is_active=True,
            full_name=user_info.name,
            google_id=user_info.id,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    # Update Google ID if not set
    elif not db_user.google_id:
        db_user.google_id = user_info.id
        db.commit()

    # Create JWT tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(db_user.id)})

    # Create session for tracking
    await auth_service.create_user_session(
        db_user,
        access_token,
        metadata={"login_method": "google_oauth_mobile", "google_id": user_info.id},
    )

    return GoogleAuthResponse(
        user=UserResponse(
            id=db_user.id,
            email=db_user.email,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
        ),
        tokens=Token(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        ),
        is_new_user=is_new_user,
    )
