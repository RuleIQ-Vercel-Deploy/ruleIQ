"""
JWT Token Management System
Centralizes JWT token handling with secure storage and rotation
"""

import os
from typing import Optional
from datetime import datetime, timedelta
import jwt
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

class JWTManager:
    """Secure JWT token management with environment-based configuration."""

    def __init__(self):
        """Initialize JWT manager with environment variables."""
        self.secret_key = self._get_secret_key()
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
        self.refresh_token_expire = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    def _get_secret_key(self) -> str:
        """
        Retrieve JWT secret key from environment.

        Returns:
            JWT secret key

        Raises:
            ValueError: If JWT_SECRET_KEY is not set
        """
        secret_key = os.getenv("JWT_SECRET_KEY")
        if not secret_key:
            raise ValueError(
                "JWT_SECRET_KEY environment variable is required. "
                "Generate a secure key with: openssl rand -base64 32"
            )
        return secret_key

    def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token.

        Args:
            data: Payload data
            expires_delta: Optional custom expiration time

        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire)

        to_encode.update({"exp": expire, "type": "access"})

        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise

    def create_refresh_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT refresh token.

        Args:
            data: Payload data
            expires_delta: Optional custom expiration time

        Returns:
            Encoded JWT refresh token
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire)

        to_encode.update({"exp": expire, "type": "refresh"})

        try:
            encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating refresh token: {e}")
            raise

    def decode_token(self, token: str) -> dict:
        """
        Decode and validate JWT token.

        Args:
            token: JWT token to decode

        Returns:
            Decoded token payload

        Raises:
            jwt.InvalidTokenError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            raise
        except jwt.InvalidTokenError as e:
            logger.error(f"Invalid token: {e}")
            raise

    def validate_token(self, token: str, token_type: str = "access") -> bool:
        """
        Validate JWT token and check type.

        Args:
            token: JWT token to validate
            token_type: Expected token type ('access' or 'refresh')

        Returns:
            True if valid, False otherwise
        """
        try:
            payload = self.decode_token(token)
            return payload.get("type") == token_type
        except (jwt.InvalidTokenError, KeyError):
            return False

    def rotate_secret_key(self, new_secret_key: str) -> None:
        """
        Rotate JWT secret key (requires coordination with all services).

        Args:
            new_secret_key: New secret key
        """
        logger.info("Rotating JWT secret key")
        self.secret_key = new_secret_key
        # In production, this would need to update the environment variable
        # and coordinate with other services


class TokenEncryption:
    """Additional encryption layer for sensitive tokens."""

    def __init__(self):
        """Initialize token encryption with Fernet."""
        encryption_key = os.getenv("TOKEN_ENCRYPTION_KEY")
        if not encryption_key:
            raise ValueError(
                "TOKEN_ENCRYPTION_KEY environment variable is required. "
                "Generate with: from cryptography.fernet import Fernet; print(Fernet.generate_key())"
            )
        self.cipher = Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)

    def encrypt_token(self, token: str) -> str:
        """
        Encrypt a token for storage.

        Args:
            token: Plain text token

        Returns:
            Encrypted token
        """
        return self.cipher.encrypt(token.encode()).decode()

    def decrypt_token(self, encrypted_token: str) -> str:
        """
        Decrypt a stored token.

        Args:
            encrypted_token: Encrypted token

        Returns:
            Decrypted plain text token
        """
        return self.cipher.decrypt(encrypted_token.encode()).decode()


# Global instance for application use
jwt_manager = JWTManager()
token_encryption = TokenEncryption() if os.getenv("TOKEN_ENCRYPTION_KEY") else None