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
from datetime import datetime, timedelta, timezone

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
warnings.filterwarnings(
    "ignore", message=".*Event loop is closed.*", category=RuntimeWarning
)
warnings.filterwarnings(
    "ignore", message=".*attached to a different loop.*", category=RuntimeWarning
)
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

mock_model.generate_content_stream.side_effect = (
    lambda *args, **kwargs: mock_stream_generator()
)

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
    elif "postgresql://" + os.getenv("DB_USER", "postgres") + ":" + os.getenv("DB_PASSWORD", "postgres") + "@" + os.getenv("DB_HOST", "localhost") + ":" + os.getenv("DB_PORT", "5432") + "/" + os.getenv("DB_NAME", "database") + "/to/sample/policy.pdf",
        automation_source="manual",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
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
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
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
    dataset_path = (
        Path(__file__).parent / "ai" / "golden_datasets" / "gdpr_questions.json"
    )

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
