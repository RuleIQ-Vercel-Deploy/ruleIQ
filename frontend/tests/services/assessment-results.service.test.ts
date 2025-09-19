import { describe, it, expect, beforeEach, vi } from 'vitest';
import { AssessmentResultsService } from '@/lib/services/assessment-results.service';
import type { AssessmentResultsResponse, ComplianceGap } from '@/types/freemium';

describe('AssessmentResultsService', () => {
  let service: AssessmentResultsService;

  beforeEach(() => {
    service = new AssessmentResultsService();
    // Clear any cached data
    service.clearCache();
  });

  describe('extractSectionScores', () => {
    const createMockResults = (gaps: Partial<ComplianceGap>[]): AssessmentResultsResponse => ({
      session_id: 'test-session',
      compliance_score: 75,
      risk_score: 25,
      completion_percentage: 100,
      results_generated_at: new Date().toISOString(),
      compliance_gaps: gaps as ComplianceGap[],
      recommendations: [],
      results_summary: 'Test summary',
      assessment_stage: 'results',
      lead_id: 'test-lead',
    });

    it('should handle gaps with category field', () => {
      const results = createMockResults([
        {
          category: 'Data Protection',
          severity: 'high',
          description: 'Test gap 1',
          recommendation: 'Test recommendation 1',
          estimated_effort: '1 week',
          regulatory_impact: 'High',
        },
        {
          category: 'Data Protection',
          severity: 'medium',
          description: 'Test gap 2',
          recommendation: 'Test recommendation 2',
          estimated_effort: '2 weeks',
          regulatory_impact: 'Medium',
        },
      ]);

      // Access private method via reflection for testing
      const extractSectionScores = (service as any).extractSectionScores.bind(service);
      const scores = extractSectionScores(results);

      expect(scores).toBeDefined();
      expect(scores['Data Protection']).toBeDefined();
      expect(scores['Data Protection']).toBeGreaterThanOrEqual(0);
      expect(scores['Data Protection']).toBeLessThanOrEqual(100);
    });

    it('should handle gaps with area field instead of category', () => {
      const results = createMockResults([
        {
          area: 'Access Control',
          severity: 'critical' as const,
          description: 'Test gap',
          recommendation: 'Test recommendation',
          estimated_effort: '1 week',
          regulatory_impact: 'Critical',
          category: undefined, // Explicitly set to undefined to test the fallback
        } as any, // Using 'any' to simulate alternative shape
      ]);

      const extractSectionScores = (service as any).extractSectionScores.bind(service);
      const scores = extractSectionScores(results);

      expect(scores).toBeDefined();
      expect(scores['Access Control']).toBeDefined();
      expect(scores['Access Control']).toBe(0); // Critical severity maps to 0
    });

    it('should handle gaps with section field as fallback', () => {
      const results = createMockResults([
        {
          section: 'Risk Management',
          severity: 'low',
          description: 'Test gap',
          recommendation: 'Test recommendation',
          estimated_effort: '1 week',
          regulatory_impact: 'Low',
        } as any, // Using 'any' to simulate alternative shape
      ]);

      const extractSectionScores = (service as any).extractSectionScores.bind(service);
      const scores = extractSectionScores(results);

      expect(scores).toBeDefined();
      expect(scores['Risk Management']).toBeDefined();
      expect(scores['Risk Management']).toBe(75); // Low severity maps to 75
    });

    it('should use General Compliance fallback when no section identifier is present', () => {
      const results = createMockResults([
        {
          severity: 'medium',
          description: 'Test gap',
          recommendation: 'Test recommendation',
          estimated_effort: '1 week',
          regulatory_impact: 'Medium',
        } as any, // Simulating a gap with no category/area/section field
      ]);

      const extractSectionScores = (service as any).extractSectionScores.bind(service);
      const scores = extractSectionScores(results);

      expect(scores).toBeDefined();
      expect(scores['General Compliance']).toBeDefined();
      expect(scores['General Compliance']).toBe(50); // Medium severity maps to 50
    });

    it('should handle mixed gap shapes in the same result', () => {
      const results = createMockResults([
        {
          category: 'Data Protection',
          severity: 'high',
          description: 'Gap with category',
          recommendation: 'Test',
          estimated_effort: '1 week',
          regulatory_impact: 'High',
        },
        {
          area: 'Access Control',
          severity: 'medium',
          description: 'Gap with area',
          recommendation: 'Test',
          estimated_effort: '1 week',
          regulatory_impact: 'Medium',
        } as any,
        {
          section: 'Risk Management',
          severity: 'low',
          description: 'Gap with section',
          recommendation: 'Test',
          estimated_effort: '1 week',
          regulatory_impact: 'Low',
        } as any,
      ]);

      const extractSectionScores = (service as any).extractSectionScores.bind(service);
      const scores = extractSectionScores(results);

      expect(scores).toBeDefined();
      expect(Object.keys(scores)).toHaveLength(3);
      expect(scores['Data Protection']).toBe(25); // High severity
      expect(scores['Access Control']).toBe(50); // Medium severity
      expect(scores['Risk Management']).toBe(75); // Low severity
    });

    it('should generate default sections when no gaps are present', () => {
      const results = createMockResults([]);

      const extractSectionScores = (service as any).extractSectionScores.bind(service);
      const scores = extractSectionScores(results);

      expect(scores).toBeDefined();
      expect(Object.keys(scores).length).toBeGreaterThan(0);
      // Should have default sections
      expect(scores['Data Protection']).toBeDefined();
      expect(scores['Access Control']).toBeDefined();
      expect(scores['Risk Management']).toBeDefined();
    });

    it('should calculate average scores for multiple gaps in same section', () => {
      const results = createMockResults([
        {
          category: 'Data Protection',
          severity: 'high',
          description: 'Gap 1',
          recommendation: 'Test',
          estimated_effort: '1 week',
          regulatory_impact: 'High',
        },
        {
          category: 'Data Protection',
          severity: 'low',
          description: 'Gap 2',
          recommendation: 'Test',
          estimated_effort: '1 week',
          regulatory_impact: 'Low',
        },
      ]);

      const extractSectionScores = (service as any).extractSectionScores.bind(service);
      const scores = extractSectionScores(results);

      expect(scores['Data Protection']).toBe(50); // Average of 25 (high) and 75 (low)
    });
  });

  describe('generateSectionDetails', () => {
    it('should use the same section grouping logic as extractSectionScores', () => {
      const results: AssessmentResultsResponse = {
        session_id: 'test-session',
        compliance_score: 75,
        risk_score: 25,
        completion_percentage: 100,
        results_generated_at: new Date().toISOString(),
        compliance_gaps: [
          {
            category: 'Data Protection',
            severity: 'high',
            description: 'Test gap',
            recommendation: 'Test recommendation',
            estimated_effort: '1 week',
            regulatory_impact: 'High',
          },
          {
            area: 'Access Control',
            severity: 'medium',
            description: 'Test gap 2',
            recommendation: 'Test recommendation 2',
            estimated_effort: '2 weeks',
            regulatory_impact: 'Medium',
          } as any,
        ],
        recommendations: [],
        results_summary: 'Test summary',
        assessment_stage: 'results',
        lead_id: 'test-lead',
      };

      const sectionDetails = service.generateSectionDetails(results);

      expect(sectionDetails).toBeDefined();
      expect(sectionDetails.length).toBeGreaterThan(0);

      // Should have sections for both Data Protection and Access Control
      const sectionNames = sectionDetails.map(d => d.sectionName);
      expect(sectionNames).toContain('Data Protection');
      expect(sectionNames).toContain('Access Control');
    });
  });
});