import { apiClient } from './client';

import type { ComplianceFramework } from '@/types/api';
import type { AssessmentFramework } from '@/lib/assessment-engine/types';

export interface FrameworkRecommendation {
  framework: ComplianceFramework;
  relevance_score: number;
  reasons: string[];
  estimated_effort: string;
  priority: 'high' | 'medium' | 'low';
}

/**
 * Helper to normalize section IDs for consistent comparison
 * Converts to lowercase and replaces spaces/underscores with hyphens
 */
export function normalizeSectionId(id: string): string {
  return id
    .toLowerCase()
    .replace(/[\s_]/g, '-')
    .replace(/[^\w-]/g, ''); // Remove non-alphanumeric chars except hyphens
}

class FrameworkService {
  /**
   * Get all available compliance frameworks
   */
  async getFrameworks(): Promise<ComplianceFramework[]> {
    const response = await apiClient.get<ComplianceFramework[]>('/frameworks');
    return response;
  }

  /**
   * Get a specific framework by ID
   */
  async getFramework(id: string): Promise<ComplianceFramework> {
    const response = await apiClient.get<ComplianceFramework>(`/frameworks/${id}`);
    return response;
  }

  /**
   * Get framework recommendations based on business profile
   */
  async getFrameworkRecommendations(businessProfileId: string): Promise<FrameworkRecommendation[]> {
    const response = await apiClient.get<FrameworkRecommendation[]>(
      `/frameworks/recommendations/${businessProfileId}`,
    );
    return response;
  }

  /**
   * Get framework controls
   */
  async getFrameworkControls(frameworkId: string): Promise<{
    framework: string;
    total_controls: number;
    controls: Array<{
      control_id: string;
      control_name: string;
      description: string;
      category: string;
      priority: string;
      evidence_required: string[];
    }>;
  }> {
    return await apiClient.get(`/frameworks/${frameworkId}/controls`);
  }

  /**
   * Get framework implementation guide
   */
  async getFrameworkImplementationGuide(frameworkId: string): Promise<{
    framework: string;
    estimated_duration: string;
    phases: Array<{
      phase: number;
      name: string;
      duration: string;
      tasks: string[];
      deliverables: string[];
    }>;
    resources_required: string[];
    key_milestones: string[];
  }> {
    return await apiClient.get(`/frameworks/${frameworkId}/implementation-guide`);
  }

  /**
   * Get framework compliance status
   */
  async getFrameworkComplianceStatus(
    frameworkId: string,
    businessProfileId: string,
  ): Promise<{
    framework: string;
    overall_compliance: number;
    by_category: Record<string, number>;
    controls_status: {
      compliant: number;
      partial: number;
      non_compliant: number;
      not_assessed: number;
    };
    last_assessment_date?: string;
    next_review_date?: string;
  }> {
    return await apiClient.get(`/frameworks/${frameworkId}/compliance-status`, {
      params: { business_profile_id: businessProfileId },
    });
  }

  /**
   * Compare multiple frameworks
   */
  async compareFrameworks(frameworkIds: string[]): Promise<{
    frameworks: Array<{
      id: string;
      name: string;
      control_count: number;
      estimated_effort: string;
      industry_alignment: string[];
      key_features: string[];
    }>;
    overlap_analysis: {
      common_controls: number;
      unique_controls: Record<string, number>;
      compatibility_score: number;
    };
    recommendation: string;
  }> {
    return await apiClient.post('/frameworks/compare', {
      framework_ids: frameworkIds,
    });
  }

  /**
   * Get framework maturity assessment
   */
  async getFrameworkMaturityAssessment(
    frameworkId: string,
    businessProfileId: string,
  ): Promise<{
    framework: string;
    maturity_level: 'initial' | 'developing' | 'defined' | 'managed' | 'optimized';
    maturity_score: number;
    strengths: string[];
    weaknesses: string[];
    improvement_areas: Array<{
      area: string;
      current_level: number;
      target_level: number;
      recommendations: string[];
    }>;
  }> {
    return await apiClient.get(`/frameworks/${frameworkId}/maturity-assessment`, {
      params: { business_profile_id: businessProfileId },
    });
  }

  /**
   * Get default assessment framework for freemium users
   */
  getDefaultFramework(): AssessmentFramework {
    return {
      id: 'freemium-default',
      name: 'Basic Compliance Assessment',
      description: 'A comprehensive assessment covering fundamental compliance areas for businesses',
      version: '1.0.0',
      scoringMethod: 'percentage',
      passingScore: 70,
      estimatedDuration: 15,
      tags: ['freemium', 'basic', 'compliance'],
      sections: [
        {
          id: 'data-protection',
          title: 'Data Protection',
          description: 'Assess your organization\'s data protection practices and policies',
          order: 1,
          questions: [
            {
              id: 'dp-001',
              type: 'radio',
              text: 'Does your organization have a formal data protection policy?',
              description: 'A data protection policy outlines how personal data is collected, processed, and stored',
              section: 'data-protection',
              weight: 3,
              validation: { required: true },
              metadata: {
                ai_hint: 'Consider GDPR Article 5 principles and UK Data Protection Act requirements',
                evidence_required: ['Policy document', 'Approval records', 'Review schedule'],
                regulatory_references: ['GDPR Article 5', 'UK DPA 2018'],
              },
              options: [
                { value: 'yes', label: 'Yes, we have a comprehensive policy' },
                { value: 'partial', label: 'Yes, but it needs updating' },
                { value: 'no', label: 'No, we don\'t have a policy' }
              ]
            },
            {
              id: 'dp-002',
              type: 'radio',
              text: 'How do you handle data subject requests (access, deletion, portability)?',
              description: 'Data subject rights are fundamental to privacy regulations like GDPR',
              section: 'data-protection',
              weight: 3,
              validation: { required: true },
              metadata: {
                ai_hint: 'GDPR requires response within 30 days for data subject requests',
                evidence_required: ['Process documentation', 'Request logs', 'Response templates'],
                regulatory_references: ['GDPR Articles 15-22'],
              },
              options: [
                { value: 'automated', label: 'Automated system with defined processes' },
                { value: 'manual', label: 'Manual process with documented procedures' },
                { value: 'adhoc', label: 'Ad-hoc handling without formal process' },
                { value: 'none', label: 'No process in place' }
              ]
            },
            {
              id: 'dp-003',
              type: 'checkbox',
              text: 'Which data protection measures do you currently have in place?',
              description: 'Select all that apply to your current data protection practices',
              section: 'data-protection',
              weight: 2,
              validation: { required: true, min: 1 },
              metadata: {
                ai_hint: 'Multiple technical and organizational measures strengthen data protection',
                evidence_required: ['Implementation records', 'Technical specifications'],
              },
              options: [
                { value: 'encryption', label: 'Data encryption at rest and in transit' },
                { value: 'anonymization', label: 'Data anonymization/pseudonymization' },
                { value: 'retention', label: 'Data retention policies' },
                { value: 'consent', label: 'Consent management system' },
                { value: 'dpia', label: 'Data Protection Impact Assessments (DPIA)' }
              ]
            }
          ]
        },
        {
          id: 'security-controls',
          title: 'Security Controls',
          description: 'Evaluate your organization\'s security controls and infrastructure',
          order: 2,
          questions: [
            {
              id: 'sc-001',
              type: 'radio',
              text: 'What type of security framework does your organization follow?',
              description: 'Security frameworks provide structured approaches to cybersecurity',
              section: 'security-controls',
              weight: 3,
              validation: { required: true },
              metadata: {
                ai_hint: 'Established frameworks demonstrate security maturity and best practices adoption',
                evidence_required: ['Framework documentation', 'Implementation evidence'],
                regulatory_references: ['ISO 27001', 'NIST CSF', 'Cyber Essentials'],
              },
              options: [
                { value: 'iso27001', label: 'ISO 27001' },
                { value: 'nist', label: 'NIST Cybersecurity Framework' },
                { value: 'custom', label: 'Custom internal framework' },
                { value: 'none', label: 'No formal framework' }
              ]
            },
            {
              id: 'sc-002',
              type: 'scale',
              text: 'How would you rate your organization\'s incident response capabilities?',
              description: 'Rate from 1 (no capabilities) to 5 (fully mature)',
              section: 'security-controls',
              weight: 2,
              validation: { required: true, min: 1, max: 5 },
              scaleMin: 1,
              scaleMax: 5,
              scaleLabels: { min: 'No capabilities', max: 'Fully mature' },
              metadata: {
                ai_hint: 'Consider response time, documentation, team training, and testing frequency',
                evidence_required: ['Incident response plan', 'Response team structure', 'Test records'],
              }
            },
            {
              id: 'sc-003',
              type: 'checkbox',
              text: 'Which security controls are currently implemented?',
              description: 'Select all security controls your organization has in place',
              section: 'security-controls',
              weight: 2,
              validation: { required: true, min: 1 },
              metadata: {
                ai_hint: 'Defense in depth requires multiple layers of security controls',
                evidence_required: ['Configuration evidence', 'Deployment records'],
              },
              options: [
                { value: 'firewall', label: 'Network firewalls' },
                { value: 'antivirus', label: 'Endpoint protection/antivirus' },
                { value: 'monitoring', label: 'Security monitoring and logging' },
                { value: 'backup', label: 'Regular data backups' },
                { value: 'vulnerability', label: 'Vulnerability management' },
                { value: 'penetration', label: 'Regular penetration testing' }
              ]
            }
          ]
        },
        {
          id: 'access-management',
          title: 'Access Management',
          description: 'Review your organization\'s access control and identity management practices',
          order: 3,
          questions: [
            {
              id: 'am-001',
              type: 'radio',
              text: 'Does your organization implement multi-factor authentication (MFA)?',
              description: 'MFA adds an extra layer of security beyond passwords',
              section: 'access-management',
              weight: 3,
              validation: { required: true },
              metadata: {
                ai_hint: 'MFA is critical for preventing unauthorized access and meeting compliance requirements',
                evidence_required: ['MFA configuration', 'Coverage reports', 'Policy documentation'],
                regulatory_references: ['NIST 800-63B', 'PCI DSS 8.3'],
              },
              options: [
                { value: 'all', label: 'Yes, for all users and systems' },
                { value: 'critical', label: 'Yes, for critical systems only' },
                { value: 'some', label: 'Yes, for some users/systems' },
                { value: 'no', label: 'No, not implemented' }
              ]
            },
            {
              id: 'am-002',
              type: 'radio',
              text: 'How frequently do you review user access permissions?',
              description: 'Regular access reviews help maintain the principle of least privilege',
              section: 'access-management',
              weight: 2,
              validation: { required: true },
              metadata: {
                ai_hint: 'Regular reviews prevent privilege creep and maintain security posture',
                evidence_required: ['Review schedule', 'Review records', 'Remediation actions'],
              },
              options: [
                { value: 'monthly', label: 'Monthly' },
                { value: 'quarterly', label: 'Quarterly' },
                { value: 'annually', label: 'Annually' },
                { value: 'adhoc', label: 'Ad-hoc/when needed' },
                { value: 'never', label: 'Never/rarely' }
              ]
            },
            {
              id: 'am-003',
              type: 'radio',
              text: 'Do you have a formal process for onboarding and offboarding employees?',
              description: 'Proper onboarding/offboarding ensures appropriate access provisioning and deprovisioning',
              section: 'access-management',
              weight: 3,
              validation: { required: true },
              metadata: {
                ai_hint: 'Timely access management reduces insider threat risk',
                evidence_required: ['Process documentation', 'Checklists', 'Completion records'],
              },
              options: [
                { value: 'automated', label: 'Yes, fully automated process' },
                { value: 'documented', label: 'Yes, documented manual process' },
                { value: 'informal', label: 'Informal process exists' },
                { value: 'none', label: 'No formal process' }
              ]
            }
          ]
        },
        {
          id: 'documentation',
          title: 'Documentation',
          description: 'Assess the completeness and quality of your compliance documentation',
          order: 4,
          questions: [
            {
              id: 'doc-001',
              type: 'checkbox',
              text: 'Which types of compliance documentation do you maintain?',
              description: 'Select all types of documentation your organization maintains',
              section: 'documentation',
              weight: 1,
              validation: { required: true },
              options: [
                { value: 'policies', label: 'Security and privacy policies' },
                { value: 'procedures', label: 'Standard operating procedures' },
                { value: 'risk', label: 'Risk assessment documentation' },
                { value: 'incident', label: 'Incident response procedures' },
                { value: 'training', label: 'Employee training records' },
                { value: 'audit', label: 'Audit and compliance reports' }
              ]
            },
            {
              id: 'doc-002',
              type: 'radio',
              text: 'How often do you review and update your compliance documentation?',
              description: 'Regular updates ensure documentation remains current and effective',
              section: 'documentation',
              weight: 1,
              validation: { required: true },
              options: [
                { value: 'quarterly', label: 'Quarterly' },
                { value: 'biannually', label: 'Twice per year' },
                { value: 'annually', label: 'Annually' },
                { value: 'adhoc', label: 'Only when required' },
                { value: 'never', label: 'Rarely or never' }
              ]
            },
            {
              id: 'doc-003',
              type: 'scale',
              text: 'How accessible is your compliance documentation to relevant staff?',
              description: 'Rate from 1 (very difficult to access) to 5 (easily accessible)',
              section: 'documentation',
              weight: 1,
              validation: { required: true },
              scaleMin: 1,
              scaleMax: 5,
              scaleLabels: { min: 'Very difficult', max: 'Easily accessible' }
            }
          ]
        }
      ]
    };
  }
}

export const frameworkService = new FrameworkService();
