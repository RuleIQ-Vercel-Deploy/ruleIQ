'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import {
  ArrowLeft,
  ArrowRight,
  Brain,
  Shield,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  Target,
  FileText,
  Zap,
  Users,
  Star,
  Download,
  Share,
  Loader2,
} from 'lucide-react';
import { freemiumService, type AssessmentResultsResponse } from '@/lib/api/freemium.service';

export default function AssessmentResultsPage() {
  const router = useRouter();
  const params = useParams();
  const token = params?.token as string;

  const [results, setResults] = useState<AssessmentResultsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      router.push('/');
      return;
    }

    loadResults();
  }, [token, router]);

  const loadResults = async () => {
    if (!token) return;

    try {
      setLoading(true);
      setError(null);
      const data = await freemiumService.getResults(token);
      setResults(data);
    } catch (err) {
      // TODO: Replace with proper logging

      // // TODO: Replace with proper logging
      setError(err instanceof Error ? err.message : 'Failed to load assessment results');
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel?.toLowerCase()) {
      case 'low':
        return 'text-green-600 bg-green-50';
      case 'medium':
        return 'text-amber-600 bg-amber-50';
      case 'high':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getRiskIcon = (riskLevel: string) => {
    switch (riskLevel?.toLowerCase()) {
      case 'low':
        return <CheckCircle className="h-5 w-5" />;
      case 'medium':
        return <AlertTriangle className="h-5 w-5" />;
      case 'high':
        return <AlertTriangle className="h-5 w-5" />;
      default:
        return <Shield className="h-5 w-5" />;
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-teal-50 via-white to-neutral-50">
        <Card className="w-full max-w-md">
          <CardContent className="p-8 text-center">
            <Loader2 className="mx-auto mb-4 h-12 w-12 animate-spin text-teal-600" />
            <h2 className="mb-2 text-xl font-semibold">Analyzing Your Results</h2>
            <p className="text-muted-foreground">
              Our AI is generating your personalized compliance assessment...
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error || !results) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-teal-50 via-white to-neutral-50">
        <Card className="w-full max-w-md">
          <CardContent className="p-8 text-center">
            <AlertTriangle className="mx-auto mb-4 h-12 w-12 text-destructive" />
            <h2 className="mb-2 text-xl font-semibold">Results Unavailable</h2>
            <p className="mb-6 text-muted-foreground">
              {error || 'Assessment results could not be found.'}
            </p>
            <div className="flex justify-center gap-2">
              <Button variant="outline" onClick={() => router.push('/')}>
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Home
              </Button>
              <Button onClick={loadResults}>Try Again</Button>
            </div>
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
                Home
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-teal-700">ruleIQ</h1>
                <p className="text-sm text-muted-foreground">Assessment Results</p>
              </div>
            </div>

            <div className="flex gap-2">
              <Button variant="outline" size="sm">
                <Download className="mr-2 h-4 w-4" />
                Download Report
              </Button>
              <Button variant="outline" size="sm">
                <Share className="mr-2 h-4 w-4" />
                Share
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="mx-auto max-w-4xl space-y-8">
          {/* Results Overview */}
          <Card className="bg-gradient-to-r from-teal-600 to-teal-700 text-white">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-2xl">Your Compliance Assessment</CardTitle>
                <Brain className="h-8 w-8" />
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
                {/* Compliance Score */}
                <div className="text-center">
                  <div className="mb-2 text-3xl font-bold">
                    {results.compliance_score ? Math.round(results.compliance_score) : 'N/A'}%
                  </div>
                  <p className="text-teal-100">Compliance Score</p>
                  {results.compliance_score && (
                    <Progress value={results.compliance_score} className="mt-2 bg-teal-800" />
                  )}
                </div>

                {/* Risk Level */}
                <div className="text-center">
                  <Badge
                    className={`px-4 py-2 text-lg ${getRiskLevelColor(results.risk_level)} text-current`}
                  >
                    {getRiskIcon(results.risk_level)}
                    <span className="ml-2 capitalize">{results.risk_level} Risk</span>
                  </Badge>
                  <p className="mt-2 text-teal-100">Current Risk Level</p>
                </div>

                {/* Completion Status */}
                <div className="text-center">
                  <CheckCircle className="mx-auto mb-2 h-12 w-12" />
                  <p className="text-teal-100">Assessment Complete</p>
                  <p className="text-xs text-teal-200">
                    {results.completed_at
                      ? new Date(results.completed_at).toLocaleDateString()
                      : 'Today'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Key Insights */}
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            {/* Strengths */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-green-700">
                  <CheckCircle className="h-5 w-5" />
                  Compliance Strengths
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-3 rounded-lg bg-green-50 p-3">
                  <Shield className="h-5 w-5 text-green-600" />
                  <span className="text-sm">Basic security measures in place</span>
                </div>
                <div className="flex items-center gap-3 rounded-lg bg-green-50 p-3">
                  <FileText className="h-5 w-5 text-green-600" />
                  <span className="text-sm">Documentation practices established</span>
                </div>
                <div className="flex items-center gap-3 rounded-lg bg-green-50 p-3">
                  <Users className="h-5 w-5 text-green-600" />
                  <span className="text-sm">Team awareness of compliance needs</span>
                </div>
              </CardContent>
            </Card>

            {/* Priority Areas */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-amber-700">
                  <Target className="h-5 w-5" />
                  Priority Improvements
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-center gap-3 rounded-lg bg-amber-50 p-3">
                  <AlertTriangle className="h-5 w-5 text-amber-600" />
                  <span className="text-sm">Formal risk assessment process</span>
                </div>
                <div className="flex items-center gap-3 rounded-lg bg-amber-50 p-3">
                  <Shield className="h-5 w-5 text-amber-600" />
                  <span className="text-sm">Enhanced security controls</span>
                </div>
                <div className="flex items-center gap-3 rounded-lg bg-amber-50 p-3">
                  <FileText className="h-5 w-5 text-amber-600" />
                  <span className="text-sm">Comprehensive policy framework</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Next Steps */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-teal-600" />
                Recommended Next Steps
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-start gap-4 rounded-lg border p-4">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-teal-100 font-semibold text-teal-600">
                    1
                  </div>
                  <div>
                    <h4 className="mb-1 font-semibold">Complete Full Assessment</h4>
                    <p className="text-sm text-muted-foreground">
                      Unlock detailed insights with our comprehensive assessment including 200+
                      questions and specific framework recommendations.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4 rounded-lg border p-4">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-teal-100 font-semibold text-teal-600">
                    2
                  </div>
                  <div>
                    <h4 className="mb-1 font-semibold">Get Expert Guidance</h4>
                    <p className="text-sm text-muted-foreground">
                      Schedule a consultation with our compliance experts to create a customized
                      roadmap for your organization.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4 rounded-lg border p-4">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-teal-100 font-semibold text-teal-600">
                    3
                  </div>
                  <div>
                    <h4 className="mb-1 font-semibold">Automate Compliance</h4>
                    <p className="text-sm text-muted-foreground">
                      Implement our AI-powered compliance automation platform to streamline your
                      ongoing compliance management.
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* CTA Section */}
          <Card className="bg-gradient-to-r from-teal-600 to-teal-700 text-white">
            <CardContent className="p-8 text-center">
              <Zap className="mx-auto mb-4 h-12 w-12" />
              <h3 className="mb-2 text-2xl font-bold">Ready to Get Compliant?</h3>
              <p className="mb-6 text-teal-100">
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
                  className="border-white text-white hover:bg-white hover:text-teal-600"
                  onClick={() => router.push('/contact?source=assessment')}
                >
                  Talk to Expert
                </Button>
              </div>

              <div className="mt-6 flex items-center justify-center gap-6 border-t border-teal-500 pt-6">
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
