export type QuestionType = 
  | 'radio' 
  | 'checkbox' 
  | 'text' 
  | 'textarea' 
  | 'number' 
  | 'date' 
  | 'select' 
  | 'scale' 
  | 'matrix'
  | 'file_upload';

export interface QuestionOption {
  value: string;
  label: string;
  description?: string;
  icon?: string;
}

export interface QuestionValidation {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  min?: number;
  max?: number;
  pattern?: string;
  custom?: (value: any, context: AssessmentContext) => string | null;
}

export interface QuestionCondition {
  questionId: string;
  operator: 'equals' | 'not_equals' | 'contains' | 'greater_than' | 'less_than' | 'in' | 'not_in';
  value: any;
  combineWith?: 'AND' | 'OR';
}

export interface Question {
  id: string;
  type: QuestionType;
  text: string;
  description?: string;
  helpText?: string;
  category?: string;
  section?: string;
  options?: QuestionOption[];
  validation?: QuestionValidation;
  conditions?: QuestionCondition[];
  weight?: number;
  metadata?: Record<string, any>;
  // For matrix questions
  rows?: { id: string; label: string }[];
  columns?: { id: string; label: string }[];
  // For scale questions
  scaleMin?: number;
  scaleMax?: number;
  scaleLabels?: { min: string; max: string };
}

export interface AssessmentSection {
  id: string;
  title: string;
  description?: string;
  order: number;
  questions: Question[];
  conditions?: QuestionCondition[];
}

export interface AssessmentFramework {
  id: string;
  name: string;
  description: string;
  version: string;
  sections: AssessmentSection[];
  scoringMethod: 'percentage' | 'weighted' | 'maturity' | 'custom';
  passingScore?: number;
  estimatedDuration?: number; // in minutes
  tags?: string[];
}

export interface Answer {
  questionId: string;
  value: any;
  timestamp: Date;
  source?: 'framework' | 'ai' | undefined; // Track if answer is from framework or AI question
  metadata?: Record<string, any> | undefined;
}

export interface AssessmentProgress {
  totalQuestions: number;
  answeredQuestions: number;
  currentSection: string;
  currentQuestion: string;
  percentComplete: number;
  estimatedTimeRemaining?: number;
  lastSaved?: Date;
}

export interface AssessmentContext {
  frameworkId: string;
  assessmentId: string;
  businessProfileId: string;
  answers: Map<string, Answer>;
  metadata: Record<string, any>;
}

export interface AssessmentResult {
  assessmentId: string;
  frameworkId: string;
  overallScore: number;
  sectionScores: Record<string, number>;
  maturityLevel?: 'initial' | 'developing' | 'defined' | 'managed' | 'optimized' | undefined;
  gaps: Gap[];
  recommendations: Recommendation[];
  completedAt: Date;
  certificateUrl?: string | undefined;
}

export interface Gap {
  id: string;
  questionId: string;
  questionText: string;
  section: string;
  category: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  description: string;
  impact: string;
  currentState: string;
  targetState: string;
  expectedAnswer: string;
  actualAnswer?: string;
}

export interface Recommendation {
  id: string;
  gapId: string;
  priority: 'immediate' | 'short_term' | 'medium_term' | 'long_term';
  title: string;
  description: string;
  estimatedEffort: string;
  resources?: string[];
  relatedFrameworks?: string[];
  category: string;
  impact: string;
  effort: string;
  estimatedTime: string;
  relatedGaps?: string[];
}

export interface QuestionnaireEngineConfig {
  allowSkipping?: boolean;
  autoSave?: boolean;
  autoSaveInterval?: number; // in seconds
  showProgress?: boolean;
  enableNavigation?: boolean;
  randomizeQuestions?: boolean;
  timeLimit?: number; // in minutes
  enableAI?: boolean; // Enable AI follow-up questions
  useMockAIOnError?: boolean; // Use mock AI questions if AI service fails
  onComplete?: (result: AssessmentResult) => void;
  onProgress?: (progress: AssessmentProgress) => void;
  onError?: (error: Error) => void;
}