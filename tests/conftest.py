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