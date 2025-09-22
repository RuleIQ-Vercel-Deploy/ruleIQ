"""
Optimized Vercel serverless handler for ruleIQ application.
This handler is designed for Vercel's serverless environment with optimizations for:
- Cold start performance
- Connection management
- Feature flags for serverless constraints
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

# Configure logging for serverless
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Environment detection
IS_VERCEL = os.getenv('VERCEL', '').lower() == '1' or os.getenv('VERCEL_ENV') is not None
IS_PRODUCTION = os.getenv('ENVIRONMENT', 'development').lower() == 'production'

# Feature flags for serverless environment
ENABLE_MONITORING = not IS_VERCEL and os.getenv('ENABLE_MONITORING', 'false').lower() == 'true'
ENABLE_BACKGROUND_TASKS = not IS_VERCEL
ENABLE_WEBSOCKETS = not IS_VERCEL
ENABLE_REDIS_CACHE = os.getenv('REDIS_URL') is not None and not IS_VERCEL
ENABLE_NEO4J = os.getenv('NEO4J_URI') is not None and not IS_VERCEL

# Create FastAPI app without lifespan for serverless
app = FastAPI(
    title="ruleIQ API",
    description="Compliance automation platform API - Vercel optimized",
    version="2.0.0",
    docs_url="/api/docs" if not IS_PRODUCTION else None,
    redoc_url="/api/redoc" if not IS_PRODUCTION else None,
)

# Essential middleware only
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv('CORS_ORIGINS', '*').split(','),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    import uuid
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

# Basic security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Global exception handler
@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Health check endpoints
@app.get("/api/health")
async def health_check():
    """Simple health check endpoint for Vercel."""
    return {
        "status": "healthy",
        "environment": "vercel" if IS_VERCEL else "local",
        "version": "2.0.0"
    }

@app.get("/api/ready")
async def readiness_check():
    """Readiness check with basic database connectivity test."""
    checks = {
        "api": "ready",
        "environment": "vercel" if IS_VERCEL else "local"
    }

    # Test database connectivity if available
    try:
        from database.session import get_db
        db = next(get_db())
        db.execute("SELECT 1")
        checks["database"] = "connected"
    except Exception as e:
        logger.warning(f"Database check failed: {e}")
        checks["database"] = "unavailable"

    return checks

# Import and include essential routers with /api/v1/* prefix
# Authentication & Users
from api.routers.auth import router as auth_router
from api.routers.users import router as users_router
app.include_router(auth_router, prefix="/api/v1", tags=["Authentication"])
app.include_router(users_router, prefix="/api/v1", tags=["Users"])

# Core Business Logic
from api.routers.assessments import router as assessments_router
from api.routers.frameworks import router as frameworks_router
from api.routers.policies import router as policies_router
from api.routers.evidence import router as evidence_router
app.include_router(assessments_router, prefix="/api/v1", tags=["Assessments"])
app.include_router(frameworks_router, prefix="/api/v1", tags=["Frameworks"])
app.include_router(policies_router, prefix="/api/v1", tags=["Policies"])
app.include_router(evidence_router, prefix="/api/v1", tags=["Evidence"])

# Business & Profiles
from api.routers.business_profiles import router as business_profiles_router
from api.routers.freemium import router as freemium_router
app.include_router(business_profiles_router, prefix="/api/v1", tags=["Business Profiles"])
app.include_router(freemium_router, prefix="/api/v1", tags=["Freemium"])

# Implementation & Reports
from api.routers.implementation import router as implementation_router
from api.routers.reports import router as reports_router
app.include_router(implementation_router, prefix="/api/v1", tags=["Implementation"])
app.include_router(reports_router, prefix="/api/v1", tags=["Reports"])

# AI Features (conditionally loaded)
if os.getenv('GOOGLE_AI_API_KEY') or os.getenv('OPENAI_API_KEY'):
    try:
        from api.routers.ai_assessments import router as ai_assessments_router
        from api.routers.ai_policy import router as ai_policy_router
        from api.routers.iq_agent import router as iq_agent_router
        from api.routers.chat import router as chat_router
        app.include_router(ai_assessments_router, prefix="/api/v1", tags=["AI Assessments"])
        app.include_router(ai_policy_router, prefix="/api/v1", tags=["AI Policy"])
        app.include_router(iq_agent_router, prefix="/api/v1", tags=["IQ Agent"])
        app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])
    except ImportError as e:
        logger.warning(f"AI routers not loaded: {e}")

# Google Auth (if configured)
if os.getenv('GOOGLE_CLIENT_ID'):
    try:
        from api.routers.google_auth import router as google_auth_router
        app.include_router(google_auth_router, prefix="/api/v1", tags=["Google Auth"])
    except ImportError as e:
        logger.warning(f"Google auth router not loaded: {e}")

# Dashboard & Analytics
try:
    from api.routers.dashboard import router as dashboard_router
    app.include_router(dashboard_router, prefix="/api/v1", tags=["Dashboard"])
except ImportError as e:
    logger.warning(f"Dashboard router not loaded: {e}")

# Compliance
try:
    from api.routers.compliance import router as compliance_router
    app.include_router(compliance_router, prefix="/api/v1", tags=["Compliance"])
except ImportError as e:
    logger.warning(f"Compliance router not loaded: {e}")

# Payment (if Stripe configured)
if os.getenv('STRIPE_SECRET_KEY'):
    try:
        from api.routers.payment import router as payment_router
        app.include_router(payment_router, prefix="/api/v1", tags=["Payment"])
    except ImportError as e:
        logger.warning(f"Payment router not loaded: {e}")

# Integrations
try:
    from api.routers.integrations import router as integrations_router
    app.include_router(integrations_router, prefix="/api/v1", tags=["Integrations"])
except ImportError as e:
    logger.warning(f"Integrations router not loaded: {e}")

# Feedback
try:
    from api.routers.feedback import router as feedback_router
    app.include_router(feedback_router, prefix="/api/v1", tags=["Feedback"])
except ImportError as e:
    logger.warning(f"Feedback router not loaded: {e}")

# Note: Excluding the following for serverless:
# - WebSocket endpoints (ai_cost_websocket, evidence_collection WebSocket)
# - Monitoring endpoints (performance_monitoring, ai_cost_monitoring)
# - Background task endpoints (ai_cost_pusher)
# - Admin endpoints (require special permissions)
# - Webhooks (require background processing)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "ruleIQ API - Vercel Edition",
        "version": "2.0.0",
        "docs": "/api/docs" if not IS_PRODUCTION else "disabled",
        "health": "/api/health"
    }

# Export the app for Vercel
handler = app