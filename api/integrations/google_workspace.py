"""Google Workspace integration implementation.

This module provides integration with Google Workspace services using
the google_workspace_client under the hood.
"""
from __future__ import annotations

from typing import Dict, Any, Optional, List
from datetime import datetime
from api.integrations.base import OAuthIntegration, IntegrationConfig, IntegrationResponse, IntegrationStatus
from api.clients.google_workspace_client import GoogleWorkspaceClient
from config.logging_config import get_logger

logger = get_logger(__name__)


class GoogleWorkspaceIntegration(OAuthIntegration):
    """Google Workspace integration for document and drive operations."""
    
    def __init__(self, config: IntegrationConfig):
        """Initialize Google Workspace integration."""
        super().__init__(config)
        self.client: Optional[GoogleWorkspaceClient] = None
        self.service_account_file = config.metadata.get("service_account_file")
        self.user_email = config.metadata.get("user_email")
        self.scopes = config.metadata.get("scopes", [
            'https://www.googleapis.com/auth/drive.readonly',
            'https://www.googleapis.com/auth/documents.readonly'
        ])
    
    async def connect(self) -> bool:
        """
        Establish connection to Google Workspace.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if not self.service_account_file:
                logger.error("No service account file provided")
                self.status = IntegrationStatus.ERROR
                self._last_error = "Missing service account configuration"
                return False
            
            self.client = GoogleWorkspaceClient(
                service_account_file=self.service_account_file
            )
            
            # Test connection by listing a single file
            await self.client.list_drive_files(max_results=1)
            
            self.status = IntegrationStatus.ACTIVE
            self._last_error = None
            logger.info("Successfully connected to Google Workspace")
            return True
            
        except Exception as e:
            self.status = IntegrationStatus.ERROR
            self._last_error = str(e)
            logger.error(f"Failed to connect to Google Workspace: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """
        Disconnect from Google Workspace.
        
        Returns:
            True if disconnection successful, False otherwise
        """
        try:
            if self.client:
                # Clean up any resources
                self.client = None
            
            self.status = IntegrationStatus.INACTIVE
            logger.info("Disconnected from Google Workspace")
            return True
            
        except Exception as e:
            logger.error(f"Error disconnecting from Google Workspace: {e}")
            return False
    
    async def validate_credentials(self) -> bool:
        """
        Validate Google Workspace credentials.
        
        Returns:
            True if credentials are valid, False otherwise
        """
        try:
            if not self.client:
                await self.connect()
            
            if self.client:
                # Try to list files to validate credentials
                await self.client.list_drive_files(max_results=1)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Credential validation failed: {e}")
            return False
    
    async def sync_data(self) -> IntegrationResponse:
        """
        Sync data from Google Workspace.
        
        Returns:
            IntegrationResponse with sync results
        """
        try:
            if not self.client:
                await self.connect()
            
            if not self.client:
                return IntegrationResponse(
                    success=False,
                    error="Not connected to Google Workspace",
                    timestamp=datetime.utcnow()
                )
            
            # Example sync: fetch recent documents
            files = await self.client.list_drive_files(max_results=100)
            
            self._last_sync = datetime.utcnow()
            
            return IntegrationResponse(
                success=True,
                data={
                    "files_synced": len(files.get("files", [])),
                    "sync_timestamp": self._last_sync.isoformat()
                },
                timestamp=self._last_sync
            )
            
        except Exception as e:
            logger.error(f"Data sync failed: {e}")
            return IntegrationResponse(
                success=False,
                error=str(e),
                timestamp=datetime.utcnow()
            )
    
    async def get_authorization_url(self, redirect_uri: str) -> str:
        """
        Get OAuth authorization URL for Google Workspace.
        
        Args:
            redirect_uri: Redirect URI after authorization
            
        Returns:
            Authorization URL
        """
        # For service account auth, this is not needed
        # If implementing OAuth2 flow, would return the auth URL here
        raise NotImplementedError(
            "OAuth2 flow not implemented. Using service account authentication."
        )
    
    async def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code
            redirect_uri: Redirect URI used in authorization
            
        Returns:
            Token response
        """
        # For service account auth, this is not needed
        raise NotImplementedError(
            "OAuth2 flow not implemented. Using service account authentication."
        )
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh the access token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            New token response
        """
        # Service account handles token refresh automatically
        raise NotImplementedError(
            "Token refresh handled automatically by service account."
        )
    
    async def list_documents(self, folder_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List Google Docs documents.
        
        Args:
            folder_id: Optional folder ID to list documents from
            
        Returns:
            List of document metadata
        """
        if not self.client:
            await self.connect()
        
        if not self.client:
            return []
        
        try:
            query = "mimeType='application/vnd.google-apps.document'"
            if folder_id:
                query += f" and '{folder_id}' in parents"
            
            result = await self.client.search_drive_files(query=query)
            return result.get("files", [])
            
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            return []
    
    async def get_document_content(self, document_id: str) -> Optional[str]:
        """
        Get the content of a Google Doc.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Document content as text, or None if failed
        """
        if not self.client:
            await self.connect()
        
        if not self.client:
            return None
        
        try:
            content = await self.client.get_document_content(document_id)
            return content
            
        except Exception as e:
            logger.error(f"Failed to get document content: {e}")
            return None
    
    async def export_document(
        self,
        document_id: str,
        export_format: str = "text/plain"
    ) -> Optional[bytes]:
        """
        Export a Google Doc in specified format.
        
        Args:
            document_id: ID of the document
            export_format: MIME type for export format
            
        Returns:
            Exported document as bytes, or None if failed
        """
        if not self.client:
            await self.connect()
        
        if not self.client:
            return None
        
        try:
            content = await self.client.export_file(document_id, export_format)
            return content
            
        except Exception as e:
            logger.error(f"Failed to export document: {e}")
            return None


__all__ = ["GoogleWorkspaceIntegration"]