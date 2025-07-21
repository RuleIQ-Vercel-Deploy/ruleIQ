#!/usr/bin/env python3
"""
This shows how the JWT secret was generated
"""

import secrets
import base64

# This is how your JWT secret was generated:
secret_bytes = secrets.token_bytes(32)  # 32 bytes = 256 bits
secret_b64 = base64.b64encode(secret_bytes).decode("utf-8")

print("How your JWT secret was generated:")
print("=" * 50)
print("1. Generated 32 random bytes (256 bits) using secrets.token_bytes()")
print("2. Encoded to base64 for safe storage")
print(f"3. Result: {secret_b64}")
print("\nYour actual JWT secret in .env.local:")
print("JWT_SECRET=nTDlGluRj39drsQ+IczE7pFw0okljEY/tKsLa+mB3d8=")
print("\nThis secret is:")
print("- 44 characters long")
print("- Cryptographically secure")
print("- Base64 encoded")
print("- 256 bits of entropy")
