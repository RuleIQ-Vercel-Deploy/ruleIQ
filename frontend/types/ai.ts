/**
 * Shared type definitions for AI-related functionality
 */

import { type AssessmentProgress } from "@/lib/assessment-engine/types";
import { type BusinessProfile } from "@/types/auth";

/**
 * User context for AI requests - provides business and assessment context
 */
export interface UserContext {
  business_profile?: Partial<BusinessProfile>;
  current_answers?: Record<string, any>;
  assessment_progress?: Partial<AssessmentProgress>;
}

/**
 * AI service error types for better error handling
 */
export type AIErrorType = 
  | 'timeout'
  | 'quota_exceeded'
  | 'service_unavailable'
  | 'content_filtered'
  | 'parsing_error'
  | 'validation_error'
  | 'unknown_error';

/**
 * AI service error with additional context
 */
export interface AIError extends Error {
  type: AIErrorType;
  code?: string;
  context?: Record<string, any>;
  retryable?: boolean;
}

/**
 * AI request configuration
 */
export interface AIRequestConfig {
  timeout?: number;
  retries?: number;
  priority?: number;
  enableCache?: boolean;
  fallbackToMock?: boolean;
}

/**
 * AI response metadata
 */
export interface AIResponseMetadata {
  confidence_score: number;
  response_time_ms: number;
  model_used: string;
  cached: boolean;
  tokens_used?: number;
  cost_estimate?: number;
}

/**
 * Base AI response interface
 */
export interface BaseAIResponse {
  metadata: AIResponseMetadata;
  request_id: string;
  generated_at: string;
}

/**
 * AI help response for assessment questions
 */
export interface AIHelpResponse extends BaseAIResponse {
  guidance: string;
  related_topics?: string[];
  follow_up_suggestions?: string[];
  source_references?: string[];
}

/**
 * AI follow-up question
 */
export interface AIFollowUpQuestion {
  id: string;
  text: string;
  type: 'radio' | 'checkbox' | 'text' | 'textarea' | 'scale';
  options?: Array<{
    value: string;
    label: string;
    description?: string;
  }>;
  reasoning: string;
  priority: 'high' | 'medium' | 'low';
  metadata?: Record<string, any>;
}

/**
 * AI recommendation
 */
export interface AIRecommendation {
  id: string;
  title: string;
  description: string;
  priority: 'immediate' | 'short_term' | 'medium_term' | 'long_term';
  effort_estimate: string;
  impact_score: number;
  resources?: string[];
  related_frameworks?: string[];
  implementation_steps?: string[];
  success_metrics?: string[];
}

/**
 * AI analysis response for assessment results
 */
export interface AIAnalysisResponse extends BaseAIResponse {
  gaps: Array<{
    id: string;
    section: string;
    severity: 'critical' | 'high' | 'medium' | 'low';
    description: string;
    impact: string;
    current_state: string;
    target_state: string;
  }>;
  recommendations: AIRecommendation[];
  risk_assessment: {
    overall_risk_level: 'low' | 'medium' | 'high' | 'critical';
    risk_score: number;
    key_risk_areas: string[];
  };
  compliance_insights: {
    maturity_level: string;
    score_breakdown: Record<string, number>;
    improvement_priority: string[];
  };
  evidence_requirements: Array<{
    priority: 'high' | 'medium' | 'low';
    evidence_type: string;
    description: string;
    control_mapping: string[];
  }>;
}

/**
 * AI service status
 */
export interface AIServiceStatus {
  available: boolean;
  last_check: string;
  response_time_ms?: number;
  error?: string;
  quota_remaining?: number;
  rate_limit_reset?: string;
}

/**
 * AI feature flags
 */
export interface AIFeatureFlags {
  help_tooltips: boolean;
  follow_up_questions: boolean;
  personalized_recommendations: boolean;
  conversational_mode: boolean;
  real_time_scoring: boolean;
  smart_adaptation: boolean;
}

/**
 * AI configuration
 */
export interface AIConfig {
  enabled: boolean;
  features: AIFeatureFlags;
  endpoints: {
    help: string;
    analysis: string;
    recommendations: string;
    follow_up: string;
  };
  timeouts: {
    help: number;
    analysis: number;
    recommendations: number;
  };
  retry_config: {
    max_attempts: number;
    base_delay: number;
    max_delay: number;
  };
}

/**
 * Type guards for AI responses
 */
export function isAIError(error: any): error is AIError {
  return error && typeof error === 'object' && 'type' in error && 'message' in error;
}

export function isAIHelpResponse(response: any): response is AIHelpResponse {
  return response && 
         typeof response === 'object' && 
         'guidance' in response && 
         'metadata' in response;
}

export function isAIAnalysisResponse(response: any): response is AIAnalysisResponse {
  return response && 
         typeof response === 'object' && 
         'gaps' in response && 
         'recommendations' in response && 
         'metadata' in response;
}
