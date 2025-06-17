"""
Service for detecting and handling duplicate evidence items.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib
import json
from sqlalchemy.orm import Session
from sqlalchemy import and_

from database.evidence_item import EvidenceItem

class DuplicateDetector:
    """Detects duplicate evidence based on content and context."""

    @staticmethod
    def is_duplicate(
        db: Session, 
        business_profile_id: str, 
        evidence_data: Dict[str, Any], 
        time_window_hours: int = 24
    ) -> bool:
        """
        Checks if an evidence item is a likely duplicate of one already stored.
        
        Args:
            db: Database session
            business_profile_id: ID of the business profile
            evidence_data: Evidence data to check for duplicates
            time_window_hours: Time window to check for duplicates (default 24 hours)
            
        Returns:
            True if duplicate found, False otherwise
        """
        try:
            # Generate content hash for comparison
            content_hash = DuplicateDetector._generate_content_hash(evidence_data)
            
            # Define time window for duplicate detection
            cutoff_time = datetime.utcnow() - timedelta(hours=time_window_hours)
            
            # Query for existing evidence with similar characteristics
            existing = db.query(EvidenceItem).filter(
                and_(
                    EvidenceItem.user_id == business_profile_id,  # Using user_id as business_profile_id
                    EvidenceItem.evidence_type == evidence_data.get('evidence_type', ''),
                    EvidenceItem.created_at > cutoff_time
                )
            ).first()
            
            # Additional content-based duplicate detection
            if existing and existing.collection_notes:
                try:
                    existing_metadata = json.loads(existing.collection_notes) if isinstance(existing.collection_notes, str) else existing.collection_notes
                    existing_hash = existing_metadata.get('content_hash')
                    if existing_hash == content_hash:
                        return True
                except (json.JSONDecodeError, TypeError):
                    pass
            
            return False
            
        except Exception as e:
            # Log error and return False to avoid blocking evidence collection
            print(f"Error in duplicate detection: {e}")
            return False

    @staticmethod
    def _generate_content_hash(evidence_data: Dict[str, Any]) -> str:
        """
        Generates a hash of the evidence content for duplicate comparison.
        
        Args:
            evidence_data: Evidence data to hash
            
        Returns:
            SHA256 hash of the content
        """
        try:
            # Extract relevant content for hashing
            content_to_hash = {
                'evidence_type': evidence_data.get('evidence_type', ''),
                'title': evidence_data.get('title', ''),
                'integration_source': evidence_data.get('integration_source', ''),
                'raw_data': evidence_data.get('raw_data', {})
            }
            
            # Create deterministic hash
            content_str = json.dumps(content_to_hash, sort_keys=True, default=str)
            return hashlib.sha256(content_str.encode()).hexdigest()
            
        except Exception as e:
            # Return empty hash on error
            print(f"Error generating content hash: {e}")
            return ""

    @staticmethod
    def find_similar_evidence(
        db: Session,
        business_profile_id: str,
        evidence_data: Dict[str, Any],
        similarity_threshold: float = 0.8,
        limit: int = 5
    ) -> list:
        """
        Finds evidence items that are similar to the given evidence.
        
        Args:
            db: Database session
            business_profile_id: ID of the business profile
            evidence_data: Evidence data to find similarities for
            similarity_threshold: Minimum similarity score (0.0 to 1.0)
            limit: Maximum number of similar items to return
            
        Returns:
            List of similar evidence items
        """
        try:
            # Query for evidence of the same type
            similar_items = db.query(EvidenceItem).filter(
                and_(
                    EvidenceItem.user_id == business_profile_id,
                    EvidenceItem.evidence_type == evidence_data.get('evidence_type', '')
                )
            ).limit(limit * 2).all()  # Get more items to filter by similarity
            
            # Calculate similarity scores
            scored_items = []
            for item in similar_items:
                similarity_score = DuplicateDetector._calculate_similarity(evidence_data, item)
                if similarity_score >= similarity_threshold:
                    scored_items.append({
                        'evidence_item': item,
                        'similarity_score': similarity_score
                    })
            
            # Sort by similarity and return top matches
            scored_items.sort(key=lambda x: x['similarity_score'], reverse=True)
            return scored_items[:limit]
            
        except Exception as e:
            print(f"Error finding similar evidence: {e}")
            return []

    @staticmethod
    def _calculate_similarity(evidence_data: Dict[str, Any], existing_item: EvidenceItem) -> float:
        """
        Calculates similarity score between new evidence and existing item.
        
        Args:
            evidence_data: New evidence data
            existing_item: Existing evidence item from database
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        try:
            similarity_score = 0.0
            
            # Compare evidence types (exact match)
            if evidence_data.get('evidence_type') == existing_item.evidence_type:
                similarity_score += 0.3
            
            # Compare titles (exact match)
            if evidence_data.get('title') == existing_item.evidence_name:
                similarity_score += 0.3
            
            # Compare descriptions (exact match)
            if evidence_data.get('description') == existing_item.description:
                similarity_score += 0.2
            
            # Compare integration sources
            if evidence_data.get('integration_source') == getattr(existing_item, 'automation_source', ''):
                similarity_score += 0.2
            
            return min(similarity_score, 1.0)
            
        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0

    @staticmethod
    def mark_as_duplicate(db: Session, evidence_item_id: str, original_item_id: str) -> bool:
        """
        Marks an evidence item as a duplicate of another.
        
        Args:
            db: Database session
            evidence_item_id: ID of the duplicate item
            original_item_id: ID of the original item
            
        Returns:
            True if successfully marked, False otherwise
        """
        try:
            evidence_item = db.query(EvidenceItem).filter(EvidenceItem.id == evidence_item_id).first()
            if not evidence_item:
                return False
            
            # Update metadata to mark as duplicate
            metadata = {
                'is_duplicate': True,
                'original_item_id': original_item_id,
                'marked_duplicate_at': datetime.utcnow().isoformat()
            }
            
            # Store metadata in collection_notes as JSON
            evidence_item.collection_notes = json.dumps(metadata)
            evidence_item.status = 'duplicate'
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            print(f"Error marking as duplicate: {e}")
            return False

    @staticmethod
    def get_duplicate_statistics(db: Session, business_profile_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Gets statistics about duplicate evidence detection.
        
        Args:
            db: Database session
            business_profile_id: ID of the business profile
            days: Number of days to analyze
            
        Returns:
            Dictionary with duplicate statistics
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Query for evidence items in the time period
            total_items = db.query(EvidenceItem).filter(
                and_(
                    EvidenceItem.user_id == business_profile_id,
                    EvidenceItem.created_at > cutoff_date
                )
            ).count()
            
            # Query for duplicate items
            duplicate_items = db.query(EvidenceItem).filter(
                and_(
                    EvidenceItem.user_id == business_profile_id,
                    EvidenceItem.created_at > cutoff_date,
                    EvidenceItem.status == 'duplicate'
                )
            ).count()
            
            duplicate_rate = (duplicate_items / total_items * 100) if total_items > 0 else 0
            
            return {
                'total_items': total_items,
                'duplicate_items': duplicate_items,
                'unique_items': total_items - duplicate_items,
                'duplicate_rate_percent': round(duplicate_rate, 2),
                'analysis_period_days': days
            }
            
        except Exception as e:
            print(f"Error getting duplicate statistics: {e}")
            return {
                'total_items': 0,
                'duplicate_items': 0,
                'unique_items': 0,
                'duplicate_rate_percent': 0,
                'analysis_period_days': days,
                'error': str(e)
            }