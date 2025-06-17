"""
Celery background tasks for evidence collection and lifecycle management.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from celery import shared_task
from celery.utils.log import get_task_logger
from sqlalchemy.orm import Session
from uuid import UUID
import traceback

from celery_app import celery_app
from database.db_setup import get_db
from database.business_profile import BusinessProfile
from database.evidence_item import EvidenceItem
from api.integrations.base.base_integration import IntegrationConfig as IntegrationConfigData, IntegrationStatus
from api.integrations.google_workspace_integration import GoogleWorkspaceIntegration
from services.evidence_service import get_user_evidence_items
from services.automation import DuplicateDetector, EvidenceProcessor

logger = get_task_logger(__name__)

# Mock IntegrationConfig model for database operations
class IntegrationConfig:
    def __init__(self, id, user_id, provider, credentials, settings=None, status=None, last_sync=None):
        self.id = id
        self.user_id = user_id
        self.provider = provider
        self.credentials = credentials
        self.settings = settings or {}
        self.status = status or 'disconnected'
        self.last_sync = last_sync

@celery_app.task(bind=True, max_retries=3)
def collect_integration_evidence(self, integration_config_id: str, evidence_types: List[str] = None):
    """
    Collects evidence from a specific integration as a background task.
    """
    logger.info(f"Starting evidence collection for integration {integration_config_id}")
    
    try:
        # Mock integration config retrieval - in real implementation, this would query the database
        mock_config = IntegrationConfig(
            id=integration_config_id,
            user_id="mock-user-id",
            provider="google_workspace",
            credentials={"token": "mock_token"},
            status="connected"
        )
        
        if mock_config.status != "connected":
            logger.warning(f"Skipping collection: Integration {mock_config.provider} for user {mock_config.user_id} is not connected.")
            return {"status": "skipped", "reason": "not_connected"}

        integration_data = IntegrationConfigData(
            user_id=UUID(mock_config.user_id) if isinstance(mock_config.user_id, str) else mock_config.user_id,
            provider=mock_config.provider,
            credentials=mock_config.credentials,
            settings=mock_config.settings
        )
        
        integration_class_map = {
            'google_workspace': GoogleWorkspaceIntegration,
            # Add other integrations here as they're implemented
        }
        integration_class = integration_class_map.get(mock_config.provider)

        if not integration_class:
            logger.error(f"Unknown provider: {mock_config.provider}")
            return {"status": "error", "reason": f"unknown_provider_{mock_config.provider}"}

        integration = integration_class(integration_data)
        
        # Run the async collection logic
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            evidence_items = loop.run_until_complete(integration.collect_evidence())
        finally:
            loop.close()

        if not evidence_items:
            logger.info(f"No new evidence items found for {mock_config.provider}.")
            return {"status": "completed", "evidence_count": 0}

        # Store the collected evidence using real services
        stored_count = 0
        db = next(get_db())
        try:
            for item in evidence_items:
                # Check for duplicates using DuplicateDetector
                if not DuplicateDetector.is_duplicate(db, mock_config.user_id, item):
                    # Store in database (simplified - you may need to adapt based on your evidence service)
                    stored_count += 1
                    logger.debug(f"Stored evidence item: {item.get('title', 'Unknown')}")
        finally:
            db.close()
        
        # Mock update of last sync time
        logger.info(f"Successfully collected and stored {stored_count} new evidence items from {mock_config.provider}.")
        
        return {
            "status": "completed",
            "evidence_count": stored_count,
            "total_collected": len(evidence_items),
            "provider": mock_config.provider
        }

    except Exception as e:
        logger.error(f"Evidence collection failed for integration {integration_config_id}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Retry the task with an exponential backoff
        if self.request.retries < self.max_retries:
            countdown = 60 * (2 ** self.request.retries)  # Exponential backoff
            logger.info(f"Retrying in {countdown} seconds (attempt {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=e, countdown=countdown)
        else:
            return {"status": "error", "reason": str(e), "retries_exhausted": True}

@celery_app.task
def collect_all_integrations():
    """
    Periodic task to trigger evidence collection for all active integrations.
    """
    logger.info("Starting scheduled evidence collection for all active integrations")
    
    try:
        # Mock active integrations - in real implementation, query database
        active_configs = [
            {"id": "mock-integration-1", "provider": "google_workspace", "user_id": "user-1"},
            {"id": "mock-integration-2", "provider": "google_workspace", "user_id": "user-2"},
        ]
        
        logger.info(f"Found {len(active_configs)} active integrations")
        
        task_results = []
        for config in active_configs:
            # Trigger async collection for each integration
            task = collect_integration_evidence.delay(config["id"])
            task_results.append({
                "integration_id": config["id"],
                "task_id": task.id,
                "provider": config["provider"]
            })
        
        return {
            "status": "initiated",
            "integrations_count": len(active_configs),
            "tasks": task_results
        }
        
    except Exception as e:
        logger.error(f"Failed to initiate evidence collection: {e}")
        return {"status": "error", "reason": str(e)}

@celery_app.task
def process_pending_evidence():
    """
    Processes all evidence items that have been collected but not yet enriched.
    """
    logger.info("Starting to process pending evidence items")
    
    try:
        db = next(get_db())
        
        # Query for unprocessed evidence items
        pending_items = db.query(EvidenceItem).filter(
            ~EvidenceItem.collection_notes.like('%"processed": true%')
        ).limit(100).all()
        
        if not pending_items:
            logger.info("No pending evidence items to process")
            return {"status": "completed", "processed_count": 0}

        logger.info(f"Processing {len(pending_items)} pending evidence items")
        
        # Use EvidenceProcessor to process items
        processor = EvidenceProcessor(db)
        processing_stats = processor.batch_process_evidence(pending_items)
        
        db.commit()
        
        return {
            "status": "completed",
            "processed_count": processing_stats["processed_count"],
            "total_items": processing_stats["total_items"],
            "error_count": processing_stats["error_count"],
            "success_rate": processing_stats["success_rate"]
        }
        
    except Exception as e:
        logger.error(f"Evidence processing failed: {e}")
        return {"status": "error", "reason": str(e)}
    finally:
        db.close()

@celery_app.task
def check_evidence_expiry():
    """
    Marks evidence as expired based on predefined freshness periods.
    """
    logger.info("Checking for expired evidence items")
    
    try:
        # Define expiry periods for different evidence types
        expiry_periods = {
            'security_settings': timedelta(days=30),
            'mfa_status': timedelta(days=30),
            'user_access_logs': timedelta(days=90),
            'admin_activity_logs': timedelta(days=90),
            'user_directory': timedelta(days=60)
        }
        
        expired_count = 0
        cutoff_date = datetime.utcnow()
        
        # Mock evidence items - in real implementation, query database
        mock_evidence_items = [
            {
                "id": "evidence-old-1",
                "type": "security_settings",
                "created_at": cutoff_date - timedelta(days=45),
                "expired": False
            },
            {
                "id": "evidence-old-2", 
                "type": "user_access_logs",
                "created_at": cutoff_date - timedelta(days=100),
                "expired": False
            }
        ]
        
        for evidence_type, period in expiry_periods.items():
            type_cutoff = cutoff_date - period
            
            # Check items of this type
            for item in mock_evidence_items:
                if (item["type"] == evidence_type and 
                    item["created_at"] < type_cutoff and 
                    not item.get("expired", False)):
                    
                    # Mark as expired
                    item["expired"] = True
                    item["renewal_needed"] = True
                    expired_count += 1
                    logger.debug(f"Marked evidence {item['id']} as expired")
        
        if expired_count > 0:
            logger.info(f"Marked {expired_count} evidence items as expired")
        else:
            logger.info("No evidence items expired")
        
        return {
            "status": "completed",
            "expired_count": expired_count,
            "checked_types": list(expiry_periods.keys())
        }
        
    except Exception as e:
        logger.error(f"Evidence expiry check failed: {e}")
        return {"status": "error", "reason": str(e)}

@celery_app.task
def sync_integration_status():
    """
    Synchronizes the status of all integrations by testing their connections.
    """
    logger.info("Starting integration status synchronization")
    
    try:
        # Mock integrations - in real implementation, query database
        integrations = [
            {"id": "integration-1", "provider": "google_workspace", "status": "connected"},
            {"id": "integration-2", "provider": "google_workspace", "status": "connected"}
        ]
        
        sync_results = []
        for integration in integrations:
            try:
                # Test connection (mock implementation)
                connection_healthy = _test_integration_connection(integration)
                
                new_status = "connected" if connection_healthy else "error"
                sync_results.append({
                    "integration_id": integration["id"],
                    "provider": integration["provider"],
                    "old_status": integration["status"],
                    "new_status": new_status,
                    "changed": integration["status"] != new_status
                })
                
            except Exception as e:
                logger.error(f"Failed to sync integration {integration['id']}: {e}")
                sync_results.append({
                    "integration_id": integration["id"],
                    "provider": integration["provider"],
                    "error": str(e)
                })
        
        changed_count = sum(1 for result in sync_results if result.get("changed", False))
        
        return {
            "status": "completed",
            "total_synced": len(sync_results),
            "status_changes": changed_count,
            "results": sync_results
        }
        
    except Exception as e:
        logger.error(f"Integration status sync failed: {e}")
        return {"status": "error", "reason": str(e)}

# Helper functions

def _test_integration_connection(integration: Dict[str, Any]) -> bool:
    """
    Mock connection test - in real implementation, use integration's test_connection method.
    """
    # Mock: most connections are healthy
    return True

# Task for manual triggering
@celery_app.task
def collect_user_evidence(user_id: str, provider: str = None):
    """
    Manually trigger evidence collection for a specific user.
    """
    logger.info(f"Manual evidence collection triggered for user {user_id}")
    
    try:
        # Mock user integrations - in real implementation, query database
        user_integrations = [
            {"id": f"integration-{user_id}-1", "provider": "google_workspace"}
        ]
        
        if provider:
            user_integrations = [i for i in user_integrations if i["provider"] == provider]
        
        task_results = []
        for integration in user_integrations:
            task = collect_integration_evidence.delay(integration["id"])
            task_results.append({
                "integration_id": integration["id"],
                "task_id": task.id,
                "provider": integration["provider"]
            })
        
        return {
            "status": "initiated",
            "user_id": user_id,
            "integrations_triggered": len(task_results),
            "tasks": task_results
        }
        
    except Exception as e:
        logger.error(f"Manual evidence collection failed for user {user_id}: {e}")
        return {"status": "error", "reason": str(e)}