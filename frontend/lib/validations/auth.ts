// Enhanced auth validation schemas with strong password requirements
import { z } from 'zod';

// Enhanced Auth validation schemas
export const loginSchema = z.object({
  email: z.string()
    .min(1, "Email is required")
    .email("Please enter a valid email address")
    .max(254, "Email is too long"),
  password: z.string()
    .min(1, "Password is required")
    .min(8, "Password must be at least 8 characters")
    .max(128, "Password must be less than 128 characters"),
  rememberMe: z.boolean().default(false),
});

// Enhanced password validation for security
const passwordSchema = z.string()
  .min(12, "Password must be at least 12 characters for security")
  .max(128, "Password must be less than 128 characters")
  .regex(/^(?=.*[a-z])/, "Password must contain at least one lowercase letter")
  .regex(/^(?=.*[A-Z])/, "Password must contain at least one uppercase letter")
  .regex(/^(?=.*\d)/, "Password must contain at least one number")
  .regex(/^(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?])/, "Password must contain at least one special character")
  .regex(/^[^\s]*$/, "Password cannot contain spaces");

// Multi-step registration schema
export const registrationStep1Schema = z.object({
  email: z.string()
    .min(1, "Email is required")
    .email("Please enter a valid email address")
    .max(254, "Email is too long"),
  password: passwordSchema,
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

export const registrationStep2Schema = z.object({
  firstName: z.string()
    .min(1, "First name is required")
    .min(2, "First name must be at least 2 characters")
    .max(50, "First name must be less than 50 characters")
    .regex(/^[a-zA-Z\s'-]+$/, "First name can only contain letters, spaces, hyphens, and apostrophes"),
  lastName: z.string()
    .min(1, "Last name is required")
    .min(2, "Last name must be at least 2 characters")
    .max(50, "Last name must be less than 50 characters")
    .regex(/^[a-zA-Z\s'-]+$/, "Last name can only contain letters, spaces, hyphens, and apostrophes"),
  companyName: z.string()
    .min(1, "Company name is required")
    .min(2, "Company name must be at least 2 characters")
    .max(100, "Company name must be less than 100 characters"),
  companySize: z.enum(["micro", "small", "medium", "large"], {
    errorMap: () => ({ message: "Please select a company size" }),
  }),
  industry: z.string()
    .min(1, "Please select an industry"),
});

export const registrationStep3Schema = z.object({
  complianceFrameworks: z.array(z.string())
    .min(1, "Please select at least one compliance framework"),
  hasDataProtectionOfficer: z.boolean(),
  agreedToTerms: z.boolean()
    .refine((val) => val === true, {
      message: "You must agree to the Terms of Service",
    }),
  agreedToDataProcessing: z.boolean()
    .refine((val) => val === true, {
      message: "You must agree to data processing to use our service",
    }),
});

// Complete registration schema
export const registerSchema = z.object({
  // Step 1 fields
  email: z.string().email(),
  password: passwordSchema,
  confirmPassword: z.string(),
  // Step 2 fields
  firstName: z.string().min(1),
  lastName: z.string().min(1),
  companyName: z.string().min(1),
  companySize: z.enum(["micro", "small", "medium", "large"]),
  industry: z.string().min(1),
  // Step 3 fields
  complianceFrameworks: z.array(z.string()).min(1),
  hasDataProtectionOfficer: z.boolean(),
  agreedToTerms: z.boolean(),
  agreedToDataProcessing: z.boolean(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

// Password reset schemas
export const forgotPasswordSchema = z.object({
  email: z.string()
    .min(1, "Email is required")
    .email("Please enter a valid email address"),
});

export const resetPasswordSchema = z.object({
  token: z.string().min(1, "Reset token is required"),
  password: passwordSchema,
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
});

// Change password schema
export const changePasswordSchema = z.object({
  currentPassword: z.string().min(1, "Current password is required"),
  newPassword: passwordSchema,
  confirmPassword: z.string(),
}).refine((data) => data.newPassword === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
}).refine((data) => data.currentPassword !== data.newPassword, {
  message: "New password must be different from current password",
  path: ["newPassword"],
});

// Email verification schema
export const emailVerificationSchema = z.object({
  token: z.string().min(1, "Verification token is required"),
});

// Resend verification schema
export const resendVerificationSchema = z.object({
  email: z.string()
    .min(1, "Email is required")
    .email("Please enter a valid email address"),
});

// User profile validation schemas
export const userProfileSchema = z.object({
  email: z.string().email("Please enter a valid email address"),
  name: z.string()
    .min(1, "Name is required")
    .max(100, "Name must be less than 100 characters")
    .optional(),
});

// Auth type exports
export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
export type RegistrationStep1Data = z.infer<typeof registrationStep1Schema>;
export type RegistrationStep2Data = z.infer<typeof registrationStep2Schema>;
export type RegistrationStep3Data = z.infer<typeof registrationStep3Schema>;
export type RegistrationData = z.infer<typeof registerSchema>;
export type ForgotPasswordData = z.infer<typeof forgotPasswordSchema>;
export type ResetPasswordData = z.infer<typeof resetPasswordSchema>;
export type ChangePasswordData = z.infer<typeof changePasswordSchema>;
export type EmailVerificationData = z.infer<typeof emailVerificationSchema>;
export type ResendVerificationData = z.infer<typeof resendVerificationSchema>;
export type UserProfileData = z.infer<typeof userProfileSchema>;

// Password strength calculation helper
export function calculatePasswordStrength(password: string): {
  score: number;
  feedback: string[];
} {
  let score = 0;
  const feedback: string[] = [];

  // Length check
  if (password.length >= 12) {
    score += 20;
  } else if (password.length >= 8) {
    score += 10;
    feedback.push("Use at least 12 characters for better security");
  } else {
    feedback.push("Password is too short");
  }

  // Lowercase check
  if (/[a-z]/.test(password)) {
    score += 20;
  } else {
    feedback.push("Add lowercase letters");
  }

  // Uppercase check
  if (/[A-Z]/.test(password)) {
    score += 20;
  } else {
    feedback.push("Add uppercase letters");
  }

  // Number check
  if (/\d/.test(password)) {
    score += 20;
  } else {
    feedback.push("Add numbers");
  }

  // Special character check
  if (/[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)) {
    score += 20;
  } else {
    feedback.push("Add special characters");
  }

  return { score, feedback };
}

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