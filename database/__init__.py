"""
Database models package.
Import all models to ensure they are registered with SQLAlchemy.
Provides database initialization utilities.
"""

from .ai_question_bank import AIQuestionBank

# Freemium models
from .assessment_lead import AssessmentLead
from .assessment_question import AssessmentQuestion
from .assessment_session import AssessmentSession
from .business_profile import BusinessProfile
from .chat_conversation import ChatConversation
from .chat_message import ChatMessage
from .compliance_framework import ComplianceFramework
from .conversion_event import ConversionEvent

# Import database setup and initialization
from .db_setup import _ASYNC_SESSION_LOCAL as _AsyncSessionLocal
from .db_setup import (
    _SESSION_LOCAL,
    Base,
    DatabaseConfig,
    cleanup_db_connections,
    get_async_db,
    get_db,
    get_db_context,
    get_engine_info,
    init_db,
    test_async_database_connection,
    test_database_connection,
)
from .evidence_item import EvidenceItem
from .freemium_assessment_session import FreemiumAssessmentSession
from .generated_policy import GeneratedPolicy
from .implementation_plan import ImplementationPlan
from .lead_scoring_event import LeadScoringEvent
from .models.evidence import Evidence
from .models.integrations import (
    EvidenceAuditLog,
    EvidenceCollection,
    Integration,
    IntegrationEvidenceItem,
    IntegrationHealthLog,
)
from .models.policy import Policy
from .rbac import (
    AuditLog,
    DataAccess,
    FrameworkAccess,
    Permission,
    Role,
    RolePermission,
    UserRole,
    UserSession,
)
from .readiness_assessment import ReadinessAssessment
from .report_schedule import ReportSchedule

# Import all models to ensure they're registered with SQLAlchemy
from .user import User

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
    "DatabaseConfig",
    # Legacy exports for backward compatibility
    "_AsyncSessionLocal",
    "_SESSION_LOCAL",
    # Models
    "User",
    "BusinessProfile",
    "ComplianceFramework",
    "EvidenceItem",
    "AssessmentSession",
    "AssessmentQuestion",
    "ImplementationPlan",
    "ReadinessAssessment",
    "GeneratedPolicy",
    "ChatConversation",
    "ChatMessage",
    "ReportSchedule",
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
]
