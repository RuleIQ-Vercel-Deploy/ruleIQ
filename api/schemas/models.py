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
    data_sensitivity: str = Field(default='Low', pattern=r'^(Low|Moderate|High|Confidential)$')

class BusinessProfileCreate(BusinessProfileBase):
    pass

class BusinessProfileUpdate(BaseModel):
    company_name: Optional[str] = Field(None, min_length=2, max_length=100)
    industry: Optional[str] = Field(None, min_length=2, max_length=50)
    employee_count: Optional[int] = Field(None, ge=1, le=1000000)
    annual_revenue: Optional[str] = Field(None, pattern=r'^(Under £\\d+[MK]|£\\d+[MK]-£\\d+[MK]|Over £\\d+[MK])$')
    country: Optional[str] = Field(None, max_length=50)
    data_sensitivity: Optional[str] = Field(None, pattern=r'^(Low|Moderate|High|Confidential)$')


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
    framework_id: UUID
    name: str
    relevance_score: float
    reasoning: str


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
    title: str = Field(..., description="A descriptive title for the evidence.")
    description: Optional[str] = Field(None, description="A detailed description of the evidence content.")
    control_id: str = Field(..., description="The specific control ID this evidence addresses (e.g., 'AC-1').")
    framework_id: UUID = Field(..., description="The compliance framework this evidence belongs to.")
    business_profile_id: UUID = Field(..., description="The business profile this evidence is associated with.")
    source: str = Field("manual_upload", description="The source of the evidence (e.g., 'manual_upload', 'integration:jira').")
    tags: Optional[List[str]] = Field(None, description="Keywords for searching and filtering.")


class EvidenceUpdate(BaseModel):
    title: Optional[str] = Field(None, description="A new title for the evidence.")
    description: Optional[str] = Field(None, description="An updated description of the evidence.")
    status: Optional[str] = Field(None, pattern=r'^(pending_review|approved|rejected)$', description="The review status of the evidence.")
    tags: Optional[List[str]] = Field(None, description="A new list of keywords.")


class EvidenceStatusUpdate(BaseModel):
    status: str = Field(..., pattern=r'^(pending_review|approved|rejected)$', description="The new review status for the evidence.")


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
