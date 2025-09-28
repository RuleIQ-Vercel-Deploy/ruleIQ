'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { useToast } from '@/components/ui/use-toast';
import {
  ArrowLeft,
  ArrowRight,
  Shield,
  AlertTriangle,
  Zap,
  Star,
  Share,
  RefreshCw,
  Loader2,
} from 'lucide-react';
import { type AssessmentResultsResponse } from '@/lib/api/freemium.service';
import { assessmentResultsService, type TrendAnalysisData } from '@/lib/services/assessment-results.service';
import { type AssessmentResult } from '@/lib/assessment-engine/types';
import { DetailedResultsDashboard } from '@/components/assessments/results/DetailedResultsDashboard';

interface AssessmentResultsClientProps {
  token: string;
}

export default function AssessmentResultsClient({ token }: AssessmentResultsClientProps) {
  const router = useRouter();
  const { toast } = useToast();

  const [results, setResults] = useState<AssessmentResultsResponse | AssessmentResult | null>(null);
  const [trendData, setTrendData] = useState<TrendAnalysisData | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingTrends, setLoadingTrends] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  useEffect(() => {
    if (!token) {
      router.push('/');
      return;
    }

    loadResults();
  }, [token, router]);

  const loadResults = async (forceRefresh = false) => {
    if (!token) return;

    try {
      setLoading(true);
      setError(null);

      // Load assessment results with caching
      const data = await assessmentResultsService.getResults(token, forceRefresh);
      setResults(data);

      // Load historical data for trend analysis using consistent key resolution
      const businessKeyParams: { session_id: string; session_token: string; lead_id?: string } = {
        session_id: data.session_id,
        session_token: token
      };
      if (data.lead_id) {
        businessKeyParams.lead_id = data.lead_id;
      }
      const businessKey = assessmentResultsService.getBusinessProfileKey(businessKeyParams);
      await loadTrendData(businessKey);

    } catch (err) {
      console.error('Failed to load assessment results:', err);

      // Try to load from sessionStorage as fallback
      try {
        const sessionData = sessionStorage.getItem(`assessment_result_${token}`);
        if (sessionData) {
          const parsedData = JSON.parse(sessionData);
          if (!('compliance_score' in parsedData) && parsedData.completedAt) {
            parsedData.completedAt = new Date(parsedData.completedAt);
          }
          setResults(parsedData);

          // Show a banner indicating it's a local preview
          toast({
            title: 'Using Cached Results',
            description: 'Displaying locally stored assessment results. Consider exporting for permanent storage.',
            variant: 'default',
          });

          // Load historical data for trend analysis using consistent key resolution
          const businessKeyParams: { session_id: string; session_token: string; lead_id?: string } = {
            session_id: parsedData.session_id,
            session_token: token
          };
          if (parsedData.lead_id) {
            businessKeyParams.lead_id = parsedData.lead_id;
          }
          const businessKey = assessmentResultsService.getBusinessProfileKey(businessKeyParams);
          await loadTrendData(businessKey);
          return;
        }
      } catch (sessionErr) {
        console.error('Failed to load from sessionStorage:', sessionErr);
      }

      // Handle specific error types
      if (err instanceof Error) {
        if (err.message.includes('expired') || err.message.includes('not found')) {
          setError('Assessment results have expired or are no longer available. Please take a new assessment.');
        } else if (err.message.includes('network') || err.message.includes('fetch')) {
          setError('Network error. Please check your connection and try again.');
        } else {
          setError(err.message);
        }
      } else {
        setError('Failed to load assessment results. Please try again.');
      }

      // Increment retry count for analytics
      setRetryCount(prev => prev + 1);
    } finally {
      setLoading(false);
    }
  };

  const loadTrendData = async (businessId: string) => {
    try {
      setLoadingTrends(true);

      // Use business profile ID for freemium assessments
      const trends = await assessmentResultsService.generateTrendData(
        businessId,
        'last_3_months',
        'freemium_framework'
      );

      setTrendData(trends);
    } catch (err) {
      console.error('Failed to load trend data:', err);
      // Don't show error for trend data - it's not critical
      setTrendData(null);
    } finally {
      setLoadingTrends(false);
    }
  };


  const handleRetry = () => {
    loadResults(true); // Force refresh
  };

  const handleShare = async () => {
    if (!results) return;

    try {
      // Use type guard to determine which score to use
      const score = 'compliance_score' in results
        ? results.compliance_score
        : results.overallScore;

      const shareData = {
        title: 'My Compliance Assessment Results',
        text: `I scored ${Math.round(score)}% on my compliance assessment with ruleIQ`,
        url: window.location.href,
      };

      if (navigator.share && navigator.canShare(shareData)) {
        await navigator.share(shareData);
      } else {
        // Fallback to clipboard
        await navigator.clipboard.writeText(window.location.href);
        toast({
          title: 'Link Copied',
          description: 'Assessment results link copied to clipboard',
        });
      }
    } catch (err) {
      console.error('Share failed:', err);
      toast({
        title: 'Share Failed',
        description: 'Unable to share results. Please try copying the URL manually.',
        variant: 'destructive',
      });
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-purple-50 via-white to-neutral-50">
          <Card className="w-full max-w-md">
            <CardContent className="p-8 text-center">
              <Loader2 className="mx-auto mb-4 h-12 w-12 animate-spin text-purple-600" />
              <h2 className="mb-2 text-xl font-semibold">Analyzing Your Results</h2>
              <p className="text-muted-foreground mb-4">
                Our AI is generating your personalized compliance assessment...
              </p>
              <div className="space-y-2">
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div className="h-full bg-purple-600 rounded-full animate-pulse" style={{ width: '60%' }} />
                </div>
                <p className="text-xs text-muted-foreground">
                  Processing assessment data and generating insights...
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
    );
  }

  if (error || !results) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-purple-50 via-white to-neutral-50">
          <Card className="w-full max-w-md">
            <CardContent className="p-8 text-center">
              <AlertTriangle className="mx-auto mb-4 h-12 w-12 text-destructive" />
              <h2 className="mb-2 text-xl font-semibold">Results Unavailable</h2>
              <p className="mb-6 text-muted-foreground">
                {error || 'Assessment results could not be found.'}
              </p>
              {retryCount > 0 && (
                <p className="mb-4 text-xs text-muted-foreground">
                  Retry attempts: {retryCount}
                </p>
              )}
              <div className="flex justify-center gap-2">
                <Button variant="outline" onClick={() => router.push('/')}>
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Back to Home
                </Button>
                <Button onClick={handleRetry} disabled={loading}>
                  <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
                  Try Again
                </Button>
              </div>
              {error?.includes('expired') && (
                <div className="mt-4 p-3 bg-blue-50 rounded-lg">
                  <p className="text-sm text-blue-700">
                    Your assessment session has expired. Please take a new assessment to get fresh results.
                  </p>
                  <Button
                    variant="link"
                    size="sm"
                    onClick={() => router.push('/assessment')}
                    className="mt-2 text-blue-600"
                  >
                    Take New Assessment
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-neutral-50">
        {/* Header */}
        <header className="sticky top-0 z-50 border-b bg-white/80 backdrop-blur-sm">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Button variant="ghost" size="sm" onClick={() => router.push('/')}>
                  <ArrowLeft className="mr-2 h-4 w-4" />
                  Home
                </Button>
                <div>
                  <h1 className="text-2xl font-bold text-purple-700">ruleIQ</h1>
                  <p className="text-sm text-muted-foreground">Assessment Results</p>
                </div>
              </div>

              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleShare}
                >
                  <Share className="mr-2 h-4 w-4" />
                  Share
                </Button>
              </div>
            </div>
          </div>
        </header>

        <main className="container mx-auto px-4 py-8">
          <div className="mx-auto max-w-7xl">
            {/* Detailed Results Dashboard */}
            <DetailedResultsDashboard
              results={
                'compliance_score' in results
                  ? assessmentResultsService.transformToAssessmentResult(results)
                  : results
              }
              sectionDetails={
                'compliance_score' in results
                  ? assessmentResultsService.generateSectionDetails(results)
                  : []
              }
              trendData={trendData?.dataPoints || []}
              className="mb-8"
            />

            {/* Loading indicator for trends */}
            {loadingTrends && (
              <Card className="mb-8">
                <CardContent className="p-6 text-center">
                  <Loader2 className="mx-auto mb-2 h-6 w-6 animate-spin text-purple-600" />
                  <p className="text-sm text-muted-foreground">Loading trend analysis...</p>
                </CardContent>
              </Card>
            )}

            {/* CTA Section */}
            <Card className="bg-gradient-to-r from-purple-700 via-purple-600 to-purple-400 text-white">
              <CardContent className="p-8 text-center">
                <Zap className="mx-auto mb-4 h-12 w-12" />
                <h3 className="mb-2 text-2xl font-bold">Ready to Get Compliant?</h3>
                <p className="mb-6 text-purple-100">
                  Take the next step with ruleIQ's comprehensive compliance automation platform. Cut
                  costs by 60%, reduce audit prep by 75%, and achieve 99.9% accuracy.
                </p>

                <div className="flex flex-col justify-center gap-4 sm:flex-row">
                  <Button
                    size="lg"
                    variant="secondary"
                    onClick={() => router.push('/pricing?source=assessment')}
                  >
                    Get Compliant Now
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                  <Button
                    size="lg"
                    variant="outline"
                    className="border-white text-white hover:bg-white hover:text-purple-600"
                    onClick={() => router.push('/contact?source=assessment')}
                  >
                    Talk to Expert
                  </Button>
                </div>

                <div className="mt-6 flex items-center justify-center gap-6 border-t border-purple-500 pt-6">
                  <div className="flex items-center gap-2">
                    <Star className="h-4 w-4 fill-current" />
                    <span className="text-sm">4.9/5 Customer Rating</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Shield className="h-4 w-4" />
                    <span className="text-sm">ISO 27001 Certified</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
  );
}