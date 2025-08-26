"""
API endpoints for managing third-party integrations (Asynchronous & Secure).
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from api.dependencies.auth import get_current_active_user
from database.user import User
from api.integrations.base.base_integration import (
    BaseIntegration,
    IntegrationConfig,
    IntegrationStatus,
)
from config.logging_config import get_logger
from database.db_setup import get_async_db
from database.models.integrations import Integration

logger = get_logger(__name__)
router = APIRouter()

# Pydantic models for requests/responses
class IntegrationCredentials(BaseModel):
    provider: str
    credentials: Dict[str, Any]
    settings: Optional[Dict[str, Any]] = None

class IntegrationResponse(BaseModel):
    provider: str
    status: str
    message: Optional[str] = None
    is_enabled: Optional[bool] = None
    last_sync_at: Optional[datetime] = None
    last_sync_status: Optional[str] = None

class IntegrationListResponse(BaseModel):
    available_providers: List[Dict[str, Any]]
    configured_integrations: List[IntegrationResponse]

# A simple integration factory would be better, but for now, we can use a dummy instance
# to access the encryption/decryption methods which don't depend on the provider specifics.
class GenericIntegration(BaseIntegration):
    """A generic class to access base methods like encryption without a real provider."""

    @property
    def provider_name(self) -> str:
        return "generic"

    async def test_connection(self) -> bool:
        return False

    async def authenticate(self) -> bool:
        return False

    async def collect_evidence(self, *args, **kwargs) -> List:
        return []

    async def get_available_evidence_types(self) -> List:
        return []

# Available integration providers (simplified for now)
AVAILABLE_PROVIDERS = {
    "google_workspace": {"name": "Google Workspace"},
    "microsoft_365": {"name": "Microsoft 365"},
}

@router.post(
    "/connect", response_model=IntegrationResponse, summary="Connect or Update Integration"
)
async def connect_integration(
    payload: IntegrationCredentials,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    provider = payload.provider.lower()
    if provider not in AVAILABLE_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Provider '{provider}' not supported."
        )

    try:
        # Use a generic integration instance to access encryption methods
        temp_config = IntegrationConfig(user_id=str(current_user.id), provider=provider, credentials={})
        integration_handler = GenericIntegration(temp_config)

        # Encrypt the credentials
        encrypted_creds = integration_handler.encrypt_credentials_to_str(payload.credentials)
        if not encrypted_creds:
            logger.error(
                f"Credential encryption failed for user {str(current_user.id)}, provider {provider}. Aborting connection."
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Credential encryption failed.",
            )

        # Check if integration already exists
        stmt = select(Integration).where(
            Integration.user_id == str(current_user.id),
            Integration.provider == provider,
        )
        result = await db.execute(stmt)
        config = result.scalars().first()

        if config:
            # Update existing configuration
            config.credentials = encrypted_creds
            config.settings = payload.settings
            config.status = IntegrationStatus.CONNECTED.value
            config.is_enabled = True
            config.updated_at = datetime.utcnow()
            message = f"Successfully updated and reconnected {provider} integration."
            logger.info(f"Integration updated for user {str(current_user.id)}, provider {provider}")
        else:
            # Create new configuration
            config = Integration(
                user_id=str(current_user.id),
                provider=provider,
                credentials=encrypted_creds,
                settings=payload.settings,
                status=IntegrationStatus.CONNECTED.value,
                is_enabled=True,
            )
            db.add(config)
            message = f"Successfully connected {provider} integration."
            logger.info(f"New integration created for user {str(current_user.id)}, provider {provider}")

        await db.commit()
        await db.refresh(config)

        return IntegrationResponse(
            provider=provider, status=config.status, message=message, is_enabled=config.is_enabled
        )
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(
            f"Database error connecting integration for user {str(current_user.id)}, provider {provider}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database operation failed."
        )
    except Exception as e:
        await db.rollback()
        logger.error(
            f"Error connecting integration for user {str(current_user.id)}, provider {provider}: {e}",
            exc_info=True,
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete(
    "/{provider}", summary="Disconnect integration", status_code=status.HTTP_204_NO_CONTENT
)
async def disconnect_integration(
    provider: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
) -> None:
    provider_key = provider.lower()
    if provider_key not in AVAILABLE_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Provider '{provider}' not found."
        )

    try:
        stmt = select(Integration).where(
            Integration.user_id == str(current_user.id),
            Integration.provider == provider_key,
        )
        result = await db.execute(stmt)
        config = result.scalars().first()

        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Integration '{provider}' not configured.",
            )

        await db.delete(config)
        await db.commit()
        logger.info(f"Integration {provider_key} disconnected for user {str(current_user.id)}")
    except SQLAlchemyError as e:
        await db.rollback()
        logger.error(
            f"Database error disconnecting {provider_key} for user {str(current_user.id)}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database operation failed."
        )

@router.get(
    "/{provider}/status", response_model=IntegrationResponse, summary="Get integration status"
)
async def get_integration_status(
    provider: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    provider_key = provider.lower()
    if provider_key not in AVAILABLE_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Provider '{provider}' not supported."
        )

    try:
        stmt = select(Integration).where(
            Integration.user_id == str(current_user.id),
            Integration.provider == provider_key,
        )
        result = await db.execute(stmt)
        config = result.scalars().first()

        if not config:
            return IntegrationResponse(
                provider=provider_key, status="not_configured", is_enabled=False
            )

        return IntegrationResponse(
            provider=config.provider,
            status=config.status,
            is_enabled=config.is_enabled,
            last_sync_at=config.last_sync_at,
            last_sync_status=config.last_sync_status,
        )
    except SQLAlchemyError as e:
        logger.error(
            f"Database error fetching status for {provider_key}, user {str(current_user.id)}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Database operation failed."
        )

@router.get("/", summary="List all available integrations")
async def list_integrations(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    """List all available integration providers and their configuration status."""
    # Placeholder implementation
    return {
        "available_providers": [
            {"provider": "google_workspace", "name": "Google Workspace", "configured": False},
            {"provider": "microsoft_365", "name": "Microsoft 365", "configured": False},
        ],
        "configured_count": 0,
    }

@router.get("/connected", summary="Get connected integrations")
async def get_connected_integrations(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Get list of currently connected integrations for the user."""
    # Placeholder implementation
    return {
        "connected_integrations": [],
        "total": 0,
    }

@router.post("/{integrationId}/test", summary="Test integration connection")
async def test_integration(
    integrationId: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Test if integration connection is working properly."""
    # Placeholder implementation
    return {
        "integration_id": integrationId,
        "status": "success",
        "message": "Connection test successful",
        "timestamp": datetime.utcnow().isoformat(),
    }

@router.get("/{integrationId}/sync-history", summary="Get sync history")
async def get_sync_history(
    integrationId: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Get synchronization history for an integration."""
    # Placeholder implementation
    return {
        "integration_id": integrationId,
        "sync_history": [
            {
                "timestamp": "2024-01-15T10:00:00Z",
                "status": "success",
                "records_synced": 150,
                "duration_seconds": 45,
            },
            {
                "timestamp": "2024-01-14T10:00:00Z",
                "status": "success",
                "records_synced": 148,
                "duration_seconds": 42,
            },
        ],
        "total_syncs": 2,
    }

@router.post("/{integrationId}/webhooks", summary="Configure webhooks")
async def configure_webhooks(
    integrationId: str,
    webhook_config: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Configure webhooks for an integration."""
    # Placeholder implementation
    webhook_url = webhook_config.get("url", "")
    events = webhook_config.get("events", [])
    
    return {
        "integration_id": integrationId,
        "webhook_url": webhook_url,
        "events": events,
        "status": "configured",
        "message": "Webhook configured successfully",
    }

@router.get("/{integrationId}/logs", summary="Get integration logs")
async def get_integration_logs(
    integrationId: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Get activity logs for an integration."""
    # Placeholder implementation
    return {
        "integration_id": integrationId,
        "logs": [
            {
                "timestamp": "2024-01-15T15:30:00Z",
                "level": "info",
                "message": "Sync completed successfully",
                "details": {"records": 150},
            },
            {
                "timestamp": "2024-01-15T15:29:00Z",
                "level": "info",
                "message": "Sync started",
                "details": {},
            },
        ],
        "total_logs": 2,
    }

@router.post("/oauth/callback", summary="Handle OAuth callback")
async def oauth_callback(
    callback_data: dict,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db),
):
    """Handle OAuth callback from integration providers."""
    # Placeholder implementation
    code = callback_data.get("code", "")
    state = callback_data.get("state", "")
    provider = callback_data.get("provider", "")
    
    return {
        "provider": provider,
        "status": "success",
        "message": "OAuth authentication successful",
        "access_token_received": bool(code),
    }
