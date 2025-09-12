/**
 * Zod Validation Schemas for AI Responses
 *
 * Runtime validation schemas that match the TypeScript interfaces
 * for comprehensive type safety and validation in Phase 6.
 */

import { z } from 'zod';

// =====================================================================
// Core Schema Validators
// =====================================================================

export const SeverityLevelSchema = z.enum(['low', 'medium', 'high', 'critical']);
export const PriorityLevelSchema = z.enum(['low', 'medium', 'high', 'urgent']);
export const ImplementationEffortSchema = z.enum(['minimal', 'low', 'medium', 'high', 'extensive']);
export const RiskLevelSchema = z.enum(['low', 'medium', 'high', 'critical']);
export const MaturityLevelSchema = z.enum([
  'initial',
  'developing',
  'defined',
  'managed',
  'optimized',
]);
export const TrendDirectionSchema = z.enum(['improving', 'stable', 'declining']);
export const InsightTypeSchema = z.enum(['strength', 'weakness', 'opportunity', 'threat']);
export const IntentTypeSchema = z.enum([
  'evidence_query',
  'compliance_check',
  'guidance_request',
  'general_query',
  'assessment_help',
]);
export const ExpectedAnswerTypeSchema = z.enum(['text', 'boolean', 'multiple_choice', 'numeric']);
export const ValidationStatusSchema = z.enum(['valid', 'invalid', 'partially_valid']);

// Score validators (0.0 to 1.0)
export const ScoreSchema = z.number().min(0).max(1);
export const PercentageSchema = z.number().min(0).max(100);

// =====================================================================
// Gap Analysis Validators
// =====================================================================

export const GapSchema = z.object({
  id: z.string().min(1),
  title: z.string().min(1).max(200),
  description: z.string().min(10),
  severity: SeverityLevelSchema,
  category: z.string().min(1),
  framework_reference: z.string().min(1),
  current_state: z.string().min(1),
  target_state: z.string().min(1),
  impact_description: z.string().min(1),
  business_impact_score: ScoreSchema,
  technical_complexity: ScoreSchema,
  regulatory_requirement: z.boolean(),
  estimated_effort: ImplementationEffortSchema,
  dependencies: z.array(z.string()).default([]),
  affected_systems: z.array(z.string()).default([]),
  stakeholders: z.array(z.string()).default([]),
});

export const GapAnalysisResponseSchema = z.object({
  gaps: z.array(GapSchema),
  overall_risk_level: RiskLevelSchema,
  priority_order: z.array(z.string()),
  estimated_total_effort: z.string().min(1),
  critical_gap_count: z.number().int().min(0),
  medium_high_gap_count: z.number().int().min(0),
  compliance_percentage: PercentageSchema,
  framework_coverage: z.record(z.string(), PercentageSchema).default({}),
  summary: z.string().min(10),
  next_steps: z.array(z.string()).min(1),
});

// =====================================================================
// Recommendation Validators
// =====================================================================

export const RecommendationSchema = z.object({
  id: z.string().min(1),
  title: z.string().min(1).max(200),
  description: z.string().min(10),
  priority: PriorityLevelSchema,
  category: z.string().min(1),
  framework_references: z.array(z.string()).min(1),
  addresses_gaps: z.array(z.string()).default([]),
  effort_estimate: ImplementationEffortSchema,
  implementation_timeline: z.string().min(1),
  impact_score: ScoreSchema,
  cost_estimate: z.string().optional(),
  resource_requirements: z.array(z.string()).default([]),
  success_criteria: z.array(z.string()).min(1),
  potential_challenges: z.array(z.string()).default([]),
  mitigation_strategies: z.array(z.string()).default([]),
  automation_potential: ScoreSchema.default(0),
  roi_estimate: z.string().optional(),
});

export const ImplementationPhaseSchema = z.object({
  phase_number: z.number().int().min(1),
  phase_name: z.string().min(1),
  duration_weeks: z.number().int().min(1),
  deliverables: z.array(z.string()).min(1),
  dependencies: z.array(z.string()).default([]),
  resources_required: z.array(z.string()).default([]),
  success_criteria: z.array(z.string()).min(1),
});

export const ImplementationPlanSchema = z.object({
  total_duration_weeks: z.number().int().min(1),
  phases: z.array(ImplementationPhaseSchema).min(1),
  resource_allocation: z.record(z.string(), z.string()).default({}),
  budget_estimate: z.string().optional(),
  risk_factors: z.array(z.string()).default([]),
  success_metrics: z.array(z.string()).min(1),
  milestone_checkpoints: z.array(z.string()).default([]),
});

export const RecommendationResponseSchema = z.object({
  recommendations: z.array(RecommendationSchema).min(1),
  implementation_plan: ImplementationPlanSchema,
  prioritization_rationale: z.string().min(10),
  quick_wins: z.array(z.string()).default([]),
  long_term_initiatives: z.array(z.string()).default([]),
  resource_summary: z.record(z.string(), z.any()).default({}),
  timeline_overview: z.string().min(10),
  success_metrics: z.array(z.string()).min(1),
});

// =====================================================================
// Assessment Analysis Validators
// =====================================================================

export const RiskAssessmentSchema = z.object({
  overall_risk_level: RiskLevelSchema,
  risk_score: PercentageSchema,
  top_risk_factors: z.array(z.string()).min(1),
  risk_mitigation_priorities: z.array(z.string()).min(1),
  regulatory_compliance_risk: PercentageSchema,
  operational_risk: PercentageSchema,
  reputational_risk: PercentageSchema,
  financial_risk: PercentageSchema,
});

export const ComplianceInsightSchema = z.object({
  insight_type: InsightTypeSchema,
  title: z.string().min(1).max(200),
  description: z.string().min(10),
  impact_level: SeverityLevelSchema,
  framework_area: z.string().min(1),
  actionable_steps: z.array(z.string()).min(1),
});

export const EvidenceRequirementSchema = z.object({
  evidence_type: z.string().min(1),
  description: z.string().min(10),
  framework_reference: z.string().min(1),
  priority: PriorityLevelSchema,
  collection_method: z.string().min(1),
  automation_potential: ScoreSchema,
  estimated_effort: ImplementationEffortSchema,
  validation_criteria: z.array(z.string()).min(1),
  retention_period: z.string().optional(),
});

export const ComplianceMetricsSchema = z.object({
  overall_compliance_score: PercentageSchema,
  framework_scores: z.record(z.string(), PercentageSchema).default({}),
  maturity_level: MaturityLevelSchema,
  coverage_percentage: PercentageSchema,
  gap_count_by_severity: z.record(SeverityLevelSchema, z.number().int().min(0)).default({}),
  improvement_trend: TrendDirectionSchema,
});

export const AssessmentAnalysisResponseSchema = z.object({
  gaps: z.array(GapSchema),
  recommendations: z.array(RecommendationSchema),
  risk_assessment: RiskAssessmentSchema,
  compliance_insights: z.array(ComplianceInsightSchema),
  evidence_requirements: z.array(EvidenceRequirementSchema),
  compliance_metrics: ComplianceMetricsSchema,
  executive_summary: z.string().min(50),
  detailed_findings: z.string().min(100),
  next_steps: z.array(z.string()).min(1),
  confidence_score: ScoreSchema,
});

// =====================================================================
// Help and Guidance Validators
// =====================================================================

export const GuidanceResponseSchema = z.object({
  guidance: z.string().min(50),
  confidence_score: ScoreSchema,
  related_topics: z.array(z.string()),
  follow_up_suggestions: z.array(z.string()),
  source_references: z.array(z.string()),
  examples: z.array(z.string()).default([]),
  best_practices: z.array(z.string()).default([]),
  common_pitfalls: z.array(z.string()).default([]),
  implementation_tips: z.array(z.string()).default([]),
});

export const FollowUpQuestionSchema = z.object({
  question_id: z.string().min(1),
  question_text: z.string().min(10),
  category: z.string().min(1),
  importance_level: PriorityLevelSchema,
  expected_answer_type: ExpectedAnswerTypeSchema,
  context: z.string().min(1),
  validation_criteria: z.array(z.string()).default([]),
});

export const FollowUpResponseSchema = z.object({
  follow_up_questions: z.array(FollowUpQuestionSchema),
  recommendations: z.array(z.string()),
  confidence_score: ScoreSchema,
  assessment_completeness: ScoreSchema,
  priority_areas: z.array(z.string()),
  suggested_next_steps: z.array(z.string()).min(1),
});

// =====================================================================
// Evidence and Workflow Validators
// =====================================================================

export const EvidenceItemSchema = z.object({
  evidence_id: z.string().min(1),
  title: z.string().min(1),
  description: z.string().min(10),
  framework_controls: z.array(z.string()),
  collection_method: z.string().min(1),
  automation_tools: z.array(z.string()).default([]),
  effort_estimate: ImplementationEffortSchema,
  priority: PriorityLevelSchema,
  frequency: z.string().min(1),
  owner_role: z.string().min(1),
  validation_requirements: z.array(z.string()),
  retention_period: z.string().min(1),
});

export const WorkflowStepSchema = z.object({
  step_number: z.number().int().min(1),
  title: z.string().min(1),
  description: z.string().min(10),
  estimated_duration: z.string().min(1),
  assigned_role: z.string().min(1),
  prerequisites: z.array(z.string()).default([]),
  deliverables: z.array(z.string()),
  validation_criteria: z.array(z.string()),
  automation_opportunities: z.array(z.string()).default([]),
});

export const WorkflowPhaseSchema = z.object({
  phase_number: z.number().int().min(1),
  phase_name: z.string().min(1),
  objective: z.string().min(10),
  steps: z.array(WorkflowStepSchema),
  estimated_duration: z.string().min(1),
  success_criteria: z.array(z.string()),
  dependencies: z.array(z.string()).default([]),
});

export const EvidenceWorkflowSchema = z.object({
  workflow_id: z.string().min(1),
  title: z.string().min(1),
  description: z.string().min(10),
  framework: z.string().min(1),
  control_reference: z.string().min(1),
  phases: z.array(WorkflowPhaseSchema),
  total_estimated_duration: z.string().min(1),
  required_roles: z.array(z.string()),
  automation_percentage: ScoreSchema,
  complexity_level: z.enum(['simple', 'moderate', 'complex']),
});

// =====================================================================
// Policy Generation Validators
// =====================================================================

export const PolicySectionSchema = z.object({
  section_number: z.string().min(1),
  title: z.string().min(1),
  content: z.string().min(10),
  subsections: z
    .array(
      z.object({
        title: z.string(),
        content: z.string(),
      }),
    )
    .default([]),
  compliance_references: z.array(z.string()).default([]),
  implementation_notes: z.array(z.string()).default([]),
});

export const PolicyDocumentSchema = z.object({
  policy_id: z.string().min(1),
  title: z.string().min(1),
  version: z.string().min(1),
  effective_date: z.string().min(1),
  framework_compliance: z.array(z.string()),
  sections: z.array(PolicySectionSchema),
  approval_workflow: z.array(z.string()),
  review_schedule: z.string().min(1),
  related_documents: z.array(z.string()).default([]),
  implementation_guidance: z.string().min(10),
});

// =====================================================================
// Chat and Conversation Validators
// =====================================================================

export const IntentClassificationSchema = z.object({
  intent_type: IntentTypeSchema,
  confidence: ScoreSchema,
  entities: z.record(z.string(), z.array(z.string())),
  context_requirements: z.array(z.string()).default([]),
  suggested_actions: z.array(z.string()).default([]),
});

export const ChatResponseSchema = z.object({
  response_text: z.string().min(1),
  intent_classification: IntentClassificationSchema,
  confidence_score: ScoreSchema,
  follow_up_suggestions: z.array(z.string()).default([]),
  related_resources: z.array(z.string()).default([]),
  action_items: z.array(z.string()).default([]),
});

// =====================================================================
// Meta Response Validators
// =====================================================================

export const ResponseMetadataSchema = z.object({
  response_id: z.string().min(1),
  timestamp: z.string().min(1),
  model_used: z.string().min(1),
  processing_time_ms: z.number().int().min(0),
  confidence_score: ScoreSchema,
  schema_version: z.string().min(1),
  validation_status: ValidationStatusSchema,
  validation_errors: z.array(z.string()).default([]),
});

export const StructuredAIResponseSchema = z.object({
  metadata: ResponseMetadataSchema,
  response_type: z.string().min(1),
  payload: z.any(), // Will be validated based on response_type
  validation_passed: z.boolean(),
  fallback_used: z.boolean().default(false),
});

// =====================================================================
// Error and Validation Validators
// =====================================================================

export const ValidationErrorSchema = z.object({
  field_path: z.string().min(1),
  error_type: z.string().min(1),
  error_message: z.string().min(1),
  expected_type: z.string().min(1),
  actual_value: z.any(),
  suggestion: z.string().optional(),
});

export const SchemaValidationResultSchema = z.object({
  is_valid: z.boolean(),
  schema_name: z.string().min(1),
  validation_errors: z.array(ValidationErrorSchema),
  warnings: z.array(z.string()).default([]),
  validation_timestamp: z.string().min(1),
  corrected_data: z.record(z.string(), z.any()).optional(),
});

// =====================================================================
// Schema Registry
// =====================================================================

// =====================================================================
// Self-Review Validators
// =====================================================================

export const SelfReviewIssueSchema = z.object({
  issue_id: z.string().min(1),
  severity: z.enum(['low', 'medium', 'high', 'critical']),
  category: z.enum([
    'factual_accuracy',
    'logical_consistency',
    'completeness',
    'clarity',
    'relevance',
    'bias',
    'assumption',
  ]),
  description: z.string().min(10),
  location: z.string().min(1),
  suggested_fix: z.string().min(10),
  confidence_in_identification: z.number().min(1).max(10),
});

export const ConfidenceFactorSchema = z.object({
  factor: z.string().min(1),
  impact: z.enum(['increases', 'decreases', 'neutral']),
  explanation: z.string().min(10),
});

export const ConfidenceAssessmentSchema = z.object({
  original_confidence: ScoreSchema,
  reviewed_confidence: ScoreSchema,
  confidence_factors: z.array(ConfidenceFactorSchema),
  uncertainty_areas: z.array(z.string()),
});

export const FactualClaimSchema = z.object({
  claim: z.string().min(1),
  verification_status: z.enum(['verified', 'uncertain', 'requires_check', 'potentially_incorrect']),
  confidence_level: z.number().min(1).max(10),
});

export const RegulatoryReferenceSchema = z.object({
  reference: z.string().min(1),
  accuracy_status: z.enum(['correct', 'outdated', 'uncertain', 'incorrect']),
  notes: z.string().optional(),
});

export const AccuracyCheckSchema = z.object({
  factual_claims: z.array(FactualClaimSchema),
  regulatory_references: z.array(RegulatoryReferenceSchema),
  overall_accuracy_score: z.number().min(0).max(10),
});

export const CompletenessReviewSchema = z.object({
  missing_aspects: z.array(z.string()),
  incomplete_explanations: z.array(z.string()),
  areas_needing_expansion: z.array(z.string()),
  completeness_score: z.number().min(0).max(10),
});

export const ReadabilityAssessmentSchema = z.object({
  complexity_level: z.enum(['basic', 'intermediate', 'advanced', 'expert']),
  target_audience_match: z.boolean(),
  improvement_suggestions: z.array(z.string()),
});

export const ClarityEvaluationSchema = z.object({
  unclear_explanations: z.array(z.string()),
  jargon_without_explanation: z.array(z.string()),
  logical_flow_issues: z.array(z.string()),
  clarity_score: z.number().min(0).max(10),
  readability_assessment: ReadabilityAssessmentSchema,
});

export const SelfCritiqueSchema = z.object({
  identified_issues: z.array(SelfReviewIssueSchema),
  confidence_assessment: ConfidenceAssessmentSchema,
  accuracy_check: AccuracyCheckSchema,
  completeness_review: CompletenessReviewSchema,
  clarity_evaluation: ClarityEvaluationSchema,
});

export const ReviewQualitySchema = z.object({
  overall_confidence: z.number().min(1).max(10),
  reliability_score: z.number().min(1).max(10),
  revision_significance: z.enum(['none', 'minor', 'moderate', 'major']),
  areas_needing_verification: z.array(z.string()),
});

export const UserGuidanceSchema = z.object({
  how_to_use: z.string().min(10),
  confidence_interpretation: z.string().min(10),
  when_to_seek_additional_help: z.string().min(10),
});

export const SelfReviewResponseSchema = z.object({
  review_id: z.string().min(1),
  timestamp: z.string().min(1),
  original_response: GuidanceResponseSchema,
  self_critique: SelfCritiqueSchema,
  revised_response: GuidanceResponseSchema,
  review_quality: ReviewQualitySchema,
  user_guidance: UserGuidanceSchema,
});

export const QuickConfidenceCheckSchema = z.object({
  confidence_score: z.number().min(0).max(10),
  confidence_factors: z.array(z.string()),
  quick_issues: z.array(z.string()),
  recommendation: z.enum(['use_as_is', 'review_recommended', 'seek_expert_help']),
});

export const SelfReviewMetricsSchema = z.object({
  total_reviews: z.number().int().min(0),
  average_confidence_change: z.number(),
  common_issue_categories: z.array(
    z.object({
      category: z.string(),
      frequency: z.number().int().min(0),
    }),
  ),
  revision_frequency: z.array(
    z.object({
      level: z.string(),
      count: z.number().int().min(0),
    }),
  ),
  user_satisfaction_with_reviews: z.number().min(0).max(10),
});

export const AI_RESPONSE_SCHEMAS = {
  gap_analysis: GapAnalysisResponseSchema,
  recommendations: RecommendationResponseSchema,
  assessment_analysis: AssessmentAnalysisResponseSchema,
  guidance: GuidanceResponseSchema,
  followup: FollowUpResponseSchema,
  intent_classification: IntentClassificationSchema,
  chat: ChatResponseSchema,
  policy: PolicyDocumentSchema,
  workflow: EvidenceWorkflowSchema,
  self_review: SelfReviewResponseSchema,
  quick_confidence_check: QuickConfidenceCheckSchema,
  self_review_metrics: SelfReviewMetricsSchema,
} as const;

export type AIResponseSchemaType = keyof typeof AI_RESPONSE_SCHEMAS;

// =====================================================================
// Validation Functions
// =====================================================================

export function validateAIResponse<T extends AIResponseSchemaType>(
  data: unknown,
  responseType: T,
): {
  success: boolean;
  data?: z.infer<(typeof AI_RESPONSE_SCHEMAS)[T]>;
  errors?: z.ZodError[];
} {
  const schema = AI_RESPONSE_SCHEMAS[responseType];

  if (!schema) {
    return {
      success: false,
      errors: [
        new z.ZodError([
          {
            code: 'custom',
            message: `Unknown response type: ${responseType}`,
            path: ['responseType'],
          },
        ]),
      ],
    };
  }

  try {
    const validatedData = schema.parse(data);
    return {
      success: true,
      data: validatedData,
    };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return {
        success: false,
        errors: [error],
      };
    }

    return {
      success: false,
      errors: [
        new z.ZodError([
          {
            code: 'custom',
            message: 'Unknown validation error',
            path: [],
          },
        ]),
      ],
    };
  }
}

export function validateStructuredResponse(data: unknown): {
  success: boolean;
  data?: z.infer<typeof StructuredAIResponseSchema>;
  errors?: z.ZodError[];
} {
  try {
    const validatedData = StructuredAIResponseSchema.parse(data);
    return {
      success: true,
      data: validatedData,
    };
  } catch (error) {
    if (error instanceof z.ZodError) {
      return {
        success: false,
        errors: [error],
      };
    }

    return {
      success: false,
      errors: [
        new z.ZodError([
          {
            code: 'custom',
            message: 'Unknown validation error',
            path: [],
          },
        ]),
      ],
    };
  }
}

export function getValidationErrors(zodError: z.ZodError): string[] {
  return zodError.errors.map((error) => {
    const path = error.path.join('.');
    return `${path}: ${error.message}`;
  });
}

export function isValidResponseType(responseType: string): responseType is AIResponseSchemaType {
  return responseType in AI_RESPONSE_SCHEMAS;
}

// =====================================================================
// Utility Validators
// =====================================================================

export function validateAndTransformAIResponse<T extends AIResponseSchemaType>(
  rawResponse: unknown,
  expectedType: T,
): {
  success: boolean;
  data?: z.infer<(typeof AI_RESPONSE_SCHEMAS)[T]>;
  errors?: string[];
  warnings?: string[];
} {
  // First validate the structured response wrapper
  const structuredValidation = validateStructuredResponse(rawResponse);

  if (!structuredValidation.success) {
    return {
      success: false,
      errors: structuredValidation.errors?.flatMap(getValidationErrors) || [
        'Unknown validation error',
      ],
    };
  }

  const structuredData = structuredValidation.data!;

  // Check if response type matches expected
  if (structuredData.response_type !== expectedType) {
    return {
      success: false,
      errors: [`Expected response type ${expectedType}, got ${structuredData.response_type}`],
    };
  }

  // Validate the payload against the specific schema
  const payloadValidation = validateAIResponse(structuredData.payload, expectedType);

  if (!payloadValidation.success) {
    return {
      success: false,
      errors: payloadValidation.errors?.flatMap(getValidationErrors) || [
        'Payload validation failed',
      ],
    };
  }

  // Check for validation warnings from metadata
  const warnings =
    structuredData.metadata.validation_errors?.length > 0
      ? structuredData.metadata.validation_errors
      : undefined;

  return {
    success: true,
    data: payloadValidation.data,
    warnings,
  };
}
