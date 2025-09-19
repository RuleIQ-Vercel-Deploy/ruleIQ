'use client';

import { FreemiumEmailCaptureInline } from '../freemium/freemium-email-capture';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { Shield, Zap, Clock, CheckCircle, Star, ArrowRight, BarChart3, Users } from 'lucide-react';

interface FreemiumMarketingSectionProps {
  className?: string;
  showInlineCapture?: boolean;
  variant?: 'hero' | 'section' | 'sidebar';
}

export function FreemiumMarketingSection({
  className = '',
  showInlineCapture = true,
  variant = 'section',
}: FreemiumMarketingSectionProps) {
  if (variant === 'hero') {
    return (
      <div className={`bg-gradient-to-br from-purple-50 to-purple-100 py-16 ${className}`}>
        <div className="container mx-auto px-4">
          <div className="mx-auto max-w-4xl space-y-8 text-center">
            <div className="space-y-4">
              <Badge className="bg-purple-600 px-4 py-1 text-white">🚀 Free AI Assessment</Badge>
              <h2 className="text-3xl font-bold text-gray-900 lg:text-4xl">
                Discover Your Compliance Gaps in
                <span className="text-purple-600"> 5 Minutes</span>
              </h2>
              <p className="mx-auto max-w-2xl text-xl text-gray-600">
                Get personalized insights from our AI that identifies critical compliance gaps and
                provides actionable recommendations tailored to your business.
              </p>
            </div>

            {/* Benefits Grid */}
            <div className="mx-auto grid max-w-3xl gap-6 md:grid-cols-3">
              <div className="rounded-lg bg-white p-6 shadow-sm">
                <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-purple-100">
                  <Zap className="h-6 w-6 text-purple-600" />
                </div>
                <h3 className="mb-2 font-semibold text-gray-900">AI-Powered</h3>
                <p className="text-sm text-gray-600">
                  Dynamic questions based on your specific business context
                </p>
              </div>
              <div className="rounded-lg bg-white p-6 shadow-sm">
                <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-purple-100">
                  <Clock className="h-6 w-6 text-purple-600" />
                </div>
                <h3 className="mb-2 font-semibold text-gray-900">5 Minutes</h3>
                <p className="text-sm text-gray-600">
                  Quick assessment with instant, actionable results
                </p>
              </div>
              <div className="rounded-lg bg-white p-6 shadow-sm">
                <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-purple-100">
                  <Shield className="h-6 w-6 text-purple-600" />
                </div>
                <h3 className="mb-2 font-semibold text-gray-900">Complete Coverage</h3>
                <p className="text-sm text-gray-600">GDPR, ISO 27001, SOC 2, and 15+ frameworks</p>
              </div>
            </div>

            {showInlineCapture && (
              <div className="mx-auto max-w-md">
                <FreemiumEmailCaptureInline />
              </div>
            )}

            {!showInlineCapture && (
              <Button
                onClick={() => (window.location.href = '/freemium')}
                className="bg-purple-600 px-8 py-3 text-lg text-white hover:bg-purple-700"
              >
                Start Free Assessment
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (variant === 'sidebar') {
    return (
      <Card className={`${className}`}>
        <CardContent className="space-y-4 p-6">
          <div className="space-y-2 text-center">
            <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-purple-100">
              <Shield className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">Free Compliance Check</h3>
            <p className="text-sm text-gray-600">
              Get your personalized compliance assessment in under 5 minutes
            </p>
          </div>

          <div className="space-y-3">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>AI-powered gap analysis</span>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>Personalized recommendations</span>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>Risk score calculation</span>
            </div>
          </div>

          {showInlineCapture ? (
            <FreemiumEmailCaptureInline />
          ) : (
            <Button
              onClick={() => (window.location.href = '/freemium')}
              className="w-full bg-purple-600 text-white hover:bg-purple-700"
            >
              Start Assessment
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          )}
        </CardContent>
      </Card>
    );
  }

  // Default 'section' variant
  return (
    <div className={`py-16 ${className}`}>
      <div className="container mx-auto px-4">
        <div className="mx-auto max-w-6xl">
          <div className="grid items-center gap-12 lg:grid-cols-2">
            {/* Left Column - Content */}
            <div className="space-y-6">
              <div className="space-y-4">
                <Badge className="border-purple-200 bg-purple-100 text-purple-700">
                  🎯 Free Assessment
                </Badge>
                <h2 className="text-3xl font-bold text-gray-900">
                  Know Your Compliance Gaps
                  <span className="text-purple-600"> Before They Become Problems</span>
                </h2>
                <p className="text-lg text-gray-600">
                  Our AI analyzes your business against 15+ compliance frameworks and provides a
                  personalized roadmap to address your most critical gaps first.
                </p>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <BarChart3 className="h-5 w-5 text-purple-600" />
                    <span className="text-2xl font-bold text-gray-900">2,300+</span>
                  </div>
                  <p className="text-sm text-gray-600">Businesses assessed</p>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <Clock className="h-5 w-5 text-purple-600" />
                    <span className="text-2xl font-bold text-gray-900">4.2 min</span>
                  </div>
                  <p className="text-sm text-gray-600">Average completion time</p>
                </div>
              </div>

              {/* Key Features */}
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-100">
                    <Zap className="h-4 w-4 text-purple-600" />
                  </div>
                  <span className="text-gray-700">
                    AI generates questions specific to your business type and size
                  </span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-100">
                    <Shield className="h-4 w-4 text-purple-600" />
                  </div>
                  <span className="text-gray-700">
                    Comprehensive coverage of GDPR, ISO 27001, SOC 2, and more
                  </span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-100">
                    <BarChart3 className="h-4 w-4 text-purple-600" />
                  </div>
                  <span className="text-gray-700">
                    Risk score and prioritized action plan with timelines
                  </span>
                </div>
              </div>

              {/* Social Proof */}
              <div className="flex items-center space-x-4 border-t border-gray-100 pt-4">
                <div className="flex -space-x-2">
                  {[1, 2, 3, 4].map((i) => (
                    <div
                      key={i}
                      className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-white bg-gradient-to-br from-purple-400 to-purple-600"
                    >
                      <Users className="h-4 w-4 text-white" />
                    </div>
                  ))}
                </div>
                <div className="flex items-center space-x-1">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <span className="text-sm text-gray-600">4.8/5 rating from 2,300+ assessments</span>
              </div>
            </div>

            {/* Right Column - Email Capture */}
            <div className="lg:pl-8">
              {showInlineCapture ? (
                <Card className="p-6">
                  <div className="mb-6 text-center">
                    <h3 className="mb-2 text-xl font-semibold text-gray-900">
                      Start Your Free Assessment
                    </h3>
                    <p className="text-gray-600">
                      Get personalized compliance insights in under 5 minutes
                    </p>
                  </div>
                  <FreemiumEmailCaptureInline />
                </Card>
              ) : (
                <div className="text-center">
                  <Button
                    onClick={() => (window.location.href = '/freemium')}
                    className="bg-purple-600 px-8 py-4 text-lg text-white hover:bg-purple-700"
                    size="lg"
                  >
                    Start Free Assessment
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default FreemiumMarketingSection;
