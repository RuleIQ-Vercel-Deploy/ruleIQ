/**
 * Comprehensive tests for FreemiumStore (Zustand)
 * 
 * Tests:
 * - State initialization and defaults
 * - Email and token management
 * - UTM parameter handling
 * - Response tracking and progress
 * - Consent state management
 * - State persistence and hydration
 * - Action creators and mutations
 * - State derivations and selectors
 * - Error handling and validation
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { act, renderHook } from '@testing-library/react';

import { useFreemiumStore, createFreemiumStore } from '../../lib/stores/freemium-store';
import type { FreemiumStoreState, FreemiumStoreActions } from '../../lib/stores/freemium-store';

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
vi.stubGlobal('localStorage', localStorageMock);

// Mock sessionStorage
const sessionStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
};
vi.stubGlobal('sessionStorage', sessionStorageMock);

describe('FreemiumStore', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset store state
    useFreemiumStore.setState({
      email: '',
      token: null,
      utmSource: null,
      utmCampaign: null,
      utmMedium: null,
      utmTerm: null,
      utmContent: null,
      consentMarketing: false,
      consentTerms: false,
      currentQuestionId: null,
      responses: {},
      progress: 0,
      assessmentStarted: false,
      assessmentCompleted: false,
      lastActivity: null,
      sessionExpiry: null
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('Initial State', () => {
    it('has correct default values', () => {
      const { result } = renderHook(() => useFreemiumStore());

      expect(result.current.email).toBe('');
      expect(result.current.token).toBeNull();
      expect(result.current.utmSource).toBeNull();
      expect(result.current.utmCampaign).toBeNull();
      expect(result.current.utmMedium).toBeNull();
      expect(result.current.utmTerm).toBeNull();
      expect(result.current.utmContent).toBeNull();
      expect(result.current.consentMarketing).toBe(false);
      expect(result.current.consentTerms).toBe(false);
      expect(result.current.currentQuestionId).toBeNull();
      expect(result.current.responses).toEqual({});
      expect(result.current.progress).toBe(0);
      expect(result.current.assessmentStarted).toBe(false);
      expect(result.current.assessmentCompleted).toBe(false);
      expect(result.current.lastActivity).toBeNull();
      expect(result.current.sessionExpiry).toBeNull();
    });

    it('provides all required action methods', () => {
      const { result } = renderHook(() => useFreemiumStore());

      expect(typeof result.current.setEmail).toBe('function');
      expect(typeof result.current.setToken).toBe('function');
      expect(typeof result.current.setUtmParams).toBe('function');
      expect(typeof result.current.setConsent).toBe('function');
      expect(typeof result.current.setCurrentQuestion).toBe('function');
      expect(typeof result.current.setProgress).toBe('function');
      expect(typeof result.current.addResponse).toBe('function');
      expect(typeof result.current.markAssessmentStarted).toBe('function');
      expect(typeof result.current.markAssessmentCompleted).toBe('function');
      expect(typeof result.current.updateLastActivity).toBe('function');
      expect(typeof result.current.reset).toBe('function');
    });
  });

  describe('Email Management', () => {
    it('sets email correctly', () => {
      const { result } = renderHook(() => useFreemiumStore());

      act(() => {
        result.current.setEmail('test@example.com');
      });

      expect(result.current.email).toBe('test@example.com');
    });

    it('trims and normalizes email', () => {
      const { result } = renderHook(() => useFreemiumStore());

      act(() => {
        result.current.setEmail('  TEST@EXAMPLE.COM  ');
      });

      expect(result.current.email).toBe('test@example.com');
    });

    it('validates email format', () => {
      const { result } = renderHook(() => useFreemiumStore());

      act(() => {
        result.current.setEmail('invalid-email');
      });

      // Should not set invalid email
      expect(result.current.email).toBe('');
    });

    it('persists email to localStorage', () => {
      const { result } = renderHook(() => useFreemiumStore());

      act(() => {
        result.current.setEmail('persistent@example.com');
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'freemium-email',
        'persistent@example.com'
      );
    });
  });

  describe('Token Management', () => {
    it('sets token correctly', () => {
      const { result } = renderHook(() => useFreemiumStore());
      const testToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';

      act(() => {
        result.current.setToken(testToken);
      });

      expect(result.current.token).toBe(testToken);
    });

    it('validates JWT token format', () => {
      const { result } = renderHook(() => useFreemiumStore());

      act(() => {
        result.current.setToken('invalid-token-format');
      });

      // Should not set invalid token
      expect(result.current.token).toBeNull();
    });

    it('extracts expiry from JWT token', () => {
      const { result } = renderHook(() => useFreemiumStore());
      
      // Mock JWT with expiry
      const mockJWT = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDk1NTc4MDB9.signature';

      act(() => {
        result.current.setToken(mockJWT);
      });

      expect(result.current.sessionExpiry).not.toBeNull();
    });

    it('persists token to sessionStorage', () => {
      const { result } = renderHook(() => useFreemiumStore());
      const testToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';

      act(() => {
        result.current.setToken(testToken);
      });

      expect(sessionStorageMock.setItem).toHaveBeenCalledWith(
        'freemium-token',
        testToken
      );
    });

    it('clears token when set to null', () => {
      const { result } = renderHook(() => useFreemiumStore());
      const testToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...';

      // Set token first
      act(() => {
        result.current.setToken(testToken);
      });

      // Clear token
      act(() => {
        result.current.setToken(null);
      });

      expect(result.current.token).toBeNull();
      expect(sessionStorageMock.removeItem).toHaveBeenCalledWith('freemium-token');
    });
  });

  describe('UTM Parameter Management', () => {
    it('sets all UTM parameters', () => {
      const { result } = renderHook(() => useFreemiumStore());
      const utmParams = {
        utm_source: 'google',
        utm_campaign: 'compliance_assessment',
        utm_medium: 'cpc',
        utm_term: 'gdpr_compliance',
        utm_content: 'cta_button'
      };

      act(() => {
        result.current.setUtmParams(utmParams);
      });

      expect(result.current.utmSource).toBe('google');
      expect(result.current.utmCampaign).toBe('compliance_assessment');
      expect(result.current.utmMedium).toBe('cpc');
      expect(result.current.utmTerm).toBe('gdpr_compliance');
      expect(result.current.utmContent).toBe('cta_button');
    });

    it('handles partial UTM parameters', () => {
      const { result } = renderHook(() => useFreemiumStore());
      const partialUtmParams = {
        utm_source: 'facebook',
        utm_campaign: 'social_campaign'
      };

      act(() => {
        result.current.setUtmParams(partialUtmParams);
      });

      expect(result.current.utmSource).toBe('facebook');
      expect(result.current.utmCampaign).toBe('social_campaign');
      expect(result.current.utmMedium).toBeNull();
      expect(result.current.utmTerm).toBeNull();
      expect(result.current.utmContent).toBeNull();
    });

    it('sanitizes UTM parameters', () => {
      const { result } = renderHook(() => useFreemiumStore());
      const maliciousUtmParams = {
        utm_source: &apos;<script>alert(&quot;xss")</script>google',
        utm_campaign: 'javascript:void(0)',
        utm_medium: &apos;data:text/html,<script>alert(1)</script>'
      };

      act(() => {
        result.current.setUtmParams(maliciousUtmParams);
      });

      expect(result.current.utmSource).not.toContain(&apos;<script>');
      expect(result.current.utmCampaign).not.toContain('javascript:');
      expect(result.current.utmMedium).not.toContain('data:');
    });

    it('persists UTM parameters to localStorage', () => {
      const { result } = renderHook(() => useFreemiumStore());
      const utmParams = {
        utm_source: 'twitter',
        utm_campaign: 'awareness'
      };

      act(() => {
        result.current.setUtmParams(utmParams);
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'freemium-utm',
        JSON.stringify(utmParams)
      );
    });
  });

  describe('Consent Management', () => {
    it('sets marketing consent', () => {
      const { result } = renderHook(() => useFreemiumStore());

      act(() => {
        result.current.setConsent('marketing', true);
      });

      expect(result.current.consentMarketing).toBe(true);
    });

    it('sets terms consent', () => {
      const { result } = renderHook(() => useFreemiumStore());

      act(() => {
        result.current.setConsent('terms', true);
      });

      expect(result.current.consentTerms).toBe(true);
    });

    it('can revoke consent', () => {
      const { result } = renderHook(() => useFreemiumStore());

      // Grant consent first
      act(() => {
        result.current.setConsent('marketing', true);
        result.current.setConsent('terms', true);
      });

      // Revoke consent
      act(() => {
        result.current.setConsent('marketing', false);
        result.current.setConsent('terms', false);
      });

      expect(result.current.consentMarketing).toBe(false);
      expect(result.current.consentTerms).toBe(false);
    });

    it('persists consent to localStorage', () => {
      const { result } = renderHook(() => useFreemiumStore());

      act(() => {
        result.current.setConsent('marketing', true);
      });

      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'freemium-consent',
        JSON.stringify({
          marketing: true,
          terms: false
        })
      );
    });
  });

  describe('Assessment Progress Management', () => {
    it('sets current question ID', () => {
      const { result } = renderHook(() => useFreemiumStore());

      act(() => {
        result.current.setCurrentQuestion('q1_business_type');
      });

      expect(result.current.currentQuestionId).toBe('q1_business_type');
    });

    it('sets progress percentage', () => {
      const { result } = renderHook(() => useFreemiumStore());

      act(() => {
        result.current.setProgress(45);
      });

      expect(result.current.progress).toBe(45);
    });

    it('validates progress range', () => {
      const { result } = renderHook(() => useFreemiumStore());

      // Test negative progress
      act(() => {
        result.current.setProgress(-10);
      });
      expect(result.current.progress).toBe(0);

      // Test progress over 100
      act(() => {
        result.current.setProgress(150);
      });
      expect(result.current.progress).toBe(100);
    });

    it('adds assessment responses', () => {
      const { result } = renderHook(() => useFreemiumStore());

      act(() => {
        result.current.addResponse('q1_business_type', 'SaaS');
        result.current.addResponse('q2_employee_count', '11-50');
      });

      expect(result.current.responses).toEqual({
        'q1_business_type': 'SaaS',
        'q2_employee_count': '11-50'
      });
    });

    it('overwrites existing responses', () => {
      const { result } = renderHook(() => useFreemiumStore());

      // Add initial response
      act(() => {
        result.current.addResponse('q1_business_type', 'E-commerce');
      });

      // Update response
      act(() => {
        result.current.addResponse('q1_business_type', 'SaaS');
      });

      expect(result.current.responses['q1_business_type']).toBe('SaaS');
    });

    it('marks assessment as started', () => {
      const { result } = renderHook(() => useFreemiumStore());

      act(() => {
        result.current.markAssessmentStarted();
      });

      expect(result.current.assessmentStarted).toBe(true);
    });

    it('marks assessment as completed', () => {
      const { result } = renderHook(() => useFreemiumStore());

      act(() => {
        result.current.markAssessmentCompleted();
      });

      expect(result.current.assessmentCompleted).toBe(true);
      expect(result.current.progress).toBe(100);
    });
  });

  describe('Activity Tracking', () => {
    it('updates last activity timestamp', () => {
      const { result } = renderHook(() => useFreemiumStore());

      act(() => {
        result.current.updateLastActivity();
      });

      expect(result.current.lastActivity).not.toBeNull();
      expect(typeof result.current.lastActivity).toBe('number');
    });

    it('tracks activity automatically on state changes', () => {
      const { result } = renderHook(() => useFreemiumStore());

      act(() => {
        result.current.setEmail('activity@example.com');
      });

      expect(result.current.lastActivity).not.toBeNull();
    });
  });

  describe('State Persistence and Hydration', () => {
    it('loads state from localStorage on initialization', () => {
      localStorageMock.getItem.mockImplementation((key) => {
        const data = {
          'freemium-email': 'saved@example.com',
          'freemium-utm': JSON.stringify({
            utm_source: 'saved_source',
            utm_campaign: 'saved_campaign'
          }),
          'freemium-consent': JSON.stringify({
            marketing: true,
            terms: true
          })
        };
        return data[key] || null;
      });

      sessionStorageMock.getItem.mockImplementation((key) => {
        const data = {
          'freemium-token': 'saved-token-123'
        };
        return data[key] || null;
      });

      // Create new store instance to trigger hydration
      const newStore = createFreemiumStore();
      const { result } = renderHook(() => newStore());

      expect(result.current.email).toBe('saved@example.com');
      expect(result.current.token).toBe('saved-token-123');
      expect(result.current.utmSource).toBe('saved_source');
      expect(result.current.consentMarketing).toBe(true);
    });

    it('handles corrupt localStorage data gracefully', () => {
      localStorageMock.getItem.mockImplementation((key) => {
        if (key === 'freemium-utm') {
          return 'invalid-json{';
        }
        return null;
      });

      // Should not throw error
      expect(() => {
        const newStore = createFreemiumStore();
        renderHook(() => newStore());
      }).not.toThrow();
    });

    it('persists responses to sessionStorage', () => {
      const { result } = renderHook(() => useFreemiumStore());

      act(() => {
        result.current.addResponse('q1', 'answer1');
        result.current.addResponse('q2', 'answer2');
      });

      expect(sessionStorageMock.setItem).toHaveBeenCalledWith(
        'freemium-responses',
        JSON.stringify({
          q1: 'answer1',
          q2: 'answer2'
        })
      );
    });
  });

  describe('State Reset', () => {
    it('resets all state to initial values', () => {
      const { result } = renderHook(() => useFreemiumStore());

      // Set some state
      act(() => {
        result.current.setEmail('test@example.com');
        result.current.setToken('test-token');
        result.current.setProgress(50);
        result.current.addResponse('q1', 'answer');
        result.current.markAssessmentStarted();
      });

      // Reset state
      act(() => {
        result.current.reset();
      });

      expect(result.current.email).toBe('');
      expect(result.current.token).toBeNull();
      expect(result.current.progress).toBe(0);
      expect(result.current.responses).toEqual({});
      expect(result.current.assessmentStarted).toBe(false);
    });

    it('clears persisted data on reset', () => {
      const { result } = renderHook(() => useFreemiumStore());

      act(() => {
        result.current.reset();
      });

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('freemium-email');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('freemium-utm');
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('freemium-consent');
      expect(sessionStorageMock.removeItem).toHaveBeenCalledWith('freemium-token');
      expect(sessionStorageMock.removeItem).toHaveBeenCalledWith('freemium-responses');
    });

    it('provides selective reset options', () => {
      const { result } = renderHook(() => useFreemiumStore());

      // Set some state
      act(() => {
        result.current.setEmail('keep@example.com');
        result.current.setToken('remove-token');
        result.current.addResponse('q1', 'remove-answer');
      });

      // Reset only assessment data
      act(() => {
        result.current.reset({ keepEmail: true, keepUtm: true });
      });

      expect(result.current.email).toBe('keep@example.com');
      expect(result.current.token).toBeNull();
      expect(result.current.responses).toEqual({});
    });
  });

  describe('Derived State and Selectors', () => {
    it('computes isSessionExpired correctly', () => {
      const { result } = renderHook(() => useFreemiumStore());

      // Mock expired session
      act(() => {
        result.current.setToken('expired-token');
        useFreemiumStore.setState({
          sessionExpiry: Date.now() - 1000 // Expired 1 second ago
        });
      });

      expect(result.current.isSessionExpired).toBe(true);
    });

    it('computes canStartAssessment correctly', () => {
      const { result } = renderHook(() => useFreemiumStore());

      // Initially can't start
      expect(result.current.canStartAssessment).toBe(false);

      // After email and consent
      act(() => {
        result.current.setEmail('ready@example.com');
        result.current.setConsent('terms', true);
        result.current.setToken('valid-token');
      });

      expect(result.current.canStartAssessment).toBe(true);
    });

    it('computes hasValidSession correctly', () => {
      const { result } = renderHook(() => useFreemiumStore());

      // Initially no valid session
      expect(result.current.hasValidSession).toBe(false);

      // After setting valid token
      act(() => {  
        result.current.setToken('valid-token');
        useFreemiumStore.setState({
          sessionExpiry: Date.now() + 3600000 // Expires in 1 hour
        });
      });

      expect(result.current.hasValidSession).toBe(true);
    });

    it('computes responseCount correctly', () => {
      const { result } = renderHook(() => useFreemiumStore());

      expect(result.current.responseCount).toBe(0);

      act(() => {
        result.current.addResponse('q1', 'answer1');
        result.current.addResponse('q2', 'answer2');
        result.current.addResponse('q3', 'answer3');
      });

      expect(result.current.responseCount).toBe(3);
    });
  });

  describe('Error Handling and Edge Cases', () => {
    it('handles localStorage quota errors', () => {
      localStorageMock.setItem.mockImplementation(() => {
        throw new DOMException('QuotaExceededError', 'QUOTA_EXCEEDED_ERR');
      });

      const { result } = renderHook(() => useFreemiumStore());

      // Should not throw error
      expect(() => {
        act(() => {
          result.current.setEmail('quota@example.com');
        });
      }).not.toThrow();
    });

    it('handles disabled localStorage gracefully', () => {
      // Mock disabled localStorage
      vi.stubGlobal('localStorage', undefined);

      const { result } = renderHook(() => useFreemiumStore());

      // Should still work without persistence
      expect(() => {
        act(() => {
          result.current.setEmail('no-storage@example.com');
        });
      }).not.toThrow();

      expect(result.current.email).toBe('no-storage@example.com');
    });

    it('validates state transitions', () => {
      const { result } = renderHook(() => useFreemiumStore());

      // Can't mark completed without starting
      act(() => {
        result.current.markAssessmentCompleted();
      });

      expect(result.current.assessmentCompleted).toBe(false);

      // Must start first
      act(() => {
        result.current.markAssessmentStarted();
        result.current.markAssessmentCompleted();
      });

      expect(result.current.assessmentCompleted).toBe(true);
    });

    it('handles concurrent state updates', async () => {
      const { result } = renderHook(() => useFreemiumStore());

      // Simulate concurrent updates
      const promises = [
        new Promise(resolve => {
          act(() => {
            result.current.addResponse('q1', 'answer1');
            resolve(undefined);
          });
        }),
        new Promise(resolve => {
          act(() => {
            result.current.addResponse('q2', 'answer2');
            resolve(undefined);
          });
        }),
        new Promise(resolve => {
          act(() => {
            result.current.setProgress(50);
            resolve(undefined);
          });
        })
      ];

      await Promise.all(promises);

      expect(result.current.responses).toEqual({
        q1: 'answer1',
        q2: 'answer2'
      });
      expect(result.current.progress).toBe(50);
    });
  });
});