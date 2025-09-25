#!/usr/bin/env python
"""
Test script to verify configuration loads correctly from environment variables
"""

import os
import sys


def test_environment_loading():
    """Test that configuration loads from environment variables"""
    print("=" * 60)
    print("CONFIGURATION ENVIRONMENT LOADING TEST")
    print("=" * 60)

    # Set environment to testing
    os.environ["ENVIRONMENT"] = "testing"

    # Check what's in .env.local
    print("\n1. Environment variables from .env.local:")
    print("-" * 40)

    # Key variables we want to verify
    test_vars = [
        "DATABASE_URL",
        "REDIS_URL",
        "JWT_SECRET_KEY",
        "OPENAI_API_KEY",
        "NEO4J_URI",
        "NEO4J_PASSWORD",
    ]

    # First, let's see what's in the environment before loading config
    for var in test_vars:
        value = os.environ.get(var, "NOT SET")
        if value and value != "NOT SET":
            # Mask sensitive parts
            if "password" in var.lower() or "key" in var.lower():
                display = value[:10] + "..." if len(value) > 10 else value
            else:
                display = value[:50] + "..." if len(value) > 50 else value
            print(f"  {var}: {display}")
        else:
            print(f"  {var}: {value}")

    # Now load the configuration
    print("\n2. Loading TestingConfig:")
    print("-" * 40)

    try:
        from config import get_config

        config = get_config("testing")

        print("✅ Configuration loaded successfully!")
        print(f"  Environment: {config.ENVIRONMENT}")

        # Check if environment variables override defaults
        print("\n3. Checking environment variable overrides:")
        print("-" * 40)

        # DATABASE_URL check
        db_url = config.DATABASE_URL
        if "neondb_owner" in db_url:
            print("✅ DATABASE_URL: Using environment value (Neon database)")
        elif db_url == "postgresql://localhost/ruleiq_test":
            print("❌ DATABASE_URL: Using hardcoded default (should use env)")
        else:
            print(f"⚠️  DATABASE_URL: Unknown value: {db_url[:50]}...")

        # JWT_SECRET_KEY check
        jwt_key = config.JWT_SECRET_KEY
        if jwt_key == "test-jwt-secret":
            print("⚠️  JWT_SECRET_KEY: Using test default (OK for testing)")
        elif "nTDlGluRj3" in jwt_key:
            print("✅ JWT_SECRET_KEY: Using environment value")
        else:
            print("⚠️  JWT_SECRET_KEY: Unknown value")

        # Redis URL check
        redis_url = config.REDIS_URL
        if redis_url == "redis://localhost:6379/15":
            print("⚠️  REDIS_URL: Using test default (OK for testing)")
        elif redis_url == "redis://localhost:6379/0":
            print("✅ REDIS_URL: Using environment value")
        else:
            print(f"⚠️  REDIS_URL: {redis_url}")

        # Neo4j check
        neo4j_password = config.NEO4J_PASSWORD
        if neo4j_password == "test":
            print("⚠️  NEO4J_PASSWORD: Using test default")
        elif neo4j_password == "please_change":
            print("✅ NEO4J_PASSWORD: Using environment value")
        else:
            print("⚠️  NEO4J_PASSWORD: Set to custom value")

        print("\n4. Configuration validation:")
        print("-" * 40)

        from config import validate_config

        try:
            validate_config(config)
            print("✅ Configuration validation passed!")
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")

    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        import traceback

        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    return True


def test_environment_override():
    """Test that we can override config with environment variables"""
    print("\n" + "=" * 60)
    print("ENVIRONMENT OVERRIDE TEST")
    print("=" * 60)

    # Set a custom DATABASE_URL
    test_db_url = "postgresql://testuser:testpass@testhost:5432/testdb"
    os.environ["DATABASE_URL"] = test_db_url
    os.environ["ENVIRONMENT"] = "testing"

    print(f"\n1. Setting DATABASE_URL to: {test_db_url}")

    # Reload config
    from config import reload_config

    config = reload_config("testing")

    print("\n2. Checking if override worked:")
    if test_db_url == config.DATABASE_URL:
        print("✅ DATABASE_URL successfully overridden!")
    else:
        print(f"❌ DATABASE_URL not overridden. Got: {config.DATABASE_URL[:50]}...")

    # Test with development config too
    print("\n3. Testing with development config:")
    config_dev = reload_config("development")
    if test_db_url == config_dev.DATABASE_URL:
        print("✅ Development config also uses environment override!")
    else:
        print("❌ Development config not using override")

    return True


if __name__ == "__main__":
    # First load environment from .env.local if it exists
    from pathlib import Path

    env_file = Path(".env.local")
    if env_file.exists():
        print(f"Loading environment from {env_file}")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    # Only set if not already in environment
                    if key not in os.environ:
                        os.environ[key] = value

    # Run tests
    success = test_environment_loading()
    if success:
        test_environment_override()
