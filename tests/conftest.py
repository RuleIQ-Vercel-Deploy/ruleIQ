"""
Fixed pytest configuration for ruleIQ tests.
Resolves event loop and database connection issues.
"""

import asyncio
import json
import os
import warnings
import logging
from typing import Generator, AsyncGenerator, Dict, Any, Optional
from contextlib import asynccontextmanager
from uuid import uuid4, UUID
from datetime import datetime, timedelta
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy import create_engine, text, pool
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, StaticPool
from fastapi.testclient import TestClient

# =============================================================================
# ENVIRONMENT SETUP
# =============================================================================

# Suppress warnings early
warnings.filterwarnings("ignore", message=".*bcrypt.*", category=UserWarning)
warnings.filterwarnings("ignore", message=".*bcrypt.*", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*bcrypt.*", category=RuntimeWarning)
logging.getLogger("passlib.handlers.bcrypt").setLevel(logging.ERROR)

# Set test environment variables
os.environ["ENV"] = "testing"
os.environ["DATABASE_URL"] = "postgresql://neondb_owner:npg_s0JhnfGNy3Ze@ep-wild-grass-a8o37wq8-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"
os.environ["SECRET_KEY"] = "test_secret_key_for_pytest_sessions"
os.environ["GOOGLE_API_KEY"] = "test_key_for_mocking"
os.environ["SENTRY_DSN"] = ""
os.environ["USE_MOCK_AI"] = "true"

# Generate Fernet key for encryption
from cryptography.fernet import Fernet
os.environ['FERNET_KEY'] = Fernet.generate_key().decode()

# =============================================================================
# COMPREHENSIVE AI MOCKING SETUP
# =============================================================================

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
sys.modules['google'] = unittest.mock.MagicMock()
sys.modules['google.generativeai'] = mock_genai
sys.modules['google.generativeai.caching'] = mock_genai.caching
sys.modules['google.generativeai.types'] = mock_types

# =============================================================================
# PROJECT IMPORTS
# =============================================================================

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import database components
from database.db_setup import Base, _get_configured_database_urls
from database.user import User
from database.business_profile import BusinessProfile
from database.compliance_framework import ComplianceFramework
from database.evidence_item import EvidenceItem
from database.generated_policy import GeneratedPolicy

# Import all models to ensure they're registered with Base
from database.assessment_question import AssessmentQuestion
from database.assessment_session import AssessmentSession
from database.chat_conversation import ChatConversation
from database.chat_message import ChatMessage
from database.implementation_plan import ImplementationPlan
from database.integration_configuration import IntegrationConfiguration
from database.readiness_assessment import ReadinessAssessment
from database.report_schedule import ReportSchedule
from database.models.integrations import Integration, EvidenceCollection, IntegrationEvidenceItem, IntegrationHealthLog, EvidenceAuditLog

# =============================================================================
# EVENT LOOP CONFIGURATION - CRITICAL FOR FIXING ASYNC ISSUES
# =============================================================================

# Use the new event_loop_policy fixture from pytest-asyncio
pytest_plugins = ("pytest_asyncio",)

@pytest.fixture(scope="session")
def event_loop_policy():
    """Create a custom event loop policy for tests."""
    return asyncio.DefaultEventLoopPolicy()

# =============================================================================
# UNIFIED DATABASE MANAGER WITH PROPER ASYNC HANDLING
# =============================================================================

class UnifiedDatabaseManager:
    """Unified database manager for all test types with proper async handling."""
    
    def __init__(self):
        self._sync_engine = None
        self._async_engine = None
        self._initialized = False
        self._async_session_maker = None
        self._sync_session_maker = None
    
    def _initialize_engines(self):
        """Initialize both sync and async engines with proper pooling."""
        if self._initialized:
            return
            
        # Get database URLs
        db_url, sync_url, async_url = _get_configured_database_urls()
        
        # Create sync engine with StaticPool for better connection management
        self._sync_engine = create_engine(
            sync_url,
            poolclass=StaticPool,  # Use StaticPool for better connection reuse
            echo=False,
            connect_args={
                "connect_timeout": 10,  # Align with production settings
                # Remove statement_timeout for Neon compatibility
            }
        )
        
        # Create async engine with proper SSL handling
        if "sslmode=require" in async_url:
            async_url = async_url.replace("sslmode=require", "")
            ssl_config = {"ssl": "require"}
        else:
            ssl_config = {}
        
        self._async_engine = create_async_engine(
            async_url,
            poolclass=NullPool,  # Use NullPool for async to avoid event loop issues
            echo=False,
            future=True,
            pool_pre_ping=True,
            connect_args={
                "server_settings": {
                    "jit": "off",
                    # Remove statement_timeout for Neon compatibility
                },
                "command_timeout": 10,  # Align with production settings
                **ssl_config
            }
        )
        
        # Create session makers
        self._sync_session_maker = sessionmaker(
            self._sync_engine, 
            autocommit=False, 
            autoflush=False
        )
        
        self._async_session_maker = async_sessionmaker(
            self._async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False
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
    
    def get_sync_session_maker(self):
        """Get sync session maker."""
        self._initialize_engines()
        return self._sync_session_maker
    
    def get_async_session_maker(self):
        """Get async session maker."""
        self._initialize_engines()
        return self._async_session_maker
    
    async def create_tables(self):
        """Create database tables for tests."""
        async_engine = self.get_async_engine()
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def drop_tables(self):
        """Drop database tables after tests."""
        if not self._initialized:
            return
            
        try:
            async_engine = self.get_async_engine()
            async with async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
        except Exception as e:
            print(f"Warning: Table cleanup failed: {e}")
    
    async def dispose(self):
        """Dispose of database engines properly."""
        if self._sync_engine:
            self._sync_engine.dispose()
            self._sync_engine = None
            
        if self._async_engine:
            await self._async_engine.dispose()
            self._async_engine = None
            
        self._initialized = False
        self._async_session_maker = None
        self._sync_session_maker = None

# Global database manager instance
_db_manager = UnifiedDatabaseManager()

# =============================================================================
# CORE PYTEST FIXTURES
# =============================================================================

@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Set up database for test session with proper cleanup."""
    # Create tables
    await _db_manager.create_tables()
    print("Database tables created successfully")
    
    # Initialize default frameworks
    try:
        async_session_maker = _db_manager.get_async_session_maker()
        async with async_session_maker() as session:
            from services.framework_service import initialize_default_frameworks
            await initialize_default_frameworks(session)
            print("Default frameworks initialized successfully")
    except Exception as e:
        print(f"Warning: Failed to initialize frameworks: {e}")
    
    yield
    
    # Clean up
    await _db_manager.drop_tables()
    await _db_manager.dispose()
    print("Database cleanup completed")

# =============================================================================
# SYNC DATABASE FIXTURES
# =============================================================================

@pytest.fixture
def db_session():
    """Sync database session for tests with proper cleanup."""
    SessionLocal = _db_manager.get_sync_session_maker()
    session = SessionLocal()
    
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

@pytest.fixture
def sync_db_session(db_session):
    """Alias for db_session for backward compatibility."""
    return db_session

# =============================================================================
# ASYNC DATABASE FIXTURES
# =============================================================================

@pytest_asyncio.fixture
async def async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Async database session for pure async tests with proper cleanup."""
    async_session_maker = _db_manager.get_async_session_maker()
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

# =============================================================================
# USER FIXTURES
# =============================================================================

# Fixed UUIDs for consistent testing
TEST_USER_ID = UUID("12345678-1234-5678-9012-123456789012")
TEST_BUSINESS_PROFILE_ID = UUID("87654321-4321-8765-4321-876543218765")

@pytest.fixture
def sample_user(db_session):
    """Create a sample user for sync tests."""
    # Check if user already exists
    existing = db_session.query(User).filter_by(email="test@example.com").first()
    if existing:
        return existing
        
    user = User(
        id=TEST_USER_ID,
        email="test@example.com",
        hashed_password="fake_password_hash",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest_asyncio.fixture
async def async_sample_user(async_db_session: AsyncSession) -> User:
    """Create a sample user for async tests."""
    from sqlalchemy import select
    
    # Check if user already exists
    result = await async_db_session.execute(
        select(User).filter_by(email="test@example.com")
    )
    existing = result.scalars().first()
    if existing:
        return existing
        
    user = User(
        id=uuid4(),
        email="test@example.com",
        hashed_password="fake_password_hash",
        is_active=True
    )
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    return user

# =============================================================================
# BUSINESS PROFILE FIXTURES
# =============================================================================

@pytest.fixture
def sample_business_profile(db_session, sample_user):
    """Create a sample business profile for sync tests."""
    # Check if profile already exists
    existing = db_session.query(BusinessProfile).filter_by(
        user_id=sample_user.id
    ).first()
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
        compliance_timeline="6-12 months"
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile

@pytest_asyncio.fixture
async def async_sample_business_profile(async_db_session: AsyncSession, async_sample_user: User) -> BusinessProfile:
    """Create a sample business profile for async tests."""
    from sqlalchemy import select
    
    # Check if profile already exists
    result = await async_db_session.execute(
        select(BusinessProfile).filter_by(user_id=async_sample_user.id)
    )
    existing = result.scalars().first()
    if existing:
        return existing
        
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
        compliance_timeline="6-12 months"
    )
    async_db_session.add(profile)
    await async_db_session.commit()
    await async_db_session.refresh(profile)
    return profile

# =============================================================================
# AUTHENTICATION FIXTURES
# =============================================================================

@pytest.fixture
def auth_token(sample_user: User) -> str:
    """Generate authentication token for tests."""
    from api.dependencies.auth import create_access_token
    
    token_data = {"sub": str(sample_user.id)}
    return create_access_token(data=token_data, expires_delta=timedelta(minutes=30))

@pytest.fixture
def authenticated_headers(auth_token: str) -> Dict[str, str]:
    """Provide authenticated headers for API tests."""
    return {"Authorization": f"Bearer {auth_token}"}

# =============================================================================
# TEST CLIENT FIXTURES WITH PROPER ASYNC HANDLING
# =============================================================================

@pytest.fixture
def client(db_session, sample_user):
    """Authenticated test client with database overrides."""
    from main import app
    from api.dependencies.auth import get_current_active_user, get_current_user
    from database.db_setup import get_async_db, get_db
    
    # Store the current overrides
    original_overrides = app.dependency_overrides.copy()
    
    # Override database dependencies
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    async def override_get_async_db():
        yield db_session
    
    # Override auth dependencies
    def override_get_current_user():
        return sample_user
    
    def override_get_current_active_user():
        return sample_user
    
    # Apply overrides
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_async_db] = override_get_async_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user
    
    with TestClient(app) as client:
        yield client
    
    # Restore original overrides
    app.dependency_overrides = original_overrides

@pytest.fixture
def unauthenticated_client(db_session):
    """Unauthenticated test client with database overrides."""
    from main import app
    from database.db_setup import get_async_db, get_db
    
    # Store the current overrides
    original_overrides = app.dependency_overrides.copy()
    
    # Override database dependencies only
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    async def override_get_async_db():
        yield db_session
    
    # Apply overrides
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_async_db] = override_get_async_db
    
    with TestClient(app) as client:
        yield client
    
    # Restore original overrides
    app.dependency_overrides = original_overrides

# =============================================================================
# ADDITIONAL DOMAIN FIXTURES
# =============================================================================

@pytest.fixture
def sample_compliance_framework(db_session):
    """Create a sample compliance framework for tests."""
    # Check if framework already exists
    existing = db_session.query(ComplianceFramework).filter_by(
        name="ISO27001"
    ).first()
    if existing:
        return existing
        
    framework = ComplianceFramework(
        id=uuid4(),
        name="ISO27001",
        display_name="ISO/IEC 27001:2022",
        description="Information security management systems",
        category="Information Security"
    )
    db_session.add(framework)
    db_session.commit()
    db_session.refresh(framework)
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
        updated_at=datetime.utcnow()
    )
    db_session.add(evidence)
    db_session.commit()
    db_session.refresh(evidence)
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
        updated_at=datetime.utcnow()
    )
    db_session.add(policy)
    db_session.commit()
    db_session.refresh(policy)
    return policy

# =============================================================================
# GLOBAL AI MOCKING FIXTURE
# =============================================================================

@pytest.fixture(autouse=True)
def ensure_ai_mocking():
    """Ensure all tests use mocked AI instead of real API calls."""
    yield mock_model

@pytest.fixture(autouse=True)
def reset_app_state():
    """Reset FastAPI app state between tests to prevent contamination."""
    yield
    
    # Clean up app state after each test
    try:
        from main import app
        
        # Clear all dependency overrides
        app.dependency_overrides.clear()
        
        # Clear any cached OpenAPI spec
        if hasattr(app, '_openapi'):
            delattr(app, '_openapi')
        
        # Clear route cache if it exists
        if hasattr(app, '_route_cache'):
            delattr(app, '_route_cache')
            
    except Exception:
        pass

@pytest.fixture
def mock_ai_client():
    """Provide a mock AI client for testing AI-related functionality."""
    from unittest.mock import Mock, patch, AsyncMock
    
    # Create a mock AI client
    mock_client = Mock()
    
    # Mock the generate_content method
    mock_response = Mock()
    mock_response.text = "Mock AI response for testing compliance guidance. GDPR requires data protection measures including consent management, data minimization, and breach notification within 72 hours."
    mock_client.generate_content.return_value = mock_response
    
    # Mock the async generate_content_async method
    mock_client.generate_content_async = AsyncMock(return_value=mock_response)
    
    # Patch the get_ai_model function to return our mock
    with patch('config.ai_config.get_ai_model', return_value=mock_client):
        yield mock_client

# =============================================================================
# TESTING UTILITY FUNCTIONS
# =============================================================================

def assert_api_response_security(response):
    """Assert security headers are present in API responses."""
    # Check for security headers
    assert "X-Content-Type-Options" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"

def assert_no_sensitive_data_in_logs(log_capture):
    """Assert no sensitive data is present in logs."""
    sensitive_keywords = ["password", "secret", "api_key", "token"]
    for record in log_capture.records:
        log_message = record.getMessage().lower()
        for keyword in sensitive_keywords:
            assert keyword not in log_message, f"Sensitive keyword '{keyword}' found in logs."

# =============================================================================
# ADDITIONAL FIXTURES FOR COMPREHENSIVE TEST COVERAGE
# =============================================================================

@pytest.fixture
def compliance_golden_dataset():
    """Load comprehensive compliance questions from golden dataset JSON files."""
    import json
    from pathlib import Path
    
    # Try to load the golden dataset, fallback to mock data if not found
    dataset_path = Path(__file__).parent / "ai" / "golden_datasets" / "gdpr_questions.json"
    
    if dataset_path.exists():
        with open(dataset_path, 'r') as f:
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
            }
        ]

@pytest.fixture
def sample_evidence_data():
    """Sample evidence data for API testing."""
    return {
        "evidence_name": "Information Security Policy",
        "description": "Comprehensive security policy covering access controls, data protection, and incident response procedures",
        "evidence_type": "policy_document",
        "raw_data": json.dumps({
            "file_type": "pdf",
            "content": "This policy establishes comprehensive security controls..."
        })
    }

@pytest.fixture
def sample_business_context():
    """Sample business context for testing."""
    return {
        'company_name': 'Test Corp',
        'industry': 'Technology',
        'employee_count': 150,
        'existing_frameworks': ['ISO27001']
    }

@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "full_name": "Test User",
        "company": "Test Corp"
    }

@pytest_asyncio.fixture
async def compliance_assistant(async_db_session):
    """Compliance assistant for testing."""
    from services.ai.assistant import ComplianceAssistant
    return ComplianceAssistant(async_db_session)

@pytest.fixture
def sample_customization_options():
    """Sample policy customization options."""
    return {
        'policy_type': 'data_protection',
        'jurisdiction': 'UK',
        'industry_specific': True,
        'include_templates': True
    }

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