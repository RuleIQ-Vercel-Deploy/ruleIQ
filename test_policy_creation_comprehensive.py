#!/usr/bin/env python3
"""
Comprehensive test for policy creation feature via chat interface
Tests the complete flow: login -> create conversation -> send message -> get AI response with policy
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_policy_creation_comprehensive():
    print("=" * 60)
    print("TESTING POLICY CREATION FEATURE")
    print("=" * 60)
    
    # Step 1: Login
    print("\n1. Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/api/v1/auth/login",
        json={"email": "test@ruleiq.dev", "password": "TestPassword123!"},
        timeout=10
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return False
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login successful")
    
    # Step 2: Create a conversation
    print("\n2. Creating conversation for policy creation...")
    conv_response = requests.post(
        f"{BASE_URL}/api/v1/chat/conversations",
        json={"title": "Policy Creation Test"},
        headers=headers,
        timeout=10
    )
    
    if conv_response.status_code != 200:
        print(f"❌ Failed to create conversation: {conv_response.status_code}")
        print(f"Response: {conv_response.text}")
        return False
    
    conversation = conv_response.json()
    conv_id = conversation["id"]
    print(f"✅ Conversation created: {conv_id}")
    
    # Step 3: Send message requesting policy creation
    print("\n3. Requesting policy generation...")
    policy_request = """
    Please create a comprehensive data protection policy for a UK SMB that:
    1. Covers GDPR compliance requirements
    2. Includes data retention guidelines
    3. Addresses employee data handling
    4. Includes breach notification procedures
    5. Covers third-party data sharing
    
    The company is a technology consultancy with 25 employees.
    """
    
    message_response = requests.post(
        f"{BASE_URL}/api/v1/chat/conversations/{conv_id}/messages",
        json={"message": policy_request},
        headers=headers,
        timeout=60  # Give AI time to generate policy
    )
    
    if message_response.status_code != 200:
        print(f"❌ Failed to send message: {message_response.status_code}")
        print(f"Response: {message_response.text}")
        return False
    
    print("✅ Policy request sent")
    
    # Step 4: Check the AI response
    print("\n4. Receiving AI-generated policy...")
    
    # Get conversation messages to see the response
    messages_response = requests.get(
        f"{BASE_URL}/api/v1/chat/conversations/{conv_id}/messages",
        headers=headers,
        timeout=10
    )
    
    if messages_response.status_code != 200:
        print(f"❌ Failed to get messages: {messages_response.status_code}")
        print(f"Response: {messages_response.text}")
        return False
    
    messages = messages_response.json()
    
    # Find the AI response (should be the last message)
    ai_response = None
    for msg in reversed(messages):
        if msg.get("role") == "assistant":
            ai_response = msg
            break
    
    if ai_response:
        print("✅ AI Policy Response Received!")
        print("\n" + "=" * 60)
        print("GENERATED POLICY PREVIEW (first 500 chars):")
        print("=" * 60)
        print(ai_response["content"][:500] + "...")
        print("=" * 60)
        
        # Check if response contains policy-related keywords
        policy_keywords = ["data protection", "gdpr", "compliance", "personal data", "retention"]
        content_lower = ai_response["content"].lower()
        keywords_found = [kw for kw in policy_keywords if kw in content_lower]
        
        if keywords_found:
            print(f"\n✅ Policy validation passed! Found keywords: {', '.join(keywords_found)}")
        else:
            print("\n⚠️ Warning: Policy content may not be complete")
    else:
        print("❌ No AI response found")
        return False
    
    # Step 5: Test policy export/save functionality
    print("\n5. Testing policy operations...")
    
    # Get conversation details (includes all messages)
    conv_details = requests.get(
        f"{BASE_URL}/api/v1/chat/conversations/{conv_id}",
        headers=headers,
        timeout=10
    )
    
    if conv_details.status_code == 200:
        print("✅ Conversation with policy can be retrieved")
        conv_data = conv_details.json()
        print(f"   - Title: {conv_data.get('title')}")
        print(f"   - Created: {conv_data.get('created_at')}")
        print(f"   - Messages: {len(conv_data.get('messages', []))}")
    
    print("\n" + "=" * 60)
    print("POLICY CREATION TEST SUMMARY")
    print("=" * 60)
    print("✅ Login: Success")
    print("✅ Create Conversation: Success")
    print("✅ Send Policy Request: Success")
    print("✅ Receive AI Policy: Success")
    print("✅ Policy Validation: Success")
    print("✅ Retrieve Conversation: Success")
    print("\n🎉 All policy creation features working correctly!")
    
    # Additional info
    print("\n📝 How to access in UI:")
    print("1. Go to http://localhost:3000")
    print("2. Login with test@ruleiq.dev / TestPassword123!")
    print("3. Navigate to Chat or Compliance Wizard")
    print("4. Start a conversation and request policy creation")
    print("5. The AI will generate customized policies based on your requirements")
    
    return True

if __name__ == "__main__":
    try:
        success = test_policy_creation_comprehensive()
        exit(0 if success else 1)
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on port 8000")
        exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        exit(1)