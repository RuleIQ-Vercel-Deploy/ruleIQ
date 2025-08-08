"""
Test to verify the hybrid approach works correctly.
"""

import pytest
from uuid import uuid4


def test_sync_database_fixture_works(sync_db_session, sync_sample_user):
    """Test that sync database fixtures work."""
    assert sync_sample_user.email == "test@example.com"
    assert sync_sample_user.is_active

    # Verify user is in database
    from database.user import User

    user = sync_db_session.query(User).filter(User.id == sync_sample_user.id).first()
    assert user is not None
    assert user.email == "test@example.com"


def test_test_client_fixture_works(test_client):
    """Test that test client fixture works."""
    # Test a simple endpoint
    response = test_client.get("/health")
    # Should not get 500 error
    assert response.status_code in [200, 404]  # 404 is ok if endpoint doesn't exist


def test_authentication_override_works(test_client):
    """Test that authentication override works in test client."""
    # Test an endpoint that requires authentication
    response = test_client.get("/api/users/me")
    # Should not get 401 error
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.json() if response.status_code != 500 else 'Server error'}")
    assert response.status_code != 401


def test_ai_assessment_endpoint_authentication(test_client):
    """Test that AI assessment endpoints don't fail with authentication."""
    request_data = {
        "question_id": "q1",
        "question_text": "What is GDPR compliance?",
        "framework_id": "gdpr",
    }

    response = test_client.post("/api/ai/assessments/gdpr/help", json=request_data)
    # Should not get 401 error
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.json() if response.status_code != 500 else 'Server error'}")
    assert response.status_code != 401


def test_followup_questions_endpoint_basic(test_client):
    """Test basic follow-up questions endpoint."""
    request_data = {
        "framework_id": "gdpr",
        "current_answers": {"q1": {"value": "yes", "source": "framework"}},
        "business_context": {
            "section_id": "data_processing",
            "business_profile_id": str(uuid4()),
        },
    }

    response = test_client.post("/api/ai/assessments/followup", json=request_data)
    # Should not get 401 error
    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.json() if response.status_code != 500 else 'Server error'}")
    assert response.status_code != 401
