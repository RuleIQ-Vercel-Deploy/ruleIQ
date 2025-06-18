"""
Base integration class for all third-party integrations.
This abstract class defines the contract that all specific
integration implementations (like Google, AWS, etc.) must follow.
"""

import json
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field
from uuid import UUID

from cryptography.fernet import Fernet, InvalidToken
from config.app_config import get_cipher_suite # Import the cipher
from config.logging_config import get_logger

logger = get_logger(__name__)

class IntegrationStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    NEEDS_REAUTH = "needs_reauth"
    PENDING_VERIFICATION = "pending_verification"

@dataclass
class IntegrationConfig:
    user_id: UUID
    provider: str
    # credentials will be stored encrypted in the DB, decrypted when loaded into this model
    credentials: Dict[str, Any] 
    settings: Optional[Dict[str, Any]] = None
    status: IntegrationStatus = IntegrationStatus.DISCONNECTED
    last_sync: Optional[datetime] = None
    # To hold the raw encrypted credentials if needed for re-encryption on key rotation (advanced)
    # encrypted_credentials_str: Optional[str] = field(default=None, repr=False) 

class BaseIntegration(ABC):
    def __init__(self, config: IntegrationConfig):
        self.config = config
        self.cipher = get_cipher_suite()
        if not self.cipher:
            logger.error(
                f"Fernet cipher not available for integration {self.config.provider} for user {self.config.user_id}. "
                f"Credentials will not be encrypted/decrypted. This is a security risk."
            )

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        pass

    @abstractmethod
    async def authenticate(self) -> bool:
        pass

    @abstractmethod
    async def collect_evidence(self, evidence_type: str, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_available_evidence_types(self) -> List[Dict[str, Any]]:
        pass

    async def validate_credentials(self, credentials_to_test: Dict[str, Any]) -> bool:
        original_creds = self.config.credentials
        self.config.credentials = credentials_to_test # Temporarily set for test_connection
        try:
            result = await self.test_connection()
            return result
        except Exception as e:
            logger.error(f"Error validating credentials for {self.provider_name}: {e}", exc_info=True)
            return False
        finally:
            self.config.credentials = original_creds # Restore original

    def encrypt_credentials_to_str(self, credentials_dict: Dict[str, Any]) -> Optional[str]:
        if not self.cipher:
            logger.error("Cannot encrypt credentials: Fernet cipher is not initialized.")
            # Fallback: store as JSON string if encryption fails (highly insecure, for dev only)
            # In production, this should raise an error or prevent saving.
            logger.critical("Storing credentials as unencrypted JSON string due to missing cipher. THIS IS INSECURE.")
            return json.dumps(credentials_dict) # Insecure fallback
        
        try:
            credentials_json = json.dumps(credentials_dict)
            credentials_bytes = credentials_json.encode('utf-8')
            encrypted_bytes = self.cipher.encrypt(credentials_bytes)
            return encrypted_bytes.decode('utf-8') # Store as string (Fernet tokens are URL-safe base64)
        except Exception as e:
            logger.error(f"Failed to encrypt credentials: {e}", exc_info=True)
            return None # Or raise an error

    def decrypt_credentials_from_str(self, encrypted_credentials_str: str) -> Optional[Dict[str, Any]]:
        if not self.cipher:
            logger.error("Cannot decrypt credentials: Fernet cipher is not initialized.")
            # Attempt to parse as JSON if it might be an unencrypted fallback
            try:
                logger.warning("Attempting to parse credentials as unencrypted JSON string due to missing cipher.")
                return json.loads(encrypted_credentials_str)
            except json.JSONDecodeError:
                logger.error("Failed to parse stored credentials as JSON, and cipher is missing.")
                return None

        try:
            encrypted_bytes = encrypted_credentials_str.encode('utf-8')
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            credentials_json = decrypted_bytes.decode('utf-8')
            return json.loads(credentials_json)
        except InvalidToken:
            logger.error("Failed to decrypt credentials: Invalid Fernet token. Key might be wrong or data corrupted.")
            return None
        except Exception as e:
            logger.error(f"Failed to decrypt credentials: {e}", exc_info=True)
            return None # Or raise an error

class IntegrationError(Exception):
    pass

class AuthenticationError(IntegrationError):
    pass

class ConnectionError(IntegrationError):
    pass

class EvidenceCollectionError(IntegrationError):
    pass
