"""
from __future__ import annotations

Minimal FastAPI app to test JWT authentication
This bypasses all startup checks to focus on JWT testing
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Load environment
load_dotenv(".env.local")

# Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "dev-jwt-secret-key-change-for-production")
ALGORITHM = "HS256"

app = FastAPI(title="JWT Test Server")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

print(f"[JWT TEST SERVER] Using JWT_SECRET: {JWT_SECRET[:10]}...")

class TestRequest(BaseModel):
    question_id: str
    """Class for TestRequest"""
    question_text: str
    framework_id: str

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Verify JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token validation failed: Signature verification failed.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        print(f"[AUTH] Verifying token: {token[:50]}...")
        print(f"[AUTH] Using secret: {JWT_SECRET[:10]}...")

        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        print(f"[AUTH] Token valid for user: {user_id}")
        return user_id

    except Exception as e:
        print(f"[AUTH] Token validation failed: {e}")
        raise credentials_exception

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "jwt_configured": True}

@app.get("/debug/config")
async def debug_config():
    """Debug endpoint to check JWT configuration"""
    return {
        "jwt_secret_first_10": JWT_SECRET[:10] if JWT_SECRET else None,
        "jwt_secret_length": len(JWT_SECRET) if JWT_SECRET else 0,
        "algorithm": ALGORITHM,
    }

@app.post("/api/v1/ai-assessments/soc2/help")
async def test_ai_endpoint(
    request: TestRequest, current_user: str = Depends(get_current_user)
):
    """Test endpoint that requires authentication"""
    return {
        "status": "success",
        "message": f"JWT authentication working! User: {current_user}",
        "request": request.dict(),
    }

if __name__ == "__main__":
    import uvicorn

    print("\nStarting JWT Test Server...")
    print(f"JWT_SECRET configured: {JWT_SECRET[:20]}...")
    print("\nTest with: python simple_jwt_test.py")
    uvicorn.run(app, host="127.0.0.1", port=8000)
