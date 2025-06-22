import { z } from "zod"

export const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
})

export const registerSchema = z
  .object({
    email: z.string().email("Invalid email address"),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .max(128, "Password must be less than 128 characters")
      .regex(
        /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
        "Password must contain at least one lowercase letter, one uppercase letter, and one number",
      ),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ["confirmPassword"],
  })

export const businessProfileSchema = z.object({
  company_name: z
    .string()
    .min(2, "Company name must be at least 2 characters")
    .max(100, "Company name must be less than 100 characters")
    .regex(/^[a-zA-Z0-9\s\-&.,()]+$/, "Company name contains invalid characters"),

  industry: z
    .string()
    .min(2, "Industry must be at least 2 characters")
    .max(50, "Industry must be less than 50 characters"),

  employee_count: z
    .number()
    .min(1, "Employee count must be at least 1")
    .max(1000000, "Employee count seems unrealistic")
    .int("Employee count must be a whole number"),

  annual_revenue: z.string().optional(),

  country: z.string().default("United Kingdom"),

  data_sensitivity: z.enum(["Low", "Moderate", "High", "Confidential"]),

  handles_personal_data: z.boolean().default(false),
  processes_payments: z.boolean().default(false),
  stores_health_data: z.boolean().default(false),
  provides_financial_services: z.boolean().default(false),
  operates_critical_infrastructure: z.boolean().default(false),
  has_international_operations: z.boolean().default(false),

  existing_frameworks: z.array(z.string()).default([]),
  planned_frameworks: z.array(z.string()).default([]),
  cloud_providers: z.array(z.string()).default([]),
  saas_tools: z.array(z.string()).default([]),
  development_tools: z.array(z.string()).default([]),

  compliance_budget: z
    .number()
    .min(0, "Compliance budget cannot be negative")
    .max(100000000, "Compliance budget seems unrealistic"),

  compliance_timeline: z.string().max(100, "Compliance timeline must be less than 100 characters").optional(),
})

export const evidenceSchema = z.object({
  title: z.string().min(1, "Title is required").max(255),
  description: z.string().max(2000),
  control_id: z.string().min(1, "Control ID is required"),
  framework: z.string().min(1, "Framework is required"),
  business_profile_id: z.string().min(1, "Business profile is required"),
  evidence_type: z.string(),
  source: z.string(),
  tags: z.array(z.string()),
})

export type LoginInput = z.infer<typeof loginSchema>
export type RegisterInput = z.infer<typeof registerSchema>
export type BusinessProfileInput = z.infer<typeof businessProfileSchema>
export type EvidenceInput = z.infer<typeof evidenceSchema>
