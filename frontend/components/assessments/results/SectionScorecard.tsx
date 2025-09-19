'use client';

import { ChevronDown, ChevronUp, CheckCircle, AlertTriangle, XCircle, Clock } from 'lucide-react';
import * as React from 'react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import type { AssessmentSection, Answer, Gap, Recommendation } from '@/lib/assessment-engine/types';
import type { SectionScoreDetail as SharedSectionScoreDetail } from '@/types/assessment-results';

// Extend the shared type for this component's specific needs
interface SectionQuestionDetail {
  questionId: string;
  questionText: string;
  answer: Answer | null;
  score: number;
  maxScore: number;
  isCorrect: boolean;
  explanation?: string;
}

interface SectionScorecardData extends Omit<SharedSectionScoreDetail, 'sectionId' | 'sectionName' | 'sectionDescription' | 'percentage'> {
  section: AssessmentSection;
  percentage?: number;
  questionsAnswered: number;
  strengths: string[];
  improvements: string[];
  questionDetails: SectionQuestionDetail[];
  relatedGaps: Gap[];
  relatedRecommendations: Recommendation[];
}

interface SectionScorecardProps {
  scorecard: SectionScorecardData;
  className?: string;
  defaultExpanded?: boolean;
  isEstimated?: boolean;
}

const getRiskLevelColor = (riskLevel: SectionScorecardData['riskLevel']) => {
  switch (riskLevel) {
    case 'low':
      return 'text-green-700 bg-green-50 border-green-200';
    case 'medium':
      return 'text-yellow-700 bg-yellow-50 border-yellow-200';
    case 'high':
      return 'text-orange-700 bg-orange-50 border-orange-200';
    case 'critical':
      return 'text-red-700 bg-red-50 border-red-200';
    default:
      return 'text-gray-700 bg-gray-50 border-gray-200';
  }
};

const getCompletionStatusColor = (status: SectionScorecardData['completionStatus']) => {
  switch (status) {
    case 'complete':
      return 'text-green-700 bg-green-50';
    case 'partial':
      return 'text-yellow-700 bg-yellow-50';
    case 'not_started':
      return 'text-gray-700 bg-gray-50';
    default:
      return 'text-gray-700 bg-gray-50';
  }
};

const getCompletionStatusIcon = (status: SectionScorecardData['completionStatus']) => {
  switch (status) {
    case 'complete':
      return <CheckCircle className="h-4 w-4" />;
    case 'partial':
      return <Clock className="h-4 w-4" />;
    case 'not_started':
      return <XCircle className="h-4 w-4" />;
    default:
      return <Clock className="h-4 w-4" />;
  }
};

const getRiskLevelIcon = (riskLevel: SectionScorecardData['riskLevel']) => {
  switch (riskLevel) {
    case 'low':
      return <CheckCircle className="h-4 w-4" />;
    case 'medium':
      return <AlertTriangle className="h-4 w-4" />;
    case 'high':
      return <AlertTriangle className="h-4 w-4" />;
    case 'critical':
      return <XCircle className="h-4 w-4" />;
    default:
      return <AlertTriangle className="h-4 w-4" />;
  }
};

const Badge: React.FC<{
  children: React.ReactNode;
  variant?: 'default' | 'secondary' | 'outline';
  className?: string;
}> = ({ children, variant = 'default', className }) => {
  const baseClasses = 'inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors';
  const variantClasses = {
    default: 'bg-purple-100 text-purple-800',
    secondary: 'bg-gray-100 text-gray-800',
    outline: 'border border-gray-200 bg-white text-gray-800',
  };

  return (
    <span className={cn(baseClasses, variantClasses[variant], className)}>
      {children}
    </span>
  );
};

export const SectionScorecard: React.FC<SectionScorecardProps> = ({
  scorecard,
  className,
  defaultExpanded = false,
  isEstimated = false,
}) => {
  const [isExpanded, setIsExpanded] = React.useState(defaultExpanded);
  const [activeTab, setActiveTab] = React.useState<'questions' | 'findings' | 'recommendations'>('questions');

  const scorePercentage = scorecard.percentage ?? (scorecard.maxScore > 0 ? Math.round((scorecard.score / scorecard.maxScore) * 100) : 0);
  const completionPercentage = scorecard.totalQuestions > 0 
    ? Math.round((scorecard.questionsAnswered / scorecard.totalQuestions) * 100) 
    : 0;

  const handleToggleExpanded = () => {
    setIsExpanded(!isExpanded);
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleToggleExpanded();
    }
  };

  return (
    <Card className={cn('transition-all duration-200', className)}>
      <CardHeader className="pb-4">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-2">
              <CardTitle className="text-lg font-semibold text-gray-900">
                {scorecard.section.title}
              </CardTitle>
              {isEstimated && (
                <span className="px-2 py-0.5 text-xs font-medium text-amber-700 bg-amber-100 border border-amber-200 rounded" title="Detailed breakdown is estimated based on overall scores">
                  Estimated
                </span>
              )}
            </div>
            {scorecard.section.description && (
              <p className="text-sm text-gray-600 mb-3">
                {scorecard.section.description}
              </p>
            )}
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleToggleExpanded}
            onKeyDown={handleKeyDown}
            aria-expanded={isExpanded}
            aria-label={`${isExpanded ? 'Collapse' : 'Expand'} ${scorecard.section.title} details`}
            className="ml-4 shrink-0"
          >
            {isExpanded ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Score Display */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Score</span>
              <span className="text-2xl font-bold text-purple-700">
                {scorePercentage}%
              </span>
            </div>
            <Progress 
              value={scorePercentage} 
              className="h-2"
              indicatorClassName={cn(
                scorePercentage >= 80 ? 'bg-green-500' :
                scorePercentage >= 60 ? 'bg-yellow-500' :
                scorePercentage >= 40 ? 'bg-orange-500' : 'bg-red-500'
              )}
              aria-label={`Section score: ${scorePercentage}%`}
            />
            <p className="text-xs text-gray-500">
              {scorecard.score} of {scorecard.maxScore} points
            </p>
          </div>

          {/* Completion Status */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Progress</span>
              <Badge className={getCompletionStatusColor(scorecard.completionStatus)}>
                {getCompletionStatusIcon(scorecard.completionStatus)}
                {scorecard.completionStatus.replace('_', ' ')}
              </Badge>
            </div>
            <Progress 
              value={completionPercentage} 
              className="h-2"
              aria-label={`Section completion: ${completionPercentage}%`}
            />
            <p className="text-xs text-gray-500">
              {scorecard.questionsAnswered} of {scorecard.totalQuestions} questions
            </p>
          </div>

          {/* Risk Level */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Risk Level</span>
              <Badge className={getRiskLevelColor(scorecard.riskLevel)}>
                {getRiskLevelIcon(scorecard.riskLevel)}
                {scorecard.riskLevel}
              </Badge>
            </div>
            <div className="text-xs text-gray-500">
              {scorecard.relatedGaps.length} gap{scorecard.relatedGaps.length !== 1 ? 's' : ''} identified
            </div>
          </div>
        </div>
      </CardHeader>

      {isExpanded && (
        <CardContent className="pt-0">
          {/* Tab Navigation */}
          <div className="border-b border-gray-200 mb-4">
            <nav className="-mb-px flex space-x-8" aria-label="Section details tabs">
              {[
                { key: 'questions', label: 'Questions', count: scorecard.questionDetails.length },
                { key: 'findings', label: 'Key Findings', count: scorecard.strengths.length + scorecard.improvements.length },
                { key: 'recommendations', label: 'Recommendations', count: scorecard.relatedRecommendations.length },
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as typeof activeTab)}
                  className={cn(
                    'whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm transition-colors',
                    activeTab === tab.key
                      ? 'border-purple-500 text-purple-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  )}
                  aria-selected={activeTab === tab.key}
                  role="tab"
                >
                  {tab.label}
                  {tab.count > 0 && (
                    <span className="ml-2 bg-gray-100 text-gray-600 py-0.5 px-2 rounded-full text-xs">
                      {tab.count}
                    </span>
                  )}
                </button>
              ))}
            </nav>
          </div>

          {/* Tab Content */}
          <div role="tabpanel" aria-labelledby={`${activeTab}-tab`}>
            {activeTab === 'questions' && (
              <div className="space-y-4">
                {scorecard.questionDetails.map((detail) => (
                  <div
                    key={detail.questionId}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-medium text-gray-900 flex-1">
                        {detail.questionText}
                      </h4>
                      <div className="flex items-center gap-2 ml-4">
                        <Badge variant={detail.isCorrect ? 'default' : 'outline'}>
                          {detail.score}/{detail.maxScore}
                        </Badge>
                        {detail.isCorrect ? (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-500" />
                        )}
                      </div>
                    </div>
                    {detail.answer && (
                      <div className="text-sm text-gray-600 mb-2">
                        <span className="font-medium">Answer: </span>
                        {typeof detail.answer.value === 'string' 
                          ? detail.answer.value 
                          : JSON.stringify(detail.answer.value)
                        }
                      </div>
                    )}
                    {detail.explanation && (
                      <div className="text-sm text-gray-500">
                        {detail.explanation}
                      </div>
                    )}
                  </div>
                ))}
                {scorecard.questionDetails.length === 0 && (
                  <p className="text-gray-500 text-center py-8">
                    No question details available for this section.
                  </p>
                )}
              </div>
            )}

            {activeTab === 'findings' && (
              <div className="space-y-6">
                {scorecard.strengths.length > 0 && (
                  <div>
                    <h4 className="font-medium text-green-700 mb-3 flex items-center gap-2">
                      <CheckCircle className="h-4 w-4" />
                      Strengths
                    </h4>
                    <ul className="space-y-2">
                      {scorecard.strengths.map((strength, index) => (
                        <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                          <div className="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 shrink-0" />
                          {strength}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {scorecard.improvements.length > 0 && (
                  <div>
                    <h4 className="font-medium text-orange-700 mb-3 flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4" />
                      Areas for Improvement
                    </h4>
                    <ul className="space-y-2">
                      {scorecard.improvements.map((improvement, index) => (
                        <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
                          <div className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 shrink-0" />
                          {improvement}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {scorecard.strengths.length === 0 && scorecard.improvements.length === 0 && (
                  <p className="text-gray-500 text-center py-8">
                    No key findings available for this section.
                  </p>
                )}
              </div>
            )}

            {activeTab === 'recommendations' && (
              <div className="space-y-4">
                {scorecard.relatedRecommendations.map((recommendation) => (
                  <div
                    key={recommendation.id}
                    className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h4 className="font-medium text-gray-900 flex-1">
                        {recommendation.title}
                      </h4>
                      <Badge 
                        variant="outline"
                        className={cn(
                          recommendation.priority === 'immediate' ? 'border-red-200 text-red-700 bg-red-50' :
                          recommendation.priority === 'short_term' ? 'border-orange-200 text-orange-700 bg-orange-50' :
                          recommendation.priority === 'medium_term' ? 'border-yellow-200 text-yellow-700 bg-yellow-50' :
                          'border-green-200 text-green-700 bg-green-50'
                        )}
                      >
                        {recommendation.priority.replace('_', ' ')}
                      </Badge>
                    </div>
                    <p className="text-sm text-gray-600 mb-3">
                      {recommendation.description}
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-gray-500">
                      <div>
                        <span className="font-medium">Effort: </span>
                        {recommendation.estimatedEffort}
                      </div>
                      <div>
                        <span className="font-medium">Impact: </span>
                        {recommendation.impact}
                      </div>
                      <div>
                        <span className="font-medium">Time: </span>
                        {recommendation.estimatedTime}
                      </div>
                    </div>
                  </div>
                ))}
                {scorecard.relatedRecommendations.length === 0 && (
                  <p className="text-gray-500 text-center py-8">
                    No recommendations available for this section.
                  </p>
                )}
              </div>
            )}
          </div>
        </CardContent>
      )}
    </Card>
  );
};

export default SectionScorecard;