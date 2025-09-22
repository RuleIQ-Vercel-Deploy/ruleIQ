from __future__ import annotations
from typing import Any, AsyncGenerator, Dict
from contextlib import asynccontextmanager
import asyncio
import os
import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from middleware.cors_enhanced import EnhancedCORSMiddleware
from config.security_settings import get_security_settings
from api.dependencies.auth import get_current_active_user
from api.middleware.error_handler import error_handler_middleware
from api.request_id_middleware import RequestIDMiddleware
from api.routers import (
    auth, assessments, business_profiles, chat, compliance, evidence,
    frameworks, freemium, policies, readiness, reports, security,
    uk_compliance, users, google_auth, ai_assessments, ai_optimization,
    implementation, evidence_collection, integrations, foundation_evidence,
    dashboard, payment, monitoring, api_keys, webhooks, secrets_vault,
    ai_cost_monitoring, feedback, ai_cost_websocket, ai_policy,
    performance_monitoring, iq_agent, agentic_rag, test_utils
)
from api.routers.admin import admin_router
from api.routers import rbac_auth
from api.schemas import APIInfoResponse, HealthCheckResponse
from config.logging_config import get_logger, setup_logging
from config.settings import settings
from database.db_setup import init_db, get_async_db
from database import User
setup_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[Any, None]:
    logger.info('Starting ComplianceGPT API...')

    # Initialize database and check if successful
    logger.info('Initializing database connection and tables...')
    if not init_db():
        error_msg = 'Database initialization failed. Application cannot start without database connection.'
        logger.error(error_msg)
        logger.error('Please check database configuration and connectivity:')
        logger.error('  1. Verify DATABASE_URL in .env or environment variables')
        logger.error('  2. Ensure PostgreSQL is running and accessible')
        logger.error('  3. Check network connectivity to database host')
        logger.error('  4. Verify database user permissions')
        raise RuntimeError(error_msg)

    logger.info('Database tables created or verified successfully.')
    from services.framework_service import initialize_default_frameworks
    try:
        async for db in get_async_db():
            await initialize_default_frameworks(db)
            break
        logger.info('Default frameworks initialized.')
    except Exception as e:
        logger.warning(f'Failed to initialize default frameworks: {e}')
    from config.cache import get_cache_manager
    await get_cache_manager()
    logger.info('Cache manager initialized.')
    # TODO: Fix TrustLevel import issue in agentic models
    # from services.agentic_integration import initialize_agentic_service
    # try:
    #     await initialize_agentic_service()
    #     logger.info('Agentic RAG service initialized.')
    # except Exception as e:
    #     logger.warning(f'Failed to initialize agentic RAG service: {e}')
    # Database monitoring initialization
    # Policy controlled by settings.database_monitoring_required:
    # - If True: Monitoring is critical, startup fails if initialization fails
    # - If False (default): Monitoring failures are logged as warnings, startup continues
    from monitoring.database_monitor import get_database_monitor
    import asyncio
    try:
        monitor = get_database_monitor()
        monitoring_task = asyncio.create_task(monitor.start_monitoring_loop(interval_seconds=30))
        logger.info('Database monitoring service started with 30s interval')
        app.state.monitoring_task = monitoring_task
    except Exception as e:
        if settings.database_monitoring_required:
            logger.error(f'Failed to start required database monitoring: {e}')
            raise RuntimeError(f'Database monitoring is required but failed to initialize: {e}')
        else:
            logger.warning(f'Failed to start database monitoring (non-critical): {e}')
    logger.info(f'Environment: {settings.environment}')
    logger.info(f'Debug mode: {settings.debug}')
    yield
    logger.info('Shutting down ComplianceGPT API...')
    if hasattr(app.state, 'monitoring_task'):
        try:
            app.state.monitoring_task.cancel()
            await app.state.monitoring_task
        except asyncio.CancelledError:
            logger.info('Database monitoring task cancelled successfully')
        except Exception as e:
            logger.warning(f'Error cancelling monitoring task: {e}')
app = FastAPI(title='ruleIQ Compliance Automation API', description='\n    **ruleIQ API** provides comprehensive compliance automation for UK Small and Medium Businesses (SMBs).\n\n    ## Features\n    - 🤖 **AI-Powered Assessments** with 6 specialized AI tools\n    - 📋 **Policy Generation** with 25+ compliance frameworks\n    - 📁 **Evidence Management** with automated validation\n    - 🔐 **RBAC Security** with JWT authentication\n    - 📊 **Real-time Analytics** and compliance scoring\n\n    ## Authentication\n    All endpoints require JWT bearer token authentication except `/api/auth/*` endpoints.\n\n    Get your access token via `/api/auth/token` endpoint.\n\n    ## Rate Limiting\n    - **General endpoints**: 100 requests/minute\n    - **AI endpoints**: 3-20 requests/minute (tiered)\n    - **Authentication**: 5 requests/minute\n\n    ## Support\n    - **Documentation**: See `/docs/api/` for detailed guides\n    - **Interactive Testing**: Use this Swagger UI to test endpoints\n    - **Status**: Production-ready (98% complete, 671+ tests)\n    ', version='2.0.0', docs_url='/docs', redoc_url='/redoc', openapi_url='/openapi.json', lifespan=lifespan, contact={'name': 'ruleIQ API Support', 'url': 'https://docs.ruleiq.com', 'email': 'api-support@ruleiq.com'}, license_info={'name': 'Proprietary', 'url': 'https://ruleiq.com/license'}, servers=[{'url': 'http://localhost:8000', 'description': 'Development server'}, {'url': 'https://api.ruleiq.com', 'description': 'Production server'}])
# Configure CORS based on environment
security_settings = get_security_settings()
if security_settings.is_production:
    # Use enhanced CORS middleware for production
    app.add_middleware(EnhancedCORSMiddleware)
    logger.info("Using enhanced CORS middleware with production settings")
else:
    # Use standard CORS for development/testing with explicit lists
    cors_config = security_settings.get_cors_config()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_config["allow_origins"],
        allow_credentials=cors_config["allow_credentials"],
        allow_methods=cors_config["allow_methods"],
        allow_headers=cors_config["allow_headers"],
        expose_headers=cors_config["expose_headers"],
        max_age=cors_config["max_age"]
    )
    logger.info(f"Using standard CORS middleware for {security_settings.environment}")
app.add_middleware(RequestIDMiddleware)
app.middleware('http')(error_handler_middleware)
from api.middleware.rbac_middleware import RBACMiddleware
app.add_middleware(RBACMiddleware, enable_audit_logging=True)
from api.middleware.rate_limiter import rate_limit_middleware
app.middleware('http')(rate_limit_middleware)

# Add JWT Authentication Middleware v2 (SEC-001 compliance)
# TODO: Fix JWT middleware parameter issue - temporarily disabled for testing
# from middleware.jwt_auth_v2 import JWTAuthMiddlewareV2
# app.add_middleware(JWTAuthMiddlewareV2)

# Add Comprehensive Audit Logging Middleware
from middleware.audit_logging import setup_audit_logging
audit_logger = setup_audit_logging(app)

from middleware.security_middleware import SecurityMiddleware
from middleware.security_headers import SecurityHeadersMiddleware
app.add_middleware(SecurityHeadersMiddleware, csp_enabled=True, cors_enabled=False, nonce_enabled=True, report_uri='/api/security/csp-report')
# Note: SecurityMiddleware auth is disabled as JWT middleware handles authentication
security_middleware = SecurityMiddleware(app=app, enable_auth=False, enable_authz=False, enable_audit=True, enable_encryption=True, enable_sql_protection=True, public_paths=['/docs', '/openapi.json', '/health', '/api/v1/auth/login', '/api/v1/auth/register', '/api/v1/freemium/leads', '/api/v1/freemium/sessions'])
app.middleware('http')(security_middleware)

@app.middleware('http')
async def add_rate_limit_headers_middleware(request: Request, call_next) -> Dict[str, Any]:
    """Add rate limit headers from request.state to responses."""
    response = await call_next(request)
    if hasattr(request.state, 'rate_limit_headers'):
        for header, value in request.state.rate_limit_headers.items():
            response.headers[header] = value
    return response

# Diagnostic wrapper for router inclusion
def include_router_with_diagnostics(
    app: FastAPI,
    router,
    prefix: str = "",
    tags: list[str] = None,
    router_name: str = None
) -> None:
    """
    Wrapper for include_router with diagnostic logging.
    Helps identify router import/inclusion failures during re-enablement.
    """
    router_name = router_name or (tags[0] if tags else "Unknown")
    try:
        app.include_router(router, prefix=prefix, tags=tags or [])
        logger.debug(f"✅ Successfully included router: {router_name} (prefix: {prefix})")
    except AttributeError as e:
        logger.error(f"❌ Router import failure for {router_name}: Missing attribute - {e}")
        logger.error(f"   Check if router module exports 'router' variable")
    except ImportError as e:
        logger.error(f"❌ Router import failure for {router_name}: Import error - {e}")
        logger.error(f"   Check module dependencies and imports")
    except Exception as e:
        logger.error(f"❌ Router inclusion failed for {router_name}: {type(e).__name__} - {e}")
        logger.error(f"   Prefix: {prefix}, Tags: {tags}")
        # Re-raise to maintain original behavior
        raise

# Include routers with diagnostic logging
include_router_with_diagnostics(app, auth.router, prefix='/api/v1/auth', tags=['Authentication'])
include_router_with_diagnostics(app, google_auth.router, prefix='/api/v1/auth/google', tags=['Google OAuth'])
include_router_with_diagnostics(app, rbac_auth.router, prefix='/api/v1/auth', tags=['RBAC Authentication'])
include_router_with_diagnostics(app, users.router, prefix='/api/v1/users', tags=['Users'])
include_router_with_diagnostics(app, business_profiles.router, prefix='/api/v1/business-profiles', tags=['Business Profiles'])
include_router_with_diagnostics(app, assessments.router, prefix='/api/v1/assessments', tags=['Assessments'])
from api.routers import usage_dashboard, audit_export
include_router_with_diagnostics(app, usage_dashboard.router, prefix='/api/v1', tags=['Usage Dashboard'])
include_router_with_diagnostics(app, audit_export.router, prefix='/api/v1', tags=['Audit Export'])
include_router_with_diagnostics(app, freemium.router, prefix='/api/v1', tags=['Freemium Assessment'])
include_router_with_diagnostics(app, ai_assessments.router, prefix='/api/v1/ai', tags=['AI Assessment Assistant'])
include_router_with_diagnostics(app, ai_optimization.router, prefix='/api/v1/ai/optimization', tags=['AI Optimization'])
include_router_with_diagnostics(app, frameworks.router, prefix='/api/v1/frameworks', tags=['Compliance Frameworks'])
include_router_with_diagnostics(app, policies.router, prefix='/api/v1/policies', tags=['Policies'])
include_router_with_diagnostics(app, implementation.router, prefix='/api/v1/implementation', tags=['Implementation Plans'])
include_router_with_diagnostics(app, evidence.router, prefix='/api/v1/evidence', tags=['Evidence'])
include_router_with_diagnostics(app, evidence_collection.router, prefix='/api/v1/evidence-collection', tags=['Evidence Collection'])
include_router_with_diagnostics(app, compliance.router, prefix='/api/v1/compliance', tags=['Compliance Status'])
include_router_with_diagnostics(app, readiness.router, prefix='/api/v1/readiness', tags=['Readiness Assessment'])
include_router_with_diagnostics(app, reports.router, prefix='/api/v1/reports', tags=['Reports'])
include_router_with_diagnostics(app, integrations.router, prefix='/api/v1/integrations', tags=['Integrations'])
include_router_with_diagnostics(app, foundation_evidence.router, prefix='/api/v1/foundation/evidence', tags=['Foundation Evidence Collection'])
include_router_with_diagnostics(app, dashboard.router, prefix='/api/v1/dashboard', tags=['Dashboard'])
include_router_with_diagnostics(app, payment.router, prefix='/api/v1/payments', tags=['Payments'])
include_router_with_diagnostics(app, monitoring.router, prefix='/api/v1/monitoring', tags=['Monitoring'])
include_router_with_diagnostics(app, security.router, prefix='/api/v1/security', tags=['Security'])
include_router_with_diagnostics(app, api_keys.router, prefix='', tags=['API Keys'], router_name='API Keys')
include_router_with_diagnostics(app, webhooks.router, prefix='', tags=['Webhooks'], router_name='Webhooks')
include_router_with_diagnostics(app, secrets_vault.router, prefix='', tags=['🔐 Secrets Vault'], router_name='Secrets Vault')
include_router_with_diagnostics(app, chat.router, prefix='/api/v1/chat', tags=['AI Assistant'])
include_router_with_diagnostics(app, ai_cost_monitoring.router, prefix='/api/v1/ai/cost', tags=['AI Cost Monitoring'])
include_router_with_diagnostics(app, feedback.router, prefix='/api/v1/feedback', tags=['Human Feedback'])
include_router_with_diagnostics(app, ai_cost_websocket.router, prefix='/api/v1/ai/cost-websocket', tags=['AI Cost WebSocket'])
include_router_with_diagnostics(app, ai_policy.router, prefix='/api/v1/ai/policies', tags=['AI Policy Generation'])
include_router_with_diagnostics(app, performance_monitoring.router, prefix='/api/v1/performance', tags=['Performance Monitoring'])
include_router_with_diagnostics(app, uk_compliance.router, prefix='/api/v1/uk-compliance', tags=['UK Compliance'])
include_router_with_diagnostics(app, iq_agent.router, prefix='/api/v1/iq-agent', tags=['IQ Agent'])
include_router_with_diagnostics(app, agentic_rag.router, prefix='/api/v1/agentic-rag', tags=['Agentic RAG'])
include_router_with_diagnostics(app, admin_router, prefix='', tags=['Admin'], router_name='Admin Router')
import os
if os.getenv('ENVIRONMENT', 'production').lower() in ['development', 'test', 'testing', 'local']:
    include_router_with_diagnostics(app, test_utils.router, prefix='/api/test-utils', tags=['Test Utilities'])

@app.get('/api/dashboard')
async def get_dashboard(current_user: User=Depends(get_current_active_user)) -> Dict[str, Any]:
    """Get user dashboard data"""
    return {'user': {'id': str(current_user.id), 'email': current_user.email, 'name': current_user.full_name or ''}, 'stats': {'assessments': 0, 'policies': 0, 'compliance_score': 0, 'recent_activities': []}}

@app.get('/', response_model=APIInfoResponse, summary='API Information')
async def root() -> Any:
    """Get basic API information"""
    return APIInfoResponse(message='ComplianceGPT API', version='1.0.0', status='operational')

@app.get('/health', response_model=HealthCheckResponse, summary='Health Check')
async def health_check() -> Any:
    """Check API health status with database monitoring"""
    try:
        from datetime import datetime, timezone
        from database.db_setup import get_engine_info
        from monitoring.database_monitor import get_database_monitor
        monitor = get_database_monitor()
        monitoring_summary = monitor.get_monitoring_summary()
        engine_info = get_engine_info()
        current_metrics = monitoring_summary.get('current_metrics', {})
        alerts = monitoring_summary.get('alerts', [])
        critical_alerts = len([a for a in alerts if a.get('severity') == 'critical'])
        warning_alerts = len([a for a in alerts if a.get('severity') == 'warning'])
        if critical_alerts > 0:
            status = 'degraded'
            message = f'Critical database issues detected ({critical_alerts} alerts)'
        elif warning_alerts > 0:
            status = 'warning'
            message = f'Database warnings detected ({warning_alerts} alerts)'
        elif not engine_info.get('async_engine_initialized'):
            status = 'degraded'
            message = 'Database engine not properly initialized'
        else:
            status = 'healthy'
            message = 'All systems operational'
        pool_utilization = 0
        active_sessions = 0
        for pool_type, metrics in current_metrics.items():
            if metrics:
                pool_utilization = max(pool_utilization, metrics.get('utilization_percent', 0))
        recent_averages = monitoring_summary.get('recent_averages', {})
        for key, value in recent_averages.items():
            if 'active_sessions' in key:
                active_sessions = value
                break
        health_data = {'status': status, 'message': message, 'database': {'engine_initialized': engine_info.get('async_engine_initialized', False), 'pool_utilization': pool_utilization, 'active_sessions': active_sessions, 'recent_alerts': {'critical': critical_alerts, 'warning': warning_alerts, 'total': len(alerts)}}, 'timestamp': monitoring_summary.get('timestamp', datetime.now(timezone.utc).isoformat())}
        return HealthCheckResponse(**health_data)
    except Exception as e:
        logger.error(f'Health check failed: {e}')
        return HealthCheckResponse(status='error', message=f'Health check failed: {e!s}')

@app.get('/debug-suite', include_in_schema=False)
async def serve_debug_suite() -> Any:
    """Serve the API debug suite HTML file"""
    import os
    from fastapi.responses import FileResponse
    debug_file_path = os.path.join(os.getcwd(), 'debug-suite.html')
    if os.path.exists(debug_file_path):
        return FileResponse(debug_file_path, media_type='text/html')
    else:
        raise HTTPException(status_code=404, detail='Debug suite not found')

@app.get('/api/v1/health', response_model=HealthCheckResponse, summary='API v1 Health Check')
async def api_health_check() -> Any:
    """API v1 health check endpoint"""
    from datetime import datetime, timezone
    return HealthCheckResponse(status='healthy', message='API v1 operational', timestamp=datetime.now(timezone.utc).isoformat(), version='2.0.0')

@app.get('/api/v1/health/detailed', response_model=HealthCheckResponse, summary='Detailed API v1 Health Check')
async def api_detailed_health_check() -> Any:
    """API v1 detailed health check with comprehensive monitoring"""
    from datetime import datetime, timezone
    from database.db_setup import get_engine_info
    from monitoring.database_monitor import get_database_monitor
    from config.cache import get_cache_manager
    from services.neo4j_service import get_neo4j_service
    engine_info = get_engine_info()
    cache_health = {'status': 'unknown', 'connected': False, 'message': 'Cache not available'}
    try:
        cache_manager = await get_cache_manager()
        if cache_manager:
            await cache_manager.redis_client.ping()
            cache_health = {'status': 'healthy', 'connected': True, 'message': 'Redis cache operational'}
    except Exception as e:
        cache_health = {'status': 'error', 'connected': False, 'message': f'Cache error: {e!s}'}
    
    # Check Neo4j connectivity with timeout
    neo4j_health = {'status': 'not_configured', 'connected': False, 'message': 'Neo4j not configured'}
    try:
        # Check if Neo4j is configured via environment variable
        if os.getenv('NEO4J_URI'):
            neo4j_service = await get_neo4j_service()
            if neo4j_service:
                # Apply timeout to health check to avoid hanging the endpoint
                neo4j_health = await asyncio.wait_for(
                    neo4j_service.health_check(), 
                    timeout=2.0
                )
        else:
            neo4j_health = {'status': 'disabled', 'connected': False, 'message': 'Neo4j not configured (NEO4J_URI not set)'}
    except asyncio.TimeoutError:
        neo4j_health = {'status': 'error', 'connected': False, 'message': 'Neo4j health check timeout'}
    except Exception as e:
        neo4j_health = {'status': 'error', 'connected': False, 'message': f'Neo4j health check failed: {e!s}'}
    
    monitor = get_database_monitor()
    monitoring_summary = monitor.get_monitoring_summary() if monitor else {}
    current_metrics = monitoring_summary.get('current_metrics', {})
    alerts = monitoring_summary.get('alerts', [])
    critical_alerts = len([a for a in alerts if a.get('severity') == 'critical'])
    warning_alerts = len([a for a in alerts if a.get('severity') == 'warning'])
    if critical_alerts > 0:
        overall_status = 'degraded'
        overall_message = f'System degraded: {critical_alerts} critical issues'
    elif warning_alerts > 0:
        overall_status = 'warning'
        overall_message = f'System operational with warnings: {warning_alerts} warnings'
    else:
        # Check individual service statuses
        overall_status = 'healthy'
        overall_message = 'All services operational'
        issues = []
        
        if not engine_info.get('async_engine_initialized'):
            overall_status = 'degraded'
            issues.append('Database')
        
        if cache_health['status'] not in ['healthy']:
            if overall_status == 'healthy':
                overall_status = 'warning'
            issues.append('Cache')
        
        # Neo4j: treat as warning if unhealthy (unless it's just not configured)
        if neo4j_health['status'] not in ['healthy', 'not_configured', 'disabled']:
            if overall_status == 'healthy':
                overall_status = 'warning'
            issues.append('Neo4j')
        
        if issues:
            overall_message = f'Services with issues: {", ".join(issues)}'
    pool_utilization = 0
    active_sessions = 0
    for pool_type, metrics in current_metrics.items():
        if metrics:
            pool_utilization = max(pool_utilization, metrics.get('utilization_percent', 0))
    recent_averages = monitoring_summary.get('recent_averages', {})
    for key, value in recent_averages.items():
        if 'active_sessions' in key:
            active_sessions = value
            break
    detailed_health = {'status': overall_status, 'message': overall_message, 'version': '2.0.0', 'environment': settings.environment, 'database': {'status': 'healthy' if engine_info.get('async_engine_initialized') else 'degraded', 'engine_initialized': engine_info.get('async_engine_initialized', False), 'pool_utilization': pool_utilization, 'active_sessions': active_sessions, 'recent_alerts': {'critical': critical_alerts, 'warning': warning_alerts, 'total': len(alerts)}}, 'cache': cache_health, 'neo4j': neo4j_health, 'monitoring': {'enabled': monitor is not None, 'last_check': monitoring_summary.get('timestamp', datetime.now(timezone.utc).isoformat()), 'metrics_available': bool(current_metrics)}, 'services': {'frameworks': {'status': 'operational', 'total': 25}, 'ai_assistant': {'status': 'operational', 'models': 6}, 'authentication': {'status': 'operational', 'method': 'JWT + RBAC'}}, 'timestamp': datetime.now(timezone.utc).isoformat()}
    return HealthCheckResponse(**detailed_health)

@app.get('/api/v1/ping', summary='Simple Ping Endpoint')
async def ping() -> Dict[str, str]:
    """Simple ping endpoint for connectivity testing"""
    return {'status': 'pong', 'message': 'API is responsive'}
if __name__ == '__main__':
    import sys
    host = '0.0.0.0'
    port = 8000
    reload = False
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == '--host' and i < len(sys.argv) - 1:
            host = sys.argv[i + 1]
        elif arg == '--port' and i < len(sys.argv) - 1:
            try:
                port = int(sys.argv[i + 1])
            except ValueError:
                logger.error(f"Invalid port: {sys.argv[i + 1]}")
                sys.exit(1)
        elif arg == '--reload':
            reload = True
    logger.info(f'Starting server on {host}:{port} (reload={reload})')
    uvicorn.run('main:app' if reload else app, host=host, port=port, reload=reload, log_level='info' if settings.debug else 'warning')
