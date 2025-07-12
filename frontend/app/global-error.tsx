'use client';

import * as Sentry from '@sentry/nextjs';
import { useEffect } from 'react';
import { AlertCircle, RefreshCw, Home } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

/**
 * Global error handler for Next.js App Router
 * This catches errors that occur during React rendering
 */
export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to Sentry
    Sentry.captureException(error, {
      tags: {
        component: 'GlobalError',
        boundary: 'global-error',
      },
      extra: {
        digest: error.digest,
      },
    });
  }, [error]);

  const handleGoHome = () => {
    window.location.href = '/';
  };

  const handleReportFeedback = () => {
    Sentry.showReportDialog();
  };

  return (
    <html>
      <body>
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
          <Card className="w-full max-w-md">
            <CardHeader className="text-center">
              <div className="flex justify-center mb-4">
                <AlertCircle className="h-12 w-12 text-red-500" />
              </div>
              <CardTitle className="text-xl font-semibold text-gray-900">
                Application Error
              </CardTitle>
              <CardDescription className="text-gray-600">
                A critical error occurred. Our team has been automatically notified and will investigate.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {process.env.NODE_ENV === 'development' && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-md">
                  <p className="text-sm font-medium text-red-800 mb-2">Error Details:</p>
                  <p className="text-xs text-red-700 font-mono">
                    {error.message}
                  </p>
                  {error.digest && (
                    <p className="text-xs text-red-600 mt-1">
                      Digest: {error.digest}
                    </p>
                  )}
                </div>
              )}
              
              <div className="flex flex-col gap-2">
                <Button 
                  onClick={reset}
                  className="w-full"
                  variant="default"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Try Again
                </Button>
                
                <Button 
                  onClick={handleGoHome}
                  className="w-full"
                  variant="outline"
                >
                  <Home className="h-4 w-4 mr-2" />
                  Go to Homepage
                </Button>
                
                <Button 
                  onClick={handleReportFeedback}
                  className="w-full"
                  variant="ghost"
                  size="sm"
                >
                  Report Feedback
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </body>
    </html>
  );
}