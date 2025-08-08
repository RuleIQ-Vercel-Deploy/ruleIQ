from datetime import timedelta
from datetime import datetime, timedelta
from uuid import UUID, uuid4

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
from database.db_setup import get_db
from database.user import User
from database.rbac import Role
from services.auth_service import auth_service
from services.rbac_service import RBACService
from config.logging_config import get_logger

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
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(id=uuid4(), email=user.email, hashed_password=hashed_password, is_active=True)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # FIXED: Auto-assign business_user role to new users
    from database.rbac import Role
    from services.rbac_service import RBACService
    
    try:
        rbac_service = RBACService(db)
        business_user_role = db.query(Role).filter(Role.name == "business_user").first()
        
        if business_user_role:
            rbac_service.assign_role_to_user(
                user_id=db_user.id,
                role_id=business_user_role.id,
                granted_by=db_user.id  # Self-assignment for registration
            )
            logger.info(f"Assigned business_user role to new user: {db_user.email}")
        else:
            logger.warning("business_user role not found - user registered without default role")
    except Exception as e:
        logger.error(f"Failed to assign role to new user {db_user.email}: {e}")
        # Don't fail registration if role assignment fails

    # Create tokens for the new user (auto-login after registration)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(db_user.id)})

    return RegisterResponse(
        user=UserResponse(
            id=db_user.id,
            email=db_user.email,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
        ),
        tokens=Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer"),
    )


@router.post("/token", response_model=Token, dependencies=[Depends(auth_rate_limit())])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    # Authenticate user
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    # Create session for tracking
    await auth_service.create_user_session(
        user, access_token, metadata={"login_method": "form_data"}
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/login", response_model=Token, dependencies=[Depends(auth_rate_limit())])
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """Login endpoint - accepts JSON data for compatibility with tests"""
    # Authenticate user
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    # Create session for tracking
    await auth_service.create_user_session(user, access_token, metadata={"login_method": "json"})

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh", response_model=Token, dependencies=[Depends(auth_rate_limit())])
async def refresh_token(refresh_request: dict, db: Session = Depends(get_db)):
    from api.dependencies.auth import decode_token

    refresh_token = refresh_request.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token required"
        )

    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user")

    # Create new tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    """Get current user information from JWT token"""
    from api.dependencies.auth import decode_token

    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user roles and permissions for enhanced response
    try:
        rbac = RBACService(db)
        roles = rbac.get_user_roles(user.id)
        permissions = rbac.get_user_permissions(user.id)
    except Exception:
        # Fallback if RBAC service fails
        roles = []
        permissions = []

    # Create enhanced response with role information
    response_data = UserResponse(
        id=user.id,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
    )
    
    # Add roles and permissions to the response dict
    response_dict = response_data.dict()
    response_dict.update({
        "roles": roles,
        "permissions": permissions,
        "total_permissions": len(permissions),
        "assessment_permissions": [p for p in permissions if 'assessment' in p.lower()]
    })
    
    return response_dict


@router.post("/logout")
async def logout(request: Request, token: str = Depends(oauth2_scheme)):
    """Logout endpoint that blacklists the current token and invalidates sessions."""
    from api.dependencies.auth import blacklist_token, decode_token

    if token:
        # Enhanced blacklist with metadata
        await blacklist_token(
            token,
            reason="user_logout",
            ip_address=getattr(request.client, "host", None),
            user_agent=request.headers.get("user-agent"),
            metadata={"logout_timestamp": datetime.utcnow().isoformat()},
        )

        # Also invalidates sessions
        try:
            payload = decode_token(token)
            if payload and payload.get("sub"):
                user_id = UUID(payload["sub"])
                await auth_service.logout_user(user_id)
        except Exception:
            # If token decode fails, still consider logout successful
            pass

    return {"message": "Successfully logged out"}


@router.post("/assign-default-role")
async def assign_default_role(
    db: Session = Depends(get_db), 
    token: str = Depends(oauth2_scheme)
):
    """
    Assign the business_user role to the current authenticated user.
    
    This endpoint allows test users to self-assign the business_user role
    without requiring admin permissions, making testing seamless.
    """
    from api.dependencies.auth import decode_token
    
    # Decode the JWT token to get user ID
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user exists and is active
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Get RBAC service and business_user role
        rbac = RBACService(db)
        business_user_role = db.query(Role).filter(Role.name == "business_user").first()
        
        if not business_user_role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="business_user role not found. Please contact administrator."
            )

        # Check if user already has the role
        existing_roles = rbac.get_user_roles(user.id)
        if any(role['name'] == 'business_user' for role in existing_roles):
            return {
                "success": True,
                "message": "User already has business_user role",
                "user_id": str(user.id),
                "email": user.email,
                "roles": existing_roles
            }

        # Assign the business_user role (self-assignment)
        rbac.assign_role_to_user(
            user_id=user.id,
            role_id=business_user_role.id,
            granted_by=user.id  # Self-assignment
        )

        # Get updated user roles and permissions
        updated_roles = rbac.get_user_roles(user.id)
        updated_permissions = rbac.get_user_permissions(user.id)

        return {
            "success": True,
            "message": "business_user role assigned successfully",
            "user_id": str(user.id),
            "email": user.email,
            "roles": updated_roles,
            "permissions": updated_permissions,
            "assessment_permissions": [p for p in updated_permissions if 'assessment' in p.lower()]
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to assign role: {str(e)}"
        )
