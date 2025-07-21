import { type Question, type QuestionValidation, type AssessmentContext } from './types';

export class ValidationError extends Error {
  public questionId: string;
  public field?: string;

  constructor(questionId: string, message: string, field?: string) {
    super(message);
    this.questionId = questionId;
    this.field = field;
    this.name = 'ValidationError';
  }
}

export class QuestionValidator {
  static validate(
    question: Question,
    value: any,
    context: AssessmentContext,
  ): ValidationError | null {
    const { validation } = question;
    if (!validation) return null;

    // Required validation
    if (validation.required && this.isEmpty(value)) {
      return new ValidationError(question.id, 'This field is required');
    }

    // Skip other validations if value is empty and not required
    if (this.isEmpty(value) && !validation.required) {
      return null;
    }

    // Type-specific validations
    switch (question.type) {
      case 'text':
      case 'textarea':
        return this.validateText(question, value, validation);

      case 'number':
        return this.validateNumber(question, value, validation);

      case 'checkbox':
        return this.validateCheckbox(question, value, validation);

      case 'date':
        return this.validateDate(question, value, validation);

      case 'file_upload':
        return this.validateFile(question, value, validation);

      default:
        break;
    }

    // Custom validation
    if (validation.custom) {
      const customError = validation.custom(value, context);
      if (customError) {
        return new ValidationError(question.id, customError);
      }
    }

    return null;
  }

  private static isEmpty(value: any): boolean {
    if (value === null || value === undefined) return true;
    if (typeof value === 'string') return value.trim() === '';
    if (Array.isArray(value)) return value.length === 0;
    if (value instanceof File) return !value.name;
    return false;
  }

  private static validateText(
    question: Question,
    value: string,
    validation: QuestionValidation,
  ): ValidationError | null {
    const textValue = String(value);

    if (validation.minLength && textValue.length < validation.minLength) {
      return new ValidationError(
        question.id,
        `Minimum ${validation.minLength} characters required`,
      );
    }

    if (validation.maxLength && textValue.length > validation.maxLength) {
      return new ValidationError(question.id, `Maximum ${validation.maxLength} characters allowed`);
    }

    if (validation.pattern) {
      const regex = new RegExp(validation.pattern);
      if (!regex.test(textValue)) {
        return new ValidationError(question.id, 'Invalid format');
      }
    }

    return null;
  }

  private static validateNumber(
    question: Question,
    value: any,
    validation: QuestionValidation,
  ): ValidationError | null {
    const numValue = Number(value);

    if (isNaN(numValue)) {
      return new ValidationError(question.id, 'Must be a valid number');
    }

    if (validation.min !== undefined && numValue < validation.min) {
      return new ValidationError(question.id, `Minimum value is ${validation.min}`);
    }

    if (validation.max !== undefined && numValue > validation.max) {
      return new ValidationError(question.id, `Maximum value is ${validation.max}`);
    }

    return null;
  }

  private static validateCheckbox(
    question: Question,
    value: any[],
    validation: QuestionValidation,
  ): ValidationError | null {
    if (!Array.isArray(value)) {
      return new ValidationError(question.id, 'Invalid selection');
    }

    if (validation.min !== undefined && value.length < validation.min) {
      return new ValidationError(
        question.id,
        `Select at least ${validation.min} option${validation.min > 1 ? 's' : ''}`,
      );
    }

    if (validation.max !== undefined && value.length > validation.max) {
      return new ValidationError(
        question.id,
        `Select at most ${validation.max} option${validation.max > 1 ? 's' : ''}`,
      );
    }

    return null;
  }

  private static validateDate(
    question: Question,
    value: any,
    _validation: QuestionValidation,
  ): ValidationError | null {
    const dateValue = new Date(value);

    if (isNaN(dateValue.getTime())) {
      return new ValidationError(question.id, 'Invalid date');
    }

    // Additional date validations can be added here
    // e.g., min/max dates, date ranges, etc.

    return null;
  }

  private static validateFile(
    question: Question,
    value: File | File[],
    validation: QuestionValidation,
  ): ValidationError | null {
    const files = Array.isArray(value) ? value : [value];

    // Check file count
    if (validation.min !== undefined && files.length < validation.min) {
      return new ValidationError(
        question.id,
        `Upload at least ${validation.min} file${validation.min > 1 ? 's' : ''}`,
      );
    }

    if (validation.max !== undefined && files.length > validation.max) {
      return new ValidationError(
        question.id,
        `Upload at most ${validation.max} file${validation.max > 1 ? 's' : ''}`,
      );
    }

    // Check file sizes (if maxLength is used for max file size in bytes)
    if (validation.maxLength) {
      for (const file of files) {
        if (file.size > validation.maxLength) {
          const maxSizeMB = Math.round(validation.maxLength / 1024 / 1024);
          return new ValidationError(question.id, `File size must not exceed ${maxSizeMB}MB`);
        }
      }
    }

    // Check file types (if pattern is used for allowed extensions)
    if (validation.pattern) {
      const allowedExtensions = validation.pattern.split('|');
      for (const file of files) {
        const extension = file.name.split('.').pop()?.toLowerCase();
        if (!extension || !allowedExtensions.includes(extension)) {
          return new ValidationError(
            question.id,
            `Allowed file types: ${allowedExtensions.join(', ')}`,
          );
        }
      }
    }

    return null;
  }
}

// Common validation patterns
export const ValidationPatterns = {
  email: '^[\\w-\\.]+@([\\w-]+\\.)+[\\w-]{2,4}$',
  url: '^https?:\\/\\/(www\\.)?[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}\\b([-a-zA-Z0-9()@:%_\\+.~#?&//=]*)$',
  phone: '^[\\+]?[(]?[0-9]{3}[)]?[-\\s\\.]?[0-9]{3}[-\\s\\.]?[0-9]{4,6}$',
  ukPostcode: '^[A-Z]{1,2}[0-9][0-9A-Z]?\\s?[0-9][A-Z]{2}$',
  alphanumeric: '^[a-zA-Z0-9]+$',
  lettersOnly: '^[a-zA-Z\\s]+$',
  numbersOnly: '^[0-9]+$',
  noSpecialChars: '^[a-zA-Z0-9\\s]+$',
};

// Common validation rules
export const CommonValidations = {
  required: { required: true },
  email: {
    required: true,
    pattern: ValidationPatterns.email,
  },
  url: {
    required: true,
    pattern: ValidationPatterns.url,
  },
  phone: {
    required: true,
    pattern: ValidationPatterns.phone,
  },
  companyName: {
    required: true,
    minLength: 2,
    maxLength: 100,
    pattern: ValidationPatterns.noSpecialChars,
  },
  description: {
    required: false,
    maxLength: 500,
  },
  shortText: {
    required: true,
    minLength: 1,
    maxLength: 50,
  },
  longText: {
    required: false,
    maxLength: 2000,
  },
  percentage: {
    required: true,
    min: 0,
    max: 100,
  },
  positiveNumber: {
    required: true,
    min: 0,
  },
  year: {
    required: true,
    min: 1900,
    max: new Date().getFullYear() + 10,
  },
};
