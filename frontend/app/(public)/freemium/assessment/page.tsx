'use client';

import { Suspense, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { FreemiumAssessmentFlow } from '../../../../components/freemium/freemium-assessment-flow';
import { FreemiumAssessmentProgress } from '../../../../components/freemium/freemium-assessment-flow';
import { Card, CardContent } from '../../../../components/ui/card';
import { Alert, AlertDescription } from '../../../../components/ui/alert';
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
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardContent className="py-8 text-center space-y-4">
            <AlertTriangle className="w-12 h-12 text-orange-500 mx-auto" />
            <div className="space-y-2">
              <h2 className="text-xl font-semibold text-gray-900">
                Session Expired
              </h2>
              <p className="text-gray-600">
                Your assessment session has expired. Please start a new assessment.
              </p>
            </div>
            <Button 
              onClick={() => router.push('/freemium')}
              className="bg-teal-600 hover:bg-teal-700"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
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
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-teal-600" />
      </div>
    );
  }

  const currentToken = tokenFromUrl || sessionData.sessionToken;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button
                onClick={() => router.push('/freemium')}
                variant="ghost"
                size="sm"
                className="text-gray-600 hover:text-gray-900"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Start
              </Button>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">
                  AI Compliance Assessment
                </h1>
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
          <div className="md:hidden mt-4">
            <FreemiumAssessmentProgress />
          </div>
        </div>
      </div>

      {/* Assessment Content */}
      <div className="container mx-auto px-4 py-8">
        <FreemiumAssessmentFlow token={currentToken || undefined} />
      </div>

      {/* Footer */}
      <div className="bg-white border-t border-gray-200 py-6">
        <div className="container mx-auto px-4">
          <div className="flex flex-col sm:flex-row items-center justify-between space-y-4 sm:space-y-0">
            <div className="flex items-center space-x-4 text-sm text-gray-500">
              <span>Powered by RuleIQ AI</span>
              <div className="w-1 h-1 bg-gray-300 rounded-full"></div>
              <span>Secure & Private</span>
              <div className="w-1 h-1 bg-gray-300 rounded-full"></div>
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
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center space-y-4">
            <Loader2 className="w-8 h-8 animate-spin text-teal-600 mx-auto" />
            <p className="text-gray-600">Loading your assessment...</p>
          </div>
        </div>
      }
    >
      <AssessmentContent />
    </Suspense>
  );
}