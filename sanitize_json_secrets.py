#!/usr/bin/env python3
"""
Script to sanitize sensitive data from JSON files.
Removes or masks API keys, passwords, tokens, and other secrets.
"""

import json
import re
import sys
from pathlib import Path


def sanitize_value(value, key_name=""):
    """Sanitize a single value based on patterns and key names."""
    if not isinstance(value, str):
        return value

    # Key name patterns that indicate secrets
    secret_key_patterns = [
        'password', 'passwd', 'pwd', 'secret', 'token', 'api_key', 'apikey',
        'auth', 'credential', 'private', 'access_key', 'secret_key',
        'client_secret', 'jwt', 'bearer', 'oauth', 'session'
    ]

    # Check if the key name suggests a secret
    key_lower = key_name.lower()
    is_secret_key = any(pattern in key_lower for pattern in secret_key_patterns)

    # Patterns for detecting secrets in values
    secret_patterns = [
        (r'sk-[a-zA-Z0-9]{48,}', 'OPENAI_API_KEY_REDACTED'),  # OpenAI
        (r'AIza[0-9A-Za-z_-]{35}', 'GOOGLE_API_KEY_REDACTED'),  # Google API
        (r'ghp_[a-zA-Z0-9]{36,}', 'GITHUB_TOKEN_REDACTED'),  # GitHub
        (r'ghs_[a-zA-Z0-9]{36,}', 'GITHUB_SECRET_REDACTED'),  # GitHub secret
        (r'pk_test_[a-zA-Z0-9]{24,}', 'STRIPE_TEST_KEY_REDACTED'),  # Stripe test
        (r'pk_live_[a-zA-Z0-9]{24,}', 'STRIPE_LIVE_KEY_REDACTED'),  # Stripe live
        (r'sk_test_[a-zA-Z0-9]{24,}', 'STRIPE_TEST_SECRET_REDACTED'),  # Stripe test secret
        (r'sk_live_[a-zA-Z0-9]{24,}', 'STRIPE_LIVE_SECRET_REDACTED'),  # Stripe live secret
        (r'xox[baprs]-[0-9]{10,13}-[a-zA-Z0-9]{24,}', 'SLACK_TOKEN_REDACTED'),  # Slack
        (r'postgres(ql)?://[^@]+:[^@]+@[^/]+/[^?]+', 'DATABASE_URL_REDACTED'),  # DB URLs
        (r'mongodb(\+srv)?://[^@]+:[^@]+@[^/]+/[^?]+', 'MONGODB_URL_REDACTED'),  # MongoDB
        (r'redis://[^@]+:[^@]+@[^/]+', 'REDIS_URL_REDACTED'),  # Redis
        (r'[a-f0-9]{32}', 'POSSIBLE_HASH_REDACTED'),  # MD5 hash
        (r'[a-f0-9]{40}', 'POSSIBLE_SHA1_REDACTED'),  # SHA1 hash
        (r'[a-f0-9]{64}', 'POSSIBLE_SHA256_REDACTED'),  # SHA256 hash
        (r'npg_[a-zA-Z0-9]{8,}', 'NEON_PASSWORD_REDACTED'),  # Neon DB password
        (r'pck_[a-zA-Z0-9]{40,}', 'STACK_CLIENT_KEY_REDACTED'),  # Stack client key
        (r'ssk_[a-zA-Z0-9]{40,}', 'STACK_SERVER_KEY_REDACTED'),  # Stack server key
        (r'whsec_[a-zA-Z0-9]{32,}', 'STRIPE_WEBHOOK_SECRET_REDACTED'),  # Stripe webhook
    ]

    # If the key name suggests a secret, redact the value
    if is_secret_key:
        # Keep some structure for debugging but redact the actual value
        if len(value) > 20:
            return f"REDACTED_{key_name.upper()}_VALUE"
        elif value and not value.startswith('REDACTED'):
            return "REDACTED"

    # Check for patterns in the value
    for pattern, replacement in secret_patterns:
        if re.search(pattern, value, re.IGNORECASE):
            return replacement

    # Check for base64 encoded secrets (common pattern)
    if re.match(r'^[A-Za-z0-9+/]{20,}={0,2}$', value) and len(value) > 30:
        return 'BASE64_ENCODED_SECRET_REDACTED'

    # Check for JWT tokens
    if value.count('.') == 2 and all(
        re.match(r'^[A-Za-z0-9_-]+$', part) for part in value.split('.')
    ):
        return 'JWT_TOKEN_REDACTED'

    return value


def sanitize_dict(obj, parent_key=""):
    """Recursively sanitize a dictionary."""
    if isinstance(obj, dict):
        sanitized = {}
        for key, value in obj.items():
            sanitized[key] = sanitize_dict(value, key)
        return sanitized
    elif isinstance(obj, list):
        return [sanitize_dict(item, parent_key) for item in obj]
    elif isinstance(obj, str):
        return sanitize_value(obj, parent_key)
    else:
        return obj


def sanitize_json_file(input_path, output_path=None):
    """Sanitize a JSON file."""
    input_path = Path(input_path)

    if not input_path.exists():
        print(f"Error: File {input_path} does not exist")
        return False

    if output_path is None:
        output_path = input_path.with_suffix('.sanitized.json')
    else:
        output_path = Path(output_path)

    try:
        # Read the JSON file
        with open(input_path, 'r') as f:
            data = json.load(f)

        # Sanitize the data
        sanitized_data = sanitize_dict(data)

        # Write the sanitized data
        with open(output_path, 'w') as f:
            json.dump(sanitized_data, f, indent=2)

        print(f"Successfully sanitized {input_path}")
        print(f"Output saved to {output_path}")

        # Show statistics
        original_str = json.dumps(data)
        sanitized_str = json.dumps(sanitized_data)
        redacted_count = sanitized_str.count('REDACTED')

        print(f"Statistics:")
        print(f"  - Original size: {len(original_str)} chars")
        print(f"  - Sanitized size: {len(sanitized_str)} chars")
        print(f"  - Redacted values: {redacted_count}")

        return True

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {input_path}: {e}")
        return False
    except Exception as e:
        print(f"Error processing {input_path}: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python sanitize_json_secrets.py <input_file> [output_file]")
        print("\nThis script sanitizes sensitive data from JSON files.")
        print("If no output file is specified, it creates a .sanitized.json file.")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    success = sanitize_json_file(input_file, output_file)
    sys.exit(0 if success else 1)