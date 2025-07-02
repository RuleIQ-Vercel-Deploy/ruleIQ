import { apiClient } from './client';

export interface ReadinessScore {
  overall_score: number;
  category_scores: {
    policies: number;
    processes: number;
    technology: number;
    people: number;
  };
  maturity_level: 'initial' | 'developing' | 'defined' | 'managed' | 'optimized';
  strengths: string[];
  weaknesses: string[];
  recommendations: Array<{
    category: string;
    priority: 'high' | 'medium' | 'low';
    description: string;
    effort: string;
    impact: string;
  }>;
}

export interface GapAnalysis {
  framework: string;
  gaps: Array<{
    control_id: string;
    control_name: string;
    gap_type: 'missing' | 'partial' | 'outdated';
    current_state: string;
    target_state: string;
    remediation_steps: string[];
    priority: 'critical' | 'high' | 'medium' | 'low';
    estimated_effort: string;
  }>;
  summary: {
    total_gaps: number;
    critical_gaps: number;
    estimated_remediation_time: string;
    quick_wins: string[];
  };
}

class ReadinessService {
  /**
   * Get readiness score for a business profile
   */
  async getReadinessScore(businessProfileId: string): Promise<ReadinessScore> {
    const response = await apiClient.get<ReadinessScore>(`/readiness/${businessProfileId}`);
    return response.data;
  }

  /**
   * Get gap analysis for a specific framework
   */
  async getGapAnalysis(
    businessProfileId: string,
    frameworkId?: string
  ): Promise<GapAnalysis> {
    const params = frameworkId ? { framework_id: frameworkId } : undefined;
    const response = await apiClient.get<GapAnalysis>(
      `/readiness/gaps/${businessProfileId}`,
      { params }
    );
    return response.data;
  }

  /**
   * Get readiness roadmap
   */
  async getReadinessRoadmap(
    businessProfileId: string,
    targetFrameworks: string[]
  ): Promise<{
    phases: Array<{
      phase: number;
      name: string;
      duration: string;
      objectives: string[];
      key_activities: Array<{
        activity: string;
        owner: string;
        effort: string;
        dependencies: string[];
      }>;
      deliverables: string[];
      success_criteria: string[];
    }>;
    timeline: {
      start_date: string;
      end_date: string;
      milestones: Array<{
        date: string;
        milestone: string;
        phase: number;
      }>;
    };
    resource_requirements: {
      internal_hours: number;
      external_support_needed: boolean;
      budget_estimate: string;
      tools_required: string[];
    };
  }> {
    const response = await apiClient.post<any>('/readiness/roadmap', {
      business_profile_id: businessProfileId,
      target_frameworks: targetFrameworks,
    });
    return response.data;
  }

  /**
   * Perform quick readiness assessment
   */
  async performQuickAssessment(
    businessProfileId: string,
    answers: Record<string, any>
  ): Promise<{
    score: number;
    interpretation: string;
    next_steps: string[];
    detailed_report_available: boolean;
  }> {
    const response = await apiClient.post<any>('/readiness/quick-assessment', {
      business_profile_id: businessProfileId,
      answers,
    });
    return response.data;
  }

  /**
   * Get readiness trends
   */
  async getReadinessTrends(
    businessProfileId: string,
    days: number = 90
  ): Promise<{
    trends: Array<{
      date: string;
      overall_score: number;
      category_scores: Record<string, number>;
    }>;
    improvements: {
      category: string;
      improvement_percentage: number;
      key_changes: string[];
    }[];
    projections: {
      estimated_compliance_date: string;
      required_improvement_rate: number;
      risk_areas: string[];
    };
  }> {
    const response = await apiClient.get<any>(`/readiness/trends/${businessProfileId}`, {
      params: { days },
    });
    return response.data;
  }

  /**
   * Get readiness benchmarks
   */
  async getReadinessBenchmarks(
    industry: string,
    company_size: string
  ): Promise<{
    industry_average: number;
    top_performers: number;
    your_position: 'below_average' | 'average' | 'above_average' | 'top_performer';
    improvement_opportunities: string[];
    peer_comparison: {
      category: string;
      your_score: number;
      industry_average: number;
      gap: number;
    }[];
  }> {
    const response = await apiClient.get<any>('/readiness/benchmarks', {
      params: { industry, company_size },
    });
    return response.data;
  }

  /**
   * Export readiness report
   */
  async exportReadinessReport(
    businessProfileId: string,
    format: 'pdf' | 'word' | 'excel'
  ): Promise<void> {
    await apiClient.download(
      `/readiness/export/${businessProfileId}?format=${format}`,
      `readiness-report.${format}`
    );
  }
}

export const readinessService = new ReadinessService();