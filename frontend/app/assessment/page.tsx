'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { ArrowLeft, Brain, Clock, CheckCircle, AlertCircle } from 'lucide-react';
import { FreemiumAssessmentFlow } from '@/components/freemium/freemium-assessment-flow';
import { freemiumService } from '@/lib/api/freemium.service';

export default function AssessmentPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const token = searchParams?.get('token') ?? null;

  const [sessionData, setSessionData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log('🔍 Assessment page loaded with token:', token);
    
    if (!token) {
      console.log('❌ No token found, redirecting to home');
      router.push('/');
      return;
    }

    console.log('✅ Token found, loading session...');
    loadSession();
  }, [token, router]);

  const loadSession = async () => {
    if (!token) return;

    try {
      setLoading(true);
      setError(null);
      const session = await freemiumService.getSessionProgress(token);
      setSessionData(session);
    } catch (err) {
      console.error('Failed to load session:', err);
      setError(err instanceof Error ? err.message : 'Failed to load assessment session');
    } finally {
      setLoading(false);
    }
  };

  const handleAssessmentComplete = () => {
    if (token) {
      router.push(`/assessment/results/${token}`);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-teal-50 via-white to-neutral-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-8 text-center">
            <Brain className="h-12 w-12 mx-auto mb-4 text-teal-600 animate-pulse" />
            <h2 className="text-xl font-semibold mb-2">Loading Your Assessment</h2>
            <p className="text-muted-foreground">
              Preparing your personalized AI-driven assessment...
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-teal-50 via-white to-neutral-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-8 text-center">
            <AlertCircle className="h-12 w-12 mx-auto mb-4 text-destructive" />
            <h2 className="text-xl font-semibold mb-2">Assessment Unavailable</h2>
            <p className="text-muted-foreground mb-6">{error}</p>
            <div className="flex gap-2 justify-center">
              <Button variant="outline" onClick={() => router.push('/')}>
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Home
              </Button>
              <Button onClick={loadSession}>
                Try Again
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!sessionData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-teal-50 via-white to-neutral-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-8 text-center">
            <AlertCircle className="h-12 w-12 mx-auto mb-4 text-amber-500" />
            <h2 className="text-xl font-semibold mb-2">Session Not Found</h2>
            <p className="text-muted-foreground mb-6">
              The assessment session could not be found or has expired.
            </p>
            <Button onClick={() => router.push('/')}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Start New Assessment
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 via-white to-neutral-50">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => router.push('/')}
              >
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-teal-700">ruleIQ</h1>
                <p className="text-sm text-muted-foreground">AI Compliance Assessment</p>
              </div>
            </div>

            <div className="flex items-center gap-4">
              <div className="text-sm text-muted-foreground">
                <Clock className="inline h-4 w-4 mr-1" />
                Session expires in{' '}
                {sessionData.expires_at ? 
                  Math.max(0, Math.ceil((new Date(sessionData.expires_at).getTime() - Date.now()) / (1000 * 60)))
                  : 60
                } min
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Progress Bar */}
      <div className="bg-white/80 backdrop-blur-sm border-b">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Assessment Progress</span>
            <span className="text-sm text-muted-foreground">
              {sessionData.questions_answered} of {sessionData.total_questions} questions
            </span>
          </div>
          <Progress 
            value={sessionData.progress_percentage} 
            className="h-2"
          />
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto">
          {sessionData.status === 'completed' ? (
            <Card className="text-center p-8">
              <CheckCircle className="h-16 w-16 mx-auto mb-4 text-teal-600" />
              <h2 className="text-2xl font-bold mb-2">Assessment Complete!</h2>
              <p className="text-muted-foreground mb-6">
                Your AI-powered compliance assessment has been completed successfully.
              </p>
              <Button onClick={handleAssessmentComplete}>
                View Results
              </Button>
            </Card>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5 text-teal-600" />
                  AI-Powered Compliance Assessment
                </CardTitle>
                <p className="text-muted-foreground">
                  Our AI will ask you personalized questions based on your responses to provide 
                  the most accurate compliance assessment for your organization.
                </p>
              </CardHeader>
              <CardContent>
                <FreemiumAssessmentFlow 
                  token={token ?? undefined} 
                  onComplete={handleAssessmentComplete}
                />
              </CardContent>
            </Card>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-auto bg-white/50 border-t">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <Brain className="h-4 w-4" />
              <span>Powered by ruleIQ AI</span>
            </div>
            <div className="flex gap-4">
              <a href="/privacy" className="hover:text-foreground transition-colors">
                Privacy Policy
              </a>
              <a href="/terms" className="hover:text-foreground transition-colors">
                Terms of Service
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}