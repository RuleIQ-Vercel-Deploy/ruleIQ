"""
from __future__ import annotations

Pytest configuration and fixtures for the test suite.
"""

# Setup test environment before anything else
from tests.setup_test_env import setup_test_database_urls
setup_test_database_urls()

import os
import pytest
import asyncio
from typing import Generator, Optional
from unittest.mock import MagicMock
import psycopg
from psycopg.rows import dict_row
from langgraph.checkpoint.postgres import PostgresSaver
from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

# Import and activate the service proxy BEFORE any tests run
from tests.mock_service_proxy import setup_test_services
setup_test_services()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_llm():
    """Provide a mock LLM for testing without API calls."""
    mock = MagicMock()
    mock.invoke.return_value = MagicMock(content="Mock response")
    mock.ainvoke.return_value = MagicMock(content="Mock async response")
    return mock

@pytest.fixture
def mock_ai_client():
    """Provide a mock AI client for testing without API calls."""
    from utils.test_helpers import create_smart_mock_ai_client
    return create_smart_mock_ai_client()


@pytest.fixture
def mock_openai_client():
    """Provide a mock OpenAI client for testing."""
    from utils.test_helpers import create_smart_mock_openai
    return create_smart_mock_openai()


@pytest.fixture
def mock_anthropic_client():
    """Provide a mock Anthropic client for testing."""
    mock = MagicMock()
    mock.messages.create = MagicMock()
    mock.messages.create.return_value = MagicMock(
        content=[MagicMock(text="Mock Anthropic response")],
    )
    return mock


@pytest.fixture
def mock_redis_client():
    """Provide a mock Redis client for testing."""
    from utils.test_helpers import get_redis_config
    mock = MagicMock()
    mock.get.return_value = None
    mock.set.return_value = True
    mock.delete.return_value = 1
    mock.exists.return_value = False
    mock.expire.return_value = True
    mock.ttl.return_value = -1
    mock.ping.return_value = True
    # Use environment-aware config
    config = get_redis_config()
    mock._config = config
    return mock


@pytest.fixture
def mock_neo4j_session():
    """Provide a mock Neo4j session for testing."""
    mock = MagicMock()
    mock.run.return_value = MagicMock(data=MagicMock(return_value=[]))
    mock.close = MagicMock()
    return mock


@pytest.fixture
def postgres_test_url():
    """Get PostgreSQL test connection URL."""
    # Priority order:
    # 1. TEST_DATABASE_URL environment variable
    # 2. DATABASE_URL environment variable (for CI/CD)
    # 3. Default local test database
    return os.getenv(
        "TEST_DATABASE_URL",
        os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5433/compliance_test",
        ),
    )


@pytest.fixture
def postgres_checkpointer(postgres_test_url):
    """
    Create a PostgreSQL checkpointer for LangGraph state persistence.

    This fixture handles:
    - Connection setup with proper parameters
    - Table creation if needed
    - Cleanup after tests
    """
    # Skip if no PostgreSQL is available
    if not os.getenv("DATABASE_URL") and not os.getenv("TEST_DATABASE_URL"):
        pytest.skip("PostgreSQL test database not configured")

    try:
        # Create connection with proper settings for PostgresSaver
        conn = psycopg.connect(
            postgres_test_url,
            autocommit=True,  # Required for PostgresSaver
            row_factory=dict_row,  # Required for PostgresSaver,
        )

        # Create checkpointer
        checkpointer = PostgresSaver(conn)

        # Setup tables (idempotent - won't error if tables exist)
        checkpointer.setup()

        yield checkpointer

        # Cleanup: Close connection
        conn.close()

    except Exception as e:
        pytest.skip(f"PostgreSQL connection failed: {e}")


@pytest.fixture
def postgres_connection(postgres_test_url):
    """
    Provide a raw PostgreSQL connection for tests that need direct DB access.
    """
    if not os.getenv("DATABASE_URL") and not os.getenv("TEST_DATABASE_URL"):
        pytest.skip("PostgreSQL test database not configured")

    try:
        conn = psycopg.connect(postgres_test_url)
        yield conn
        conn.close()
    except Exception as e:
        pytest.skip(f"PostgreSQL connection failed: {e}")


@pytest.fixture
def db_session():
    """
    Provide a SQLAlchemy session for database tests.
    Creates a fresh database session for each test and rolls back changes after.
    """
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL") or os.getenv("TEST_DATABASE_URL")

    # Skip if no database is available
    if not database_url:
        pytest.skip("No database URL configured")

    try:
        # Import here to avoid circular imports
        from database import Base

        # Convert to SQLAlchemy format
        sqlalchemy_url = database_url

        # Handle asyncpg URLs - convert to psycopg2
        if "+asyncpg" in sqlalchemy_url:
            sqlalchemy_url = sqlalchemy_url.replace("+asyncpg", "+psycopg2")
        elif "postgresql://" in sqlalchemy_url and "+" not in sqlalchemy_url:
            sqlalchemy_url = sqlalchemy_url.replace(
                "postgresql://", "postgresql+psycopg2://",
            )

        # Remove SSL parameters that cause issues with psycopg2
        if "sslmode=" in sqlalchemy_url:
            from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

            parts = urlparse(sqlalchemy_url)
            query_params = parse_qs(parts.query)
            query_params.pop("sslmode", None)
            query_params.pop("channel_binding", None)
            new_query = urlencode(query_params, doseq=True)
            sqlalchemy_url = urlunparse(parts._replace(query=new_query))

        # Add SSL args if needed
        connect_args = {}
        if "azure" in sqlalchemy_url or "neon" in sqlalchemy_url:
            connect_args = {"sslmode": "require"}

        engine = create_engine(sqlalchemy_url, connect_args=connect_args)

        # Create all tables
        Base.metadata.create_all(bind=engine)

        # Create session factory
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

        # Create session for test
        session = SessionLocal()

        # Start a transaction that will be rolled back
        connection = engine.connect()
        transaction = connection.begin()

        # Configure the session to use our connection
        session.bind = connection

        yield session

        # Rollback the transaction
        session.close()
        transaction.rollback()
        connection.close()

    except Exception as e:
        pytest.skip(f"Database session creation failed: {e}")


@contextmanager
def temporary_env_var(key: str, value: str):
    """
    Temporarily set an environment variable for testing.
    """
    old_value = os.environ.get(key)
    os.environ[key] = value
    try:
        yield
    finally:
        if old_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = old_value


@pytest.fixture
def clean_test_db(postgres_connection):
    """
    Ensure a clean database state for each test.
    Drops and recreates checkpointing tables.
    """
    with postgres_connection.cursor() as cursor:
        # Drop existing checkpointing tables if they exist
        cursor.execute(
            """
            DROP TABLE IF EXISTS checkpoints CASCADE;
            DROP TABLE IF EXISTS checkpoint_blobs CASCADE;
            DROP TABLE IF EXISTS checkpoint_metadata CASCADE;
        """,
        )
        postgres_connection.commit()

    yield

    # Cleanup after test
    with postgres_connection.cursor() as cursor:
        cursor.execute(
            """
            DROP TABLE IF EXISTS checkpoints CASCADE;
            DROP TABLE IF EXISTS checkpoint_blobs CASCADE;
            DROP TABLE IF EXISTS checkpoint_metadata CASCADE;
        """,
        )
        postgres_connection.commit()


# Mark slow tests
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line(
        "markers", "requires_db: mark test as requiring database connection",
    )


def assert_api_response_security(response):
    """Assert API response has proper security headers."""
    # Check for security headers
    assert "X-Content-Type-Options" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    # Additional security checks can be added here
    pass


@pytest.fixture
def client():
    """Create a test client for FastAPI application."""
    from fastapi.testclient import TestClient
    from main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def authenticated_headers():
    """Create authenticated headers for testing."""
    # Mock JWT token for testing
    return {
        "Authorization": "Bearer test_token_12345",
        "Content-Type": "application/json",
    }


@pytest.fixture
def sample_business_profile():
    """Create a sample business profile for testing."""
    from unittest.mock import MagicMock

    profile = MagicMock()
    profile.id = "550e8400-e29b-41d4-a716-446655440000"
    profile.name = "Test Business"
    profile.company_name = "Test Company Inc."
    profile.industry = "Technology"
    profile.size = "Small"
    profile.employee_count = "50-100"
    profile.location = "US"
    profile.country = "United States"
    profile.existing_frameworks = ["ISO 27001", "SOC 2"]
    profile.planned_frameworks = ["GDPR", "HIPAA"]
    profile.handles_personal_data = True
    profile.processes_payments = True
    profile.stores_health_data = False
    profile.provides_financial_services = False
    profile.operates_critical_infrastructure = False
    profile.has_international_operations = True

    return profile


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    from unittest.mock import MagicMock

    user = MagicMock()
    user.id = "123e4567-e89b-12d3-a456-426614174000"
    user.email = "test@example.com"
    user.name = "Test User"
    user.is_active = True

    return user

# Import optimized fixtures if available
try:
    from database import Base
    from sqlalchemy import create_engine, event
    from sqlalchemy.orm import sessionmaker, Session
    from sqlalchemy.pool import StaticPool
    
    @pytest.fixture(scope="session")
    def sqlite_engine():
        """
        Create a shared in-memory SQLite database engine.
        Uses StaticPool to ensure the same connection is reused across tests.
        """
        from sqlalchemy.dialects import sqlite
        from sqlalchemy.dialects.postgresql import JSONB
        
        # Register JSONB as JSON for SQLite
        import sqlalchemy.dialects.sqlite
        sqlalchemy.dialects.sqlite.JSON = JSONB
        
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False
        )
        
        # Create all tables with JSON instead of JSONB for SQLite
        with engine.begin() as conn:
            # Override JSONB to use JSON for SQLite
            @event.listens_for(engine, "before_execute", once=True)
            def receive_before_execute(conn, clauseelement, multiparams, params, execution_options):
                if hasattr(clauseelement, 'element'):
                    pass
        
        Base.metadata.create_all(bind=engine)
        return engine
    
    @pytest.fixture(scope="function")
    def fast_db_session(sqlite_engine) -> Generator[Session, None, None]:
        """
        Fast database session using transaction rollback.
        
        Each test runs in a transaction that's rolled back after completion,
        ensuring test isolation without expensive table drops/creates.
        """
        connection = sqlite_engine.connect()
        transaction = connection.begin()
        
        # Configure session with connection
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=connection
        )
        session = SessionLocal()
        
        # Begin nested transaction for additional safety
        nested = connection.begin_nested()
        
        @event.listens_for(session, "after_transaction_end")
        def restart_savepoint(session, transaction):
            if transaction.nested and not transaction._parent.nested:
                nested = connection.begin_nested()
        
        yield session
        
        # Rollback and cleanup
        session.close()
        transaction.rollback()
        connection.close()
except ImportError:
    # Fallback to regular db_session if optimized fixtures not available
    @pytest.fixture
    def fast_db_session(db_session):
        return db_session


@pytest.fixture
def sample_user_data():
    """Create sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "company": "Test Company",
        "role": "compliance_manager"
    }
