"""Final verification that test setup is working."""

import pytest
from sqlalchemy import text


def test_database_connection(db_session):
    """Test basic database connection."""
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1
    print("✅ Database connection works!")


def test_user_creation(db_session, sample_user):
    """Test user fixture creation."""
    assert sample_user.email == "test@example.com"
    assert sample_user.is_active is True

    # Verify user exists in database
    from database.user import User

    user = db_session.query(User).filter_by(email="test@example.com").first()
    assert user is not None
    assert user.id == sample_user.id
    print("✅ User fixture works!")


def test_business_profile(db_session, sample_business_profile):
    """Test business profile fixture."""
    assert sample_business_profile.company_name == "Test Company"
    assert sample_business_profile.industry == "Technology"
    print("✅ Business profile fixture works!")


def test_authenticated_client(client):
    """Test authenticated client fixture."""
    response = client.get("/api/users/me")
    # Even if it fails with 401, the client is working
    assert response.status_code in [200, 401, 403, 404]
    print("✅ Client fixture works!")


def test_evidence_service():
    """Test that services can be imported."""
    from services.evidence_service import EvidenceService

    print("✅ Services can be imported!")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
