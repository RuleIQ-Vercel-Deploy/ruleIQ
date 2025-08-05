import { apiClient } from './client';

// Types for freemium assessment flow
export interface FreemiumEmailCaptureRequest {
  email: string;
  utm_source?: string;
  utm_campaign?: string;
  consent_marketing: boolean;
}

export interface FreemiumEmailCaptureResponse {
  success: boolean;
  token: string;
  message?: string;
}

export interface FreemiumAssessmentStartResponse {
  question_id: string;
  question_text: string;
  question_type: 'multiple_choice' | 'text' | 'boolean' | 'scale';
  options?: string[];
  progress: number;
  total_questions_estimate?: number;
}

export interface FreemiumAnswerRequest {
  question_id: string;
  answer: string | number | boolean;
}

export interface FreemiumAnswerResponse {
  question_id?: string;
  question_text?: string;
  question_type?: 'multiple_choice' | 'text' | 'boolean' | 'scale';
  options?: string[];
  progress: number;
  total_questions_estimate?: number;
  assessment_complete?: boolean;
  redirect_to_results?: boolean;
}

export interface ComplianceGap {
  framework: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  gap_description: string;
  impact_score: number;
  category?: string;
}

export interface TrialOffer {
  discount_percentage: number;
  trial_days: number;
  cta_text: string;
  payment_link: string;
  features_included?: string[];
}

export interface FreemiumResultsResponse {
  compliance_gaps: ComplianceGap[];
  risk_score: number;
  recommendations: string[];
  trial_offer: TrialOffer;
  assessment_summary?: {
    business_type: string;
    company_size: string;
    frameworks_needed: string[];
    key_risks: string[];
  };
}

export interface ConversionTrackingRequest {
  event_type: 'cta_click' | 'email_shared' | 'page_view' | 'trial_started';
  cta_text?: string;
  conversion_value?: number;
  additional_data?: Record<string, any>;
}

export interface ConversionTrackingResponse {
  success: boolean;
  tracking_id?: string;
}

/**
 * Capture email for freemium assessment with UTM tracking
 */
export const captureEmail = async (
  data: FreemiumEmailCaptureRequest
): Promise<FreemiumEmailCaptureResponse> => {
  try {
    const response = await apiClient.publicPost<FreemiumEmailCaptureResponse>(
      '/freemium/capture-email',
      data
    );
    return response;
  } catch (error: any) {
    // Handle specific error cases
    if (error.response?.status === 400) {
      throw new Error(error.response.data?.message || 'Invalid email or parameters');
    }
    if (error.response?.status === 409) {
      throw new Error('Email already registered. Please use a different email.');
    }
    throw new Error('Failed to capture email. Please try again.');
  }
};

/**
 * Start AI-driven assessment session
 */
export const startAssessment = async (
  token: string
): Promise<FreemiumAssessmentStartResponse> => {
  try {
    const response = await apiClient.publicPost<FreemiumAssessmentStartResponse>(
      '/freemium/start-assessment',
      { token }
    );
    return response;
  } catch (error: any) {
    if (error.response?.status === 404) {
      throw new Error('Assessment session not found. Please start over.');
    }
    if (error.response?.status === 410) {
      throw new Error('Assessment session has expired. Please start over.');
    }
    throw new Error('Failed to start assessment. Please try again.');
  }
};

/**
 * Submit answer and get next AI-generated question
 */
export const answerQuestion = async (
  token: string,
  answerData: FreemiumAnswerRequest
): Promise<FreemiumAnswerResponse> => {
  try {
    const response = await apiClient.publicPost<FreemiumAnswerResponse>(
      '/freemium/answer-question',
      {
        token,
        ...answerData,
      }
    );
    return response;
  } catch (error: any) {
    if (error.response?.status === 400) {
      throw new Error('Invalid answer format. Please try again.');
    }
    if (error.response?.status === 404) {
      throw new Error('Question not found. Please refresh and try again.');
    }
    if (error.response?.status === 410) {
      throw new Error('Assessment session has expired. Please start over.');
    }
    throw new Error('Failed to submit answer. Please try again.');
  }
};

/**
 * Get freemium assessment results
 */
export const getResults = async (
  token: string
): Promise<FreemiumResultsResponse> => {
  try {
    const response = await apiClient.publicGet<FreemiumResultsResponse>(
      `/freemium/results/${token}`
    );
    return response;
  } catch (error: any) {
    if (error.response?.status === 404) {
      throw new Error('Results not found. Please complete the assessment first.');
    }
    if (error.response?.status === 410) {
      throw new Error('Results have expired. Please take the assessment again.');
    }
    throw new Error('Failed to load results. Please try again.');
  }
};

/**
 * Track conversion events for lead scoring
 */
export const trackConversion = async (
  token: string,
  trackingData: ConversionTrackingRequest
): Promise<ConversionTrackingResponse> => {
  try {
    const response = await apiClient.publicPost<ConversionTrackingResponse>(
      '/freemium/track-conversion',
      {
        token,
        ...trackingData,
      }
    );
    return response;
  } catch (error: any) {
    // Conversion tracking failures should not break the user experience
    console.warn('Conversion tracking failed:', error);
    return { success: false };
  }
};

// Utility functions for freemium flow
export const extractUtmParams = () => {
  if (typeof window === 'undefined') return { utm_source: undefined, utm_campaign: undefined };
  
  const urlParams = new URLSearchParams(window.location.search);
  return {
    utm_source: urlParams.get('utm_source') || undefined,
    utm_campaign: urlParams.get('utm_campaign') || undefined,
  };
};

export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const getSeverityColor = (severity: ComplianceGap['severity']): string => {
  switch (severity) {
    case 'critical':
      return 'text-red-600 bg-red-50 border-red-200';
    case 'high':
      return 'text-orange-600 bg-orange-50 border-orange-200';
    case 'medium':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200';
    case 'low':
      return 'text-green-600 bg-green-50 border-green-200';
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200';
  }
};

export const getRiskScoreColor = (score: number): string => {
  if (score >= 8) return 'text-red-600';
  if (score >= 6) return 'text-orange-600';
  if (score >= 4) return 'text-yellow-600';
  return 'text-green-600';
};

export const formatRiskScore = (score: number): string => {
  return `${score.toFixed(1)}/10`;
};