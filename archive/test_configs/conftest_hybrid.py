"""
Hybrid pytest configuration supporting both sync and async database operations.
This solves the FastAPI TestClient + async database event loop conflicts.
"""

import asyncio
import os
import warnings
import logging
from typing import AsyncGenerator, Dict
from uuid import uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

# Suppress warnings early
warnings.filterwarnings("ignore", message=".*bcrypt.*", category=UserWarning)
warnings.filterwarnings("ignore", message=".*bcrypt.*", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*bcrypt.*", category=RuntimeWarning)
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)

# Set test environment variables
os.environ["ENV"] = "testing"
os.environ["DATABASE_URL"] = (
    os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/compliance_test?sslmode=require")
)
os.environ["SECRET_KEY"] = "test_secret_key_for_pytest_sessions"
os.environ["GOOGLE_API_KEY"] = "test_key_for_mocking"
os.environ["SENTRY_DSN"] = ""
os.environ["USE_MOCK_AI"] = "true"

# Generate Fernet key for encryption
from cryptography.fernet import Fernet

os.environ["FERNET_KEY"] = Fernet.generate_key().decode()

# Import after environment setup
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import database components
from database.db_setup import Base, _get_configured_database_urls
from database.user import User
from database.business_profile import BusinessProfile


class HybridDatabaseManager:
    """Manages both sync and async database connections for testing."""

    def __init__(self) -> None:
        self._sync_engine = None
        self._async_engine = None
        self._initialized = False

    def _initialize_engines(self) -> None:
        """Initialize both sync and async engines."""
        if self._initialized:
            return

        # Get database URLs
        db_url, sync_url, async_url = _get_configured_database_urls()

        # Create sync engine for TestClient tests
        self._sync_engine = create_engine(
            sync_url,
            poolclass=StaticPool,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False,
            connect_args={
                "connect_timeout": 30,
            },
        )

        # Create async engine for pure async tests
        # Handle SSL configuration for asyncpg
        if "sslmode=require" in async_url:
            async_url = async_url.replace("sslmode=require", "")
            ssl_config = {"ssl": "require"}
        else:
            ssl_config = {}

        self._async_engine = create_async_engine(
            async_url,
            poolclass=StaticPool,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False,
            future=True,
            connect_args={
                "server_settings": {
                    "jit": "off",
                    "statement_timeout": "30s",
                },
                **ssl_config,
            },
        )

        self._initialized = True

    def get_sync_engine(self):
        """Get sync engine for TestClient tests."""
        self._initialize_engines()
        return self._sync_engine

    def get_async_engine(self):
        """Get async engine for pure async tests."""
        self._initialize_engines()
        return self._async_engine

    def create_sync_session(self) -> sessionmaker:
        """Create sync session factory."""
        engine = self.get_sync_engine()
        return sessionmaker(autocommit=False, autoflush=False, bind=engine)

    async def create_tables(self) -> None:
        """Create database tables for tests."""
        # Create tables using async engine
        async_engine = self.get_async_engine()
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self) -> None:
        """Drop database tables after tests."""
        if not self._initialized:
            return

        try:
            async_engine = self.get_async_engine()
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
        except Exception as e:
            print(f"Warning: Table cleanup failed: {e}")

    async def dispose(self) -> None:
        """Dispose of database engines."""
        if self._sync_engine:
            self._sync_engine.dispose()
        if self._async_engine:
            await self._async_engine.dispose()
        self._initialized = False


# Global database manager
_hybrid_db_manager = HybridDatabaseManager()


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for entire test session."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Set up database for test session with proper cleanup."""
    # Create tables
    await _hybrid_db_manager.create_tables()

    yield

    # Clean up
    await _hybrid_db_manager.drop_tables()
    await _hybrid_db_manager.dispose()


# SYNC FIXTURES (for TestClient tests)
@pytest.fixture
def sync_db_session():
    """Sync database session for TestClient tests."""
    SessionLocal = _hybrid_db_manager.create_sync_session()
    session = SessionLocal()

    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@pytest.fixture
def sync_db_session_isolated():
    """Isolated sync database session for TestClient tests (new session each time)."""
    SessionLocal = _hybrid_db_manager.create_sync_session()
    session = SessionLocal()

    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@pytest.fixture
def sync_sample_user(sync_db_session):
    """Create a sample user for sync tests."""
    # Use a fixed UUID for consistency across tests
    from uuid import UUID

    fixed_user_id = UUID("12345678-1234-5678-9012-123456789012")

    user = User(
        id=fixed_user_id,
        email="test@example.com",
        hashed_password="fake_password_hash",
        is_active=True,
    )
    sync_db_session.add(user)
    sync_db_session.commit()
    sync_db_session.refresh(user)
    return user


@pytest.fixture(scope="session")
def sync_sample_business_profile_session():
    """Create a sample business profile for sync tests (session scope)."""
    # Use a fixed UUID for the business profile for consistency
    from uuid import UUID

    fixed_profile_id = UUID("87654321-4321-8765-4321-876543218765")
    fixed_user_id = UUID("12345678-1234-5678-9012-123456789012")

    return {
        "id": fixed_profile_id,
        "user_id": fixed_user_id,
        "company_name": "Test Company",
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
def sync_sample_business_profile(
    sync_db_session, sync_sample_user, sync_sample_business_profile_session
):
    """Create a sample business profile for sync tests."""
    from database.business_profile import BusinessProfile

    # Check if profile already exists
    existing_profile = (
        sync_db_session.query(BusinessProfile)
        .filter(BusinessProfile.id == sync_sample_business_profile_session["id"])
        .first()
    )

    if existing_profile:
        return existing_profile

    # Create new profile
    profile = BusinessProfile(**sync_sample_business_profile_session)
    sync_db_session.add(profile)
    sync_db_session.commit()
    sync_db_session.refresh(profile)

    # Ensure the profile is actually in the database
    check_profile = (
        sync_db_session.query(BusinessProfile)
        .filter(BusinessProfile.id == profile.id)
        .first()
    )
    assert (
        check_profile is not None
    ), f"Business profile {profile.id} not found in database"

    return profile


# ASYNC FIXTURES (for pure async tests)
@pytest.fixture
async def async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Async database session for pure async tests."""
    async_engine = _hybrid_db_manager.get_async_engine()
    async with AsyncSession(async_engine, expire_on_commit=False) as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture
async def async_sample_user(async_db_session: AsyncSession) -> User:
    """Create a sample user for async tests."""
    user = User(
        id=uuid4(),
        email="test@example.com",
        hashed_password="fake_password_hash",
        is_active=True,
    )
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    return user


@pytest.fixture
async def async_sample_business_profile(
    async_db_session: AsyncSession, async_sample_user: User
) -> BusinessProfile:
    """Create a sample business profile for async tests."""
    profile = BusinessProfile(
        id=uuid4(),
        user_id=async_sample_user.id,
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
    async_db_session.add(profile)
    await async_db_session.commit()
    await async_db_session.refresh(profile)
    return profile


# TESTCLIENT FIXTURES (uses sync database)
@pytest.fixture
def authenticated_test_client(sync_db_session, sync_sample_user):
    """Create FastAPI test client with sync database AND authentication overrides."""
    from main import app
    from api.dependencies.auth import get_current_active_user, get_current_user
    from database.db_setup import get_async_db, get_db

    # Use the same user as the sample user to ensure consistency
    test_user = sync_sample_user

    # Override database dependencies
    def override_get_db():
        try:
            yield sync_db_session
        finally:
            pass  # Session managed by fixture

    async def override_get_async_db():
        # For TestClient, we need to provide a sync session even for async endpoints
        # This is a workaround for the event loop issue
        # Create a mock async session that wraps the sync session
        class SyncSessionWrapper:
            def __init__(self, sync_session) -> None:
                self.sync_session = sync_session

            async def execute(self, statement):
                # Mock async execute by returning the sync result
                class MockAsyncResult:
                    def __init__(self, sync_result) -> None:
                        self.sync_result = sync_result

                    def scalars(self):
                        class MockScalars:
                            def __init__(self, sync_scalars) -> None:
                                self.sync_scalars = sync_scalars

                            def first(self):
                                return self.sync_scalars.first()

                            def all(self):
                                return self.sync_scalars.all()

                        return MockScalars(self.sync_result.scalars())

                result = self.sync_session.execute(statement)
                return MockAsyncResult(result)

            def add(self, instance):
                return self.sync_session.add(instance)

            async def commit(self):
                return self.sync_session.commit()

            async def refresh(self, instance):
                return self.sync_session.refresh(instance)

            async def rollback(self):
                return self.sync_session.rollback()

            async def close(self):
                return self.sync_session.close()

        wrapper = SyncSessionWrapper(sync_db_session)
        try:
            yield wrapper
        finally:
            pass  # Session managed by fixture

    # Override auth dependencies
    def override_get_current_user():
        return test_user

    def override_get_current_active_user():
        return test_user

    # Store original overrides to restore later
    original_overrides = app.dependency_overrides.copy()

    try:
        # Set up dependency overrides
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_async_db] = override_get_async_db
        app.dependency_overrides[get_current_user] = override_get_current_user
        app.dependency_overrides[get_current_active_user] = (
            override_get_current_active_user
        )

        client = TestClient(app)
        yield client
    finally:
        # Ensure overrides are always restored
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


@pytest.fixture
def unauthenticated_test_client(sync_db_session):
    """Create FastAPI test client with sync database but NO authentication overrides."""
    from main import app
    from database.db_setup import get_async_db, get_db

    # Override database dependencies only
    def override_get_db():
        try:
            yield sync_db_session
        finally:
            pass  # Session managed by fixture

    async def override_get_async_db():
        # For TestClient, we need to provide a sync session even for async endpoints
        # This is a workaround for the event loop issue
        # Create a mock async session that wraps the sync session
        class SyncSessionWrapper:
            def __init__(self, sync_session) -> None:
                self.sync_session = sync_session

            async def execute(self, statement):
                # Mock async execute by returning the sync result
                class MockAsyncResult:
                    def __init__(self, sync_result) -> None:
                        self.sync_result = sync_result

                    def scalars(self):
                        class MockScalars:
                            def __init__(self, sync_scalars) -> None:
                                self.sync_scalars = sync_scalars

                            def first(self):
                                return self.sync_scalars.first()

                            def all(self):
                                return self.sync_scalars.all()

                        return MockScalars(self.sync_result.scalars())

                result = self.sync_session.execute(statement)
                return MockAsyncResult(result)

            def add(self, instance):
                return self.sync_session.add(instance)

            async def commit(self):
                return self.sync_session.commit()

            async def refresh(self, instance):
                return self.sync_session.refresh(instance)

            async def rollback(self):
                return self.sync_session.rollback()

            async def close(self):
                return self.sync_session.close()

        wrapper = SyncSessionWrapper(sync_db_session)
        try:
            yield wrapper
        finally:
            pass  # Session managed by fixture

    # Store original overrides to restore later
    original_overrides = app.dependency_overrides.copy()

    try:
        # Set up database overrides only (no auth overrides)
        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_async_db] = override_get_async_db

        client = TestClient(app)
        yield client
    finally:
        # Ensure overrides are always restored
        app.dependency_overrides.clear()
        app.dependency_overrides.update(original_overrides)


# Default test_client fixture uses authenticated client
@pytest.fixture
def test_client(authenticated_test_client):
    """Default test client with authentication (for backward compatibility)."""
    return authenticated_test_client


# AUTHENTICATION FIXTURES
@pytest.fixture
def auth_token(sync_sample_user: User) -> str:
    """Generate authentication token for tests."""
    from datetime import timedelta
    from api.dependencies.auth import create_access_token

    token_data = {"sub": str(sync_sample_user.id)}
    return create_access_token(data=token_data, expires_delta=timedelta(minutes=30))


@pytest.fixture
def authenticated_headers(auth_token: str) -> Dict[str, str]:
    """Provide authenticated headers for API tests."""
    return {"Authorization": f"Bearer {auth_token}"}


# COMPATIBILITY FIXTURES (for backward compatibility)
@pytest.fixture
def client(authenticated_test_client):
    """Alias for authenticated_test_client for backward compatibility."""
    return authenticated_test_client


@pytest.fixture
def sample_user(sync_sample_user):
    """Alias for sync_sample_user for backward compatibility."""
    return sync_sample_user


@pytest.fixture
def sample_business_profile(sync_sample_business_profile):
    """Alias for sync_sample_business_profile for backward compatibility."""
    return sync_sample_business_profile


# MOCK AI FIXTURES
@pytest.fixture(autouse=True)
def mock_ai_services():
    """Mock AI services to prevent external API calls."""
    import unittest.mock

    # Mock Google Generative AI
    mock_genai = unittest.mock.MagicMock()
    mock_response = unittest.mock.MagicMock()
    mock_response.text = "Mock AI response for testing"
    mock_response.parts = [unittest.mock.MagicMock()]
    mock_response.parts[0].text = "Mock AI response for testing"

    mock_model = unittest.mock.MagicMock()
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model

    # Apply mocks
    import sys

    sys.modules["google.generativeai"] = mock_genai
    sys.modules["google.generativeai.types"] = unittest.mock.MagicMock()

    return mock_genai
