// Central export file for all validation schemas
export * from './auth';
export * from './business-profile';

// Evidence validation schemas
import { z } from 'zod';

export const evidenceSchema = z.object({
  title: z.string().min(1, 'Title is required').max(255, 'Title must be less than 255 characters'),
  description: z.string().max(2000, 'Description must be less than 2000 characters').optional(),
  control_id: z.string().min(1, 'Control ID is required'),
  framework: z.string().min(1, 'Framework is required'),
  business_profile_id: z.string().min(1, 'Business profile is required'),
  evidence_type: z.string().min(1, 'Evidence type is required'),
  source: z.string().optional(),
  tags: z.array(z.string()).default([]),
});

// Assessment validation schemas
export const assessmentResponseSchema = z.object({
  question_id: z.string(),
  response_type: z.enum(['multiple_choice', 'text', 'boolean']),
  response_value: z.union([z.string(), z.boolean(), z.array(z.string())]),
});

export const assessmentSessionSchema = z.object({
  business_profile_id: z.string().min(1, 'Business profile is required'),
  framework_id: z.string().optional(),
  responses: z.array(assessmentResponseSchema).default([]),
});

// Policy generation validation schemas
export const policyGenerationSchema = z.object({
  framework: z.string().min(1, 'Framework is required'),
  business_profile_id: z.string().min(1, 'Business profile is required'),
  policy_title: z
    .string()
    .min(1, 'Policy title is required')
    .max(255, 'Policy title must be less than 255 characters'),
  tone: z.enum(['formal', 'informal', 'strict'], {
    errorMap: () => ({ message: 'Please select a tone' }),
  }),
  specific_controls: z.array(z.string()).default([]),
});

// Implementation plan validation schemas
export const implementationPlanSchema = z.object({
  business_profile_id: z.string().min(1, 'Business profile is required'),
  framework_id: z.string().min(1, 'Framework is required'),
  title: z.string().min(1, 'Title is required').max(255, 'Title must be less than 255 characters'),
  start_date: z.string().min(1, 'Start date is required'),
  end_date: z.string().min(1, 'End date is required'),
});

// Report generation validation schemas
export const reportGenerationSchema = z.object({
  business_profile_id: z.string().min(1, 'Business profile is required'),
  report_type: z.enum(
    [
      'executive_summary',
      'gap_analysis',
      'evidence_report',
      'audit_readiness',
      'compliance_status',
      'control_matrix',
      'risk_assessment',
    ],
    {
      errorMap: () => ({ message: 'Please select a report type' }),
    },
  ),
  format: z.enum(['pdf', 'excel', 'html', 'csv'], {
    errorMap: () => ({ message: 'Please select a format' }),
  }),
  start_date: z.string().optional(),
  end_date: z.string().optional(),
  frameworks: z.array(z.string()).default([]),
  include_evidence: z.boolean().default(true),
});

// Chat validation schemas
export const chatMessageSchema = z.object({
  message: z
    .string()
    .min(1, 'Message cannot be empty')
    .max(2000, 'Message must be less than 2000 characters'),
});

// Search validation schemas
export const searchSchema = z.object({
  query: z.string().min(1, 'Search query is required'),
  filters: z
    .object({
      framework: z.string().optional(),
      evidence_type: z.string().optional(),
      status: z.string().optional(),
    })
    .optional(),
});

// Integration validation schemas
export const integrationConfigSchema = z.object({
  provider: z.enum(['google_workspace', 'microsoft_365', 'slack', 'github', 'jira', 'azure_ad'], {
    errorMap: () => ({ message: 'Please select a provider' }),
  }),
  credentials: z.record(z.string()),
  settings: z.record(z.any()).optional(),
});

// Type exports for all schemas
export type EvidenceFormData = z.infer<typeof evidenceSchema>;
export type AssessmentResponseData = z.infer<typeof assessmentResponseSchema>;
export type AssessmentSessionData = z.infer<typeof assessmentSessionSchema>;
export type PolicyGenerationData = z.infer<typeof policyGenerationSchema>;
export type ImplementationPlanData = z.infer<typeof implementationPlanSchema>;
export type ReportGenerationData = z.infer<typeof reportGenerationSchema>;
export type ChatMessageData = z.infer<typeof chatMessageSchema>;
export type SearchData = z.infer<typeof searchSchema>;
export type IntegrationConfigData = z.infer<typeof integrationConfigSchema>;
