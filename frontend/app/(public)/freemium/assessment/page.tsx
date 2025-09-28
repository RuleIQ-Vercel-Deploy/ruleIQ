'use client';

import { Suspense, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import {
  FreemiumAssessmentFlow,
  FreemiumAssessmentProgress,
} from '../../../../components/freemium/freemium-assessment-flow';
import { Card, CardContent } from '../../../../components/ui/card';
import { Button } from '../../../../components/ui/button';
import { useFreemiumStore, useFreemiumSession } from '../../../../lib/stores/freemium-store';
import { AlertTriangle, Loader2, ArrowLeft } from 'lucide-react';

function AssessmentContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { loadSession } = useFreemiumStore();
  const { hasSession, sessionData } = useFreemiumSession();

  const tokenFromUrl = searchParams?.get('token');
  const errorFromUrl = searchParams?.get('error');

  // Load session from URL if provided and not already in store
  useEffect(() => {
    if (tokenFromUrl && tokenFromUrl !== sessionData.sessionToken) {
      loadSession(tokenFromUrl).catch(console.error);
    }
  }, [tokenFromUrl, sessionData.sessionToken, loadSession]);

  // Handle error states
  if (errorFromUrl === 'session_expired') {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50 p-4">
        <Card className="w-full max-w-md">
          <CardContent className="space-y-4 py-8 text-center">
            <AlertTriangle className="mx-auto h-12 w-12 text-orange-500" />
            <div className="space-y-2">
              <h2 className="text-xl font-semibold text-gray-900">Session Expired</h2>
              <p className="text-gray-600">
                Your assessment session has expired. Please start a new assessment.
              </p>
            </div>
            <Button
              onClick={() => router.push('/freemium')}
              className="bg-purple-600 hover:bg-purple-700"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Start New Assessment
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Redirect to landing page if no session
  if (!hasSession && !tokenFromUrl) {
    router.push('/freemium');
    return (
      <div className="flex min-h-screen items-center justify-center bg-gray-50">
        <Loader2 className="h-8 w-8 animate-spin text-purple-600" />
      </div>
    );
  }

  const currentToken = tokenFromUrl || sessionData.sessionToken;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="border-b border-gray-200 bg-white">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                onClick={() => router.push('/freemium')}
                variant="ghost"
                size="sm"
                className="text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Start
              </Button>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">AI Compliance Assessment</h1>
                <p className="text-sm text-gray-600">
                  Personalized questions based on your business
                </p>
              </div>
            </div>

            {/* Progress indicator for desktop */}
            <div className="hidden md:block">
              <FreemiumAssessmentProgress />
            </div>
          </div>

          {/* Progress indicator for mobile */}
          <div className="mt-4 md:hidden">
            <FreemiumAssessmentProgress />
          </div>
        </div>
      </div>

      {/* Assessment Content */}
      <div className="container mx-auto px-4 py-8">
        {currentToken ? (
          <FreemiumAssessmentFlow token={currentToken} />
        ) : (
          <div className="flex items-center justify-center py-8">
            <Loader2 className="h-8 w-8 animate-spin text-purple-600" />
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="border-t border-gray-200 bg-white py-6">
        <div className="container mx-auto px-4">
          <div className="flex flex-col items-center justify-between space-y-4 sm:flex-row sm:space-y-0">
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <span>Powered by RuleIQ AI</span>
              <div className="h-1 w-1 rounded-full bg-gray-300"></div>
              <span>Secure & Private</span>
              <div className="h-1 w-1 rounded-full bg-gray-300"></div>
              <span>GDPR Compliant</span>
            </div>

            <div className="text-sm text-gray-500">
              Questions tailored to: <span className="font-medium">{sessionData.email}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function FreemiumAssessmentPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-gray-50">
          <div className="space-y-4 text-center">
            <Loader2 className="mx-auto h-8 w-8 animate-spin text-purple-600" />
            <p className="text-gray-600">Loading your assessment...</p>
          </div>
        </div>
      }
    >
      <AssessmentContent />
    </Suspense>
  );
}
