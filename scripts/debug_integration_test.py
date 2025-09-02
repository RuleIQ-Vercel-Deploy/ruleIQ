#!/usr/bin/env python3
"""Debug integration test manually"""

import asyncio
import sys
import os

sys.path.insert(0, ".")

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch

# Load environment from .env.local (same as main app)
from dotenv import load_dotenv

load_dotenv(".env.local", override=True)

# Set up testing overrides only
os.environ.update({"IS_TESTING": "true"})


def test_ai_help_manually():
    """Test the AI help endpoint manually"""
    try:
        from main import app
        from database.db_setup import get_db_session
        from tests.conftest import TEST_USER_ID
        from database.user import User
        from database.business_profile import BusinessProfile
        from api.dependencies.auth import create_access_token, get_password_hash
        from datetime import timedelta
        from services.ai.assistant import ComplianceAssistant

        print("🔄 Setting up test client...")
        client = TestClient(app)

        print("🔄 Setting up database session...")
        # Force database initialization to pick up latest schema
        from database.db_setup import init_db

        init_db()
        db = next(get_db_session())

        # Check database columns first
        print("🔄 Checking database schema...")
        from sqlalchemy import text

        result = db.execute(
            text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'users' ORDER BY ordinal_position"
            )
        )
        columns = [row[0] for row in result]
        print(f"✅ Columns in users table: {columns}")

        # Create test user if not exists
        print("🔄 Creating test user...")
        existing_user = db.query(User).filter_by(id=TEST_USER_ID).first()
        if not existing_user:
            user = User(
                id=TEST_USER_ID,
                email="test@example.com",
                hashed_password=get_password_hash("TestPassword123!"),
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            user = existing_user

        print(f"✅ User created/found: {user.email}")

        # Create business profile
        print("🔄 Creating business profile...")
        existing_profile = db.query(BusinessProfile).filter_by(user_id=user.id).first()
        if not existing_profile:
            profile = BusinessProfile(
                user_id=user.id,
                company_name="Test Company",
                industry="Technology",
                company_size="10-50",
                primary_location="London",
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
        else:
            profile = existing_profile

        print(f"✅ Business profile created/found: {profile.company_name}")

        # Create auth token
        print("🔄 Creating auth token...")
        token_data = {"sub": str(user.id)}
        auth_token = create_access_token(
            data=token_data, expires_delta=timedelta(minutes=30)
        )
        headers = {"Authorization": f"Bearer {auth_token}"}

        print(f"✅ Auth token created: {auth_token[:50]}...")

        # Prepare request data
        request_data = {
            "question_id": "q1",
            "question_text": "What is GDPR compliance?",
            "framework_id": "gdpr",
            "section_id": "data_protection",
            "user_context": {
                "business_profile_id": str(profile.id),
                "industry": "technology",
            },
        }

        print("🔄 Testing endpoint with mock...")
        with patch.object(ComplianceAssistant, "get_assessment_help") as mock_help:
            # Mock successful AI response
            mock_help.return_value = {
                "guidance": "GDPR requires organizations to protect personal data...",
                "confidence_score": 0.95,
                "related_topics": ["data protection", "privacy rights"],
                "follow_up_suggestions": ["What are the key GDPR principles?"],
                "source_references": ["GDPR Article 5"],
                "request_id": "test-request-id",
                "generated_at": "2024-01-01T00:00:00Z",
            }

            print("🔄 Making POST request...")
            response = client.post(
                "/api/ai/assessments/gdpr/help", json=request_data, headers=headers
            )

            print(f"✅ Response status: {response.status_code}")
            print(f"✅ Response headers: {dict(response.headers)}")

            if response.status_code != 200:
                print(f"❌ Response content: {response.text}")
                print(
                    f"❌ Response JSON: {response.json() if response.content else 'No content'}"
                )
            else:
                response_data = response.json()
                print(f"✅ Response data keys: {list(response_data.keys())}")
                print(f"✅ Guidance: {response_data.get('guidance', 'N/A')[:100]}...")

                # Test assertions
                assert "guidance" in response_data
                assert "confidence_score" in response_data
                assert "request_id" in response_data
                assert "generated_at" in response_data
                assert response_data["confidence_score"] >= 0.0
                assert response_data["confidence_score"] <= 1.0

                print("🎉 All assertions passed!")

        db.close()

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_ai_help_manually()
