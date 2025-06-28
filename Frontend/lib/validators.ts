// Validation schemas for NexCompli forms
import { z } from 'zod';

// Auth validation schemas
export const loginSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  password: z.string().min(8, "Password must be at least 8 characters").max(128, "Password must be less than 128 characters"),
});

export const registerSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  password: z.string()
    .min(8, "Password must be at least 8 characters")
    .max(128, "Password must be less than 128 characters")
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, "Password must contain at least one uppercase letter, one lowercase letter, and one number"),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

// Business profile validation schemas
export const businessProfileSchema = z.object({
  company_name: z.string()
    .min(2, "Company name must be at least 2 characters")
    .max(100, "Company name must be less than 100 characters"),
  industry: z.string().min(1, "Please select an industry"),
  employee_count: z.number()
    .min(1, "Employee count must be at least 1")
    .max(1000000, "Employee count cannot exceed 1,000,000"),
  annual_revenue: z.string().min(1, "Please select annual revenue range"),
  country: z.string().default("United Kingdom"),
  data_sensitivity: z.enum(["Low", "Moderate", "High", "Confidential"], {
    errorMap: () => ({ message: "Please select data sensitivity level" }),
  }),
  
  // Boolean fields
  handles_personal_data: z.boolean().default(false),
  processes_payments: z.boolean().default(false),
  stores_health_data: z.boolean().default(false),
  provides_financial_services: z.boolean().default(false),
  operates_critical_infrastructure: z.boolean().default(false),
  has_international_operations: z.boolean().default(false),
  
  // Multi-select arrays
  existing_frameworks: z.array(z.string()).default([]),
  planned_frameworks: z.array(z.string()).default([]),
  cloud_providers: z.array(z.string()).default([]),
  saas_tools: z.array(z.string()).default([]),
  development_tools: z.array(z.string()).default([]),
  
  // Optional fields
  compliance_budget: z.string().optional(),
  compliance_timeline: z.string().optional(),
});

// Evidence validation schemas
export const evidenceSchema = z.object({
  title: z.string()
    .min(1, "Title is required")
    .max(255, "Title must be less than 255 characters"),
  description: z.string()
    .max(2000, "Description must be less than 2000 characters")
    .optional(),
  control_id: z.string().min(1, "Control ID is required"),
  framework: z.string().min(1, "Framework is required"),
  business_profile_id: z.string().min(1, "Business profile is required"),
  evidence_type: z.string().min(1, "Evidence type is required"),
  source: z.string().optional(),
  tags: z.array(z.string()).default([]),
});

// Assessment validation schemas
export const assessmentResponseSchema = z.object({
  question_id: z.string(),
  response_type: z.enum(["multiple_choice", "text", "boolean"]),
  response_value: z.union([z.string(), z.boolean(), z.array(z.string())]),
});

export const assessmentSessionSchema = z.object({
  business_profile_id: z.string().min(1, "Business profile is required"),
  framework_id: z.string().optional(),
  responses: z.array(assessmentResponseSchema).default([]),
});

// Policy generation validation schemas
export const policyGenerationSchema = z.object({
  framework: z.string().min(1, "Framework is required"),
  business_profile_id: z.string().min(1, "Business profile is required"),
  policy_title: z.string()
    .min(1, "Policy title is required")
    .max(255, "Policy title must be less than 255 characters"),
  tone: z.enum(["formal", "informal", "strict"], {
    errorMap: () => ({ message: "Please select a tone" }),
  }),
  specific_controls: z.array(z.string()).default([]),
});

// Implementation plan validation schemas
export const implementationPlanSchema = z.object({
  business_profile_id: z.string().min(1, "Business profile is required"),
  framework_id: z.string().min(1, "Framework is required"),
  title: z.string()
    .min(1, "Title is required")
    .max(255, "Title must be less than 255 characters"),
  start_date: z.string().min(1, "Start date is required"),
  end_date: z.string().min(1, "End date is required"),
});

// Report generation validation schemas
export const reportGenerationSchema = z.object({
  business_profile_id: z.string().min(1, "Business profile is required"),
  report_type: z.enum([
    "executive_summary",
    "gap_analysis", 
    "evidence_report",
    "audit_readiness",
    "compliance_status",
    "control_matrix",
    "risk_assessment"
  ], {
    errorMap: () => ({ message: "Please select a report type" }),
  }),
  format: z.enum(["pdf", "json", "html", "csv"], {
    errorMap: () => ({ message: "Please select a format" }),
  }),
  start_date: z.string().optional(),
  end_date: z.string().optional(),
  frameworks: z.array(z.string()).default([]),
  include_evidence: z.boolean().default(true),
});

// Chat validation schemas
export const chatMessageSchema = z.object({
  message: z.string()
    .min(1, "Message cannot be empty")
    .max(2000, "Message must be less than 2000 characters"),
});

// Search validation schemas
export const searchSchema = z.object({
  query: z.string().min(1, "Search query is required"),
  filters: z.object({
    framework: z.string().optional(),
    evidence_type: z.string().optional(),
    status: z.string().optional(),
  }).optional(),
});

// User profile validation schemas
export const userProfileSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  name: z.string()
    .min(1, "Name is required")
    .max(100, "Name must be less than 100 characters")
    .optional(),
});

// Password change validation schema
export const passwordChangeSchema = z.object({
  current_password: z.string().min(1, "Current password is required"),
  new_password: z.string()
    .min(8, "Password must be at least 8 characters")
    .max(128, "Password must be less than 128 characters")
    .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/, "Password must contain at least one uppercase letter, one lowercase letter, and one number"),
  confirm_password: z.string(),
}).refine((data) => data.new_password === data.confirm_password, {
  message: "Passwords don't match",
  path: ["confirm_password"],
});

// Integration validation schemas
export const integrationConfigSchema = z.object({
  provider: z.enum(["google_workspace", "microsoft_365"], {
    errorMap: () => ({ message: "Please select a provider" }),
  }),
  credentials: z.record(z.string()),
  settings: z.record(z.any()).optional(),
});

// Export type inference helpers
export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
export type BusinessProfileFormData = z.infer<typeof businessProfileSchema>;
export type EvidenceFormData = z.infer<typeof evidenceSchema>;
export type AssessmentResponseData = z.infer<typeof assessmentResponseSchema>;
export type AssessmentSessionData = z.infer<typeof assessmentSessionSchema>;
export type PolicyGenerationData = z.infer<typeof policyGenerationSchema>;
export type ImplementationPlanData = z.infer<typeof implementationPlanSchema>;
export type ReportGenerationData = z.infer<typeof reportGenerationSchema>;
export type ChatMessageData = z.infer<typeof chatMessageSchema>;
export type SearchData = z.infer<typeof searchSchema>;
export type UserProfileData = z.infer<typeof userProfileSchema>;
export type PasswordChangeData = z.infer<typeof passwordChangeSchema>;
export type IntegrationConfigData = z.infer<typeof integrationConfigSchema>;

// Validation helper function
export function validateForm<T>(schema: z.ZodSchema<T>, data: unknown): { success: true; data: T } | { success: false; errors: Record<string, string> } {
  try {
    const validatedData = schema.parse(data);
    return { success: true, data: validatedData };
  } catch (error) {
    if (error instanceof z.ZodError) {
      const errors: Record<string, string> = {};
      error.errors.forEach((err) => {
        if (err.path.length > 0) {
          errors[err.path.join('.')] = err.message;
        }
      });
      return { success: false, errors };
    }
    throw error;
  }
}