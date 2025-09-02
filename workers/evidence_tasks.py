"""
from __future__ import annotations

Celery background tasks for evidence collection and lifecycle management, with async support.
"""
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from uuid import UUID
from celery.utils.log import get_task_logger
from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError
from celery_app import celery_app
from core.exceptions import BusinessLogicException, DatabaseException
from database.db_setup import get_async_db
from database.evidence_item import EvidenceItem
from services.automation.duplicate_detector import DuplicateDetector
from services.automation.evidence_processor import EvidenceProcessor
logger = get_task_logger(__name__)

async def _process_evidence_item_async(evidence_data: Dict[str, Any], user_id: UUID, business_profile_id: UUID, integration_id: str) -> Dict[str, Any]:
    """Async helper to process a single piece of evidence."""
    async for db in get_async_db():
        try:
            if await DuplicateDetector.is_duplicate(db, user_id, evidence_data):
                logger.info(f'Duplicate evidence detected and skipped for user {user_id}.')
                return {'status': 'skipped', 'reason': 'duplicate'}
            processor = EvidenceProcessor(db)
            new_evidence = EvidenceItem(user_id=user_id, business_profile_id=business_profile_id, evidence_type=evidence_data.get('evidence_type'), description=evidence_data.get('description'), source=evidence_data.get('source'), raw_data=evidence_data.get('raw_data', {}), status='active')
            processor.process_evidence(new_evidence)
            db.add(new_evidence)
            await db.commit()
            await db.refresh(new_evidence)
            logger.info(f'Successfully processed and saved new evidence {new_evidence.id} for user {user_id}')
            return {'status': 'processed', 'evidence_id': str(new_evidence.id)}
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f'Database error while processing evidence for user {user_id}: {e}', exc_info=True)
            raise DatabaseException('Failed to process evidence due to a database error.') from e
        except Exception as e:
            await db.rollback()
            logger.error(f'Unexpected error during evidence processing for user {user_id}: {e}', exc_info=True)
            raise BusinessLogicException('An unexpected error occurred during evidence processing.') from e

async def _sync_evidence_status_async() -> Dict[str, int]:
    """Async helper to find old, active evidence and mark it as stale."""
    async for db in get_async_db():
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=90)
            stmt = update(EvidenceItem).where(EvidenceItem.status == 'active', EvidenceItem.collected_at < cutoff_date).values(status='stale').execution_options(synchronize_session=False)
            result = await db.execute(stmt)
            await db.commit()
            updated_count = result.rowcount
            logger.info(f'Evidence status sync completed. Marked {updated_count} items as stale.')
            return {'updated_count': updated_count}
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f'Database error during evidence status sync: {e}', exc_info=True)
            raise DatabaseException('Failed to sync evidence status due to a database error.') from e

@celery_app.task(bind=True, autoretry_for=(DatabaseException, Exception), retry_kwargs={'max_retries': 5, 'countdown': 60}, retry_backoff=True, retry_backoff_max=600, retry_jitter=True, rate_limit='5/m')
def process_evidence_item(self, evidence_data: Dict[str, Any], user_id_str: str, business_profile_id_str: str, integration_id: str) -> Any:
    """Processes a single evidence item by running the async helper."""
    logger.info(f"Processing evidence from integration '{integration_id}' for user '{user_id_str}'")
    try:
        user_id = UUID(user_id_str)
        business_profile_id = UUID(business_profile_id_str)
        return asyncio.run(_process_evidence_item_async(evidence_data, user_id, business_profile_id, integration_id))
    except BusinessLogicException as e:
        logger.error(f'Business logic error processing evidence, not retrying: {e}', exc_info=True)
    except Exception as e:
        logger.critical(f'Unexpected, non-retriable error processing evidence: {e}', exc_info=True)
        raise e

@celery_app.task(bind=True, autoretry_for=(DatabaseException, Exception), retry_kwargs={'max_retries': 5, 'countdown': 120}, retry_backoff=True, retry_backoff_max=600, retry_jitter=True, rate_limit='3/m')
def sync_evidence_status(self) -> Any:
    """Periodically syncs the status of evidence items by running the async helper."""
    logger.info('Starting evidence status sync task')
    try:
        return asyncio.run(_sync_evidence_status_async())
    except Exception as e:
        logger.critical(f'Unexpected, non-retriable error in evidence status sync: {e}', exc_info=True)
        raise e