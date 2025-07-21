import { apiClient } from './client';

import type { Assessment, AssessmentQuestion, AssessmentResponse } from '@/types/api';

export interface CreateAssessmentRequest {
  business_profile_id: string;
  framework_id: string;
  assessment_type?: 'quick' | 'comprehensive';
}

export interface UpdateAssessmentRequest {
  status?: string;
  responses?: Record<string, any>;
}

export interface SubmitAssessmentAnswerRequest {
  question_id: string;
  answer: any;
  metadata?: Record<string, any>;
}

class AssessmentService {
  /**
   * Get all assessments for the current user
   */
  async getAssessments(params?: {
    business_profile_id?: string;
    framework_id?: string;
    status?: string;
    page?: number;
    page_size?: number;
  }): Promise<{ items: Assessment[]; total: number }> {
    const response = await apiClient.get<{ items: Assessment[]; total: number }>('/assessments', {
      params,
    });
    return response.data;
  }

  /**
   * Get a specific assessment by ID
   */
  async getAssessment(id: string): Promise<Assessment> {
    const response = await apiClient.get<Assessment>(`/assessments/${id}`);
    return response.data;
  }

  /**
   * Create a new assessment
   */
  async createAssessment(data: CreateAssessmentRequest): Promise<Assessment> {
    const response = await apiClient.post<Assessment>('/assessments', data);
    return response.data;
  }

  /**
   * Update an assessment
   */
  async updateAssessment(id: string, data: UpdateAssessmentRequest): Promise<Assessment> {
    const response = await apiClient.patch<Assessment>(`/assessments/${id}`, data);
    return response.data;
  }

  /**
   * Delete an assessment
   */
  async deleteAssessment(id: string): Promise<void> {
    await apiClient.delete(`/assessments/${id}`);
  }

  /**
   * Get assessment questions
   */
  async getAssessmentQuestions(assessmentId: string): Promise<AssessmentQuestion[]> {
    const response = await apiClient.get<AssessmentQuestion[]>(
      `/assessments/${assessmentId}/questions`,
    );
    return response.data;
  }

  /**
   * Submit an answer for an assessment question
   */
  async submitAssessmentAnswer(
    assessmentId: string,
    data: SubmitAssessmentAnswerRequest,
  ): Promise<AssessmentResponse> {
    const response = await apiClient.post<AssessmentResponse>(
      `/assessments/${assessmentId}/answers`,
      data,
    );
    return response.data;
  }

  /**
   * Complete an assessment
   */
  async completeAssessment(id: string): Promise<Assessment> {
    const response = await apiClient.post<Assessment>(`/assessments/${id}/complete`);
    return response.data;
  }

  /**
   * Get assessment results
   */
  async getAssessmentResults(id: string): Promise<any> {
    const response = await apiClient.get<any>(`/assessments/${id}/results`);
    return response.data;
  }

  /**
   * Get quick assessment for a framework
   */
  async getQuickAssessment(businessProfileId: string, frameworkId: string): Promise<any> {
    const response = await apiClient.post<any>('/assessments/quick', {
      business_profile_id: businessProfileId,
      framework_id: frameworkId,
    });
    return response.data;
  }
}

export const assessmentService = new AssessmentService();
