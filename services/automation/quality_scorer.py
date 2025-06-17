"""
Service for calculating a quality score for each piece of evidence.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json

from database.evidence_item import EvidenceItem

class QualityScorer:
    """Calculates a quality score (0-100) for evidence."""

    def __init__(self):
        """Initialize the quality scorer with scoring weights."""
        self.weights = {
            'completeness': 0.30,  # How complete is the evidence data
            'freshness': 0.25,     # How recent is the evidence
            'relevance': 0.25,     # How relevant to compliance frameworks
            'verifiability': 0.20  # How verifiable/trustworthy is the source
        }

    def calculate_score(self, evidence: EvidenceItem) -> float:
        """
        Calculates a weighted quality score based on completeness, freshness,
        relevance, and verifiability.
        
        Args:
            evidence: EvidenceItem to score
            
        Returns:
            Quality score between 0.0 and 100.0
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
            
        except Exception as e:
            print(f"Error calculating quality score: {e}")
            return 50.0  # Return neutral score on error

    def _score_completeness(self, evidence: EvidenceItem) -> float:
        """
        Score based on how complete the evidence content is.
        
        Args:
            evidence: EvidenceItem to score
            
        Returns:
            Completeness score (0-100)
        """
        try:
            score = 0.0
            
            # Check for basic required fields
            if evidence.evidence_name and len(evidence.evidence_name.strip()) > 0:
                score += 25.0
            
            if evidence.description and len(evidence.description.strip()) > 0:
                score += 25.0
            
            if evidence.evidence_type and len(evidence.evidence_type.strip()) > 0:
                score += 20.0
                
            # Check for control reference
            if evidence.control_reference and len(evidence.control_reference.strip()) > 0:
                score += 15.0
                
            # Check for automation source (indicates structured collection)
            if evidence.automation_source and len(evidence.automation_source.strip()) > 0:
                score += 15.0
            
            return score
            
        except Exception as e:
            print(f"Error scoring completeness: {e}")
            return 50.0

    def _score_freshness(self, evidence: EvidenceItem) -> float:
        """
        Score based on the age of the evidence.
        
        Args:
            evidence: EvidenceItem to score
            
        Returns:
            Freshness score (0-100)
        """
        try:
            if not evidence.created_at:
                return 25.0  # Neutral score if no date
                
            age = datetime.utcnow() - evidence.created_at
            
            # Scoring based on age
            if age <= timedelta(days=7):
                return 100.0  # Very fresh
            elif age <= timedelta(days=30):
                return 90.0   # Fresh
            elif age <= timedelta(days=60):
                return 75.0   # Acceptable
            elif age <= timedelta(days=90):
                return 50.0   # Getting old
            elif age <= timedelta(days=180):
                return 25.0   # Old
            else:
                return 10.0   # Very old
                
        except Exception as e:
            print(f"Error scoring freshness: {e}")
            return 50.0

    def _score_relevance(self, evidence: EvidenceItem) -> float:
        """
        Score based on how well it's mapped to compliance frameworks.
        
        Args:
            evidence: EvidenceItem to score
            
        Returns:
            Relevance score (0-100)
        """
        try:
            score = 0.0
            
            # Check for control reference (indicates framework mapping)
            if evidence.control_reference:
                score += 40.0
            
            # Check for audit section mapping
            if evidence.audit_section:
                score += 30.0
                
            # Check for priority level (indicates importance assessment)
            if evidence.priority and evidence.priority in ['critical', 'high', 'medium', 'low']:
                score += 20.0
                
            # Check for compliance score impact
            if hasattr(evidence, 'compliance_score_impact') and evidence.compliance_score_impact > 0:
                score += 10.0
            
            return score if score > 0 else 30.0  # Minimum relevance score
            
        except Exception as e:
            print(f"Error scoring relevance: {e}")
            return 50.0

    def _score_verifiability(self, evidence: EvidenceItem) -> float:
        """
        Score based on whether it was automatically collected and source reliability.
        
        Args:
            evidence: EvidenceItem to score
            
        Returns:
            Verifiability score (0-100)
        """
        try:
            score = 0.0
            
            # Automated collection is more verifiable
            if evidence.collection_method == 'automated':
                score += 50.0
            elif evidence.collection_method == 'semi_automated':
                score += 35.0
            elif evidence.collection_method == 'manual':
                score += 20.0
            else:
                score += 25.0  # Unknown method
            
            # Integration source adds verifiability
            if evidence.automation_source:
                trusted_sources = ['google_workspace', 'microsoft_365', 'aws', 'azure']
                if any(source in evidence.automation_source.lower() for source in trusted_sources):
                    score += 30.0
                else:
                    score += 15.0
            
            # Required for audit adds verifiability
            if evidence.required_for_audit:
                score += 20.0
            
            return min(score, 100.0)
            
        except Exception as e:
            print(f"Error scoring verifiability: {e}")
            return 50.0

    def get_score_breakdown(self, evidence: EvidenceItem) -> Dict[str, Any]:
        """
        Gets a detailed breakdown of the quality score components.
        
        Args:
            evidence: EvidenceItem to analyze
            
        Returns:
            Dictionary with score breakdown
        """
        try:
            component_scores = {
                'completeness': self._score_completeness(evidence),
                'freshness': self._score_freshness(evidence),
                'relevance': self._score_relevance(evidence),
                'verifiability': self._score_verifiability(evidence)
            }
            
            weighted_scores = {
                component: score * self.weights[component]
                for component, score in component_scores.items()
            }
            
            total_score = sum(weighted_scores.values())
            
            return {
                'total_score': round(total_score, 2),
                'component_scores': component_scores,
                'weighted_scores': {k: round(v, 2) for k, v in weighted_scores.items()},
                'weights': self.weights,
                'score_interpretation': self._interpret_score(total_score)
            }
            
        except Exception as e:
            print(f"Error getting score breakdown: {e}")
            return {
                'total_score': 50.0,
                'error': str(e)
            }

    def _interpret_score(self, score: float) -> str:
        """
        Provides a human-readable interpretation of the quality score.
        
        Args:
            score: Quality score (0-100)
            
        Returns:
            Score interpretation string
        """
        if score >= 90:
            return 'Excellent - High quality evidence suitable for audit'
        elif score >= 80:
            return 'Good - Quality evidence with minor gaps'
        elif score >= 70:
            return 'Acceptable - Evidence meets basic requirements'
        elif score >= 60:
            return 'Fair - Evidence has notable quality issues'
        elif score >= 50:
            return 'Poor - Evidence has significant quality issues'
        else:
            return 'Very Poor - Evidence requires major improvements'

    def suggest_improvements(self, evidence: EvidenceItem) -> list:
        """
        Suggests specific improvements to increase evidence quality.
        
        Args:
            evidence: EvidenceItem to analyze
            
        Returns:
            List of improvement suggestions
        """
        try:
            suggestions = []
            
            # Completeness improvements
            if not evidence.evidence_name or len(evidence.evidence_name.strip()) == 0:
                suggestions.append("Add a descriptive evidence name/title")
                
            if not evidence.description or len(evidence.description.strip()) == 0:
                suggestions.append("Add a detailed description of the evidence")
                
            if not evidence.control_reference:
                suggestions.append("Map evidence to specific compliance framework controls")
                
            if not evidence.automation_source:
                suggestions.append("Specify the automation source for better traceability")
            
            # Freshness improvements
            if evidence.created_at:
                age = datetime.utcnow() - evidence.created_at
                if age > timedelta(days=90):
                    suggestions.append("Consider refreshing this evidence as it's getting old")
            
            # Relevance improvements
            if not evidence.audit_section:
                suggestions.append("Specify which audit section this evidence supports")
                
            if not evidence.priority:
                suggestions.append("Assign a priority level (critical, high, medium, low)")
            
            # Verifiability improvements
            if evidence.collection_method == 'manual':
                suggestions.append("Consider automating collection for better verifiability")
                
            if not evidence.required_for_audit:
                suggestions.append("Clarify if this evidence is required for compliance audits")
            
            return suggestions
            
        except Exception as e:
            print(f"Error generating improvement suggestions: {e}")
            return ["Review evidence data for completeness and accuracy"]

    def calculate_batch_scores(self, evidence_items: list) -> Dict[str, Any]:
        """
        Calculates quality scores for multiple evidence items.
        
        Args:
            evidence_items: List of EvidenceItem objects
            
        Returns:
            Dictionary with batch scoring results
        """
        try:
            if not evidence_items:
                return {
                    'total_items': 0,
                    'average_score': 0.0,
                    'score_distribution': {}
                }
            
            scores = [self.calculate_score(item) for item in evidence_items]
            average_score = sum(scores) / len(scores)
            
            # Create score distribution
            score_ranges = {
                'excellent': (90, 100),
                'good': (80, 89),
                'acceptable': (70, 79),
                'fair': (60, 69),
                'poor': (50, 59),
                'very_poor': (0, 49)
            }
            
            distribution = {}
            for range_name, (min_score, max_score) in score_ranges.items():
                count = sum(1 for score in scores if min_score <= score <= max_score)
                distribution[range_name] = {
                    'count': count,
                    'percentage': round(count / len(scores) * 100, 1)
                }
            
            return {
                'total_items': len(evidence_items),
                'average_score': round(average_score, 2),
                'highest_score': max(scores),
                'lowest_score': min(scores),
                'score_distribution': distribution,
                'scores': scores
            }
            
        except Exception as e:
            print(f"Error in batch scoring: {e}")
            return {
                'total_items': len(evidence_items) if evidence_items else 0,
                'error': str(e)
            }