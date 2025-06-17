"""
Base integration class for all third-party integrations.
This abstract class defines the contract that all specific
integration implementations (like Google, AWS, etc.) must follow.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
import logging
from uuid import UUID

logger = logging.getLogger(__name__)

class IntegrationStatus(str, Enum):
    """Enumeration for the connection status of an integration."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    ERROR = "error"
    NEEDS_REAUTH = "needs_reauth"

@dataclass
class IntegrationConfig:
    """Dataclass to hold configuration and credentials for an integration."""
    user_id: UUID
    provider: str
    credentials: Dict[str, Any]  # Store encrypted credentials here
    settings: Optional[Dict[str, Any]] = None
    status: IntegrationStatus = IntegrationStatus.DISCONNECTED
    last_sync: Optional[datetime] = None

class BaseIntegration(ABC):
    """
    Abstract Base Class for all compliance integrations.
    It provides a common structure for authentication, testing connections,
    and collecting evidence.
    """

    def __init__(self, config: IntegrationConfig):
        self.config = config

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """The official name of the provider (e.g., 'google_workspace')."""
        pass

    @abstractmethod
    async def test_connection(self) -> bool:
        """
        Tests the connection to the provider using the stored credentials.
        Returns True if successful, False otherwise.
        """
        pass

    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Authenticates with the provider. This might involve refreshing tokens.
        Returns True if authentication is successful.
        """
        pass

    @abstractmethod
    async def collect_evidence(self) -> List[Dict[str, Any]]:
        """
        Collects all supported evidence types from the provider.
        Returns a list of standardized evidence dictionaries.
        """
        pass

    def format_evidence(
        self,
        evidence_type: str,
        title: str,
        description: str,
        raw_data: Dict,
        compliance_frameworks: List[str],
        control_mappings: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        A helper method to format collected data into a standardized
        evidence structure.
        """
        return {
            "integration_source": self.provider_name,
            "evidence_type": evidence_type,
            "title": title,
            "description": description,
            "raw_data": raw_data,
            "collected_at": datetime.utcnow(),
            "compliance_frameworks": compliance_frameworks,
            "control_mappings": control_mappings
        }

    async def get_supported_evidence_types(self) -> List[Dict[str, Any]]:
        """
        Returns a list of evidence types that this integration can collect.
        Each evidence type includes metadata about what it provides.
        """
        return []

    async def refresh_credentials(self) -> bool:
        """
        Attempts to refresh expired credentials if possible.
        Returns True if successful, False otherwise.
        """
        return await self.authenticate()

    def get_integration_info(self) -> Dict[str, Any]:
        """
        Returns metadata about this integration.
        """
        return {
            "provider": self.provider_name,
            "status": self.config.status.value,
            "last_sync": self.config.last_sync.isoformat() if self.config.last_sync else None,
            "user_id": str(self.config.user_id)
        }

    async def validate_credentials(self, credentials: Dict[str, Any]) -> bool:
        """
        Validates credentials without storing them.
        Useful for testing credentials before saving.
        """
        # Create a temporary config for testing
        temp_config = IntegrationConfig(
            user_id=self.config.user_id,
            provider=self.config.provider,
            credentials=credentials
        )
        
        # Temporarily replace config
        original_config = self.config
        self.config = temp_config
        
        try:
            result = await self.test_connection()
            return result
        finally:
            # Restore original config
            self.config = original_config

    def encrypt_credentials(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Encrypts sensitive credential data before storage.
        In a production system, this would use proper encryption.
        """
        # TODO: Implement proper encryption
        # For now, return as-is (in production, encrypt sensitive fields)
        logger.warning("Credential encryption not implemented - using plaintext storage")
        return credentials

    def decrypt_credentials(self, encrypted_credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Decrypts credential data after retrieval from storage.
        In a production system, this would use proper decryption.
        """
        # TODO: Implement proper decryption
        # For now, return as-is (in production, decrypt sensitive fields)
        return encrypted_credentials

class IntegrationError(Exception):
    """Base exception for integration-related errors."""
    pass

class AuthenticationError(IntegrationError):
    """Raised when authentication fails."""
    pass

class ConnectionError(IntegrationError):
    """Raised when connection to the provider fails."""
    pass

class EvidenceCollectionError(IntegrationError):
    """Raised when evidence collection fails."""
    pass