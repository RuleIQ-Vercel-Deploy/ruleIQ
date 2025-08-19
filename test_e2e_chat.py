#!/usr/bin/env python3
"""
End-to-end test for chat functionality.
Tests the complete flow from API request to AI response.
"""

import asyncio
import requests
from datetime import datetime, timedelta
from jose import jwt
import os
import sys

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.ai.assistant import ComplianceAssistant
from database.db_setup import get_async_db
from database.user import User
from uuid import uuid4, UUID
from typing import Optional

# Configuration
API_BASE_URL = "http://localhost:8000/api/v1"
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-for-production")


def create_test_jwt_token():
    """Create a JWT token for testing"""
    payload = {
        "sub": "4f27e8ae-58ef-4e28-b936-c89b8e02ddb1",  # Use real user ID from database
        "type": "access",
        "iat": int(datetime.utcnow().timestamp()),
        "exp": int((datetime.utcnow() + timedelta(hours=2)).timestamp()),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def test_api_create_conversation():
    """Test creating a conversation via REST API"""
    token = create_test_jwt_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    print("🧪 Testing conversation creation...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat/conversations",
            headers=headers,
            json={"title": "E2E Test Conversation"},
            timeout=10,
        )

        if response.status_code in [200, 201]:
            data = response.json()
            # Handle different response formats
            if "conversation" in data:
                conv_id = data["conversation"]["id"]
            else:
                conv_id = data["id"]
            print(f"✅ Conversation created: {conv_id}")
            return conv_id
        else:
            print(f"❌ Failed to create conversation: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating conversation: {e}")
        return None


def test_api_send_message(conversation_id):
    """Test sending a message via REST API"""
    if not conversation_id:
        return None

    token = create_test_jwt_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    test_message = (
        "Hello! Can you explain the key GDPR requirements for a small technology company?"
    )

    print("🧪 Testing message sending...")
    print(f"Message: {test_message}")

    try:
        response = requests.post(
            f"{API_BASE_URL}/chat/conversations/{conversation_id}/messages",
            headers=headers,
            json={"message": test_message},
            timeout=30,
        )

        if response.status_code in [200, 201]:
            data = response.json()
            print("✅ Message sent successfully")
            print(f"AI Response ID: {data.get('id')}")
            print(f"AI Response Preview: {data.get('content', '')[:100]}...")
            return data
        else:
            print(f"❌ Failed to send message: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error sending message: {e}")
        return None


def test_get_conversation_messages(conversation_id):
    """Test retrieving conversation messages"""
    if not conversation_id:
        return None

    token = create_test_jwt_token()
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    print("🧪 Testing message retrieval...")

    try:
        response = requests.get(
            f"{API_BASE_URL}/chat/conversations/{conversation_id}", headers=headers, timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            messages = data.get("messages", [])
            print(f"✅ Retrieved {len(messages)} messages")

            for i, msg in enumerate(messages):
                role = msg.get("role", "unknown")
                content = (
                    msg.get("content", "")[:100] + "..."
                    if len(msg.get("content", "")) > 100
                    else msg.get("content", "")
                )
                print(f"  [{i + 1}] {role}: {content}")

            return messages
        else:
            print(f"❌ Failed to retrieve messages: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error retrieving messages: {e}")
        return None


async def test_direct_ai_processing() -> Optional[bool]:
    """Test direct AI processing without API"""
    print("🧪 Testing direct AI processing...")

    try:
        async for db in get_async_db():
            assistant = ComplianceAssistant(db)

            # Create mock user
            user = User(
                id=UUID("4f27e8ae-58ef-4e28-b936-c89b8e02ddb1"),
                email="testuser@example.com",
                is_active=True,
            )

            conversation_id = uuid4()
            business_profile_id = uuid4()
            test_message = "What are the main data processing requirements under GDPR?"

            response, metadata = await assistant.process_message(
                conversation_id=conversation_id,
                user=user,
                message=test_message,
                business_profile_id=business_profile_id,
            )

            print("✅ Direct AI processing successful")
            print(f"Response length: {len(response)} characters")
            print(f"Response preview: {response[:200]}...")
            print(f"Metadata keys: {list(metadata.keys())}")

            return True
            break

    except Exception as e:
        print(f"❌ Error in direct AI processing: {e}")
        import traceback

        traceback.print_exc()
        return False


def main() -> bool:
    """Run complete end-to-end test"""
    print("🚀 Starting End-to-End Chat Functionality Test")
    print("=" * 60)

    # Test 1: Direct AI Processing
    print("\n1️⃣ Testing Direct AI Processing")
    direct_ai_success = asyncio.run(test_direct_ai_processing())

    # Test 2: API Flow
    print("\n2️⃣ Testing API Flow")
    conversation_id = test_api_create_conversation()
    message_data = None

    if conversation_id:
        message_data = test_api_send_message(conversation_id)

        # Wait a moment for AI processing
        print("⏳ Waiting for AI response processing...")
        import time

        time.sleep(3)

        messages = test_get_conversation_messages(conversation_id)

        # Check if we got AI response
        if messages and len(messages) >= 2:
            ai_messages = [msg for msg in messages if msg.get("role") == "assistant"]
            if ai_messages:
                print("✅ AI response received and stored")
                ai_response = ai_messages[0].get("content", "")
                if len(ai_response) > 50 and (
                    "GDPR" in ai_response or "data" in ai_response.lower()
                ):
                    print("✅ AI response quality check passed")
                else:
                    print(f"⚠️ AI response may not be optimal: {ai_response[:100]}...")
            else:
                print("⚠️ No AI responses found in conversation")
        else:
            print(
                f"⚠️ Expected at least 2 messages (user + AI), got {len(messages) if messages else 0}"
            )

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print(f"✅ Direct AI Processing: {'PASS' if direct_ai_success else 'FAIL'}")
    print(f"✅ API Conversation Creation: {'PASS' if conversation_id else 'FAIL'}")
    print(f"✅ Message Flow: {'PASS' if message_data else 'FAIL'}")

    if direct_ai_success and conversation_id and message_data:
        print("🎉 All tests passed! Chat functionality is working end-to-end.")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
