"use client";

import { AlertTriangle, RefreshCw, Bot } from "lucide-react";
import React from "react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

interface AIErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

interface AIErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<{
    error: Error;
    resetError: () => void;
    errorInfo?: React.ErrorInfo;
  }>;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

class AIErrorBoundaryClass extends React.Component<
  AIErrorBoundaryProps,
  AIErrorBoundaryState
> {
  constructor(props: AIErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error: Error): Partial<AIErrorBoundaryState> {
    return { hasError: true, error };
  }

  override componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("AI Error Boundary caught error:", error, errorInfo);
    
    this.setState({ errorInfo });
    
    // Call custom error handler if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // In production, send to error monitoring service
    if (process.env.NODE_ENV === "production") {
      // TODO: Send to Sentry or similar service
      // Sentry.captureException(error, { contexts: { react: { componentStack: errorInfo.componentStack } } });
    }
  }

  resetError = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  override render() {
    if (this.state.hasError && this.state.error) {
      const FallbackComponent = this.props.fallback || DefaultAIErrorFallback;
      const props = {
        error: this.state.error,
        resetError: this.resetError,
        ...(this.state.errorInfo && { errorInfo: this.state.errorInfo })
      };
      
      return <FallbackComponent {...props} />;
    }

    return this.props.children;
  }
}

// Default fallback component for AI errors
function DefaultAIErrorFallback({
  error,
  resetError,
}: {
  error: Error;
  resetError: () => void;
  errorInfo?: React.ErrorInfo;
}) {
  const isAIServiceError = error.message.includes("AI") || 
                          error.message.includes("timeout") ||
                          error.message.includes("Unable to get AI assistance");

  return (
    <Card className="border-amber-200 bg-amber-50 dark:border-amber-800 dark:bg-amber-950">
      <CardContent className="p-4">
        <Alert variant="default" className="border-0 bg-transparent p-0">
          <div className="flex items-start gap-3">
            <div className="p-2 bg-amber-100 dark:bg-amber-900 rounded-lg">
              <Bot className="h-4 w-4 text-amber-600 dark:text-amber-400" />
            </div>
            <div className="flex-1 space-y-2">
              <AlertTitle className="text-amber-800 dark:text-amber-200 text-sm font-medium">
                {isAIServiceError ? "AI Service Temporarily Unavailable" : "AI Feature Error"}
              </AlertTitle>
              <AlertDescription className="text-amber-700 dark:text-amber-300 text-xs">
                {isAIServiceError ? (
                  <>
                    AI assistance is temporarily unavailable. You can continue the assessment manually.
                    The core functionality remains fully operational.
                  </>
                ) : (
                  <>
                    An error occurred with the AI feature. Please try again or continue without AI assistance.
                  </>
                )}
              </AlertDescription>
              <div className="flex gap-2 pt-1">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={resetError}
                  className="h-7 text-xs border-amber-300 text-amber-700 hover:bg-amber-100 dark:border-amber-700 dark:text-amber-300 dark:hover:bg-amber-900"
                >
                  <RefreshCw className="h-3 w-3 mr-1" />
                  Retry AI Service
                </Button>
              </div>
            </div>
          </div>
        </Alert>
      </CardContent>
    </Card>
  );
}

// Lightweight error boundary for inline AI features
export function InlineAIErrorBoundary({ 
  children 
}: { 
  children: React.ReactNode 
}) {
  return (
    <AIErrorBoundaryClass
      fallback={({ resetError }) => (
        <div className="flex items-center gap-2 p-2 bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 rounded text-xs">
          <AlertTriangle className="h-3 w-3 text-amber-600 dark:text-amber-400" />
          <span className="text-amber-700 dark:text-amber-300">AI unavailable</span>
          <Button
            variant="ghost"
            size="sm"
            onClick={resetError}
            className="h-5 px-1 text-xs text-amber-600 hover:text-amber-700 dark:text-amber-400 dark:hover:text-amber-300"
          >
            Retry
          </Button>
        </div>
      )}
    >
      {children}
    </AIErrorBoundaryClass>
  );
}

// Main AI error boundary export
export function AIErrorBoundary({
  children,
  onError,
  fallback
}: {
  children: React.ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  fallback?: React.ComponentType<{
    error: Error;
    resetError: () => void;
    errorInfo?: React.ErrorInfo;
  }>;
}) {
  const props: AIErrorBoundaryProps = {
    children,
    ...(onError && { onError }),
    ...(fallback && { fallback })
  };
  
  return <AIErrorBoundaryClass {...props} />;
}

// Hook for programmatic error handling in AI components
export function useAIErrorHandler() {
  const [error, setError] = React.useState<Error | null>(null);

  React.useEffect(() => {
    if (error) {
      throw error;
    }
  }, [error]);

  const resetError = React.useCallback(() => {
    setError(null);
  }, []);

  const captureError = React.useCallback((error: Error) => {
    console.error("AI Error captured:", error);
    setError(error);
  }, []);

  return { captureError, resetError };
}
