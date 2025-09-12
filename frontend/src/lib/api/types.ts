/**
 * TypeScript types generated from OpenAPI specification
 * This file will be auto-generated once the backend OpenAPI is available
 */

// Base types
export interface BaseResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// Policy types
export interface Policy {
  id: string;
  name: string;
  description: string;
  framework: string;
  status: 'active' | 'draft' | 'archived';
  created_at: string;
  updated_at: string;
  requirements: Requirement[];
}

export interface Requirement {
  id: string;
  policy_id: string;
  title: string;
  description: string;
  category: string;
  priority: 'high' | 'medium' | 'low';
  status: 'compliant' | 'non_compliant' | 'partial' | 'not_assessed';
}

// Evidence types
export interface Evidence {
  id: string;
  requirement_id: string;
  title: string;
  description: string;
  file_url?: string;
  type: 'document' | 'screenshot' | 'report' | 'other';
  uploaded_at: string;
  uploaded_by: string;
  status: 'pending' | 'approved' | 'rejected';
}

// Risk types
export interface Risk {
  id: string;
  title: string;
  description: string;
  category: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  likelihood: 'certain' | 'likely' | 'possible' | 'unlikely' | 'rare';
  impact: 'severe' | 'major' | 'moderate' | 'minor' | 'negligible';
  status: 'identified' | 'mitigated' | 'accepted' | 'transferred';
  mitigation_plan?: string;
}

// Assessment types
export interface Assessment {
  id: string;
  policy_id: string;
  name: string;
  description: string;
  status: 'not_started' | 'in_progress' | 'completed';
  compliance_score: number;
  started_at?: string;
  completed_at?: string;
  assessor?: string;
}

// API Response types
export type PoliciesResponse = BaseResponse<Policy[]>;
export type PolicyResponse = BaseResponse<Policy>;
export type EvidenceResponse = BaseResponse<Evidence[]>;
export type RisksResponse = BaseResponse<Risk[]>;
export type AssessmentResponse = BaseResponse<Assessment>;

// API Request types
export interface CreatePolicyRequest {
  name: string;
  description: string;
  framework: string;
}

export interface UpdatePolicyRequest {
  name?: string;
  description?: string;
  status?: Policy['status'];
}

export interface CreateEvidenceRequest {
  requirement_id: string;
  title: string;
  description: string;
  type: Evidence['type'];
  file?: File;
}

export interface CreateRiskRequest {
  title: string;
  description: string;
  category: string;
  severity: Risk['severity'];
  likelihood: Risk['likelihood'];
  impact: Risk['impact'];
  mitigation_plan?: string;
}

// Pagination
export interface PaginationParams {
  page?: number;
  limit?: number;
  sort_by?: string;
  order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> extends BaseResponse<T> {
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}