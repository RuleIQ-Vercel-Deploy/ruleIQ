#!/usr/bin/env python3
"""
Configuration validation script for ruleIQ backend
Validates that all critical configuration values are properly set
"""

import os
import sys
from typing import List, Tuple

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.settings import get_settings
from config.security_config import SecurityConfig
from core.security.credential_encryption import get_credential_encryption


def validate_configuration() -> Tuple[bool, List[str]]:
    """
    Validate all critical configuration values

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []
    is_valid = True

    try:
        settings = get_settings()
        SecurityConfig()
        encryption = get_credential_encryption()

        # Validate database configuration
        if "localhost" in settings.database_url and settings.is_production:
            issues.append("WARNING: Using localhost database in production")

        # Validate security keys
        dev_defaults = [
            "development-secret-key-change-in-production",
            "development-credential-master-key-change-in-production",
            "development-fernet-key-change-in-production",
        ]

        if settings.secret_key in dev_defaults:
            issues.append("CRITICAL: Using development SECRET_KEY")
            is_valid = False

        if settings.credential_master_key in dev_defaults:
            issues.append("CRITICAL: Using development CREDENTIAL_MASTER_KEY")
            is_valid = False

        if settings.fernet_key in dev_defaults:
            issues.append("CRITICAL: Using development FERNET_KEY")
            is_valid = False

        # Validate API keys
        if settings.google_api_key == "your-google-api-key":
            issues.append("WARNING: Google API key not configured")

        if not settings.openai_api_key:
            issues.append("INFO: OpenAI API key not configured")

        if not settings.anthropic_api_key:
            issues.append("INFO: Anthropic API key not configured")

        # Validate encryption system
        try:
            health = encryption.verify_encryption_health()
            if health.get("status") != "healthy":
                issues.append(f"ERROR: Encryption system unhealthy: {health}")
                is_valid = False
        except Exception as e:
            issues.append(f"ERROR: Failed to validate encryption system: {e}")
            is_valid = False

        # Validate environment
        if settings.is_production:
            try:
                settings.validate_production_settings()
            except ValueError as e:
                issues.append(f"CRITICAL: Production validation failed: {e}")
                is_valid = False

    except Exception as e:
        issues.append(f"ERROR: Failed to load configuration: {e}")
        is_valid = False

    return is_valid, issues


def print_validation_report() -> int:
    """Print a comprehensive validation report"""
    print("🔍 ruleIQ Backend Configuration Validation")
    print("=" * 50)

    is_valid, issues = validate_configuration()

    if is_valid and not issues:
        print("✅ All configuration values are valid!")
        return 0

    print("\n📋 Validation Results:")

    for issue in issues:
        if issue.startswith("CRITICAL"):
            print(f"❌ {issue}")
        elif issue.startswith("WARNING"):
            print(f"⚠️  {issue}")
        elif issue.startswith("ERROR"):
            print(f"❌ {issue}")
        else:
            print(f"ℹ️  {issue}")

    if not is_valid:
        print("\n🔧 Configuration Fix Commands:")
        print("1. Set secure SECRET_KEY:")
        print(
            "   export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
        )
        print("2. Set secure CREDENTIAL_MASTER_KEY:")
        print(
            "   export CREDENTIAL_MASTER_KEY=$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
        )
        print("3. Set secure FERNET_KEY:")
        print(
            "   export FERNET_KEY=$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
        )
        print("4. Set Google API key:")
        print("   export GOOGLE_API_KEY=your_actual_google_api_key")

    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(print_validation_report())
