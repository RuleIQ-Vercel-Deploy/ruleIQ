"""
RuleIQ Compliance Automation API - Refactored Main Module
Reduced cognitive complexity and improved maintainability
"""
from __future__ import annotations

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict, Generator

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from api.dependencies.auth import get_current_active_user
from api.middleware.error_handler import error_handler_middleware
from api.middleware.rate_limiter import rate_limit_middleware
from api.middleware.rbac_middleware import RBACMiddleware
from api.request_id_middleware import RequestIDMiddleware
from api.schemas import APIInfoResponse, HealthCheckResponse
from config.logging_config import get_logger, setup_logging
from config.settings import settings
from database import User
from database.db_setup import get_async_db, get_engine_info, init_db
from middleware.jwt_auth import JWTAuthMiddleware
from middleware.security_headers import SecurityHeadersMiddleware
from middleware.security_middleware import SecurityMiddleware

# Import all routers (grouped for clarity)
from api.routers import (
    admin,
    agentic_rag,
    ai_assessments,
    ai_cost_monitoring,
    ai_cost_websocket,
    ai_optimization,
    ai_policy,
    api_keys,
    assessments,
    audit_export,
    auth,
    auth_monitoring,
    business_profiles,
    chat,
    compliance,
    dashboard,
    evidence,
    evidence_collection,
    feedback,
    foundation_evidence,
    frameworks,
    freemium,
    google_auth,
    implementation,
    integrations,
    iq_agent,
    monitoring,
    payment,
    performance_monitoring,
    policies,
    rbac_auth,
    readiness,
    reports,
    security,
    secrets_vault,
    test_utils,
    uk_compliance,
    usage_dashboard,
    users,
    webhooks,
)

# Initialize logging
setup_logging()
logger = get_logger(__name__)


class ApplicationLifecycle:
    """Manages application startup and shutdown lifecycle"""

    @staticmethod
    async def initialize_database() -> None:
        """Initialize database and tables"""
        logger.info("Starting ComplianceGPT API...")
        init_db()
        logger.info("Database tables created or verified.")

    @staticmethod
    async def initialize_frameworks() -> None:
        """Initialize default compliance frameworks"""
        from services.framework_service import initialize_default_frameworks

        try:
            async for db in get_async_db():
                await initialize_default_frameworks(db)
                break
            logger.info("Default frameworks initialized.")
        except Exception as e:
            logger.warning(f"Failed to initialize default frameworks: {e}")

    @staticmethod
    async def initialize_cache() -> None:
        """Initialize cache manager"""
        from config.cache import get_cache_manager

        await get_cache_manager()
        logger.info("Cache manager initialized.")

    @staticmethod
    async def initialize_agentic_service() -> None:
        """Initialize agentic RAG service"""
        from services.agentic_integration import initialize_agentic_service

        try:
            await initialize_agentic_service()
            logger.info("Agentic RAG service initialized.")
        except Exception as e:
            logger.warning(f"Failed to initialize agentic RAG service: {e}")

    @staticmethod
    async def start_monitoring(app: FastAPI) -> None:
        """Start database monitoring service"""
        from monitoring.database_monitor import get_database_monitor

        try:
            monitor = get_database_monitor()
            monitoring_task = asyncio.create_task(
                monitor.start_monitoring_loop(interval_seconds=30)
            )
            logger.info("Database monitoring service started with 30s interval")
            app.state.monitoring_task = monitoring_task
        except Exception as e:
            logger.warning(f"Failed to start database monitoring: {e}")

    @staticmethod
    async def stop_monitoring(app: FastAPI) -> None:
        """Stop database monitoring service"""
        if hasattr(app.state, "monitoring_task"):
            try:
                app.state.monitoring_task.cancel()
                await app.state.monitoring_task
            except asyncio.CancelledError:
                logger.info("Database monitoring task cancelled successfully")
            except Exception as e:
                logger.warning(f"Error cancelling monitoring task: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, None]:
    """Application lifespan manager"""
    lifecycle = ApplicationLifecycle()

    # Startup
    await lifecycle.initialize_database()
    await lifecycle.initialize_frameworks()
    await lifecycle.initialize_cache()
    await lifecycle.initialize_agentic_service()
    await lifecycle.start_monitoring(app)

    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    yield

    # Shutdown
    logger.info("Shutting down ComplianceGPT API...")
    await lifecycle.stop_monitoring(app)


class ApplicationFactory:
    """Factory for creating and configuring the FastAPI application"""

    @staticmethod
    def create_app() -> FastAPI:
        """Create and configure the FastAPI application"""
        return FastAPI(
            title="ruleIQ Compliance Automation API",
            description=ApplicationFactory._get_api_description(),
            version="2.0.0",
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json",
            lifespan=lifespan,
            contact={
                "name": "ruleIQ API Support",
                "url": "https://docs.ruleiq.com",
                "email": "api-support@ruleiq.com",
            },
            license_info={"name": "Proprietary", "url": "https://ruleiq.com/license"},
            servers=[
                {"url": "http://localhost:8000", "description": "Development server"},
                {"url": "https://api.ruleiq.com", "description": "Production server"},
            ],
        )

    @staticmethod
    def _get_api_description() -> str:
        """Get API description"""
        return """
        **ruleIQ API** provides comprehensive compliance automation for UK Small and Medium Businesses (SMBs).

        ## Features
        - 🤖 **AI-Powered Assessments** with 6 specialized AI tools
        - 📋 **Policy Generation** with 25+ compliance frameworks
        - 📁 **Evidence Management** with automated validation
        - 🔐 **RBAC Security** with JWT authentication
        - 📊 **Real-time Analytics** and compliance scoring

        ## Authentication
        All endpoints require JWT bearer token authentication except `/api/auth/*` endpoints.
        Get your access token via `/api/auth/token` endpoint.

        ## Rate Limiting
        - **General endpoints**: 100 requests/minute
        - **AI endpoints**: 3-20 requests/minute (tiered)
        - **Authentication**: 5 requests/minute

        ## Support
        - **Documentation**: See `/docs/api/` for detailed guides
        - **Interactive Testing**: Use this Swagger UI to test endpoints
        - **Status**: Production-ready (98% complete, 671+ tests)
        """

    @staticmethod
    def configure_middleware(app: FastAPI) -> None:
        """Configure all middleware for the application"""
        # CORS Middleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Request ID Middleware
        app.add_middleware(RequestIDMiddleware)

        # Error Handler Middleware
        app.middleware("http")(error_handler_middleware)

        # RBAC Middleware
        app.add_middleware(RBACMiddleware, enable_audit_logging=True)

        # Rate Limiter Middleware
        app.middleware("http")(rate_limit_middleware)

        # JWT Authentication Middleware
        jwt_middleware = JWTAuthMiddleware(
            enable_strict_mode=settings.is_production,
            enable_rate_limiting=True,
            enable_audit_logging=True,
        )
        app.middleware("http")(jwt_middleware)

        # Security Headers Middleware
        app.add_middleware(
            SecurityHeadersMiddleware,
            csp_enabled=True,
            cors_enabled=False,
            nonce_enabled=True,
            report_uri="/api/security/csp-report",
        )

        # Security Middleware
        security_middleware = SecurityMiddleware(
            app=app,
            enable_auth=False,  # JWT middleware handles auth
            enable_authz=False,
            enable_audit=True,
            enable_encryption=True,
            enable_sql_protection=True,
            public_paths=[
                "/docs",
                "/openapi.json",
                "/health",
                "/api/v1/auth/login",
                "/api/v1/auth/register",
                "/api/v1/freemium/leads",
                "/api/v1/freemium/sessions",
            ],
        )
        app.middleware("http")(security_middleware)

        # Rate Limit Headers Middleware
        app.middleware("http")(ApplicationFactory._add_rate_limit_headers)

    @staticmethod
    async def _add_rate_limit_headers(request: Request, call_next) -> Any:
        """Add rate limit headers from request.state to responses"""
        response = await call_next(request)
        if hasattr(request.state, "rate_limit_headers"):
            for header, value in request.state.rate_limit_headers.items():
                response.headers[header] = value
        return response

    @staticmethod
    def configure_routes(app: FastAPI) -> None:
        """Configure all API routes"""
        # Authentication routes
        app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
        app.include_router(
            google_auth.router, prefix="/api/v1/auth/google", tags=["Google OAuth"]
        )
        app.include_router(
            rbac_auth.router, prefix="/api/v1/auth", tags=["RBAC Authentication"]
        )
        app.include_router(
            auth_monitoring.router, tags=["Authentication Monitoring"]
        )

        # User and Business routes
        app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
        app.include_router(
            business_profiles.router,
            prefix="/api/v1/business-profiles",
            tags=["Business Profiles"],
        )

        # Assessment routes
        app.include_router(
            assessments.router, prefix="/api/v1/assessments", tags=["Assessments"]
        )
        app.include_router(
            ai_assessments.router,
            prefix="/api/v1/ai",
            tags=["AI Assessment Assistant"],
        )
        app.include_router(
            freemium.router, prefix="/api/v1", tags=["Freemium Assessment"]
        )

        # Compliance and Framework routes
        app.include_router(
            frameworks.router,
            prefix="/api/v1/frameworks",
            tags=["Compliance Frameworks"],
        )
        app.include_router(
            compliance.router,
            prefix="/api/v1/compliance",
            tags=["Compliance Status"],
        )
        app.include_router(
            uk_compliance.router,
            prefix="/api/v1/uk-compliance",
            tags=["UK Compliance"],
        )

        # Policy and Implementation routes
        app.include_router(policies.router, prefix="/api/v1/policies", tags=["Policies"])
        app.include_router(
            implementation.router,
            prefix="/api/v1/implementation",
            tags=["Implementation Plans"],
        )
        app.include_router(
            ai_policy.router,
            prefix="/api/v1/ai/policies",
            tags=["AI Policy Generation"],
        )

        # Evidence routes
        app.include_router(evidence.router, prefix="/api/v1/evidence", tags=["Evidence"])
        app.include_router(
            evidence_collection.router,
            prefix="/api/v1/evidence-collection",
            tags=["Evidence Collection"],
        )
        app.include_router(
            foundation_evidence.router,
            prefix="/api/v1/foundation/evidence",
            tags=["Foundation Evidence Collection"],
        )

        # Dashboard and Reporting routes
        app.include_router(
            dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"]
        )
        app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
        app.include_router(
            usage_dashboard.router, prefix="/api/v1", tags=["Usage Dashboard"]
        )
        app.include_router(
            audit_export.router, prefix="/api/v1", tags=["Audit Export"]
        )

        # AI and Optimization routes
        app.include_router(
            ai_optimization.router,
            prefix="/api/v1/ai/optimization",
            tags=["AI Optimization"],
        )
        app.include_router(chat.router, prefix="/api/v1/chat", tags=["AI Assistant"])
        app.include_router(
            iq_agent.router, prefix="/api/v1/iq-agent", tags=["IQ Agent"]
        )
        app.include_router(
            agentic_rag.router, prefix="/api/v1/agentic-rag", tags=["Agentic RAG"]
        )

        # Monitoring routes
        app.include_router(
            monitoring.router, prefix="/api/v1/monitoring", tags=["Monitoring"]
        )
        app.include_router(
            ai_cost_monitoring.router,
            prefix="/api/v1/ai/cost",
            tags=["AI Cost Monitoring"],
        )
        app.include_router(
            ai_cost_websocket.router,
            prefix="/api/v1/ai/cost-websocket",
            tags=["AI Cost WebSocket"],
        )
        app.include_router(
            performance_monitoring.router,
            prefix="/api/v1/performance",
            tags=["Performance Monitoring"],
        )

        # Integration and External routes
        app.include_router(
            integrations.router, prefix="/api/v1/integrations", tags=["Integrations"]
        )
        app.include_router(payment.router, prefix="/api/v1/payments", tags=["Payments"])
        app.include_router(webhooks.router, tags=["Webhooks"])
        app.include_router(api_keys.router, tags=["API Keys"])

        # Security and Admin routes
        app.include_router(security.router, prefix="/api/v1/security", tags=["Security"])
        app.include_router(secrets_vault.router, tags=["🔐 Secrets Vault"])
        app.include_router(admin.admin_router)

        # Other routes
        app.include_router(
            readiness.router, prefix="/api/v1/readiness", tags=["Readiness Assessment"]
        )
        app.include_router(feedback.router, prefix="/api/v1/feedback", tags=["Human Feedback"])

        # Test utilities (development only)
        if ApplicationFactory._is_development_environment():
            app.include_router(
                test_utils.router, prefix="/api/test-utils", tags=["Test Utilities"]
            )

    @staticmethod
    def _is_development_environment() -> bool:
        """Check if running in development environment"""
        env = os.getenv("ENVIRONMENT", "production").lower()
        return env in ["development", "test", "testing", "local"]


class HealthCheckService:
    """Service for handling health check operations"""

    @staticmethod
    async def get_basic_health() -> HealthCheckResponse:
        """Get basic health status"""
        return HealthCheckResponse(
            status="healthy",
            message="API v1 operational",
            timestamp=datetime.now(timezone.utc).isoformat(),
            version="2.0.0",
        )

    @staticmethod
    async def get_detailed_health() -> HealthCheckResponse:
        """Get detailed health status with monitoring information"""
        try:
            from config.cache import get_cache_manager
            from monitoring.database_monitor import get_database_monitor

            # Get database status
            engine_info = get_engine_info()
            db_status = HealthCheckService._get_database_status(engine_info)

            # Get cache status
            cache_status = await HealthCheckService._get_cache_status()

            # Get monitoring status
            monitor = get_database_monitor()
            monitoring_data = HealthCheckService._get_monitoring_data(monitor)

            # Determine overall status
            overall_status = HealthCheckService._determine_overall_status(
                db_status, cache_status, monitoring_data
            )

            return HealthCheckResponse(
                status=overall_status["status"],
                message=overall_status["message"],
                version="2.0.0",
                environment=settings.environment,
                database=db_status,
                cache=cache_status,
                monitoring=monitoring_data["monitoring"],
                services=HealthCheckService._get_services_status(),
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return HealthCheckResponse(
                status="error",
                message=f"Health check failed: {str(e)}",
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

    @staticmethod
    def _get_database_status(engine_info: Dict[str, Any]) -> Dict[str, Any]:
        """Get database status information"""
        return {
            "status": "healthy" if engine_info.get("async_engine_initialized") else "degraded",
            "engine_initialized": engine_info.get("async_engine_initialized", False),
        }

    @staticmethod
    async def _get_cache_status() -> Dict[str, Any]:
        """Get cache status information"""
        from config.cache import get_cache_manager

        try:
            cache_manager = await get_cache_manager()
            if cache_manager:
                await cache_manager.redis_client.ping()
                return {
                    "status": "healthy",
                    "connected": True,
                    "message": "Redis cache operational",
                }
        except Exception as e:
            return {
                "status": "error",
                "connected": False,
                "message": f"Cache error: {str(e)}",
            }
        return {
            "status": "unknown",
            "connected": False,
            "message": "Cache not available",
        }

    @staticmethod
    def _get_monitoring_data(monitor: Any) -> Dict[str, Any]:
        """Get monitoring data and alerts"""
        if not monitor:
            return {
                "monitoring": {
                    "enabled": False,
                    "metrics_available": False,
                },
                "alerts": {"critical": 0, "warning": 0, "total": 0},
            }

        summary = monitor.get_monitoring_summary()
        alerts = summary.get("alerts", [])
        
        critical_count = sum(1 for a in alerts if a.get("severity") == "critical")
        warning_count = sum(1 for a in alerts if a.get("severity") == "warning")

        return {
            "monitoring": {
                "enabled": True,
                "last_check": summary.get(
                    "timestamp", datetime.now(timezone.utc).isoformat()
                ),
                "metrics_available": bool(summary.get("current_metrics")),
            },
            "alerts": {
                "critical": critical_count,
                "warning": warning_count,
                "total": len(alerts),
            },
        }

    @staticmethod
    def _determine_overall_status(
        db_status: Dict[str, Any],
        cache_status: Dict[str, Any],
        monitoring_data: Dict[str, Any],
    ) -> Dict[str, str]:
        """Determine overall system status"""
        alerts = monitoring_data.get("alerts", {})
        
        if alerts.get("critical", 0) > 0:
            return {
                "status": "degraded",
                "message": f"System degraded: {alerts['critical']} critical issues",
            }
        elif alerts.get("warning", 0) > 0:
            return {
                "status": "warning",
                "message": f"System operational with warnings: {alerts['warning']} warnings",
            }
        elif db_status["status"] != "healthy" or cache_status["status"] != "healthy":
            return {
                "status": "degraded",
                "message": "Some services not fully operational",
            }
        else:
            return {"status": "healthy", "message": "All services operational"}

    @staticmethod
    def _get_services_status() -> Dict[str, Any]:
        """Get status of various services"""
        return {
            "frameworks": {"status": "operational", "total": 25},
            "ai_assistant": {"status": "operational", "models": 6},
            "authentication": {"status": "operational", "method": "JWT + RBAC"},
        }


# Create the FastAPI application
app = ApplicationFactory.create_app()
ApplicationFactory.configure_middleware(app)
ApplicationFactory.configure_routes(app)

# Health check service instance
health_service = HealthCheckService()


# Root endpoint
@app.get("/", response_model=APIInfoResponse, summary="API Information")
async def root() -> APIInfoResponse:
    """Get basic API information"""
    return APIInfoResponse(
        message="ComplianceGPT API", version="1.0.0", status="operational"
    )


# Health check endpoints
@app.get("/health", response_model=HealthCheckResponse, summary="Health Check")
async def health_check() -> HealthCheckResponse:
    """Check API health status with database monitoring"""
    return await health_service.get_detailed_health()


@app.get("/api/v1/health", response_model=HealthCheckResponse, summary="API v1 Health Check")
async def api_health_check() -> HealthCheckResponse:
    """API v1 health check endpoint"""
    return await health_service.get_basic_health()


@app.get(
    "/api/v1/health/detailed",
    response_model=HealthCheckResponse,
    summary="Detailed API v1 Health Check",
)
async def api_detailed_health_check() -> HealthCheckResponse:
    """API v1 detailed health check with comprehensive monitoring"""
    return await health_service.get_detailed_health()


@app.get("/api/v1/ping", summary="Simple Ping Endpoint")
async def ping() -> Dict[str, str]:
    """Simple ping endpoint for connectivity testing"""
    return {"status": "pong", "message": "API is responsive"}


@app.get("/api/dashboard")
async def get_dashboard(
    current_user: User = Depends(get_current_active_user),
) -> Dict[str, Any]:
    """Get user dashboard data"""
    return {
        "user": {
            "id": current_user["id"],
            "email": current_user["primaryEmail"],
            "name": current_user.get("displayName", ""),
        },
        "stats": {
            "assessments": 0,
            "policies": 0,
            "compliance_score": 0,
            "recent_activities": [],
        },
    }


@app.get("/debug-suite", include_in_schema=False)
async def serve_debug_suite() -> FileResponse:
    """Serve the API debug suite HTML file"""
    debug_file_path = os.path.join(os.getcwd(), "debug-suite.html")
    if os.path.exists(debug_file_path):
        return FileResponse(debug_file_path, media_type="text/html")
    else:
        raise HTTPException(status_code=404, detail="Debug suite not found")


def parse_command_line_args() -> tuple[str, int, bool]:
    """Parse command line arguments"""
    host = "0.0.0.0"
    port = 8000
    reload = False

    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--host" and i < len(sys.argv) - 1:
            host = sys.argv[i + 1]
        elif arg == "--port" and i < len(sys.argv) - 1:
            try:
                port = int(sys.argv[i + 1])
            except ValueError:
                logger.error(f"Invalid port: {sys.argv[i + 1]}")
                sys.exit(1)
        elif arg == "--reload":
            reload = True

    return host, port, reload


if __name__ == "__main__":
    host, port, reload = parse_command_line_args()
    logger.info(f"Starting server on {host}:{port} (reload={reload})")
    
    uvicorn.run(
        "main:app" if reload else app,
        host=host,
        port=port,
        reload=reload,
        log_level="info" if settings.debug else "warning",
    )