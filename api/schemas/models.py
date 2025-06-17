from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, validator

from api.utils.validators import InputValidators


# User schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=128)

    @validator('password')
    def validate_password_strength(self, v):
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

# Business Profile schemas with validation
class BusinessProfileBase(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=100)
    industry: str = Field(..., min_length=2, max_length=50)
    employee_count: int = Field(..., ge=1, le=1000000)
    annual_revenue: Optional[str] = Field(None, pattern=r'^(Under £\d+[MK]|£\d+[MK]-£\d+[MK]|Over £\d+[MK])$')
    country: str = Field(default="UK", pattern=r'^[A-Z]{2,3}$')
    handles_personal_data: bool = Field(..., description="Handles personal data")
    processes_payments: bool = Field(..., description="Processes payments")
    stores_health_data: bool = Field(..., description="Stores health data")
    provides_financial_services: bool = Field(..., description="Provides financial services")
    operates_critical_infrastructure: bool = Field(..., description="Operates critical infrastructure")
    has_international_operations: bool = Field(..., description="Has international operations")
    cloud_providers: List[str] = Field(default_factory=list, max_items=10)
    saas_tools: List[str] = Field(default_factory=list, max_items=20)
    development_tools: List[str] = Field(default_factory=list, max_items=10)
    existing_frameworks: List[str] = Field(default_factory=list, max_items=10)
    planned_frameworks: List[str] = Field(default_factory=list, max_items=10)
    compliance_budget: Optional[str] = Field(None, pattern=r'^(Under £\d+K|£\d+K-£\d+K|Over £\d+K)$')
    compliance_timeline: Optional[str] = Field(None, pattern=r'^\d+ months?$')

    @validator('company_name')
    def validate_company_name(self, v):
        return InputValidators.validate_company_name(v)

    @validator('cloud_providers', 'saas_tools', 'development_tools', 'existing_frameworks', 'planned_frameworks', each_item=True)
    def validate_list_items(self, v):
        return InputValidators.validate_safe_string(v, 50)

class BusinessProfileCreate(BusinessProfileBase):
    pass

class BusinessProfileUpdate(BaseModel):
    company_name: Optional[str] = Field(None, min_length=2, max_length=100)
    industry: Optional[str] = Field(None, min_length=2, max_length=50)
    employee_count: Optional[int] = Field(None, ge=1, le=1000000)
    annual_revenue: Optional[str] = None
    handles_personal_data: Optional[bool] = None
    processes_payments: Optional[bool] = None
    stores_health_data: Optional[bool] = None
    provides_financial_services: Optional[bool] = None
    operates_critical_infrastructure: Optional[bool] = None
    has_international_operations: Optional[bool] = None
    cloud_providers: Optional[List[str]] = None
    saas_tools: Optional[List[str]] = None
    development_tools: Optional[List[str]] = None
    existing_frameworks: Optional[List[str]] = None
    planned_frameworks: Optional[List[str]] = None
    compliance_budget: Optional[str] = None
    compliance_timeline: Optional[str] = None

class BusinessProfileResponse(BusinessProfileBase):
    id: UUID
    user_id: UUID
    assessment_completed: bool
    assessment_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Assessment schemas
class AssessmentSessionCreate(BaseModel):
    session_type: str = Field(default="compliance_scoping", pattern=r'^[a-z_]+$')

class AssessmentResponseUpdate(BaseModel):
    question_id: str = Field(..., pattern=r'^[a-z_]+$')
    response: str = Field(..., min_length=1, max_length=5000)
    move_to_next_stage: bool = False

class AssessmentSessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    business_profile_id: Optional[UUID]
    session_type: str
    status: str
    current_stage: int
    total_stages: int
    questions_answered: int
    total_questions: int
    responses: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    recommended_frameworks: List[str]
    priority_order: List[str]
    next_steps: List[str]
    created_at: datetime
    last_activity: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

class AssessmentQuestion(BaseModel):
    id: str
    question: str
    type: str
    options: Optional[List[str]] = None
    required: bool = True

# Framework schemas
class FrameworkBase(BaseModel):
    name: str
    display_name: str
    description: str
    category: str
    region: str
    mandatory_for: List[str]
    applicable_industries: List[str]
    company_size_range: Dict[str, int]
    key_requirements: List[str]
    typical_controls: int
    estimated_effort: str
    certification_available: bool
    regulatory_body: Optional[str]
    penalties_for_non_compliance: Optional[str]

class FrameworkResponse(FrameworkBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class FrameworkRecommendation(BaseModel):
    framework: FrameworkResponse
    relevance_score: float = Field(..., ge=0, le=100)
    reasons: List[str]
    priority: str = Field(..., pattern=r'^(High|Medium|Low)$')

# Policy schemas
class PolicyGenerateRequest(BaseModel):
    framework_id: UUID
    control_ids: Optional[List[UUID]] = None
    customizations: Optional[Dict[str, Any]] = None

class GeneratedPolicyResponse(BaseModel):
    id: UUID
    business_profile_id: UUID
    framework_id: UUID
    policy_name: str
    policy_type: str
    content: str
    sections: Dict[str, Any]
    customizations: Dict[str, Any]
    version: int
    status: str
    generated_by: str
    approved: bool
    approved_by: Optional[UUID]
    approved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Implementation Plan schemas
class ImplementationPlanCreate(BaseModel):
    framework_id: UUID
    control_ids: Optional[List[UUID]] = None

class ImplementationTaskUpdate(BaseModel):
    status: str = Field(..., pattern=r'^(not_started|in_progress|completed|blocked)$')
    assigned_to: Optional[str] = Field(None, max_length=100)
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    notes: Optional[str] = Field(None, max_length=2000)

class ImplementationPlanResponse(BaseModel):
    id: UUID
    business_profile_id: UUID
    framework_id: UUID
    plan_name: str
    total_phases: int
    total_tasks: int
    estimated_duration_weeks: int
    estimated_budget: Optional[float]
    phases: List[Dict[str, Any]]
    tasks: List[Dict[str, Any]]
    milestones: List[Dict[str, Any]]
    resources_required: List[Dict[str, Any]]
    risk_factors: List[Dict[str, Any]]
    status: str
    progress_percentage: float = Field(..., ge=0, le=100)
    created_at: datetime
    updated_at: datetime
    start_date: Optional[datetime]
    target_end_date: Optional[datetime]

    class Config:
        from_attributes = True

# Evidence schemas
class EvidenceItemCreate(BaseModel):
    framework_id: UUID
    control_id: UUID
    evidence_type: str = Field(..., pattern=r'^(document|screenshot|log|report|certificate)$')
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    file_url: Optional[str] = None
    automation_possible: bool = False
    collection_method: Optional[str] = Field(None, pattern=r'^(manual|automated|hybrid)$')

class EvidenceItemUpdate(BaseModel):
    status: str = Field(..., pattern=r'^(not_collected|collected|approved|rejected|expired)$')
    file_url: Optional[str] = None
    collected_data: Optional[Dict[str, Any]] = None
    notes: Optional[str] = Field(None, max_length=1000)

class EvidenceItemResponse(BaseModel):
    id: UUID
    business_profile_id: UUID
    framework_id: UUID
    control_id: UUID
    evidence_type: str
    title: str
    description: Optional[str]
    status: str
    file_url: Optional[str]
    automation_possible: bool
    automation_configured: bool
    collection_method: Optional[str]
    collected_data: Dict[str, Any]
    last_collected: Optional[datetime]
    review_status: str
    reviewed_by: Optional[UUID]
    reviewed_at: Optional[datetime]
    review_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Readiness Assessment schemas
class ReadinessAssessmentResponse(BaseModel):
    overall_score: float = Field(..., ge=0, le=100)
    framework_scores: Dict[str, float]
    control_coverage: Dict[str, Dict[str, Any]]
    gaps: List[Dict[str, Any]]
    recommendations: List[Dict[str, Any]]
    risk_level: str = Field(..., pattern=r'^(Low|Medium|High|Critical)$')
    projected_timeline: str
    next_review_date: datetime
    executive_summary: str
    timestamp: datetime

class ComplianceReport(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    framework: str
    report_type: str = Field(..., pattern=r'^(executive|detailed|audit|gap_analysis)$')
    format: str = Field(default="pdf", pattern=r'^(pdf|docx|html)$')
    include_evidence: bool = True
    include_recommendations: bool = True
