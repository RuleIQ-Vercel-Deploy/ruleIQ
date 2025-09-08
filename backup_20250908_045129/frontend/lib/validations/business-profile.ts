/**
 * Business Profile Validation Schemas
 *
 * Comprehensive validation schemas using clean, descriptive field names.
 * These schemas validate the frontend data before it's mapped to API format.
 */

import { z } from 'zod';

import {
  INDUSTRIES,
  ANNUAL_REVENUE_RANGES,
  COUNTRIES,
  COMPLIANCE_FRAMEWORKS,
  CLOUD_PROVIDERS,
  SAAS_TOOLS,
  DEVELOPMENT_TOOLS,
  COMPLIANCE_BUDGET_RANGES,
  COMPLIANCE_TIMELINE_OPTIONS,
} from '@/types/business-profile';

// Base validation schemas for reuse
const nonEmptyString = z.string().min(1, 'This field is required').trim();
// const _optionalString = z.string().optional();
const positiveInteger = z.number().int().positive('Must be a positive number');

// Company Information Schema
export const companyInfoSchema = z.object({
  company_name: nonEmptyString
    .min(2, 'Company name must be at least 2 characters')
    .max(100, 'Company name must be less than 100 characters')
    .describe('Legal name of the company'),

  industry: z
    .enum(INDUSTRIES, {
      errorMap: () => ({ message: 'Please select a valid industry' }),
    })
    .describe('Primary industry sector'),

  employee_count: positiveInteger
    .max(1000000, 'Employee count seems unrealistic')
    .describe('Total number of employees'),

  annual_revenue: z.enum(ANNUAL_REVENUE_RANGES).optional().describe('Annual revenue range'),

  country: z
    .enum(COUNTRIES, {
      errorMap: () => ({ message: 'Please select a valid country' }),
    })
    .describe('Primary country of operation'),
});

// Compliance Profile Schema
export const complianceProfileSchema = z.object({
  data_sensitivity: z
    .enum(['Low', 'Moderate', 'High', 'Confidential'], {
      errorMap: () => ({ message: 'Please select a data sensitivity level' }),
    })
    .describe('Level of data sensitivity handled'),

  // Business characteristics with descriptive names
  handles_personal_data: z
    .boolean()
    .describe('Whether the company handles personal data of individuals'),

  processes_payments: z.boolean().describe('Whether the company processes payment information'),

  stores_health_data: z.boolean().describe('Whether the company stores health or medical data'),

  provides_financial_services: z
    .boolean()
    .describe('Whether the company provides financial services'),

  operates_critical_infrastructure: z
    .boolean()
    .describe('Whether the company operates critical infrastructure'),

  has_international_operations: z
    .boolean()
    .describe('Whether the company has international operations'),
});

// Technology Stack Schema
export const technologyStackSchema = z.object({
  cloud_providers: z
    .array(z.enum([...CLOUD_PROVIDERS, 'Other']))
    .default([])
    .describe('Cloud service providers used'),

  saas_tools: z
    .array(z.enum([...SAAS_TOOLS, 'Other']))
    .default([])
    .describe('Software-as-a-Service tools used'),

  development_tools: z
    .array(z.enum([...DEVELOPMENT_TOOLS, 'Other']))
    .default([])
    .describe('Development and deployment tools used'),
});

// Compliance Goals Schema
export const complianceGoalsSchema = z.object({
  existing_frameworks: z
    .array(z.enum([...COMPLIANCE_FRAMEWORKS, 'Other']))
    .default([])
    .describe('Compliance frameworks currently implemented'),

  planned_frameworks: z
    .array(z.enum([...COMPLIANCE_FRAMEWORKS, 'Other']))
    .default([])
    .describe('Compliance frameworks planned for implementation'),

  compliance_budget: z
    .enum(COMPLIANCE_BUDGET_RANGES)
    .optional()
    .describe('Budget allocated for compliance activities'),

  compliance_timeline: z
    .enum(COMPLIANCE_TIMELINE_OPTIONS)
    .optional()
    .describe('Timeline for achieving compliance goals'),
});

// Base schema without refinements
const businessProfileBaseSchema = z.object({
  // Merge all step schemas
  ...companyInfoSchema.shape,
  ...complianceProfileSchema.shape,
  ...technologyStackSchema.shape,
  ...complianceGoalsSchema.shape,

  // Assessment metadata
  assessment_completed: z.boolean().default(false),
  assessment_data: z.record(z.any()).default({}),
});

// Complete Business Profile Schema with refinements
export const businessProfileSchema = businessProfileBaseSchema
  .refine(
    (data) => {
      // Custom validation: If handles personal data, should consider GDPR
      if (
        data.handles_personal_data &&
        !data.existing_frameworks.includes('GDPR') &&
        !data.planned_frameworks.includes('GDPR')
      ) {
        return false;
      }
      return true;
    },
    {
      message: 'Companies handling personal data should consider GDPR compliance',
      path: ['planned_frameworks'],
    },
  )
  .refine(
    (data) => {
      // Custom validation: Financial services should consider relevant frameworks
      if (
        data.provides_financial_services &&
        !data.existing_frameworks.some((f) => ['PCI DSS', 'FCA', 'SOC 2'].includes(f)) &&
        !data.planned_frameworks.some((f) => ['PCI DSS', 'FCA', 'SOC 2'].includes(f))
      ) {
        return false;
      }
      return true;
    },
    {
      message: 'Financial services should consider PCI DSS, FCA, or SOC 2 compliance',
      path: ['planned_frameworks'],
    },
  );

// Form data schema (excludes metadata) - using base schema
export const businessProfileFormSchema = businessProfileBaseSchema.omit({
  assessment_completed: true,
  assessment_data: true,
});

// Step-specific schemas for wizard validation
export const wizardStepSchemas = {
  'company-info': companyInfoSchema,
  'compliance-profile': complianceProfileSchema,
  'technology-stack': technologyStackSchema,
  'compliance-goals': complianceGoalsSchema,
} as const;

// Partial schemas for draft saving
export const partialCompanyInfoSchema = companyInfoSchema.partial();
export const partialComplianceProfileSchema = complianceProfileSchema.partial();
export const partialTechnologyStackSchema = technologyStackSchema.partial();
export const partialComplianceGoalsSchema = complianceGoalsSchema.partial();

// Update schema for partial updates
export const businessProfileUpdateSchema = businessProfileFormSchema.partial();

// Type inference
export type CompanyInfoFormData = z.infer<typeof companyInfoSchema>;
export type ComplianceProfileFormData = z.infer<typeof complianceProfileSchema>;
export type TechnologyStackFormData = z.infer<typeof technologyStackSchema>;
export type ComplianceGoalsFormData = z.infer<typeof complianceGoalsSchema>;
export type BusinessProfileFormData = z.infer<typeof businessProfileFormSchema>;
export type BusinessProfileUpdateData = z.infer<typeof businessProfileUpdateSchema>;

// Validation helper functions
export function validateWizardStep(
  stepId: keyof typeof wizardStepSchemas,
  data: unknown,
): { success: boolean; errors?: z.ZodError; data?: any } {
  const schema = wizardStepSchemas[stepId];
  const result = schema.safeParse(data);

  if (result.success) {
    return { success: true, data: result.data };
  } else {
    return { success: false, errors: result.error };
  }
}

export function validateCompleteProfile(data: unknown): {
  success: boolean;
  errors?: z.ZodError;
  data?: BusinessProfileFormData;
} {
  const result = businessProfileFormSchema.safeParse(data);

  if (result.success) {
    return { success: true, data: result.data };
  } else {
    return { success: false, errors: result.error };
  }
}

// Custom validation rules
export const customValidationRules = {
  // Check if company size matches employee count
  validateCompanySize: (employeeCount: number, annualRevenue?: string): string[] => {
    const warnings: string[] = [];

    if (employeeCount > 1000 && annualRevenue === 'Under £1M') {
      warnings.push(
        'Large employee count with low revenue may indicate non-profit or government organization',
      );
    }

    if (employeeCount < 10 && annualRevenue === 'Over £100M') {
      warnings.push('High revenue with small team may indicate specialized or high-value services');
    }

    return warnings;
  },

  // Validate framework selection based on business characteristics
  validateFrameworkSelection: (profile: Partial<BusinessProfileFormData>): string[] => {
    const recommendations: string[] = [];

    if (
      profile.handles_personal_data &&
      !profile.existing_frameworks?.includes('GDPR') &&
      !profile.planned_frameworks?.includes('GDPR')
    ) {
      recommendations.push('Consider GDPR compliance for personal data handling');
    }

    if (
      profile.processes_payments &&
      !profile.existing_frameworks?.includes('PCI DSS') &&
      !profile.planned_frameworks?.includes('PCI DSS')
    ) {
      recommendations.push('Consider PCI DSS compliance for payment processing');
    }

    if (
      profile.stores_health_data &&
      !profile.existing_frameworks?.includes('HIPAA') &&
      !profile.planned_frameworks?.includes('HIPAA')
    ) {
      recommendations.push('Consider HIPAA compliance for health data');
    }

    return recommendations;
  },

  // Validate technology stack completeness
  validateTechnologyStack: (stack: Partial<TechnologyStackFormData>): string[] => {
    const suggestions: string[] = [];

    if (!stack.cloud_providers?.length && !stack.saas_tools?.length) {
      suggestions.push('Adding technology information helps with compliance recommendations');
    }

    if (stack.cloud_providers?.length && !stack.development_tools?.length) {
      suggestions.push('Consider adding development tools for complete technology profile');
    }

    return suggestions;
  },
};

// Error message formatting
export function formatValidationErrors(
  error: z.ZodError,
): Array<{ field: string; message: string }> {
  return error.errors.map((err) => ({
    field: err.path.join('.'),
    message: err.message,
  }));
}
