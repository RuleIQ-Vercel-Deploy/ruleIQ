"""
Pytest configuration and shared fixtures for ComplianceGPT tests.
"""

import os
from cryptography.fernet import Fernet

# Set environment variables for testing BEFORE any application modules are imported.
# This prevents the app from loading production settings during test collection.
os.environ["ENV"] = "testing"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://test_user:test_password@localhost:5433/test_db"
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

# Add project root to the Python path to resolve import errors
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Assuming these are the correct paths from your project structure
from database.db_setup import get_async_db, Base, _init_async_db, _async_engine
from database.user import User
from database.business_profile import BusinessProfile
from database.evidence_item import EvidenceItem
from database.generated_policy import GeneratedPolicy # Assuming this is the model for policy documents


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
    if _async_engine is None: # Ensure engine is initialized if not already
        _init_async_db()
    engine_to_use = _async_engine
    async with engine_to_use.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_to_use.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session() -> AsyncSession: # Changed from db_session to align with async
    """Create an async test database session for unit tests."""
    async for session in get_async_db():
        yield session
        # No explicit close needed due to 'async with' in get_async_db
        break # Important to break to ensure the generator is exhausted

@pytest.fixture
async def sample_user(db_session: AsyncSession) -> User:
    """Create a sample user for tests."""
    user = User(
        id=uuid4(),
        username="sampleuser@example.com",
        email="sampleuser@example.com",
        password_hash="fake_password_hash" # In real scenarios, hash properly
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
        "compliance_frameworks": ["ISO27001", "SOC2"],
        "description": "A sample company for testing purposes.",
        "website": "http://samplecorp.test"
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
async def sample_evidence_item(db_session: AsyncSession, sample_business_profile: BusinessProfile) -> EvidenceItem:
    """Create a sample evidence item for tests."""
    evidence = EvidenceItem(
        id=uuid4(),
        user_id=sample_business_profile.user_id,
        business_profile_id=sample_business_profile.id,
        evidence_name="Sample Security Policy",
        evidence_type="policy_document",
        description="A sample security policy document for testing.",
        status="active",
        file_path="/path/to/sample/policy.pdf", # Placeholder
        integration_source="manual",
        framework_mappings=["ISO27001:A.5.1"],
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
