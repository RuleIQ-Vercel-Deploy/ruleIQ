"""Base classes and interfaces for API integrations.

This module defines abstract base classes and interfaces that should be
extended by specific integration implementations.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Generic, TypeVar
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from config.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class IntegrationStatus(str, Enum):
    """Status of an integration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    CONFIGURING = "configuring"
    DISABLED = "disabled"


class IntegrationConfig(BaseModel):
    """Base configuration for integrations."""
    name: str = Field(..., description="Integration name")
    enabled: bool = Field(default=True, description="Whether integration is enabled")
    api_key: Optional[str] = Field(None, description="API key if required")
    api_secret: Optional[str] = Field(None, description="API secret if required")
    webhook_url: Optional[str] = Field(None, description="Webhook URL if applicable")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class IntegrationResponse(BaseModel):
    """Standard response from integration operations."""
    success: bool = Field(..., description="Whether operation succeeded")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if failed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")


class BaseIntegration(ABC):
    """Abstract base class for all integrations."""
    
    def __init__(self, config: IntegrationConfig):
        """Initialize integration with configuration."""
        self.config = config
        self.status = IntegrationStatus.INACTIVE
        self._last_error: Optional[str] = None
        self._last_sync: Optional[datetime] = None
    
    @abstractmethod
    async def connect(self) -> bool:
        """
        Establish connection to the integration service.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> bool:
        """
        Disconnect from the integration service.
        
        Returns:
            True if disconnection successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """
        Validate the integration credentials.
        
        Returns:
            True if credentials are valid, False otherwise
        """
        pass
    
    @abstractmethod
    async def sync_data(self) -> IntegrationResponse:
        """
        Synchronize data with the integration service.
        
        Returns:
            IntegrationResponse with sync results
        """
        pass
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get current integration status.
        
        Returns:
            Dictionary with status information
        """
        return {
            "name": self.config.name,
            "status": self.status.value,
            "enabled": self.config.enabled,
            "last_sync": self._last_sync.isoformat() if self._last_sync else None,
            "last_error": self._last_error
        }
    
    async def handle_webhook(self, payload: Dict[str, Any]) -> IntegrationResponse:
        """
        Handle incoming webhook from the integration.
        
        Args:
            payload: Webhook payload
            
        Returns:
            IntegrationResponse with processing results
        """
        logger.info(f"Webhook received for {self.config.name}: {payload}")
        return IntegrationResponse(
            success=True,
            data={"message": "Webhook processed"},
            timestamp=datetime.utcnow()
        )


class DataSyncIntegration(BaseIntegration):
    """Base class for integrations that sync data."""
    
    @abstractmethod
    async def fetch_records(self, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Fetch records from the integration service.
        
        Args:
            since: Optional datetime to fetch records since
            
        Returns:
            List of records
        """
        pass
    
    @abstractmethod
    async def push_records(self, records: List[Dict[str, Any]]) -> IntegrationResponse:
        """
        Push records to the integration service.
        
        Args:
            records: Records to push
            
        Returns:
            IntegrationResponse with push results
        """
        pass
    
    async def sync_data(self) -> IntegrationResponse:
        """
        Synchronize data bidirectionally.
        
        Returns:
            IntegrationResponse with sync results
        """
        try:
            # Fetch new records
            records = await self.fetch_records(since=self._last_sync)
            
            # Process and push if needed
            # This is a placeholder implementation
            
            self._last_sync = datetime.utcnow()
            self.status = IntegrationStatus.ACTIVE
            
            return IntegrationResponse(
                success=True,
                data={"records_synced": len(records)},
                timestamp=self._last_sync
            )
        except Exception as e:
            self._last_error = str(e)
            self.status = IntegrationStatus.ERROR
            logger.error(f"Data sync failed for {self.config.name}: {e}")
            return IntegrationResponse(
                success=False,
                error=str(e),
                timestamp=datetime.utcnow()
            )


class OAuthIntegration(BaseIntegration):
    """Base class for OAuth-based integrations."""
    
    @abstractmethod
    async def get_authorization_url(self, redirect_uri: str) -> str:
        """
        Get OAuth authorization URL.
        
        Args:
            redirect_uri: Redirect URI after authorization
            
        Returns:
            Authorization URL
        """
        pass
    
    @abstractmethod
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code
            redirect_uri: Redirect URI used in authorization
            
        Returns:
            Token response
        """
        pass
    
    @abstractmethod
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh the access token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New token response
        """
        pass


__all__ = [
    "IntegrationStatus",
    "IntegrationConfig",
    "IntegrationResponse",
    "BaseIntegration",
    "DataSyncIntegration",
    "OAuthIntegration"
]