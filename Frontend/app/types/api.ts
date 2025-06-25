// Core API types based on backend schemas
export interface User {
  id: string
  email: string
  created_at: string
  is_active: boolean
  role?: string
  permissions?: string[]
  avatar?: string
  first_name?: string
  last_name?: string
  organization_id?: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface BusinessProfile {
  id: string
  company_name: string
  industry: string
  employee_count: number
  annual_revenue: string
  country: string
  data_sensitivity: "Low" | "Moderate" | "High" | "Confidential"
  handles_personal_data: boolean
  processes_payments: boolean
  stores_health_data: boolean
  provides_financial_services: boolean
  operates_critical_infrastructure: boolean
  has_international_operations: boolean
  existing_frameworks: string[]
  planned_frameworks: string[]
  cloud_providers: string[]
  saas_tools: string[]
  development_tools: string[]
  compliance_budget: number
  compliance_timeline: string
  created_at: string
  updated_at: string
}

export interface Evidence {
  id: string
  title: string
  description: string
  control_id: string
  framework: string
  business_profile_id: string
  evidence_type: string
  source: string
  tags: string[]
  status: "draft" | "review" | "approved" | "rejected"
  quality_score: number
  created_at: string
  updated_at: string
}

export interface ChatConversation {
  id: string
  title: string
  created_at: string
  updated_at: string
  message_count: number
  last_message?: string
  is_pinned?: boolean
  tags?: string[]
}

export interface ChatMessage {
  id: string
  conversation_id: string
  content: string
  role: "user" | "assistant"
  created_at: string
  message_type?: "text" | "file" | "code" | "table"
  metadata?: {
    files?: ChatFile[]
    code_language?: string
    thinking?: string
    sources?: string[]
    confidence?: number
  }
  is_edited?: boolean
  edited_at?: string
  reactions?: ChatReaction[]
}

export interface ChatFile {
  id: string
  name: string
  size: number
  type: string
  url: string
  uploaded_at: string
}

export interface ChatReaction {
  emoji: string
  count: number
  users: string[]
}

export interface ChatSettings {
  model: string
  temperature: number
  max_tokens: number
  system_prompt?: string
  auto_save: boolean
  show_thinking: boolean
  enable_web_search: boolean
  enable_code_execution: boolean
}

export interface Assessment {
  id: string
  title: string
  description: string
  framework: string
  business_profile_id: string
  status: "draft" | "in_progress" | "completed" | "reviewed"
  progress: number
  score?: number
  max_score?: number
  started_at?: string
  completed_at?: string
  created_at: string
  updated_at: string
  questions_count: number
  answered_count: number
}

export interface AssessmentQuestion {
  id: string
  assessment_id: string
  question_text: string
  question_type:
    | "multiple_choice"
    | "single_choice"
    | "text"
    | "textarea"
    | "file_upload"
    | "boolean"
    | "scale"
    | "matrix"
  required: boolean
  order: number
  section: string
  control_reference?: string
  options?: AssessmentQuestionOption[]
  validation_rules?: Record<string, any>
  help_text?: string
  weight: number
}

export interface AssessmentQuestionOption {
  id: string
  text: string
  value: string | number
  score: number
}

export interface AssessmentAnswer {
  id: string
  assessment_id: string
  question_id: string
  answer_value: string | string[] | number | boolean
  score: number
  notes?: string
  evidence_ids?: string[]
  created_at: string
  updated_at: string
}

export interface AssessmentResult {
  id: string
  assessment_id: string
  overall_score: number
  max_score: number
  percentage: number
  section_scores: AssessmentSectionScore[]
  recommendations: AssessmentRecommendation[]
  gaps: AssessmentGap[]
  created_at: string
}

export interface AssessmentSectionScore {
  section: string
  score: number
  max_score: number
  percentage: number
  questions_count: number
  answered_count: number
}

export interface AssessmentRecommendation {
  id: string
  title: string
  description: string
  priority: "low" | "medium" | "high" | "critical"
  category: string
  estimated_effort: string
}

export interface AssessmentGap {
  id: string
  control_reference: string
  description: string
  current_score: number
  target_score: number
  impact: "low" | "medium" | "high"
}

export interface Report {
  id: string
  title: string
  description?: string
  type:
    | "compliance_summary"
    | "assessment_results"
    | "evidence_inventory"
    | "gap_analysis"
    | "executive_summary"
    | "audit_trail"
    | "custom"
  status: "generating" | "completed" | "failed" | "scheduled"
  format: "pdf" | "excel" | "csv" | "html"
  business_profile_id?: string
  assessment_id?: string
  framework?: string
  date_range?: {
    start_date: string
    end_date: string
  }
  filters?: Record<string, any>
  template_id?: string
  generated_by: string
  file_url?: string
  file_size?: number
  created_at: string
  updated_at: string
  scheduled_at?: string
  delivered_at?: string
  recipients?: string[]
  tags?: string[]
}

export interface ReportTemplate {
  id: string
  name: string
  description: string
  type: Report["type"]
  is_default: boolean
  is_custom: boolean
  sections: ReportSection[]
  styling: ReportStyling
  created_by: string
  created_at: string
  updated_at: string
}

export interface ReportSection {
  id: string
  name: string
  type: "text" | "chart" | "table" | "metrics" | "recommendations" | "gaps"
  order: number
  config: Record<string, any>
  is_required: boolean
}

export interface ReportStyling {
  logo?: string
  colors: {
    primary: string
    secondary: string
    accent: string
  }
  fonts: {
    heading: string
    body: string
  }
  layout: "standard" | "executive" | "detailed"
}

export interface ReportSchedule {
  id: string
  report_config: Omit<Report, "id" | "status" | "created_at" | "updated_at">
  frequency: "daily" | "weekly" | "monthly" | "quarterly" | "yearly"
  day_of_week?: number
  day_of_month?: number
  time: string
  timezone: string
  is_active: boolean
  next_run: string
  last_run?: string
  recipients: string[]
  created_at: string
  updated_at: string
}

export interface ReportAnalytics {
  total_reports: number
  reports_this_month: number
  most_popular_type: string
  average_generation_time: number
  success_rate: number
  download_stats: {
    format: string
    count: number
  }[]
  usage_by_user: {
    user_id: string
    user_name: string
    report_count: number
  }[]
}

export interface Integration {
  id: string
  provider_id: string
  name: string
  description: string
  status: "connected" | "disconnected" | "error" | "pending"
  connection_status: "active" | "inactive" | "expired" | "revoked"
  auth_type: "oauth2" | "api_key" | "basic_auth" | "custom"
  config: Record<string, any>
  credentials?: {
    access_token?: string
    refresh_token?: string
    api_key?: string
    expires_at?: string
  }
  sync_settings: {
    auto_sync: boolean
    sync_frequency: "realtime" | "hourly" | "daily" | "weekly"
    last_sync?: string
    next_sync?: string
  }
  data_mapping: Record<string, string>
  created_at: string
  updated_at: string
  connected_at?: string
  last_activity?: string
  error_message?: string
}

export interface IntegrationProvider {
  id: string
  name: string
  display_name: string
  description: string
  category:
    | "cloud_storage"
    | "identity_provider"
    | "security_tool"
    | "monitoring"
    | "documentation"
    | "ticketing"
    | "other"
  logo_url: string
  website_url: string
  documentation_url: string
  auth_type: "oauth2" | "api_key" | "basic_auth" | "custom"
  supported_features: string[]
  data_types: string[]
  is_popular: boolean
  is_enterprise: boolean
  setup_complexity: "easy" | "medium" | "advanced"
  oauth_config?: {
    authorization_url: string
    token_url: string
    scopes: string[]
    redirect_uri: string
  }
  config_schema: IntegrationConfigField[]
  rate_limits?: {
    requests_per_minute: number
    requests_per_hour: number
    requests_per_day: number
  }
}

export interface IntegrationConfigField {
  name: string
  label: string
  type: "text" | "password" | "select" | "multiselect" | "boolean" | "number" | "url"
  required: boolean
  description?: string
  placeholder?: string
  options?: { label: string; value: string }[]
  validation?: {
    pattern?: string
    min?: number
    max?: number
  }
  sensitive?: boolean
}

export interface IntegrationLog {
  id: string
  integration_id: string
  event_type: "sync" | "auth" | "error" | "config_change" | "connection_test"
  level: "info" | "warning" | "error" | "debug"
  message: string
  details?: Record<string, any>
  timestamp: string
  user_id?: string
}

export interface IntegrationSync {
  id: string
  integration_id: string
  status: "running" | "completed" | "failed" | "cancelled"
  sync_type: "full" | "incremental" | "manual"
  started_at: string
  completed_at?: string
  records_processed: number
  records_created: number
  records_updated: number
  records_failed: number
  error_message?: string
  progress_percentage: number
}

export interface IntegrationAnalytics {
  total_integrations: number
  active_integrations: number
  sync_success_rate: number
  average_sync_time: number
  data_volume_synced: number
  most_used_providers: {
    provider_id: string
    provider_name: string
    usage_count: number
  }[]
  sync_frequency_distribution: {
    frequency: string
    count: number
  }[]
  error_trends: {
    date: string
    error_count: number
  }[]
}

export interface SystemHealth {
  status: "healthy" | "warning" | "critical"
  uptime: number
  last_check: string
  services: {
    database: ServiceStatus
    redis: ServiceStatus
    storage: ServiceStatus
    email: ServiceStatus
    integrations: ServiceStatus
  }
  performance: {
    response_time: number
    cpu_usage: number
    memory_usage: number
    disk_usage: number
  }
}

export interface ServiceStatus {
  status: "healthy" | "warning" | "critical" | "down"
  response_time?: number
  last_check: string
  error_message?: string
}

export interface PerformanceMetrics {
  timestamp: string
  response_time: number
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  active_connections: number
  requests_per_minute: number
  error_rate: number
}

export interface UserActivity {
  id: string
  user_id: string
  user_email: string
  action: string
  resource_type: string
  resource_id?: string
  ip_address: string
  user_agent: string
  timestamp: string
  details?: Record<string, any>
  session_id: string
}

export interface ErrorLog {
  id: string
  level: "error" | "warning" | "info" | "debug"
  message: string
  stack_trace?: string
  user_id?: string
  request_id?: string
  endpoint?: string
  method?: string
  status_code?: number
  timestamp: string
  resolved: boolean
  resolved_by?: string
  resolved_at?: string
  tags: string[]
}

export interface AuditLog {
  id: string
  user_id: string
  user_email: string
  action: string
  resource_type: string
  resource_id: string
  old_values?: Record<string, any>
  new_values?: Record<string, any>
  ip_address: string
  timestamp: string
  compliance_relevant: boolean
  retention_period: number
}

export interface Alert {
  id: string
  type: "system" | "security" | "performance" | "compliance"
  severity: "low" | "medium" | "high" | "critical"
  title: string
  message: string
  source: string
  triggered_at: string
  resolved_at?: string
  resolved_by?: string
  status: "active" | "acknowledged" | "resolved"
  metadata?: Record<string, any>
  notification_sent: boolean
}

export interface MonitoringStats {
  total_users: number
  active_users_24h: number
  total_requests_24h: number
  error_rate_24h: number
  average_response_time: number
  system_uptime: number
  storage_used: number
  storage_total: number
  integrations_active: number
  assessments_completed_24h: number
  evidence_uploaded_24h: number
}

export interface ResourceUsage {
  timestamp: string
  cpu_usage: number
  memory_usage: number
  disk_usage: number
  network_in: number
  network_out: number
  active_connections: number
  queue_size: number
}

export interface ApiError {
  detail: string
  status_code: number
}
