"""
Simplified pytest configuration for ruleIQ tests.
Fixes database setup issues and handles missing dependencies gracefully.
"""

import asyncio
import atexit
import os
import sys
import warnings
import logging
from typing import Generator, Dict, Any, Optional
from uuid import uuid4, UUID
from datetime import datetime, timedelta
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# =============================================================================
# ASYNC EVENT LOOP CONFIGURATION
# =============================================================================

# Fix event loop policy for tests
if sys.platform.startswith("win"):
    # Windows ProactorEventLoop closes all socket connections on exit
    # which can cause issues with database connections
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Global variable to track if cleanup has been performed
_cleanup_done = False


def cleanup_async_engines():
    """Cleanup async engines at exit."""
    global _cleanup_done
    if not _cleanup_done:
        try:
            # Try to get the current event loop
            loop = asyncio.get_event_loop()
            if not loop.is_closed():
                from database.db_setup import cleanup_db_connections

                loop.run_until_complete(cleanup_db_connections())
        except Exception:
            pass
        _cleanup_done = True


# Register cleanup at exit
atexit.register(cleanup_async_engines)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop

    # Ensure all async generators are closed
    try:
        loop.run_until_complete(loop.shutdown_asyncgens())
    except Exception:
        pass

    # Clean up pending tasks
    try:
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        # Run until all tasks are cancelled
        if pending:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
    except Exception:
        pass

    # Close the loop
    loop.close()


# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================

# Suppress warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
logging.getLogger("passlib").setLevel(logging.ERROR)

# Set test environment variables
os.environ["ENV"] = "testing"
os.environ["DATABASE_URL"] = (
    "postgresql://neondb_owner:npg_s0JhnfGNy3Ze@ep-wild-grass-a8o37wq8-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
)
os.environ["SECRET_KEY"] = "test_secret_key_for_pytest_sessions"
os.environ["GOOGLE_API_KEY"] = "test_key_for_mocking"
os.environ["SENTRY_DSN"] = ""
os.environ["USE_MOCK_AI"] = "true"
os.environ["REDIS_URL"] = ""  # Disable Redis for tests
os.environ["TESTING"] = "true"  # Flag for testing mode

# Generate Fernet key
from cryptography.fernet import Fernet

os.environ["FERNET_KEY"] = Fernet.generate_key().decode()

# =============================================================================
# AI MOCKING
# =============================================================================

import unittest.mock

# Mock google.generativeai
mock_google = unittest.mock.MagicMock()
mock_genai = unittest.mock.MagicMock()
mock_types = unittest.mock.MagicMock()

# Mock the HarmCategory and HarmBlockThreshold enums
mock_types.HarmCategory = unittest.mock.MagicMock()
mock_types.HarmCategory.HARM_CATEGORY_HATE_SPEECH = "HARM_CATEGORY_HATE_SPEECH"
mock_types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT = "HARM_CATEGORY_DANGEROUS_CONTENT"
mock_types.HarmCategory.HARM_CATEGORY_HARASSMENT = "HARM_CATEGORY_HARASSMENT"
mock_types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT = "HARM_CATEGORY_SEXUALLY_EXPLICIT"

mock_types.HarmBlockThreshold = unittest.mock.MagicMock()
mock_types.HarmBlockThreshold.BLOCK_NONE = "BLOCK_NONE"

# Mock the response
mock_response = unittest.mock.MagicMock()
mock_response.text = "Mock AI response for testing"
mock_response.parts = [unittest.mock.MagicMock()]
mock_response.parts[0].text = "Mock AI response for testing"
mock_response.candidates = []

# Mock the model
mock_model = unittest.mock.MagicMock()
mock_model.generate_content.return_value = mock_response
mock_model.generate_content_async = unittest.mock.AsyncMock(return_value=mock_response)
mock_model.model_name = "gemini-2.5-flash"


# Mock streaming
def mock_stream_generator():
    for i in range(3):
        chunk = unittest.mock.MagicMock()
        chunk.text = f"Stream chunk {i}"
        chunk.parts = [unittest.mock.MagicMock()]
        chunk.parts[0].text = f"Stream chunk {i}"
        yield chunk


mock_model.generate_content_stream.side_effect = lambda *args, **kwargs: mock_stream_generator()

# Mock caching
mock_cached_content = unittest.mock.MagicMock()
mock_cached_content.name = "mock-cache"
mock_genai.caching.CachedContent.create.return_value = mock_cached_content

# Set up the module structure
mock_genai.GenerativeModel.return_value = mock_model
mock_genai.types = mock_types
mock_genai.configure.return_value = None
mock_genai.caching = unittest.mock.MagicMock()
mock_genai.caching.CachedContent = unittest.mock.MagicMock()
mock_genai.caching.CachedContent.create.return_value = mock_cached_content

mock_google.generativeai = mock_genai

# Install the mocks
sys.modules["google"] = mock_google
sys.modules["google.generativeai"] = mock_genai
sys.modules["google.generativeai.types"] = mock_types

# Mock boto3 and botocore
mock_boto3 = unittest.mock.MagicMock()
mock_botocore = unittest.mock.MagicMock()
mock_botocore.exceptions.ClientError = Exception
mock_botocore.exceptions.NoCredentialsError = Exception
mock_botocore.exceptions.BotoCoreError = Exception

sys.modules["boto3"] = mock_boto3
sys.modules["botocore"] = mock_botocore
sys.modules["botocore.exceptions"] = mock_botocore.exceptions
sys.modules["google.generativeai.caching"] = mock_genai.caching

# =============================================================================
# MOCK REDIS TO AVOID DEPENDENCY ISSUES
# =============================================================================


class MockRedis:
    """Mock Redis client for tests with async support."""

    def __init__(self, *args, **kwargs):
        self.data = {}
        self._closed = False

    async def get(self, key):
        """Async get method."""
        return self.data.get(key)

    async def set(self, key, value, ex=None):
        """Async set method."""
        self.data[key] = value
        return True

    async def setex(self, key, ttl, value):
        """Async setex method for setting with expiration."""
        self.data[key] = value
        return True

    async def delete(self, *keys):
        """Async delete method."""
        deleted = 0
        for key in keys:
            if key in self.data:
                del self.data[key]
                deleted += 1
        return deleted

    async def exists(self, key):
        """Async exists method."""
        return key in self.data

    async def keys(self, pattern):
        """Async keys method with pattern matching."""
        # Simple pattern matching for tests
        if pattern == "*":
            return list(self.data.keys())

        # Handle simple patterns like "prefix:*"
        if pattern.endswith("*"):
            prefix = pattern[:-1]
            return [k for k in self.data.keys() if k.startswith(prefix)]

        # Handle patterns with * in the middle
        pattern_parts = pattern.split("*")
        matching_keys = []
        for key in self.data.keys():
            match = True
            key_pos = 0
            for part in pattern_parts:
                if part:  # Skip empty parts from consecutive *
                    pos = key.find(part, key_pos)
                    if pos == -1:
                        match = False
                        break
                    key_pos = pos + len(part)
            if match:
                matching_keys.append(key)
        return matching_keys

    async def ping(self):
        """Async ping method."""
        if self._closed:
            raise ConnectionError("Connection is closed")
        return True

    async def close(self):
        """Async close method."""
        self._closed = True

    def __repr__(self):
        return f"<MockRedis(data_keys={len(self.data)})>"


# Mock redis module
mock_redis_module = unittest.mock.MagicMock()
mock_redis_module.Redis = MockRedis
mock_redis_module.from_url = MockRedis

# Mock redis.asyncio
mock_redis_asyncio = unittest.mock.MagicMock()
mock_redis_asyncio.Redis = MockRedis
mock_redis_asyncio.from_url = MockRedis

sys.modules["redis"] = mock_redis_module
sys.modules["redis.asyncio"] = mock_redis_asyncio

# =============================================================================
# MOCK ASYNCPG TO AVOID MISSING DEPENDENCY
# =============================================================================

# Mock asyncpg module
mock_asyncpg = unittest.mock.MagicMock()
sys.modules["asyncpg"] = mock_asyncpg

# =============================================================================
# PROJECT IMPORTS
# =============================================================================

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import database models after mocking
from database.db_setup import Base
from database.user import User
from database.business_profile import BusinessProfile
from database.compliance_framework import ComplianceFramework
from database.evidence_item import EvidenceItem
from database.generated_policy import GeneratedPolicy
from database.assessment_question import AssessmentQuestion
from database.assessment_session import AssessmentSession
from database.chat_conversation import ChatConversation
from database.chat_message import ChatMessage
from database.implementation_plan import ImplementationPlan

# IntegrationConfiguration was moved to database.models.integrations.Integration
from database.readiness_assessment import ReadinessAssessment
from database.report_schedule import ReportSchedule

# Import freemium models
from database.assessment_lead import AssessmentLead
from database.freemium_assessment_session import FreemiumAssessmentSession
from database.ai_question_bank import AIQuestionBank
from database.lead_scoring_event import LeadScoringEvent
from database.conversion_event import ConversionEvent

# Try to import integration models if they exist
try:
    from database.models.integrations import (
        Integration,
        EvidenceCollection,
        IntegrationEvidenceItem,
        IntegrationHealthLog,
        EvidenceAuditLog,
    )
except ImportError:
    # Models might not exist in all branches
    pass

# Import RBAC models
try:
    from database.rbac import (
        Role, Permission, UserRole, RolePermission, 
        FrameworkAccess, AuditLog, UserSession, DataAccess
    )
except ImportError:
    # RBAC models might not exist in all branches
    pass

# =============================================================================
# DATABASE SETUP
# =============================================================================

# Get database URL and convert to sync
db_url = os.environ["DATABASE_URL"]
if "+asyncpg" in db_url:
    db_url = db_url.replace("+asyncpg", "+psycopg2")
elif "postgresql://" in db_url and "+psycopg2" not in db_url:
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

# Create engine with proper settings for tests
engine = create_engine(
    db_url,
    poolclass=StaticPool,
    echo=False,
    connect_args={"connect_timeout": 10},
)

# Create session factory
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# =============================================================================
# DATABASE FIXTURES
# =============================================================================


@pytest.fixture(scope="session", autouse=True)
def setup_database(event_loop):
    """Set up database for entire test session."""
    # Run Alembic migrations instead of create_all
    import subprocess
    import sys
    import os

    # Change to project root directory
    original_dir = os.getcwd()
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)

    try:
        # Run alembic upgrade to latest
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"], capture_output=True, text=True
        )

        if result.returncode != 0:
            print(f"Alembic migration failed: {result.stderr}")
            raise RuntimeError(f"Failed to run database migrations: {result.stderr}")
    finally:
        os.chdir(original_dir)

    # Ensure all tables are created (including freemium tables)
    from database import Base
    Base.metadata.create_all(bind=engine)

    # Initialize default frameworks
    session = TestSessionLocal()
    try:
        frameworks = [
            {
                "name": "GDPR",
                "display_name": "General Data Protection Regulation",
                "description": "EU data protection and privacy regulation",
                "category": "Data Protection",
            },
            {
                "name": "ISO27001",
                "display_name": "ISO/IEC 27001:2022",
                "description": "Information security management systems",
                "category": "Information Security",
            },
            {
                "name": "SOC2",
                "display_name": "SOC 2 Type II",
                "description": "Service Organization Control 2",
                "category": "Security & Compliance",
            },
        ]

        for fw_data in frameworks:
            existing = session.query(ComplianceFramework).filter_by(name=fw_data["name"]).first()
            if not existing:
                framework = ComplianceFramework(**fw_data)
                session.add(framework)

        session.commit()
    except Exception as e:
        print(f"Warning: Failed to initialize frameworks: {e}")
        session.rollback()
    finally:
        session.close()

    yield

    # Skip cleanup of async connections for now to avoid issues
    # The engines will be cleaned up when the process exits

    # Clean up sync engine
    engine.dispose()

    # Clean up - optional, can be commented out to preserve test data
    # Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    """Provide a database session for tests."""
    session = TestSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# Async session fixture that returns sync session for compatibility
@pytest.fixture
def async_db_session(db_session):
    """Provide sync session for async fixtures (compatibility)."""
    return db_session


# Proper async database session fixture
@pytest_asyncio.fixture
async def real_async_db_session():
    """Provide a real async database session for tests."""
    from database.db_setup import get_async_db

    async for session in get_async_db():
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# =============================================================================
# USER AND AUTH FIXTURES
# =============================================================================

TEST_USER_ID = UUID("12345678-1234-5678-9012-123456789012")
TEST_BUSINESS_PROFILE_ID = UUID("87654321-4321-8765-4321-876543218765")


@pytest.fixture
def sample_user(db_session):
    """Create a test user."""
    # Check if user already exists and return it
    existing = db_session.query(User).filter_by(id=TEST_USER_ID).first()
    if existing:
        return existing

    # Create a proper bcrypt hash for testing
    from api.dependencies.auth import get_password_hash

    user = User(
        id=TEST_USER_ID,
        email="test@example.com",
        hashed_password=get_password_hash("TestPassword123!"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def async_sample_user(sample_user):
    """Async user fixture for compatibility."""
    return sample_user


@pytest.fixture
def sample_business_profile(db_session, sample_user):
    """Create a test business profile."""
    # Check if profile already exists and return it
    existing = db_session.query(BusinessProfile).filter_by(id=TEST_BUSINESS_PROFILE_ID).first()
    if existing:
        return existing

    profile = BusinessProfile(
        id=TEST_BUSINESS_PROFILE_ID,
        user_id=sample_user.id,
        company_name="Test Company",
        industry="Technology",
        employee_count=50,
        country="USA",
        handles_personal_data=True,
        processes_payments=False,
        stores_health_data=False,
        provides_financial_services=False,
        operates_critical_infrastructure=False,
        has_international_operations=True,
        existing_frameworks=["ISO27001", "SOC2"],
        planned_frameworks=[],
        cloud_providers=["AWS", "Azure"],
        saas_tools=["Office365", "Salesforce"],
        development_tools=["GitHub"],
        compliance_budget="50000-100000",
        compliance_timeline="6-12 months",
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile


@pytest.fixture
def async_sample_business_profile(sample_business_profile):
    """Async business profile fixture for compatibility."""
    return sample_business_profile


@pytest.fixture
def auth_token(sample_user):
    """Generate auth token."""
    from api.dependencies.auth import create_access_token

    token_data = {"sub": str(sample_user.id)}
    return create_access_token(data=token_data, expires_delta=timedelta(minutes=30))


@pytest.fixture
def authenticated_headers(auth_token):
    """Auth headers for API requests."""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def another_user(db_session):
    """Create another test user."""
    from api.dependencies.auth import get_password_hash

    user = User(
        id=uuid4(),
        email=f"another-user-{uuid4()}@example.com",
        hashed_password=get_password_hash("AnotherPassword123!"),
        full_name="Another User",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    yield user

    # Cleanup
    db_session.delete(user)
    db_session.commit()


@pytest.fixture
def another_auth_token(another_user):
    """Generate auth token for another user."""
    from api.dependencies.auth import create_access_token

    token_data = {"sub": str(another_user.id)}
    return create_access_token(data=token_data, expires_delta=timedelta(minutes=30))


@pytest.fixture
def expired_token(sample_user):
    """Generate an expired auth token for testing."""
    from api.dependencies.auth import create_access_token

    token_data = {"sub": str(sample_user.id)}
    # Create a token that's already expired
    return create_access_token(data=token_data, expires_delta=timedelta(minutes=-1))


@pytest.fixture
def another_authenticated_headers(another_auth_token):
    """Auth headers for another user."""
    return {"Authorization": f"Bearer {another_auth_token}"}


# =============================================================================
# ASYNC SESSION WRAPPER
# =============================================================================


class AsyncSessionWrapper:
    """Wrapper to make sync sessions work with async code in tests."""

    def __init__(self, sync_session):
        self.sync_session = sync_session
        self._closed = False

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        # Don't close here as the sync session is managed by the fixture
        return False

    async def execute(self, stmt):
        return self.sync_session.execute(stmt)

    async def commit(self):
        if not self._closed:
            self.sync_session.commit()

    async def rollback(self):
        if not self._closed:
            self.sync_session.rollback()

    async def close(self):
        # Mark as closed but don't actually close the sync session
        # as it's managed by the fixture
        self._closed = True

    def add(self, instance):
        self.sync_session.add(instance)

    def delete(self, instance):
        self.sync_session.delete(instance)

    async def refresh(self, instance):
        self.sync_session.refresh(instance)

    async def merge(self, instance):
        return self.sync_session.merge(instance)

    def query(self, *args, **kwargs):
        return self.sync_session.query(*args, **kwargs)

    async def flush(self):
        self.sync_session.flush()

    async def scalar(self, stmt):
        result = await self.execute(stmt)
        return result.scalar()

    async def scalars(self, stmt):
        result = await self.execute(stmt)
        return result.scalars()

    async def get(self, model, ident):
        return self.sync_session.get(model, ident)

    def begin(self):
        return self

    async def __aiter__(self):
        yield self


# =============================================================================
# TEST CLIENT FIXTURES
# =============================================================================


@pytest.fixture
def client(db_session, sample_user):
    """Authenticated test client."""
    from tests.test_app import create_test_app
    from api.dependencies.auth import get_current_active_user, get_current_user
    from database.db_setup import get_async_db, get_db

    # Create test app
    app = create_test_app()

    # Override dependencies
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_async_db():
        # For TestClient, return regular generator, not async
        yield AsyncSessionWrapper(db_session)

    def override_get_current_user():
        return sample_user

    def override_get_current_active_user():
        return sample_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_async_db] = override_get_async_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides
    app.dependency_overrides.clear()


@pytest.fixture
def unauthenticated_client(db_session):
    """Unauthenticated test client."""
    from tests.test_app import create_test_app
    from database.db_setup import get_async_db, get_db

    # Create test app
    app = create_test_app()

    # Override only database dependencies
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_async_db():
        # For TestClient, return regular generator, not async
        yield AsyncSessionWrapper(db_session)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_async_db] = override_get_async_db

    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides
    app.dependency_overrides.clear()


# =============================================================================
# DOMAIN FIXTURES
# =============================================================================


@pytest.fixture
def sample_compliance_framework(db_session):
    """Create a test compliance framework."""
    existing = db_session.query(ComplianceFramework).filter_by(name="ISO27001").first()
    if existing:
        return existing

    framework = ComplianceFramework(
        id=uuid4(),
        name="ISO27001",
        display_name="ISO/IEC 27001:2022",
        description="Information security management systems",
        category="Information Security",
    )
    db_session.add(framework)
    db_session.commit()
    db_session.refresh(framework)
    return framework


@pytest.fixture
def sample_evidence_item(db_session, sample_business_profile, sample_compliance_framework):
    """Create a test evidence item."""
    evidence = EvidenceItem(
        id=uuid4(),
        user_id=sample_business_profile.user_id,
        business_profile_id=sample_business_profile.id,
        framework_id=sample_compliance_framework.id,
        evidence_name="Sample Security Policy",
        evidence_type="policy_document",
        control_reference="A.5.1",
        description="A sample security policy document for testing.",
        status="active",
        file_path="/path/to/sample/policy.pdf",
        automation_source="manual",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(evidence)
    db_session.commit()
    db_session.refresh(evidence)

    yield evidence

    # Cleanup
    db_session.delete(evidence)
    db_session.commit()


@pytest.fixture
def evidence_item_instance(sample_evidence_item):
    """Alias for sample_evidence_item for compatibility."""
    return sample_evidence_item


@pytest.fixture
def sample_policy_document(db_session, sample_business_profile):
    """Create a test policy document."""
    policy = GeneratedPolicy(
        id=uuid4(),
        user_id=sample_business_profile.user_id,
        business_profile_id=sample_business_profile.id,
        policy_name="Sample Acceptable Use Policy",
        policy_type="acceptable_use",
        content="This is a sample acceptable use policy content...",
        version="1.0",
        status="draft",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(policy)
    db_session.commit()
    db_session.refresh(policy)

    yield policy

    # Cleanup
    db_session.delete(policy)
    db_session.commit()


# =============================================================================
# UTILITY FIXTURES
# =============================================================================


@pytest.fixture(autouse=True)
def ensure_ai_mocking():
    """Ensure AI is mocked."""
    yield mock_model


@pytest.fixture(autouse=True)
def reset_app_state():
    """Reset FastAPI app state between tests."""
    yield
    try:
        from main import app

        app.dependency_overrides.clear()
        if hasattr(app, "_openapi"):
            delattr(app, "_openapi")
        if hasattr(app, "_route_cache"):
            delattr(app, "_route_cache")
    except Exception:
        pass


@pytest.fixture(autouse=True)
async def cleanup_async_resources():
    """Cleanup async resources after each test."""
    yield
    # Give time for any pending async operations
    await asyncio.sleep(0.01)

    # Get current loop
    loop = asyncio.get_running_loop()

    # Cancel any remaining tasks except the current one
    current_task = asyncio.current_task()
    tasks = [t for t in asyncio.all_tasks(loop) if t != current_task and not t.done()]

    for task in tasks:
        task.cancel()

    # Wait for all tasks to be cancelled
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)


@pytest.fixture
def mock_ai_client():
    """Mock AI client for testing."""
    from unittest.mock import Mock, patch, AsyncMock

    mock_client = Mock()
    mock_response = Mock()
    mock_response.text = "Mock AI response for testing compliance guidance."
    mock_client.generate_content.return_value = mock_response
    mock_client.generate_content_async = AsyncMock(return_value=mock_response)

    with patch("config.ai_config.get_ai_model", return_value=mock_client):
        yield mock_client


@pytest.fixture
def mock_compliance_assistant():
    """Mock ComplianceAssistant for testing."""
    from unittest.mock import Mock, AsyncMock
    from services.ai.assistant import ComplianceAssistant
    from services.ai.circuit_breaker import AICircuitBreaker

    assistant = Mock(spec=ComplianceAssistant)
    assistant.circuit_breaker = Mock(spec=AICircuitBreaker)
    assistant.circuit_breaker.is_model_available.return_value = True
    assistant.circuit_breaker.get_status.return_value = {
        "overall_state": "CLOSED",
        "model_states": {"gemini-2.5-flash": "CLOSED"},
        "metrics": {"success_rate": 0.95},
    }

    # Mock async methods
    assistant.analyze_assessment_results = AsyncMock(
        return_value={"analysis": "Mock analysis", "gaps": [], "recommendations": []}
    )
    assistant.analyze_assessment_results_stream = AsyncMock()
    assistant.get_question_help = AsyncMock(
        return_value={"guidance": "Mock guidance", "confidence_score": 0.9}
    )
    assistant.generate_followup_questions = AsyncMock(return_value={"questions": []})
    assistant.get_personalized_recommendations = AsyncMock(return_value={"recommendations": []})

    return assistant


@pytest_asyncio.fixture
async def async_test_client(db_session, sample_user):
    """Async test client with proper database and auth mocking."""
    from httpx import ASGITransport, AsyncClient
    from api.dependencies.database import get_db, get_async_db
    from api.dependencies.auth import get_current_user, get_current_active_user
    from main import app

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_async_db():
        # For TestClient, return regular generator, not async
        yield AsyncSessionWrapper(db_session)

    def override_get_current_user():
        return sample_user

    def override_get_current_active_user():
        return sample_user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_async_db] = override_get_async_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# =============================================================================
# BACKWARD COMPATIBILITY
# =============================================================================


@pytest.fixture
def sync_db_session(db_session):
    """Alias for compatibility."""
    return db_session


@pytest.fixture
def sync_sample_user(sample_user):
    """Alias for compatibility."""
    return sample_user


@pytest.fixture
def authenticated_test_client(client):
    """Alias for compatibility."""
    return client


@pytest.fixture
def unauthenticated_test_client(unauthenticated_client):
    """Alias for compatibility."""
    return unauthenticated_client


@pytest.fixture
def test_client(client):
    """Alias for compatibility."""
    return client


@pytest.fixture 
def db(db_session):
    """Alias for RBAC tests compatibility."""
    return db_session


# =============================================================================
# TEST UTILITIES
# =============================================================================


def assert_api_response_security(response):
    """Assert API response has proper security headers."""
    # Check for security headers
    assert "X-Content-Type-Options" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    # Additional security checks can be added here


# =============================================================================
# ADDITIONAL TEST FIXTURES
# =============================================================================


@pytest.fixture
async def mock_cache_manager():
    """Mock cache manager for tests."""
    from config.cache import get_cache_manager

    # Get the cache manager and ensure it uses our mock Redis
    cache_manager = await get_cache_manager()

    # The cache manager should now use our MockRedis with async methods
    yield cache_manager

    # Clean up cache data after test
    if cache_manager.redis_client:
        cache_manager.redis_client.data.clear()


@pytest.fixture
def sample_evidence_data():
    """Sample evidence data."""
    return {
        "evidence_name": "Information Security Policy",
        "description": "Comprehensive security policy",
        "evidence_type": "policy_document",
        "raw_data": '{"file_type": "pdf", "content": "Policy content..."}',
    }


@pytest.fixture
def sample_business_context():
    """Sample business context."""
    return {
        "company_name": "Test Corp",
        "industry": "Technology",
        "employee_count": 150,
        "existing_frameworks": ["ISO27001"],
    }


@pytest.fixture
def optimized_cache_config():
    """Cache configuration."""
    from services.ai.cached_content import CacheLifecycleConfig

    return CacheLifecycleConfig(
        default_ttl_hours=2,
        max_ttl_hours=8,
        min_ttl_minutes=15,
        performance_based_ttl=True,
        cache_warming_enabled=True,
        intelligent_invalidation=True,
        fast_response_threshold_ms=200,
        slow_response_threshold_ms=2000,
        ttl_adjustment_factor=0.2,
    )


@pytest.fixture
def compliance_assistant(db_session):
    """Compliance assistant for testing."""
    from services.ai.assistant import ComplianceAssistant

    return ComplianceAssistant(db_session)


@pytest.fixture
def performance_config():
    """Performance test configuration."""
    return {
        "max_response_time": 3.0,  # seconds
        "min_throughput": 10,  # requests per second
        "max_memory_mb": 500,
        "target_success_rate": 0.95,
        "concurrent_users": [1, 5, 10, 20],
        "test_duration": 30,  # seconds
    }


@pytest.fixture
def compliance_golden_dataset():
    """Load compliance test data."""
    return [
        {
            "id": "gdpr_001",
            "framework": "GDPR",
            "difficulty": "basic",
            "question": "What is the maximum fine for GDPR violations?",
            "expected_answer": "The maximum fine for GDPR violations is €20 million or 4% of annual global turnover, whichever is higher.",
            "key_points": [
                "€20 million",
                "4% of annual global turnover",
                "whichever is higher",
            ],
            "category": "penalties",
        },
        {
            "id": "gdpr_002",
            "framework": "GDPR",
            "difficulty": "basic",
            "question": "What is the timeframe for reporting data breaches under GDPR?",
            "expected_answer": "Data breaches must be reported to supervisory authorities within 72 hours of becoming aware of the breach.",
            "key_points": ["72 hours", "supervisory authorities", "becoming aware"],
            "category": "breach_notification",
        },
    ]


@pytest.fixture
def sample_customization_options():
    """Sample policy customization options."""
    return {
        "policy_type": "data_protection",
        "jurisdiction": "UK",
        "industry_specific": True,
        "include_templates": True,
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "company": "Test Corp",
    }
