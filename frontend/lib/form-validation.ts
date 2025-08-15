'use client';

import React from 'react';

// Form validation utilities for the ruleIQ platform
export interface ValidationRule {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: RegExp;
  custom?: (value: any) => string | null;
}

export interface ValidationResult {
  isValid: boolean;
  error?: string;
  success?: string;
}

export function validateField(value: any, rules: ValidationRule): ValidationResult {
  // Required validation
  if (rules.required && (!value || (typeof value === 'string' && value.trim() === ''))) {
    return { isValid: false, error: 'This field is required' };
  }

  // Skip other validations if field is empty and not required
  if (!value || (typeof value === 'string' && value.trim() === '')) {
    return { isValid: true };
  }

  // String-specific validations
  if (typeof value === 'string') {
    // Min length validation
    if (rules.minLength && value.length < rules.minLength) {
      return {
        isValid: false,
        error: `Must be at least ${rules.minLength} characters long`,
      };
    }

    // Max length validation
    if (rules.maxLength && value.length > rules.maxLength) {
      return {
        isValid: false,
        error: `Must be no more than ${rules.maxLength} characters long`,
      };
    }

    // Pattern validation
    if (rules.pattern && !rules.pattern.test(value)) {
      return { isValid: false, error: 'Invalid format' };
    }
  }

  // Custom validation
  if (rules.custom) {
    const customError = rules.custom(value);
    if (customError) {
      return { isValid: false, error: customError };
    }
  }

  return { isValid: true, success: 'Valid input' };
}

// Common validation patterns
export const ValidationPatterns = {
  email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  phone: /^\+?[\d\s\-$$$$]+$/,
  url: /^https?:\/\/.+/,
  strongPassword: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
  alphanumeric: /^[a-zA-Z0-9]+$/,
  numbersOnly: /^\d+$/,
} as const;

// Pre-defined validation rules for common fields
export const CommonValidationRules = {
  email: {
    required: true,
    pattern: ValidationPatterns.email,
    custom: (value: string) => {
      if (value && !ValidationPatterns.email.test(value)) {
        return 'Please enter a valid email address';
      }
      return null;
    },
  },
  password: {
    required: true,
    minLength: 8,
    custom: (value: string) => {
      if (value && value.length >= 8) {
        if (!ValidationPatterns.strongPassword.test(value)) {
          return 'Password must contain uppercase, lowercase, number, and special character';
        }
      }
      return null;
    },
  },
  companyName: {
    required: true,
    minLength: 2,
    maxLength: 100,
  },
  phone: {
    pattern: ValidationPatterns.phone,
    custom: (value: string) => {
      if (value && !ValidationPatterns.phone.test(value)) {
        return 'Please enter a valid phone number';
      }
      return null;
    },
  },
} as const;

// Form validation hook
export function useFormValidation<T extends Record<string, any>>(
  initialValues: T,
  validationRules: Partial<Record<keyof T, ValidationRule>>,
) {
  const [values, setValues] = React.useState<T>(initialValues);
  const [errors, setErrors] = React.useState<Partial<Record<keyof T, string>>>({});
  const [touched, setTouched] = React.useState<Partial<Record<keyof T, boolean>>>({});

  const validateField = (name: keyof T, value: any): { isValid: boolean; error?: string } => {
    const rules = validationRules[name];
    if (!rules) return { isValid: true };

    const result = validateField(value, rules);

    setErrors((prev) => ({
      ...prev,
      [name]: result.error,
    }));

    return result;
  };

  const handleChange = (name: keyof T, value: any) => {
    setValues((prev) => ({ ...prev, [name]: value }));

    // Only validate if field has been touched
    if (touched[name]) {
      validateField(name, value);
    }
  };

  const handleBlur = (name: keyof T) => {
    setTouched((prev) => ({ ...prev, [name]: true }));
    validateField(name, values[name]);
  };

  const validateAll = () => {
    const newErrors: Partial<Record<keyof T, string>> = {};
    let isValid = true;

    Object.keys(validationRules).forEach((key) => {
      const result = validateField(key as keyof T, values[key as keyof T]);
      if (!result.isValid) {
        newErrors[key as keyof T] = result.error;
        isValid = false;
      }
    });

    setErrors(newErrors);
    setTouched(
      Object.keys(validationRules).reduce(
        (acc, key) => ({
          ...acc,
          [key]: true,
        }),
        {},
      ),
    );

    return isValid;
  };

  return {
    values,
    errors,
    touched,
    handleChange,
    handleBlur,
    validateAll,
    isValid: Object.keys(errors).length === 0,
  };
}
