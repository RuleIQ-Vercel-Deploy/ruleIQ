#!/usr/bin/env python3
"""
Create a test user for easy development login/logout.

This script creates a test user with known credentials for development purposes.
DO NOT USE IN PRODUCTION!

Usage:
    python scripts/create_test_user.py

The test user will have:
    Email: test@ruleiq.dev
    Password: TestPassword123!
"""

import os
import sys
import requests

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from config.logging_config import get_logger, setup_logging

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Test user credentials
TEST_USER_EMAIL = "test@ruleiq.dev"
TEST_USER_PASSWORD = "TestPassword123!"

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def create_test_user():
    """Create a test user for development purposes using the API."""
    logger.info("Creating test user for development...")

    try:
        # Try to register the test user
        register_url = f"{API_BASE_URL}/api/auth/register"
        user_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }

        response = requests.post(register_url, json=user_data)

        if response.status_code == 201:
            logger.info("✅ Test user created successfully!")
            logger.info("=" * 50)
            logger.info("🔑 TEST USER CREDENTIALS")
            logger.info("=" * 50)
            logger.info(f"📧 Email: {TEST_USER_EMAIL}")
            logger.info(f"🔒 Password: {TEST_USER_PASSWORD}")
            logger.info("=" * 50)
            logger.info("💡 You can now login to the frontend at:")
            logger.info("   http://localhost:3000/login")
            logger.info("=" * 50)
            return True
        elif response.status_code == 409:
            logger.info(f"Test user '{TEST_USER_EMAIL}' already exists!")
            logger.info("You can login with:")
            logger.info(f"  📧 Email: {TEST_USER_EMAIL}")
            logger.info(f"  🔒 Password: {TEST_USER_PASSWORD}")
            logger.info("💡 Frontend: http://localhost:3000/login")
            return True
        else:
            logger.error(f"Failed to create test user. Status: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        logger.error("❌ Could not connect to the API server.")
        logger.error("Make sure the backend is running on http://localhost:8000")
        logger.error("Start it with: python main.py")
        return False
    except Exception as e:
        logger.error(f"Error creating test user: {e}")
        return False

def test_login():
    """Test login with the test user credentials."""
    logger.info("Testing login with test user...")

    try:
        login_url = f"{API_BASE_URL}/api/auth/login"
        login_data = {
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        }

        response = requests.post(login_url, json=login_data)

        if response.status_code == 200:
            logger.info("✅ Login test successful!")
            token_data = response.json()
            logger.info(f"Access token received: {token_data['access_token'][:20]}...")
            return True
        else:
            logger.error(f"❌ Login test failed. Status: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False

    except Exception as e:
        logger.error(f"Error testing login: {e}")
        return False

def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        success = test_login()
    else:
        success = create_test_user()

    return success

if __name__ == "__main__":
    print("🚀 RuleIQ Test User Management")
    print("=" * 40)

    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage:")
        print("  python scripts/create_test_user.py          # Create test user")
        print("  python scripts/create_test_user.py --test   # Test login")
        print("  python scripts/create_test_user.py --help   # Show this help")
        sys.exit(0)

    success = main()
    sys.exit(0 if success else 1)
