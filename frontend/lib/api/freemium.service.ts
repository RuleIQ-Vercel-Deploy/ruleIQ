/**
 * FreemiumService - API client for public assessment endpoints
 * Handles email capture, session management, and assessment flow
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Validate email format
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Get severity color for UI display
 */
export const getSeverityColor = (severity: 'low' | 'medium' | 'high' | 'critical'): string => {
  const colors = {
    low: 'text-blue-600 bg-blue-50',
    medium: 'text-yellow-600 bg-yellow-50',
    high: 'text-orange-600 bg-orange-50',
    critical: 'text-red-600 bg-red-50'
  };
  return colors[severity] || colors.medium;
};

/**
 * Get risk score color for UI display
 */
export const getRiskScoreColor = (score: number): string => {
  if (score >= 80) return 'text-red-600';
  if (score >= 60) return 'text-orange-600';
  if (score >= 40) return 'text-yellow-600';
  return 'text-green-600';
};

/**
 * Format risk score for display
 */
export const formatRiskScore = (score: number): string => {
  return `${score.toFixed(0)}%`;
};

/**
 * Extract UTM parameters from URL
 */
export const extractUtmParams = () => {
  if (typeof window === 'undefined') return {};
  
  const urlParams = new URLSearchParams(window.location.search);
  return {
    utm_source: urlParams.get('utm_source'),
    utm_medium: urlParams.get('utm_medium'),
    utm_campaign: urlParams.get('utm_campaign'),
    utm_term: urlParams.get('utm_term'),
    utm_content: urlParams.get('utm_content'),
  };
};

// ============================================================================
// TYPE EXPORTS
// ============================================================================

export type { ComplianceGap, AssessmentResultsResponse as FreemiumResultsResponse } from '@/types/freemium';

// Additional type aliases for backward compatibility
export interface FreemiumEmailCaptureRequest extends LeadCaptureRequest {}
export interface FreemiumEmailCaptureResponse extends LeadResponse { 
  token?: string; 
}

export interface FreemiumAssessmentStartResponse {
  session_id: string;
  session_token: string;
  question_id: string;
  question_text: string;
  question_type: 'multiple_choice' | 'yes_no' | 'text' | 'scale';
  question_context?: string;
  answer_options?: string[];
  progress: {
    current_question: number;
    total_questions_estimate: number;
    progress_percentage: number;
  };
  personalization_applied: boolean;
  expires_at: string;
}

export interface FreemiumAnswerRequest {
  question_id: string;
  answer: string;
  answer_confidence?: 'low' | 'medium' | 'high';
  time_spent_seconds?: number;
  skip_reason?: string;
}

export interface FreemiumAnswerResponse {
  next_question_id?: string;
  next_question_text?: string;
  next_question_type?: 'multiple_choice' | 'yes_no' | 'text' | 'scale';
  next_question_context?: string;
  next_answer_options?: string[];
  progress: {
    current_question: number;
    total_questions_estimate: number;
    progress_percentage: number;
  };
  is_complete: boolean;
  assessment_complete?: boolean;
  redirect_to_results?: boolean;
  session_token: string;
  answer_recorded: boolean;
  validation_errors?: string[];
}

export interface ConversionTrackingRequest {
  event_type: string;
  metadata?: Record<string, any>;
}

export interface ConversionTrackingResponse {
  event_id: string;
  score_applied: number;
  total_score: number;
  engagement_level: 'low' | 'medium' | 'high';
  conversion_probability: number;
  next_recommended_action: string;
  recorded_at: string;
}

export interface TrialOffer {
  title: string;
  description: string;
  cta_text: string;
  discount_percentage?: number;
  valid_until?: string;
}

// Types
export interface LeadCaptureRequest {
  email: string;
  first_name?: string;
  last_name?: string;
  company_name?: string;
  company_size?: '1-10' | '11-50' | '51-200' | '201-500' | '500+';
  industry?: string;
  phone?: string;
  
  // UTM tracking
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  utm_term?: string;
  utm_content?: string;
  
  // Context
  referrer_url?: string;
  landing_page?: string;
  user_agent?: string;
  
  // Consent
  marketing_consent?: boolean;
  newsletter_subscribed?: boolean;
}

export interface LeadResponse {
  lead_id: string;
  email: string;
  lead_score: number;
  lead_status: string;
  created_at: string;
}

export interface SessionStartRequest {
  lead_email: string;
  business_type: string;
  company_size?: '1-10' | '11-50' | '51-200' | '201-500' | '500+';
  assessment_type?: 'general' | 'gdpr' | 'security' | 'compliance';
  industry_focus?: string;
  compliance_frameworks?: string[];
  priority_areas?: string[];
}

export interface SessionResponse {
  session_id: string;
  session_token: string;
  lead_id: string;
  status: string;
  progress_percentage: number;
  current_question_id?: string;
  total_questions: number;
  questions_answered: number;
  expires_at: string;
  created_at: string;
}

export interface AnswerSubmissionRequest {
  question_id: string;
  answer: string;
  answer_confidence?: 'low' | 'medium' | 'high';
  time_spent_seconds?: number;
  skip_reason?: string;
}

export interface AssessmentResultsResponse {
  session_id: string;
  compliance_score?: number;
  risk_level: string;
  completed_at?: string;
  recommendations?: any[];
  gaps?: any[];
  next_steps?: any[];
}

class FreemiumService {
  private baseUrl = `${API_BASE}/api/v1/freemium`;

  /**
   * Capture email and lead information
   */
  async captureEmail(data: LeadCaptureRequest): Promise<LeadResponse> {
    const response = await fetch(`${this.baseUrl}/leads`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...data,
        user_agent: navigator.userAgent,
        referrer_url: document.referrer,
        landing_page: window.location.href,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(error.detail || 'Failed to capture email');
    }

    return response.json();
  }

  /**
   * Start a new assessment session
   */
  async startAssessment(data: SessionStartRequest): Promise<SessionResponse> {
    const response = await fetch(`${this.baseUrl}/sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(error.detail || 'Failed to start assessment');
    }

    return response.json();
  }

  /**
   * Get session progress
   */
  async getSessionProgress(sessionToken: string): Promise<SessionResponse> {
    const response = await fetch(`${this.baseUrl}/sessions/${sessionToken}`, {
      method: 'GET',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(error.detail || 'Failed to get session progress');
    }

    return response.json();
  }

  /**
   * Submit an answer
   */
  async submitAnswer(sessionToken: string, data: AnswerSubmissionRequest): Promise<any> {
    const response = await fetch(`${this.baseUrl}/sessions/${sessionToken}/answers`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(error.detail || 'Failed to submit answer');
    }

    return response.json();
  }

  /**
   * Get assessment results
   */
  async getResults(sessionToken: string): Promise<AssessmentResultsResponse> {
    const response = await fetch(`${this.baseUrl}/sessions/${sessionToken}/results`, {
      method: 'GET',
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(error.detail || 'Failed to get results');
    }

    return response.json();
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<any> {
    const response = await fetch(`${this.baseUrl}/health`, {
      method: 'GET',
    });

    if (!response.ok) {
      throw new Error('Freemium API is not available');
    }

    return response.json();
  }
}

export const freemiumService = new FreemiumService();

// ============================================================================
// BACKWARD COMPATIBILITY API FUNCTIONS
// ============================================================================

export const captureEmail = (data: FreemiumEmailCaptureRequest): Promise<FreemiumEmailCaptureResponse> =>
  freemiumService.captureEmail(data);

export const startAssessment = (token: string): Promise<FreemiumAssessmentStartResponse> =>
  freemiumService.startAssessment({ lead_email: token, business_type: 'default' }) as any;

export const answerQuestion = (token: string, answerData: FreemiumAnswerRequest): Promise<FreemiumAnswerResponse> =>
  freemiumService.submitAnswer(token, answerData) as any;

export const getResults = (token: string): Promise<AssessmentResultsResponse> =>
  freemiumService.getResults(token);

export const trackConversion = (token: string, data: ConversionTrackingRequest): Promise<ConversionTrackingResponse> =>
  Promise.resolve({
    event_id: 'mock',
    score_applied: 0,
    total_score: 0,
    engagement_level: 'low' as const,
    conversion_probability: 0,
    next_recommended_action: 'continue',
    recorded_at: new Date().toISOString(),
  });