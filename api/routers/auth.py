from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies.stack_auth import get_current_stack_user
from api.schemas.models import UserResponse

router = APIRouter()


@router.post("/register", status_code=status.HTTP_410_GONE)
async def register():
    """Legacy registration endpoint - now handled by Stack Auth"""
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Registration is now handled by Stack Auth. Please use the Stack Auth SDK or redirect to /handler/sign-up"
    )


@router.post("/token", status_code=status.HTTP_410_GONE)
async def login_for_access_token():
    """Legacy OAuth2 token endpoint - now handled by Stack Auth"""
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Token authentication is now handled by Stack Auth. Please use the Stack Auth SDK or redirect to /handler/sign-in"
    )


@router.post("/login", status_code=status.HTTP_410_GONE)
async def login():
    """Legacy login endpoint - now handled by Stack Auth"""
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Login is now handled by Stack Auth. Please use the Stack Auth SDK or redirect to /handler/sign-in"
    )


@router.post("/refresh", status_code=status.HTTP_410_GONE)
async def refresh_token():
    """Legacy token refresh endpoint - now handled by Stack Auth"""
    raise HTTPException(
        status_code=status.HTTP_410_GONE,
        detail="Token refresh is now handled by Stack Auth. Please use the Stack Auth SDK for automatic token refresh"
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user: dict = Depends(get_current_stack_user)):
    """Get current user information from Stack Auth"""
    return UserResponse(
        id=current_user["id"],
        email=current_user.get("primaryEmail", current_user.get("email", "")),
        is_active=True,  # Stack Auth users are active by definition
        created_at=current_user.get("createdAt", "2024-01-01T00:00:00Z"),
    )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_stack_user)):
    """Logout user - Stack Auth handles session management"""
    # Note: Stack Auth handles logout through the frontend SDK
    # This endpoint provides confirmation for API clients
    return {"message": "Successfully logged out", "user_id": current_user["id"]}
