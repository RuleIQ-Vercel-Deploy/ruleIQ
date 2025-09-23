"""
Automation services package for ComplianceGPT
"""

from typing import Any, Dict, List, Optional

from .duplicate_detector import DuplicateDetector
from .evidence_processor import EvidenceProcessor
from .quality_scorer import QualityScorer

__all__ = ["DuplicateDetector", "EvidenceProcessor", "QualityScorer"]
