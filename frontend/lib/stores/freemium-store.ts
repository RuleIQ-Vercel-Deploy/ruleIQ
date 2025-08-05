import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  FreemiumStore,
  FreemiumState,
  FreemiumActions,
  LeadCaptureRequest,
  AssessmentStartRequest,
  AssessmentAnswerRequest,
  ResultsGenerationRequest,
  AssessmentQuestion,
  AssessmentResponse,
  AssessmentProgress,
  FreemiumSession,
  AssessmentResultsResponse,
  TrackingMetadata,
} from '@/types/freemium';

// ============================================================================
// INITIAL STATE
// ============================================================================

const initialState: FreemiumState = {
  // Lead information
  leadId: null,
  email: null,
  leadScore: 0,
  leadStatus: 'new',
  
  // Session management
  session: null,
  sessionToken: null,
  sessionExpiry: null,
  
  // Assessment state
  currentQuestion: null,
  responses: [],
  progress: {
    current_question: 0,
    total_questions_estimate: 10,
    progress_percentage: 0,
    questions_answered: 0,
    time_elapsed_seconds: 0,
  },
  isAssessmentStarted: false,
  isAssessmentComplete: false,
  
  // Results
  results: null,
  hasViewedResults: false,
  
  // UI state
  isLoading: false,
  error: null,
  
  // Consent and compliance
  hasMarketingConsent: false,
  hasNewsletterConsent: true,
  consentDate: null,
  
  // Analytics and tracking
  timeStarted: null,
  totalTimeSpent: 0,
  analyticsEvents: [],
};

// ============================================================================
// API INTEGRATION HELPERS
// ============================================================================

const apiCall = async (endpoint: string, data?: any, method: string = 'POST') => {
  const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const url = `${baseUrl}/api/freemium${endpoint}`;
  
  const response = await fetch(url, {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
    ...(data && { body: JSON.stringify(data) }),
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
  }
  
  return response.json();
};

// ============================================================================
// STORE IMPLEMENTATION
// ============================================================================

export const useFreemiumStore = create<FreemiumStore>()(
  persist(
    (set, get) => ({
      ...initialState,
      
      // ========================================================================
      // LEAD MANAGEMENT
      // ========================================================================
      
      captureLead: async (leadData: LeadCaptureRequest) => {
        try {
          set({ isLoading: true, error: null });
          
          const response = await apiCall('/leads', leadData);
          
          set({
            leadId: response.lead_id,
            email: leadData.email,
            leadScore: response.lead_score || 0,
            leadStatus: response.lead_status || 'new',
            hasMarketingConsent: leadData.marketing_consent || false,
            hasNewsletterConsent: leadData.newsletter_subscribed !== false,
            consentDate: leadData.marketing_consent ? new Date().toISOString() : null,
            isLoading: false,
          });
          
          // Track lead capture event
          get().trackEvent('lead_captured', {
            email: leadData.email,
            utm_source: leadData.utm_source,
            utm_campaign: leadData.utm_campaign,
          });
          
        } catch (error) {
          set({ 
            isLoading: false, 
            error: error instanceof Error ? error.message : 'Failed to capture lead'
          });
          throw error;
        }
      },
      
      setLeadInfo: (leadId: string, email: string) => {
        set({ leadId, email });
      },
      
      updateLeadScore: (score: number) => {
        set({ leadScore: score });
      },
      
      // ========================================================================
      // SESSION MANAGEMENT
      // ========================================================================
      
      startAssessment: async (startData: AssessmentStartRequest) => {
        try {
          set({ isLoading: true, error: null });
          
          const response = await apiCall('/assessment/start', startData);
          
          const session: FreemiumSession = {
            session_id: response.session_id,
            session_token: response.session_token,
            lead_id: startData.lead_id,
            status: 'started',
            created_at: new Date().toISOString(),
            expires_at: response.expires_at,
          };
          
          const question: AssessmentQuestion = {
            question_id: response.question_id,
            question_text: response.question_text,
            question_type: response.question_type,
            question_context: response.question_context,
            answer_options: response.answer_options,
            is_required: true,
          };
          
          const progress: AssessmentProgress = {
            current_question: response.progress.current_question,
            total_questions_estimate: response.progress.total_questions_estimate,
            progress_percentage: response.progress.progress_percentage,
            questions_answered: 0,
            time_elapsed_seconds: 0,
          };
          
          set({
            session,
            sessionToken: response.session_token,
            sessionExpiry: response.expires_at,
            currentQuestion: question,
            progress,
            isAssessmentStarted: true,
            timeStarted: new Date().toISOString(),
            isLoading: false,
          });
          
          get().trackEvent('assessment_started', {
            session_id: response.session_id,
            business_type: startData.business_type,
          });
          
        } catch (error) {
          set({ 
            isLoading: false, 
            error: error instanceof Error ? error.message : 'Failed to start assessment'
          });
          throw error;
        }
      },
      
      loadSession: async (sessionToken: string) => {
        try {
          set({ isLoading: true, error: null });
          
          // In a real implementation, this would load session from backend
          // For now, just validate the token format
          if (!sessionToken || sessionToken.length < 10) {
            throw new Error('Invalid session token');
          }
          
          set({
            sessionToken,
            isLoading: false,
          });
          
        } catch (error) {
          set({ 
            isLoading: false, 
            error: error instanceof Error ? error.message : 'Failed to load session'
          });
          throw error;
        }
      },
      
      clearSession: () => {
        set({
          session: null,
          sessionToken: null,
          sessionExpiry: null,
          currentQuestion: null,
          responses: [],
          isAssessmentStarted: false,
          isAssessmentComplete: false,
          results: null,
          hasViewedResults: false,
          timeStarted: null,
          totalTimeSpent: 0,
          analyticsEvents: [],
        });
      },
      
      // ========================================================================
      // QUESTION FLOW
      // ========================================================================
      
      submitAnswer: async (answerData: AssessmentAnswerRequest) => {
        try {
          set({ isLoading: true, error: null });
          
          const response = await apiCall('/assessment/answer', answerData);
          
          // Record the response
          const newResponse: AssessmentResponse = {
            question_id: answerData.question_id,
            answer: answerData.answer,
            answered_at: new Date().toISOString(),
            time_spent_seconds: answerData.time_spent_seconds,
            confidence_level: answerData.confidence_level,
          };
          
          const currentResponses = get().responses;
          const updatedResponses = [...currentResponses, newResponse];
          
          // Update progress
          const updatedProgress: AssessmentProgress = {
            current_question: response.progress.current_question,
            total_questions_estimate: response.progress.total_questions_estimate,
            progress_percentage: response.progress.progress_percentage,
            questions_answered: updatedResponses.length,
            time_elapsed_seconds: get().progress.time_elapsed_seconds + (answerData.time_spent_seconds || 0),
          };
          
          set({
            responses: updatedResponses,
            progress: updatedProgress,
            isLoading: false,
          });
          
          // Handle next question or completion
          if (response.is_complete) {
            set({ isAssessmentComplete: true });
            get().trackEvent('assessment_completed', {
              questions_answered: updatedResponses.length,
              completion_percentage: response.progress.progress_percentage,
            });
          } else if (response.next_question_id) {
            const nextQuestion: AssessmentQuestion = {
              question_id: response.next_question_id,
              question_text: response.next_question_text!,
              question_type: response.next_question_type!,
              question_context: response.next_question_context,
              answer_options: response.next_answer_options,
              is_required: true,
            };
            set({ currentQuestion: nextQuestion });
          }
          
        } catch (error) {
          set({ 
            isLoading: false, 
            error: error instanceof Error ? error.message : 'Failed to submit answer'
          });
          throw error;
        }
      },
      
      skipQuestion: () => {
        // Implementation for skipping questions
        get().trackEvent('question_skipped', {
          question_id: get().currentQuestion?.question_id,
        });
      },
      
      goToPreviousQuestion: () => {
        // Implementation for going back to previous question
        get().trackEvent('question_back', {
          question_id: get().currentQuestion?.question_id,
        });
      },
      
      // ========================================================================
      // RESULTS
      // ========================================================================
      
      generateResults: async (includeDetails: boolean = true) => {
        try {
          const sessionToken = get().sessionToken;
          if (!sessionToken) {
            throw new Error('No active session');
          }
          
          set({ isLoading: true, error: null });
          
          const requestData: ResultsGenerationRequest = {
            session_token: sessionToken,
            include_recommendations: includeDetails,
            include_detailed_analysis: includeDetails,
          };
          
          const response = await apiCall('/assessment/results', requestData);
          
          set({
            results: response,
            isLoading: false,
          });
          
          get().trackEvent('results_generated', {
            compliance_score: response.compliance_score,
            risk_score: response.risk_score,
          });
          
        } catch (error) {
          set({ 
            isLoading: false, 
            error: error instanceof Error ? error.message : 'Failed to generate results'
          });
          throw error;
        }
      },
      
      markResultsViewed: () => {
        set({ hasViewedResults: true });
        get().trackEvent('results_viewed', {
          timestamp: new Date().toISOString(),
        });
      },
      
      // ========================================================================
      // PROGRESS TRACKING
      // ========================================================================
      
      updateProgress: (progressUpdate: Partial<AssessmentProgress>) => {
        const currentProgress = get().progress;
        set({
          progress: {
            ...currentProgress,
            ...progressUpdate,
          },
        });
      },
      
      trackTimeSpent: (seconds: number) => {
        const currentTotal = get().totalTimeSpent;
        set({ totalTimeSpent: currentTotal + seconds });
      },
      
      // ========================================================================
      // CONSENT MANAGEMENT
      // ========================================================================
      
      setMarketingConsent: (consent: boolean) => {
        set({ 
          hasMarketingConsent: consent,
          consentDate: consent ? new Date().toISOString() : null,
        });
        get().trackEvent('consent_updated', { marketing_consent: consent });
      },
      
      setNewsletterConsent: (consent: boolean) => {
        set({ hasNewsletterConsent: consent });
        get().trackEvent('consent_updated', { newsletter_consent: consent });
      },
      
      updateConsent: (marketing: boolean, newsletter: boolean) => {
        set({ 
          hasMarketingConsent: marketing,
          hasNewsletterConsent: newsletter,
          consentDate: marketing ? new Date().toISOString() : null,
        });
        get().trackEvent('consent_updated', { 
          marketing_consent: marketing, 
          newsletter_consent: newsletter 
        });
      },
      
      // ========================================================================
      // ANALYTICS
      // ========================================================================
      
      trackEvent: (eventType: string, metadata?: Record<string, any>) => {
        const event = {
          event_type: eventType,
          timestamp: new Date().toISOString(),
          ...(metadata && { metadata }),
        };
        
        const currentEvents = get().analyticsEvents;
        set({
          analyticsEvents: [...currentEvents, event],
        });
      },
      
      recordBehavioralEvent: async (eventData: any) => {
        try {
          await apiCall('/events', eventData);
        } catch (error) {
          console.warn('Failed to record behavioral event:', error);
        }
      },
      
      // ========================================================================
      // UTILITY METHODS
      // ========================================================================
      
      isSessionExpired: () => {
        const sessionExpiry = get().sessionExpiry;
        if (!sessionExpiry) return false;
        return new Date() > new Date(sessionExpiry);
      },
      
      canStartAssessment: () => {
        const state = get();
        return !!(state.leadId && state.hasMarketingConsent && !state.isSessionExpired());
      },
      
      hasValidSession: () => {
        const state = get();
        return !!(state.sessionToken && !state.isSessionExpired());
      },
      
      getCompletionPercentage: () => {
        return get().progress.progress_percentage;
      },
      
      getResponseCount: () => {
        return get().responses.length;
      },
      
      // ========================================================================
      // STATE MANAGEMENT
      // ========================================================================
      
      reset: () => {
        set(initialState);
      },
      
      setLoading: (loading: boolean) => {
        set({ isLoading: loading });
      },
      
      setError: (error: string | null) => {
        set({ error });
      },
    }),
    {
      name: 'freemium-assessment-storage',
      partialize: (state) => ({
        leadId: state.leadId,
        email: state.email,
        leadScore: state.leadScore,
        leadStatus: state.leadStatus,
        sessionToken: state.sessionToken,
        sessionExpiry: state.sessionExpiry,
        hasMarketingConsent: state.hasMarketingConsent,
        hasNewsletterConsent: state.hasNewsletterConsent,
        consentDate: state.consentDate,
        isAssessmentComplete: state.isAssessmentComplete,
        hasViewedResults: state.hasViewedResults,
        responses: state.responses,
        results: state.results,
      }),
    }
  )
);

// ============================================================================
// SELECTOR HOOKS
// ============================================================================

export const useFreemiumSession = () => {
  const store = useFreemiumStore();
  return {
    hasSession: store.hasValidSession(),
    isInProgress: store.isAssessmentStarted && !store.isAssessmentComplete,
    canViewResults: store.isAssessmentComplete && store.hasValidSession(),
    sessionData: {
      leadId: store.leadId,
      email: store.email,
      sessionToken: store.sessionToken,
      expires: store.sessionExpiry,
    },
  };
};

export const useFreemiumProgress = () => {
  const store = useFreemiumStore();
  return {
    progress: store.progress.progress_percentage,
    currentQuestion: store.progress.current_question,
    totalQuestions: store.progress.total_questions_estimate,
    questionsAnswered: store.progress.questions_answered,
    isComplete: store.isAssessmentComplete,
    completionPercentage: store.getCompletionPercentage(),
    responseCount: store.getResponseCount(),
  };
};

export const useFreemiumConversion = () => {
  const store = useFreemiumStore();
  return {
    events: store.analyticsEvents,
    hasViewedResults: store.hasViewedResults,
    canStartAssessment: store.canStartAssessment(),
    trackEvent: store.trackEvent,
    markResultsViewed: store.markResultsViewed,
  };
};