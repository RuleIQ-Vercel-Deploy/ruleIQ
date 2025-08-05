'use client';

import { FreemiumEmailCaptureInline } from '../freemium/freemium-email-capture';
import { Card, CardContent } from '../ui/card';
import { Badge } from '../ui/badge';
import { Button } from '../ui/button';
import { 
  Shield, 
  Zap, 
  Clock, 
  CheckCircle, 
  Star,
  ArrowRight,
  BarChart3,
  Users
} from 'lucide-react';

interface FreemiumMarketingSectionProps {
  className?: string;
  showInlineCapture?: boolean;
  variant?: 'hero' | 'section' | 'sidebar';
}

export function FreemiumMarketingSection({ 
  className = "",
  showInlineCapture = true,
  variant = 'section'
}: FreemiumMarketingSectionProps) {
  if (variant === 'hero') {
    return (
      <div className={`bg-gradient-to-br from-teal-50 to-teal-100 py-16 ${className}`}>
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto text-center space-y-8">
            <div className="space-y-4">
              <Badge className="bg-teal-600 text-white px-4 py-1">
                🚀 Free AI Assessment
              </Badge>
              <h2 className="text-3xl lg:text-4xl font-bold text-gray-900">
                Discover Your Compliance Gaps in 
                <span className="text-teal-600"> 5 Minutes</span>
              </h2>
              <p className="text-xl text-gray-600 max-w-2xl mx-auto">
                Get personalized insights from our AI that identifies critical compliance gaps 
                and provides actionable recommendations tailored to your business.
              </p>
            </div>

            {/* Benefits Grid */}
            <div className="grid md:grid-cols-3 gap-6 max-w-3xl mx-auto">
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <div className="w-12 h-12 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Zap className="w-6 h-6 text-teal-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">AI-Powered</h3>
                <p className="text-sm text-gray-600">
                  Dynamic questions based on your specific business context
                </p>
              </div>
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <div className="w-12 h-12 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Clock className="w-6 h-6 text-teal-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">5 Minutes</h3>
                <p className="text-sm text-gray-600">
                  Quick assessment with instant, actionable results
                </p>
              </div>
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <div className="w-12 h-12 bg-teal-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Shield className="w-6 h-6 text-teal-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Complete Coverage</h3>
                <p className="text-sm text-gray-600">
                  GDPR, ISO 27001, SOC 2, and 15+ frameworks
                </p>
              </div>
            </div>

            {showInlineCapture && (
              <div className="max-w-md mx-auto">
                <FreemiumEmailCaptureInline />
              </div>
            )}

            {!showInlineCapture && (
              <Button
                onClick={() => window.location.href = '/freemium'}
                className="bg-teal-600 hover:bg-teal-700 text-white px-8 py-3 text-lg"
              >
                Start Free Assessment
                <ArrowRight className="w-5 h-5 ml-2" />
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
        <CardContent className="p-6 space-y-4">
          <div className="text-center space-y-2">
            <div className="w-12 h-12 bg-teal-100 rounded-full flex items-center justify-center mx-auto">
              <Shield className="w-6 h-6 text-teal-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900">
              Free Compliance Check
            </h3>
            <p className="text-sm text-gray-600">
              Get your personalized compliance assessment in under 5 minutes
            </p>
          </div>

          <div className="space-y-3">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span>AI-powered gap analysis</span>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span>Personalized recommendations</span>
            </div>
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <CheckCircle className="w-4 h-4 text-green-500" />
              <span>Risk score calculation</span>
            </div>
          </div>

          {showInlineCapture ? (
            <FreemiumEmailCaptureInline />
          ) : (
            <Button
              onClick={() => window.location.href = '/freemium'}
              className="w-full bg-teal-600 hover:bg-teal-700 text-white"
            >
              Start Assessment
              <ArrowRight className="w-4 h-4 ml-2" />
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
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Column - Content */}
            <div className="space-y-6">
              <div className="space-y-4">
                <Badge className="bg-teal-100 text-teal-700 border-teal-200">
                  🎯 Free Assessment
                </Badge>
                <h2 className="text-3xl font-bold text-gray-900">
                  Know Your Compliance Gaps 
                  <span className="text-teal-600"> Before They Become Problems</span>
                </h2>
                <p className="text-lg text-gray-600">
                  Our AI analyzes your business against 15+ compliance frameworks and provides 
                  a personalized roadmap to address your most critical gaps first.
                </p>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-6">
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <BarChart3 className="w-5 h-5 text-teal-600" />
                    <span className="text-2xl font-bold text-gray-900">2,300+</span>
                  </div>
                  <p className="text-sm text-gray-600">Businesses assessed</p>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <Clock className="w-5 h-5 text-teal-600" />
                    <span className="text-2xl font-bold text-gray-900">4.2 min</span>
                  </div>
                  <p className="text-sm text-gray-600">Average completion time</p>
                </div>
              </div>

              {/* Key Features */}
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-teal-100 rounded-full flex items-center justify-center">
                    <Zap className="w-4 h-4 text-teal-600" />
                  </div>
                  <span className="text-gray-700">
                    AI generates questions specific to your business type and size
                  </span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-teal-100 rounded-full flex items-center justify-center">
                    <Shield className="w-4 h-4 text-teal-600" />
                  </div>
                  <span className="text-gray-700">
                    Comprehensive coverage of GDPR, ISO 27001, SOC 2, and more
                  </span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-8 h-8 bg-teal-100 rounded-full flex items-center justify-center">
                    <BarChart3 className="w-4 h-4 text-teal-600" />
                  </div>
                  <span className="text-gray-700">
                    Risk score and prioritized action plan with timelines
                  </span>
                </div>
              </div>

              {/* Social Proof */}
              <div className="flex items-center space-x-4 pt-4 border-t border-gray-100">
                <div className="flex -space-x-2">
                  {[1, 2, 3, 4].map((i) => (
                    <div
                      key={i}
                      className="w-8 h-8 bg-gradient-to-br from-teal-400 to-teal-600 rounded-full border-2 border-white flex items-center justify-center"
                    >
                      <Users className="w-4 h-4 text-white" />
                    </div>
                  ))}
                </div>
                <div className="flex items-center space-x-1">
                  {[1, 2, 3, 4, 5].map((i) => (
                    <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <span className="text-sm text-gray-600">
                  4.8/5 rating from 2,300+ assessments
                </span>
              </div>
            </div>

            {/* Right Column - Email Capture */}
            <div className="lg:pl-8">
              {showInlineCapture ? (
                <Card className="p-6">
                  <div className="text-center mb-6">
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
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
                    onClick={() => window.location.href = '/freemium'}
                    className="bg-teal-600 hover:bg-teal-700 text-white px-8 py-4 text-lg"
                    size="lg"
                  >
                    Start Free Assessment
                    <ArrowRight className="w-5 h-5 ml-2" />
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