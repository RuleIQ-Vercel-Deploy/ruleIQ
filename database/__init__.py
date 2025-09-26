"""
Database models package.
Import all models to ensure they are registered with SQLAlchemy.
Provides database initialization utilities.
"""

import os
import logging

# Set up logging for database package initialization
logger = logging.getLogger(__name__)

# Detect Cloud Run environment
IS_CLOUD_RUN = bool(os.getenv('K_SERVICE') or os.getenv('CLOUD_RUN_JOB'))

if IS_CLOUD_RUN:
    logger.info('🌩️ Cloud Run: Initializing database package with lazy loading')
else:
    logger.debug('Initializing database package')

# Import database setup and initialization with error handling
try:
    from .db_setup import (
        Base,
        init_db,
        test_database_connection,
        test_async_database_connection,
        cleanup_db_connections,
        get_engine_info,
        get_db,
        get_async_db,
        get_db_context,
        DatabaseConfig,
        get_async_session_maker,
    )
    
    # Import session locals with lazy evaluation to prevent eager initialization
    try:
        from .db_setup import _ASYNC_SESSION_LOCAL as _AsyncSessionLocal
        from .db_setup import _SESSION_LOCAL
        if IS_CLOUD_RUN:
            logger.debug('🌩️ Cloud Run: Database session locals imported successfully')
    except ImportError as session_error:
        # Provide fallback None values if session locals can't be imported
        _AsyncSessionLocal = None
        _SESSION_LOCAL = None
        if IS_CLOUD_RUN:
            logger.warning('🌩️ Cloud Run: Session locals not available: %s', session_error)
        else:
            logger.warning('Session locals not available: %s', session_error)
    
    if IS_CLOUD_RUN:
        logger.info('🌩️ Cloud Run: Database setup imported successfully')
    else:
        logger.debug('Database setup imported successfully')
        
except ImportError as db_error:
    if IS_CLOUD_RUN:
        logger.warning('🌩️ Cloud Run: Failed to import database setup: %s - some database functions may not be available', db_error)
        # Provide fallback implementations for Cloud Run
        from typing import Generator, AsyncGenerator, Any
        from contextlib import contextmanager
        
        Base = None
        init_db = lambda: False
        test_database_connection = lambda: False
        
        async def test_async_database_connection() -> bool:
            return False
        
        async def cleanup_db_connections() -> None:
            return None
        
        get_engine_info = lambda: {}
        
        def get_db() -> Generator[Any, None, None]:
            if False:
                yield None
        
        async def get_async_db() -> AsyncGenerator[Any, None]:
            if False:
                yield None
        
        @contextmanager
        def _get_db_context():
            yield None
        
        get_db_context = _get_db_context
        get_async_session_maker = lambda: None
        
        class DatabaseConfig:
            """Stub DatabaseConfig class for Cloud Run fallback"""
            pass
        _AsyncSessionLocal = None
        _SESSION_LOCAL = None
    else:
        logger.error('Failed to import database setup: %s', db_error)
        raise
except Exception as setup_error:
    if IS_CLOUD_RUN:
        logger.warning('🌩️ Cloud Run: Unexpected error importing database setup: %s - continuing with limited functionality', setup_error)
        # Provide fallback implementations
        from typing import Generator, AsyncGenerator, Any
        from contextlib import contextmanager
        
        Base = None
        init_db = lambda: False
        test_database_connection = lambda: False
        
        async def test_async_database_connection() -> bool:
            return False
        
        async def cleanup_db_connections() -> None:
            return None
        
        get_engine_info = lambda: {}
        
        def get_db() -> Generator[Any, None, None]:
            if False:
                yield None
        
        async def get_async_db() -> AsyncGenerator[Any, None]:
            if False:
                yield None
        
        @contextmanager
        def _get_db_context():
            yield None
        
        get_db_context = _get_db_context
        get_async_session_maker = lambda: None
        
        class DatabaseConfig:
            """Stub DatabaseConfig class for Cloud Run fallback"""
            pass
        _AsyncSessionLocal = None
        _SESSION_LOCAL = None
    else:
        logger.error('Unexpected error importing database setup: %s', setup_error)
        raise

# Provide None defaults for all model variables to support lazy loading
AssessmentLead = FreemiumAssessmentSession = AIQuestionBank = None
LeadScoringEvent = ConversionEvent = Policy = Evidence = None
Integration = EvidenceCollection = IntegrationEvidenceItem = None
IntegrationHealthLog = EvidenceAuditLog = None
Role = Permission = UserRole = RolePermission = None
FrameworkAccess = UserSession = AuditLog = DataAccess = None

def load_models():
    """
    Load all database models to ensure they are registered with SQLAlchemy.
    This function should be called explicitly when models are needed.
    """
    global AssessmentLead, FreemiumAssessmentSession, AIQuestionBank
    global LeadScoringEvent, ConversionEvent, Policy, Evidence
    global Integration, EvidenceCollection, IntegrationEvidenceItem
    global IntegrationHealthLog, EvidenceAuditLog
    global Role, Permission, UserRole, RolePermission
    global FrameworkAccess, UserSession, AuditLog, DataAccess

    # Import core models if available
    try:
        from . import models  # Assuming models are in a models.py or similar
        if IS_CLOUD_RUN:
            logger.debug('🌩️ Cloud Run: Core models imported successfully')
        else:
            logger.debug('Core models imported successfully')
    except ImportError as e:
        logger.warning('Core models import failed: %s', e)

    # Freemium models with error handling
    try:
        from .assessment_lead import AssessmentLead as _AssessmentLead
        from .freemium_assessment_session import FreemiumAssessmentSession as _FreemiumAssessmentSession
        from .ai_question_bank import AIQuestionBank as _AIQuestionBank
        from .lead_scoring_event import LeadScoringEvent as _LeadScoringEvent
        from .conversion_event import ConversionEvent as _ConversionEvent
        from .models.policy import Policy as _Policy
        from .models.evidence import Evidence as _Evidence
        from .models.integrations import (
            Integration as _Integration,
            EvidenceCollection as _EvidenceCollection,
            IntegrationEvidenceItem as _IntegrationEvidenceItem,
            IntegrationHealthLog as _IntegrationHealthLog,
            EvidenceAuditLog as _EvidenceAuditLog,
        )

        # Assign to module-level variables
        AssessmentLead = _AssessmentLead
        FreemiumAssessmentSession = _FreemiumAssessmentSession
        AIQuestionBank = _AIQuestionBank
        LeadScoringEvent = _LeadScoringEvent
        ConversionEvent = _ConversionEvent
        Policy = _Policy
        Evidence = _Evidence
        Integration = _Integration
        EvidenceCollection = _EvidenceCollection
        IntegrationEvidenceItem = _IntegrationEvidenceItem
        IntegrationHealthLog = _IntegrationHealthLog
        EvidenceAuditLog = _EvidenceAuditLog

        if IS_CLOUD_RUN:
            logger.debug('🌩️ Cloud Run: Freemium and integration models imported successfully')
        else:
            logger.debug('Freemium and integration models imported successfully')

    except ImportError as freemium_error:
        if IS_CLOUD_RUN:
            logger.warning('🌩️ Cloud Run: Failed to import freemium/integration models: %s - some freemium features may not be available', freemium_error)
        else:
            logger.warning('Failed to import freemium/integration models: %s', freemium_error)

    # RBAC models with error handling
    try:
        from .rbac import (
            Role as _Role,
            Permission as _Permission,
            UserRole as _UserRole,
            RolePermission as _RolePermission,
            FrameworkAccess as _FrameworkAccess,
            UserSession as _UserSession,
            AuditLog as _AuditLog,
            DataAccess as _DataAccess,
        )

        # Assign to module-level variables
        Role = _Role
        Permission = _Permission
        UserRole = _UserRole
        RolePermission = _RolePermission
        FrameworkAccess = _FrameworkAccess
        UserSession = _UserSession
        AuditLog = _AuditLog
        DataAccess = _DataAccess

        if IS_CLOUD_RUN:
            logger.debug('🌩️ Cloud Run: RBAC models imported successfully')
        else:
            logger.debug('RBAC models imported successfully')

    except ImportError as rbac_error:
        if IS_CLOUD_RUN:
            logger.warning('🌩️ Cloud Run: Failed to import RBAC models: %s - RBAC features may not be available', rbac_error)
        else:
            logger.warning('Failed to import RBAC models: %s', rbac_error)

if IS_CLOUD_RUN:
    logger.info('🌩️ Cloud Run: Database package initialization completed')
else:
    logger.debug('Database package initialization completed')


__all__ = [
    # Database setup and utilities
    "Base",
    "init_db",
    "test_database_connection",
    "test_async_database_connection",
    "cleanup_db_connections",
    "get_engine_info",
    "get_db",
    "get_async_db",
    "get_db_context",
    "get_async_session_maker",
    "DatabaseConfig",
    # Legacy exports for backward compatibility
    "_AsyncSessionLocal",
    "_SESSION_LOCAL",
    # Freemium models
    "AssessmentLead",
    "FreemiumAssessmentSession",
    "AIQuestionBank",
    "LeadScoringEvent",
    "ConversionEvent",
    "Policy",
    "Evidence",
    "Integration",
    "EvidenceCollection",
    "IntegrationEvidenceItem",
    "IntegrationHealthLog",
    "EvidenceAuditLog",
    # RBAC models
    "Role",
    "Permission",
    "UserRole",
    "RolePermission",
    "FrameworkAccess",
    "UserSession",
    "AuditLog",
    "DataAccess",
    # Function to load models
    "load_models",
]
