"""
Pydantic schemas for reporting API endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from datetime import datetime
from enum import Enum

class ReportFormat(str, Enum):
    PDF = "pdf"
    JSON = "json"
    HTML = "html"
    CSV = "csv"

class ReportType(str, Enum):
    EXECUTIVE_SUMMARY = "executive_summary"
    GAP_ANALYSIS = "gap_analysis"
    EVIDENCE_REPORT = "evidence_report"
    AUDIT_READINESS = "audit_readiness"
    COMPLIANCE_STATUS = "compliance_status"
    CONTROL_MATRIX = "control_matrix"
    RISK_ASSESSMENT = "risk_assessment"

class ReportFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"

class GenerateReportRequest(BaseModel):
    """Request schema for generating a report on-demand."""
    business_profile_id: UUID
    report_type: ReportType
    format: ReportFormat = ReportFormat.PDF
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    class Config:
        schema_extra = {
            "example": {
                "business_profile_id": "550e8400-e29b-41d4-a716-446655440000",
                "report_type": "executive_summary",
                "format": "pdf",
                "parameters": {
                    "frameworks": ["ISO27001", "SOC2"],
                    "period_days": 30
                }
            }
        }

class ReportResponse(BaseModel):
    """Response schema for generated reports."""
    report_id: str
    report_type: ReportType
    format: ReportFormat
    content: Union[str, Dict[str, Any]]  # Base64 string for PDF, JSON object for data
    content_type: str
    generated_at: datetime
    size_bytes: Optional[int] = None
    
    class Config:
        schema_extra = {
            "example": {
                "report_id": "report_123",
                "report_type": "executive_summary",
                "format": "pdf",
                "content": "JVBERi0xLjQK...",  # Base64 encoded PDF
                "content_type": "application/pdf",
                "generated_at": "2024-01-15T10:30:00Z",
                "size_bytes": 245760
            }
        }

class CreateScheduleRequest(BaseModel):
    """Request schema for creating a scheduled report."""
    business_profile_id: UUID
    report_type: ReportType
    frequency: ReportFrequency
    recipients: List[str] = Field(..., min_items=1)
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    schedule_config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('recipients')
    def validate_recipients(cls, v):
        # Basic email validation
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        for email in v:
            if not re.match(email_pattern, email):
                raise ValueError(f'Invalid email address: {email}')
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "business_profile_id": "550e8400-e29b-41d4-a716-446655440000",
                "report_type": "executive_summary",
                "frequency": "weekly",
                "recipients": ["manager@company.com", "compliance@company.com"],
                "parameters": {
                    "frameworks": ["ISO27001"],
                    "include_trends": True
                },
                "schedule_config": {
                    "hour": 9,
                    "day_of_week": 1  # Monday
                }
            }
        }

class ScheduleResponse(BaseModel):
    """Response schema for report schedules."""
    schedule_id: str
    business_profile_id: UUID
    report_type: ReportType
    frequency: ReportFrequency
    recipients: List[str]
    parameters: Dict[str, Any]
    active: bool
    created_at: datetime
    next_execution: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UpdateScheduleRequest(BaseModel):
    """Request schema for updating a scheduled report."""
    frequency: Optional[ReportFrequency] = None
    recipients: Optional[List[str]] = None
    parameters: Optional[Dict[str, Any]] = None
    active: Optional[bool] = None
    schedule_config: Optional[Dict[str, Any]] = None
    
    @validator('recipients')
    def validate_recipients(cls, v):
        if v is not None:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            for email in v:
                if not re.match(email_pattern, email):
                    raise ValueError(f'Invalid email address: {email}')
        return v

class ScheduleListResponse(BaseModel):
    """Response schema for listing schedules."""
    schedules: List[ScheduleResponse]
    total: int
    
class ReportHistoryItem(BaseModel):
    """Schema for report history items."""
    report_id: str
    report_type: ReportType
    format: ReportFormat
    generated_at: datetime
    size_bytes: Optional[int] = None
    download_url: Optional[str] = None
    status: str  # "completed", "failed", "processing"

class ReportHistoryResponse(BaseModel):
    """Response schema for report history."""
    reports: List[ReportHistoryItem]
    total: int
    page: int
    per_page: int

class ReportStatsResponse(BaseModel):
    """Response schema for reporting statistics."""
    total_reports_generated: int
    reports_this_month: int
    active_schedules: int
    most_popular_report_type: str
    total_recipients: int
    success_rate: float
    by_report_type: Dict[str, int]
    by_frequency: Dict[str, int]

class ExecuteScheduleResponse(BaseModel):
    """Response schema for manual schedule execution."""
    status: str
    task_id: Optional[str] = None
    schedule_id: str
    executed_at: datetime
    message: Optional[str] = None