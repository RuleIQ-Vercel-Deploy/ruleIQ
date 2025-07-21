"""
Improved pytest configuration with robust async database handling.
This replaces the problematic patterns in conftest.py with stable solutions.
"""

import asyncio
import os
import warnings
import logging
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
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
    "postgresql://neondb_owner:npg_s0JhnfGNy3Ze@ep-wild-grass-a8o37wq8-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
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
from database.compliance_framework import ComplianceFramework
from database.evidence_item import EvidenceItem


class DatabaseTestManager:
    """Manages database connections and cleanup for tests."""

    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._connection_count = 0
        self._max_connections = 10

    @asynccontextmanager
    async def get_engine(self) -> AsyncEngine:
        """Get or create async engine with connection limits."""
        if self._engine is None:
            from sqlalchemy.ext.asyncio import create_async_engine

            # Get database URLs
            db_url, sync_url, async_url = _get_configured_database_urls()

            # Convert SSL configuration for asyncpg
            if "sslmode=require" in async_url:
                async_url = async_url.replace("sslmode=require", "")
                ssl_config = {"ssl": "require"}
            else:
                ssl_config = {}

            # Create engine with connection pooling limits
            self._engine = create_async_engine(
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

        try:
            yield self._engine
        finally:
            # Don't dispose here - let session manager handle it
            pass

    async def create_tables(self):
        """Create database tables for tests."""
        async with self.get_engine() as engine:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self):
        """Drop database tables after tests."""
        if self._engine is None:
            return

        try:
            async with self._engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
        except Exception:
            # Fallback to schema recreation if table drops fail
            try:
                async with self._engine.begin() as conn:
                    await conn.execute(text("DROP SCHEMA public CASCADE"))
                    await conn.execute(text("CREATE SCHEMA public"))
            except Exception as schema_error:
                print(f"Warning: Schema cleanup failed: {schema_error}")

    async def dispose(self):
        """Dispose of the database engine."""
        if self._engine is not None:
            try:
                await self._engine.dispose()
            except Exception as e:
                print(f"Warning: Engine disposal failed: {e}")
            finally:
                self._engine = None


# Global database manager
_db_manager = DatabaseTestManager()


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
    await _db_manager.create_tables()

    yield

    # Clean up
    await _db_manager.drop_tables()
    await _db_manager.dispose()


@pytest.fixture
async def async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide async database session with proper cleanup."""
    async with _db_manager.get_engine() as engine:
        async with AsyncSession(engine, expire_on_commit=False) as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()


@pytest.fixture
async def sample_user(async_db_session: AsyncSession) -> User:
    """Create a sample user for tests."""
    user = User(
        id=uuid4(), email="test@example.com", hashed_password="fake_password_hash", is_active=True
    )
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    return user


@pytest.fixture
async def sample_business_profile(
    async_db_session: AsyncSession, sample_user: User
) -> BusinessProfile:
    """Create a sample business profile for tests."""
    profile = BusinessProfile(
        id=uuid4(),
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
    async_db_session.add(profile)
    await async_db_session.commit()
    await async_db_session.refresh(profile)
    return profile


@pytest.fixture
async def sample_compliance_framework(async_db_session: AsyncSession) -> ComplianceFramework:
    """Create a sample compliance framework for tests."""
    framework = ComplianceFramework(
        id=uuid4(),
        name=f"ISO27001-{uuid4().hex[:8]}",
        display_name="ISO/IEC 27001:2022",
        description="Information security management systems",
        category="Information Security",
    )
    async_db_session.add(framework)
    await async_db_session.commit()
    await async_db_session.refresh(framework)
    return framework


@pytest.fixture
async def sample_evidence_item(
    async_db_session: AsyncSession,
    sample_user: User,
    sample_business_profile: BusinessProfile,
    sample_compliance_framework: ComplianceFramework,
) -> EvidenceItem:
    """Create a sample evidence item for tests."""
    evidence = EvidenceItem(
        id=uuid4(),
        user_id=sample_user.id,
        business_profile_id=sample_business_profile.id,
        framework_id=sample_compliance_framework.id,
        evidence_name="Sample Security Policy",
        evidence_type="policy_document",
        control_reference="A.5.1",
        description="A sample security policy document for testing.",
        status="active",
        file_path="/path/to/sample/policy.pdf",
        automation_source="manual",
        created_at=pytest.datetime.utcnow() if hasattr(pytest, "datetime") else None,
        updated_at=pytest.datetime.utcnow() if hasattr(pytest, "datetime") else None,
    )
    async_db_session.add(evidence)
    await async_db_session.commit()
    await async_db_session.refresh(evidence)
    return evidence


# Authentication fixtures with proper async handling
@pytest.fixture
def auth_token(sample_user: User) -> str:
    """Generate authentication token for tests."""
    from datetime import timedelta
    from api.dependencies.auth import create_access_token

    token_data = {"sub": str(sample_user.id)}
    return create_access_token(data=token_data, expires_delta=timedelta(minutes=30))


@pytest.fixture
def authenticated_headers(auth_token: str) -> dict:
    """Provide authenticated headers for API tests."""
    return {"Authorization": f"Bearer {auth_token}"}


# API client fixture with proper dependency overrides
@pytest.fixture
def client() -> TestClient:
    """Create FastAPI test client with database overrides."""
    from main import app
    from api.dependencies.auth import get_current_active_user, get_current_user
    from database.db_setup import get_async_db
    from database.user import User
    from uuid import uuid4

    # Create a test user that will be returned by all auth overrides
    test_user = User(
        id=uuid4(), email="test@example.com", hashed_password="fake_password_hash", is_active=True
    )

    # Use the existing database manager from this file
    async def override_get_async_db():
        async with _db_manager.get_engine() as engine:
            async with AsyncSession(engine, expire_on_commit=False) as session:
                try:
                    yield session
                except Exception:
                    await session.rollback()
                    raise
                finally:
                    await session.close()

    # Simple auth overrides that always return the test user
    def override_get_current_user():
        return test_user

    def override_get_current_active_user():
        return test_user

    # Store original overrides
    original_overrides = app.dependency_overrides.copy()

    # Set up dependency overrides
    app.dependency_overrides[get_async_db] = override_get_async_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    client = TestClient(app)
    yield client

    # Restore original overrides
    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)
