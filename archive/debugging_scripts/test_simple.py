#!/usr/bin/env python3
"""Simple test to debug the failing test."""

import sys
import os
import asyncio
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, ".")

# Set test environment
os.environ["ENVIRONMENT"] = "test"


async def test_basic_functionality() -> Optional[bool]:
    """Test basic functionality that's failing in pytest."""
    try:
        # Test imports
        print("1. Testing imports...")
        from services.ai.assistant import ComplianceAssistant

        print("✓ ComplianceAssistant imported")

        # Test golden dataset loading
        print("\n2. Testing golden dataset...")
        import json

        dataset_path = Path("tests/ai/golden_datasets/gdpr_questions.json")
        with open(dataset_path) as f:
            data = json.load(f)
        basic_questions = [q for q in data if q.get("difficulty") == "basic"]
        print(f"✓ Loaded {len(basic_questions)} basic questions")

        # Test database setup
        print("\n3. Testing database...")
        from tests.conftest import _db_manager

        await _db_manager.create_tables()
        print("✓ Database tables created")

        # Test getting a session
        print("\n4. Testing database session...")
        async_session_maker = _db_manager.get_async_session_maker()
        async with async_session_maker() as session:
            print("✓ Database session created")

        # Test creating ComplianceAssistant with session
        print("\n5. Testing ComplianceAssistant creation...")
        async with async_session_maker() as session:
            assistant = ComplianceAssistant(session)
            print("✓ ComplianceAssistant created")

        # Test mock AI client
        print("\n6. Testing mock AI client...")
        from unittest.mock import Mock

        mock_ai_client = Mock()
        mock_response = Mock()
        mock_response.text = "Mock AI response for testing compliance guidance."
        mock_ai_client.generate_content.return_value = mock_response
        print("✓ Mock AI client created")

        # Test creating user and business profile
        print("\n7. Testing user creation...")
        from database.user import User
        from database.business_profile import BusinessProfile
        from uuid import uuid4

        async with async_session_maker() as session:
            # Create test user
            user = User(id=uuid4(), email="test@example.com", hashed_password="test_hash")
            session.add(user)
            await session.commit()
            print(f"✓ User created: {user.id}")

            # Create test business profile
            profile = BusinessProfile(
                id=uuid4(),
                user_id=user.id,
                company_name="Test Company",
                industry="Technology",
                employee_count=50,
                country="USA",
                handles_personal_data=True,
                processes_payments=False,
                stores_health_data=False,
                provides_financial_services=False,
                operates_critical_infrastructure=False,
                has_international_operations=False,
            )
            session.add(profile)
            await session.commit()
            print(f"✓ Business profile created: {profile.id}")

        # Test the actual method call
        print("\n8. Testing assistant process_message...")
        async with async_session_maker() as session:
            assistant = ComplianceAssistant(session)

            # Create a simple test using proper parameters
            question = basic_questions[0]
            print(f"Question: {question['question'][:50]}...")

            # This is where it might be failing - let's try manually
            try:
                result = await assistant.process_message(
                    conversation_id=uuid4(),
                    user=user,
                    message=question["question"],
                    business_profile_id=profile.id,
                )
                print(f"✓ process_message returned: {type(result)}")

            except Exception as e:
                print(f"✗ process_message failed: {e}")
                import traceback

                traceback.print_exc()
                return False

        print("\n✓ All tests passed!")
        return True

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        try:
            await _db_manager.drop_tables()
            await _db_manager.dispose()
            print("✓ Database cleanup completed")
        except:
            pass


if __name__ == "__main__":
    success = asyncio.run(test_basic_functionality())
    sys.exit(0 if success else 1)
