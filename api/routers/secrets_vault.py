"""
🔐 SecretsVault API Router - Easily Identifiable Vault Management

This router provides endpoints for managing and monitoring the SecretsVault
integration with AWS Secrets Manager. Includes health checks, status monitoring,
and vault management operations.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from api.dependencies.auth import get_current_active_user
from config.settings import settings
from database.user import User

logger = logging.getLogger(__name__)

# Create router with clear identification
router = APIRouter(
    prefix="/api/v1/api/v1/secrets-vault",
    tags=["🔐 Secrets Vault"],
    responses={
        404: {"description": "SecretsVault not found"},
        500: {"description": "Vault operation failed"},
    },
)

class VaultHealthResponse(BaseModel):
    """SecretsVault health check response model"""
    status: str
    enabled: bool
    vault_type: str
    region: Optional[str] = None
    secret_name: Optional[str] = None
    message: str
    timestamp: Optional[str] = None

class VaultStatusResponse(BaseModel):
    """SecretsVault status response model"""
    vault_available: bool
    vault_enabled: bool
    configuration: Dict[str, Any]
    health: Dict[str, Any]
    integration_active: bool

async def get_vault_health(
    current_user: User = Depends(get_current_active_user)
) -> VaultHealthResponse:
    """
    🔐 Check SecretsVault health status
    
    Returns comprehensive health information for the SecretsVault integration
    including connectivity, configuration, and operational status for the
    configured backend (Vercel, AWS, or Local Environment).
    
    Requires authentication.
    """
    try:
        # Get vault health from settings
        health = settings.get_secrets_vault_health()
        
        # Add timestamp
        from datetime import datetime
        health["timestamp"] = datetime.utcnow().isoformat()
        
        logger.info(f"🔐 Vault health check requested by user {current_user.email}")
        logger.debug(f"🔐 Vault health status: {health.get('status', 'unknown')} ({health.get('vault_type', 'unknown')})")
        
        return VaultHealthResponse(**health)
        
    except Exception as e:
        logger.error(f"❌ SecretsVault health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "vault_health_check_failed",
                "message": f"Failed to check SecretsVault health: {str(e)}",
                "vault_type": "Multi-Platform SecretsVault"
            }
        )

@router.get("/status", response_model=VaultStatusResponse, summary="🔐 SecretsVault Status")
async def get_vault_status(
    current_user: User = Depends(get_current_active_user)
) -> VaultStatusResponse:
    """
    🔐 Get comprehensive SecretsVault status
    
    Returns detailed status information including:
    - Vault availability and configuration
    - Health check results
    - Integration status
    - Configuration settings
    
    Requires authentication.
    """
    try:
        # Check if SecretsVault module is available
        try:
            from config.secrets_vault import SECRETS_VAULT_AVAILABLE, get_secrets_vault
            vault_available = True
        except ImportError:
            vault_available = False
            
        # Get health information
        health = settings.get_secrets_vault_health()
        
        # Prepare configuration info (safe values only)
        configuration = {
            "enabled": settings.secrets_vault_enabled,
            "region": settings.secrets_vault_region,
            "secret_name": settings.secrets_vault_name,
            "environment": settings.environment.value,
        }
        
        # Determine integration status
        integration_active = (
            vault_available and 
            settings.secrets_vault_enabled and 
            health.get("status") in ["healthy", "disabled"]
        )
        
        status_data = VaultStatusResponse(
            vault_available=vault_available,
            vault_enabled=settings.secrets_vault_enabled,
            configuration=configuration,
            health=health,
            integration_active=integration_active
        )
        
        logger.info(f"🔐 Vault status check requested by user {current_user.email}")
        logger.debug(f"🔐 Integration active: {integration_active}")
        
        return status_data
        
    except Exception as e:
        logger.error(f"❌ SecretsVault status check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "vault_status_check_failed",
                "message": f"Failed to get SecretsVault status: {str(e)}",
            }
        )

async def test_vault_connection(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    🔐 Test SecretsVault connection and basic operations
    
    Performs a basic connectivity test to the configured SecretsVault backend
    (Vercel, AWS, or Local Environment) without retrieving sensitive data.
    
    Requires authentication.
    """
    try:
        from config.secrets_vault import get_secrets_vault
        
        # Get vault instance
        vault = get_secrets_vault()
        
        # Perform health check
        health = vault.health_check()
        
        # Determine vault type for display
        vault_type_display = health.get("vault_type", "Unknown")
        backend = health.get("backend", "unknown")
        
        # Try to check if vault is responsive (without retrieving secrets)
        test_result = {
            "connection_test": "completed",
            "vault_type": vault_type_display,
            "backend": backend,
            "health_status": health.get("status", "unknown"),
            "connectivity": health.get("status") == "healthy",
            "message": health.get("message", "No message available"),
        }
        
        # Add backend-specific information
        if backend == "aws":
            test_result.update({
                "region": health.get("region", "unknown"),
                "secret_name": health.get("secret_name", "unknown")
            })
        elif backend == "vercel":
            test_result.update({
                "vercel_url": health.get("vercel_url"),
                "deployment_id": health.get("deployment_id")
            })
        
        logger.info(f"🔐 Vault connection test requested by user {current_user.email}")
        logger.info(f"🔐 Connection test result: {test_result['connectivity']} ({backend})")
        
        return {
            "status": "success",
            "message": f"SecretsVault connection test completed ({vault_type_display})",
            "test_results": test_result,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except ImportError:
        logger.warning("⚠️ SecretsVault module not available for connection test")
        raise HTTPException(
            status_code=503,
            detail={
                "error": "vault_unavailable",
                "message": "SecretsVault module is not available",
                "suggestion": "Check if secrets_vault.py is properly installed"
            }
        )
    except Exception as e:
        logger.error(f"❌ SecretsVault connection test failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "vault_connection_test_failed",
                "message": f"SecretsVault connection test failed: {str(e)}",
                "vault_type": "Multi-Platform SecretsVault"
            }
        )

async def get_vault_config(
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    🔐 Get SecretsVault configuration (safe values only)
    
    Returns non-sensitive configuration information for the SecretsVault
    integration including enabled status, backend type, and deployment info.
    
    Requires authentication.
    """
    try:
        # Check if module is available
        try:
            from config.secrets_vault import get_secrets_vault
            vault = get_secrets_vault()
            module_available = True
            backend = vault.backend
            vault_type = vault.health_check().get("vault_type", "Unknown")
        except ImportError:
            module_available = False
            backend = "unavailable"
            vault_type = "Module Not Available"
        
        config_data = {
            "vault_integration": "Multi-Platform SecretsVault",
            "enabled": settings.secrets_vault_enabled,
            "backend": backend,
            "vault_type": vault_type,
            "environment": settings.environment.value,
            "module_available": module_available,
        }
        
        # Add backend-specific configuration
        if backend == "aws":
            config_data.update({
                "region": settings.secrets_vault_region,
                "secret_name": settings.secrets_vault_name,
            })
        elif backend == "vercel":
            config_data.update({
                "deployment_platform": "Vercel",
                "environment_variables": "Managed via Vercel Dashboard"
            })
        else:
            config_data.update({
                "environment_variables": "Local .env files"
            })
            
        logger.info(f"🔐 Vault config requested by user {current_user.email}")
        logger.debug(f"🔐 Vault backend: {backend}, type: {vault_type}")
        
        return {
            "status": "success",
            "message": "SecretsVault configuration retrieved",
            "configuration": config_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get SecretsVault configuration: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "vault_config_retrieval_failed",
                "message": f"Failed to retrieve SecretsVault configuration: {str(e)}"
            }
        )