"""
Automation services package for ComplianceGPT
"""

from .duplicate_detector import DuplicateDetector
from .quality_scorer import QualityScorer
from .evidence_processor import EvidenceProcessor

__all__ = ['DuplicateDetector', 'QualityScorer', 'EvidenceProcessor']