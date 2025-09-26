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
            logger.warning(f'🌩️ Cloud Run: Session locals not available: {session_error}')
        else:
            logger.warning(f'Session locals not available: {session_error}')
    
    if IS_CLOUD_RUN:
        logger.info('🌩️ Cloud Run: Database setup imported successfully')
    else:
        logger.debug('Database setup imported successfully')
        
except ImportError as db_error:
    error_msg = f'Failed to import database setup: {db_error}'
    if IS_CLOUD_RUN:
        logger.warning(f'🌩️ Cloud Run: {error_msg} - some database functions may not be available')
        # Provide fallback implementations for Cloud Run
        Base = None
        init_db = lambda: False
        test_database_connection = lambda: False
        
        async def test_async_database_connection() -> bool:
            return False
        
        async def cleanup_db_connections() -> None:
            return None
        
        get_engine_info = lambda: {}
        get_db = lambda: None
        
        async def get_async_db():
            yield None
        
        get_db_context = lambda: None
        get_async_session_maker = lambda: None
        DatabaseConfig = None
        _AsyncSessionLocal = None
        _SESSION_LOCAL = None
    else:
        logger.error(error_msg)
        raise
except Exception as setup_error:
    error_msg = f'Unexpected error importing database setup: {setup_error}'
    if IS_CLOUD_RUN:
        logger.warning(f'🌩️ Cloud Run: {error_msg} - continuing with limited functionality')
        # Provide fallback implementations
        Base = None
        init_db = lambda: False
        test_database_connection = lambda: False
        
        async def test_async_database_connection() -> bool:
            return False
        
        async def cleanup_db_connections() -> None:
            return None
        
        get_engine_info = lambda: {}
        get_db = lambda: None
        
        async def get_async_db():
            yield None
        
        get_db_context = lambda: None
        get_async_session_maker = lambda: None
        DatabaseConfig = None
        _AsyncSessionLocal = None
        _SESSION_LOCAL = None
    else:
        logger.error(error_msg)
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
        logger.warning(f'Core models import failed: {e}')

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
        error_msg = f'Failed to import freemium/integration models: {freemium_error}'
        if IS_CLOUD_RUN:
            logger.warning(f'🌩️ Cloud Run: {error_msg} - some freemium features may not be available')
        else:
            logger.warning(error_msg)

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
        error_msg = f'Failed to import RBAC models: {rbac_error}'
        if IS_CLOUD_RUN:
            logger.warning(f'🌩️ Cloud Run: {error_msg} - RBAC features may not be available')
        else:
            logger.warning(error_msg)

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
