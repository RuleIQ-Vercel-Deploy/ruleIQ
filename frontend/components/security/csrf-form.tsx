'use client';

import { ReactNode, FormEvent } from 'react';
import { useCsrfToken, getCsrfHeaders } from '@/lib/hooks/use-csrf-token';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';

interface CsrfFormProps {
  children: ReactNode;
  onSubmit: (formData: FormData, csrfToken: string) => Promise<void> | void;
  action?: string;
  method?: 'POST' | 'PUT' | 'DELETE' | 'PATCH';
  className?: string;
  submitText?: string;
  loadingText?: string;
  disabled?: boolean;
}

/**
 * Form component with built-in CSRF protection
 */
export function CsrfForm({
  children,
  onSubmit,
  action,
  method = 'POST',
  className,
  submitText = 'Submit',
  loadingText = 'Submitting...',
  disabled = false,
}: CsrfFormProps) {
  const { token, loading: tokenLoading, error: tokenError } = useCsrfToken();

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    
    if (!token) {
      console.error('CSRF token not available');
      return;
    }

    const formData = new FormData(event.currentTarget);
    formData.append('_csrf', token);

    try {
      await onSubmit(formData, token);
    } catch (error) {
      console.error('Form submission error:', error);
    }
  };

  if (tokenLoading) {
    return (
      <div className="flex items-center justify-center p-4">
        <Loader2 className="h-6 w-6 animate-spin" />
        <span className="ml-2">Loading security token...</span>
      </div>
    );
  }

  if (tokenError) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-md">
        <p className="text-red-800">
          Security error: {tokenError}
        </p>
        <p className="text-sm text-red-600 mt-1">
          Please refresh the page and try again.
        </p>
      </div>
    );
  }

  return (
    <form 
      onSubmit={handleSubmit}
      action={action}
      method={method}
      className={className}
    >
      {/* Hidden CSRF token field for fallback */}
      <input type="hidden" name="_csrf" value={token || ''} />
      
      {children}
    </form>
  );
}

/**
 * CSRF-protected submit button component
 */
interface CsrfSubmitButtonProps {
  loading?: boolean;
  disabled?: boolean;
  children: ReactNode;
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  className?: string;
}

export function CsrfSubmitButton({
  loading = false,
  disabled = false,
  children,
  variant = 'default',
  size = 'default',
  className,
}: CsrfSubmitButtonProps) {
  return (
    <Button
      type="submit"
      disabled={disabled || loading}
      variant={variant}
      size={size}
      className={className}
    >
      {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      {children}
    </Button>
  );
}