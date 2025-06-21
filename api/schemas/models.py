from datetime import date, datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator


# User schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

    @validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        from api.dependencies.auth import validate_password
        is_valid, message = validate_password(v)
        if not is_valid:
            raise ValueError(message)
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None

# --- Shared Detail Models ---

class RecommendationDetail(BaseModel):
    """A specific recommendation for improving compliance posture."""
    title: str = Field(..., description="The title of the recommendation.")
    description: str = Field(..., description="A detailed description of the recommendation.")
    priority: str = Field(..., pattern=r'^(Low|Medium|High)$', description="The priority for implementing the recommendation.")
    estimated_effort: str = Field(..., pattern=r'^(Low|Medium|High)$', description="Estimated effort to implement.")
    related_controls: List[str] = Field(default_factory=list, description="List of control IDs this recommendation addresses.")

# Business Profile schemas
class BusinessProfileBase(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=100)
    industry: str = Field(..., min_length=2, max_length=50)
    employee_count: int = Field(..., ge=1, le=1000000)
    annual_revenue: Optional[str] = Field(None, pattern=r'^(Under £\\d+[MK]|£\\d+[MK]-£\\d+[MK]|Over £\\d+[MK])$')
    country: str = Field(default='United Kingdom', max_length=50)
    data_sensitivity: str = Field(default='Low', pattern=r'^(Low|Moderate|High|Confidential)$')  # Re-added for framework relevance

    # Required boolean fields (matching database model)
    handles_persona: bool = Field(..., description="Handles personal data")
    processes_payme: bool = Field(..., description="Processes payments")
    stores_health_d: bool = Field(..., description="Stores health data")
    provides_financ: bool = Field(..., description="Provides financial services")
    operates_critic: bool = Field(..., description="Operates critical infrastructure")
    has_internation: bool = Field(..., description="Has international operations")

    # Optional JSONB fields with defaults
    existing_framew: Optional[List[str]] = Field(default_factory=list)
    planned_framewo: Optional[List[str]] = Field(default_factory=list)
    cloud_providers: Optional[List[str]] = Field(default_factory=list)
    saas_tools: Optional[List[str]] = Field(default_factory=list)
    development_too: Optional[List[str]] = Field(default_factory=list)
    compliance_budg: Optional[str] = Field(None)
    compliance_time: Optional[str] = Field(None)

class BusinessProfileCreate(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=100)
    industry: str = Field(..., min_length=2, max_length=50)
    employee_count: int = Field(..., ge=1, le=1000000)
    annual_revenue: Optional[str] = Field(None, pattern=r'^(Under £\\d+[MK]|£\\d+[MK]-£\\d+[MK]|Over £\\d+[MK])$')
    country: str = Field(default='United Kingdom', max_length=50)
    data_sensitivity: str = Field(default='Low', pattern=r'^(Low|Moderate|High|Confidential)$')  # Re-added for framework relevance

    # Optional boolean fields with defaults (for minimal profile creation)
    handles_persona: bool = Field(default=False, description="Handles personal data")
    processes_payme: bool = Field(default=False, description="Processes payments")
    stores_health_d: bool = Field(default=False, description="Stores health data")
    provides_financ: bool = Field(default=False, description="Provides financial services")
    operates_critic: bool = Field(default=False, description="Operates critical infrastructure")
    has_internation: bool = Field(default=False, description="Has international operations")

    # Optional JSONB fields with defaults
    existing_framew: Optional[List[str]] = Field(default_factory=list)
    planned_framewo: Optional[List[str]] = Field(default_factory=list)
    cloud_providers: Optional[List[str]] = Field(default_factory=list)
    saas_tools: Optional[List[str]] = Field(default_factory=list)
    development_too: Optional[List[str]] = Field(default_factory=list)
    compliance_budg: Optional[str] = Field(None)
    compliance_time: Optional[str] = Field(None)

class BusinessProfileUpdate(BaseModel):
    company_name: Optional[str] = Field(None, min_length=2, max_length=100)
    industry: Optional[str] = Field(None, min_length=2, max_length=50)
    employee_count: Optional[int] = Field(None, ge=1, le=1000000)
    annual_revenue: Optional[str] = Field(None, pattern=r'^(Under £\\d+[MK]|£\\d+[MK]-£\\d+[MK]|Over £\\d+[MK])$')
    country: Optional[str] = Field(None, max_length=50)
    # data_sensitivity: Optional[str] = Field(None, pattern=r'^(Low|Moderate|High|Confidential)$')  # Temporarily removed

    # Optional boolean fields
    handles_persona: Optional[bool] = Field(None)
    processes_payme: Optional[bool] = Field(None)
    stores_health_d: Optional[bool] = Field(None)
    provides_financ: Optional[bool] = Field(None)
    operates_critic: Optional[bool] = Field(None)
    has_internation: Optional[bool] = Field(None)

    # Optional JSONB fields
    existing_framew: Optional[List[str]] = Field(None)
    planned_framewo: Optional[List[str]] = Field(None)
    cloud_providers: Optional[List[str]] = Field(None)
    saas_tools: Optional[List[str]] = Field(None)
    development_too: Optional[List[str]] = Field(None)
    compliance_budg: Optional[str] = Field(None)
    compliance_time: Optional[str] = Field(None)


class BusinessProfileResponse(BusinessProfileBase):
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Compliance Framework Schemas
class ComplianceFrameworkResponse(BaseModel):
    id: UUID
    name: str
    description: str
    category: str
    version: Optional[str]
    controls: List[Dict[str, Any]]

    class Config:
        from_attributes = True

class FrameworkRecommendation(BaseModel):
    framework: ComplianceFrameworkResponse
    relevance_score: float
    reasons: Optional[List[str]] = []
    priority: Optional[str] = "medium"


# Policy Schemas
class PolicyGenerateRequest(BaseModel):
    framework_name: str = Field(..., description="The name of the compliance framework (e.g., 'ISO 27001').")
    business_profile_id: UUID = Field(..., description="The ID of the business profile to tailor the policy for.")
    policy_title: Optional[str] = Field(None, description="A specific title for the policy document.")
    tone: str = Field("formal", pattern=r'^(formal|informal|strict)$', description="The tone of the generated policy.")
    specific_controls: Optional[List[str]] = Field(None, description="A list of specific control IDs to focus on.")


class GeneratedPolicyResponse(BaseModel):
    policy_title: str
    content: str
    version: str
    created_at: datetime


# Evidence Schemas
class EvidenceCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="A descriptive title for the evidence.")
    description: Optional[str] = Field(None, max_length=2000, description="A detailed description of the evidence content.")
    control_id: str = Field(..., min_length=1, max_length=50, description="The specific control ID this evidence addresses (e.g., 'AC-1').")
    framework_id: UUID = Field(..., description="The compliance framework this evidence belongs to.")
    business_profile_id: UUID = Field(..., description="The business profile this evidence is associated with.")
    source: str = Field("manual_upload", min_length=1, description="The source of the evidence (e.g., 'manual_upload', 'integration:jira').")
    tags: Optional[List[str]] = Field(None, description="Keywords for searching and filtering.")
    evidence_type: str = Field("document", description="The type of evidence (e.g., 'document', 'policy_document', 'screenshot', 'log_file').")


class EvidenceUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="A descriptive title for the evidence.")
    description: Optional[str] = Field(None, max_length=2000, description="A detailed description of the evidence content.")
    status: Optional[str] = Field(None, description="The review status of the evidence.")
    tags: Optional[List[str]] = Field(None, description="Keywords for searching and filtering.")
    evidence_type: Optional[str] = Field(None, description="The type of evidence.")


class EvidenceBulkUpdate(BaseModel):
    """Schema for bulk updating evidence items."""
    evidence_ids: List[UUID]
    status: str
    reason: Optional[str] = None


class EvidenceBulkUpdateResponse(BaseModel):
    """Schema for bulk update response."""
    updated_count: int
    failed_count: int
    failed_ids: Optional[List[UUID]] = None

class EvidenceStatusUpdate(BaseModel):
    status: str = Field(..., pattern=r'^(pending_review|approved|rejected)$', description="The new review status for the evidence.")
    notes: Optional[str] = Field(None, description="Optional notes about the status update.")


class EvidenceResponse(EvidenceCreate):
    id: UUID
    user_id: UUID
    file_path: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecentEvidenceItem(BaseModel):
    id: UUID
    title: str
    control_id: str
    status: str
    updated_at: datetime


class EvidenceDashboardResponse(BaseModel):
    total_items: int
    status_counts: Dict[str, int]
    completion_percentage: float
    recently_updated: List[RecentEvidenceItem]


class EvidenceListResponse(BaseModel):
    """Response schema for evidence list endpoint."""
    evidence_items: List[EvidenceResponse]
    total_count: int
    page: int
    page_size: int


class EvidenceStatisticsResponse(BaseModel):
    """Response schema for evidence statistics."""
    total_evidence_items: int
    by_status: Dict[str, int]
    by_type: Dict[str, int]
    by_framework: Dict[str, int]
    average_quality_score: float


class EvidenceSearchResult(BaseModel):
    """Individual search result item."""
    id: UUID
    title: str
    description: Optional[str]
    evidence_type: str
    status: str
    relevance_score: float
    created_at: datetime
    updated_at: datetime


class EvidenceSearchResponse(BaseModel):
    """Response schema for evidence search."""
    results: List[EvidenceSearchResult]
    total_count: int
    page: int
    page_size: int


class EvidenceValidationResult(BaseModel):
    """Response schema for evidence validation."""
    quality_score: int
    validation_results: Dict[str, str]
    issues: List[str]
    recommendations: List[str]


class EvidenceRequirement(BaseModel):
    """Individual evidence requirement."""
    control_id: str
    evidence_type: str
    title: str
    description: str
    automation_possible: bool


class EvidenceRequirementsResponse(BaseModel):
    """Response schema for evidence requirements."""
    requirements: List[EvidenceRequirement]


class EvidenceAutomationResponse(BaseModel):
    """Response schema for evidence automation configuration."""
    configuration_successful: bool
    automation_enabled: bool
    test_connection: bool
    next_collection: str


class ComplianceStatusResponse(BaseModel):
    """Response schema for compliance status."""
    overall_score: float
    status: str
    message: str
    framework_scores: Dict[str, float]
    evidence_summary: Dict[str, Any]
    recent_activity: List[Dict[str, Any]]
    recommendations: List[str]
    last_updated: str


# Assessment Session Schemas
class AssessmentQuestion(BaseModel):
    question_id: str = Field(..., description="Unique identifier for the question.")
    text: str = Field(..., description="The text of the assessment question.")
    question_type: str = Field(..., pattern=r'^(multiple_choice|free_text|yes_no)$', description="The type of question.")
    options: Optional[List[Dict[str, str]]] = Field(None, description="A list of options for multiple-choice questions, e.g., [{'value': 'opt1', 'label': 'Option 1'}].")


class AssessmentSessionCreate(BaseModel):
    business_profile_id: UUID
    session_type: str = "compliance_scoping"


class AssessmentSessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    business_profile_id: Optional[UUID]
    session_type: str
    status: str
    current_stage: int
    total_stages: int
    responses: Dict[str, Any]
    recommendations: List[Any]
    started_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class AssessmentResponseUpdate(BaseModel):
    responses: Dict[str, Any] = Field(..., description="The user's responses to the assessment questions.")
    status: Optional[str] = Field(None, pattern=r'^(in_progress|completed)$', description="The updated status of the assessment session.")


# Implementation Plan Schemas
class ImplementationPlanCreate(BaseModel):
    business_profile_id: UUID
    framework_id: UUID
    title: str
    phases: List[Dict[str, Any]]
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None


class ImplementationPlanResponse(BaseModel):
    id: UUID
    user_id: UUID
    business_profile_id: UUID
    framework_id: UUID
    title: str
    status: str
    phases: List[Dict[str, Any]]
    planned_start_date: Optional[date] = None
    planned_end_date: Optional[date] = None
    actual_start_date: Optional[date] = None
    actual_end_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ImplementationTaskUpdate(BaseModel):
    status: Optional[str] = Field(None, description="New status of the task (e.g., 'pending', 'in_progress', 'completed', 'blocked')")
    notes: Optional[str] = Field(None, description="Additional notes for the task update.")
    assignee_id: Optional[UUID] = Field(None, description="ID of the user assigned to the task.")
    due_date: Optional[date] = Field(None, description="New due date for the task.")
    completion_percentage: Optional[int] = Field(None, ge=0, le=100, description="Percentage of task completion.")


# Readiness and Reporting Schemas
class ReadinessAssessmentResponse(BaseModel):
    id: UUID
    user_id: UUID
    framework_id: UUID
    business_profile_id: UUID
    overall_score: float
    score_breakdown: Dict[str, Any]
    priority_actions: Optional[List[Dict[str, Any]]]
    quick_wins: Optional[List[Dict[str, Any]]]
    score_trend: str
    estimated_readiness_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ComplianceReport(BaseModel):
    framework: str = Field(..., description="The name or ID of the compliance framework for the report.")
    report_type: str = Field(default="summary", description="Type of report to generate (e.g., 'summary', 'detailed', 'attestation').")
    format: str = Field(default="pdf", pattern=r'^(pdf|json)$', description="The output format for the report.")
    include_evidence: bool = Field(default=False, description="Whether to include evidence summaries in the report.")
    include_recommendations: bool = Field(default=True, description="Whether to include actionable recommendations.")
