"""
Enterprise-grade credential encryption system for ruleIQ
Implements AES-256 encryption with proper key derivation and security practices
"""

import os
import json
import base64
import hashlib
import secrets
from typing import Dict, Any, Optional
from datetime import datetime

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from config.logging_config import get_logger

logger = get_logger(__name__)


class CredentialEncryptionError(Exception):
    """Base exception for credential encryption errors"""

    pass


class InvalidEncryptionKeyError(CredentialEncryptionError):
    """Raised when encryption key is invalid or missing"""

    pass


class CredentialDecryptionError(CredentialEncryptionError):
    """Raised when credential decryption fails"""

    pass


class CredentialEncryption:
    """
    Enterprise-grade credential encryption system

    Features:
    - AES-256 encryption with Fernet (includes HMAC for integrity)
    - PBKDF2 key derivation with configurable iterations
    - Salt-based encryption for unique keys per deployment
    - Automatic key rotation support
    - Secure key management with environment variables
    - Comprehensive error handling and logging
    """

    # Security configuration
    DEFAULT_ITERATIONS = 100000  # PBKDF2 iterations
    MIN_KEY_LENGTH = 32  # Minimum master key length
    SALT_LENGTH = 32  # Salt length for key derivation

    def __init__(
        self, master_key: Optional[str] = None, salt: Optional[bytes] = None
    ) -> None:
        """
        Initialize credential encryption system

        Args:
            master_key: Master encryption key (if None, reads from environment)
            salt: Salt for key derivation (if None, generates from deployment config)
        """
        self.master_key = master_key or self._get_master_key()
        self.salt = salt or self._get_deployment_salt()
        self.encryption_key = self._derive_encryption_key()
        self.cipher = Fernet(self.encryption_key)

        logger.info("Credential encryption system initialized")

    def _get_master_key(self) -> str:
        """Get master encryption key from environment"""
        master_key = os.environ.get("CREDENTIAL_MASTER_KEY")

        if not master_key:
            raise InvalidEncryptionKeyError(
                "CREDENTIAL_MASTER_KEY environment variable is required. "
                'Generate with: python -c "import secrets; print(secrets.token_urlsafe(32))"'
            )

        if len(master_key) < self.MIN_KEY_LENGTH:
            raise InvalidEncryptionKeyError(
                f"Master key must be at least {self.MIN_KEY_LENGTH} characters long"
            )

        return master_key

    def _get_deployment_salt(self) -> bytes:
        """
        Get deployment-specific salt for key derivation
        This ensures each deployment has unique encryption keys
        """
        # Use environment variable for salt if available
        salt_env = os.environ.get("DEPLOYMENT_SALT")
        if salt_env:
            try:
                return base64.b64decode(salt_env)
            except Exception:
                logger.warning("Invalid DEPLOYMENT_SALT format, generating new salt")

        # Generate cryptographically secure salt
        deployment_id = os.environ.get("DEPLOYMENT_ID", "default-deployment")
        salt = secrets.token_bytes(32)

        # In production, this should be stored in secure key management
        logger.warning(
            (
                f"Generated new deployment salt for {deployment_id} - "
                "store securely in DEPLOYMENT_SALT env var"
            )
        )
        return salt

    def _derive_encryption_key(self) -> bytes:
        """Derive encryption key using PBKDF2"""
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,  # 256 bits
                salt=self.salt,
                iterations=self.DEFAULT_ITERATIONS,
            )

            derived_key = kdf.derive(self.master_key.encode())
            return base64.urlsafe_b64encode(derived_key)

        except Exception as e:
            raise InvalidEncryptionKeyError(f"Failed to derive encryption key: {e}")

    def encrypt_credentials(self, credentials: Dict[str, Any]) -> str:
        """
        Encrypt credential dictionary to base64 string

        Args:
            credentials: Dictionary containing sensitive credential data

        Returns:
            Base64-encoded encrypted string suitable for database storage

        Raises:
            CredentialEncryptionError: If encryption fails
        """
        try:
            # Validate input
            if not isinstance(credentials, dict):
                raise ValueError("Credentials must be a dictionary")

            if not credentials:
                raise ValueError("Credentials cannot be empty")

            # Add metadata for versioning and integrity
            credential_package = {
                "version": "1.0",
                "encrypted_at": datetime.utcnow().isoformat(),
                "checksum": self._calculate_checksum(credentials),
                "data": credentials,
            }

            # Serialize to JSON
            cred_json = json.dumps(
                credential_package, sort_keys=True, separators=(",", ":")
            )

            # Encrypt using Fernet (includes HMAC for integrity)
            encrypted_bytes = self.cipher.encrypt(cred_json.encode("utf-8"))

            # Return base64 encoded string for database storage
            encrypted_b64 = base64.urlsafe_b64encode(encrypted_bytes).decode("ascii")

            logger.debug(
                "Credentials encrypted successfully",
                extra={"credential_count": len(credentials)},
            )

            return encrypted_b64

        except Exception as e:
            logger.error(f"Failed to encrypt credentials: {e}")
            raise CredentialEncryptionError(f"Encryption failed: {e}")

    def decrypt_credentials(self, encrypted_creds: str) -> Dict[str, Any]:
        """
        Decrypt base64 string back to credential dictionary

        Args:
            encrypted_creds: Base64-encoded encrypted credential string

        Returns:
            Dictionary containing decrypted credential data

        Raises:
            CredentialDecryptionError: If decryption fails
        """
        try:
            # Validate input
            if not encrypted_creds or not isinstance(encrypted_creds, str):
                raise ValueError("Encrypted credentials must be a non-empty string")

            # Decode from base64
            try:
                encrypted_bytes = base64.urlsafe_b64decode(
                    encrypted_creds.encode("ascii")
                )
            except Exception as e:
                raise ValueError(f"Invalid base64 encoding: {e}")

            # Decrypt using Fernet
            try:
                decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            except InvalidToken:
                raise CredentialDecryptionError(
                    "Invalid encryption token - credentials may be corrupted or key changed"
                )

            # Parse JSON
            try:
                credential_package = json.loads(decrypted_bytes.decode("utf-8"))
            except Exception as e:
                raise ValueError(f"Invalid JSON in decrypted data: {e}")

            # Validate package structure
            if not isinstance(credential_package, dict):
                raise ValueError("Decrypted data is not a valid credential package")

            if "data" not in credential_package:
                raise ValueError("Missing 'data' field in credential package")

            credentials = credential_package["data"]

            # Verify integrity if checksum is present
            if "checksum" in credential_package:
                expected_checksum = credential_package["checksum"]
                actual_checksum = self._calculate_checksum(credentials)

                if expected_checksum != actual_checksum:
                    raise CredentialDecryptionError("Credential integrity check failed")

            logger.debug(
                "Credentials decrypted successfully",
                extra={"credential_count": len(credentials)},
            )

            return credentials

        except CredentialDecryptionError:
            raise
        except Exception as e:
            logger.error(f"Failed to decrypt credentials: {e}")
            raise CredentialDecryptionError(f"Decryption failed: {e}")

    def _calculate_checksum(self, credentials: Dict[str, Any]) -> str:
        """Calculate SHA-256 checksum for credential integrity verification"""
        try:
            # Create deterministic JSON representation
            cred_json = json.dumps(credentials, sort_keys=True, separators=(",", ":"))

            # Calculate SHA-256 hash
            checksum = hashlib.sha256(cred_json.encode("utf-8")).hexdigest()

            return checksum

        except Exception as e:
            logger.warning(f"Failed to calculate credential checksum: {e}")
            return ""

    def rotate_encryption_key(self, new_master_key: str) -> "CredentialEncryption":
        """
        Create new encryption instance with rotated key
        Used for key rotation scenarios

        Args:
            new_master_key: New master encryption key

        Returns:
            New CredentialEncryption instance with rotated key
        """
        try:
            logger.info("Rotating encryption key")

            new_encryption = CredentialEncryption(
                master_key=new_master_key,
                salt=self.salt,  # Keep same salt for consistent derivation
            )

            logger.info("Encryption key rotated successfully")
            return new_encryption

        except Exception as e:
            logger.error(f"Failed to rotate encryption key: {e}")
            raise CredentialEncryptionError(f"Key rotation failed: {e}")

    def verify_encryption_health(self) -> Dict[str, Any]:
        """
        Verify encryption system health by performing test encryption/decryption

        Returns:
            Health status dictionary
        """
        try:
            # Test encryption/decryption with sample data
            test_data = {
                "test_key": "test_value",
                "timestamp": datetime.utcnow().isoformat(),
            }

            start_time = datetime.utcnow()

            # Test encryption
            encrypted = self.encrypt_credentials(test_data)

            # Test decryption
            decrypted = self.decrypt_credentials(encrypted)

            end_time = datetime.utcnow()

            # Verify data integrity
            if decrypted != test_data:
                raise CredentialEncryptionError(
                    "Test data mismatch after encryption/decryption"
                )

            response_time = (end_time - start_time).total_seconds()

            return {
                "status": "healthy",
                "response_time": response_time,
                "encryption_algorithm": "AES-256",
                "key_derivation": "PBKDF2-SHA256",
                "iterations": self.DEFAULT_ITERATIONS,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Encryption health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }


# Global encryption instance
_encryption_instance: Optional[CredentialEncryption] = None


def get_credential_encryption() -> CredentialEncryption:
    """
    Get global credential encryption instance (singleton pattern)

    Returns:
        CredentialEncryption instance
    """
    global _encryption_instance

    if _encryption_instance is None:
        _encryption_instance = CredentialEncryption()

    return _encryption_instance


def encrypt_credentials(credentials: Dict[str, Any]) -> str:
    """
    Convenience function to encrypt credentials using global instance

    Args:
        credentials: Dictionary containing credential data

    Returns:
        Encrypted credential string
    """
    encryption = get_credential_encryption()
    return encryption.encrypt_credentials(credentials)


def decrypt_credentials(encrypted_creds: str) -> Dict[str, Any]:
    """
    Convenience function to decrypt credentials using global instance

    Args:
        encrypted_creds: Encrypted credential string

    Returns:
        Decrypted credential dictionary
    """
    encryption = get_credential_encryption()
    return encryption.decrypt_credentials(encrypted_creds)


def verify_encryption_health() -> Dict[str, Any]:
    """
    Convenience function to verify encryption health

    Returns:
        Health status dictionary
    """
    encryption = get_credential_encryption()
    return encryption.verify_encryption_health()
