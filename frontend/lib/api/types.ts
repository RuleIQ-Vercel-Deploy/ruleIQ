/**
 * API Types generated from OpenAPI specification
 * These types match the backend FastAPI endpoints
 */

// Base types
export interface UUID {
  id: string;
}

// Policy types
export interface Policy {
  id: string;
  title: string;
  description: string;
  category: PolicyCategory;
  status: PolicyStatus;
  created_at: string;
  updated_at: string;
  version: number;
  content?: string;
  tags?: string[];
  compliance_frameworks?: string[];
  risk_level?: RiskLevel;
}

export enum PolicyCategory {
  DATA_PROTECTION = 'data_protection',
  SECURITY = 'security',
  PRIVACY = 'privacy',
  COMPLIANCE = 'compliance',
  OPERATIONAL = 'operational',
  FINANCIAL = 'financial',
}

export enum PolicyStatus {
  DRAFT = 'draft',
  PENDING_APPROVAL = 'pending_approval',
  UNDER_REVIEW = 'under_review',
  APPROVED = 'approved',
  PUBLISHED = 'published',
  ARCHIVED = 'archived',
}

export enum RiskLevel {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pages: number;
  per_page: number;
}

export interface ErrorResponse {
  detail: string;
  status: number;
  type?: string;
}

// Evidence types
export interface Evidence {
  id: string;
  title: string;
  description: string;
  type: EvidenceType;
  status: EvidenceStatus;
  policy_id?: string;
  file_url?: string;
  created_at: string;
  updated_at: string;
  metadata?: Record<string, any>;
}

export enum EvidenceType {
  DOCUMENT = 'document',
  SCREENSHOT = 'screenshot',
  LOG = 'log',
  AUDIT_REPORT = 'audit_report',
  CERTIFICATE = 'certificate',
  OTHER = 'other',
}

export enum EvidenceStatus {
  PENDING = 'pending',
  UNDER_REVIEW = 'under_review',
  VERIFIED = 'verified',
  REJECTED = 'rejected',
  EXPIRED = 'expired',
}

// Risk types
export interface Risk {
  id: string;
  title: string;
  description: string;
  category: RiskCategory;
  level: RiskLevel;
  status: RiskStatus;
  impact: number;
  likelihood: number;
  mitigation_plan?: string;
  owner?: string;
  created_at: string;
  updated_at: string;
}

export enum RiskCategory {
  STRATEGIC = 'strategic',
  OPERATIONAL = 'operational',
  FINANCIAL = 'financial',
  COMPLIANCE = 'compliance',
  REPUTATIONAL = 'reputational',
  TECHNOLOGICAL = 'technological',
}

export enum RiskStatus {
  IDENTIFIED = 'identified',
  ASSESSED = 'assessed',
  MONITORING = 'monitoring',
  MITIGATED = 'mitigated',
  ACCEPTED = 'accepted',
  CLOSED = 'closed',
}

// Request types
export interface CreatePolicyRequest {
  title: string;
  description: string;
  category: PolicyCategory;
  content?: string;
  tags?: string[];
  compliance_frameworks?: string[];
  risk_level?: RiskLevel;
}

export interface UpdatePolicyRequest extends Partial<CreatePolicyRequest> {
  status?: PolicyStatus;
}

export interface PolicyQueryParams {
  page?: number;
  per_page?: number;
  category?: PolicyCategory;
  status?: PolicyStatus;
  search?: string;
  sort_by?: 'created_at' | 'updated_at' | 'title';
  sort_order?: 'asc' | 'desc';
}

// User/Auth types
export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  created_at: string;
  is_active: boolean;
}

export enum UserRole {
  ADMIN = 'admin',
  MANAGER = 'manager',
  USER = 'user',
  VIEWER = 'viewer',
  AUDITOR = 'auditor',
  COMPLIANCE_OFFICER = 'compliance_officer',
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Settings types
export interface Settings {
  id: string;
  organization_name: string;
  timezone: string;
  date_format: string;
  notifications_enabled: boolean;
  email_notifications: boolean;
  compliance_frameworks: string[];
  updated_at: string;
}