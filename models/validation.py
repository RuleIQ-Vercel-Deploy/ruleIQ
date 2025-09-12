"""Validation models for RAG Self-Critic system."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from uuid import UUID, uuid4


class ValidationStatus(str, Enum):
    """Status of validation result."""
    
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class ReviewPriority(str, Enum):
    """Priority levels for human review queue."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ValidationRequest(BaseModel):
    """Request model for validation."""
    
    model_config = ConfigDict(use_enum_values=True)
    
    request_id: UUID = Field(default_factory=uuid4)
    response_text: str
    response_metadata: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    assessment_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ValidationScore(BaseModel):
    """Individual validation score components."""
    
    semantic_similarity: float = Field(ge=0.0, le=1.0)
    citation_coverage: float = Field(ge=0.0, le=1.0)
    fact_consistency: float = Field(ge=0.0, le=1.0)
    overall_confidence: float = Field(ge=0.0, le=100.0)


class ValidationFailure(BaseModel):
    """Details of validation failure."""
    
    reason: str
    description: str
    severity: str = Field(default="medium")
    suggestion: Optional[str] = None
    evidence: Optional[List[str]] = None


class HumanReviewRequest(BaseModel):
    """Request for human review of validation."""
    
    model_config = ConfigDict(use_enum_values=True)
    
    review_id: UUID = Field(default_factory=uuid4)
    validation_id: UUID
    priority: ReviewPriority
    confidence_score: float
    failure_reasons: List[ValidationFailure]
    response_text: str
    suggested_corrections: Optional[List[str]] = None
    assigned_to: Optional[str] = None
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None
    reviewer_notes: Optional[str] = None


class BatchValidationRequest(BaseModel):
    """Request for batch validation."""
    
    batch_id: UUID = Field(default_factory=uuid4)
    responses: List[ValidationRequest]
    priority: ReviewPriority = ReviewPriority.MEDIUM
    max_parallel: int = Field(default=10, le=10)
    timeout_seconds: int = Field(default=30)


class BatchValidationResult(BaseModel):
    """Result of batch validation."""
    
    batch_id: UUID
    total_responses: int
    successful_validations: int
    failed_validations: int
    requiring_review: int
    average_confidence: float
    total_processing_time_ms: float
    results: List[Dict[str, Any]]
    completed_at: datetime = Field(default_factory=datetime.utcnow)


class ValidationAuditEntry(BaseModel):
    """Audit log entry for validation."""
    
    model_config = ConfigDict(use_enum_values=True)
    
    audit_id: UUID = Field(default_factory=uuid4)
    validation_id: UUID
    request_id: UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Request details
    original_response: str
    context: Optional[Dict[str, Any]] = None
    
    # Validation results
    confidence_score: float
    is_valid: bool
    requires_review: bool
    failure_reasons: List[str] = Field(default_factory=list)
    
    # Performance metrics
    processing_time_ms: float
    cache_hit: bool = False
    
    # Regulatory matches
    matched_regulations: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ValidationConfiguration(BaseModel):
    """Configuration for validation thresholds and behavior."""
    
    # Confidence thresholds
    human_review_threshold: float = Field(default=80.0, ge=0.0, le=100.0)
    invalid_threshold: float = Field(default=50.0, ge=0.0, le=100.0)
    
    # Score weights
    semantic_weight: float = Field(default=0.40, ge=0.0, le=1.0)
    citation_weight: float = Field(default=0.30, ge=0.0, le=1.0)
    consistency_weight: float = Field(default=0.30, ge=0.0, le=1.0)
    
    # Performance settings
    max_processing_time_ms: int = Field(default=100)
    enable_caching: bool = True
    cache_ttl_seconds: int = Field(default=3600)
    
    # Batch settings
    max_batch_size: int = Field(default=10)
    batch_timeout_seconds: int = Field(default=30)
    
    # Circuit breaker settings
    circuit_breaker_threshold: int = Field(default=5)
    circuit_breaker_timeout: int = Field(default=60)


class ValidationMetricsSnapshot(BaseModel):
    """Snapshot of validation metrics at a point in time."""
    
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    total_validations: int
    successful_validations: int
    failed_validations: int
    human_review_required: int
    
    # Performance metrics
    average_confidence: float
    average_processing_time_ms: float
    p95_processing_time_ms: Optional[float] = None
    p99_processing_time_ms: Optional[float] = None
    
    # Cache metrics
    cache_hit_rate: float
    cache_size: int
    
    # Error metrics
    error_rate: float
    timeout_rate: float
    
    # Regulatory coverage
    unique_regulations_matched: int
    most_common_failures: List[Dict[str, Any]] = Field(default_factory=list)