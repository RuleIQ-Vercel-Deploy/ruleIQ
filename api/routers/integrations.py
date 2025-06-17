"""
API endpoints for managing third-party integrations.
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from datetime import datetime

from database.db_setup import get_db
from api.dependencies.auth import get_current_user
from api.integrations.google_workspace_integration import GoogleWorkspaceIntegration
from api.integrations.base.base_integration import IntegrationConfig, IntegrationStatus
from sqlalchemy_access import User

router = APIRouter()

# Pydantic models for requests/responses
class IntegrationCredentials(BaseModel):
    """Model for integration credentials"""
    provider: str
    credentials: Dict[str, Any]
    settings: Optional[Dict[str, Any]] = None

class IntegrationResponse(BaseModel):
    """Response model for integration operations"""
    provider: str
    status: str
    message: Optional[str] = None
    evidence_types: Optional[List[Dict[str, Any]]] = None
    last_sync: Optional[str] = None

class EvidenceCollectionResponse(BaseModel):
    """Response model for evidence collection"""
    provider: str
    status: str
    evidence_items_collected: int
    evidence_items: Optional[List[Dict[str, Any]]] = None
    collection_time: str

class IntegrationListResponse(BaseModel):
    """Response model for listing integrations"""
    available_providers: List[Dict[str, Any]]
    configured_integrations: List[Dict[str, Any]]

# Available integration providers
AVAILABLE_PROVIDERS = {
    "google_workspace": {
        "name": "Google Workspace",
        "description": "Collect user activity logs, admin actions, and directory information",
        "evidence_types": ["user_access_logs", "admin_activity_logs", "user_directory", "access_groups"],
        "frameworks": ["SOC2", "ISO27001", "GDPR"],
        "setup_instructions": "Requires Admin API access and OAuth2 credentials"
    },
    "microsoft_365": {
        "name": "Microsoft 365",
        "description": "Collect audit logs, user activities, and security configurations",
        "evidence_types": ["audit_logs", "security_events", "user_activities"],
        "frameworks": ["SOC2", "ISO27001", "GDPR"],
        "setup_instructions": "Coming soon"
    },
    "aws": {
        "name": "Amazon Web Services",
        "description": "Collect CloudTrail logs, IAM configurations, and security findings",
        "evidence_types": ["cloudtrail_logs", "iam_configs", "security_findings"],
        "frameworks": ["SOC2", "ISO27001"],
        "setup_instructions": "Coming soon"
    }
}

@router.get("/", response_model=IntegrationListResponse, summary="List available and configured integrations")
async def list_integrations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a list of available integration providers and user's configured integrations.
    """
    # TODO: In a real implementation, fetch user's configured integrations from database
    configured_integrations = []
    
    # Mock some configured integrations for demonstration
    if current_user:
        configured_integrations = [
            {
                "provider": "google_workspace",
                "status": "connected",
                "last_sync": "2024-01-15T10:30:00Z",
                "evidence_count": 156
            }
        ]
    
    return IntegrationListResponse(
        available_providers=[
            {"provider": k, **v} for k, v in AVAILABLE_PROVIDERS.items()
        ],
        configured_integrations=configured_integrations
    )

@router.post("/connect", response_model=IntegrationResponse, summary="Connect a new integration")
async def connect_integration(
    integration_data: IntegrationCredentials,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Connect and configure a new third-party integration.
    """
    provider = integration_data.provider.lower()
    
    if provider not in AVAILABLE_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Provider '{provider}' is not supported. Available providers: {list(AVAILABLE_PROVIDERS.keys())}"
        )
    
    try:
        if provider == "google_workspace":
            # Create configuration
            config = IntegrationConfig(
                user_id=current_user.id,
                provider=provider,
                credentials=integration_data.credentials,
                settings=integration_data.settings
            )
            
            # Test the connection
            integration = GoogleWorkspaceIntegration(config)
            connection_successful = await integration.test_connection()
            
            if not connection_successful:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to connect to Google Workspace. Please check your credentials and permissions."
                )
            
            # Get supported evidence types
            evidence_types = await integration.get_supported_evidence_types()
            
            # TODO: Save the configuration to database (encrypted)
            # For now, we'll simulate success
            
            return IntegrationResponse(
                provider=provider,
                status="connected",
                message="Successfully connected to Google Workspace",
                evidence_types=evidence_types
            )
        
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Integration for '{provider}' is not yet implemented"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to connect integration: {str(e)}"
        )

@router.post("/{provider}/test", response_model=IntegrationResponse, summary="Test integration connection")
async def test_integration(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Test the connection to a configured integration.
    """
    provider = provider.lower()
    
    if provider not in AVAILABLE_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider}' not found"
        )
    
    # TODO: Fetch user's saved configuration from database
    # For now, simulate with mock credentials
    mock_credentials = {"token": "mock_token", "refresh_token": "mock_refresh"}
    
    try:
        if provider == "google_workspace":
            config = IntegrationConfig(
                user_id=current_user.id,
                provider=provider,
                credentials=mock_credentials
            )
            
            integration = GoogleWorkspaceIntegration(config)
            connection_successful = await integration.test_connection()
            
            return IntegrationResponse(
                provider=provider,
                status="connected" if connection_successful else "error",
                message="Connection test successful" if connection_successful else "Connection test failed"
            )
        
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Testing for '{provider}' is not yet implemented"
            )
            
    except Exception as e:
        return IntegrationResponse(
            provider=provider,
            status="error",
            message=f"Connection test failed: {str(e)}"
        )

@router.post("/{provider}/collect", response_model=EvidenceCollectionResponse, summary="Trigger evidence collection")
async def collect_evidence(
    provider: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger evidence collection from the specified integration provider.
    """
    provider = provider.lower()
    
    if provider not in AVAILABLE_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider}' not found"
        )
    
    # TODO: Fetch user's saved configuration from database
    # For now, simulate with mock credentials
    mock_credentials = {"token": "mock_token", "refresh_token": "mock_refresh"}
    
    try:
        if provider == "google_workspace":
            config = IntegrationConfig(
                user_id=current_user.id,
                provider=provider,
                credentials=mock_credentials,
                status=IntegrationStatus.CONNECTED
            )
            
            integration = GoogleWorkspaceIntegration(config)
            
            # Collect evidence
            collected_evidence = await integration.collect_evidence()
            
            # TODO: Save collected evidence to database
            # For now, we'll just return the count and sample data
            
            return EvidenceCollectionResponse(
                provider=provider,
                status="completed",
                evidence_items_collected=len(collected_evidence),
                evidence_items=collected_evidence[:3],  # Return first 3 items as sample
                collection_time=datetime.utcnow().isoformat()
            )
        
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Evidence collection for '{provider}' is not yet implemented"
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evidence collection failed: {str(e)}"
        )

@router.get("/{provider}/evidence-types", summary="Get supported evidence types")
async def get_evidence_types(
    provider: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get the evidence types supported by the specified provider.
    """
    provider = provider.lower()
    
    if provider not in AVAILABLE_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider}' not found"
        )
    
    try:
        if provider == "google_workspace":
            # Create a temporary integration to get evidence types
            config = IntegrationConfig(
                user_id=current_user.id,
                provider=provider,
                credentials={}  # Empty credentials for metadata only
            )
            
            integration = GoogleWorkspaceIntegration(config)
            evidence_types = await integration.get_supported_evidence_types()
            
            return {
                "provider": provider,
                "evidence_types": evidence_types
            }
        
        else:
            # Return static information for other providers
            provider_info = AVAILABLE_PROVIDERS[provider]
            return {
                "provider": provider,
                "evidence_types": [
                    {
                        "type": evidence_type,
                        "title": evidence_type.replace('_', ' ').title(),
                        "description": f"Evidence collection for {evidence_type}",
                        "frameworks": provider_info["frameworks"],
                        "status": "coming_soon"
                    }
                    for evidence_type in provider_info["evidence_types"]
                ]
            }
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get evidence types: {str(e)}"
        )

@router.delete("/{provider}", summary="Disconnect integration")
async def disconnect_integration(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disconnect and remove an integration configuration.
    """
    provider = provider.lower()
    
    if provider not in AVAILABLE_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider}' not found"
        )
    
    # TODO: Remove the integration configuration from database
    # For now, simulate success
    
    return {
        "provider": provider,
        "status": "disconnected",
        "message": f"Successfully disconnected {provider} integration"
    }

@router.get("/{provider}/status", response_model=IntegrationResponse, summary="Get integration status")
async def get_integration_status(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the current status of an integration.
    """
    provider = provider.lower()
    
    if provider not in AVAILABLE_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Provider '{provider}' not found"
        )
    
    # TODO: Fetch actual status from database
    # For now, return mock status
    
    return IntegrationResponse(
        provider=provider,
        status="connected",
        message="Integration is active and collecting evidence",
        last_sync="2024-01-15T10:30:00Z"
    )