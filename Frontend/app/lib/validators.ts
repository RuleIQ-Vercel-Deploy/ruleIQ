import { z } from "zod"

export const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(1, "Password is required"),
})

export const registerSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string()
    .min(8, "Password must be at least 8 characters")
    .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
    .regex(/[a-z]/, "Password must contain at least one lowercase letter")
    .regex(/[0-9]/, "Password must contain at least one number")
    .regex(/[!@#$%^&*()\-+?_=,<>/]/, "Password must contain at least one special character"),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
})

export const passwordResetSchema = z.object({
  email: z.string().email("Invalid email address"),
})

// Business Profile validation schemas
export const businessProfileSchema = z.object({
  company_name: z.string().min(2, "Company name must be at least 2 characters").max(100, "Company name must be less than 100 characters"),
  industry: z.string().min(1, "Please select an industry"),
  employee_count: z.number().min(1, "Employee count must be at least 1").max(1000000, "Employee count seems too high"),
  annual_revenue: z.string().optional(),
  country: z.string().default("United Kingdom"),
  data_sensitivity: z.enum(["Low", "Moderate", "High", "Confidential"]).default("Low"),
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
  compliance_budget: z.number().min(0, "Budget must be positive").optional(),
  compliance_timeline: z.string().optional(),
})

export const businessProfileUpdateSchema = businessProfileSchema.partial()

export type LoginInput = z.infer<typeof loginSchema>
export type RegisterInput = z.infer<typeof registerSchema>
export type PasswordResetInput = z.infer<typeof passwordResetSchema>
export type BusinessProfileInput = z.infer<typeof businessProfileSchema>
export type BusinessProfileUpdateInput = z.infer<typeof businessProfileUpdateSchema>