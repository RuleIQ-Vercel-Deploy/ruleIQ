"""
Main FastAPI application for ruleIQ API
Production-ready FastAPI application with comprehensive configuration
"""
from __future__ import annotations

import logging
import os
import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

# Constants
HTTP_SERVICE_UNAVAILABLE = 503
from api.routers import ai_assessments, ai_cost_monitoring, ai_cost_websocket, ai_optimization, ai_policy, assessments, auth, business_profiles, chat, compliance, evidence, evidence_collection, foundation_evidence, frameworks, freemium, implementation, integrations, iq_agent, monitoring, policies, readiness, rbac_auth, reports, security, uk_compliance, users
from api.routers.admin import data_access, user_management, token_management
from api.middleware.error_handler import error_handler_middleware
from api.middleware.rate_limiter import rate_limit_middleware
from api.middleware.security_headers import security_headers_middleware
from database import test_async_database_connection, cleanup_db_connections, get_db, _AsyncSessionLocal as AsyncSessionLocal
from config.settings import settings
from monitoring.sentry import init_sentry
from config.ai_config import ai_config
from app.core.monitoring.setup import configure_from_settings
from app.core.monitoring.shutdown import get_shutdown_manager
logging.basicConfig(level=getattr(logging, settings.log_level.value),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) ->AsyncGenerator[None, None]:
    """
    Application lifespan context manager for startup/shutdown events
    """
    logger.info('--- Lifespan Startup: Initiated ---')
    logger.info('--- Lifespan Startup: Validating Configuration... ---')
    validate_configuration()
    logger.info('--- Lifespan Startup: Configuration Validated ---')
    logger.info('--- Lifespan Startup: Initializing Sentry... ---')
    init_sentry()
    logger.info('--- Lifespan Startup: Sentry Initialized ---')
    logger.info(
        '--- Lifespan Startup: Verifying Database Connection (Async)... ---')
    if not await test_async_database_connection():
        logger.error(
            '--- Lifespan Startup: Async database connection verification FAILED ---'
            )
        raise RuntimeError('Async database connection verification failed')
    logger.info(
        '--- Lifespan Startup: Database Connection Verified (Async) ---')
    logger.info('--- Lifespan Startup: Completed Successfully ---')
    yield
    logger.info('Shutting down ruleIQ API...')
    try:
        from api.routers.iq_agent import cleanup_iq_agent
        await cleanup_iq_agent()
        logger.info('IQ agent resources cleaned up')
    except Exception as e:
        logger.warning('IQ agent cleanup warning: %s' % e)
    await cleanup_db_connections()
    logger.info('Database connections closed')
    logger.info('ruleIQ API shutdown complete')


app = FastAPI(title='ruleIQ API', description=
    'AI-powered compliance and risk management platform', version='1.0.0',
    docs_url='/api/v1/docs' if settings.debug else None, redoc_url=
    '/api/v1/redoc' if settings.debug else None, openapi_url=
    '/api/v1/openapi.json', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
    allow_credentials=True, allow_methods=['GET', 'POST', 'PUT', 'DELETE',
    'OPTIONS', 'PATCH'], allow_headers=['*'], expose_headers=[
    'X-Total-Count', 'X-Rate-Limit-Remaining'])
app.add_middleware(TrustedHostMiddleware, allowed_hosts=['*'])
app.add_middleware(GZipMiddleware, minimum_size=1000)
configure_from_settings(app)
shutdown_manager = get_shutdown_manager()
shutdown_manager.install_signal_handlers()
app.middleware('http')(error_handler_middleware)
app.middleware('http')(security_headers_middleware)
app.middleware('http')(rate_limit_middleware)
app.include_router(auth.router, prefix='/api/v1/auth', tags=['authentication'])
app.include_router(users.router, prefix='/api/v1/users', tags=['users'])
app.include_router(assessments.router, prefix='/api/v1/assessments', tags=[
    'assessments'])
app.include_router(ai_assessments.router, prefix='/api/v1/ai-assessments',
    tags=['ai-assessments'])
app.include_router(ai_optimization.router, prefix='/api/v1/ai-optimization',
    tags=['ai-optimization'])
app.include_router(business_profiles.router, prefix=
    '/api/v1/business-profiles', tags=['business-profiles'])
app.include_router(chat.router, prefix='/api/v1/chat', tags=['chat'])
app.include_router(compliance.router, prefix='/api/v1/compliance', tags=[
    'compliance'])
app.include_router(evidence.router, prefix='/api/v1/evidence', tags=[
    'evidence'])
app.include_router(evidence_collection.router, prefix=
    '/api/v1/evidence-collection', tags=['evidence-collection'])
app.include_router(foundation_evidence.router, prefix=
    '/api/v1/foundation-evidence', tags=['foundation-evidence'])
app.include_router(frameworks.router, prefix='/api/v1/frameworks', tags=[
    'frameworks'])
app.include_router(implementation.router, prefix='/api/v1/implementation',
    tags=['implementation'])
app.include_router(integrations.router, prefix='/api/v1/integrations', tags
    =['integrations'])
app.include_router(iq_agent.router, prefix='/api/v1/iq', tags=['iq-agent',
    'graphrag'])
app.include_router(monitoring.router, prefix='/api/v1/monitoring', tags=[
    'monitoring'])
app.include_router(policies.router, prefix='/api/v1/policies', tags=[
    'policies'])
app.include_router(readiness.router, prefix='/api/v1/readiness', tags=[
    'readiness'])
app.include_router(reports.router, prefix='/api/v1/reports', tags=['reports'])
app.include_router(security.router, prefix='/api/v1/security', tags=[
    'security'])
app.include_router(ai_policy.router, prefix='/api/v1/ai', tags=['ai', 'policy']
    )
app.include_router(ai_cost_monitoring.router, prefix='/api/v1/ai', tags=[
    'ai', 'cost-monitoring'])
app.include_router(ai_cost_websocket.router, prefix='/api/v1/ai', tags=[
    'ai', 'websocket'])
app.include_router(freemium.router, prefix='/api/v1/freemium', tags=[
    'freemium'])
app.include_router(rbac_auth.router, prefix='/api/v1/rbac', tags=['rbac',
    'authentication'])
app.include_router(uk_compliance.router, prefix='/api/v1/uk-compliance',
    tags=['compliance', 'uk'])
app.include_router(user_management.router, prefix='/api/v1/admin', tags=[
    'admin', 'user-management'])
app.include_router(data_access.router, prefix='/api/v1/admin', tags=[
    'admin', 'data-access'])
app.include_router(token_management.router, prefix='/api/v1/admin', tags=[
    'admin', 'token-management'])


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException
    ) ->JSONResponse:
    """Handle HTTP exceptions with consistent error format"""
    return JSONResponse(status_code=exc.status_code, content={'error': {
        'message': exc.detail, 'type': 'http_exception', 'status_code': exc
        .status_code}})


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError
    ) ->JSONResponse:
    """Handle database exceptions"""
    logger.error('Database error: %s' % exc)
    return JSONResponse(status_code=500, content={'error': {'message':
        'Database operation failed', 'type': 'database_error',
        'status_code': 500}})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception
    ) ->JSONResponse:
    """Handle all other exceptions"""
    logger.error('Unexpected error: %s' % exc, exc_info=True)
    return JSONResponse(status_code=500, content={'error': {'message':
        'Internal server error', 'type': 'internal_error', 'status_code': 500}}
        )


async def health_check() ->Dict[str, Any]:
    """Basic health check endpoint"""
    return {'status': 'healthy', 'timestamp': time.time(), 'version': '1.0.0'}


async def api_health_check() ->Dict[str, Any]:
    """API v1 health check endpoint"""
    return {'status': 'healthy', 'timestamp': time.time(), 'version':
        '1.0.0', 'api_version': 'v1'}


@app.get('/api/v1/health/detailed')
async def api_health_detailed() ->Dict[str, Any]:
    """Detailed API v1 health check endpoint with component status"""
    db_status = 'unknown'
    ai_status = 'unknown'
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text('SELECT 1'))
            if result:
                db_status = 'healthy'
    except Exception as e:
        db_status = f'unhealthy: {str(e)}'
    try:
        ai_config._initialize_google_ai()
        ai_status = 'healthy'
    except Exception as e:
        ai_status = f'unhealthy: {str(e)}'
    overall_status = ('healthy' if db_status == 'healthy' and ai_status ==
        'healthy' else 'degraded')
    return {'status': overall_status, 'timestamp': time.time(), 'version':
        '1.0.0', 'api_version': 'v1', 'components': {'database': db_status,
        'ai_services': ai_status, 'redis': 'not_configured'}}


@app.get('/health/ready')
async def readiness_check() ->Dict[str, Any]:
    """Readiness check with database connectivity"""
    db = None
    try:
        db = next(get_db())
        db.execute(text('SELECT 1'))
        return {'status': 'ready', 'database': 'connected', 'timestamp':
            time.time()}
    except Exception as e:
        logger.error('Readiness check failed: %s' % e)
        raise HTTPException(status_code=HTTP_SERVICE_UNAVAILABLE, detail=
            'Service not ready - database connection failed')
    finally:
        if db is not None:
            db.close()


@app.get('/health/live')
async def liveness_check() ->Dict[str, Any]:
    """Liveness check for container orchestration"""
    return {'status': 'alive', 'timestamp': time.time(), 'uptime': time.
        time() - getattr(app.state, 'start_time', time.time())}


@app.get('/')
async def root() ->Dict[str, Any]:
    """Root endpoint with API information"""
    return {'name': 'ruleIQ API', 'version': '1.0.0', 'description':
        'AI-powered compliance and risk management platform',
        'documentation': '/docs' if settings.debug else None, 'health':
        '/health'}


@app.on_event('startup')
async def startup_event() ->None:
    """Set application start time"""
    app.state.start_time = time.time()


@app.get('/debug/config')
async def debug_config() ->Dict[str, Any]:
    """Diagnostic endpoint - remove in production"""
    from config.settings import get_settings
    settings = get_settings()
    return {'jwt_secret_first_10': settings.jwt_secret[:10] if settings.
        jwt_secret else None, 'jwt_secret_length': len(settings.jwt_secret) if
        settings.jwt_secret else 0, 'working_directory': os.getcwd(),
        'env_file_exists': os.path.exists('.env.local'), 'JWT_SECRET_env': 
        os.getenv('JWT_SECRET')[:10] if os.getenv('JWT_SECRET') else None}


def validate_configuration() ->None:
    """Validate critical configuration settings"""
    required_vars = ['database_url', 'jwt_secret_key']
    missing_vars = []
    for var in required_vars:
        if not getattr(settings, var, None):
            missing_vars.append(var.upper())
    if missing_vars:
        raise ValueError(
            f'Missing required environment variables: {missing_vars}')


if __name__ == '__main__':
    uvicorn.run('api.main:app', host=str(settings.host), port=int(settings.
        port), reload=bool(settings.debug), log_level=str(settings.
        log_level).lower(), workers=1 if settings.debug else 4)
