import { apiClient } from './client';

export interface ComplianceStatus {
  framework: string;
  overall_compliance_percentage: number;
  status: 'compliant' | 'partial' | 'non_compliant' | 'not_assessed';
  last_assessment_date?: string;
  next_review_date?: string;
  by_domain: Array<{
    domain: string;
    compliance_percentage: number;
    controls_compliant: number;
    controls_total: number;
    critical_findings: number;
  }>;
  risk_summary: {
    high_risk_items: number;
    medium_risk_items: number;
    low_risk_items: number;
    remediation_in_progress: number;
  };
}

export interface ComplianceTask {
  id: string;
  title: string;
  description: string;
  control_id: string;
  framework: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  status: 'pending' | 'in_progress' | 'completed' | 'blocked';
  assigned_to?: string;
  due_date?: string;
  effort_hours: number;
  dependencies: string[];
  evidence_required: string[];
}

export interface ComplianceRisk {
  id: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  likelihood: 'very_likely' | 'likely' | 'possible' | 'unlikely';
  impact: string;
  affected_controls: string[];
  mitigation_plan?: string;
  status: 'identified' | 'mitigating' | 'accepted' | 'resolved';
}

class ComplianceService {
  /**
   * Get compliance status for all frameworks
   */
  async getComplianceStatus(businessProfileId: string): Promise<ComplianceStatus[]> {
    const response = await apiClient.get<ComplianceStatus[]>('/compliance/status', {
      params: { business_profile_id: businessProfileId },
    });
    return response;
  }

  /**
   * Get compliance status for a specific framework
   */
  async getFrameworkComplianceStatus(
    businessProfileId: string,
    frameworkId: string,
  ): Promise<ComplianceStatus> {
    const response = await apiClient.get<ComplianceStatus>(`/compliance/status/${frameworkId}`, {
      params: { business_profile_id: businessProfileId },
    });
    return response;
  }

  /**
   * Get compliance tasks
   */
  async getComplianceTasks(params?: {
    business_profile_id: string;
    framework_id?: string;
    status?: string;
    priority?: string;
    assigned_to?: string;
    page?: number;
    page_size?: number;
  }): Promise<{ tasks: ComplianceTask[]; total: number }> {
    const response = await apiClient.get<{ tasks: ComplianceTask[]; total: number }>(
      '/compliance/tasks',
      { params },
    );
    return response;
  }

  /**
   * Create compliance task
   */
  async createComplianceTask(data: Partial<ComplianceTask>): Promise<ComplianceTask> {
    const response = await apiClient.post<ComplianceTask>('/compliance/tasks', data);
    return response;
  }

  /**
   * Update compliance task
   */
  async updateComplianceTask(
    taskId: string,
    data: Partial<ComplianceTask>,
  ): Promise<ComplianceTask> {
    const response = await apiClient.patch<ComplianceTask>(`/compliance/tasks/${taskId}`, data);
    return response;
  }

  /**
   * Get compliance risks
   */
  async getComplianceRisks(params?: {
    business_profile_id: string;
    framework_id?: string;
    severity?: string;
    status?: string;
    page?: number;
    page_size?: number;
  }): Promise<{ risks: ComplianceRisk[]; total: number }> {
    const response = await apiClient.get<{ risks: ComplianceRisk[]; total: number }>(
      '/compliance/risks',
      { params },
    );
    return response;
  }

  /**
   * Create compliance risk
   */
  async createComplianceRisk(data: Partial<ComplianceRisk>): Promise<ComplianceRisk> {
    const response = await apiClient.post<ComplianceRisk>('/compliance/risks', data);
    return response;
  }

  /**
   * Update compliance risk
   */
  async updateComplianceRisk(
    riskId: string,
    data: Partial<ComplianceRisk>,
  ): Promise<ComplianceRisk> {
    const response = await apiClient.patch<ComplianceRisk>(`/compliance/risks/${riskId}`, data);
    return response;
  }

  /**
   * Get compliance timeline
   */
  async getComplianceTimeline(
    businessProfileId: string,
    frameworkId?: string,
  ): Promise<{
    milestones: Array<{
      date: string;
      title: string;
      type: 'assessment' | 'audit' | 'certification' | 'review';
      status: 'completed' | 'upcoming' | 'overdue';
      description?: string;
    }>;
    upcoming_deadlines: Array<{
      date: string;
      item: string;
      type: string;
      days_remaining: number;
    }>;
  }> {
    const params = frameworkId
      ? { business_profile_id: businessProfileId, framework_id: frameworkId }
      : { business_profile_id: businessProfileId };
    const response = await apiClient.get<any>('/compliance/timeline', { params });
    return response;
  }

  /**
   * Get compliance dashboard
   */
  async getComplianceDashboard(businessProfileId: string): Promise<{
    overall_score: number;
    frameworks_status: ComplianceStatus[];
    pending_tasks: number;
    open_risks: number;
    upcoming_audits: Array<{
      framework: string;
      date: string;
      type: string;
    }>;
    recent_activity: Array<{
      timestamp: string;
      type: string;
      description: string;
      user?: string;
    }>;
    compliance_trends: Array<{
      date: string;
      score: number;
    }>;
  }> {
    const response = await apiClient.get<any>('/compliance/dashboard', {
      params: { business_profile_id: businessProfileId },
    });
    return response;
  }

  /**
   * Generate compliance certificate
   */
  async generateComplianceCertificate(
    businessProfileId: string,
    frameworkId: string,
  ): Promise<{
    certificate_id: string;
    issued_date: string;
    valid_until: string;
    download_url: string;
  }> {
    const response = await apiClient.post<any>('/compliance/certificate/generate', {
      business_profile_id: businessProfileId,
      framework_id: frameworkId,
    });
    return response;
  }
}

export const complianceService = new ComplianceService();
