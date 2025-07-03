/**
 * Test data fixtures for E2E tests
 */

export const TEST_USERS = {
  VALID_USER: {
    email: 'test.user@ruleiq.com',
    password: 'TestPassword123!',
    fullName: 'Test User',
    company: 'Test Company Ltd'
  },
  ADMIN_USER: {
    email: 'admin@ruleiq.com',
    password: 'AdminPassword123!',
    fullName: 'Admin User',
    company: 'ruleIQ Admin'
  },
  NEW_USER: {
    email: `new.user.${Date.now()}@ruleiq.com`,
    password: 'NewUserPassword123!',
    fullName: 'New Test User',
    company: 'New Test Company'
  }
} as const;

export const BUSINESS_PROFILES = {
  TECH_STARTUP: {
    companyName: 'TechStart Solutions',
    industry: 'Technology',
    employeeCount: '10-50',
    dataTypes: ['personal_data', 'financial_data', 'health_data'],
    description: 'A technology startup focused on SaaS solutions',
    website: 'https://techstart.example.com',
    address: {
      street: '123 Tech Street',
      city: 'London',
      postcode: 'SW1A 1AA',
      country: 'United Kingdom'
    }
  },
  FINANCIAL_SERVICES: {
    companyName: 'FinServ Corp',
    industry: 'Financial Services',
    employeeCount: '100-500',
    dataTypes: ['personal_data', 'financial_data', 'payment_data'],
    description: 'Financial services company providing investment advice',
    website: 'https://finserv.example.com',
    address: {
      street: '456 Finance Avenue',
      city: 'Edinburgh',
      postcode: 'EH1 1AA',
      country: 'United Kingdom'
    }
  },
  HEALTHCARE: {
    companyName: 'HealthCare Plus',
    industry: 'Healthcare',
    employeeCount: '50-100',
    dataTypes: ['personal_data', 'health_data', 'sensitive_data'],
    description: 'Healthcare provider with digital health solutions',
    website: 'https://healthcare.example.com',
    address: {
      street: '789 Health Road',
      city: 'Manchester',
      postcode: 'M1 1AA',
      country: 'United Kingdom'
    }
  }
} as const;

export const ASSESSMENT_DATA = {
  GDPR_BASIC: {
    frameworkName: 'GDPR',
    assessmentType: 'basic',
    questions: [
      {
        questionId: 'gdpr-1',
        question: 'Do you process personal data?',
        answer: 'yes'
      },
      {
        questionId: 'gdpr-2',
        question: 'Do you have a privacy policy?',
        answer: 'yes'
      },
      {
        questionId: 'gdpr-3',
        question: 'Do you obtain consent for data processing?',
        answer: 'yes'
      }
    ]
  },
  ISO27001_COMPREHENSIVE: {
    frameworkName: 'ISO 27001',
    assessmentType: 'comprehensive',
    questions: [
      {
        questionId: 'iso-1',
        question: 'Do you have an information security policy?',
        answer: 'yes'
      },
      {
        questionId: 'iso-2',
        question: 'Do you conduct regular security risk assessments?',
        answer: 'partially'
      },
      {
        questionId: 'iso-3',
        question: 'Do you have incident response procedures?',
        answer: 'no'
      }
    ]
  }
} as const;

export const EVIDENCE_DATA = {
  POLICY_DOCUMENT: {
    title: 'Privacy Policy Document',
    description: 'Company privacy policy for GDPR compliance',
    fileName: 'privacy-policy.pdf',
    fileType: 'application/pdf',
    category: 'policy',
    tags: ['gdpr', 'privacy', 'policy']
  },
  SECURITY_CERTIFICATE: {
    title: 'ISO 27001 Certificate',
    description: 'ISO 27001 certification document',
    fileName: 'iso27001-cert.pdf',
    fileType: 'application/pdf',
    category: 'certificate',
    tags: ['iso27001', 'security', 'certificate']
  },
  TRAINING_RECORD: {
    title: 'Staff Training Records',
    description: 'Records of security awareness training',
    fileName: 'training-records.xlsx',
    fileType: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    category: 'training',
    tags: ['training', 'security', 'awareness']
  }
} as const;

export const POLICY_TEMPLATES = {
  PRIVACY_POLICY: {
    name: 'Privacy Policy',
    type: 'privacy',
    framework: 'GDPR',
    sections: [
      'Data Collection',
      'Data Processing',
      'Data Subject Rights',
      'Data Retention',
      'Contact Information'
    ]
  },
  SECURITY_POLICY: {
    name: 'Information Security Policy',
    type: 'security',
    framework: 'ISO 27001',
    sections: [
      'Security Objectives',
      'Risk Management',
      'Access Control',
      'Incident Response',
      'Business Continuity'
    ]
  }
} as const;

export const INTEGRATION_DATA = {
  SLACK: {
    name: 'Slack',
    type: 'communication',
    webhookUrl: 'https://hooks.slack.com/test-webhook',
    channels: ['#compliance', '#alerts']
  },
  MICROSOFT_365: {
    name: 'Microsoft 365',
    type: 'productivity',
    tenantId: 'test-tenant-id',
    clientId: 'test-client-id'
  }
} as const;

export const DASHBOARD_DATA = {
  WIDGETS: [
    {
      id: 'compliance-score',
      type: 'score',
      title: 'Compliance Score',
      position: { x: 0, y: 0, w: 6, h: 4 }
    },
    {
      id: 'framework-progress',
      type: 'progress',
      title: 'Framework Progress',
      position: { x: 6, y: 0, w: 6, h: 4 }
    },
    {
      id: 'pending-tasks',
      type: 'tasks',
      title: 'Pending Tasks',
      position: { x: 0, y: 4, w: 4, h: 6 }
    },
    {
      id: 'activity-feed',
      type: 'activity',
      title: 'Recent Activity',
      position: { x: 4, y: 4, w: 4, h: 6 }
    },
    {
      id: 'upcoming-deadlines',
      type: 'deadlines',
      title: 'Upcoming Deadlines',
      position: { x: 8, y: 4, w: 4, h: 6 }
    },
    {
      id: 'ai-insights',
      type: 'insights',
      title: 'AI Insights',
      position: { x: 0, y: 10, w: 12, h: 4 }
    }
  ]
} as const;

export const API_RESPONSES = {
  LOGIN_SUCCESS: {
    access_token: 'mock-access-token',
    refresh_token: 'mock-refresh-token',
    user: {
      id: '1',
      email: 'test@example.com',
      full_name: 'Test User',
      is_active: true,
      created_at: '2024-01-01T00:00:00Z'
    }
  },
  DASHBOARD_DATA: {
    stats: {
      compliance_score: 85,
      total_assessments: 5,
      completed_assessments: 3,
      pending_tasks: 12
    },
    recent_activity: [
      {
        id: '1',
        type: 'assessment_completed',
        title: 'GDPR Assessment Completed',
        timestamp: '2024-01-01T10:00:00Z'
      }
    ],
    pending_tasks: [
      {
        id: '1',
        title: 'Update Privacy Policy',
        priority: 'high',
        due_date: '2024-01-15T00:00:00Z'
      }
    ]
  }
} as const;

/**
 * Generate random test data
 */
export const generateTestData = {
  user: () => ({
    email: `test.${Date.now()}@example.com`,
    password: 'TestPassword123!',
    fullName: `Test User ${Date.now()}`,
    company: `Test Company ${Date.now()}`
  }),
  
  businessProfile: () => ({
    companyName: `Test Company ${Date.now()}`,
    industry: 'Technology',
    employeeCount: '10-50',
    dataTypes: ['personal_data'],
    description: 'Test company description'
  }),
  
  evidence: () => ({
    title: `Test Evidence ${Date.now()}`,
    description: 'Test evidence description',
    category: 'policy',
    tags: ['test']
  })
};
