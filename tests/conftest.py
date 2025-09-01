"""
Pytest configuration and fixtures for the test suite.
"""
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
            "postgresql://postgres:postgres@localhost:5433/compliance_test"
        )
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
            row_factory=dict_row  # Required for PostgresSaver
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
            sqlalchemy_url = sqlalchemy_url.replace("postgresql://", "postgresql+psycopg2://")
        
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
        cursor.execute("""
            DROP TABLE IF EXISTS checkpoints CASCADE;
            DROP TABLE IF EXISTS checkpoint_blobs CASCADE;
            DROP TABLE IF EXISTS checkpoint_metadata CASCADE;
        """)
        postgres_connection.commit()
    
    yield
    
    # Cleanup after test
    with postgres_connection.cursor() as cursor:
        cursor.execute("""
            DROP TABLE IF EXISTS checkpoints CASCADE;
            DROP TABLE IF EXISTS checkpoint_blobs CASCADE;
            DROP TABLE IF EXISTS checkpoint_metadata CASCADE;
        """)
        postgres_connection.commit()



# Mark slow tests
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "requires_db: mark test as requiring database connection"
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
        "Content-Type": "application/json"
    }


@pytest.fixture
def sample_business_profile():
    """Create a sample business profile for testing."""
    from unittest.mock import MagicMock
    
    profile = MagicMock()
    profile.id = "550e8400-e29b-41d4-a716-446655440000"
    profile.name = "Test Business"
    profile.industry = "Technology"
    profile.size = "Small"
    profile.location = "US"
    
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