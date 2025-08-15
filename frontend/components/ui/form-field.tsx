'use client';

import { AlertCircle, CheckCircle2 } from 'lucide-react';
import * as React from 'react';

import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';

interface FormFieldProps {
  children: React.ReactNode;
  label?: string;
  error?: string;
  success?: string;
  description?: string;
  required?: boolean;
  className?: string;
}

export function FormField({
  children,
  label,
  error,
  success,
  description,
  required,
  className,
}: FormFieldProps) {
  const fieldId = React.useId();
  const hasError = Boolean(error);
  const hasSuccess = Boolean(success);

  return (
    <div className={cn('space-y-2', className)}>
      {label && (
        <Label
          htmlFor={fieldId}
          variant={hasError ? 'error' : hasSuccess ? 'success' : 'default'}
          className="flex items-center gap-1"
        >
          {label}
          {required && <span className="text-error">*</span>}
        </Label>
      )}

      <div className="relative">
        {React.cloneElement(children as React.ReactElement, {
          id: fieldId,
          'aria-describedby': error ? `${fieldId}-error` : success ? `${fieldId}-success` : description ? `${fieldId}-description` : undefined,
          'aria-invalid': hasError,
        } as any)}
      </div>

      {description && !error && !success && (
        <p className="text-xs text-muted-foreground" id={`${fieldId}-description`}>
          {description}
        </p>
      )}

      {error && (
        <div className="flex items-center gap-2 text-error">
          <AlertCircle className="h-4 w-4" />
          <p className="text-xs font-medium" id={`${fieldId}-error`}>
            {error}
          </p>
        </div>
      )}

      {success && (
        <div className="flex items-center gap-2 text-success">
          <CheckCircle2 className="h-4 w-4" />
          <p className="text-xs font-medium" id={`${fieldId}-success`}>
            {success}
          </p>
        </div>
      )}
    </div>
  );
}
