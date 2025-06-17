"""
Main service for processing and enriching collected evidence.
"""

from datetime import datetime
import hashlib
import json
from sqlalchemy.orm import Session

from database.evidence_item import EvidenceItem
from .quality_scorer import QualityScorer

class EvidenceProcessor:
    """Processes raw evidence to add scores, tags, and mappings."""

    def __init__(self, db: Session):
        self.db = db
        self.quality_scorer = QualityScorer()

    def process_evidence(self, evidence: EvidenceItem) -> None:
        """
        Runs the full enrichment pipeline on a single evidence item.
        """
        try:
            # Calculate quality score
            quality_score = self.quality_scorer.calculate_score(evidence)
            
            # Generate content hash
            content_to_hash = {
                'evidence_type': evidence.evidence_type,
                'evidence_name': evidence.evidence_name,
                'description': evidence.description,
                'raw_data': evidence.raw_data
            }
            content_hash = hashlib.sha256(
                json.dumps(content_to_hash, sort_keys=True, default=str).encode()
            ).hexdigest()

            # Update metadata in-place
            metadata = {}
            if evidence.collection_notes:
                try:
                    metadata = json.loads(evidence.collection_notes) if isinstance(evidence.collection_notes, str) else evidence.collection_notes
                except (json.JSONDecodeError, TypeError):
                    metadata = {}
            
            metadata.update({
                'quality_score': quality_score,
                'content_hash': content_hash,
                'processed': True,
                'processed_at': datetime.utcnow().isoformat(),
            })
            
            # Store metadata back to collection_notes as JSON
            evidence.collection_notes = json.dumps(metadata)
            
            # The commit will be handled by the calling task
            
        except Exception as e:
            print(f"Error processing evidence {evidence.id}: {e}")
            raise

    def batch_process_evidence(self, evidence_items: list) -> dict:
        """
        Process multiple evidence items in batch.
        
        Args:
            evidence_items: List of EvidenceItem objects to process
            
        Returns:
            Dictionary with processing statistics
        """
        processed_count = 0
        error_count = 0
        
        for evidence in evidence_items:
            try:
                self.process_evidence(evidence)
                processed_count += 1
            except Exception as e:
                error_count += 1
                print(f"Failed to process evidence {evidence.id}: {e}")
        
        return {
            'total_items': len(evidence_items),
            'processed_count': processed_count,
            'error_count': error_count,
            'success_rate': (processed_count / len(evidence_items) * 100) if evidence_items else 0
        }

    def get_processing_statistics(self, business_profile_id: str, days: int = 30) -> dict:
        """
        Get processing statistics for a business profile.
        
        Args:
            business_profile_id: ID of the business profile
            days: Number of days to analyze
            
        Returns:
            Dictionary with processing statistics
        """
        try:
            from datetime import timedelta
            from sqlalchemy import and_
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Query for processed evidence items
            processed_items = self.db.query(EvidenceItem).filter(
                and_(
                    EvidenceItem.user_id == business_profile_id,
                    EvidenceItem.created_at > cutoff_date,
                    EvidenceItem.collection_notes.like('%"processed": true%')
                )
            ).all()
            
            # Calculate average quality score
            quality_scores = []
            for item in processed_items:
                try:
                    metadata = json.loads(item.collection_notes) if isinstance(item.collection_notes, str) else item.collection_notes
                    if metadata and 'quality_score' in metadata:
                        quality_scores.append(metadata['quality_score'])
                except (json.JSONDecodeError, TypeError):
                    continue
            
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
            
        except Exception as e:
            print(f"Error getting processing statistics: {e}")
            return {
                'processed_items': 0,
                'average_quality_score': 0,
                'quality_score_distribution': {'high': 0, 'medium': 0, 'low': 0},
                'analysis_period_days': days,
                'error': str(e)
            }