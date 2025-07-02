import { apiClient } from './client';

import type { ComplianceFramework } from '@/types/api';

export interface FrameworkRecommendation {
  framework: ComplianceFramework;
  relevance_score: number;
  reasons: string[];
  estimated_effort: string;
  priority: 'high' | 'medium' | 'low';
}

class FrameworkService {
  /**
   * Get all available compliance frameworks
   */
  async getFrameworks(): Promise<ComplianceFramework[]> {
    const response = await apiClient.get<ComplianceFramework[]>('/frameworks');
    return response.data;
  }

  /**
   * Get a specific framework by ID
   */
  async getFramework(id: string): Promise<ComplianceFramework> {
    const response = await apiClient.get<ComplianceFramework>(`/frameworks/${id}`);
    return response.data;
  }

  /**
   * Get framework recommendations based on business profile
   */
  async getFrameworkRecommendations(businessProfileId: string): Promise<FrameworkRecommendation[]> {
    const response = await apiClient.get<FrameworkRecommendation[]>(
      `/frameworks/recommendations/${businessProfileId}`
    );
    return response.data;
  }

  /**
   * Get framework controls
   */
  async getFrameworkControls(frameworkId: string): Promise<{
    framework: string;
    total_controls: number;
    controls: Array<{
      control_id: string;
      control_name: string;
      description: string;
      category: string;
      priority: string;
      evidence_required: string[];
    }>;
  }> {
    const response = await apiClient.get<any>(`/frameworks/${frameworkId}/controls`);
    return response.data;
  }

  /**
   * Get framework implementation guide
   */
  async getFrameworkImplementationGuide(frameworkId: string): Promise<{
    framework: string;
    estimated_duration: string;
    phases: Array<{
      phase: number;
      name: string;
      duration: string;
      tasks: string[];
      deliverables: string[];
    }>;
    resources_required: string[];
    key_milestones: string[];
  }> {
    const response = await apiClient.get<any>(`/frameworks/${frameworkId}/implementation-guide`);
    return response.data;
  }

  /**
   * Get framework compliance status
   */
  async getFrameworkComplianceStatus(
    frameworkId: string,
    businessProfileId: string
  ): Promise<{
    framework: string;
    overall_compliance: number;
    by_category: Record<string, number>;
    controls_status: {
      compliant: number;
      partial: number;
      non_compliant: number;
      not_assessed: number;
    };
    last_assessment_date?: string;
    next_review_date?: string;
  }> {
    const response = await apiClient.get<any>(`/frameworks/${frameworkId}/compliance-status`, {
      params: { business_profile_id: businessProfileId },
    });
    return response.data;
  }

  /**
   * Compare multiple frameworks
   */
  async compareFrameworks(frameworkIds: string[]): Promise<{
    frameworks: Array<{
      id: string;
      name: string;
      control_count: number;
      estimated_effort: string;
      industry_alignment: string[];
      key_features: string[];
    }>;
    overlap_analysis: {
      common_controls: number;
      unique_controls: Record<string, number>;
      compatibility_score: number;
    };
    recommendation: string;
  }> {
    const response = await apiClient.post<any>('/frameworks/compare', {
      framework_ids: frameworkIds,
    });
    return response.data;
  }

  /**
   * Get framework maturity assessment
   */
  async getFrameworkMaturityAssessment(
    frameworkId: string,
    businessProfileId: string
  ): Promise<{
    framework: string;
    maturity_level: 'initial' | 'developing' | 'defined' | 'managed' | 'optimized';
    maturity_score: number;
    strengths: string[];
    weaknesses: string[];
    improvement_areas: Array<{
      area: string;
      current_level: number;
      target_level: number;
      recommendations: string[];
    }>;
  }> {
    const response = await apiClient.get<any>(`/frameworks/${frameworkId}/maturity-assessment`, {
      params: { business_profile_id: businessProfileId },
    });
    return response.data;
  }
}

export const frameworkService = new FrameworkService();