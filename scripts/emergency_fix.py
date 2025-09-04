from __future__ import annotations
import logging
logger = logging.getLogger(__name__)
import subprocess
import sys
import os

def install_missing_dependencies() ->None:
    """Install all missing dependencies"""
    logger.info('🔧 Installing missing dependencies...')
    dependencies = ['asyncpg', 'mistralai', 'httpx', 'redis', 'celery',
        'fastapi', 'uvicorn', 'pydantic', 'sqlalchemy', 'alembic',
        'passlib[bcrypt]', 'python-jose[cryptography]', 'python-multipart',
        'email-validator', 'python-dotenv']
    for dep in dependencies:
        logger.info('📦 Installing %s...' % dep)
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
    logger.info('✅ All dependencies installed!')

def create_minimal_backend() ->None:
    """Create a minimal working backend"""
    logger.info('🚀 Creating minimal backend...')
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
            "compliance_score": 0,
        },
    }

# Mock assessments endpoint
@app.get("/api/assessments")
async def get_assessments():
    return {
        "assessments": [],
        "total": 0,
        "page": 1,
        "page_size": 50,
    }

# Mock policies endpoint
@app.get("/api/policies")
async def get_policies():
    return {
        "policies": [],
        "total": 0,
        "page": 1,
        "page_size": 50,
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
            "token_type": "bearer",
        }
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/api/auth/me")
async def get_me():
    return {
        "id": 1,
        "email": "test@example.com",
        "full_name": "Test User",
        "is_active": True,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
    with open('minimal_backend.py', 'w') as f:
        f.write(minimal_backend)
    logger.info('✅ Minimal backend created!')

def main() ->None:
    logger.info('🚨 RuleIQ Emergency Fix Script')
    """Main"""
    logger.info('=' * 40)
    if not os.path.exists('main.py'):
        logger.info('❌ Please run this script from the RuleIQ root directory')
        return
    install_missing_dependencies()
    create_minimal_backend()
    logger.info('\n✅ Emergency fix complete!')
    logger.info('\n📋 Next steps:')
    logger.info('1. Run the minimal backend: python3 minimal_backend.py')
    logger.info('2. This will get your frontend working temporarily')
    logger.info('3. Implement Stack Auth for a permanent solution')
    logger.info('\n🎯 To run minimal backend:')
    logger.info('   python3 minimal_backend.py')

if __name__ == '__main__':
    main()
