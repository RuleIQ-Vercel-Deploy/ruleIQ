// AI Response Types - Based on backend response_formats.py schemas
// These types mirror the structured AI responses from the backend

export type SeverityLevel = 'low' | 'medium' | 'high' | 'critical';
export type PriorityLevel = 'low' | 'medium' | 'high' | 'urgent';
export type EffortLevel = 'minimal' | 'low' | 'medium' | 'high' | 'extensive';
export type MaturityLevel = 'initial' | 'developing' | 'defined' | 'managed' | 'optimized';
export type InsightType = 'strength' | 'weakness' | 'opportunity' | 'threat';
export type ImprovementTrend = 'improving' | 'stable' | 'declining';
export type RiskLevel = 'low' | 'medium' | 'high' | 'critical';

// =====================================================================
// Gap Analysis Response Types
// =====================================================================

export interface ComplianceGap {
  id: string;
  title: string;
  description: string;
  severity: SeverityLevel;
  category: string;
  framework_reference: string;
  current_state: string;
  target_state: string;
  impact_description: string;
  business_impact_score: number; // 0.0 - 1.0
  technical_complexity: number; // 0.0 - 1.0
  regulatory_requirement: boolean;
  estimated_effort: EffortLevel;
  dependencies?: string[];
  affected_systems?: string[];
  stakeholders?: string[];
}

export interface GapAnalysisResponse {
  gaps: ComplianceGap[];
  overall_risk_level: RiskLevel;
  priority_order: string[];
  estimated_total_effort: string;
  critical_gap_count: number;
  medium_high_gap_count: number;
  compliance_percentage: number; // 0.0 - 100.0
  framework_coverage: Record<string, number>; // framework -> percentage
  summary: string;
  next_steps: string[];
}

// =====================================================================
// Recommendations Response Types
// =====================================================================

export interface ComplianceRecommendation {
  id: string;
  title: string;
  description: string;
  priority: PriorityLevel;
  category: string;
  framework_references: string[];
  addresses_gaps: string[];
  effort_estimate: EffortLevel;
  implementation_timeline: string;
  impact_score: number; // 0.0 - 1.0
  cost_estimate?: string;
  resource_requirements?: string[];
  success_criteria?: string[];
  potential_challenges?: string[];
  mitigation_strategies?: string[];
  automation_potential?: number; // 0.0 - 1.0
  roi_estimate?: string;
}

export interface ImplementationPhase {
  phase_number: number;
  phase_name: string;
  duration_weeks: number;
  deliverables: string[];
  dependencies?: string[];
  resources_required?: string[];
  success_criteria: string[];
}

export interface ImplementationPlan {
  total_duration_weeks: number;
  phases: ImplementationPhase[];
  resource_allocation?: Record<string, string>;
  budget_estimate?: string;
  risk_factors?: string[];
  success_metrics: string[];
  milestone_checkpoints?: string[];
}

export interface RecommendationsResponse {
  recommendations: ComplianceRecommendation[];
  implementation_plan: ImplementationPlan;
  prioritization_rationale: string;
  quick_wins?: string[];
  long_term_initiatives?: string[];
  resource_summary?: Record<string, any>;
  timeline_overview: string;
  success_metrics: string[];
}

// =====================================================================
// Assessment Analysis Response Types
// =====================================================================

export interface RiskAssessment {
  overall_risk_level: RiskLevel;
  risk_score: number; // 0.0 - 100.0
  top_risk_factors: string[];
  risk_mitigation_priorities: string[];
  regulatory_compliance_risk?: number; // 0.0 - 100.0
  operational_risk?: number; // 0.0 - 100.0
  reputational_risk?: number; // 0.0 - 100.0
  financial_risk?: number; // 0.0 - 100.0
}

export interface ComplianceInsight {
  insight_type: InsightType;
  title: string;
  description: string;
  impact_level: SeverityLevel;
  framework_area: string;
  actionable_steps: string[];
}

export interface EvidenceRequirement {
  evidence_type: string;
  description: string;
  framework_reference: string;
  priority: PriorityLevel;
  collection_method: string;
  automation_potential?: number; // 0.0 - 1.0
  estimated_effort: EffortLevel;
  validation_criteria?: string[];
  retention_period?: string;
}

export interface ComplianceMetrics {
  overall_compliance_score: number; // 0.0 - 100.0
  framework_scores?: Record<string, number>; // framework -> score
  maturity_level: MaturityLevel;
  coverage_percentage: number; // 0.0 - 100.0
  gap_count_by_severity?: {
    low?: number;
    medium?: number;
    high?: number;
    critical?: number;
  };
  improvement_trend: ImprovementTrend;
}

export interface AssessmentAnalysisResponse {
  gaps: ComplianceGap[];
  recommendations: ComplianceRecommendation[];
  risk_assessment: RiskAssessment;
  compliance_insights: ComplianceInsight[];
  evidence_requirements: EvidenceRequirement[];
  compliance_metrics: ComplianceMetrics;
  executive_summary: string;
  detailed_findings: string;
  next_steps: string[];
  confidence_score: number; // 0.0 - 1.0
}

// =====================================================================
// Guidance Response Types
// =====================================================================

export interface GuidanceResponse {
  guidance: string;
  confidence_score: number; // 0.0 - 1.0
  related_topics: string[];
  follow_up_suggestions: string[];
  source_references: string[];
  examples?: string[];
  best_practices?: string[];
  common_pitfalls?: string[];
  implementation_tips?: string[];
}

// =====================================================================
// Follow-up Response Types
// =====================================================================

export type AnswerType = 'text' | 'boolean' | 'multiple_choice' | 'numeric';

export interface FollowUpQuestion {
  question_id: string;
  question_text: string;
  category: string;
  importance_level: PriorityLevel;
  expected_answer_type: AnswerType;
  context?: string;
  validation_criteria?: string[];
}

export interface FollowUpResponse {
  follow_up_questions: FollowUpQuestion[];
  recommendations: string[];
  confidence_score: number; // 0.0 - 1.0
  assessment_completeness: number; // 0.0 - 1.0
  priority_areas: string[];
  suggested_next_steps: string[];
}

// =====================================================================
// Intent Classification Types
// =====================================================================

export type IntentType = 
  | 'evidence_query'
  | 'compliance_check'
  | 'guidance_request'
  | 'general_query'
  | 'assessment_help';

export interface IntentClassification {
  intent_type: IntentType;
  confidence: number; // 0.0 - 1.0
  entities: {
    frameworks?: string[];
    evidence_types?: string[];
    topics?: string[];
  };
  context_requirements?: string[];
  suggested_actions?: string[];
}

// =====================================================================
// Union Type for All AI Response Types
// =====================================================================

export type AIResponseType = 
  | 'gap_analysis'
  | 'recommendations'
  | 'assessment_analysis'
  | 'guidance'
  | 'followup'
  | 'intent_classification';

export interface AIResponseWrapper {
  type: AIResponseType;
  data: GapAnalysisResponse | RecommendationsResponse | AssessmentAnalysisResponse | 
        GuidanceResponse | FollowUpResponse | IntentClassification;
  confidence_score?: number;
  processing_time_ms?: number;
  model_used?: string;
}

// =====================================================================
// UI Component Props Types
// =====================================================================

export interface ComplianceMessageRendererProps {
  content: string;
  metadata?: {
    response_type?: AIResponseType;
    confidence?: number;
    sources?: string[];
    [key: string]: any;
  };
  onActionClick?: (action: string, data?: any) => void;
}