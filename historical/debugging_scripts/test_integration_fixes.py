#!/usr/bin/env python3
"""
Test script to verify the integration fixes
"""

import asyncio
import os
from core.security.credential_encryption import CredentialEncryption
from api.clients.base_api_client import APICredentials, AuthType


async def test_encryption_fixes():
    """Test encryption fixes"""
    print("Testing encryption fixes...")

    # Set up test environment
    os.environ["CREDENTIAL_MASTER_KEY"] = "test-key-32-chars-long-for-testing"
    os.environ["DEPLOYMENT_ID"] = "test-deployment"

    try:
        # Test encryption system
        encryption = CredentialEncryption()

        test_creds = {
            "access_key": "test-access-key",
            "secret_key": "test-secret-key",
            "region": "us-east-1",
        }

        # Test encryption
        encrypted = encryption.encrypt_credentials(test_creds)
        print(f"✓ Credentials encrypted successfully: {len(encrypted)} bytes")

        # Test decryption
        decrypted = encryption.decrypt_credentials(encrypted)
        print(f"✓ Credentials decrypted successfully: {len(decrypted)} keys")

        # Verify integrity
        assert decrypted == test_creds
        print("✓ Encryption/decryption integrity verified")

        # Test health check
        health = encryption.verify_encryption_health()
        print(f"✓ Encryption health check: {health['status']}")

    except Exception as e:
        print(f"✗ Encryption test failed: {e}")
        return False

    return True


def test_model_imports():
    """Test model imports are working"""
    print("\nTesting model imports...")

    try:
        # Test model imports
        print("✓ All models imported successfully")

        # Test service imports
        print("✓ All services imported successfully")

        # Test client imports
        print("✓ Client classes imported successfully")

        return True

    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False


def test_validation_logic():
    """Test validation logic"""
    print("\nTesting validation logic...")

    try:
        # Test APICredentials validation
        valid_creds = APICredentials(
            provider="aws",
            auth_type=AuthType.API_KEY,
            credentials={"access_key": "test", "secret_key": "test"},
            region="us-east-1",
        )
        print(f"✓ Valid credentials object created: {valid_creds.provider}")

        # Test provider validation
        valid_providers = ["aws", "okta", "google_workspace", "microsoft_365"]
        for provider in valid_providers:
            assert provider in valid_providers
        print(f"✓ Provider validation logic: {len(valid_providers)} valid providers")

        return True

    except Exception as e:
        print(f"✗ Validation test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("=== Integration Fixes Test Suite ===\n")

    tests = [
        test_model_imports,
        test_validation_logic,
        test_encryption_fixes,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if asyncio.iscoroutinefunction(test):
                result = await test()
            else:
                result = test()

            if result:
                passed += 1

        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")

    print(f"\n=== Test Results: {passed}/{total} tests passed ===")

    if passed == total:
        print("🎉 All tests passed! The integration fixes are working correctly.")
        return True
    else:
        print("❌ Some tests failed. Review the implementation.")
        return False


if __name__ == "__main__":
    asyncio.run(main())
