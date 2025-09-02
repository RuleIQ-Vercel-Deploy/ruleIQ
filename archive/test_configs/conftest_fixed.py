"""
Unified pytest configuration for ruleIQ tests - Fixed version.
Consolidates all conftest files to eliminate fixture conflicts and ensure 100% test pass rate.
"""

import asyncio
import json
import os
import warnings
import logging
from uuid import uuid4
from datetime import datetime, timedelta

import pytest
import pytest_asyncio
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from fastapi.testclient import TestClient

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================

# Suppress warnings early
warnings.filterwarnings("ignore", message=".*bcrypt.*", category=UserWarning)
warnings.filterwarnings("ignore", message=".*bcrypt.*", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*bcrypt.*", category=RuntimeWarning)
warnings.filterwarnings("ignore", message=".*Event loop is closed.*", category=RuntimeWarning)
warnings.filterwarnings(
    "ignore", message=".*attached to a different loop.*", category=RuntimeWarning
)
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)

# Set test environment variables
os.environ["ENV"] = "testing"
os.environ["DATABASE_URL"] = (
    "postgresql://neondb_owner:npg_s0JhnfGNy3Ze@ep-wild-grass-a8o37wq8-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
)
os.environ["SECRET_KEY"] = "test_secret_key_for_pytest_sessions"
os.environ["GOOGLE_API_KEY"] = "test_key_for_mocking"
os.environ["SENTRY_DSN"] = ""
os.environ["USE_MOCK_AI"] = "true"

# Generate Fernet key for encryption
from cryptography.fernet import Fernet

os.environ["FERNET_KEY"] = Fernet.generate_key().decode()

# =============================================================================
# COMPREHENSIVE AI MOCKING SETUP
# =============================================================================

import sys
import unittest.mock

# Mock the entire google.generativeai module
mock_genai = unittest.mock.MagicMock()

# Mock model response
mock_response = unittest.mock.MagicMock()
mock_response.text = "Mock AI response for testing compliance guidance"
mock_response.parts = [unittest.mock.MagicMock()]
mock_response.parts[0].text = "Mock AI response for testing compliance guidance"
mock_response.candidates = []

# Mock model
mock_model = unittest.mock.MagicMock()
mock_model.generate_content.return_value = mock_response
mock_model.model_name = "gemini-2.5-flash"


# Mock streaming response
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

# Mock types
mock_types = unittest.mock.MagicMock()
mock_types.HarmBlockThreshold = unittest.mock.MagicMock()
mock_types.HarmCategory = unittest.mock.MagicMock()

# Set up genai module mock
mock_genai.GenerativeModel.return_value = mock_model
mock_genai.configure.return_value = None
mock_genai.types = mock_types

# Apply mocks to all relevant modules
sys.modules["google"] = unittest.mock.MagicMock()
sys.modules["google.generativeai"] = mock_genai
sys.modules["google.generativeai.caching"] = mock_genai.caching
sys.modules["google.generativeai.types"] = mock_types

# =============================================================================
# PROJECT IMPORTS
# =============================================================================

# Add project root to path
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import database components
from database.user import User
from database.business_profile import BusinessProfile
from database.compliance_framework import ComplianceFramework
from database.evidence_item import EvidenceItem
from database.generated_policy import GeneratedPolicy

# Import all models to ensure they're registered with Base

# =============================================================================
# EVENT LOOP CONFIGURATION - CRITICAL FOR FIXING ASYNC ISSUES
# =============================================================================

# Use the new event_loop_policy fixture from pytest-asyncio
pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session")
def event_loop_policy():
    """Set event loop policy for the test session."""
    return asyncio.get_event_loop_policy()


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for entire test session."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


# =============================================================================
# DATABASE URL MANAGEMENT
# =============================================================================


def get_test_database_url():
    """Get test database URLs."""
    db_url = os.environ["DATABASE_URL"]

    # Sync URL
    sync_url = db_url
    if "+asyncpg" in sync_url:
        sync_url = sync_url.replace("+asyncpg", "+psycopg2")
    elif "postgresql://" in sync_url and "+psycopg2" not in sync_url:
        sync_url = sync_url.replace("postgresql://", "postgresql+psycopg2://", 1)

    # Async URL
    async_url = db_url
    if "+asyncpg" not in async_url:
        if "+psycopg2" in async_url:
            async_url = async_url.replace("+psycopg2", "+asyncpg")
        elif "postgresql://" in async_url:
            async_url = async_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    return sync_url, async_url


# =============================================================================
# DATABASE ENGINE FIXTURES
# =============================================================================


@pytest.fixture(scope="session")
def sync_engine():
    """Create sync database engine for the test session."""
    sync_url, _ = get_test_database_url()

    engine = create_engine(
        sync_url,
        poolclass=NullPool,
        echo=False,
        future=True,
        connect_args={
            "connect_timeout": 30,
            "options": "-c default_transaction_isolation='read committed'",
        },
    )

    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def async_engine():
    """Create async database engine for the test session."""
    _, async_url = get_test_database_url()

    # Handle SSL
    if "sslmode=require" in async_url:
        async_url = async_url.replace("?sslmode=require", "").replace("&sslmode=require", "")
        ssl_config = {"ssl": "require"}
    else:
        ssl_config = {}

    engine = create_async_engine(
        async_url,
        poolclass=NullPool,
        echo=False,
        future=True,
        connect_args={
            "server_settings": {
                "jit": "off",
                "statement_timeout": "30s",
            },
            "timeout": 30,
            **ssl_config,
        },
    )

    yield engine

    # Dispose is handled in event loop context
    asyncio.get_event_loop().run_until_complete(engine.dispose())


# =============================================================================
# DATABASE SETUP AND TEARDOWN
# =============================================================================


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database(async_engine):
    """Set up database for test session."""
    # Note: We assume tables are already created by setup_test_database.py
    # This fixture just initializes frameworks if needed

    try:
        # Check if frameworks exist
        async with AsyncSession(async_engine, expire_on_commit=False) as session:
            result = await session.execute(text("SELECT COUNT(*) FROM compliance_frameworks"))
            count = result.scalar()

            if count == 0:
                from services.framework_service import initialize_default_frameworks

                await initialize_default_frameworks(session)
                print("Default frameworks initialized in test session")
    except Exception as e:
        print(f"Warning: Framework initialization check failed: {e}")

    yield

    # Cleanup is optional since we're using a shared test database


# =============================================================================
# SYNC DATABASE FIXTURES
# =============================================================================


@pytest.fixture
def db_session(sync_engine):
    """Sync database session for tests."""
    SessionLocal = sessionmaker(
        bind=sync_engine, autocommit=False, autoflush=False, expire_on_commit=False
    )

    session = SessionLocal()

    # Start a transaction that will be rolled back
    session.begin()

    yield session

    # Rollback the transaction
    session.rollback()
    session.close()


@pytest.fixture
def sync_db_session(db_session):
    """Alias for db_session."""
    return db_session


# =============================================================================
# ASYNC DATABASE FIXTURES
# =============================================================================


@pytest_asyncio.fixture
async def async_db_session(async_engine):
    """Async database session for tests."""
    async_session_maker = async_sessionmaker(
        bind=async_engine,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    async with async_session_maker() as session:
        async with session.begin():
            yield session
            # Transaction will be rolled back automatically


# =============================================================================
# USER FIXTURES
# =============================================================================


@pytest.fixture
def sample_user(db_session):
    """Create a sample user for sync tests."""
    user = User(
        id=uuid4(),
        email=f"test_{uuid4().hex[:8]}@example.com",
        hashed_password="fake_password_hash",
        is_active=True,
    )
    db_session.add(user)
    db_session.flush()  # Use flush instead of commit in transaction
    return user


@pytest_asyncio.fixture
async def async_sample_user(async_db_session):
    """Create a sample user for async tests."""
    user = User(
        id=uuid4(),
        email=f"test_{uuid4().hex[:8]}@example.com",
        hashed_password="fake_password_hash",
        is_active=True,
    )
    async_db_session.add(user)
    await async_db_session.flush()
    return user


# =============================================================================
# BUSINESS PROFILE FIXTURES
# =============================================================================


@pytest.fixture
def sample_business_profile(db_session, sample_user):
    """Create a sample business profile for sync tests."""
    profile = BusinessProfile(
        id=uuid4(),
        user_id=sample_user.id,
        company_name=f"Test Company {uuid4().hex[:8]}",
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
    db_session.flush()
    return profile


@pytest_asyncio.fixture
async def async_sample_business_profile(async_db_session, async_sample_user):
    """Create a sample business profile for async tests."""
    profile = BusinessProfile(
        id=uuid4(),
        user_id=async_sample_user.id,
        company_name=f"Test Company {uuid4().hex[:8]}",
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
    async_db_session.add(profile)
    await async_db_session.flush()
    return profile


# =============================================================================
# AUTHENTICATION FIXTURES
# =============================================================================


@pytest.fixture
def auth_token(sample_user):
    """Generate authentication token for tests."""
    from api.dependencies.auth import create_access_token

    token_data = {"sub": str(sample_user.id)}
    return create_access_token(data=token_data, expires_delta=timedelta(minutes=30))


@pytest.fixture
def authenticated_headers(auth_token):
    """Provide authenticated headers for API tests."""
    return {"Authorization": f"Bearer {auth_token}"}


# =============================================================================
# TEST CLIENT FIXTURES
# =============================================================================


@pytest.fixture
def client(db_session, sample_user):
    """Authenticated test client with database overrides."""
    from main import app
    from api.dependencies.auth import get_current_active_user, get_current_user
    from database.db_setup import get_async_db, get_db

    # Override dependencies
    def override_get_db():
        yield db_session

    async def override_get_async_db():
        yield db_session  # Use sync session for TestClient

    def override_get_current_user():
        return sample_user

    def override_get_current_active_user():
        return sample_user

    # Apply overrides
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
    """Unauthenticated test client with database overrides."""
    from main import app
    from database.db_setup import get_async_db, get_db

    # Override database dependencies only
    def override_get_db():
        yield db_session

    async def override_get_async_db():
        yield db_session  # Use sync session for TestClient

    # Apply overrides
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_async_db] = override_get_async_db

    with TestClient(app) as test_client:
        yield test_client

    # Clear overrides
    app.dependency_overrides.clear()


# =============================================================================
# ADDITIONAL DOMAIN FIXTURES
# =============================================================================


@pytest.fixture
def sample_compliance_framework(db_session):
    """Create a sample compliance framework for tests."""
    framework = ComplianceFramework(
        id=uuid4(),
        name=f"TEST-FRAMEWORK-{uuid4().hex[:8]}",
        display_name="Test Framework",
        description="Test framework for unit tests",
        category="Testing",
    )
    db_session.add(framework)
    db_session.flush()
    return framework


@pytest.fixture
def sample_evidence_item(db_session, sample_business_profile, sample_compliance_framework):
    """Create a sample evidence item for tests."""
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
    db_session.flush()
    return evidence


@pytest.fixture
def sample_policy_document(db_session, sample_business_profile):
    """Create a sample policy document for tests."""
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
    db_session.flush()
    return policy


# =============================================================================
# AI MOCKING FIXTURES
# =============================================================================


@pytest.fixture(autouse=True)
def ensure_ai_mocking():
    """Ensure all tests use mocked AI instead of real API calls."""
    return mock_model


@pytest.fixture
def mock_ai_client():
    """Provide a mock AI client for testing AI-related functionality."""
    from unittest.mock import Mock, patch, AsyncMock

    mock_client = Mock()

    mock_response = Mock()
    mock_response.text = "Mock AI response for testing compliance guidance. GDPR requires data protection measures including consent management, data minimization, and breach notification within 72 hours."
    mock_client.generate_content.return_value = mock_response
    mock_client.generate_content_async = AsyncMock(return_value=mock_response)

    with patch("config.ai_config.get_ai_model", return_value=mock_client):
        yield mock_client


# =============================================================================
# TEST DATA FIXTURES
# =============================================================================


@pytest.fixture
def sample_business_profile_data():
    """Sample business profile data for testing."""
    return {
        "company_name": f"Test Company {uuid4().hex[:8]}",
        "industry": "Technology",
        "employee_count": 50,
        "country": "USA",
        "handles_personal_data": True,
        "processes_payments": False,
        "stores_health_data": False,
        "provides_financial_services": False,
        "operates_critical_infrastructure": False,
        "has_international_operations": True,
        "existing_frameworks": ["ISO27001", "SOC2"],
        "planned_frameworks": [],
        "cloud_providers": ["AWS", "Azure"],
        "saas_tools": ["Office365", "Salesforce"],
        "development_tools": ["GitHub"],
        "compliance_budget": "50000-100000",
        "compliance_timeline": "6-12 months",
    }


@pytest.fixture
def compliance_golden_dataset():
    """Load comprehensive compliance questions from golden dataset JSON files."""
    dataset_path = Path(__file__).parent / "ai" / "golden_datasets" / "gdpr_questions.json"

    if dataset_path.exists():
        with open(dataset_path, "r") as f:
            return json.load(f)
    else:
        # Fallback mock data
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
            }
        ]


# =============================================================================
# BACKWARD COMPATIBILITY ALIASES
# =============================================================================


@pytest.fixture
def authenticated_test_client(client):
    """Alias for backward compatibility."""
    return client


@pytest.fixture
def unauthenticated_test_client(unauthenticated_client):
    """Alias for backward compatibility."""
    return unauthenticated_client


@pytest.fixture
def test_client(client):
    """Alias for backward compatibility."""
    return client
