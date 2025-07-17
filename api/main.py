"""
Main FastAPI application for ruleIQ API
Production-ready FastAPI application with comprehensive configuration
"""

import logging
import os
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import uvicorn

from api.routers import (
    ai_assessments,
    ai_optimization,
    assessments,
    auth,
    business_profiles,
    chat,
    compliance,
    evidence,
    evidence_collection,
    foundation_evidence,
    frameworks,
    implementation,
    integrations,
    monitoring,
    policies,
    readiness,
    reporting,
    security,
    users
)
from api.middleware.error_handler import error_handler_middleware
from api.middleware.rate_limiter import rate_limit_middleware
from api.middleware.security_headers import security_headers_middleware
from database import init_db, test_database_connection, cleanup_db_connections, get_db, _AsyncSessionLocal as AsyncSessionLocal
from config.settings import settings
from monitoring.sentry import init_sentry
from config.ai_config import ai_config

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.value),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager for startup/shutdown events
    """
    # Startup
    logger.info("Starting ruleIQ API...")
    
    # Initialize Sentry
    init_sentry()

    # Initialize database using the new init_db function
    if not init_db():
        logger.error("Database initialization failed during startup")
        raise RuntimeError("Database initialization failed")
    
    # Verify database connection
    if not test_database_connection():
        logger.error("Database connection verification failed")
        raise RuntimeError("Database connection verification failed")
    
    logger.info("ruleIQ API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down ruleIQ API...")
    
    # Close database connections
    await cleanup_db_connections()
    logger.info("Database connections closed")
    
    logger.info("ruleIQ API shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="ruleIQ API",
    description="AI-powered compliance and risk management platform",
    version="1.0.0",
    docs_url="/api/v1/docs" if settings.debug else None,
    redoc_url="/api/v1/redoc" if settings.debug else None,
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Rate-Limit-Remaining"]
)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Allow all hosts for now, configure based on your needs
)

# Add compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add custom middleware
app.middleware("http")(error_handler_middleware)
app.middleware("http")(security_headers_middleware)
app.middleware("http")(rate_limit_middleware)

# Include all routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(assessments.router, prefix="/api/v1/assessments", tags=["assessments"])
app.include_router(ai_assessments.router, prefix="/api/v1/ai-assessments", tags=["ai-assessments"])
app.include_router(ai_optimization.router, prefix="/api/v1/ai-optimization", tags=["ai-optimization"])
app.include_router(business_profiles.router, prefix="/api/v1/business-profiles", tags=["business-profiles"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(compliance.router, prefix="/api/v1/compliance", tags=["compliance"])
app.include_router(evidence.router, prefix="/api/v1/evidence", tags=["evidence"])
app.include_router(evidence_collection.router, prefix="/api/v1/evidence-collection", tags=["evidence-collection"])
app.include_router(foundation_evidence.router, prefix="/api/v1/foundation-evidence", tags=["foundation-evidence"])
app.include_router(frameworks.router, prefix="/api/v1/frameworks", tags=["frameworks"])
app.include_router(implementation.router, prefix="/api/v1/implementation", tags=["implementation"])
app.include_router(integrations.router, prefix="/api/v1/integrations", tags=["integrations"])
app.include_router(monitoring.router, prefix="/api/v1/monitoring", tags=["monitoring"])
app.include_router(policies.router, prefix="/api/v1/policies", tags=["policies"])
app.include_router(readiness.router, prefix="/api/v1/readiness", tags=["readiness"])
app.include_router(reporting.router, prefix="/api/v1/reporting", tags=["reporting"])
app.include_router(security.router, prefix="/api/v1/security", tags=["security"])


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with consistent error format"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "message": exc.detail,
                "type": "http_exception",
                "status_code": exc.status_code
            }
        }
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database exceptions"""
    logger.error(f"Database error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "Database operation failed",
                "type": "database_error",
                "status_code": 500
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all other exceptions"""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "Internal server error",
                "type": "internal_error",
                "status_code": 500
            }
        }
    )

# Health check endpoints
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }

@app.get("/api/v1/health")
async def api_health_check() -> Dict[str, Any]:
    """API v1 health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "api_version": "v1"
    }

@app.get("/api/v1/health/detailed")
async def api_health_detailed() -> Dict[str, Any]:
    """Detailed API v1 health check endpoint with component status"""
    db_status = "unknown"
    ai_status = "unknown"

    # Check DB status
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            if result:
                db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # Check AI service status
    try:
        ai_config._initialize_google_ai()
        ai_status = "healthy"
    except Exception as e:
        ai_status = f"unhealthy: {str(e)}"
    
    overall_status = "healthy" if db_status == "healthy" and ai_status == "healthy" else "degraded"

    return {
        "status": overall_status,
        "timestamp": time.time(),
        "version": "1.0.0",
        "api_version": "v1",
        "components": {
            "database": db_status,
            "ai_services": ai_status,
            "redis": "not_configured",
        }
    }

@app.get("/health/ready")
async def readiness_check() -> Dict[str, Any]:
    """Readiness check with database connectivity"""
    db = None
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "database": "connected",
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="Service not ready - database connection failed"
        )
    finally:
        if db is not None:
            db.close()

@app.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """Liveness check for container orchestration"""
    return {
        "status": "alive",
        "timestamp": time.time(),
        "uptime": time.time() - (getattr(app.state, 'start_time', time.time()))
    }

# Root endpoint
@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint with API information"""
    return {
        "name": "ruleIQ API",
        "version": "1.0.0",
        "description": "AI-powered compliance and risk management platform",
        "documentation": "/docs" if settings.debug else None,
        "health": "/health"
    }

# Startup event to set start time
@app.on_event("startup")
async def startup_event():
    """Set application start time"""
    app.state.start_time = time.time()

# Configuration validation
def validate_configuration() -> None:
    """Validate critical configuration settings"""
    required_vars = [
        "database_url",
        "secret_key",
    ]
    
    missing_vars = []
    for var in required_vars:
        if not getattr(settings, var, None):
            missing_vars.append(var.upper())
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {missing_vars}")

# Validate configuration on import
validate_configuration()

if __name__ == "__main__":
    uvicorn.run(
        "api.main:app",
        host=str(settings.host),
        port=int(settings.port),
        reload=bool(settings.debug),
        log_level=str(settings.log_level).lower(),
        workers=1 if settings.debug else 4
    )