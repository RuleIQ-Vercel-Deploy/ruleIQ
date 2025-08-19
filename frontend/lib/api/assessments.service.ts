import { apiClient } from './client';

import type { Assessment, AssessmentQuestion, AssessmentResponse, PaginatedResponse, SubmitResponseRequest } from '@/types/api';

export interface CreateAssessmentRequest {
  business_profile_id: string;
  framework_id: string;
  assessment_type?: string;
  metadata?: Record<string, any>;
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
  }): Promise<PaginatedResponse<Assessment>> {
    const params_with_defaults = {
      page: 1,
      page_size: 20,
      ...params,
    };
    
    const response = await apiClient.get<{ items: Assessment[]; total: number }>('/assessments', {
      params: params_with_defaults,
    });
    
    // Transform to proper PaginatedResponse
    return {
      items: response.items,
      total: response.total,
      page: params_with_defaults.page,
      page_size: params_with_defaults.page_size,
      total_pages: Math.ceil(response.total / params_with_defaults.page_size),
    };
  }

  /**
   * Get a specific assessment by ID
   */
  async getAssessment(id: string): Promise<Assessment> {
    const response = await apiClient.get<Assessment>(`/assessments/${id}`);
    return response;
  }

  /**
   * Create a new assessment
   */
  async createAssessment(data: CreateAssessmentRequest): Promise<Assessment> {
    const response = await apiClient.post<Assessment>('/assessments', data);
    return response;
  }

  /**
   * Update an assessment
   */
  async updateAssessment(id: string, data: UpdateAssessmentRequest): Promise<Assessment> {
    const response = await apiClient.patch<Assessment>(`/assessments/${id}`, data);
    return response;
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
    return response;
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
    return response;
  }

  /**
   * Complete an assessment
   */
  async completeAssessment(id: string): Promise<Assessment> {
    const response = await apiClient.post<Assessment>(`/assessments/${id}/complete`);
    return response;
  }

  /**
   * Get assessment results
   */
  async getAssessmentResults(id: string): Promise<any> {
    const response = await apiClient.get<any>(`/assessments/${id}/results`);
    return response;
  }

  /**
   * Get quick assessment for a framework
   */
  async getQuickAssessment(businessProfileId: string, frameworkId: string): Promise<any> {
    const response = await apiClient.post<any>('/assessments/quick', {
      business_profile_id: businessProfileId,
      framework_id: frameworkId,
    });
    return response;
  }

  /**
   * Submit a response to an assessment
   */
  async submitResponse(assessmentId: string, data: SubmitResponseRequest): Promise<AssessmentResponse> {
    const response = await apiClient.post<AssessmentResponse>(
      `/assessments/${assessmentId}/responses`,
      data,
    );
    return response;
  }

  /**
   * Start a quick assessment
   */
  async startQuickAssessment(businessProfileId: string, frameworkId: string): Promise<Assessment> {
    const response = await apiClient.post<Assessment>('/assessments/quick/start', {
      business_profile_id: businessProfileId,
      framework_id: frameworkId,
    });
    return response;
  }
}

export const assessmentService = new AssessmentService();
