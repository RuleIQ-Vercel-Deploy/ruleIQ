"""
Service for calculating a quality score for each piece of evidence.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import json

from database.evidence_item import EvidenceItem
from config.logging_config import get_logger
from core.exceptions import BusinessLogicException

logger = get_logger(__name__)

class QualityScorer:
    """Calculates a quality score (0-100) for evidence."""

    def __init__(self):
        """Initialize the quality scorer with scoring weights."""
        self.weights = {
            'completeness': 0.30,
            'freshness': 0.25,
            'relevance': 0.25,
            'verifiability': 0.20
        }

    def calculate_score(self, evidence: EvidenceItem) -> float:
        """
        Calculates a weighted quality score based on completeness, freshness,
        relevance, and verifiability.
        """
        try:
            scores = {
                'completeness': self._score_completeness(evidence),
                'freshness': self._score_freshness(evidence),
                'relevance': self._score_relevance(evidence),
                'verifiability': self._score_verifiability(evidence)
            }

            total_score = sum(scores[aspect] * self.weights[aspect] for aspect in scores)
            return round(min(max(total_score, 0.0), 100.0), 2)
            
        except (ValueError, TypeError, KeyError) as e:
            logger.warning(
                f"Could not calculate quality score for evidence {evidence.id} due to data issue: {e}",
                exc_info=True
            )
            return 50.0  # Return neutral score on error

    def _score_completeness(self, evidence: EvidenceItem) -> float:
        """Score based on how complete the evidence content is."""
        try:
            if not isinstance(evidence.content, dict):
                return 10.0 # Low score if content is not a dictionary

            required_fields = ['name', 'description', 'source', 'timestamp']
            present_fields = sum(1 for field in required_fields if evidence.content.get(field))
            
            # Additional check for meaningful content
            if len(evidence.content.get('description', '')) < 20:
                present_fields -= 0.5 # Penalize short descriptions

            return (present_fields / len(required_fields)) * 100
        except (TypeError, AttributeError) as e:
            logger.warning(f"Completeness scoring failed for evidence {evidence.id}: {e}")
            return 20.0

    def _score_freshness(self, evidence: EvidenceItem) -> float:
        """Score based on the age of the evidence."""
        try:
            evidence_date = evidence.collected_at
            age = datetime.utcnow() - evidence_date

            if age < timedelta(days=30):
                return 100.0
            if age < timedelta(days=90):
                return 80.0
            if age < timedelta(days=180):
                return 50.0
            return 20.0
        except TypeError as e:
            logger.warning(f"Freshness scoring failed for evidence {evidence.id}: {e}")
            return 0.0

    def _score_relevance(self, evidence: EvidenceItem) -> float:
        """Score based on relevance to compliance frameworks (mock)."""
        # In a real implementation, this would involve NLP or keyword matching.
        try:
            if not isinstance(evidence.content, dict):
                return 10.0
            
            relevance_score = 50.0 # Base score
            description = evidence.content.get('description', '').lower()
            if any(keyword in description for keyword in ['audit', 'control', 'security', 'compliance']):
                relevance_score += 25.0
            if evidence.control_id:
                relevance_score += 25.0
            
            return min(relevance_score, 100.0)
        except AttributeError as e:
            logger.warning(f"Relevance scoring failed for evidence {evidence.id}: {e}")
            return 20.0

    def _score_verifiability(self, evidence: EvidenceItem) -> float:
        """Score based on the trustworthiness of the evidence source."""
        try:
            if not isinstance(evidence.content, dict):
                return 10.0

            source = evidence.content.get('source', 'unknown').lower()
            if source in ['api_integration', 'sso_logs', 'cloud_audit_logs']:
                return 100.0
            if source == 'user_upload':
                return 60.0
            return 30.0
        except AttributeError as e:
            logger.warning(f"Verifiability scoring failed for evidence {evidence.id}: {e}")
            return 20.0

    def get_score_breakdown(self, evidence: EvidenceItem) -> Dict[str, Any]:
        """Provides a detailed breakdown of the quality score."""
        try:
            scores = {
                'completeness': self._score_completeness(evidence),
                'freshness': self._score_freshness(evidence),
                'relevance': self._score_relevance(evidence),
                'verifiability': self._score_verifiability(evidence)
            }
            total_score = self.calculate_score(evidence)

            return {
                'total_score': total_score,
                'breakdown': scores,
                'weights': self.weights
            }
        except (ValueError, TypeError) as e:
            raise BusinessLogicException(f"Failed to get score breakdown for evidence {evidence.id}") from e

    def calculate_batch_scores(self, evidence_items: List[EvidenceItem]) -> Dict[str, Any]:
        """Calculates quality scores for multiple evidence items."""
        if not evidence_items:
            return {
                'total_items': 0,
                'average_score': 0.0,
                'score_distribution': {}
            }
        
        try:
            scores = [self.calculate_score(item) for item in evidence_items]
            average_score = sum(scores) / len(scores)
            
            score_ranges = {
                'excellent': (90, 100),
                'good': (80, 89.99),
                'acceptable': (70, 79.99),
                'poor': (50, 69.99),
                'very_poor': (0, 49.99)
            }
            
            distribution = {range_name: {'count': 0, 'percentage': 0.0} for range_name in score_ranges}
            for score in scores:
                for range_name, (min_s, max_s) in score_ranges.items():
                    if min_s <= score <= max_s:
                        distribution[range_name]['count'] += 1
                        break
            
            for range_name in distribution:
                count = distribution[range_name]['count']
                distribution[range_name]['percentage'] = round(count / len(scores) * 100, 1)

            return {
                'total_items': len(evidence_items),
                'average_score': round(average_score, 2),
                'score_distribution': distribution,
            }
        except Exception as e:
            logger.error(f"Error in batch scoring: {e}", exc_info=True)
            raise BusinessLogicException("Failed to calculate batch scores.") from e
