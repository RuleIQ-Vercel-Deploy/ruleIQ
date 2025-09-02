# emergency_fix.py - Quick fix to get your backend running
import subprocess
import sys
import os


def install_missing_dependencies() -> None:
    """Install all missing dependencies"""
    print("🔧 Installing missing dependencies...")

    dependencies = [
        "asyncpg",
        "mistralai",
        "httpx",
        "redis",
        "celery",
        "fastapi",
        "uvicorn",
        "pydantic",
        "sqlalchemy",
        "alembic",
        "passlib[bcrypt]",
        "python-jose[cryptography]",
        "python-multipart",
        "email-validator",
        "python-dotenv",
    ]

    for dep in dependencies:
        print(f"📦 Installing {dep}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", dep])

    print("✅ All dependencies installed!")


def create_minimal_backend() -> None:
    """Create a minimal working backend"""
    print("🚀 Creating minimal backend...")

    minimal_backend = """# minimal_backend.py - Emergency backend to test with
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os

app = FastAPI(title="RuleIQ Emergency Backend")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Emergency backend running"}

# Mock dashboard endpoint
@app.get("/api/dashboard")
async def get_dashboard():
    return {
        "message": "Dashboard data would go here",
        "user": {"id": "test-user", "email": "test@example.com"},
        "stats": {
            "assessments": 0,
            "policies": 0,
            "compliance_score": 0
        }
    }

# Mock assessments endpoint
@app.get("/api/assessments")
async def get_assessments():
    return {
        "assessments": [],
        "total": 0,
        "page": 1,
        "page_size": 50
    }

# Mock policies endpoint
@app.get("/api/policies")
async def get_policies():
    return {
        "policies": [],
        "total": 0,
        "page": 1,
        "page_size": 50
    }

# Mock auth endpoints (temporary)
class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/auth/login")
async def login(request: LoginRequest):
    # This is just for testing - replace with Stack Auth
    if request.username == "test@example.com" and request.password == "password":
        return {
            "access_token": "fake-jwt-token",
            "refresh_token": "fake-refresh-token",
            "token_type": "bearer"
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/auth/me")
async def get_me():
    return {
        "id": 1,
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""

    with open("minimal_backend.py", "w") as f:
        f.write(minimal_backend)

    print("✅ Minimal backend created!")


def main() -> None:
    print("🚨 RuleIQ Emergency Fix Script")
    print("=" * 40)

    # Check current directory
    if not os.path.exists("main.py"):
        print("❌ Please run this script from the RuleIQ root directory")
        return

    # Install dependencies
    install_missing_dependencies()

    # Create minimal backend
    create_minimal_backend()

    print("\n✅ Emergency fix complete!")
    print("\n📋 Next steps:")
    print("1. Run the minimal backend: python3 minimal_backend.py")
    print("2. This will get your frontend working temporarily")
    print("3. Implement Stack Auth for a permanent solution")
    print("\n🎯 To run minimal backend:")
    print("   python3 minimal_backend.py")


if __name__ == "__main__":
    main()
