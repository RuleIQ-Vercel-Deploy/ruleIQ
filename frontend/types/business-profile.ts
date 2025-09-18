/**
 * Business Profile Types
 *
 * Clean, self-documenting interfaces for frontend use.
 * These use descriptive field names that are mapped to the backend's
 * truncated field names via the BusinessProfileFieldMapper.
 */

// Assessment data type
export interface AssessmentData {
  current_step?: number;
  completed_steps?: string[];
  answers?: Record<string, string | number | boolean | string[] | null>;
  progress_percentage?: number;
  last_updated?: string;
  responses?: Record<string, string | number | boolean | string[]>;
  scores?: Array<{
    category: string;
    score: number;
    confidence: number;
  }>;
  completion_status?: 'not_started' | 'in_progress' | 'completed';
}

// Validation schema for form fields
export interface ValidationSchema {
  required?: boolean;
  minLength?: number;
  maxLength?: number;
  pattern?: string;
  min?: number;
  max?: number;
  enum?: string[];
  custom?: (value: unknown) => string | null;
}

export interface BusinessProfile {
  // Basic Company Information
  id?: string;
  user_id?: string;
  company_name: string;
  industry: string;
  employee_count: number;
  annual_revenue?: string;
  country: string;

  // Data Sensitivity Classification
  data_sensitivity: 'Low' | 'Moderate' | 'High' | 'Confidential';
  data_types: string[];

  // Business Characteristics - Using full, descriptive names
  handles_personal_data: boolean;
  processes_payments: boolean;
  stores_health_data: boolean;
  provides_financial_services: boolean;
  operates_critical_infrastructure: boolean;
  has_international_operations: boolean;

  // Technology Stack - Using full names
  cloud_providers: string[];
  saas_tools: string[];
  development_tools: string[];

  // Current Compliance State - Using full names
  existing_frameworks: string[];
  planned_frameworks: string[];
  compliance_budget?: string;
  compliance_timeline?: string;

  // Assessment Status
  assessment_completed: boolean;
  assessment_data: AssessmentData;

  // Metadata
  created_at?: string;
  updated_at?: string;
}

// Form data type (excludes metadata fields)
export type BusinessProfileFormData = Omit<
  BusinessProfile,
  'id' | 'user_id' | 'created_at' | 'updated_at'
>;

// Step-specific form data types for the wizard
export interface CompanyInfoData {
  company_name: string;
  industry: string;
  employee_count: number;
  annual_revenue?: string;
  country: string;
}

export interface ComplianceProfileData {
  data_sensitivity: 'Low' | 'Moderate' | 'High' | 'Confidential';
  handles_personal_data: boolean;
  processes_payments: boolean;
  stores_health_data: boolean;
  provides_financial_services: boolean;
  operates_critical_infrastructure: boolean;
  has_international_operations: boolean;
}

export interface TechnologyStackData {
  cloud_providers: string[];
  saas_tools: string[];
  development_tools: string[];
}

export interface ComplianceGoalsData {
  existing_frameworks: string[];
  planned_frameworks: string[];
  compliance_budget?: string;
  compliance_timeline?: string;
}

// Wizard step data union type
export type WizardStepData =
  | CompanyInfoData
  | ComplianceProfileData
  | TechnologyStackData
  | ComplianceGoalsData;

// Industry options
export const INDUSTRIES = [
  'Technology',
  'Healthcare',
  'Financial Services',
  'Education',
  'Government',
  'Manufacturing',
  'Retail',
  'Professional Services',
  'Non-profit',
  'Other',
] as const;

export type Industry = (typeof INDUSTRIES)[number];

// Employee count ranges
export const EMPLOYEE_COUNT_RANGES = [
  { value: 1, label: '1-10 employees' },
  { value: 25, label: '11-50 employees' },
  { value: 100, label: '51-200 employees' },
  { value: 500, label: '201-1000 employees' },
  { value: 1001, label: '1000+ employees' },
] as const;

// Annual revenue ranges
export const ANNUAL_REVENUE_RANGES = [
  'Under £1M',
  '£1M-£5M',
  '£5M-£25M',
  '£25M-£100M',
  'Over £100M',
] as const;

export type AnnualRevenue = (typeof ANNUAL_REVENUE_RANGES)[number];

// Countries
export const COUNTRIES = [
  'United Kingdom',
  'United States',
  'Canada',
  'Germany',
  'France',
  'Netherlands',
  'Ireland',
  'Australia',
  'Other',
] as const;

export type Country = (typeof COUNTRIES)[number];

// Data sensitivity levels
export const DATA_SENSITIVITY_LEVELS = [
  { value: 'Low', label: 'Low', description: 'Basic business data, no personal information' },
  {
    value: 'Moderate',
    label: 'Moderate',
    description: 'Some personal data, standard business information',
  },
  { value: 'High', label: 'High', description: 'Sensitive personal data, financial information' },
  {
    value: 'Confidential',
    label: 'Confidential',
    description: 'Highly sensitive data, health records, financial services',
  },
] as const;

// Compliance frameworks
export const COMPLIANCE_FRAMEWORKS = [
  'GDPR',
  'ISO 27001',
  'SOC 2',
  'PCI DSS',
  'HIPAA',
  'FCA',
  'CQC',
  'Cyber Essentials',
  'NIST',
  'Other',
] as const;

export type ComplianceFramework = (typeof COMPLIANCE_FRAMEWORKS)[number];

// Cloud providers
export const CLOUD_PROVIDERS = [
  'AWS',
  'Microsoft Azure',
  'Google Cloud',
  'IBM Cloud',
  'Oracle Cloud',
  'DigitalOcean',
  'Linode',
  'Other',
] as const;

// SaaS tools
export const SAAS_TOOLS = [
  'Microsoft 365',
  'Google Workspace',
  'Salesforce',
  'HubSpot',
  'Slack',
  'Zoom',
  'Dropbox',
  'Box',
  'Atlassian',
  'Other',
] as const;

// Development tools
export const DEVELOPMENT_TOOLS = [
  'GitHub',
  'GitLab',
  'Bitbucket',
  'Azure DevOps',
  'Jenkins',
  'Docker',
  'Kubernetes',
  'Terraform',
  'Other',
] as const;

// Compliance budget ranges
export const COMPLIANCE_BUDGET_RANGES = [
  'Under £5K',
  '£5K-£25K',
  '£25K-£100K',
  '£100K-£500K',
  'Over £500K',
] as const;

// Compliance timeline options
export const COMPLIANCE_TIMELINE_OPTIONS = [
  '3 months',
  '6 months',
  '12 months',
  '18 months',
  '24+ months',
] as const;

// Wizard step configuration
export interface WizardStep {
  id: string;
  title: string;
  description: string;
  component: string;
  validation?: ValidationSchema;
}

export const WIZARD_STEPS: WizardStep[] = [
  {
    id: 'company-info',
    title: 'Company Information',
    description: 'Tell us about your organization',
    component: 'CompanyInfoStep',
  },
  {
    id: 'compliance-profile',
    title: 'Compliance Profile',
    description: 'Define your data handling and business activities',
    component: 'ComplianceProfileStep',
  },
  {
    id: 'technology-stack',
    title: 'Technology Stack',
    description: 'What tools and platforms do you use?',
    component: 'TechnologyStackStep',
  },
  {
    id: 'compliance-goals',
    title: 'Compliance Goals',
    description: 'What frameworks are you targeting?',
    component: 'ComplianceGoalsStep',
  },
];

// Validation error types
export interface ValidationError {
  field: string;
  message: string;
}

export interface BusinessProfileValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings?: string[];
}

// Framework recommendation type
export interface FrameworkRecommendation {
  framework: string;
  score: number;
  reasons: string[];
  priority: 'high' | 'medium' | 'low';
  estimatedEffort: string;
  estimatedCost: string;
}
