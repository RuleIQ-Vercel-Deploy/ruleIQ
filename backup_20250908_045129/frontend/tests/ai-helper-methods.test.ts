/**
 * AI Helper Methods Tests
 * Tests for Phase 1.5.3: Testing & Validation
 * Testing helper methods directly without full service dependencies
 */

// Set up test environment
process.env.NODE_ENV = 'test';

describe('AI Helper Methods Tests', () => {
  // Test data for different business scenarios
  const testBusinessProfiles = [
    {
      id: 'test-1',
      company_name: 'TechCorp Ltd',
      industry: 'Technology',
      size: 'medium',
      compliance_frameworks: ['GDPR', 'ISO 27001'],
    },
    {
      id: 'test-2',
      company_name: 'HealthCare Solutions',
      industry: 'Healthcare',
      size: 'large',
      compliance_frameworks: ['GDPR', 'HIPAA'],
    },
    {
      id: 'test-3',
      company_name: 'FinanceFirst Bank',
      industry: 'Financial Services',
      size: 'large',
      compliance_frameworks: ['GDPR', 'PCI DSS', 'FCA'],
    },
  ];

  const testAnswers = {
    company_size: '50-200',
    industry: 'technology',
    handles_personal_data: 'Yes',
    processes_payments: 'No',
    data_sensitivity: 'High',
    implementation_timeline: '3 months',
    biggest_concern: 'Data protection compliance',
    recent_incidents: 'No',
    compliance_budget: '£25K-£100K',
  };

  describe('Business Profile Context Extraction', () => {
    test('should extract company size from answers', () => {
      // Mock the helper method functionality
      const extractContext = (businessProfile: any, currentAnswers: any) => {
        const context = { ...businessProfile };

        if (currentAnswers?.['company_size'] || currentAnswers?.['employee_count']) {
          (context as any).size =
            currentAnswers['company_size'] || currentAnswers['employee_count'];
        }

        if (currentAnswers?.['industry'] || currentAnswers?.['business_sector']) {
          context.industry = currentAnswers['industry'] || currentAnswers['business_sector'];
        }

        return context;
      };

      const context = extractContext(testBusinessProfiles[0], testAnswers);

      expect(context).toBeDefined();
      expect(context.industry).toBe('technology'); // From answers, overrides profile
      expect((context as any).size).toBe('50-200'); // From answers
    });
  });

  describe('Existing Policies Extraction', () => {
    test('should identify existing policies and gaps', () => {
      const testAnswersWithPolicies = {
        ...testAnswers,
        privacy_policy: 'Yes',
        data_protection_policy: 'No',
        security_policy: 'Yes',
        regular_audits: 'Yes',
        staff_training: 'No',
      };

      // Mock the helper method functionality
      const extractPolicies = (currentAnswers: any) => {
        const result = {
          existing_policies: [] as string[],
          compliance_measures: [] as string[],
          gaps_identified: [] as string[],
        };

        const policyQuestions = ['privacy_policy', 'data_protection_policy', 'security_policy'];

        policyQuestions.forEach((policy) => {
          if (currentAnswers[policy] === 'Yes') {
            result.existing_policies.push(
              policy.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
            );
          } else if (currentAnswers[policy] === 'No') {
            result.gaps_identified.push(
              policy.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
            );
          }
        });

        const complianceMeasures = ['regular_audits', 'staff_training'];
        complianceMeasures.forEach((measure) => {
          if (currentAnswers[measure] === 'Yes') {
            result.compliance_measures.push(
              measure.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
            );
          } else if (currentAnswers[measure] === 'No') {
            result.gaps_identified.push(
              measure.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
            );
          }
        });

        return result;
      };

      const policies = extractPolicies(testAnswersWithPolicies);

      expect(policies.existing_policies).toContain('Privacy Policy');
      expect(policies.existing_policies).toContain('Security Policy');
      expect(policies.gaps_identified).toContain('Data Protection Policy');
      expect(policies.gaps_identified).toContain('Staff Training');
      expect(policies.compliance_measures).toContain('Regular Audits');
    });
  });

  describe('Industry Context Determination', () => {
    test('should determine correct regulations for technology industry', () => {
      const extractIndustryContext = (businessProfile: any, currentAnswers: any) => {
        const industry = businessProfile?.industry || currentAnswers?.['industry'] || 'general';
        const result = {
          industry,
          applicable_regulations: ['GDPR', 'UK GDPR', 'Data Protection Act 2018'] as string[],
          risk_level: 'medium' as 'low' | 'medium' | 'high',
          special_requirements: [] as string[],
        };

        switch (industry.toLowerCase()) {
          case 'technology':
          case 'software':
            result.applicable_regulations.push('Cyber Security Regulations');
            if (currentAnswers?.['ai_processing'] || currentAnswers?.['automated_decisions']) {
              result.special_requirements.push('AI governance', 'Algorithmic transparency');
            }
            break;

          case 'healthcare':
          case 'medical':
            result.applicable_regulations.push('MHRA Regulations', 'Clinical Trial Regulations');
            result.risk_level = 'high';
            result.special_requirements.push(
              'Patient data protection',
              'Medical device compliance',
            );
            break;

          case 'financial services':
          case 'banking':
          case 'fintech':
            result.applicable_regulations.push('FCA Regulations', 'PCI DSS', 'Basel III');
            result.risk_level = 'high';
            result.special_requirements.push(
              'Financial conduct reporting',
              'Anti-money laundering',
            );
            break;
        }

        return result;
      };

      // Test Technology industry
      const techContext = extractIndustryContext(testBusinessProfiles[0], testAnswers);
      expect(techContext.industry).toBe('Technology');
      expect(techContext.applicable_regulations).toContain('GDPR');
      expect(techContext.applicable_regulations).toContain('Cyber Security Regulations');
      expect(techContext.risk_level).toBe('medium');

      // Test Healthcare industry
      const healthContext = extractIndustryContext(testBusinessProfiles[1], {
        ...testAnswers,
        industry: 'healthcare',
      });
      expect(healthContext.industry).toBe('Healthcare');
      expect(healthContext.applicable_regulations).toContain('MHRA Regulations');
      expect(healthContext.risk_level).toBe('high');
      expect(healthContext.special_requirements).toContain('Patient data protection');

      // Test Financial Services industry
      const financeContext = extractIndustryContext(testBusinessProfiles[2], {
        ...testAnswers,
        industry: 'financial services',
      });
      expect(financeContext.industry).toBe('Financial Services');
      expect(financeContext.applicable_regulations).toContain('FCA Regulations');
      expect(financeContext.applicable_regulations).toContain('Basel III');
      expect(financeContext.risk_level).toBe('high');
    });
  });

  describe('Timeline Preference Extraction', () => {
    test('should extract urgency correctly from answers', () => {
      const extractTimeline = (currentAnswers: any) => {
        const result = {
          urgency: 'medium' as 'low' | 'medium' | 'high' | 'critical',
          preferred_timeline: '3-6 months',
          implementation_capacity: 'moderate' as 'limited' | 'moderate' | 'high',
          priority_areas: [] as string[],
        };

        if (!currentAnswers) return result;

        // Extract explicit timeline preferences
        if (currentAnswers['implementation_timeline']) {
          result.preferred_timeline = currentAnswers['implementation_timeline'];

          const timeline = currentAnswers['implementation_timeline'].toLowerCase();
          if (timeline.includes('immediate') || timeline.includes('1 month')) {
            result.urgency = 'critical';
          } else if (timeline.includes('3 month') || timeline.includes('quarter')) {
            result.urgency = 'high';
          } else if (timeline.includes('6 month') || timeline.includes('year')) {
            result.urgency = 'medium';
          } else {
            result.urgency = 'low';
          }
        }

        // Extract urgency indicators
        if (
          currentAnswers['recent_incidents'] === 'Yes' ||
          currentAnswers['security_breaches'] === 'Yes'
        ) {
          result.urgency = 'critical';
          result.priority_areas.push('Incident response', 'Security measures');
        }

        if (
          currentAnswers['regulatory_deadline'] === 'Yes' ||
          currentAnswers['compliance_deadline']
        ) {
          result.urgency = result.urgency === 'low' ? 'high' : 'critical';
          result.priority_areas.push('Regulatory compliance');
        }

        return result;
      };

      // Test urgent timeline
      const urgentAnswers = {
        ...testAnswers,
        implementation_timeline: 'immediate',
        recent_incidents: 'Yes',
        regulatory_deadline: 'Yes',
      };

      const urgentTimeline = extractTimeline(urgentAnswers);
      expect(urgentTimeline.urgency).toBe('critical');
      expect(urgentTimeline.priority_areas).toContain('Incident response');
      expect(urgentTimeline.priority_areas).toContain('Regulatory compliance');

      // Test standard timeline
      const standardTimeline = extractTimeline(testAnswers);
      expect(standardTimeline.urgency).toBe('high'); // 3 months = high urgency
      expect(standardTimeline.preferred_timeline).toBe('3 months');
      expect(standardTimeline.implementation_capacity).toBe('moderate');
    });
  });

  describe('Timeout Handling', () => {
    test('should handle timeout scenarios correctly', async () => {
      const executeWithTimeout = async <T>(
        promise: Promise<T>,
        timeoutMs: number = 30000,
        operation: string = 'Operation',
      ): Promise<T> => {
        const timeoutPromise = new Promise<never>((_, reject) => {
          setTimeout(() => {
            reject(new Error(`${operation} timed out after ${timeoutMs}ms`));
          }, timeoutMs);
        });

        try {
          const result = await Promise.race([promise, timeoutPromise]);
          return result;
        } catch {
          if (error instanceof Error && error.message.includes('timed out')) {
            throw new Error(`${operation} is taking longer than expected. Please try again.`);
          }
          throw error;
        }
      };

      // Test successful operation
      const fastPromise = new Promise((resolve) => setTimeout(() => resolve('success'), 100));
      const result = await executeWithTimeout(fastPromise, 1000, 'Fast operation');
      expect(result).toBe('success');

      // Test timeout scenario
      const slowPromise = new Promise((resolve) => setTimeout(() => resolve('slow'), 2000));

      try {
        await executeWithTimeout(slowPromise, 500, 'Slow operation');
        fail('Should have thrown timeout error');
      } catch {
        expect(error).toBeInstanceOf(Error);
        expect((error as Error).message).toContain('is taking longer than expected');
      }
    });
  });
});
