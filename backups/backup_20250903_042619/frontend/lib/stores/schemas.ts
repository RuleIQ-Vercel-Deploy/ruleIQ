import { z } from 'zod';

// Assessment Schemas
export const AssessmentSchema = z.object({
  id: z.string().min(1, 'Assessment ID is required'),
  name: z.string().min(1, 'Assessment name is required'),
  status: z.enum(['draft', 'in_progress', 'completed', 'expired'], {
    errorMap: () => ({ message: 'Status must be one of: draft, in_progress, completed, expired' }),
  }),
  framework_id: z.string().min(1, 'Framework ID is required'),
  business_profile_id: z.string().min(1, 'Business profile ID is required'),
  created_at: z.string().datetime().optional(),
  updated_at: z.string().datetime().optional(),
  total_questions: z.number().int().min(0).optional(),
  answered_questions: z.number().int().min(0).optional(),
  score: z.number().min(0).max(100).optional(),
});

export const AssessmentsArraySchema = z.array(AssessmentSchema);

// Evidence Schemas
export const EvidenceItemSchema = z.object({
  id: z.string().min(1, 'Evidence ID is required'),
  title: z.string().min(1, 'Evidence title is required'),
  description: z.string().optional(),
  status: z.enum(['pending', 'collected', 'verified', 'rejected'], {
    errorMap: () => ({ message: 'Status must be one of: pending, collected, verified, rejected' }),
  }),
  evidence_type: z.string().min(1, 'Evidence type is required'),
  file_url: z.string().url().optional(),
  file_name: z.string().optional(),
  file_size: z.number().int().min(0).optional(),
  control_mapping: z.array(z.string()).optional(),
  framework_id: z.string().min(1, 'Framework ID is required'),
  business_profile_id: z.string().min(1, 'Business profile ID is required'),
  created_at: z.string().datetime().optional(),
  updated_at: z.string().datetime().optional(),
});

export const EvidenceArraySchema = z.array(EvidenceItemSchema);

// Widget Configuration Schemas
export const WidgetConfigSchema = z.object({
  id: z.string().min(1, 'Widget ID is required'),
  type: z.enum(
    [
      'compliance-score',
      'framework-progress',
      'pending-tasks',
      'activity-feed',
      'upcoming-deadlines',
      'ai-insights',
    ],
    {
      errorMap: () => ({ message: 'Invalid widget type' }),
    },
  ),
  position: z.object({
    x: z.number().int().min(0),
    y: z.number().int().min(0),
  }),
  size: z.object({
    w: z.number().int().min(1),
    h: z.number().int().min(1),
  }),
  settings: z.record(z.any()),
  isVisible: z.boolean(),
});

export const WidgetsArraySchema = z.array(WidgetConfigSchema);

// Metrics Schema
export const MetricsSchema = z.object({
  complianceScore: z.number().min(0).max(100).optional(),
  completedAssessments: z.number().int().min(0).optional(),
  pendingTasks: z.number().int().min(0).optional(),
  overall_score: z.number().min(0).max(100).optional(),
  policy_score: z.number().min(0).max(100).optional(),
  implementation_score: z.number().min(0).max(100).optional(),
  evidence_score: z.number().min(0).max(100).optional(),
  trend: z.enum(['up', 'down', 'stable']).optional(),
  domain_scores: z.record(z.number()).optional(),
  control_scores: z.record(z.number()).optional(),
  breakdown: z
    .array(
      z.object({
        framework: z.string(),
        score: z.number().min(0).max(100),
        weight: z.number().min(0).max(1),
      }),
    )
    .optional(),
});

// Framework Schema
export const FrameworkSchema = z.object({
  id: z.string().min(1, 'Framework ID is required'),
  name: z.string().min(1, 'Framework name is required'),
  description: z.string().optional(),
  version: z.string().optional(),
  status: z.enum(['active', 'deprecated', 'draft']).optional(),
});

export const FrameworksArraySchema = z.array(FrameworkSchema);

// Performance validation schemas
export const LoadingStateSchema = z.boolean();

// Helper function to safely validate and log errors
export function safeValidate<T>(schema: z.ZodSchema<T>, data: unknown, context: string): T {
  try {
    return schema.parse(data);
  } catch {
    if (error instanceof z.ZodError) {
      // TODO: Replace with proper logging

      // // TODO: Replace with proper logging
      // In development, throw the error. In production, you might want to handle it gracefully
      if (process.env.NODE_ENV === 'development') {
        throw new Error(
          `Validation failed in ${context}: ${error.errors.map((e) => e.message).join(', ')}`,
        );
      }
    }
    throw error;
  }
}
