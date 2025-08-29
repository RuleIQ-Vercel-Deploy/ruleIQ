#!/usr/bin/env python3
"""Common schemas for Golden Dataset system."""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class RegCitation(BaseModel):
    """Regulatory citation reference."""
    
    framework: str = Field(..., description="Regulatory framework (e.g., GDPR, HIPAA)")
    citation: str = Field(..., description="Specific citation (e.g., Article 5)")
    url: Optional[str] = Field(None, description="URL to the citation")
    jurisdiction: Optional[str] = Field(None, description="Jurisdiction (e.g., EU, US)")
    notes: Optional[str] = Field(None, description="Additional notes about the citation")


class SourceMeta(BaseModel):
    """Metadata about the source of data."""
    
    source_kind: str = Field(..., description="Type of source (e.g., regulatory_document, manual)")
    method: str = Field(..., description="Method of extraction (e.g., manual_extraction, automated)")
    created_by: str = Field(..., description="Who created this data")
    created_at: datetime = Field(..., description="When this data was created")
    version: Optional[str] = Field("1.0.0", description="Version of the source")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class TemporalValidity(BaseModel):
    """Temporal validity period for regulations."""
    
    effective_from: datetime = Field(..., description="When this becomes effective")
    effective_to: Optional[datetime] = Field(None, description="When this expires (None = no expiry)")
    
    @field_validator('effective_to')
    @classmethod
    def validate_dates(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """Ensure effective_to >= effective_from if set."""
        if v is not None and 'effective_from' in info.data:
            if v < info.data['effective_from']:
                raise ValueError("effective_to must be >= effective_from")
        return v


class ExpectedOutcome(BaseModel):
    """Expected outcome for compliance scenarios."""
    
    outcome_code: str = Field(..., description="Outcome code (e.g., COMPLIANT, REQUIRES_CONSENT)")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional outcome details")
    
    @field_validator('outcome_code')
    @classmethod
    def validate_outcome_code(cls, v: str) -> str:
        """Ensure outcome_code is not empty."""
        if not v or not v.strip():
            raise ValueError("outcome_code is required")
        return v