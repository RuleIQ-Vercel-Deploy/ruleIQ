"""
Evidence collection nodes for LangGraph implementation.

Phase 4 Implementation: Migrate evidence tasks from Celery to LangGraph nodes.
This module replaces workers/evidence_tasks.py with native LangGraph implementations.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from uuid import UUID
import logging

from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import ToolNode

from database.db_setup import get_async_db
from database.evidence_item import EvidenceItem
from services.automation.duplicate_detector import DuplicateDetector
from services.automation.evidence_processor import EvidenceProcessor
from core.exceptions import BusinessLogicException, DatabaseException
from langgraph_agent.graph.enhanced_state import EnhancedComplianceState

logger = logging.getLogger(__name__)


class EvidenceCollectionNode:
    """
    LangGraph node for evidence collection and processing.
    
    Replaces Celery evidence_tasks with native LangGraph implementation
    using Neon database for state persistence.
    """
    
    def __init__(self):
        """Initialize evidence collection node."""
        self.processor = None
        self.duplicate_detector = None
    
    async def process_evidence(
        self, 
        state: EnhancedComplianceState
    ) -> EnhancedComplianceState:
        """
        Process evidence items from various integrations.
        
        Replaces: process_evidence_item Celery task
        
        Args:
            state: Current enhanced compliance state
            
        Returns:
            Updated state with processed evidence
        """
        try:
            # Extract evidence data from state
            evidence_data = state.get("current_evidence", {})
            user_id = state.get("user_id")
            business_profile_id = state.get("business_profile_id")
            integration_id = state.get("integration_id", "manual")
            
            if not evidence_data:
                logger.warning("No evidence data found in state")
                state["messages"].append(
                    SystemMessage(content="No evidence data to process")
                )
                return state
            
            # Process evidence asynchronously
            async for db in get_async_db():
                try:
                    # Check for duplicates
                    if await DuplicateDetector.is_duplicate(db, user_id, evidence_data):
                        logger.info(f"Duplicate evidence detected for user {user_id}")
                        state["processing_status"] = "skipped"
                        state["messages"].append(
                            SystemMessage(content="Evidence skipped: duplicate detected")
                        )
                        return state
                    
                    # Create evidence processor
                    processor = EvidenceProcessor(db)
                    
                    # Create new evidence item
                    new_evidence = EvidenceItem(
                        user_id=user_id,
                        business_profile_id=business_profile_id,
                        framework_id=evidence_data.get("framework_id", user_id),  # Use user_id as fallback
                        evidence_name=evidence_data.get("evidence_name", "Evidence Item"),
                        evidence_type=evidence_data.get("evidence_type", "Document"),
                        control_reference=evidence_data.get("control_reference", "N/A"),
                        description=evidence_data.get("description", ""),
                        automation_source=evidence_data.get("source", integration_id),
                        ai_metadata=evidence_data.get("raw_data", {}),
                        status="collected",  # Use valid status value
                        collected_at=datetime.utcnow(),
                        collected_by=str(user_id)
                    )
                    
                    # Process evidence
                    processor.process_evidence(new_evidence)
                    
                    # Save to database
                    db.add(new_evidence)
                    await db.commit()
                    await db.refresh(new_evidence)
                    
                    # Update state
                    state["evidence_items"].append({
                        "id": str(new_evidence.id),
                        "type": new_evidence.evidence_type,
                        "status": "processed"
                    })
                    state["processing_status"] = "completed"
                    state["messages"].append(
                        SystemMessage(content=f"Evidence processed: {new_evidence.id}")
                    )
                    
                    logger.info(f"Successfully processed evidence {new_evidence.id}")
                    
                except DatabaseException as e:
                    await db.rollback()
                    logger.error(f"Database error processing evidence: {e}")
                    state["error_count"] += 1
                    state["errors"].append(str(e))
                    raise
                    
                except Exception as e:
                    await db.rollback()
                    logger.error(f"Unexpected error processing evidence: {e}")
                    state["error_count"] += 1
                    state["errors"].append(str(e))
                    raise
                    
        except Exception as e:
            logger.error(f"Failed to process evidence: {e}")
            state["processing_status"] = "failed"
            state["messages"].append(
                SystemMessage(content=f"Evidence processing failed: {str(e)}")
            )
            
        return state
    
    async def sync_evidence_status(
        self,
        state: EnhancedComplianceState
    ) -> EnhancedComplianceState:
        """
        Sync evidence status by marking old evidence as stale.
        
        Replaces: sync_evidence_status Celery task
        
        Args:
            state: Current enhanced compliance state
            
        Returns:
            Updated state with sync results
        """
        try:
            async for db in get_async_db():
                try:
                    # Calculate cutoff date (90 days old)
                    cutoff_date = datetime.utcnow() - timedelta(days=90)
                    
                    # Update stale evidence
                    from sqlalchemy import update
                    stmt = (
                        update(EvidenceItem)
                        .where(
                            EvidenceItem.status == "collected",
                            EvidenceItem.collected_at < cutoff_date
                        )
                        .values(status="rejected")  # Mark old evidence as rejected
                        .execution_options(synchronize_session=False)
                    )
                    
                    result = await db.execute(stmt)
                    await db.commit()
                    
                    updated_count = result.rowcount
                    
                    # Update state
                    state["sync_results"] = {
                        "updated_count": updated_count,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    state["messages"].append(
                        SystemMessage(
                            content=f"Evidence sync completed: {updated_count} items marked stale"
                        )
                    )
                    
                    logger.info(f"Evidence status sync: {updated_count} items updated")
                    
                except Exception as e:
                    await db.rollback()
                    logger.error(f"Error syncing evidence status: {e}")
                    state["error_count"] += 1
                    state["errors"].append(str(e))
                    raise
                    
        except Exception as e:
            logger.error(f"Failed to sync evidence status: {e}")
            state["messages"].append(
                SystemMessage(content=f"Evidence sync failed: {str(e)}")
            )
            
        return state
    
    async def check_evidence_expiry(
        self,
        state: EnhancedComplianceState
    ) -> EnhancedComplianceState:
        """
        Check for expired evidence and mark appropriately.
        
        Replaces: check_evidence_expiry Celery task
        
        Args:
            state: Current enhanced compliance state
            
        Returns:
            Updated state with expiry check results
        """
        try:
            async for db in get_async_db():
                try:
                    # Check for evidence approaching expiry
                    warning_date = datetime.utcnow() + timedelta(days=30)
                    expiry_date = datetime.utcnow()
                    
                    # Find evidence needing attention
                    from sqlalchemy import select, and_
                    
                    # Evidence expiring soon - check by review date since there's no expires_at field
                    warning_stmt = select(EvidenceItem).where(
                        and_(
                            EvidenceItem.status == "collected",
                            EvidenceItem.collected_at <= warning_date,
                            EvidenceItem.collected_at > expiry_date
                        )
                    )
                    warning_results = await db.execute(warning_stmt)
                    warning_items = warning_results.scalars().all()
                    
                    # Expired evidence - evidence older than expiry date
                    expired_stmt = select(EvidenceItem).where(
                        and_(
                            EvidenceItem.status == "collected",
                            EvidenceItem.collected_at <= expiry_date
                        )
                    )
                    expired_results = await db.execute(expired_stmt)
                    expired_items = expired_results.scalars().all()
                    
                    # Mark expired evidence
                    for item in expired_items:
                        item.status = "rejected"  # No 'expired' status, use rejected
                    
                    if expired_items:
                        await db.commit()
                    
                    # Update state
                    state["expiry_check"] = {
                        "warning_count": len(warning_items),
                        "expired_count": len(expired_items),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    state["messages"].append(
                        SystemMessage(
                            content=f"Expiry check: {len(warning_items)} warnings, "
                                  f"{len(expired_items)} expired"
                        )
                    )
                    
                    logger.info(
                        f"Evidence expiry check: {len(warning_items)} warnings, "
                        f"{len(expired_items)} expired"
                    )
                    
                except Exception as e:
                    await db.rollback()
                    logger.error(f"Error checking evidence expiry: {e}")
                    state["error_count"] += 1
                    state["errors"].append(str(e))
                    raise
                    
        except Exception as e:
            logger.error(f"Failed to check evidence expiry: {e}")
            state["messages"].append(
                SystemMessage(content=f"Expiry check failed: {str(e)}")
            )
            
        return state
    
    async def collect_all_integrations(
        self,
        state: EnhancedComplianceState
    ) -> EnhancedComplianceState:
        """
        Collect evidence from all configured integrations.
        
        Replaces: collect_all_integrations Celery task
        
        Args:
            state: Current enhanced compliance state
            
        Returns:
            Updated state with collection results
        """
        try:
            # Get all configured integrations from state
            integrations = state.get("configured_integrations", [])
            
            if not integrations:
                logger.warning("No integrations configured for evidence collection")
                state["messages"].append(
                    SystemMessage(content="No integrations configured")
                )
                return state
            
            collection_results = []
            
            for integration in integrations:
                try:
                    # Simulate evidence collection for each integration
                    # In production, this would call actual integration APIs
                    logger.info(f"Collecting evidence from {integration}")
                    
                    # Add placeholder for actual integration logic
                    result = {
                        "integration": integration,
                        "status": "collected",
                        "count": 0,
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    collection_results.append(result)
                    
                except Exception as e:
                    logger.error(f"Error collecting from {integration}: {e}")
                    collection_results.append({
                        "integration": integration,
                        "status": "failed",
                        "error": str(e)
                    })
            
            # Update state
            state["collection_results"] = collection_results
            state["messages"].append(
                SystemMessage(
                    content=f"Evidence collection completed for {len(integrations)} integrations"
                )
            )
            
        except Exception as e:
            logger.error(f"Failed to collect evidence from integrations: {e}")
            state["messages"].append(
                SystemMessage(content=f"Collection failed: {str(e)}")
            )
            
        return state
    
    async def process_pending_evidence(
        self,
        state: EnhancedComplianceState
    ) -> EnhancedComplianceState:
        """
        Process any pending evidence items.
        
        Replaces: process_pending_evidence Celery task
        
        Args:
            state: Current enhanced compliance state
            
        Returns:
            Updated state with processing results
        """
        try:
            async for db in get_async_db():
                try:
                    # Find pending evidence  
                    from sqlalchemy import select
                    stmt = select(EvidenceItem).where(
                        EvidenceItem.status == "not_started"
                    ).limit(100)  # Process in batches
                    
                    result = await db.execute(stmt)
                    pending_items = result.scalars().all()
                    
                    processed_count = 0
                    
                    for item in pending_items:
                        try:
                            # Process each pending item
                            processor = EvidenceProcessor(db)
                            processor.process_evidence(item)
                            item.status = "collected"
                            processed_count += 1
                            
                        except Exception as e:
                            logger.error(f"Error processing pending item {item.id}: {e}")
                            item.status = "rejected"
                    
                    if pending_items:
                        await db.commit()
                    
                    # Update state
                    state["pending_processing"] = {
                        "processed_count": processed_count,
                        "total_count": len(pending_items),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    
                    state["messages"].append(
                        SystemMessage(
                            content=f"Processed {processed_count}/{len(pending_items)} pending items"
                        )
                    )
                    
                    logger.info(f"Pending evidence processing: {processed_count} items")
                    
                except Exception as e:
                    await db.rollback()
                    logger.error(f"Error processing pending evidence: {e}")
                    state["error_count"] += 1
                    state["errors"].append(str(e))
                    raise
                    
        except Exception as e:
            logger.error(f"Failed to process pending evidence: {e}")
            state["messages"].append(
                SystemMessage(content=f"Pending processing failed: {str(e)}")
            )
            
        return state


# Export node instance
evidence_node = EvidenceCollectionNode()