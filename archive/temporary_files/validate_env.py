#!/usr/bin/env python3
"""
Environment file validator - checks if JWT_SECRET is properly set
without revealing the actual secret value.
"""

import os
import re
from typing import Optional


def check_env_file(filepath) -> Optional[str]:
    """Check if an env file has proper JWT_SECRET configuration."""
    if not os.path.exists(filepath):
        return f"File {filepath} does not exist"

    try:
        with open(filepath, "r") as f:
            content = f.read()

        # Check for JWT_SECRET
        jwt_pattern = r"^JWT_SECRET\s*=\s*(.+)$"
        matches = re.findall(jwt_pattern, content, re.MULTILINE)

        if not matches:
            return f"JWT_SECRET not found in {filepath}"

        secret_value = matches[0].strip()

        # Remove quotes if present
        if (secret_value.startswith('"') and secret_value.endswith('"')) or (
            secret_value.startswith("'") and secret_value.endswith("'")
        ):
            secret_value = secret_value[1:-1]

        # Check for common issues
        issues = []
        if not secret_value:
            issues.append("JWT_SECRET is empty")
        if len(secret_value) < 10:
            issues.append("JWT_SECRET is too short (less than 10 characters)")
        if " " in secret_value:
            issues.append("JWT_SECRET contains spaces")
        if secret_value in ["your-secret-key", "change-this", "secret"]:
            issues.append("JWT_SECRET uses a placeholder value")

        if issues:
            return f"JWT_SECRET found but has issues: {', '.join(issues)}"

        return f"JWT_SECRET properly configured (length: {len(secret_value)})"

    except Exception as e:
        return f"Error reading {filepath}: {e}"


# Check all possible env files
print("Environment File Validation")
print("=" * 50)

env_files = [".env", ".env.local", ".env.development", ".env.production"]

for env_file in env_files:
    result = check_env_file(env_file)
    print(f"{env_file}: {result}")

print("\nNote: This script validates the format without revealing actual secrets.")
