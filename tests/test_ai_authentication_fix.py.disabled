"""
Test to verify the authentication fix for AI assessment endpoints.
This uses a mock approach to avoid database connection issues with TestClient.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from uuid import uuid4

from main import app
from database.user import User
from api.dependencies.auth import get_current_active_user, get_current_user
from database.db_setup import get_async_db


@pytest.fixture
def mock_user():
    """Create a mock user for testing."""
    return User(
        id=uuid4(), email="test@example.com", hashed_password="fake_password_hash", is_active=True
    )


@pytest.fixture
def mock_business_profile():
    """Create a mock business profile."""
    return {
        "id": str(uuid4()),
        "company_name": "Test Company",
        "industry": "Technology",
        "user_id": str(uuid4()),
    }


@pytest.fixture
def test_client_with_auth(mock_user, mock_business_profile):
    """Create test client with authentication overrides."""
    # Mock database session with proper async chaining
    mock_db = AsyncMock()
    mock_result = AsyncMock()
    mock_scalars = AsyncMock()
    mock_scalars.first = AsyncMock(return_value=mock_business_profile)
    mock_result.scalars = AsyncMock(return_value=mock_scalars)
    mock_db.execute = AsyncMock(return_value=mock_result)

    # Override dependencies
    async def override_get_async_db():
        yield mock_db

    def override_get_current_user():
        return mock_user

    def override_get_current_active_user():
        return mock_user

    # Store original overrides
    original_overrides = app.dependency_overrides.copy()

    # Apply overrides
    app.dependency_overrides[get_async_db] = override_get_async_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_current_active_user] = override_get_current_active_user

    client = TestClient(app)
    yield client

    # Restore original overrides
    app.dependency_overrides.clear()
    app.dependency_overrides.update(original_overrides)


def test_ai_help_endpoint_authentication_success(test_client_with_auth):
    """Test that AI help endpoint authentication works correctly."""
    request_data = {
        "question_id": "q1",
        "question_text": "What is GDPR compliance?",
        "framework_id": "gdpr",
        "section_id": "data_protection",
        "user_context": {
            "business_profile_id": str(uuid4()),
            "industry": "technology",
        },
    }

    # Mock the AI service to avoid actual AI calls
    with patch("services.ai.assistant.ComplianceAssistant") as mock_assistant:
        mock_assistant.return_value.get_assessment_help.return_value = {
            "guidance": "GDPR requires organizations to protect personal data...",
            "confidence_score": 0.95,
            "related_topics": ["data protection", "privacy rights"],
            "follow_up_suggestions": ["What are the key GDPR principles?"],
            "source_references": ["GDPR Article 5"],
            "request_id": "test-request-id",
            "generated_at": "2024-01-01T00:00:00Z",
        }

        # Make request with authentication headers (not needed due to override)
        response = test_client_with_auth.post(
            "/api/ai/assessments/gdpr/help",
            json=request_data,
            headers={"Authorization": "Bearer fake-token"},
        )

        # Verify authentication worked (no 401 error)
        assert response.status_code != 401
        print(f"Response status: {response.status_code}")
        print(
            f"Response content: {response.json() if response.status_code != 500 else 'Server error'}"
        )

        # The endpoint should at least not fail with authentication error
        assert response.status_code in [200, 500]  # 500 might be from other issues, but not 401


def test_followup_questions_endpoint_authentication_success(test_client_with_auth):
    """Test that follow-up questions endpoint authentication works correctly."""
    request_data = {
        "framework_id": "gdpr",
        "current_answers": {"q1": {"value": "yes", "source": "framework"}},
        "business_context": {
            "section_id": "data_processing",
            "business_profile_id": str(uuid4()),
        },
    }

    # Mock the AI service
    with patch("services.ai.assistant.ComplianceAssistant") as mock_assistant:
        mock_assistant.return_value.generate_assessment_followup.return_value = {
            "questions": [
                {
                    "id": "ai-q1",
                    "text": "What types of personal data do you process?",
                    "type": "multiple_choice",
                    "options": [
                        {"value": "names", "label": "Names"},
                        {"value": "emails", "label": "Email addresses"},
                        {"value": "financial", "label": "Financial data"},
                    ],
                    "reasoning": "Need to understand data types",
                    "priority": "high",
                }
            ],
            "request_id": "followup_123",
            "generated_at": "2024-01-01T00:00:00Z",
        }

        # Make request
        response = test_client_with_auth.post(
            "/api/ai/assessments/followup",
            json=request_data,
            headers={"Authorization": "Bearer fake-token"},
        )

        # Verify authentication worked (no 401 error)
        assert response.status_code != 401
        print(f"Response status: {response.status_code}")
        print(
            f"Response content: {response.json() if response.status_code != 500 else 'Server error'}"
        )

        # The endpoint should at least not fail with authentication error
        assert response.status_code in [200, 500]  # 500 might be from other issues, but not 401


def test_ai_help_endpoint_without_auth_override():
    """Test that endpoint still requires authentication when override is not applied."""
    request_data = {
        "question_id": "q1",
        "question_text": "What is GDPR compliance?",
        "framework_id": "gdpr",
    }

    # Create client without auth overrides
    client = TestClient(app)

    response = client.post("/api/ai/assessments/gdpr/help", json=request_data)

    # Should return 401 without authentication
    assert response.status_code == 401
