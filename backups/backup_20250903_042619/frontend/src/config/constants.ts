/**
 * Application-wide constants
 */

export const APP_NAME = 'ruleIQ';
export const APP_DESCRIPTION = 'AI-powered compliance automation platform for UK SMBs';

// API Configuration
export const API_VERSION = 'v1';
export const API_TIMEOUT = 30000; // 30 seconds
export const API_RETRY_ATTEMPTS = 3;
export const API_RETRY_DELAY = 1000; // 1 second

// Authentication
export const AUTH_TOKEN_KEY = 'ruleiq_auth_token';
export const REFRESH_TOKEN_KEY = 'ruleiq_refresh_token';
export const USER_KEY = 'ruleiq_user';

// UI/UX Constants
export const TOAST_DURATION = 5000; // 5 seconds
export const DEBOUNCE_DELAY = 300; // 300ms
export const ANIMATION_DURATION = 200; // 200ms
export const SKELETON_PULSE_DURATION = 1500; // 1.5 seconds

// Pagination
export const DEFAULT_PAGE_SIZE = 10;
export const PAGE_SIZE_OPTIONS = [10, 25, 50, 100];

// File Upload
export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
export const ACCEPTED_FILE_TYPES = {
  documents: ['.pdf', '.doc', '.docx', '.txt', '.csv', '.xlsx', '.xls'],
  images: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
  all: ['*'],
};

// Feature Flags (will be overridden by env vars)
export const FEATURES = {
  CHAT: true,
  POLICIES: true,
  ASSESSMENTS: true,
  EVIDENCE: true,
  REPORTS: true,
  INTEGRATIONS: true,
  TEAM_MANAGEMENT: true,
};

// Compliance Frameworks
export const COMPLIANCE_FRAMEWORKS = [
  { id: 'gdpr', name: 'GDPR', description: 'General Data Protection Regulation' },
  { id: 'iso27001', name: 'ISO 27001', description: 'Information Security Management' },
  { id: 'soc2', name: 'SOC 2', description: 'Service Organization Control 2' },
  { id: 'pci-dss', name: 'PCI DSS', description: 'Payment Card Industry Data Security Standard' },
  {
    id: 'hipaa',
    name: 'HIPAA',
    description: 'Health Insurance Portability and Accountability Act',
  },
  { id: 'fca', name: 'FCA', description: 'Financial Conduct Authority' },
] as const;

// Status Types
export const STATUS = {
  IDLE: 'idle',
  LOADING: 'loading',
  SUCCESS: 'success',
  ERROR: 'error',
} as const;

// Priority Levels
export const PRIORITY_LEVELS = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  CRITICAL: 'critical',
} as const;

// Assessment Status
export const ASSESSMENT_STATUS = {
  SCHEDULED: 'Scheduled',
  IN_PROGRESS: 'In Progress',
  UNDER_REVIEW: 'Under Review',
  COMPLETED: 'Completed',
  OVERDUE: 'Overdue',
} as const;
