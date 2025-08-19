'use client';

import React from 'react';
import {
  AlertTriangle,
  CheckCircle,
  Clock,
  FileText,
  Shield,
  Target,
  TrendingUp,
  Users,
  Zap,
  ChevronRight,
  ExternalLink,
  Download,
} from 'lucide-react';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { cn } from '@/lib/utils';

import type {
  AIResponseType,
  AssessmentAnalysisResponse,
  ComplianceGap,
  ComplianceInsight,
  ComplianceMessageRendererProps,
  ComplianceRecommendation,
  EvidenceRequirement,
  GapAnalysisResponse,
  GuidanceResponse,
  RecommendationsResponse,
  SeverityLevel,
} from '@/types/ai-responses';

// =====================================================================
// Severity and Priority Styling Utilities
// =====================================================================

const getSeverityColor = (severity: SeverityLevel) => {
  switch (severity) {
    case 'critical':
      return 'destructive';
    case 'high':
      return 'destructive';
    case 'medium':
      return 'pending';
    case 'low':
      return 'secondary';
    default:
      return 'secondary';
  }
};

const getSeverityIcon = (severity: SeverityLevel) => {
  switch (severity) {
    case 'critical':
      return <AlertTriangle className="h-4 w-4 text-destructive" />;
    case 'high':
      return <AlertTriangle className="h-4 w-4 text-destructive" />;
    case 'medium':
      return <Clock className="h-4 w-4 text-yellow-600" />;
    case 'low':
      return <CheckCircle className="h-4 w-4 text-green-600" />;
    default:
      return <Shield className="h-4 w-4" />;
  }
};

const getEffortColor = (effort: string) => {
  switch (effort) {
    case 'extensive':
      return 'destructive';
    case 'high':
      return 'pending';
    case 'medium':
      return 'secondary';
    case 'low':
      return 'outline';
    case 'minimal':
      return 'outline';
    default:
      return 'secondary';
  }
};

// =====================================================================
// Gap Analysis Components
// =====================================================================

interface GapCardProps {
  gap: ComplianceGap;
  onActionClick?: (action: string, data: any) => void;
}

function GapCard({ gap, onActionClick }: GapCardProps) {
  return (
    <Card className="transition-all hover:shadow-md">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-2">
            {getSeverityIcon(gap.severity)}
            <CardTitle className="text-base">{gap.title}</CardTitle>
          </div>
          <Badge variant={getSeverityColor(gap.severity)}>{gap.severity}</Badge>
        </div>
        <CardDescription className="text-sm">{gap.framework_reference}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground">{gap.description}</p>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-medium text-muted-foreground">Current State</p>
            <p className="text-sm">{gap.current_state}</p>
          </div>
          <div>
            <p className="text-xs font-medium text-muted-foreground">Target State</p>
            <p className="text-sm">{gap.target_state}</p>
          </div>
        </div>

        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              <Target className="h-3 w-3" />
              <span>Impact: {Math.round(gap.business_impact_score * 100)}%</span>
            </div>
            <Badge variant={getEffortColor(gap.estimated_effort)}>{gap.estimated_effort}</Badge>
          </div>
          {gap.regulatory_requirement && (
            <Badge variant="secondary" className="text-xs">
              <Shield className="mr-1 h-3 w-3" />
              Required
            </Badge>
          )}
        </div>

        {gap.stakeholders && gap.stakeholders.length > 0 && (
          <div>
            <p className="text-xs font-medium text-muted-foreground">Stakeholders</p>
            <div className="mt-1 flex flex-wrap gap-1">
              {gap.stakeholders.map((stakeholder, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  <Users className="mr-1 h-3 w-3" />
                  {stakeholder}
                </Badge>
              ))}
            </div>
          </div>
        )}

        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            className="text-xs"
            onClick={() => onActionClick?.('view_gap_details', gap)}
          >
            View Details
            <ChevronRight className="ml-1 h-3 w-3" />
          </Button>
          <Button
            size="sm"
            variant="outline"
            className="text-xs"
            onClick={() => onActionClick?.('create_evidence_task', gap)}
          >
            <FileText className="mr-1 h-3 w-3" />
            Create Task
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

interface GapAnalysisRendererProps {
  data: GapAnalysisResponse;
  onActionClick?: (action: string, data: any) => void;
}

function GapAnalysisRenderer({ data, onActionClick }: GapAnalysisRendererProps) {
  return (
    <div className="space-y-4">
      {/* Summary Header */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-yellow-600" />
              Gap Analysis Results
            </CardTitle>
            <Badge variant={getSeverityColor(data.overall_risk_level)}>
              {data.overall_risk_level} Risk
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm">{data.summary}</p>
          
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-destructive">{data.critical_gap_count}</p>
              <p className="text-xs text-muted-foreground">Critical Gaps</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-yellow-600">{data.medium_high_gap_count}</p>
              <p className="text-xs text-muted-foreground">High/Medium Gaps</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">
                {Math.round(data.compliance_percentage)}%
              </p>
              <p className="text-xs text-muted-foreground">Compliant</p>
            </div>
          </div>

          <div>
            <div className="flex items-center justify-between text-sm">
              <span>Compliance Progress</span>
              <span>{Math.round(data.compliance_percentage)}%</span>
            </div>
            <Progress value={data.compliance_percentage} className="mt-2" />
          </div>
        </CardContent>
      </Card>

      {/* Gaps Grid */}
      <div className="space-y-3">
        <h4 className="text-sm font-medium">Identified Gaps ({data.gaps.length})</h4>
        <div className="grid gap-3">
          {data.gaps.slice(0, 5).map((gap, index) => (
            <GapCard key={gap.id || index} gap={gap} onActionClick={onActionClick} />
          ))}
          {data.gaps.length > 5 && (
            <Button
              variant="outline"
              className="w-full"
              onClick={() => onActionClick?.('view_all_gaps', data.gaps)}
            >
              View All {data.gaps.length} Gaps
            </Button>
          )}
        </div>
      </div>

      {/* Next Steps */}
      {data.next_steps.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-4 w-4" />
              Recommended Next Steps
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {data.next_steps.map((step, index) => (
                <li key={index} className="flex items-start gap-2 text-sm">
                  <ChevronRight className="mt-0.5 h-3 w-3 text-yellow-600" />
                  {step}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// =====================================================================
// Recommendations Components
// =====================================================================

interface RecommendationCardProps {
  recommendation: ComplianceRecommendation;
  onActionClick?: (action: string, data: any) => void;
}

function RecommendationCard({ recommendation, onActionClick }: RecommendationCardProps) {
  const priorityColor = recommendation.priority === 'urgent' ? 'destructive' : 
                       recommendation.priority === 'high' ? 'pending' : 'secondary';

  return (
    <Card className="transition-all hover:shadow-md">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <CardTitle className="text-base">{recommendation.title}</CardTitle>
          <Badge variant={priorityColor}>{recommendation.priority}</Badge>
        </div>
        <CardDescription>{recommendation.category}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-muted-foreground">{recommendation.description}</p>
        
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-xs font-medium text-muted-foreground">Timeline</p>
            <p>{recommendation.implementation_timeline}</p>
          </div>
          <div>
            <p className="text-xs font-medium text-muted-foreground">Effort</p>
            <Badge variant={getEffortColor(recommendation.effort_estimate)}>
              {recommendation.effort_estimate}
            </Badge>
          </div>
        </div>

        {recommendation.framework_references.length > 0 && (
          <div>
            <p className="text-xs font-medium text-muted-foreground">Frameworks</p>
            <div className="mt-1 flex flex-wrap gap-1">
              {recommendation.framework_references.map((framework, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {framework}
                </Badge>
              ))}
            </div>
          </div>
        )}

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-1 text-sm">
            <TrendingUp className="h-3 w-3" />
            Impact: {Math.round(recommendation.impact_score * 100)}%
          </div>
          {recommendation.automation_potential && (
            <div className="flex items-center gap-1 text-sm text-blue-700">
              <Zap className="h-3 w-3" />
              {Math.round(recommendation.automation_potential * 100)}% automatable
            </div>
          )}
        </div>

        <div className="flex gap-2">
          <Button
            size="sm"
            className="bg-yellow-500 text-blue-900 hover:bg-yellow-600"
            onClick={() => onActionClick?.('implement_recommendation', recommendation)}
          >
            Implement
            <ChevronRight className="ml-1 h-3 w-3" />
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => onActionClick?.('view_recommendation_details', recommendation)}
          >
            Details
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

interface RecommendationsRendererProps {
  data: RecommendationsResponse;
  onActionClick?: (action: string, data: any) => void;
}

function RecommendationsRenderer({ data, onActionClick }: RecommendationsRendererProps) {
  return (
    <div className="space-y-4">
      {/* Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5 text-yellow-600" />
            Implementation Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm">{data.prioritization_rationale}</p>
          <div className="text-sm">
            <strong>Timeline:</strong> {data.timeline_overview}
          </div>
        </CardContent>
      </Card>

      {/* Quick Wins */}
      {data.quick_wins && data.quick_wins.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-green-600" />
              Quick Wins
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-1">
              {data.quick_wins.map((win, index) => (
                <li key={index} className="flex items-start gap-2 text-sm">
                  <CheckCircle className="mt-0.5 h-3 w-3 text-green-600" />
                  {win}
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Recommendations Grid */}
      <div className="space-y-3">
        <h4 className="text-sm font-medium">Detailed Recommendations ({data.recommendations.length})</h4>
        <div className="grid gap-3">
          {data.recommendations.slice(0, 3).map((rec, index) => (
            <RecommendationCard
              key={rec.id || index}
              recommendation={rec}
              onActionClick={onActionClick}
            />
          ))}
          {data.recommendations.length > 3 && (
            <Button
              variant="outline"
              className="w-full"
              onClick={() => onActionClick?.('view_all_recommendations', data.recommendations)}
            >
              View All {data.recommendations.length} Recommendations
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}

// =====================================================================
// Main ComplianceMessageRenderer Component
// =====================================================================

export function ComplianceMessageRenderer({
  content,
  metadata,
  onActionClick,
}: ComplianceMessageRendererProps) {
  // Try to parse content as structured AI response
  const tryParseStructuredResponse = (): {
    type: AIResponseType;
    data: any;
  } | null => {
    try {
      // Check if it's already parsed JSON
      if (typeof content === 'object') {
        return content as any;
      }

      // Check metadata first
      if (metadata?.response_type) {
        const parsed = JSON.parse(content);
        return {
          type: metadata.response_type,
          data: parsed,
        };
      }

      // Try to parse as JSON and infer type
      const parsed = JSON.parse(content);
      
      // Detect response type by structure
      if (parsed.gaps && parsed.overall_risk_level) {
        return { type: 'gap_analysis', data: parsed as GapAnalysisResponse };
      }
      if (parsed.recommendations && parsed.implementation_plan) {
        return { type: 'recommendations', data: parsed as RecommendationsResponse };
      }
      if (parsed.gaps && parsed.recommendations && parsed.risk_assessment) {
        return { type: 'assessment_analysis', data: parsed as AssessmentAnalysisResponse };
      }
      if (parsed.guidance && parsed.confidence_score) {
        return { type: 'guidance', data: parsed as GuidanceResponse };
      }
      
      return null;
    } catch {
      return null;
    }
  };

  const structuredResponse = tryParseStructuredResponse();

  // If not structured, render as regular text
  if (!structuredResponse) {
    return (
      <div className="space-y-2 text-sm">
        {content.split('\n\n').map((paragraph, idx) => (
          <p key={idx}>{paragraph}</p>
        ))}
      </div>
    );
  }

  // Render structured response
  const { type, data } = structuredResponse;

  switch (type) {
    case 'gap_analysis':
      return <GapAnalysisRenderer data={data} onActionClick={onActionClick} />;
      
    case 'recommendations':
      return <RecommendationsRenderer data={data} onActionClick={onActionClick} />;
      
    case 'assessment_analysis':
      // For now, render the executive summary with a link to full analysis
      return (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-blue-900" />
                Assessment Analysis
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm">{data.executive_summary}</p>
              <div className="grid grid-cols-2 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-blue-900">
                    {Math.round(data.compliance_metrics.overall_compliance_score)}%
                  </p>
                  <p className="text-xs text-muted-foreground">Compliance Score</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-yellow-600">
                    {Math.round(data.confidence_score * 100)}%
                  </p>
                  <p className="text-xs text-muted-foreground">Confidence</p>
                </div>
              </div>
              <Button
                className="w-full bg-blue-900 text-yellow-500 hover:bg-blue-800"
                onClick={() => onActionClick?.('view_full_analysis', data)}
              >
                <FileText className="mr-2 h-4 w-4" />
                View Full Analysis
              </Button>
            </CardContent>
          </Card>
        </div>
      );
      
    case 'guidance':
      return (
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-blue-900" />
                Compliance Guidance
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm">{data.guidance}</p>
              
              {data.best_practices && data.best_practices.length > 0 && (
                <div>
                  <h5 className="text-sm font-medium text-green-600 mb-2">Best Practices</h5>
                  <ul className="space-y-1">
                    {data.best_practices.map((practice: string, index: number) => (
                      <li key={index} className="flex items-start gap-2 text-sm">
                        <CheckCircle className="mt-0.5 h-3 w-3 text-green-600" />
                        {practice}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {data.follow_up_suggestions.length > 0 && (
                <div>
                  <h5 className="text-sm font-medium mb-2">Next Steps</h5>
                  <div className="flex flex-wrap gap-2">
                    {data.follow_up_suggestions.map((suggestion: string, index: number) => (
                      <Button
                        key={index}
                        size="sm"
                        variant="outline"
                        onClick={() => onActionClick?.('ask_followup', suggestion)}
                      >
                        {suggestion}
                      </Button>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      );
      
    default:
      // Fallback to text rendering
      return (
        <div className="space-y-2 text-sm">
          {content.split('\n\n').map((paragraph, idx) => (
            <p key={idx}>{paragraph}</p>
          ))}
        </div>
      );
  }
}