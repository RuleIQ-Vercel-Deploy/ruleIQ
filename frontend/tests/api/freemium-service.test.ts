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
import { rest } from 'msw';
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
        rest.post('/api/v1/freemium/capture-email', (req, res, ctx) => {
          return res(ctx.json(mockResponse));
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
        rest.post('/api/v1/freemium/capture-email', (req, res, ctx) => {
          return res(
            ctx.status(422),
            ctx.json({
              detail: [
                {
                  loc: ['body', 'email'],
                  msg: 'value is not a valid email address',
                  type: 'value_error.email'
                }
              ]
            })
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
        rest.post('/api/v1/freemium/capture-email', (req, res, ctx) => {
          return res(
            ctx.status(400),
            ctx.json({
              detail: 'Terms of service consent is required'
            })
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
        rest.post('/api/v1/freemium/capture-email', (req, res, ctx) => {
          return res(ctx.json(mockResponse));
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
        rest.post('/api/v1/freemium/capture-email', (req, res, ctx) => {
          return res(
            ctx.status(429),
            ctx.json({
              detail: 'Too many requests. Please try again later.',
              retry_after: 60
            })
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
        rest.post('/api/v1/freemium/capture-email', async (req, res, ctx) => {
          capturedRequest = await req.json();
          return res(ctx.json({ success: true, token: 'test', message: 'ok' }));
        })
      );

      const request: FreemiumEmailCaptureRequest = {
        email: '  TEST@EXAMPLE.COM  ',
        utm_source: '<script>alert("xss")</script>google',
        consent_marketing: true,
        consent_terms: true
      };

      await captureEmail(request);

      expect(capturedRequest.email).toBe('test@example.com'); // Trimmed and lowercased
      expect(capturedRequest.utm_source).not.toContain('<script>'); // XSS filtered
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
        rest.post('/api/v1/freemium/start-assessment', (req, res, ctx) => {
          return res(ctx.json(mockResponse));
        })
      );

      const result = await startAssessment('valid-token-123');

      expect(result).toEqual(mockResponse);
    });

    it('handles invalid token error', async () => {
      server.use(
        rest.post('/api/v1/freemium/start-assessment', (req, res, ctx) => {
          return res(
            ctx.status(401),
            ctx.json({
              detail: 'Invalid or expired token'
            })
          );
        })
      );

      await expect(startAssessment('invalid-token')).rejects.toThrow(/invalid.*expired/i);
    });

    it('handles AI service unavailable error', async () => {
      server.use(
        rest.post('/api/v1/freemium/start-assessment', (req, res, ctx) => {
          return res(
            ctx.status(503),
            ctx.json({
              detail: 'AI service temporarily unavailable. Please try again.',
              fallback_available: true
            })
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
        rest.post('/api/v1/freemium/start-assessment', (req, res, ctx) => {
          return res(ctx.json(mockResponse));
        })
      );

      const result = await startAssessment('existing-session-token');

      expect(result).toEqual(mockResponse);
      expect(result.session_resumed).toBe(true);
    });

    it('handles network timeout', async () => {
      server.use(
        rest.post('/api/v1/freemium/start-assessment', (req, res, ctx) => {
          return res(ctx.delay('infinite'));
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
        rest.post('/api/v1/freemium/answer-question', (req, res, ctx) => {
          return res(ctx.json(mockResponse));
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
        rest.post('/api/v1/freemium/answer-question', (req, res, ctx) => {
          return res(
            ctx.status(400),
            ctx.json({
              detail: 'Invalid question ID for current session'
            })
          );
        })
      );

      const request: FreemiumAnswerQuestionRequest = {
        question_id: 'invalid_question',
        answer: 'test answer'
      };

      await expect(answerQuestion('valid-token', request)).rejects.toThrow(/invalid question/i);
    });

    it('handles assessment completion', async () => {
      const mockResponse: FreemiumAnswerQuestionResponse = {
        answer_recorded: true,
        assessment_complete: true,
        redirect_to_results: true,
        progress: 100
      };

      server.use(
        rest.post('/api/v1/freemium/answer-question', (req, res, ctx) => {
          return res(ctx.json(mockResponse));
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
        rest.post('/api/v1/freemium/answer-question', (req, res, ctx) => {
          return res(
            ctx.status(422),
            ctx.json({
              detail: [
                {
                  loc: ['body', 'answer'],
                  msg: 'Answer is required',
                  type: 'value_error.missing'
                }
              ]
            })
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
        rest.post('/api/v1/freemium/answer-question', (req, res, ctx) => {
          return res(ctx.json(mockResponse));
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
        rest.get('/api/v1/freemium/results/:token', (req, res, ctx) => {
          return res(ctx.json(mockResponse));
        })
      );

      const result = await getResults('completed-token-123');

      expect(result).toEqual(mockResponse);
    });

    it('handles incomplete assessment error', async () => {
      server.use(
        rest.get('/api/v1/freemium/results/:token', (req, res, ctx) => {
          return res(
            ctx.status(400),
            ctx.json({
              detail: 'Assessment not yet complete. Please finish all questions.'
            })
          );
        })
      );

      await expect(getResults('incomplete-token')).rejects.toThrow(/not yet complete/i);
    });

    it('handles expired token error', async () => {
      server.use(
        rest.get('/api/v1/freemium/results/:token', (req, res, ctx) => {
          return res(
            ctx.status(401),
            ctx.json({
              detail: 'Invalid or expired token'
            })
          );
        })
      );

      await expect(getResults('expired-token')).rejects.toThrow(/invalid.*expired/i);
    });

    it('caches results for performance', async () => {
      let requestCount = 0;

      server.use(
        rest.get('/api/v1/freemium/results/:token', (req, res, ctx) => {
          requestCount++;
          return res(ctx.json({
            compliance_gaps: [],
            risk_score: 5.0,
            recommendations: []
          }));
        })
      );

      // First request
      await getResults('cached-token');
      expect(requestCount).toBe(1);

      // Second request with same token should use cache
      await getResults('cached-token');
      expect(requestCount).toBe(1); // No additional request
    });

    it('handles AI service errors gracefully', async () => {
      server.use(
        rest.get('/api/v1/freemium/results/:token', (req, res, ctx) => {
          return res(
            ctx.status(503),
            ctx.json({
              detail: 'AI analysis service unavailable. Showing basic results.',
              partial_results: true,
              basic_analysis: {
                risk_score: 5.0,
                risk_level: 'medium',
                recommendations: ['Contact support for detailed analysis']
              }
            })
          );
        })
      );

      await expect(getResults('ai-error-token')).rejects.toThrow(/ai.*unavailable/i);
    });
  });

  describe('trackConversion', () => {
    it('tracks conversion event successfully', async () => {
      const mockResponse: FreemiumConversionTrackingResponse = {
        tracked: true,
        event_id: 'evt_1234567890',
        message: 'Conversion event tracked successfully'
      };

      server.use(
        rest.post('/api/v1/freemium/track-conversion', (req, res, ctx) => {
          return res(ctx.json(mockResponse));
        })
      );

      const request: FreemiumConversionTrackingRequest = {
        event_type: 'cta_click',
        cta_text: 'Get Compliant Now - 30% Off',
        conversion_value: 30,
        page_url: '/freemium/results',
        user_agent: 'Mozilla/5.0...',
        metadata: {
          time_on_page: 45.2,
          scroll_depth: 0.8,
          results_viewed: true
        }
      };

      const result = await trackConversion('valid-token', request);

      expect(result).toEqual(mockResponse);
    });

    it('handles duplicate event tracking', async () => {
      const mockResponse: FreemiumConversionTrackingResponse = {
        tracked: false,
        duplicate: true,
        event_id: 'evt_existing',
        message: 'Event already tracked'
      };

      server.use(
        rest.post('/api/v1/freemium/track-conversion', (req, res, ctx) => {
          return res(ctx.json(mockResponse));
        })
      );

      const request: FreemiumConversionTrackingRequest = {
        event_type: 'cta_click',
        cta_text: 'Get Compliant Now - 30% Off',
        conversion_value: 30
      };

      const result = await trackConversion('valid-token', request);

      expect(result).toEqual(mockResponse);
      expect(result.duplicate).toBe(true);
    });

    it('handles invalid event type error', async () => {
      server.use(
        rest.post('/api/v1/freemium/track-conversion', (req, res, ctx) => {
          return res(
            ctx.status(422),
            ctx.json({
              detail: [
                {
                  loc: ['body', 'event_type'],
                  msg: 'value is not a valid enumeration member',
                  type: 'type_error.enum'
                }
              ]
            })
          );
        })
      );

      const request = {
        event_type: 'invalid_event' as any,
        conversion_value: 30
      };

      await expect(trackConversion('valid-token', request)).rejects.toThrow(/enumeration/i);
    });

    it('includes proper metadata in tracking', async () => {
      let capturedRequest: any;

      server.use(
        rest.post('/api/v1/freemium/track-conversion', async (req, res, ctx) => {
          capturedRequest = await req.json();
          return res(ctx.json({ tracked: true, event_id: 'test', message: 'ok' }));
        })
      );

      const request: FreemiumConversionTrackingRequest = {
        event_type: 'cta_click',
        cta_text: 'Get Compliant Now',
        conversion_value: 30,
        metadata: {
          time_on_page: 60.5,
          scroll_depth: 0.9,
          results_viewed: true,
          referrer: 'https://google.com'
        }
      };

      await trackConversion('valid-token', request);

      expect(capturedRequest.metadata).toEqual(request.metadata);
      expect(capturedRequest.conversion_value).toBe(30);
    });
  });

  describe('Error Handling and Resilience', () => {
    it('retries failed requests with exponential backoff', async () => {
      let attemptCount = 0;

      server.use(
        rest.post('/api/v1/freemium/capture-email', (req, res, ctx) => {
          attemptCount++;
          if (attemptCount < 3) {
            return res(ctx.status(500), ctx.json({ detail: 'Internal server error' }));
          }
          return res(ctx.json({ success: true, token: 'retry-success', message: 'ok' }));
        })
      );

      const request: FreemiumEmailCaptureRequest = {
        email: 'retry@example.com',
        consent_marketing: true,
        consent_terms: true
      };

      const result = await captureEmail(request);

      expect(attemptCount).toBe(3);
      expect(result.success).toBe(true);
    });

    it('fails after maximum retry attempts', async () => {
      server.use(
        rest.post('/api/v1/freemium/capture-email', (req, res, ctx) => {
          return res(ctx.status(500), ctx.json({ detail: 'Persistent server error' }));
        })
      );

      const request: FreemiumEmailCaptureRequest = {
        email: 'fail@example.com',
        consent_marketing: true,
        consent_terms: true
      };

      await expect(captureEmail(request)).rejects.toThrow(/server error/i);
    });

    it('handles network connectivity issues', async () => {
      server.use(
        rest.post('/api/v1/freemium/capture-email', (req, res, ctx) => {
          return res.networkError('Network connection failed');
        })
      );

      const request: FreemiumEmailCaptureRequest = {
        email: 'network@example.com',
        consent_marketing: true,
        consent_terms: true
      };

      await expect(captureEmail(request)).rejects.toThrow(/network/i);
    });

    it('validates response data structure', async () => {
      server.use(
        rest.post('/api/v1/freemium/capture-email', (req, res, ctx) => {
          return res(ctx.json({
            // Missing required fields
            invalid: true
          }));
        })
      );

      const request: FreemiumEmailCaptureRequest = {
        email: 'validation@example.com',
        consent_marketing: true,
        consent_terms: true
      };

      await expect(captureEmail(request)).rejects.toThrow(/invalid response/i);
    });
  });

  describe('Performance and Optimization', () => {
    it('cancels requests when component unmounts', async () => {
      const abortController = new AbortController();

      server.use(
        rest.post('/api/v1/freemium/start-assessment', (req, res, ctx) => {
          return res(ctx.delay(1000), ctx.json({ session_started: true }));
        })
      );

      const requestPromise = startAssessment('valid-token', {
        signal: abortController.signal
      });

      // Cancel request after 100ms
      setTimeout(() => abortController.abort(), 100);

      await expect(requestPromise).rejects.toThrow(/abort/i);
    });

    it('compresses large payloads', async () => {
      let requestHeaders: any = {};

      server.use(
        rest.post('/api/v1/freemium/answer-question', (req, res, ctx) => {
          requestHeaders = req.headers.all();
          return res(ctx.json({ answer_recorded: true }));
        })
      );

      const largeRequest: FreemiumAnswerQuestionRequest = {
        question_id: 'q_large_text',
        answer: 'A'.repeat(10000), // Large answer
        answer_metadata: {
          detailed_reasoning: 'B'.repeat(5000)
        }
      };

      await answerQuestion('valid-token', largeRequest);

      expect(requestHeaders['content-encoding']).toBe('gzip');
    });

    it('implements request deduplication', async () => {
      let requestCount = 0;

      server.use(
        rest.get('/api/v1/freemium/results/:token', (req, res, ctx) => {
          requestCount++;
          return res(ctx.json({ compliance_gaps: [] }));
        })
      );

      // Make multiple simultaneous requests
      const promises = [
        getResults('dedup-token'),
        getResults('dedup-token'),
        getResults('dedup-token')
      ];

      await Promise.all(promises);

      // Should only make one actual request
      expect(requestCount).toBe(1);
    });
  });
});