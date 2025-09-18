'use client';

import { useState } from 'react';
import { Calendar, Download, FileText, TrendingUp, Users, CheckCircle, Clock, Target } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ComplianceScoreGauge } from './compliance-score-gauge';
import { GapAnalysisChart } from './gap-analysis-chart';
import { RecommendationsList } from './recommendations-list';
import { TrendAnalysisChart } from './TrendAnalysisChart';
import { SectionScorecard } from './SectionScorecard';
import { ExportButton } from './ExportButton';
import { AssessmentResult, Gap, Recommendation } from '@/lib/assessment-engine/types';
import { AssessmentResultsResponse } from '@/types/freemium';
import { TrendDataPoint, SectionScoreDetail } from '@/types/assessment-results';

// Use SectionScoreDetail but keep a type alias for backward compatibility
type SectionScore = {
  id: string;
  name: string;
  score: number;
  questionsAnswered: number;
  totalQuestions: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  status: 'complete' | 'partial' | 'not_started';
  strengths: string[];
  improvements: string[];
};

interface DetailedResultsDashboardProps {
  results: AssessmentResult;  // Only accept AssessmentResult format
  sectionDetails?: SectionScore[];
  trendData?: TrendDataPoint[];

  isExporting?: boolean;
  className?: string;
}


export function DetailedResultsDashboard({
  results,
  sectionDetails = [],
  trendData = [],

  isExporting = false,
  className = ''
}: DetailedResultsDashboardProps) {
  const [activeTab, setActiveTab] = useState('overview');
  
  // Directly use results (AssessmentResult format)
  const { overallScore, gaps, recommendations, sectionScores, completedAt } = results;
  const completionPercentage = 100; // AssessmentResult is always complete

  // Generate default section details if not provided
  // Use deterministic counts based on completion percentage and section scores
  const defaultSectionDetails: SectionScore[] = Object.entries(sectionScores).map(([id, score]) => {
    // NOTE: These are estimated values when actual section data is not available
    // In production, these should be derived from actual assessment framework data
    // Consider showing an "estimated" badge in the UI for these values
    const sectionCount = Object.keys(sectionScores).length || 5; // Default to 5 sections
    const totalQuestionsPerSection = 10; // Estimated standard questions per section

    // Calculate questions answered based on completion percentage and score
    const questionsAnswered = completionPercentage < 100
      ? Math.floor((completionPercentage / 100) * totalQuestionsPerSection)
      : Math.round((score / 100) * totalQuestionsPerSection);

    return {
      id,
      name: id.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase()),
      score,
      questionsAnswered,
      totalQuestions: totalQuestionsPerSection,
      riskLevel: score >= 80 ? 'low' : score >= 60 ? 'medium' : score >= 40 ? 'high' : 'critical',
      status: completionPercentage >= 100 ? 'complete' : completionPercentage > 50 ? 'partial' : 'not_started',
      strengths: score >= 60 ? ['Good implementation practices', 'Adequate documentation'] : [],
      improvements: score < 80 ? ['Enhanced monitoring needed', 'Regular reviews required'] : []
    };
  });

  const sectionsToDisplay = sectionDetails.length > 0 ? sectionDetails : defaultSectionDetails;

  // Calculate summary statistics
  const totalQuestions = sectionsToDisplay.reduce((sum, section) => sum + section.totalQuestions, 0);
  const answeredQuestions = sectionsToDisplay.reduce((sum, section) => sum + section.questionsAnswered, 0);
  const nextAssessmentDate = new Date(completedAt);
  nextAssessmentDate.setMonth(nextAssessmentDate.getMonth() + 6);

  // Prepare gap analysis data
  const gapAnalysisData = sectionsToDisplay.map(section => ({
    name: section.name,
    score: section.score
  }));

  // Transform recommendations for display
  const displayRecommendations = recommendations.map(rec => ({
    id: rec.id,
    text: rec.description,
    priority: rec.priority === 'immediate' ? 'High' : 
             rec.priority === 'short_term' ? 'High' :
             rec.priority === 'medium_term' ? 'Medium' : 'Low'
  }));

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header with Export Buttons */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Assessment Results</h1>
          <p className="text-muted-foreground">
            Completed on {completedAt.toLocaleDateString()}
          </p>
        </div>
        <ExportButton
          results={results}
          trendData={trendData}
        />
      </div>

      {/* Summary Statistics Panel */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-teal-600" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Questions Answered</p>
                <p className="text-2xl font-bold">{answeredQuestions}/{totalQuestions}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2">
              <Target className="h-5 w-5 text-teal-600" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Completion</p>
                <p className="text-2xl font-bold">{Math.round(completionPercentage)}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2">
              <Calendar className="h-5 w-5 text-teal-600" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Assessment Date</p>
                <p className="text-sm font-bold">{completedAt.toLocaleDateString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-2">
              <Clock className="h-5 w-5 text-teal-600" />
              <div>
                <p className="text-sm font-medium text-muted-foreground">Next Assessment</p>
                <p className="text-sm font-bold">{nextAssessmentDate.toLocaleDateString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Dashboard Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="sections">Section Details</TabsTrigger>
          <TabsTrigger value="gaps">Gaps & Recommendations</TabsTrigger>
          <TabsTrigger value="trends">Trends</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Compliance Score Gauge */}
            <Card>
              <CardHeader>
                <CardTitle>Overall Compliance Score</CardTitle>
                <CardDescription>
                  Your current compliance level based on assessment responses
                </CardDescription>
              </CardHeader>
              <CardContent className="flex justify-center">
                <ComplianceScoreGauge score={overallScore} />
              </CardContent>
            </Card>

            {/* Quick Stats */}
            <Card>
              <CardHeader>
                <CardTitle>Assessment Summary</CardTitle>
                <CardDescription>Key metrics from your assessment</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Risk Level</span>
                  <span className={`text-sm font-bold ${
                    overallScore >= 80 ? 'text-green-600' :
                    overallScore >= 60 ? 'text-yellow-600' :
                    'text-red-600'
                  }`}>
                    {overallScore >= 80 ? 'Low' : overallScore >= 60 ? 'Medium' : 'High'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Critical Gaps</span>
                  <span className="text-sm font-bold text-red-600">
                    {gaps.filter(gap => gap.severity === 'critical').length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium">High Priority Items</span>
                  <span className="text-sm font-bold text-orange-600">
                    {recommendations.filter(rec => rec.priority === 'immediate' || rec.priority === 'short_term').length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm font-medium">Sections Completed</span>
                  <span className="text-sm font-bold">
                    {sectionsToDisplay.filter(s => s.status === 'complete').length}/{sectionsToDisplay.length}
                  </span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Gap Analysis Overview */}
          {gapAnalysisData.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Section Performance Overview</CardTitle>
                <CardDescription>
                  Performance breakdown across different assessment areas
                </CardDescription>
              </CardHeader>
              <CardContent>
                <GapAnalysisChart data={gapAnalysisData} />
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Section Details Tab */}
        <TabsContent value="sections" className="space-y-6">
          <div className="space-y-6">
            {sectionsToDisplay.map((section) => {
              // Transform section data to SectionScorecard format
              const scorecardData = {
                section: {
                  id: section.id,
                  title: section.name,
                  description: `Assessment section covering ${section.name.toLowerCase()} compliance requirements`,
                  questions: []
                },
                score: section.score,
                maxScore: 100,
                questionsAnswered: section.questionsAnswered,
                totalQuestions: section.totalQuestions,
                completionStatus: section.status,
                riskLevel: section.riskLevel,
                strengths: section.strengths,
                improvements: section.improvements,
                questionDetails: [],
                relatedGaps: gaps.filter(gap => gap.section === section.id || gap.category === section.name),
                relatedRecommendations: recommendations.filter(rec => rec.category === section.name)
              };
              
              return (
                <SectionScorecard
                  key={section.id}
                  scorecard={scorecardData}
                  defaultExpanded={false}
                />
              );
            })}
          </div>
        </TabsContent>

        {/* Gaps & Recommendations Tab */}
        <TabsContent value="gaps" className="space-y-6">
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Gap Analysis Chart */}
            <Card>
              <CardHeader>
                <CardTitle>Gap Analysis</CardTitle>
                <CardDescription>
                  Areas requiring attention based on your responses
                </CardDescription>
              </CardHeader>
              <CardContent>
                <GapAnalysisChart data={gapAnalysisData} />
              </CardContent>
            </Card>

            {/* Gap Summary */}
            <Card>
              <CardHeader>
                <CardTitle>Gap Summary</CardTitle>
                <CardDescription>Breakdown of identified compliance gaps</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {['critical', 'high', 'medium', 'low'].map((severity) => {
                  const count = gaps.filter(gap => gap.severity === severity).length;
                  return (
                    <div key={severity} className="flex justify-between items-center">
                      <span className="text-sm font-medium capitalize">{severity} Risk</span>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-bold">{count}</span>
                        <div className={`h-2 w-8 rounded-full ${
                          severity === 'critical' ? 'bg-red-500' :
                          severity === 'high' ? 'bg-orange-500' :
                          severity === 'medium' ? 'bg-yellow-500' :
                          'bg-green-500'
                        }`} />
                      </div>
                    </div>
                  );
                })}
              </CardContent>
            </Card>
          </div>

          {/* Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle>Recommendations</CardTitle>
              <CardDescription>
                Prioritized actions to improve your compliance posture
              </CardDescription>
            </CardHeader>
            <CardContent>
              <RecommendationsList recommendations={displayRecommendations} />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Trends Tab */}
        <TabsContent value="trends" className="space-y-6">
          {trendData.length > 0 ? (
            <Card>
              <CardHeader>
                <CardTitle>Score Trends</CardTitle>
                <CardDescription>
                  Track your compliance score progress over time
                </CardDescription>
              </CardHeader>
              <CardContent>
                <TrendAnalysisChart
                  data={trendData}
                />
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>No Historical Data</CardTitle>
                <CardDescription>
                  Complete more assessments to see trend analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-center py-12">
                  <TrendingUp className="h-12 w-12 text-muted-foreground/50 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Start Building Your Trend History</h3>
                  <p className="text-muted-foreground mb-4">
                    Take regular assessments to track your compliance progress over time.
                  </p>
                  <Button variant="outline">
                    Schedule Next Assessment
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}