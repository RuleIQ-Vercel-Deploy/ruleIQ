from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from uuid import UUID, uuid4

import requests
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.dependencies.auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    oauth2_scheme,
    verify_password,
)
from api.middleware.rate_limiter import auth_rate_limit
from api.schemas.models import Token, UserCreate, UserResponse
from config.logging_config import get_logger
from database.db_setup import get_db
from database.rbac import Role
from database.user import User
from services.auth_service import auth_service
from services.rbac_service import RBACService
from services.security_alerts import SecurityAlertService

logger = get_logger(__name__)


class LoginRequest(BaseModel):
    email: str
    password: str


router = APIRouter()


class RegisterResponse(BaseModel):
    user: UserResponse
    tokens: Token


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(auth_rate_limit())],
)
async def register(user: UserCreate, db: Session = Depends(get_db)) -> Any:
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")
    hashed_password = get_password_hash(user.password)
    db_user = User(id=uuid4(), email=user.email, hashed_password=hashed_password, is_active=True)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    try:
        rbac_service = RBACService(db)
        business_user_role = db.query(Role).filter(Role.name == "business_user").first()
        if business_user_role:
            rbac_service.assign_role_to_user(user_id=db_user.id, role_id=business_user_role.id, granted_by=db_user.id)
            logger.info("Assigned business_user role to new user: %s" % db_user.email)
        else:
            logger.warning(
                "business_user role not found - user registered without default role",
            )
    except Exception as e:
        logger.error("Failed to assign role to new user %s: %s" % (db_user.email, e))
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(db_user.id)}, expires_delta=access_token_expires)
    refresh_token = create_refresh_token(data={"sub": str(db_user.id)})
    return RegisterResponse(
        user=UserResponse(
            id=db_user.id, email=db_user.email, is_active=db_user.is_active, created_at=db_user.created_at
        ),
        tokens=Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer"),
    )


@router.post("/token", response_model=Token, dependencies=[Depends(auth_rate_limit())])
async def login_for_access_token(
    request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        logger.warning("Login attempt for non-existent user: %s from IP: %s" % (form_data.username, ip_address))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.password, user.hashed_password):
        try:
            from database.db_setup import async_session_maker

            async with async_session_maker() as async_db:
                await SecurityAlertService.log_and_check_login_attempt(
                    db=async_db, user=user, success=False, ip_address=ip_address, user_agent=user_agent
                )
        except Exception as e:
            logger.error("Failed to log security event: %s" % e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        from database.db_setup import async_session_maker

        async with async_session_maker() as async_db:
            await SecurityAlertService.log_and_check_login_attempt(
                db=async_db, user=user, success=True, ip_address=ip_address, user_agent=user_agent
            )
    except Exception as e:
        logger.error("Failed to log successful login: %s" % e)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)
    await auth_service.create_user_session(user, access_token, metadata={"login_method": "form_data", "ip": ip_address})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/login", response_model=Token, dependencies=[Depends(auth_rate_limit())])
async def login(request: Request, login_data: LoginRequest, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Login endpoint - accepts JSON data for compatibility with tests"""
    ip_address = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        logger.warning("Login attempt for non-existent user: %s from IP: %s" % (login_data.email, ip_address))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(login_data.password, user.hashed_password):
        try:
            from database.db_setup import async_session_maker

            async with async_session_maker() as async_db:
                await SecurityAlertService.log_and_check_login_attempt(
                    db=async_db, user=user, success=False, ip_address=ip_address, user_agent=user_agent
                )
        except Exception as e:
            logger.error("Failed to log security event: %s" % e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        from database.db_setup import async_session_maker

        async with async_session_maker() as async_db:
            await SecurityAlertService.log_and_check_login_attempt(
                db=async_db, user=user, success=True, ip_address=ip_address, user_agent=user_agent
            )
    except Exception as e:
        logger.error("Failed to log successful login: %s" % e)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)
    await auth_service.create_user_session(user, access_token, metadata={"login_method": "json", "ip": ip_address})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token)
async def refresh_token(token: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Refresh access token using refresh token"""
    from jose import JWTError, jwt

    from config.settings import get_settings

    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        if user_id is None or payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}


@router.post("/logout", dependencies=[Depends(oauth2_scheme)])
async def logout(token: str = Depends(oauth2_scheme)) -> Dict[str, str]:
    """Logout user by invalidating their session"""
    await auth_service.revoke_token(token)
    return {"message": "Successfully logged out"}


@router.post("/google/callback")
async def google_callback(token: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Process Google OAuth callback - verifies token and creates/updates user"""
    import google.auth.transport.requests
    from google.oauth2 import id_token

    try:
        request = google.auth.transport.requests.Request()
        from config.settings import get_settings

        settings = get_settings()
        if not settings.google_client_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Google OAuth not configured")
        idinfo = id_token.verify_oauth2_token(token, request, settings.google_client_id)
        email = idinfo.get("email")
        if not email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not provided in Google token")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                id=uuid4(),
                email=email,
                hashed_password="",
                is_active=True,
                google_id=idinfo.get("sub"),
                google_picture=idinfo.get("picture"),
                google_name=idinfo.get("name"),
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            try:
                rbac_service = RBACService(db)
                business_user_role = db.query(Role).filter(Role.name == "business_user").first()
                if business_user_role:
                    rbac_service.assign_role_to_user(user_id=user.id, role_id=business_user_role.id, granted_by=user.id)
            except Exception as e:
                logger.error("Failed to assign role to Google user: %s" % e)
        else:
            user.google_id = idinfo.get("sub")
            user.google_picture = idinfo.get("picture")
            user.google_name = idinfo.get("name")
            db.commit()
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": str(user.id)}, expires_delta=access_token_expires)
        refresh_token = create_refresh_token(data={"sub": str(user.id)})
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {"email": user.email, "name": user.google_name, "picture": user.google_picture},
        }
    except ValueError as e:
        logger.error("Google token verification failed: %s" % e)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Google token")
    except Exception as e:
        logger.error("Google OAuth error: %s" % e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Authentication failed")
