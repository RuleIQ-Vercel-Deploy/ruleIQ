'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Progress } from '@/components/ui/progress';
import {
  Brain,
  Shield,
  AlertTriangle,
  CheckCircle,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Target,
  FileText,
  Network,
  Clock,
  TrendingUp
} from 'lucide-react';
import { cn } from '@/lib/utils';
import type { 
  ComplianceQueryResponse, 
  Evidence, 
  ActionPlan, 
  RiskAssessment,
  GraphAnalysis 
} from '@/types/iq-agent';

interface IQComplianceResponseProps {
  response: ComplianceQueryResponse;
  className?: string;
}

export function IQComplianceResponse({ response, className }: IQComplianceResponseProps) {
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    evidence: false,
    actions: false,
    risks: false,
    graph: false
  });

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const getTrustLevelColor = (trustLevel: string) => {
    switch (trustLevel) {
      case 'helper': return 'bg-blue-500';
      case 'advisor': return 'bg-green-500';
      case 'partner': return 'bg-purple-500';
      default: return 'bg-gray-500';
    }
  };

  const getRiskColor = (level: string) => {
    switch (level.toLowerCase()) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className={cn('space-y-4', className)}>
      {/* Main Summary Card */}
      <Card className="border-l-4 border-l-blue-500">
        <CardHeader className="pb-3">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-blue-600" />
              <CardTitle className="text-lg">IQ Agent Analysis</CardTitle>
            </div>
            <div className="flex items-center gap-2 ml-auto">
              <Badge variant="secondary" className="text-xs">
                {response.trust_level} Mode
              </Badge>
              <Badge variant="outline" className="text-xs">
                {response.confidence_score}% Confidence
              </Badge>
              <Badge variant="outline" className="text-xs">
                <Clock className="w-3 h-3 mr-1" />
                {response.response_time_ms}ms
              </Badge>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Trust Level Progress */}
          <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
            <Shield className="w-4 h-4 text-blue-600" />
            <div className="flex-1">
              <div className="flex justify-between text-sm mb-1">
                <span className="font-medium">Trust Level: {response.trust_level}</span>
                <span className="text-muted-foreground">Progress to next level</span>
              </div>
              <Progress 
                value={response.confidence_score} 
                className="h-2"
                indicatorClassName={getTrustLevelColor(response.trust_level)}
              />
            </div>
          </div>

          {/* Main Summary */}
          <div className="prose prose-sm max-w-none">
            <p className="text-gray-700 leading-relaxed">{response.summary}</p>
          </div>
        </CardContent>
      </Card>

      {/* Evidence Section */}
      {response.evidence && response.evidence.length > 0 && (
        <Card>
          <Collapsible 
            open={expandedSections.evidence}
            onOpenChange={() => toggleSection('evidence')}
          >
            <CollapsibleTrigger asChild>
              <CardHeader className="cursor-pointer hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-green-600" />
                    <CardTitle className="text-base">Supporting Evidence</CardTitle>
                    <Badge variant="secondary">{response.evidence.length}</Badge>
                  </div>
                  {expandedSections.evidence ? (
                    <ChevronUp className="w-4 h-4" />
                  ) : (
                    <ChevronDown className="w-4 h-4" />
                  )}
                </div>
              </CardHeader>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <CardContent className="pt-0">
                <div className="space-y-3">
                  {response.evidence.map((evidence, index) => (
                    <div key={index} className="border rounded-lg p-3 bg-gray-50">
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-medium text-sm">{evidence.title}</h4>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-xs">
                            {evidence.type}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {Math.round(evidence.relevance_score * 100)}% Relevant
                          </Badge>
                        </div>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{evidence.summary}</p>
                      {evidence.source_url && (
                        <Button variant="ghost" size="sm" className="p-0 h-auto">
                          <ExternalLink className="w-3 h-3 mr-1" />
                          View Source
                        </Button>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </CollapsibleContent>
          </Collapsible>
        </Card>
      )}

      {/* Action Plan Section */}
      {response.action_plan && (
        <Card>
          <Collapsible 
            open={expandedSections.actions}
            onOpenChange={() => toggleSection('actions')}
          >
            <CollapsibleTrigger asChild>
              <CardHeader className="cursor-pointer hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Target className="w-4 h-4 text-blue-600" />
                    <CardTitle className="text-base">Recommended Actions</CardTitle>
                    <Badge variant="secondary">{response.action_plan.immediate_actions.length}</Badge>
                  </div>
                  {expandedSections.actions ? (
                    <ChevronUp className="w-4 h-4" />
                  ) : (
                    <ChevronDown className="w-4 h-4" />
                  )}
                </div>
              </CardHeader>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <CardContent className="pt-0 space-y-4">
                {/* Immediate Actions */}
                <div>
                  <h4 className="font-medium text-sm mb-3 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-orange-500" />
                    Immediate Actions
                  </h4>
                  <div className="space-y-2">
                    {response.action_plan.immediate_actions.map((action, index) => (
                      <div key={index} className="flex items-start gap-2 p-2 bg-orange-50 rounded border-l-2 border-orange-200">
                        <CheckCircle className="w-4 h-4 text-orange-600 mt-0.5" />
                        <div className="flex-1">
                          <p className="text-sm font-medium">{action.title}</p>
                          <p className="text-xs text-gray-600 mt-1">{action.description}</p>
                          <div className="flex items-center gap-2 mt-2">
                            <Badge variant="outline" className="text-xs">
                              {action.priority}
                            </Badge>
                            <span className="text-xs text-gray-500">
                              ~{action.estimated_effort} effort
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Long-term Strategy */}
                {response.action_plan.long_term_strategy && (
                  <>
                    <Separator />
                    <div>
                      <h4 className="font-medium text-sm mb-3 flex items-center gap-2">
                        <TrendingUp className="w-4 h-4 text-blue-500" />
                        Long-term Strategy
                      </h4>
                      <div className="p-3 bg-blue-50 rounded border border-blue-200">
                        <p className="text-sm text-gray-700">{response.action_plan.long_term_strategy}</p>
                      </div>
                    </div>
                  </>
                )}
              </CardContent>
            </CollapsibleContent>
          </Collapsible>
        </Card>
      )}

      {/* Risk Assessment */}
      {response.risk_assessment && (
        <Card>
          <Collapsible 
            open={expandedSections.risks}
            onOpenChange={() => toggleSection('risks')}
          >
            <CollapsibleTrigger asChild>
              <CardHeader className="cursor-pointer hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-red-600" />
                    <CardTitle className="text-base">Risk Assessment</CardTitle>
                    <Badge 
                      variant="outline" 
                      className={cn('text-xs', getRiskColor(response.risk_assessment.overall_risk_level))}
                    >
                      {response.risk_assessment.overall_risk_level} Risk
                    </Badge>
                  </div>
                  {expandedSections.risks ? (
                    <ChevronUp className="w-4 h-4" />
                  ) : (
                    <ChevronDown className="w-4 h-4" />
                  )}
                </div>
              </CardHeader>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <CardContent className="pt-0">
                <div className="space-y-3">
                  {response.risk_assessment.identified_risks.map((risk, index) => (
                    <div key={index} className={cn('p-3 rounded border', getRiskColor(risk.severity))}>
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-medium text-sm">{risk.title}</h4>
                        <Badge variant="outline" className="text-xs">
                          {risk.severity}
                        </Badge>
                      </div>
                      <p className="text-sm mb-2">{risk.description}</p>
                      <div className="text-xs">
                        <span className="font-medium">Impact:</span> {risk.impact}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </CollapsibleContent>
          </Collapsible>
        </Card>
      )}

      {/* Graph Analysis */}
      {response.graph_analysis && (
        <Card>
          <Collapsible 
            open={expandedSections.graph}
            onOpenChange={() => toggleSection('graph')}
          >
            <CollapsibleTrigger asChild>
              <CardHeader className="cursor-pointer hover:bg-gray-50 transition-colors">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Network className="w-4 h-4 text-purple-600" />
                    <CardTitle className="text-base">Knowledge Graph Analysis</CardTitle>
                  </div>
                  {expandedSections.graph ? (
                    <ChevronUp className="w-4 h-4" />
                  ) : (
                    <ChevronDown className="w-4 h-4" />
                  )}
                </div>
              </CardHeader>
            </CollapsibleTrigger>
            <CollapsibleContent>
              <CardContent className="pt-0">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                  <div className="text-center p-3 bg-purple-50 rounded">
                    <div className="text-2xl font-bold text-purple-600">
                      {response.graph_analysis.nodes_accessed}
                    </div>
                    <div className="text-xs text-purple-700">Nodes Analyzed</div>
                  </div>
                  <div className="text-center p-3 bg-purple-50 rounded">
                    <div className="text-2xl font-bold text-purple-600">
                      {response.graph_analysis.relationships_traversed}
                    </div>
                    <div className="text-xs text-purple-700">Relationships</div>
                  </div>
                  <div className="text-center p-3 bg-purple-50 rounded">
                    <div className="text-2xl font-bold text-purple-600">
                      {response.graph_analysis.relevant_frameworks.length}
                    </div>
                    <div className="text-xs text-purple-700">Frameworks</div>
                  </div>
                  <div className="text-center p-3 bg-purple-50 rounded">
                    <div className="text-2xl font-bold text-purple-600">
                      {Math.round((response.graph_analysis.confidence_factors?.data_completeness || 0) * 100)}%
                    </div>
                    <div className="text-xs text-purple-700">Data Complete</div>
                  </div>
                </div>
                
                {response.graph_analysis.relevant_frameworks.length > 0 && (
                  <div>
                    <h4 className="font-medium text-sm mb-2">Related Frameworks</h4>
                    <div className="flex flex-wrap gap-2">
                      {response.graph_analysis.relevant_frameworks.map((framework, index) => (
                        <Badge key={index} variant="secondary" className="text-xs">
                          {framework}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </CardContent>
            </CollapsibleContent>
          </Collapsible>
        </Card>
      )}
    </div>
  );
}