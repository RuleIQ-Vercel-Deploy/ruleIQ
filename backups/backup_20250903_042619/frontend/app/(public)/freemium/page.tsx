import type { Metadata } from 'next';
import { FreemiumEmailCapture } from '../../../components/freemium/freemium-email-capture';
import { Card, CardContent } from '../../../components/ui/card';
import { Badge } from '../../../components/ui/badge';
import { Shield, Zap, Users, Clock, CheckCircle, Star, ArrowRight } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Free AI Compliance Assessment | RuleIQ',
  description:
    'Get a personalized compliance assessment in under 5 minutes. AI-powered analysis identifies your critical compliance gaps and provides actionable recommendations.',
  keywords: 'compliance assessment, GDPR compliance, ISO 27001, free assessment, AI compliance',
  openGraph: {
    title: 'Free AI Compliance Assessment | RuleIQ',
    description:
      'Discover your compliance gaps in under 5 minutes with our AI-powered assessment tool.',
    type: 'website',
  },
};

export default function FreemiumLandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-teal-50">
      {/* Hero Section */}
      <div className="container mx-auto px-4 py-12">
        <div className="mx-auto max-w-6xl">
          <div className="grid items-center gap-12 lg:grid-cols-2">
            {/* Left Column - Hero Content */}
            <div className="space-y-8">
              <div className="space-y-4">
                <Badge className="border-teal-200 bg-teal-100 px-3 py-1 text-sm text-teal-700">
                  🚀 AI-Powered Assessment
                </Badge>
                <h1 className="text-4xl font-bold leading-tight text-gray-900 lg:text-5xl">
                  Discover Your
                  <span className="text-teal-600"> Compliance Gaps</span>
                  in 5 Minutes
                </h1>
                <p className="text-xl leading-relaxed text-gray-600">
                  Get a personalized AI assessment that identifies critical compliance gaps,
                  calculates your risk score, and provides actionable recommendations tailored to
                  your business.
                </p>
              </div>

              {/* Key Benefits */}
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-teal-100">
                    <Zap className="h-4 w-4 text-teal-600" />
                  </div>
                  <span className="font-medium text-gray-700">
                    AI generates questions based on your specific business context
                  </span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-teal-100">
                    <Shield className="h-4 w-4 text-teal-600" />
                  </div>
                  <span className="font-medium text-gray-700">
                    Identify gaps across GDPR, ISO 27001, SOC 2, and more
                  </span>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="flex h-8 w-8 items-center justify-center rounded-full bg-teal-100">
                    <Clock className="h-4 w-4 text-teal-600" />
                  </div>
                  <span className="font-medium text-gray-700">
                    Get results instantly with prioritized action items
                  </span>
                </div>
              </div>

              {/* Social Proof */}
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <div className="flex -space-x-2">
                    {[1, 2, 3, 4].map((i) => (
                      <div
                        key={i}
                        className="flex h-8 w-8 items-center justify-center rounded-full border-2 border-white bg-gradient-to-br from-teal-400 to-teal-600"
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
                </div>
                <p className="text-sm text-gray-600">
                  <span className="font-semibold">2,300+</span> businesses have discovered their
                  compliance gaps. Average time to complete:{' '}
                  <span className="font-semibold">4.2 minutes</span>
                </p>
              </div>
            </div>

            {/* Right Column - Email Capture Form */}
            <div className="lg:pl-8">
              <FreemiumEmailCapture />
            </div>
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="bg-white py-16">
        <div className="container mx-auto px-4">
          <div className="mx-auto max-w-4xl space-y-12 text-center">
            <div className="space-y-4">
              <h2 className="text-3xl font-bold text-gray-900">How Our AI Assessment Works</h2>
              <p className="text-lg text-gray-600">
                Advanced AI technology analyzes your responses to create a personalized compliance
                roadmap
              </p>
            </div>

            <div className="grid gap-8 md:grid-cols-3">
              <div className="space-y-4 text-center">
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-teal-100">
                  <span className="text-2xl font-bold text-teal-600">1</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900">Smart Questions</h3>
                <p className="text-gray-600">
                  AI asks targeted questions based on your business type, size, and industry to
                  understand your unique compliance needs.
                </p>
              </div>

              <div className="space-y-4 text-center">
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-teal-100">
                  <span className="text-2xl font-bold text-teal-600">2</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900">Gap Analysis</h3>
                <p className="text-gray-600">
                  Our AI analyzes your responses against 15+ compliance frameworks to identify
                  critical gaps and calculate your risk score.
                </p>
              </div>

              <div className="space-y-4 text-center">
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-teal-100">
                  <span className="text-2xl font-bold text-teal-600">3</span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900">Action Plan</h3>
                <p className="text-gray-600">
                  Get prioritized recommendations with clear next steps to address your most
                  critical compliance gaps first.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* What You'll Discover Section */}
      <div className="bg-gray-50 py-16">
        <div className="container mx-auto px-4">
          <div className="mx-auto max-w-4xl">
            <div className="mb-12 space-y-4 text-center">
              <h2 className="text-3xl font-bold text-gray-900">What You'll Discover</h2>
              <p className="text-lg text-gray-600">
                Get actionable insights that help you prioritize your compliance efforts
              </p>
            </div>

            <div className="grid gap-8 md:grid-cols-2">
              <Card>
                <CardContent className="space-y-4 p-6">
                  <div className="flex items-center space-x-3">
                    <Shield className="h-6 w-6 text-red-500" />
                    <h3 className="text-lg font-semibold text-gray-900">
                      Critical Compliance Gaps
                    </h3>
                  </div>
                  <ul className="space-y-2 text-sm text-gray-600">
                    <li className="flex items-center space-x-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>Missing data processing records (GDPR)</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>Incomplete risk assessments (ISO 27001)</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>Missing incident response procedures</span>
                    </li>
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardContent className="space-y-4 p-6">
                  <div className="flex items-center space-x-3">
                    <Zap className="h-6 w-6 text-teal-500" />
                    <h3 className="text-lg font-semibold text-gray-900">
                      Personalized Recommendations
                    </h3>
                  </div>
                  <ul className="space-y-2 text-sm text-gray-600">
                    <li className="flex items-center space-x-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>Priority action items with timelines</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>Resource requirements and costs</span>
                    </li>
                    <li className="flex items-center space-x-2">
                      <CheckCircle className="h-4 w-4 text-green-500" />
                      <span>Step-by-step implementation guides</span>
                    </li>
                  </ul>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-teal-600 py-16">
        <div className="container mx-auto px-4 text-center">
          <div className="mx-auto max-w-3xl space-y-6">
            <h2 className="text-3xl font-bold text-white">
              Ready to Discover Your Compliance Gaps?
            </h2>
            <p className="text-xl text-teal-100">
              Join thousands of businesses who have used our AI assessment to improve their
              compliance posture.
            </p>
            <div className="pt-4">
              <a
                href="#assessment-form"
                className="inline-flex items-center rounded-lg bg-white px-8 py-3 font-semibold text-teal-600 transition-colors hover:bg-gray-100"
              >
                Start Your Free Assessment
                <ArrowRight className="ml-2 h-5 w-5" />
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
