"""
Pytest configuration and shared fixtures for ComplianceGPT tests.
"""

import os
from cryptography.fernet import Fernet

# Set environment variables for testing BEFORE any application modules are imported.
# This prevents the app from loading production settings during test collection.
os.environ["ENV"] = "testing"
# Use Neon database for testing - keep the original format with sslmode=require
# The db_setup.py will handle the conversion to asyncpg format properly
os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_s0JhnfGNy3Ze@ep-wild-grass-a8o37wq8-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
os.environ["SECRET_KEY"] = "test_secret_key_for_pytest_sessions"
os.environ["GOOGLE_API_KEY"] = "test_google_api_key"
os.environ["SENTRY_DSN"] = ""
os.environ['FERNET_KEY'] = Fernet.generate_key().decode()

import asyncio
import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

# Add project root to the Python path to resolve import errors
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Assuming these are the correct paths from your project structure
import database.db_setup as db_setup
from database.db_setup import get_async_db, Base
from database.user import User
from database.business_profile import BusinessProfile
from database.evidence_item import EvidenceItem
from database.compliance_framework import ComplianceFramework
from database.generated_policy import GeneratedPolicy # Assuming this is the model for policy documents

# Import the Evidence model from database.models to ensure the table is created
from database.models import Evidence

# Import FastAPI test client for API tests
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Fixture to manage database schema (similar to integration tests)
@pytest.fixture(scope="session", autouse=True)
async def manage_test_database_schema_unit(): # Renamed to avoid conflict if integration conftest is ever merged/used
    """Create and drop test database schema for the session for unit tests."""
    # Use the centralized database setup which handles SSL properly
    db_setup._init_async_db()  # This is not async, don't await it

    async with db_setup._async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Use CASCADE to handle foreign key dependencies during teardown
    async with db_setup._async_engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))
    await db_setup._async_engine.dispose()

@pytest.fixture
async def db_session():
    """Create an isolated async test database session for unit tests."""
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    from sqlalchemy.orm import sessionmaker
    import os
    import asyncio

    # Create test-specific async database engine
    test_db_url = os.getenv("DATABASE_URL")
    if "+asyncpg" in test_db_url:
        test_async_url = test_db_url
    else:
        test_async_url = test_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Handle SSL configuration for asyncpg
    async_engine_kwargs = {
        "pool_pre_ping": True,
        "pool_recycle": -1,  # Disable connection recycling for tests
        "pool_timeout": 10,   # Shorter timeout for tests
        "pool_size": 1,       # Minimal pool for tests
        "max_overflow": 0,    # No overflow for tests
        "echo": False,        # Disable SQL echo for cleaner test output
    }
    if "sslmode=require" in test_async_url:
        test_async_url = test_async_url.replace("?sslmode=require", "").replace("&sslmode=require", "")
        async_engine_kwargs["connect_args"] = {"ssl": True}

    # Create isolated test async engine and session
    test_async_engine = create_async_engine(test_async_url, **async_engine_kwargs)
    TestAsyncSessionLocal = sessionmaker(
        bind=test_async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            # Clean up async engine
            try:
                await test_async_engine.dispose()
            except Exception:
                # If disposal fails, ignore it to prevent test failures
                pass

@pytest.fixture
async def sample_user(db_session: AsyncSession) -> User:
    """Create a sample user for tests with unique email."""
    user = User(
        id=uuid4(),
        email=f"sampleuser-{uuid4()}@example.com",
        hashed_password="fake_password_hash" # In real scenarios, hash properly
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def sample_business_profile(db_session: AsyncSession, sample_user: User) -> BusinessProfile:
    """Create a sample business profile for tests."""
    profile_data = {
        "company_name": "Sample Test Corp",
        "industry": "Software Development",
        "employee_count": 75,
        "country": "USA",
        "existing_framew": ["ISO27001", "SOC2"],
        "planned_framewo": [],
        # Required boolean fields
        "handles_persona": True,
        "processes_payme": False,
        "stores_health_d": False,
        "provides_financ": False,
        "operates_critic": False,
        "has_internation": True,
        # Optional fields with defaults
        "cloud_providers": ["AWS", "Azure"],
        "saas_tools": ["Office365", "Salesforce"],
        "development_too": ["GitHub"],
        "compliance_budg": "50000-100000",
        "compliance_time": "6-12 months"
    }
    profile = BusinessProfile(
        id=uuid4(),
        user_id=sample_user.id,
        **profile_data
    )
    db_session.add(profile)
    await db_session.commit()
    await db_session.refresh(profile)
    return profile

@pytest.fixture
async def sample_compliance_framework(db_session: AsyncSession) -> ComplianceFramework:
    """Create a sample compliance framework for tests."""
    # Use a unique name to avoid conflicts across test runs
    unique_name = f"ISO27001-{uuid4().hex[:8]}"
    framework = ComplianceFramework(
        id=uuid4(),
        name=unique_name,
        display_name="ISO/IEC 27001:2022",
        description="Information security management systems",
        category="Information Security"
    )
    db_session.add(framework)
    await db_session.commit()
    await db_session.refresh(framework)
    return framework

@pytest.fixture
async def sample_evidence_item(db_session: AsyncSession, sample_business_profile: BusinessProfile, sample_compliance_framework: ComplianceFramework) -> EvidenceItem:
    """Create a sample evidence item for tests."""
    evidence = EvidenceItem(
        id=uuid4(),
        user_id=sample_business_profile.user_id,
        business_profile_id=sample_business_profile.id,
        framework_id=sample_compliance_framework.id,
        evidence_name="Sample Security Policy",
        evidence_type="policy_document",
        control_reference="A.5.1",  # Required field
        description="A sample security policy document for testing.",
        status="active",
        file_path="/path/to/sample/policy.pdf", # Placeholder
        automation_source="manual",  # Correct field name
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(evidence)
    await db_session.commit()
    await db_session.refresh(evidence)
    return evidence

@pytest.fixture
async def sample_policy_document(db_session: AsyncSession, sample_business_profile: BusinessProfile) -> GeneratedPolicy:
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
        updated_at=datetime.utcnow()
    )
    db_session.add(policy)
    await db_session.commit()
    await db_session.refresh(policy)
    return policy

@pytest.fixture
def client():
    """Create a FastAPI test client for API tests with isolated database."""
    from main import app
    from database.db_setup import get_db, get_async_db
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
    import os
    import asyncio

    # Create test-specific database engines
    test_db_url = os.getenv("DATABASE_URL")
    if "+asyncpg" in test_db_url:
        test_sync_url = test_db_url.replace("+asyncpg", "+psycopg2")
        test_async_url = test_db_url
    else:
        test_sync_url = test_db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
        test_async_url = test_db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # Handle SSL configuration for asyncpg
    async_engine_kwargs = {
        "pool_pre_ping": True,
        "pool_recycle": -1,  # Disable connection recycling for tests
        "pool_timeout": 10,   # Shorter timeout for tests
        "pool_size": 1,       # Minimal pool for tests
        "max_overflow": 0,    # No overflow for tests
        "echo": False,        # Disable SQL echo for cleaner test output
    }
    if "sslmode=require" in test_async_url:
        test_async_url = test_async_url.replace("?sslmode=require", "").replace("&sslmode=require", "")
        async_engine_kwargs["connect_args"] = {"ssl": True}

    # Create isolated test engines and sessions
    test_engine = create_engine(test_sync_url, pool_pre_ping=True, echo=False)
    test_async_engine = create_async_engine(test_async_url, **async_engine_kwargs)

    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    TestAsyncSessionLocal = sessionmaker(
        bind=test_async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    def override_get_db():
        """Override sync database dependency for tests."""
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    async def override_get_async_db():
        """Override async database dependency for tests."""
        async with TestAsyncSessionLocal() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    # Override both database dependencies
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_async_db] = override_get_async_db

    client = TestClient(app)
    yield client

    # Clean up
    app.dependency_overrides.clear()
    test_engine.dispose()

    # Clean up async engine in a new event loop if needed
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is running, schedule cleanup for later
            loop.create_task(test_async_engine.dispose())
        else:
            # If loop is not running, run cleanup directly
            loop.run_until_complete(test_async_engine.dispose())
    except RuntimeError:
        # If no event loop exists, create one for cleanup
        asyncio.run(test_async_engine.dispose())

@pytest.fixture
def sample_assessment_data():
    """Provide sample assessment data for tests."""
    return {
        "business_profile_id": str(uuid4()),
        "framework_id": "ISO27001",
        "responses": [
            {"control_id": "A.5.1", "status": "implemented", "evidence_ids": [str(uuid4())]},
            {"control_id": "A.6.1", "status": "partially_implemented", "notes": "Work in progress"}
        ],
        "overall_notes": "Initial assessment for ISO27001."
    }

@pytest.fixture
def sample_readiness_data():
    """Provide sample readiness data for tests."""
    return {
        "overall_score": 75.5,
        "framework_scores": {"ISO27001": 75.5, "SOC2": 0.0},
        "gaps": [
            {"control_id": "A.6.1.2", "description": "User access reviews not fully implemented.", "priority": "High"},
            {"control_id": "A.12.1.2", "description": "Change management procedures need formalization.", "priority": "Medium"}
        ],
        "risk_level": "Medium",
        "recommendations": ["Implement quarterly user access reviews.", "Formalize change management process."]
    }

@pytest.fixture
def sample_user_data():
    """Provide sample user data for tests with unique email."""
    from uuid import uuid4
    return {
        "email": f"test-{uuid4()}@example.com",
        "password": "SecurePassword123!",
        "full_name": "Test User",
        "is_active": True
    }

@pytest.fixture
async def auth_token(sample_user):
    """Provide a valid auth token for tests."""
    from api.dependencies.auth import create_access_token
    from datetime import timedelta

    # Create a test token for the actual sample user
    token_data = {"sub": str(sample_user.id)}
    token = create_access_token(data=token_data, expires_delta=timedelta(minutes=30))
    return token

@pytest.fixture
def expired_token():
    """Provide an expired auth token for tests."""
    from api.dependencies.auth import create_access_token
    from datetime import timedelta

    # Create an expired token (negative expiry)
    token_data = {"sub": str(uuid4())}
    token = create_access_token(data=token_data, expires_delta=timedelta(minutes=-30))
    return token

@pytest.fixture
async def authenticated_headers(auth_token):
    """Provide authenticated headers for API tests."""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
async def another_authenticated_headers(db_session: AsyncSession):
    """Provide authenticated headers for a different user for testing access control."""
    from api.dependencies.auth import create_access_token
    from datetime import timedelta

    # Create another user in the database
    another_user = User(
        id=uuid4(),
        email=f"anotheruser-{uuid4()}@example.com",
        hashed_password="fake_password_hash"
    )
    db_session.add(another_user)
    await db_session.commit()
    await db_session.refresh(another_user)

    # Create a token for this real user
    token_data = {"sub": str(another_user.id)}
    token = create_access_token(data=token_data, expires_delta=timedelta(minutes=30))
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def evidence_item_instance(sample_evidence_item):
    """Alias for sample_evidence_item to match integration test expectations."""
    return sample_evidence_item

@pytest.fixture
def mock_ai_client():
    """Provide a mock AI client for testing AI-related functionality."""
    from unittest.mock import Mock, AsyncMock, patch

    # Create a mock AI client that mimics Google Generative AI
    mock_client = Mock()

    # Mock the generate_content method
    mock_response = Mock()
    mock_response.text = "This is a mock AI response for compliance guidance. GDPR requires data protection measures including consent management, data minimization, and breach notification within 72 hours."
    mock_client.generate_content.return_value = mock_response

    # Mock the async generate_content_async method
    mock_client.generate_content_async = AsyncMock(return_value=mock_response)

    # Patch the get_ai_model function to return our mock
    with patch('config.ai_config.get_ai_model', return_value=mock_client):
        yield mock_client

@pytest.fixture
def gdpr_golden_dataset():
    """Provide GDPR golden dataset for AI accuracy testing."""
    return [
        {
            "id": "gdpr_001",
            "framework": "GDPR",
            "difficulty": "basic",
            "question": "What is the maximum fine for GDPR violations?",
            "expected_answer": "The maximum fine for GDPR violations is €20 million or 4% of annual global turnover, whichever is higher.",
            "key_points": ["€20 million", "4% of annual global turnover", "whichever is higher"],
            "category": "penalties"
        },
        {
            "id": "gdpr_002",
            "framework": "GDPR",
            "difficulty": "basic",
            "question": "What is the timeframe for reporting data breaches under GDPR?",
            "expected_answer": "Data breaches must be reported to supervisory authorities within 72 hours of becoming aware of the breach.",
            "key_points": ["72 hours", "supervisory authorities", "becoming aware"],
            "category": "breach_notification"
        },
        {
            "id": "gdpr_003",
            "framework": "GDPR",
            "difficulty": "intermediate",
            "question": "What are the lawful bases for processing personal data under GDPR?",
            "expected_answer": "The six lawful bases are: consent, contract, legal obligation, vital interests, public task, and legitimate interests.",
            "key_points": ["consent", "contract", "legal obligation", "vital interests", "public task", "legitimate interests"],
            "category": "lawful_basis"
        }
    ]

@pytest.fixture
def compliance_golden_dataset():
    """Provide comprehensive compliance golden dataset for testing."""
    return [
        {
            "id": "comp_001",
            "framework": "GDPR",
            "question": "What constitutes personal data under GDPR?",
            "expected_answer": "Personal data is any information relating to an identified or identifiable natural person.",
            "key_points": ["identified", "identifiable", "natural person"],
            "category": "definitions"
        },
        {
            "id": "comp_002",
            "framework": "ISO 27001",
            "question": "What is the purpose of ISO 27001?",
            "expected_answer": "ISO 27001 provides requirements for establishing, implementing, maintaining and continually improving an information security management system.",
            "key_points": ["information security management system", "ISMS", "continual improvement"],
            "category": "overview"
        },
        {
            "id": "comp_003",
            "framework": "SOX",
            "question": "What does Section 404 of SOX require?",
            "expected_answer": "Section 404 requires management to assess and report on the effectiveness of internal controls over financial reporting.",
            "key_points": ["internal controls", "financial reporting", "management assessment"],
            "category": "requirements"
        },
        {
            "id": "comp_004",
            "framework": "HIPAA",
            "question": "What is PHI under HIPAA?",
            "expected_answer": "PHI (Protected Health Information) is individually identifiable health information held or transmitted by covered entities.",
            "key_points": ["individually identifiable", "health information", "covered entities"],
            "category": "definitions"
        }
    ]

def assert_api_response_security(response):
    """Placeholder for security assertion on API responses."""
    # A real implementation would check for security headers like CSP, HSTS, etc.
    assert "X-Content-Type-Options" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    pass


def assert_no_sensitive_data_in_logs(log_capture):
    """Placeholder for checking sensitive data in logs."""
    # A real implementation would use more sophisticated pattern matching.
    sensitive_keywords = ["password", "secret", "api_key", "token"]
    for record in log_capture.records:
        log_message = record.getMessage().lower()
        for keyword in sensitive_keywords:
            assert keyword not in log_message, f"Sensitive keyword '{keyword}' found in logs."
    pass
