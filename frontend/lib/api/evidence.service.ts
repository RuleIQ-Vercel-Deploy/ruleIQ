import { apiClient } from './client';

import type { EvidenceItem } from '@/types/api';
import type { UnknownRecord } from '@/types/common';

export interface CreateEvidenceRequest {
  framework_id: string;
  control_id: string;
  evidence_type: string;
  title: string;
  description?: string;
  metadata?: UnknownRecord;
}

export interface UpdateEvidenceRequest extends Partial<CreateEvidenceRequest> {
  status?: 'pending' | 'approved' | 'rejected' | 'needs_review';
}

export interface BulkUpdateEvidenceRequest {
  evidence_ids: string[];
  status: 'pending' | 'approved' | 'rejected' | 'needs_review';
  reason?: string;
}

export interface EvidenceAutomationConfig {
  enabled: boolean;
  schedule?: string;
  integration_id?: string;
  settings?: UnknownRecord;
}

export interface EvidenceClassificationRequest {
  force_reclassify?: boolean;
}

export interface EvidenceSearchParams {
  framework_id?: string;
  evidence_type?: string;
  status?: string;
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

class EvidenceService {
  /**
   * Get all evidence items
   */
  async getEvidence(params?: EvidenceSearchParams): Promise<{ items: EvidenceItem[]; total: number }> {
    const response = await apiClient.get<{ items: EvidenceItem[]; total: number }>('/evidence', { params });
    return response.data;
  }

  /**
   * Get a specific evidence item by ID
   */
  async getEvidenceItem(id: string): Promise<EvidenceItem> {
    const response = await apiClient.get<EvidenceItem>(`/evidence/${id}`);
    return response.data;
  }

  /**
   * Create a new evidence item
   */
  async createEvidence(data: CreateEvidenceRequest): Promise<EvidenceItem> {
    const response = await apiClient.post<EvidenceItem>('/evidence', data);
    return response.data;
  }

  /**
   * Update an evidence item
   */
  async updateEvidence(id: string, data: UpdateEvidenceRequest): Promise<EvidenceItem> {
    const response = await apiClient.patch<EvidenceItem>(`/evidence/${id}`, data);
    return response.data;
  }

  /**
   * Delete an evidence item
   */
  async deleteEvidence(id: string): Promise<void> {
    await apiClient.delete(`/evidence/${id}`);
  }

  /**
   * Bulk update evidence status
   */
  async bulkUpdateEvidence(data: BulkUpdateEvidenceRequest): Promise<{
    updated_count: number;
    failed_count: number;
    failed_ids?: string[];
  }> {
    const response = await apiClient.post<{
      updated_count: number;
      failed_count: number;
      failed_ids?: string[];
    }>('/evidence/bulk-update', data);
    return response.data;
  }

  /**
   * Upload file for evidence
   */
  async uploadEvidenceFile(id: string, file: File, _onProgress?: (progress: number) => void): Promise<EvidenceItem> {
    const response = await apiClient.upload<EvidenceItem>(`/evidence/${id}/upload`, file, _onProgress);
    return response.data;
  }

  /**
   * Configure evidence automation
   */
  async configureEvidenceAutomation(id: string, config: EvidenceAutomationConfig): Promise<{
    configuration_successful: boolean;
    automation_enabled: boolean;
    test_connection: boolean;
    next_collection?: string;
  }> {
    const response = await apiClient.post<{
      configuration_successful: boolean;
      automation_enabled: boolean;
      test_connection: boolean;
      next_collection?: string;
    }>(`/evidence/${id}/automation`, config);
    return response.data;
  }

  /**
   * Get evidence dashboard for a framework
   */
  async getEvidenceDashboard(frameworkId: string): Promise<{
    total_controls: number;
    covered_controls: number;
    pending_evidence: number;
    approved_evidence: number;
    coverage_percentage: number;
    by_type: Record<string, number>;
    recent_activity: UnknownRecord[];
  }> {
    const response = await apiClient.get<UnknownRecord>(`/evidence/dashboard/${frameworkId}`);
    return response.data;
  }

  /**
   * Classify evidence using AI
   */
  async classifyEvidence(id: string, request?: EvidenceClassificationRequest): Promise<{
    evidence_id: string;
    current_type: string;
    ai_classification: UnknownRecord;
    apply_suggestion: boolean;
    confidence: number;
    suggested_controls: string[];
    reasoning: string;
  }> {
    const response = await apiClient.post<UnknownRecord>(`/evidence/${id}/classify`, request || {});
    return response.data;
  }

  /**
   * Search evidence
   */
  async searchEvidence(query: string): Promise<EvidenceItem[]> {
    const response = await apiClient.get<EvidenceItem[]>(`/evidence/search?q=${encodeURIComponent(query)}`);
    return response.data;
  }

  /**
   * Get evidence requirements for a framework
   */
  async getEvidenceRequirements(frameworkId: string): Promise<{
    framework: string;
    total_requirements: number;
    requirements: Array<{
      control_id: string;
      control_name: string;
      evidence_types: string[];
      priority: string;
      description: string;
    }>;
  }> {
    const response = await apiClient.get<UnknownRecord>(`/evidence/requirements/${frameworkId}`);
    return response.data;
  }

  /**
   * Get evidence quality analysis
   */
  async getEvidenceQualityAnalysis(id: string): Promise<{
    quality_score: number;
    completeness: number;
    relevance: number;
    recency: number;
    suggestions: string[];
  }> {
    const response = await apiClient.get<UnknownRecord>(`/evidence/${id}/quality`);
    return response.data;
  }
}

export const evidenceService = new EvidenceService();