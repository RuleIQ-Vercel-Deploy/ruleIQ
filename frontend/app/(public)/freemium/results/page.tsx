'use client';

import { Suspense, useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { FreemiumResults } from '../../../../components/freemium/freemium-results';
import { Card, CardContent } from '../../../../components/ui/card';
import { Alert, AlertDescription } from '../../../../components/ui/alert';
import { Button } from '../../../../components/ui/button';
import { useFreemiumStore, useFreemiumSession } from '../../../../lib/stores/freemium-store';
import { AlertTriangle, Loader2, ArrowLeft, Share2, Download } from 'lucide-react';

function ResultsContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { loadSession } = useFreemiumStore();
  const { hasSession, sessionData, canViewResults } = useFreemiumSession();
  const [hasSharedResults, setHasSharedResults] = useState(false);
  
  const tokenFromUrl = searchParams?.get('token');
  const errorFromUrl = searchParams?.get('error');

  // Load session from URL if provided and not already in store
  useEffect(() => {
    if (tokenFromUrl && tokenFromUrl !== sessionData.sessionToken) {
      loadSession(tokenFromUrl).catch(console.error);
    }
  }, [tokenFromUrl, sessionData.sessionToken, loadSession]);

  // Handle error states
  if (errorFromUrl === 'expired') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <Card className="w-full max-w-md">
          <CardContent className="py-8 text-center space-y-4">
            <AlertTriangle className="w-12 h-12 text-orange-500 mx-auto" />
            <div className="space-y-2">
              <h2 className="text-xl font-semibold text-gray-900">
                Results Expired
              </h2>
              <p className="text-gray-600">
                Your assessment results have expired. Please take the assessment again to get fresh results.
              </p>
            </div>
            <Button 
              onClick={() => router.push('/freemium')}
              className="bg-teal-600 hover:bg-teal-700"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Take New Assessment
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Redirect to assessment if no session or assessment not complete
  if (!hasSession || !canViewResults) {
    if (tokenFromUrl) {
      // If token is provided but assessment not complete, redirect to assessment
      router.push(`/freemium/assessment?token=${tokenFromUrl}`);
    } else {
      // No token, redirect to landing page
      router.push('/freemium');
    }
    
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center space-y-4">
          <Loader2 className="w-8 h-8 animate-spin text-teal-600 mx-auto" />
          <p className="text-gray-600">Redirecting to assessment...</p>
        </div>
      </div>
    );
  }

  const currentToken = tokenFromUrl || sessionData.sessionToken;

  const handleShareResults = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'My Compliance Assessment Results - RuleIQ',
          text: 'I just completed a compliance assessment and discovered important gaps in my business. Check out RuleIQ for your free assessment!',
          url: `${window.location.origin}/freemium`,
        });
        setHasSharedResults(true);
      } catch {
        // User cancelled or share failed, fallback to copy
        await navigator.clipboard.writeText(`${window.location.origin}/freemium`);
        setHasSharedResults(true);
      }
    } else {
      // Fallback for browsers without Web Share API
      await navigator.clipboard.writeText(`${window.location.origin}/freemium`);
      setHasSharedResults(true);
    }
  };

  const handleDownloadResults = () => {
    // This would typically generate a PDF report
    // For now, we'll just track the event
    // TODO: Replace with proper logging
  };

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
                Take Another Assessment
              </Button>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">
                  Your Compliance Assessment Results
                </h1>
                <p className="text-sm text-gray-600">
                  Personalized insights for {sessionData.email}
                </p>
              </div>
            </div>
            
            {/* Action buttons for desktop */}
            <div className="hidden md:flex items-center space-x-2">
              <Button
                onClick={handleShareResults}
                variant="outline"
                size="sm"
                className="text-gray-600 hover:text-gray-900"
              >
                <Share2 className="w-4 h-4 mr-2" />
                {hasSharedResults ? 'Shared!' : 'Share Results'}
              </Button>
              <Button
                onClick={handleDownloadResults}
                variant="outline"
                size="sm"
                className="text-gray-600 hover:text-gray-900"
              >
                <Download className="w-4 h-4 mr-2" />
                Download Report
              </Button>
            </div>
          </div>
          
          {/* Action buttons for mobile */}
          <div className="md:hidden mt-4 flex space-x-2">
            <Button
              onClick={handleShareResults}
              variant="outline"
              size="sm"
              className="flex-1 text-gray-600 hover:text-gray-900"
            >
              <Share2 className="w-4 h-4 mr-2" />
              {hasSharedResults ? 'Shared!' : 'Share'}
            </Button>
            <Button
              onClick={handleDownloadResults}
              variant="outline"
              size="sm"
              className="flex-1 text-gray-600 hover:text-gray-900"
            >
              <Download className="w-4 h-4 mr-2" />
              Download
            </Button>
          </div>
        </div>
      </div>

      {/* Results Content */}
      <div className="container mx-auto px-4 py-8">
        <FreemiumResults token={currentToken!} />
      </div>

      {/* Footer */}
      <div className="bg-white border-t border-gray-200 py-6">
        <div className="container mx-auto px-4">
          <div className="text-center space-y-4">
            <div className="flex flex-col sm:flex-row items-center justify-center space-y-2 sm:space-y-0 sm:space-x-6 text-sm text-gray-500">
              <span>🔒 Your data is secure and never shared</span>
              <span>📧 Results saved to {sessionData.email}</span>
              <span>🚀 Powered by RuleIQ AI</span>
            </div>
            
            {/* Call to action for additional assessments */}
            <div className="pt-4 border-t border-gray-100">
              <p className="text-sm text-gray-600 mb-3">
                Want to assess another business unit or framework?
              </p>
              <Button
                onClick={() => router.push('/freemium')}
                variant="outline"
                className="border-teal-200 text-teal-600 hover:bg-teal-50"
              >
                Start Another Assessment
              </Button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function FreemiumResultsPage() {
  return (
    <Suspense 
      fallback={
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center space-y-4">
            <Loader2 className="w-8 h-8 animate-spin text-teal-600 mx-auto" />
            <p className="text-gray-600">Loading your results...</p>
          </div>
        </div>
      }
    >
      <ResultsContent />
    </Suspense>
  );
}