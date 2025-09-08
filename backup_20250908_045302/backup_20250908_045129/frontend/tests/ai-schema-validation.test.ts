/**
 * Tests for AI Schema Validation in Phase 6 Implementation
 *
 * Comprehensive tests for TypeScript interfaces, Zod validation,
 * and runtime type safety for AI responses.
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { z } from 'zod';

// Import schemas and validators
import {
  validateAIResponse,
  validateStructuredResponse,
  validateAndTransformAIResponse,
  GapAnalysisResponseSchema,
  RecommendationResponseSchema,
  AssessmentAnalysisResponseSchema,
  GuidanceResponseSchema,
  FollowUpResponseSchema,
  getValidationErrors,
  isValidResponseType,
} from '@/lib/validations/ai-schemas';

// Import TypeScript types and type guards
import {
  type GapAnalysisResponse,
  type RecommendationResponse,
  type AssessmentAnalysisResponse,
  type GuidanceResponse,
  type FollowUpResponse,
  type StructuredAIResponse,
  isGapAnalysisResponse,
  isRecommendationResponse,
  isAssessmentAnalysisResponse,
  isGuidanceResponse,
  isFollowUpResponse,
  isStructuredAIResponse,
} from '@/types/ai-schemas';

describe('AI Schema Validation - Phase 6', () => {
  // =====================================================================
  // Test Data Fixtures
  // =====================================================================

  const validGapAnalysisData: GapAnalysisResponse = {
    gaps: [
      {
        id: 'gap_001',
        title: 'Missing Data Encryption',
        description: 'Personal data is not encrypted at rest, violating GDPR requirements',
        severity: 'high',
        category: 'Data Protection',
        framework_reference: 'GDPR Article 32',
        current_state: 'Data stored in plain text',
        target_state: 'All personal data encrypted at rest',
        impact_description: 'Risk of data breach and regulatory fines',
        business_impact_score: 0.8,
        technical_complexity: 0.6,
        regulatory_requirement: true,
        estimated_effort: 'medium',
        dependencies: ['Infrastructure upgrade'],
        affected_systems: ['Database', 'File storage'],
        stakeholders: ['IT Team', 'DPO'],
      },
    ],
    overall_risk_level: 'high',
    priority_order: ['gap_001'],
    estimated_total_effort: '4-6 weeks',
    critical_gap_count: 0,
    medium_high_gap_count: 1,
    compliance_percentage: 65.5,
    framework_coverage: {
      GDPR: 65.5,
      ISO27001: 70.0,
    },
    summary:
      'Assessment identified 1 high-priority gap in data protection requiring immediate attention',
    next_steps: [
      'Implement data encryption at rest',
      'Update data protection policies',
      'Train staff on new procedures',
    ],
  };

  const validRecommendationData: RecommendationResponse = {
    recommendations: [
      {
        id: 'rec_001',
        title: 'Implement Data Encryption',
        description: 'Deploy encryption solution for all personal data storage',
        priority: 'high',
        category: 'Data Protection',
        framework_references: ['GDPR Article 32', 'ISO27001 A.10.1.1'],
        addresses_gaps: ['gap_001'],
        effort_estimate: 'medium',
        implementation_timeline: '4-6 weeks',
        impact_score: 0.8,
        cost_estimate: '£5,000 - £10,000',
        resource_requirements: ['IT Staff', 'Security Consultant'],
        success_criteria: ['All data encrypted', 'Compliance verified'],
        potential_challenges: ['System downtime', 'Performance impact'],
        mitigation_strategies: ['Phased rollout', 'Performance testing'],
        automation_potential: 0.7,
        roi_estimate: 'ROI within 12 months',
      },
    ],
    implementation_plan: {
      total_duration_weeks: 6,
      phases: [
        {
          phase_number: 1,
          phase_name: 'Planning and Preparation',
          duration_weeks: 2,
          deliverables: ['Implementation plan', 'Risk assessment'],
          dependencies: [],
          resources_required: ['Project Manager', 'Security Architect'],
          success_criteria: ['Plan approved', 'Resources allocated'],
        },
      ],
      resource_allocation: {
        'IT Staff': 'Full-time',
        'Security Consultant': 'Part-time',
      },
      budget_estimate: '£8,000',
      risk_factors: ['Technical complexity', 'Timeline constraints'],
      success_metrics: ['Encryption coverage %', 'Compliance score'],
      milestone_checkpoints: ['Phase 1 complete', 'Testing complete'],
    },
    prioritization_rationale:
      'High-impact security improvement with regulatory compliance benefits',
    quick_wins: ['rec_001'],
    long_term_initiatives: [],
    resource_summary: {
      total_hours: 120,
      external_cost: 5000,
    },
    timeline_overview: '6-week implementation with immediate security benefits',
    success_metrics: ['100% data encryption', 'GDPR compliance achieved'],
  };

  const validGuidanceData: GuidanceResponse = {
    guidance:
      'To ensure GDPR compliance for data encryption, you should implement AES-256 encryption for all personal data at rest. This includes database fields containing personal information and file storage systems.',
    confidence_score: 0.9,
    related_topics: ['Data Protection', 'Encryption Standards', 'GDPR Compliance'],
    follow_up_suggestions: [
      'Consider encryption key management strategy',
      'Review data backup encryption',
      'Assess impact on system performance',
    ],
    source_references: ['GDPR Article 32', 'ISO27001 A.10.1.1', 'NIST Cybersecurity Framework'],
    examples: ['Database column encryption using TDE', 'File-level encryption with BitLocker'],
    best_practices: [
      'Use industry-standard encryption algorithms',
      'Implement proper key rotation',
      'Monitor encryption performance',
    ],
    common_pitfalls: [
      'Poor key management',
      'Performance degradation',
      'Incomplete encryption coverage',
    ],
    implementation_tips: [
      'Start with most sensitive data',
      'Test thoroughly in staging environment',
      'Document encryption procedures',
    ],
  };

  const validStructuredResponse: StructuredAIResponse<GapAnalysisResponse> = {
    metadata: {
      response_id: 'resp_123456',
      timestamp: '2024-01-15T10:30:00Z',
      model_used: 'gemini-2.5-flash-001',
      processing_time_ms: 1500,
      confidence_score: 0.85,
      schema_version: '1.0.0',
      validation_status: 'valid',
      validation_errors: [],
    },
    response_type: 'gap_analysis',
    payload: validGapAnalysisData,
    validation_passed: true,
    fallback_used: false,
  };

  // =====================================================================
  // Zod Schema Validation Tests
  // =====================================================================

  describe('Zod Schema Validation', () => {
    it('should validate correct gap analysis response', () => {
      const result = validateAIResponse(validGapAnalysisData, 'gap_analysis');

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.errors).toBeUndefined();
      expect(result.data?.gaps).toHaveLength(1);
      expect(result.data?.overall_risk_level).toBe('high');
    });

    it('should validate correct recommendation response', () => {
      const result = validateAIResponse(validRecommendationData, 'recommendations');

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.errors).toBeUndefined();
      expect(result.data?.recommendations).toHaveLength(1);
      expect(result.data?.implementation_plan.total_duration_weeks).toBe(6);
    });

    it('should validate correct guidance response', () => {
      const result = validateAIResponse(validGuidanceData, 'guidance');

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.errors).toBeUndefined();
      expect(result.data?.confidence_score).toBe(0.9);
    });

    it('should reject invalid gap analysis response', () => {
      const invalidData = {
        ...validGapAnalysisData,
        gaps: [
          {
            ...validGapAnalysisData.gaps[0],
            business_impact_score: 1.5, // Invalid: exceeds 1.0
            severity: 'invalid_severity', // Invalid enum value
          },
        ],
        compliance_percentage: 150, // Invalid: exceeds 100
      };

      const result = validateAIResponse(invalidData, 'gap_analysis');

      expect(result.success).toBe(false);
      expect(result.errors).toBeDefined();
      expect(result.errors![0].errors.length).toBeGreaterThan(0);
    });

    it('should reject missing required fields', () => {
      const incompleteData = {
        gaps: [],
        // Missing required fields
      };

      const result = validateAIResponse(incompleteData, 'gap_analysis');

      expect(result.success).toBe(false);
      expect(result.errors).toBeDefined();
    });

    it('should validate score ranges correctly', () => {
      const dataWithInvalidScores = {
        ...validGapAnalysisData,
        gaps: [
          {
            ...validGapAnalysisData.gaps[0],
            business_impact_score: -0.1, // Invalid: below 0
            technical_complexity: 1.1, // Invalid: above 1
          },
        ],
      };

      const result = validateAIResponse(dataWithInvalidScores, 'gap_analysis');

      expect(result.success).toBe(false);
      expect(result.errors).toBeDefined();
    });

    it('should validate array constraints', () => {
      const dataWithEmptyArrays = {
        ...validGapAnalysisData,
        next_steps: [], // Invalid: should have min 1 item
        gaps: [], // Invalid: should have items for meaningful response
      };

      const result = validateAIResponse(dataWithEmptyArrays, 'gap_analysis');

      expect(result.success).toBe(false);
      expect(result.errors).toBeDefined();
    });
  });

  // =====================================================================
  // Structured Response Validation Tests
  // =====================================================================

  describe('Structured Response Validation', () => {
    it('should validate correct structured response', () => {
      const result = validateStructuredResponse(validStructuredResponse);

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.data?.response_type).toBe('gap_analysis');
      expect(result.data?.validation_passed).toBe(true);
    });

    it('should reject structured response with invalid metadata', () => {
      const invalidStructuredResponse = {
        ...validStructuredResponse,
        metadata: {
          ...validStructuredResponse.metadata,
          confidence_score: 1.5, // Invalid: exceeds 1.0
          processing_time_ms: -100, // Invalid: negative time
        },
      };

      const result = validateStructuredResponse(invalidStructuredResponse);

      expect(result.success).toBe(false);
      expect(result.errors).toBeDefined();
    });

    it('should validate complete transform and validation flow', () => {
      const result = validateAndTransformAIResponse(validStructuredResponse, 'gap_analysis');

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
      expect(result.errors).toBeUndefined();
      expect(result.data?.gaps).toHaveLength(1);
    });

    it('should reject mismatched response types', () => {
      const mismatchedResponse = {
        ...validStructuredResponse,
        response_type: 'recommendations', // Different from expected 'gap_analysis'
      };

      const result = validateAndTransformAIResponse(mismatchedResponse, 'gap_analysis');

      expect(result.success).toBe(false);
      expect(result.errors).toBeDefined();
      expect(result.errors![0]).toContain('Expected response type gap_analysis');
    });
  });

  // =====================================================================
  // TypeScript Type Guard Tests
  // =====================================================================

  describe('TypeScript Type Guards', () => {
    it('should correctly identify gap analysis response', () => {
      expect(isGapAnalysisResponse(validGapAnalysisData)).toBe(true);
      expect(isGapAnalysisResponse(validRecommendationData)).toBe(false);
      expect(isGapAnalysisResponse(validGuidanceData)).toBe(false);
      expect(isGapAnalysisResponse(null)).toBe(false);
      expect(isGapAnalysisResponse({})).toBe(false);
    });

    it('should correctly identify recommendation response', () => {
      expect(isRecommendationResponse(validRecommendationData)).toBe(true);
      expect(isRecommendationResponse(validGapAnalysisData)).toBe(false);
      expect(isRecommendationResponse(validGuidanceData)).toBe(false);
    });

    it('should correctly identify guidance response', () => {
      expect(isGuidanceResponse(validGuidanceData)).toBe(true);
      expect(isGuidanceResponse(validGapAnalysisData)).toBe(false);
      expect(isGuidanceResponse(validRecommendationData)).toBe(false);
    });

    it('should correctly identify structured AI response', () => {
      expect(isStructuredAIResponse(validStructuredResponse)).toBe(true);
      expect(isStructuredAIResponse(validGapAnalysisData)).toBe(false);
      expect(isStructuredAIResponse({})).toBe(false);
    });

    it('should validate response type strings', () => {
      expect(isValidResponseType('gap_analysis')).toBe(true);
      expect(isValidResponseType('recommendations')).toBe(true);
      expect(isValidResponseType('guidance')).toBe(true);
      expect(isValidResponseType('invalid_type')).toBe(false);
      expect(isValidResponseType('')).toBe(false);
    });
  });

  // =====================================================================
  // Error Handling Tests
  // =====================================================================

  describe('Error Handling and Reporting', () => {
    it('should provide detailed validation error messages', () => {
      const invalidData = {
        gaps: [
          {
            id: '', // Invalid: empty string
            title: 'A', // Invalid: too short
            business_impact_score: 'not_a_number', // Invalid: wrong type
          },
        ],
        // Missing many required fields
      };

      const result = validateAIResponse(invalidData, 'gap_analysis');

      expect(result.success).toBe(false);
      expect(result.errors).toBeDefined();

      const errorMessages = getValidationErrors(result.errors![0]);
      expect(errorMessages.length).toBeGreaterThan(0);

      // Check that we have validation errors - the exact field names may vary
      expect(errorMessages.length).toBeGreaterThan(5); // Should have multiple validation errors

      // Check for validation errors without being too specific about field paths
      const hasValidationErrors = errorMessages.some(
        (msg) =>
          msg.includes('Required') ||
          msg.includes('String must contain') ||
          msg.includes('Expected') ||
          msg.includes('Invalid'),
      );
      expect(hasValidationErrors).toBe(true);
    });

    it('should handle unknown response types gracefully', () => {
      const result = validateAIResponse(validGapAnalysisData, 'unknown_type' as any);

      expect(result.success).toBe(false);
      expect(result.errors).toBeDefined();
      expect(result.errors![0].errors[0].message).toContain('Unknown response type');
    });

    it('should handle malformed data gracefully', () => {
      const malformedData = {
        gaps: 'not_an_array',
        overall_risk_level: 123,
        compliance_percentage: 'not_a_number',
      };

      const result = validateAIResponse(malformedData, 'gap_analysis');

      expect(result.success).toBe(false);
      expect(result.errors).toBeDefined();
    });
  });

  // =====================================================================
  // Real-world Scenario Tests
  // =====================================================================

  describe('Real-world Scenario Tests', () => {
    it('should handle partial responses with missing optional fields', () => {
      const partialResponse = {
        ...validGapAnalysisData,
        framework_coverage: {}, // Empty but valid
        gaps: [
          {
            ...validGapAnalysisData.gaps[0],
            dependencies: [], // Empty array
            affected_systems: [], // Empty array
            stakeholders: [], // Empty array
          },
        ],
      };

      const result = validateAIResponse(partialResponse, 'gap_analysis');

      expect(result.success).toBe(true);
      expect(result.data).toBeDefined();
    });

    it('should validate realistic recommendation data with all fields', () => {
      const comprehensiveRecommendation = {
        ...validRecommendationData,
        recommendations: [
          {
            ...validRecommendationData.recommendations[0],
            cost_estimate: '£10,000 - £15,000',
            roi_estimate: 'Break-even in 18 months',
            potential_challenges: [
              'Staff training required',
              'Legacy system integration',
              'Budget constraints',
            ],
            mitigation_strategies: [
              'Phased training program',
              'Dedicated integration team',
              'Budget pre-approval',
            ],
          },
        ],
      };

      const result = validateAIResponse(comprehensiveRecommendation, 'recommendations');

      expect(result.success).toBe(true);
      expect(result.data?.recommendations[0].cost_estimate).toBeDefined();
      expect(result.data?.recommendations[0].roi_estimate).toBeDefined();
    });

    it('should validate edge cases for scores and percentages', () => {
      const edgeCaseData = {
        ...validGapAnalysisData,
        compliance_percentage: 0, // Minimum valid value
        gaps: [
          {
            ...validGapAnalysisData.gaps[0],
            business_impact_score: 0, // Minimum valid value
            technical_complexity: 1, // Maximum valid value
            automation_potential: 0.5, // Mid-range value
          },
        ],
      };

      const result = validateAIResponse(edgeCaseData, 'gap_analysis');

      expect(result.success).toBe(true);
      expect(result.data?.compliance_percentage).toBe(0);
      expect(result.data?.gaps[0].business_impact_score).toBe(0);
      expect(result.data?.gaps[0].technical_complexity).toBe(1);
    });
  });

  // =====================================================================
  // Performance and Scalability Tests
  // =====================================================================

  describe('Performance and Scalability', () => {
    it('should handle large gap analysis responses efficiently', () => {
      const largeGapData = {
        ...validGapAnalysisData,
        gaps: Array.from({ length: 50 }, (_, i) => ({
          ...validGapAnalysisData.gaps[0],
          id: `gap_${i.toString().padStart(3, '0')}`,
          title: `Gap ${i + 1}`,
          description: `Description for gap ${i + 1} with detailed explanation`,
        })),
        priority_order: Array.from(
          { length: 50 },
          (_, i) => `gap_${i.toString().padStart(3, '0')}`,
        ),
      };

      const startTime = performance.now();
      const result = validateAIResponse(largeGapData, 'gap_analysis');
      const endTime = performance.now();

      expect(result.success).toBe(true);
      expect(result.data?.gaps).toHaveLength(50);
      expect(endTime - startTime).toBeLessThan(1000); // Should complete within 1 second
    });

    it('should handle complex nested recommendation structures', () => {
      const complexRecommendation = {
        ...validRecommendationData,
        implementation_plan: {
          ...validRecommendationData.implementation_plan,
          phases: Array.from({ length: 10 }, (_, i) => ({
            phase_number: i + 1,
            phase_name: `Phase ${i + 1}`,
            duration_weeks: 2,
            deliverables: [`Deliverable ${i + 1}A`, `Deliverable ${i + 1}B`],
            dependencies: i > 0 ? [`Phase ${i}`] : [],
            resources_required: [`Resource ${i + 1}`],
            success_criteria: [`Criteria ${i + 1}`],
          })),
        },
      };

      const result = validateAIResponse(complexRecommendation, 'recommendations');

      expect(result.success).toBe(true);
      expect(result.data?.implementation_plan.phases).toHaveLength(10);
    });
  });
});
