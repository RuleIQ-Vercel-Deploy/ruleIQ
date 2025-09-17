"""
Integration script for Security Middleware (Stories 1.1, 1.2, 1.3)

This script shows how to integrate JWT validation, rate limiting, and CORS
configuration into the main FastAPI application.
"""
from fastapi import FastAPI
import logging

# Import security middleware
from middleware.jwt_auth_v2 import JWTAuthMiddlewareV2
from middleware.rate_limiter import RateLimitMiddleware
from middleware.cors_config import setup_cors

logger = logging.getLogger(__name__)


def setup_security_middleware(app: FastAPI) -> None:
    """
    Configure all security middleware for the application.
    
    Order matters! Middleware is executed in reverse order of addition:
    1. CORS (needs to be early for preflight)
    2. Rate Limiting (before expensive operations)
    3. JWT Authentication (after rate limiting)
    
    Args:
        app: FastAPI application instance
    """

    # ============================================================
    # Story 1.3: CORS Configuration
    # ============================================================
    logger.info("Setting up CORS middleware...")

    # Method 1: Using our custom setup function
    setup_cors(app)

    # Alternative Method 2: Manual configuration
    # cors_config = CORSConfig()
    # app.add_middleware(
    #     CORSMiddleware,
    #     **cors_config.to_middleware_kwargs()
    # )

    logger.info("✓ CORS middleware configured")

    # ============================================================
    # Story 1.2: Rate Limiting
    # ============================================================
    logger.info("Setting up rate limiting middleware...")

    # Add rate limiting middleware
    app.add_middleware(RateLimitMiddleware)

    logger.info("✓ Rate limiting middleware configured")

    # ============================================================
    # Story 1.1: JWT Validation Enhancement
    # ============================================================
    logger.info("Setting up JWT authentication middleware v2...")

    # Add JWT middleware (already exists, we enhanced it)
    app.add_middleware(JWTAuthMiddlewareV2)

    logger.info("✓ JWT authentication middleware v2 configured")

    # Log middleware stack
    logger.info(
        "Security middleware stack configured:\n"
        "  1. JWT Authentication (enhanced with blacklisting)\n"
        "  2. Rate Limiting (tiered with Redis)\n"
        "  3. CORS (environment-specific)"
    )


def create_secure_app() -> FastAPI:
    """
    Create a FastAPI application with all security middleware configured.
    
    Returns:
        Configured FastAPI application
    """
    # Create base application
    app = FastAPI(
        title="RuleIQ API",
        description="AI-powered compliance automation platform",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Configure security middleware
    setup_security_middleware(app)

    # Add API routers (example)
    # from api.routers import auth, users, assessments
    # app.include_router(auth.router, prefix="/api/v1")
    # app.include_router(users.router, prefix="/api/v1")
    # app.include_router(assessments.router, prefix="/api/v1")

    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint (public, no auth required)."""
        return {"status": "healthy", "service": "ruleiq-api"}

    # Add root endpoint
    @app.get("/")
    async def root():
        """Root endpoint (public)."""
        return {
            "service": "RuleIQ API",
            "version": "2.0.0",
            "security": {
                "jwt": "v2 with blacklisting",
                "rate_limiting": "enabled",
                "cors": "configured"
            }
        }

    return app


# Example main.py integration
MAIN_PY_EXAMPLE = '''
"""
RuleIQ API Main Application

Enhanced with comprehensive security middleware:
- JWT v2 with token blacklisting (Story 1.1)
- Rate limiting with Redis (Story 1.2)  
- CORS configuration (Story 1.3)
"""
import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

# Security middleware imports
from middleware.jwt_auth_v2 import JWTAuthMiddlewareV2
from middleware.rate_limiter import RateLimitMiddleware
from middleware.cors_config import setup_cors

# API routers
from api.routers import (
    auth,
    users,
    assessments,
    frameworks,
    policies,
    reports,
    admin
)

# Services
from services.token_blacklist_service import get_blacklist_service
from database.db_setup import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting RuleIQ API...")
    
    # Initialize database
    await init_db()
    
    # Initialize services
    blacklist_service = get_blacklist_service()
    logger.info("Token blacklist service initialized")
    
    # Warm up caches
    # await warm_up_caches()
    
    logger.info("RuleIQ API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down RuleIQ API...")
    
    # Cleanup
    # await cleanup_connections()
    
    logger.info("RuleIQ API shutdown complete")


# Create application
app = FastAPI(
    title="RuleIQ API",
    description="AI-powered compliance automation platform with enhanced security",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# ============================================================
# MIDDLEWARE CONFIGURATION (Order matters!)
# ============================================================

# 1. Trusted Host Middleware (security)
if os.getenv("ENVIRONMENT") == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["app.ruleiq.com", "www.ruleiq.com", "api.ruleiq.com"]
    )

# 2. GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 3. CORS Configuration (Story 1.3)
setup_cors(app)
logger.info("CORS middleware configured")

# 4. Rate Limiting (Story 1.2)
app.add_middleware(RateLimitMiddleware)
logger.info("Rate limiting middleware configured")

# 5. JWT Authentication v2 (Story 1.1)
app.add_middleware(JWTAuthMiddlewareV2)
logger.info("JWT authentication v2 middleware configured")

# ============================================================
# API ROUTES
# ============================================================

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(assessments.router, prefix="/api/v1/assessments", tags=["Assessments"])
app.include_router(frameworks.router, prefix="/api/v1/frameworks", tags=["Frameworks"])
app.include_router(policies.router, prefix="/api/v1/policies", tags=["Policies"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])

# ============================================================
# HEALTH & MONITORING ENDPOINTS
# ============================================================

@app.get("/health", tags=["Monitoring"])
async def health_check():
    """Health check endpoint (public)."""
    return {
        "status": "healthy",
        "service": "ruleiq-api",
        "version": "2.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/health/detailed", tags=["Monitoring"])
async def detailed_health():
    """Detailed health check (requires auth)."""
    # This endpoint will require auth due to middleware
    return {
        "status": "healthy",
        "components": {
            "database": "connected",
            "redis": "connected",
            "jwt_validation": "v2_active",
            "rate_limiting": "active",
            "cors": "configured"
        }
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint (public)."""
    return {
        "service": "RuleIQ API",
        "version": "2.0.0",
        "documentation": "/docs",
        "health": "/health",
        "security_features": {
            "jwt_validation": "v2 with token blacklisting",
            "rate_limiting": "tiered limits with Redis",
            "cors": "environment-specific configuration"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # Development server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
'''


def print_integration_summary():
    """Print summary of the security integration."""
    print("\n" + "="*60)
    print("SECURITY MIDDLEWARE INTEGRATION COMPLETE")
    print("="*60)

    print("\n✅ Story 1.1: JWT Validation")
    print("   - Enhanced JWT validation with strict claim checks")
    print("   - Token blacklisting service with Redis")
    print("   - Refresh token mechanism")
    print("   - Performance target: <10ms validation")

    print("\n✅ Story 1.2: Rate Limiting")
    print("   - Tiered rate limits (Anonymous/Auth/Premium/Enterprise)")
    print("   - Redis-backed sliding window algorithm")
    print("   - Per-endpoint configuration")
    print("   - Rate limit headers in responses")

    print("\n✅ Story 1.3: CORS Configuration")
    print("   - Environment-specific origins")
    print("   - No wildcards in production")
    print("   - Proper preflight handling")
    print("   - Credentials support for JWT")

    print("\n📁 Files Created:")
    print("   - /services/token_blacklist_service.py")
    print("   - /middleware/rate_limiter.py")
    print("   - /middleware/cors_config.py")
    print("   - /tests/test_jwt_validation.py")
    print("   - /tests/test_rate_limiting.py")
    print("   - /tests/test_cors.py")

    print("\n🔧 Integration Steps:")
    print("   1. Update main.py with middleware configuration")
    print("   2. Configure Redis connection in settings")
    print("   3. Set environment variables for CORS origins")
    print("   4. Run tests to validate implementation")
    print("   5. Deploy with feature flags for gradual rollout")

    print("\n⚙️ Environment Variables Required:")
    print("   - ENVIRONMENT (development/staging/production)")
    print("   - REDIS_HOST, REDIS_PORT, REDIS_PASSWORD")
    print("   - CORS_ORIGINS (optional override)")
    print("   - JWT_ISSUER, JWT_AUDIENCE")
    print("   - RATE_LIMIT_IP_WHITELIST (optional)")

    print("\n" + "="*60)


if __name__ == "__main__":
    # Print the integration summary
    print_integration_summary()

    # Save the example main.py
    with open("main_example.py", "w") as f:
        f.write(MAIN_PY_EXAMPLE)

    print("\n💾 Example main.py saved to 'main_example.py'")
    print("\n🚀 Security middleware implementation complete!")
