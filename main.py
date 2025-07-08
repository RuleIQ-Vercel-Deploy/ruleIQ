from contextlib import asynccontextmanager

import uvicorn
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies.auth import get_current_active_user
from api.dependencies.database import get_async_db
from api.middleware.error_handler import error_handler_middleware
from api.request_id_middleware import RequestIDMiddleware
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
    users,
)
from api.schemas import APIInfoResponse, HealthCheckResponse
from config.logging_config import get_logger, setup_logging
from config.settings import settings
from database.db_setup import create_db_and_tables
from database import User  # Import all models through the database package

# Setup logging
setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting ComplianceGPT API...")
    await create_db_and_tables()
    logger.info("Database tables created or verified.")

    # Initialize default frameworks
    from database.db_setup import get_async_db
    from services.framework_service import initialize_default_frameworks
    try:
        async for db in get_async_db():
            await initialize_default_frameworks(db)
            break  # Only need one iteration
        logger.info("Default frameworks initialized.")
    except Exception as e:
        logger.warning(f"Failed to initialize default frameworks: {e}")

    # Initialize cache manager
    from config.cache import get_cache_manager
    await get_cache_manager()
    logger.info("Cache manager initialized.")

    logger.info(f"Environment: {settings.env.value}")
    logger.info(f"Debug mode: {settings.debug}")
    yield
    # Shutdown
    logger.info("Shutting down ComplianceGPT API...")

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
app.add_middleware(RequestIDMiddleware)
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
app.include_router(ai_assessments.router, prefix="/api", tags=["AI Assessment Assistant"])
app.include_router(ai_optimization.router, prefix="/api/ai", tags=["AI Optimization"])
app.include_router(frameworks.router, prefix="/api/frameworks", tags=["Compliance Frameworks"])
app.include_router(policies.router, prefix="/api/policies", tags=["Policies"])
app.include_router(implementation.router, prefix="/api/implementation", tags=["Implementation Plans"])
app.include_router(evidence.router, prefix="/api/evidence", tags=["Evidence"])
app.include_router(evidence_collection.router, prefix="/api", tags=["Evidence Collection"])
app.include_router(compliance.router, prefix="/api/compliance", tags=["Compliance Status"])
app.include_router(readiness.router, prefix="/api/readiness", tags=["Readiness Assessment"])
app.include_router(reporting.router, prefix="/api/reports", tags=["Reports"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["Integrations"])
app.include_router(foundation_evidence.router, prefix="/api", tags=["Foundation Evidence Collection"])
app.include_router(monitoring.router, prefix="/api/monitoring", tags=["Monitoring"])
app.include_router(security.router, prefix="/api/security", tags=["Security"])
app.include_router(chat.router, prefix="/api", tags=["AI Assistant"])

@app.get("/api/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get user dashboard data - alias for /api/users/dashboard"""
    from api.routers.users import get_user_dashboard
    return await get_user_dashboard(current_user, db)

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
    """Check API health status with database monitoring"""
    try:
        from database.db_setup import get_engine_info
        from services.monitoring.database_monitor import database_monitor

        # Get basic database engine info
        engine_info = get_engine_info()

        # Get database monitoring status
        db_status = database_monitor.get_current_status()

        # Determine overall health
        critical_alerts = db_status['alert_counts']['critical']
        warning_alerts = db_status['alert_counts']['warning']

        if critical_alerts > 0:
            status = "degraded"
            message = f"Critical database issues detected ({critical_alerts} alerts)"
        elif warning_alerts > 0:
            status = "warning"
            message = f"Database warnings detected ({warning_alerts} alerts)"
        elif not engine_info.get('async_engine_initialized'):
            status = "degraded"
            message = "Database engine not properly initialized"
        else:
            status = "healthy"
            message = "All systems operational"

        # Include basic monitoring data in health response
        health_data = {
            "status": status,
            "message": message,
            "database": {
                "engine_initialized": engine_info.get('async_engine_initialized', False),
                "pool_utilization": db_status['pool_metrics']['utilization_percent'] if db_status['pool_metrics'] else 0,
                "active_sessions": db_status['session_metrics']['active_sessions'],
                "recent_alerts": db_status['alert_counts']
            },
            "timestamp": db_status['timestamp']
        }

        return HealthCheckResponse(**health_data)

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthCheckResponse(
            status="error",
            message=f"Health check failed: {e!s}"
        )

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development
    )
