"""
Asynchronous service for processing and enriching collected evidence.
"""

from datetime import datetime, timedelta
import hashlib
import json
from typing import List, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.exc import SQLAlchemyError

from database.models import EvidenceItem
from .quality_scorer import QualityScorer
from core.exceptions import DatabaseException, BusinessLogicException
from config.logging_config import get_logger

logger = get_logger(__name__)

class EvidenceProcessor:
    """Processes raw evidence to add scores, tags, and mappings asynchronously."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.quality_scorer = QualityScorer() # QualityScorer is synchronous and CPU-bound

    def process_evidence(self, evidence: EvidenceItem) -> None:
        """
        Runs the full enrichment pipeline on a single evidence item in-memory.
        The caller is responsible for committing the changes. This method is synchronous
        to allow for efficient in-memory batch processing before a final async commit.
        """
        try:
            quality_score = self.quality_scorer.calculate_score(evidence)
            
            raw_data_for_hash = json.loads(evidence.raw_data) if isinstance(evidence.raw_data, str) else evidence.raw_data

            content_to_hash = {
                'evidence_type': evidence.evidence_type,
                'description': evidence.description,
                'raw_data': raw_data_for_hash
            }
            content_hash = hashlib.sha256(
                json.dumps(content_to_hash, sort_keys=True, default=str).encode()
            ).hexdigest()

            metadata = evidence.metadata or {}
            metadata.update({
                'quality_score': quality_score,
                'content_hash': content_hash,
                'processed': True,
                'processed_at': datetime.utcnow().isoformat(),
            })
            
            evidence.metadata = metadata
            flag_modified(evidence, "metadata")

        except (TypeError, ValueError, AttributeError, json.JSONDecodeError) as e:
            logger.error(f"Failed to process evidence {evidence.id} due to data error: {e}", exc_info=True)
            metadata = evidence.metadata or {}
            metadata.update({'processed': False, 'error': str(e)})
            evidence.metadata = metadata
            flag_modified(evidence, "metadata")
            # Do not re-raise to allow batch processing to continue

    async def get_processing_stats(self, user_id: UUID, days: int = 30) -> Dict[str, Any]:
        """Retrieves processing statistics for a given user."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            stmt = select(EvidenceItem).where(
                and_(
                    EvidenceItem.user_id == user_id,
                    EvidenceItem.created_at > cutoff_date,
                    EvidenceItem.metadata['processed'].as_boolean() == True
                )
            )
            result = await self.db.execute(stmt)
            processed_items = result.scalars().all()
            
            quality_scores = [
                item.metadata['quality_score']
                for item in processed_items
                if item.metadata and 'quality_score' in item.metadata
            ]
            
            avg_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            return {
                'processed_items': len(processed_items),
                'average_quality_score': round(avg_quality_score, 2),
                'quality_score_distribution': {
                    'high': len([s for s in quality_scores if s >= 80]),
                    'medium': len([s for s in quality_scores if 50 <= s < 80]),
                    'low': len([s for s in quality_scores if s < 50])
                },
                'analysis_period_days': days
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Database error while getting processing stats for user {user_id}: {e}", exc_info=True)
            raise DatabaseException("Failed to retrieve processing statistics.") from e
        except Exception as e:
            logger.error(f"Unexpected error getting processing stats for user {user_id}: {e}", exc_info=True)
            raise BusinessLogicException("An unexpected error occurred while calculating statistics.") from e
