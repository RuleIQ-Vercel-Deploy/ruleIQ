from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.middleware.error_handler import error_handler_middleware
from api.routers import (
    assessments,
    auth,
    business_profiles,
    chat,
    evidence,
    frameworks,
    implementation,
    integrations,
    policies,
    readiness,
    reporting,
    users,
)
from api.schemas import APIInfoResponse, HealthCheckResponse
from config.logging_config import get_logger, setup_logging
from config.settings import settings
from database.db_setup import Base, engine

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.logger.info("Starting ComplianceGPT API...")
    logger.logger.info(f"Environment: {settings.env.value}")
    logger.logger.info(f"Debug mode: {settings.debug}")
    yield
    # Shutdown
    logger.logger.info("Shutting down ComplianceGPT API...")

app = FastAPI(
    title="ComplianceGPT API",
    description="AI-powered compliance automation platform for UK SMBs",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.middleware("http")(error_handler_middleware)

# Rate limiting
from api.middleware.rate_limiter import rate_limit_middleware

app.middleware("http")(rate_limit_middleware)

# Security headers
from api.middleware.security_headers import security_headers_middleware

app.middleware("http")(security_headers_middleware)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(business_profiles.router, prefix="/api/business-profiles", tags=["Business Profiles"])
app.include_router(assessments.router, prefix="/api/assessments", tags=["Assessments"])
app.include_router(frameworks.router, prefix="/api/frameworks", tags=["Compliance Frameworks"])
app.include_router(policies.router, prefix="/api/policies", tags=["Policies"])
app.include_router(implementation.router, prefix="/api/implementation", tags=["Implementation Plans"])
app.include_router(evidence.router, prefix="/api/evidence", tags=["Evidence"])
app.include_router(readiness.router, prefix="/api/readiness", tags=["Readiness Assessment"])
app.include_router(reporting.router, prefix="/api/reports", tags=["Reports"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["Integrations"])
app.include_router(chat.router, prefix="/api", tags=["AI Assistant"])

@app.get("/", response_model=APIInfoResponse, summary="API Information")
async def root():
    """Get basic API information"""
    return APIInfoResponse(
        message="ComplianceGPT API",
        version="1.0.0",
        status="operational"
    )

@app.get("/health", response_model=HealthCheckResponse, summary="Health Check")
async def health_check():
    """Check API health status"""
    return HealthCheckResponse(status="healthy")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development
    )
