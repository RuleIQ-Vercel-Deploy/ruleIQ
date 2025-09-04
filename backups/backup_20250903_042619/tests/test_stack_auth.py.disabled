#!/usr/bin/env python3
"""
Test script for Stack Auth integration
"""
import asyncio
import os
import sys
from typing import Dict, Any

# Add project root to Python path
sys.path.insert(0, '.')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

async def test_stack_auth():
    """Test Stack Auth functionality"""

    print("🧪 Testing Stack Auth Integration")
    print("=" * 50)

    # Check environment variables
    print("\n1. Environment Variables:")
    project_id = os.getenv("STACK_PROJECT_ID")
    secret_key = os.getenv("STACK_SECRET_SERVER_KEY")

    print(f"   STACK_PROJECT_ID: {'✅ Set' if project_id else '❌ Missing'}")
    print(f"   STACK_SECRET_SERVER_KEY: {'✅ Set' if secret_key else '❌ Missing'}")

    if not project_id or not secret_key:
        print("\n❌ Missing required environment variables!")
        return False

    # Test imports
    print("\n2. Testing Imports:")
    try:
        from api.middleware.stack_auth_middleware import validate_stack_token, StackAuthMiddleware
        from api.dependencies.stack_auth import get_current_stack_user
        print("   ✅ Stack Auth modules import successfully")
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False

    # Test middleware creation
    print("\n3. Testing Middleware Creation:")
    try:
        from fastapi import FastAPI
        app = FastAPI()
        middleware = StackAuthMiddleware(app)
        print("   ✅ Stack Auth middleware creates successfully")
    except Exception as e:
        print(f"   ❌ Middleware creation error: {e}")
        return False

    # Test token validation with dummy token (should fail gracefully)
    print("\n4. Testing Token Validation:")
    try:
        result = await validate_stack_token("invalid_token_for_testing")
        if result is None:
            print("   ✅ Invalid token correctly rejected")
        else:
            print("   ⚠️  Invalid token unexpectedly accepted")
    except Exception as e:
        if "Token validation" in str(e) or "Stack Auth" in str(e):
            print("   ✅ Invalid token correctly rejected with proper error")
        else:
            print(f"   ❌ Unexpected error: {e}")
            return False

    print("\n✅ Stack Auth integration tests passed!")
    print("\n📋 Next Steps:")
    print("   1. Ensure Stack Auth server is configured correctly")
    print("   2. Test with valid Stack Auth token from frontend")
    print("   3. Verify middleware is applied to protected routes")

    return True

if __name__ == "__main__":
    success = asyncio.run(test_stack_auth())
    sys.exit(0 if success else 1)
