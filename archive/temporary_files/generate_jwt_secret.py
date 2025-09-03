#!/usr/bin/env python3
"""
Generate a secure JWT secret key
"""
import logging
logger = logging.getLogger(__name__)

import secrets
import base64
import string

logger.info("JWT Secret Key Generator")
logger.info("=" * 50)

# Method 1: Using secrets (Recommended)
logger.info("\nMethod 1 - Cryptographically secure random bytes (Recommended):")
secret_bytes = secrets.token_bytes(32)  # 256 bits
secret_b64 = base64.b64encode(secret_bytes).decode("utf-8")
logger.info(f"JWT_SECRET={secret_b64}")

# Method 2: URL-safe string
logger.info("\nMethod 2 - URL-safe string:")
secret_urlsafe = secrets.token_urlsafe(32)
logger.info(f"JWT_SECRET={secret_urlsafe}")

# Method 3: Alphanumeric string
logger.info("\nMethod 3 - Alphanumeric string:")
alphabet = string.ascii_letters + string.digits
secret_alphanumeric = "".join(secrets.choice(alphabet) for _ in range(64))
logger.info(f"JWT_SECRET={secret_alphanumeric}")

logger.info("\n" + "=" * 50)
logger.info("\nInstructions:")
logger.info("1. Choose one of the generated secrets above")
logger.info("2. Copy the entire line (including JWT_SECRET=)")
logger.info("3. Paste it into your .env.local file")
logger.info("4. Save the file and restart your server")
logger.info("\nSecurity Notes:")
logger.info("- Use a different secret for each environment (dev, staging, prod)")
logger.info("- Never commit secrets to version control")
logger.info("- Keep production secrets in a secure secret management system")
logger.info("- The secret should be at least 256 bits (32 bytes) for security")
