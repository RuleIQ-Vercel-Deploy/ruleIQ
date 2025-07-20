#!/usr/bin/env python3
"""
Generate a secure JWT secret key
"""

import secrets
import base64
import string

print("JWT Secret Key Generator")
print("="*50)

# Method 1: Using secrets (Recommended)
print("\nMethod 1 - Cryptographically secure random bytes (Recommended):")
secret_bytes = secrets.token_bytes(32)  # 256 bits
secret_b64 = base64.b64encode(secret_bytes).decode('utf-8')
print(f"JWT_SECRET={secret_b64}")

# Method 2: URL-safe string
print("\nMethod 2 - URL-safe string:")
secret_urlsafe = secrets.token_urlsafe(32)
print(f"JWT_SECRET={secret_urlsafe}")

# Method 3: Alphanumeric string
print("\nMethod 3 - Alphanumeric string:")
alphabet = string.ascii_letters + string.digits
secret_alphanumeric = ''.join(secrets.choice(alphabet) for _ in range(64))
print(f"JWT_SECRET={secret_alphanumeric}")

print("\n" + "="*50)
print("\nInstructions:")
print("1. Choose one of the generated secrets above")
print("2. Copy the entire line (including JWT_SECRET=)")
print("3. Paste it into your .env.local file")
print("4. Save the file and restart your server")
print("\nSecurity Notes:")
print("- Use a different secret for each environment (dev, staging, prod)")
print("- Never commit secrets to version control")
print("- Keep production secrets in a secure secret management system")
print("- The secret should be at least 256 bits (32 bytes) for security")
