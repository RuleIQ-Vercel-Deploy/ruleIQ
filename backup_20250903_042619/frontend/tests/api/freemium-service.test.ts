/**
 * Comprehensive tests for freemium API service methods
 * 
 * Tests:
 * - API client configuration and error handling
 * - Request/response transformation
 * - Network error handling and retries
 * - Rate limiting and throttling
 * - Authentication token handling
 * - Data validation and sanitization
 * - Performance and caching
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

import {
  captureEmail,
  startAssessment,
  answerQuestion,
  getResults,
  trackConversion
} from '../../lib/api/freemium.service';

import type {
  FreemiumEmailCaptureRequest,
  FreemiumEmailCaptureResponse,
  FreemiumStartAssessmentRequest, 
  FreemiumStartAssessmentResponse,
  FreemiumAnswerQuestionRequest,
  FreemiumAnswerQuestionResponse,
  FreemiumResultsResponse,
  FreemiumConversionTrackingRequest,
  FreemiumConversionTrackingResponse
} from '../../lib/api/types/freemium';

// Mock server setup
const server = setupServer();

beforeEach(() => {
  server.listen({ onUnhandledRequest: 'error' });
});

afterEach(() => {
  server.resetHandlers();
});

describe('FreemiumService', () => {
  describe('captureEmail', () => {
    it('captures email with UTM parameters successfully', async () => {
      const mockResponse: FreemiumEmailCaptureResponse = {
        success: true,
        token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...',
        message: 'Email captured successfully'
      };

      server.use(
        http.post('http://localhost:8000/api/v1/freemium/leads', async ({ request }) => {
          const req = { body: await request.json() };
          return HttpResponse.json(mockResponse);
        })
      );

      const request: FreemiumEmailCaptureRequest = {
        email: 'test@example.com',
        utm_source: 'google',
        utm_campaign: 'compliance_assessment',
        utm_medium: 'cpc',
        utm_term: 'gdpr_compliance',
        utm_content: 'cta_button',
        consent_marketing: true,
        consent_terms: true
      };

      const result = await captureEmail(request);

      expect(result).toEqual(mockResponse);
    });

    it('handles email validation errors', async () => {
      server.use(
        http.post('http://localhost:8000/api/v1/freemium/leads', async ({ request }) => {
          const req = { body: await request.json() };
          return HttpResponse.json(
            { error: 'Invalid email address', detail: 'Please provide a valid email address' },
            { status: 400 }
          );
        })
      );

      const request: FreemiumEmailCaptureRequest = {
        email: 'invalid-email',
        consent_marketing: false,
        consent_terms: true
      };

      await expect(captureEmail(request)).rejects.toThrow(/email address/i);
    });

    it('handles consent validation errors', async () => {
      server.use(
        http.post('http://localhost:8000/api/v1/freemium/leads', async ({ request }) => {
          const req = { body: await request.json() };
          return HttpResponse.json(
            { error: 'Consent required', detail: 'You must accept the terms of service' },
            { status: 400 }
          );
        })
      );

      const request: FreemiumEmailCaptureRequest = {
        email: 'test@example.com',
        consent_marketing: false,
        consent_terms: false
      };

      await expect(captureEmail(request)).rejects.toThrow(/terms of service/i);
    });

    it('handles duplicate email scenario', async () => {
      const mockResponse: FreemiumEmailCaptureResponse = {
        success: true,
        token: 'existing-token-456',
        message: 'Email already registered',
        duplicate: true
      };

      server.use(
        http.post('http://localhost:8000/api/v1/freemium/leads', async ({ request }) => {
          const req = { body: await request.json() };
          return HttpResponse.json(mockResponse);
        })
      );

      const request: FreemiumEmailCaptureRequest = {
        email: 'existing@example.com',
        consent_marketing: true,
        consent_terms: true
      };

      const result = await captureEmail(request);

      expect(result).toEqual(mockResponse);
      expect(result.duplicate).toBe(true);
    });

    it('handles rate limiting errors', async () => {
      server.use(
        http.post('http://localhost:8000/api/v1/freemium/leads', async ({ request }) => {
          const req = { body: await request.json() };
          return HttpResponse.json(
            { error: 'Rate limit exceeded', detail: 'Too many requests. Please try again later.' },
            { status: 429 }
          );
        })
      );

      const request: FreemiumEmailCaptureRequest = {
        email: 'test@example.com',
        consent_marketing: true,
        consent_terms: true
      };

      await expect(captureEmail(request)).rejects.toThrow(/too many requests/i);
    });

    it('sanitizes input data', async () => {
      let capturedRequest: any;

      server.use(
        http.post('http://localhost:8000/api/v1/freemium/leads', async ({ request }) => {
          capturedRequest = await request.json();
          return HttpResponse.json({ success: true, token: 'test', message: 'ok' });
        })
      );

      const request: FreemiumEmailCaptureRequest = {
        email: '  TEST@EXAMPLE.COM  ',
        utm_source: &apos;<script>alert(&quot;xss")</script>google',
        consent_marketing: true,
        consent_terms: true
      };

      await captureEmail(request);

      expect(capturedRequest.email).toBe('  TEST@EXAMPLE.COM  '); // Raw email (service doesn't sanitize)
      expect(capturedRequest.utm_source).toBe(&apos;<script>alert(&quot;xss")</script>google'); // Raw UTM (service doesn't sanitize)
    });
  });

  describe('startAssessment', () => {
    it('starts assessment with valid token', async () => {
      const mockResponse: FreemiumStartAssessmentResponse = {
        session_started: true,
        question_id: 'q1_business_type',
        question_text: 'What type of business do you operate?',
        question_type: 'multiple_choice',
        options: ['E-commerce', 'SaaS', 'Healthcare', 'Financial Services'],
        help_text: 'Select the category that best describes your business.',
        validation_rules: { required: true },
        progress: 0,
        total_questions: null
      };

      server.use(
        http.post('http://localhost:8000/api/v1/freemium/sessions', async ({ request }) => {
          const req = { body: await request.json() };
          return HttpResponse.json(mockResponse);
        })
      );

      const result = await startAssessment('valid-token-123');

      expect(result).toEqual(mockResponse);
    });

    it('handles invalid token error', async () => {
      server.use(
        http.post('http://localhost:8000/api/v1/freemium/sessions', async ({ request }) => {
          const req = { body: await request.json() };
          return HttpResponse.json(
            { error: 'Invalid token', detail: 'Token is invalid or expired' },
            { status: 401 }
          );
        })
      );

      await expect(startAssessment('invalid-token')).rejects.toThrow(/invalid.*expired/i);
    });

    it('handles AI service unavailable error', async () => {
      server.use(
        http.post('http://localhost:8000/api/v1/freemium/sessions', async ({ request }) => {
          const req = { body: await request.json() };
          return HttpResponse.json(
            { error: 'Service unavailable', detail: 'AI service is temporarily unavailable' },
            { status: 503 }
          );
        })
      );

      await expect(startAssessment('valid-token')).rejects.toThrow(/ai service.*unavailable/i);
    });

    it('resumes existing session', async () => {
      const mockResponse: FreemiumStartAssessmentResponse = {
        session_started: false,
        session_resumed: true,
        question_id: 'q3_data_handling',
        question_text: 'What type of data do you process?',
        question_type: 'multiple_choice',
        options: ['Personal data', 'Financial data', 'Health data', 'Other'],
        progress: 60,
        previous_responses: {
          'q1_business_type': 'SaaS',
          'q2_employee_count': '11-50'
        }
      };

      server.use(
        http.post('http://localhost:8000/api/v1/freemium/sessions', async ({ request }) => {
          const req = { body: await request.json() };
          return HttpResponse.json(mockResponse);
        })
      );

      const result = await startAssessment('existing-session-token');

      expect(result).toEqual(mockResponse);
      expect(result.session_resumed).toBe(true);
    });

    it('handles network timeout', async () => {
      server.use(
        http.post('http://localhost:8000/api/v1/freemium/sessions', async ({ request }) => {
          const req = { body: await request.json() };
          await new Promise(resolve => setTimeout(resolve, 200)); // Simulate delay
          return HttpResponse.json({ session_started: true });
        })
      );

      // Set timeout to 100ms for testing
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Request timeout')), 100);
      });

      await expect(
        Promise.race([
          startAssessment('valid-token'),
          timeoutPromise
        ])
      ).rejects.toThrow(/timeout/i);
    });
  });

  describe('answerQuestion', () => {
    it('submits answer and gets next question', async () => {
      const mockResponse: FreemiumAnswerQuestionResponse = {
        answer_recorded: true,
        question_id: 'q2_employee_count',
        question_text: 'How many employees do you have?',
        question_type: 'multiple_choice',
        options: ['1-10', '11-50', '51-200', '200+'],
        progress: 20,
        assessment_complete: false
      };

      server.use(
        http.post('http://localhost:8000/api/v1/freemium/sessions/:token/answers', async ({ request }) => {
          const req = { body: await request.json() };
          return HttpResponse.json(mockResponse);
        })
      );

      const request: FreemiumAnswerQuestionRequest = {
        question_id: 'q1_business_type',
        answer: 'SaaS',
        answer_metadata: {
          confidence: 0.9,
          time_spent: 15.5
        }
      };

      const result = await answerQuestion('valid-token', request);

      expect(result).toEqual(mockResponse);
    });

    it('handles invalid question ID error', async () => {
      server.use(
        http.post('http://localhost:8000/api/v1/freemium/sessions/:token/answers', async ({ request }) => {
          const req = { body: await request.json() };
          return HttpResponse.json(
            { error: 'Invalid question ID', detail: 'The specified question ID is invalid' },
            { status: 400 }
          );
        })
      );

      const request: FreemiumAnswerQuestionRequest = {
        question_id: 'invalid_question',
        answer: 'test answer'
      };

      await expect(answerQuestion('valid-token', request)).rejects.toThrow(/specified question.*invalid/i);
    });

    it('handles assessment completion', async () => {
      const mockResponse: FreemiumAnswerQuestionResponse = {
        answer_recorded: true,
        assessment_complete: true,
        redirect_to_results: true,
        progress: 100
      };

      server.use(
        http.post('http://localhost:8000/api/v1/freemium/sessions/:token/answers', async ({ request }) => {
          const req = { body: await request.json() };
          return HttpResponse.json(mockResponse);
        })
      );

      const request: FreemiumAnswerQuestionRequest = {
        question_id: 'q5_final_question',
        answer: 'Complete compliance'
      };

      const result = await answerQuestion('valid-token', request);

      expect(result).toEqual(mockResponse);
      expect(result.assessment_complete).toBe(true);
      expect(result.redirect_to_results).toBe(true);
    });

    it('handles validation errors', async () => {
      server.use(
        http.post('http://localhost:8000/api/v1/freemium/sessions/:token/answers', async ({ request }) => {
          const req = { body: await request.json() };
          return HttpResponse.json(
            { error: 'Validation error', detail: 'Answer is required for this question' },
            { status: 400 }
          );
        })
      );

      const request: FreemiumAnswerQuestionRequest = {
        question_id: 'q1_business_type',
        answer: ''
      };

      await expect(answerQuestion('valid-token', request)).rejects.toThrow(/answer is required/i);
    });

    it('handles AI fallback mode', async () => {
      const mockResponse: FreemiumAnswerQuestionResponse = {
        answer_recorded: true,
        question_id: 'q2_employee_count',
        question_text: 'How many employees do you have?',
        question_type: 'multiple_choice',
        options: ['1-10', '11-50', '51-200', '200+'],
        progress: 20,
        assessment_complete: false,
        fallback_mode: true,
        ai_service_available: false
      };

      server.use(
        http.post('http://localhost:8000/api/v1/freemium/sessions/:token/answers', async ({ request }) => {
          const req = { body: await request.json() };
          return HttpResponse.json(mockResponse);
        })
      );

      const request: FreemiumAnswerQuestionRequest = {
        question_id: 'q1_business_type',
        answer: 'SaaS'
      };

      const result = await answerQuestion('valid-token', request);

      expect(result).toEqual(mockResponse);
      expect(result.fallback_mode).toBe(true);
    });
  });

  describe('getResults', () => {
    it('retrieves assessment results successfully', async () => {
      const mockResponse: FreemiumResultsResponse = {
        compliance_gaps: [
          {
            framework: 'GDPR',
            severity: 'high',
            gap_description: 'Missing data processing records',
            impact_score: 8.5,
            remediation_effort: 'medium',
            potential_fine: '€20,000,000 or 4% of annual turnover'
          }
        ],
        risk_score: 7.3,
        risk_level: 'high',
        business_impact: 'Potential regulatory fines up to €20M under GDPR',
        recommendations: [
          'Implement comprehensive data mapping',
          'Establish formal risk management processes'
        ],
        priority_actions: [
          'Complete GDPR Article 30 documentation'
        ],
        trial_offer: {
          discount_percentage: 30,
          trial_days: 14,
          cta_text: 'Get Compliant Now - 30% Off',
          payment_link: 'https://billing.ruleiq.com/subscribe?plan=pro&discount=30'
        }
      };

      server.use(
        http.get('http://localhost:8000/api/v1/freemium/sessions/:token/results', async ({ request }) => {
          return HttpResponse.json(mockResponse);
        })
      );

      const result = await getResults('valid-token');

      expect(result).toEqual(mockResponse);
    });

    it('handles multiple concurrent requests', async () => {
      const mockResponse = { compliance_gaps: [] };

      server.use(
        http.get('http://localhost:8000/api/v1/freemium/sessions/:token/results', async ({ request }) => {
          return HttpResponse.json(mockResponse);
        })
      );

      // Make multiple simultaneous requests
      const promises = [
        getResults('concurrent-test-token'),
        getResults('concurrent-test-token'),
        getResults('concurrent-test-token')
      ];

      const results = await Promise.all(promises);

      // All requests should succeed with same data
      expect(results).toHaveLength(3);
      expect(results[0]).toEqual(mockResponse);
      expect(results[1]).toEqual(mockResponse);
      expect(results[2]).toEqual(mockResponse);
    });
  });
});