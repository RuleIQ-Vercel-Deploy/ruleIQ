/**
 * Type definitions for testing utilities and mocks
 */

import { type RenderOptions } from '@testing-library/react';

// Test utilities types
export interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  preloadedState?: any;
  store?: any;
  wrapper?: React.ComponentType<any>;
}

export interface TestUser {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  role?: string;
  created_at?: string;
  updated_at?: string;
}

export interface TestBusinessProfile {
  id?: string;
  company_name: string;
  industry: string;
  employee_count: string;
  data_types: string[];
  description?: string;
  website?: string;
  address?: {
    street: string;
    city: string;
    postcode: string;
    country: string;
  };
  created_at?: string;
  updated_at?: string;
}

export interface TestAssessment {
  id?: string;
  framework_name: string;
  assessment_type: 'basic' | 'comprehensive';
  status: 'draft' | 'in_progress' | 'completed';
  score?: number;
  questions: TestQuestion[];
  answers: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

export interface TestQuestion {
  id: string;
  text: string;
  type: 'boolean' | 'multiple' | 'single' | 'text';
  required: boolean;
  options?: TestQuestionOption[];
  category?: string;
  weight?: number;
}

export interface TestQuestionOption {
  value: string;
  label: string;
  score?: number;
}

export interface TestEvidence {
  id?: string;
  title: string;
  description?: string;
  file_name: string;
  file_type: string;
  file_size?: number;
  category: string;
  tags: string[];
  status: 'pending' | 'approved' | 'rejected';
  uploaded_by?: string;
  uploaded_at?: string;
  approved_by?: string;
  approved_at?: string;
}

export interface TestApiResponse<T = any> {
  data: T;
  message: string;
  status: number;
}

export interface TestPaginatedResponse<T = any> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface TestAuthResponse {
  access_token: string;
  refresh_token: string;
  user: TestUser;
}

export interface TestDashboardData {
  stats: {
    compliance_score: number;
    total_assessments: number;
    completed_assessments: number;
    pending_tasks: number;
  };
  recent_activity: TestActivity[];
  pending_tasks: TestTask[];
  frameworks: TestFramework[];
}

export interface TestActivity {
  id: string;
  type: string;
  title: string;
  description?: string;
  timestamp: string;
  user_id?: string;
  metadata?: Record<string, any>;
}

export interface TestTask {
  id: string;
  title: string;
  description?: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'in_progress' | 'completed';
  due_date?: string;
  assigned_to?: string;
  created_at: string;
}

export interface TestFramework {
  id: string;
  name: string;
  category: string;
  description: string;
  estimated_time: number;
  question_count: number;
  is_recommended: boolean;
}

// Mock function types
export interface MockApiClient {
  get: jest.MockedFunction<any>;
  post: jest.MockedFunction<any>;
  put: jest.MockedFunction<any>;
  patch: jest.MockedFunction<any>;
  delete: jest.MockedFunction<any>;
}

export interface MockAuthService {
  login: jest.MockedFunction<any>;
  register: jest.MockedFunction<any>;
  logout: jest.MockedFunction<any>;
  refreshToken: jest.MockedFunction<any>;
  getCurrentUser: jest.MockedFunction<any>;
  requestPasswordReset: jest.MockedFunction<any>;
  resetPassword: jest.MockedFunction<any>;
  verifyEmail: jest.MockedFunction<any>;
  updateProfile: jest.MockedFunction<any>;
  changePassword: jest.MockedFunction<any>;
}

export interface MockRouter {
  push: jest.MockedFunction<any>;
  replace: jest.MockedFunction<any>;
  back: jest.MockedFunction<any>;
  forward: jest.MockedFunction<any>;
  refresh: jest.MockedFunction<any>;
  prefetch: jest.MockedFunction<any>;
}

export interface MockToast {
  toast: jest.MockedFunction<any>;
  dismiss: jest.MockedFunction<any>;
}

// Test helper types
export interface TestHelperOptions {
  timeout?: number;
  retries?: number;
  skipAuth?: boolean;
  mockApi?: boolean;
}

export interface PerformanceTestResult {
  metric: string;
  value: number;
  threshold: number;
  passed: boolean;
  timestamp: number;
}

export interface AccessibilityTestResult {
  violations: unknown[];
  passes: unknown[];
  incomplete: unknown[];
  inapplicable: unknown[];
  url: string;
  timestamp: number;
}

export interface VisualTestResult {
  name: string;
  passed: boolean;
  diff?: {
    pixels: number;
    percentage: number;
  };
  screenshot?: string;
  baseline?: string;
  timestamp: number;
}

// Store test types
export interface TestStoreState {
  auth: {
    user: TestUser | null;
    isAuthenticated: boolean;
    isLoading: boolean;
    error: string | null;
  };
  businessProfile: {
    profile: TestBusinessProfile | null;
    isLoading: boolean;
    error: string | null;
    currentStep: number;
    formData: Partial<TestBusinessProfile>;
  };
  assessments: {
    assessments: TestAssessment[];
    currentAssessment: TestAssessment | null;
    isLoading: boolean;
    error: string | null;
  };
  evidence: {
    evidence: TestEvidence[];
    isLoading: boolean;
    error: string | null;
    uploadProgress: number;
  };
}

// Component test props
export interface TestComponentProps {
  children?: React.ReactNode;
  className?: string;
  testId?: string;
  [key: string]: any;
}

// Form test types
export interface TestFormData {
  [key: string]: any;
}

export interface TestFormErrors {
  [key: string]: string | string[];
}

export interface TestFormState {
  data: TestFormData;
  errors: TestFormErrors;
  isSubmitting: boolean;
  isValid: boolean;
  touched: Record<string, boolean>;
}

// API test types
export interface TestApiEndpoint {
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  url: string;
  headers?: Record<string, string>;
  body?: any;
  response?: any;
  status?: number;
  delay?: number;
}

export interface TestApiMock {
  endpoints: TestApiEndpoint[];
  baseUrl: string;
  defaultHeaders: Record<string, string>;
  defaultDelay: number;
}

// E2E test types
export interface TestPageObject {
  navigate: (path: string) => Promise<void>;
  waitForElement: (selector: string) => Promise<void>;
  clickElement: (selector: string) => Promise<void>;
  fillField: (selector: string, value: string) => Promise<void>;
  submitForm: (selector: string) => Promise<void>;
  takeScreenshot: (name: string) => Promise<void>;
}

export interface TestScenario {
  name: string;
  description: string;
  steps: TestStep[];
  expectedResult: string;
  tags: string[];
}

export interface TestStep {
  action: string;
  target?: string;
  value?: string;
  expected?: string;
  timeout?: number;
}

// Global test types
declare global {
  namespace jest {
    interface Matchers<R> {
      toHaveNoViolations(): R;
      toBeAccessible(): R;
      toMatchVisualBaseline(): R;
      toMeetPerformanceThreshold(threshold: number): R;
    }
  }

  interface Window {
    gtag?: (...args: unknown[]) => void;
    dataLayer?: unknown[];
    performance: Performance & {
      memory?: {
        usedJSHeapSize: number;
        totalJSHeapSize: number;
        jsHeapSizeLimit: number;
      };
    };
  }
}

export {};
