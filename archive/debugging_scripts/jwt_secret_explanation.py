#!/usr/bin/env python3
"""
This shows how the JWT secret was generated
"""
import logging
logger = logging.getLogger(__name__)

import secrets
import base64

# This is how your JWT secret was generated:
secret_bytes = secrets.token_bytes(32)  # 32 bytes = 256 bits
secret_b64 = base64.b64encode(secret_bytes).decode("utf-8")

logger.info("How your JWT secret was generated:")
logger.info("=" * 50)
logger.info("1. Generated 32 random bytes (256 bits) using secrets.token_bytes()")
logger.info("2. Encoded to base64 for safe storage")
logger.info(f"3. Result: {secret_b64}")
logger.info("\nYour actual JWT secret in .env.local:")
logger.info("JWT_SECRET=nTDlGluRj39drsQ+IczE7pFw0okljEY/tKsLa+mB3d8=")
logger.info("\nThis secret is:")
logger.info("- 44 characters long")
logger.info("- Cryptographically secure")
logger.info("- Base64 encoded")
logger.info("- 256 bits of entropy")
