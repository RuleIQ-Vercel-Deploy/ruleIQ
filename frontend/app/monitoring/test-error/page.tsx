'use client';

import { useState } from 'react';
import * as Sentry from '@sentry/nextjs';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { AlertTriangle, Bug, Settings } from 'lucide-react';

/**
 * Test page for Sentry error tracking
 * Only available in development mode
 */
export default function TestErrorPage() {
  const [shouldError, setShouldError] = useState(false);

  // This will cause a React render error
  if (shouldError) {
    throw new Error('Test error for Sentry integration - triggered from TestErrorPage');
  }

  const triggerJSError = () => {
    throw new Error('Manual JavaScript error for Sentry testing');
  };

  const triggerAsyncError = async () => {
    try {
      // Simulate an async operation that fails
      await new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Async operation failed')), 100);
      });
    } catch (error) {
      Sentry.captureException(error, {
        tags: {
          test: true,
          type: 'async-error',
        },
        extra: {
          timestamp: new Date().toISOString(),
          userAction: 'test-async-error',
        },
      });
      throw error;
    }
  };

  const triggerCustomEvent = () => {
    Sentry.captureMessage('Custom test event from error test page', 'info');
    alert('Custom event sent to Sentry (check your dashboard)');
  };

  const triggerUserFeedback = () => {
    Sentry.showReportDialog({
      eventId: Sentry.captureMessage('User feedback test', 'info'),
    });
  };

  // Only show this page in development
  if (process.env.NODE_ENV === 'production') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>Not Available</CardTitle>
            <CardDescription>
              Error testing is only available in development mode.
            </CardDescription>
          </CardHeader>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2 mb-2">
              <Bug className="h-6 w-6 text-orange-500" />
              <CardTitle>Sentry Error Testing</CardTitle>
            </div>
            <CardDescription>
              Test different types of errors to verify Sentry integration is working correctly.
              Check your Sentry dashboard after triggering errors.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-3">
              <Button 
                onClick={() => setShouldError(true)}
                variant="destructive"
                className="w-full justify-start"
              >
                <AlertTriangle className="h-4 w-4 mr-2" />
                Trigger React Render Error
              </Button>

              <Button 
                onClick={triggerJSError}
                variant="destructive"
                className="w-full justify-start"
              >
                <AlertTriangle className="h-4 w-4 mr-2" />
                Trigger JavaScript Error
              </Button>

              <Button 
                onClick={triggerAsyncError}
                variant="destructive"
                className="w-full justify-start"
              >
                <AlertTriangle className="h-4 w-4 mr-2" />
                Trigger Async Error
              </Button>

              <Button 
                onClick={triggerCustomEvent}
                variant="outline"
                className="w-full justify-start"
              >
                <Settings className="h-4 w-4 mr-2" />
                Send Custom Event
              </Button>

              <Button 
                onClick={triggerUserFeedback}
                variant="outline"
                className="w-full justify-start"
              >
                <Settings className="h-4 w-4 mr-2" />
                Test User Feedback Dialog
              </Button>
            </div>

            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-md">
              <h3 className="text-sm font-medium text-blue-800 mb-2">
                Testing Instructions:
              </h3>
              <ul className="text-xs text-blue-700 space-y-1">
                <li>• Click buttons to trigger different error types</li>
                <li>• Check browser console for local error logs</li>
                <li>• Verify errors appear in your Sentry dashboard</li>
                <li>• Test user feedback functionality</li>
                <li>• Ensure source maps provide readable stack traces</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}