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
    // TODO: Replace with proper logging
    if (!token) {
      // TODO: Replace with proper logging
      router.push('/');
      return;
    }
    // TODO: Replace with proper logging
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
      // TODO: Replace with proper logging

      // // TODO: Replace with proper logging
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
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-teal-50 via-white to-neutral-50">
        <Card className="w-full max-w-md">
          <CardContent className="p-8 text-center">
            <Brain className="mx-auto mb-4 h-12 w-12 animate-pulse text-teal-600" />
            <h2 className="mb-2 text-xl font-semibold">Loading Your Assessment</h2>
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
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-teal-50 via-white to-neutral-50">
        <Card className="w-full max-w-md">
          <CardContent className="p-8 text-center">
            <AlertCircle className="mx-auto mb-4 h-12 w-12 text-destructive" />
            <h2 className="mb-2 text-xl font-semibold">Assessment Unavailable</h2>
            <p className="mb-6 text-muted-foreground">{error}</p>
            <div className="flex justify-center gap-2">
              <Button variant="outline" onClick={() => router.push('/')}>
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Home
              </Button>
              <Button onClick={loadSession}>Try Again</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!sessionData) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-teal-50 via-white to-neutral-50">
        <Card className="w-full max-w-md">
          <CardContent className="p-8 text-center">
            <AlertCircle className="mx-auto mb-4 h-12 w-12 text-amber-500" />
            <h2 className="mb-2 text-xl font-semibold">Session Not Found</h2>
            <p className="mb-6 text-muted-foreground">
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
      <header className="sticky top-0 z-50 border-b bg-white/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" onClick={() => router.push('/')}>
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
                <Clock className="mr-1 inline h-4 w-4" />
                Session expires in{' '}
                {sessionData.expires_at
                  ? Math.max(
                      0,
                      Math.ceil(
                        (new Date(sessionData.expires_at).getTime() - Date.now()) / (1000 * 60),
                      ),
                    )
                  : 60}{' '}
                min
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Progress Bar */}
      <div className="border-b bg-white/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-3">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-sm font-medium">Assessment Progress</span>
            <span className="text-sm text-muted-foreground">
              {sessionData.questions_answered} of {sessionData.total_questions} questions
            </span>
          </div>
          <Progress value={sessionData.progress_percentage} className="h-2" />
        </div>
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="mx-auto max-w-3xl">
          {sessionData.status === 'completed' ? (
            <Card className="p-8 text-center">
              <CheckCircle className="mx-auto mb-4 h-16 w-16 text-teal-600" />
              <h2 className="mb-2 text-2xl font-bold">Assessment Complete!</h2>
              <p className="mb-6 text-muted-foreground">
                Your AI-powered compliance assessment has been completed successfully.
              </p>
              <Button onClick={handleAssessmentComplete}>View Results</Button>
            </Card>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Brain className="h-5 w-5 text-teal-600" />
                  AI-Powered Compliance Assessment
                </CardTitle>
                <p className="text-muted-foreground">
                  Our AI will ask you personalized questions based on your responses to provide the
                  most accurate compliance assessment for your organization.
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
      <footer className="mt-auto border-t bg-white/50">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <Brain className="h-4 w-4" />
              <span>Powered by ruleIQ AI</span>
            </div>
            <div className="flex gap-4">
              <a href="/privacy" className="transition-colors hover:text-foreground">
                Privacy Policy
              </a>
              <a href="/terms" className="transition-colors hover:text-foreground">
                Terms of Service
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
