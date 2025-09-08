import type { AssessmentFramework, Question } from '@/lib/assessment-engine/types';

export const createMockFramework = (
  overrides?: Partial<AssessmentFramework>,
): AssessmentFramework => ({
  id: 'test-framework',
  name: 'Test Framework',
  description: 'Test framework description',
  version: '1.0',
  scoringMethod: 'percentage',
  passingScore: 70,
  estimatedDuration: 30,
  tags: ['test'],
  sections: [
    {
      id: 'section-1',
      title: 'Test Section',
      description: 'Test section description',
      order: 1,
      questions: [
        {
          id: 'q1',
          type: 'radio',
          text: 'Test question 1?',
          options: [
            { value: 'yes', label: 'Yes' },
            { value: 'no', label: 'No' },
          ],
          validation: { required: true },
          weight: 1,
        },
        {
          id: 'q2',
          type: 'textarea',
          text: 'Test question 2',
          validation: { required: true, minLength: 10 },
          weight: 1,
        },
      ],
    },
  ],
  ...overrides,
});

export const createMockAssessmentContext = () => ({
  assessmentId: 'test-assessment-id',
  frameworkId: 'test-framework',
  businessProfileId: 'test-profile-id',
  answers: new Map(),
  metadata: {},
});
