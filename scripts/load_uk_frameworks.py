"""
from __future__ import annotations

UK Compliance Frameworks Data Loader

Loads UK-specific compliance frameworks with ISO 27001 template integration.
"""
import logging
from pathlib import Path
from typing import Dict, Any
import sys
sys.path.append(str(Path(__file__).parent.parent))
from services.compliance_loader import UKComplianceLoader
from database.db_setup import get_db
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_uk_gdpr_framework() ->Dict[str, Any]:
    """Load UK GDPR framework data"""
    return {'name': 'ICO_GDPR_UK', 'display_name':
        'UK GDPR (ICO Implementation)', 'description':
        """
        Data Protection Act 2018 & UK GDPR requirements as enforced by the Information Commissioner's Office (ICO).
        Covers data protection, privacy rights, and security requirements for organizations processing personal data in the UK.
        """
        , 'category': 'Data Protection', 'applicable_indu': ['all'],
        'employee_thresh': 1, 'revenue_thresho': '£0+', 'geographic_scop':
        ['UK', 'England', 'Scotland', 'Wales', 'Northern Ireland'],
        'key_requirement': ['Lawful basis for processing personal data',
        'Data subject rights (access, rectification, erasure, portability)',
        'Data Protection Impact Assessments (DPIAs)',
        'Breach notification (72 hours to ICO, 30 days to individuals)',
        'Privacy by design and by default',
        'Records of processing activities', 'Data processor agreements',
        'International data transfer safeguards',
        'Staff training and awareness',
        'Data retention and disposal policies'], 'control_domains': [
        'Access Control', 'Data Minimization', 'Consent Management',
        'Data Subject Rights', 'Breach Management',
        'Privacy Impact Assessment', 'Data Retention',
        'Third Party Management', 'Staff Training'], 'evidence_types': [
        'Privacy Policy', 'Data Processing Records', 'DPIA Documentation',
        'Staff Training Records', 'Audit Logs',
        'Breach Notification Records', 'Data Processor Agreements',
        'Consent Management Records'], 'relevance_facto': {
        'data_processing': 10, 'personal_data_volume': 8,
        'cross_border_transfers': 7, 'automated_decision_making': 6},
        'complexity_scor': 8, 'implementation_': 16, 'estimated_cost_':
        '£15,000-£75,000', 'policy_template':
        """
        # UK GDPR Privacy Policy Template

        ## 1. Data Controller Information
        [Organization Name]
        [Address]
        [ICO Registration Number]

        ## 2. Legal Basis for Processing
        We process personal data under the following legal bases:
        - Consent (Article 6(1)(a))
        - Contract performance (Article 6(1)(b))
        - Legal obligation (Article 6(1)(c))
        - Legitimate interests (Article 6(1)(f))

        ## 3. Data Subject Rights
        You have the right to:
        - Access your personal data
        - Rectify inaccurate data
        - Erasure ("right to be forgotten")
        - Data portability
        - Object to processing
        - Restrict processing
        """
        , 'version': '1.0'}


def load_fca_framework() ->Dict[str, Any]:
    """Load FCA regulatory framework data"""
    return {'name': 'FCA_REGULATORY', 'display_name':
        'FCA Regulatory Requirements', 'description':
        """
        Financial Conduct Authority requirements for financial services firms.
        Covers consumer protection, market integrity, and operational resilience.
        """
        , 'category': 'Financial Services', 'applicable_indu': [
        'financial_services', 'fintech', 'banking', 'insurance',
        'investment'], 'employee_thresh': 1, 'revenue_thresho': '£0+',
        'geographic_scop': ['UK'], 'key_requirement': [
        'Senior Managers & Certification Regime (SM&CR)',
        'Treating Customers Fairly (TCF)',
        'Operational resilience requirements', 'Financial crime prevention',
        'Data governance and protection', 'Consumer duty obligations',
        'Market conduct rules', 'Prudential requirements',
        'Regulatory reporting', 'Complaints handling'], 'control_domains':
        ['Governance & Oversight', 'Risk Management',
        'Operational Resilience', 'Consumer Protection', 'Financial Crime',
        'Data Management', 'Market Conduct', 'Regulatory Reporting'],
        'evidence_types': ['Governance Policies', 'Risk Assessments',
        'Operational Resilience Plans', 'Consumer Outcomes Reports',
        'Training Records', 'Incident Reports', 'Regulatory Returns',
        'Complaints Logs'], 'complexity_scor': 9, 'implementation_': 24,
        'estimated_cost_': '£25,000-£150,000', 'version': '1.0'}


def load_cyber_essentials_framework() ->Dict[str, Any]:
    """Load Cyber Essentials framework data"""
    return {'name': 'CYBER_ESSENTIALS_UK', 'display_name':
        'Cyber Essentials', 'description':
        """
        UK Government-backed cybersecurity certification scheme.
        Covers basic cyber security controls to protect against common cyber attacks.
        """
        , 'category': 'Cybersecurity', 'applicable_indu': ['all'],
        'employee_thresh': 1, 'revenue_thresho': '£0+', 'geographic_scop':
        ['UK'], 'key_requirement': [
        'Boundary firewalls and internet gateways', 'Secure configuration',
        'Access control', 'Malware protection', 'Patch management'],
        'control_domains': ['Network Security', 'System Configuration',
        'Access Management', 'Malware Protection', 'Patch Management'],
        'evidence_types': ['Network Diagrams', 'Configuration Standards',
        'Access Control Lists', 'Antivirus Reports',
        'Patch Management Logs'], 'complexity_scor': 4, 'implementation_':
        8, 'estimated_cost_': '£2,000-£10,000', 'version': '1.0'}


def load_pci_dss_uk_framework() ->Dict[str, Any]:
    """Load PCI DSS UK implementation framework"""
    return {'name': 'PCI_DSS_UK', 'display_name':
        'PCI DSS (UK Implementation)', 'description':
        """
        Payment Card Industry Data Security Standard for UK organizations handling cardholder data.
        Mandatory for any organization that stores, processes, or transmits payment card data.
        """
        , 'category': 'Financial Services', 'applicable_indu': ['retail',
        'ecommerce', 'financial_services', 'hospitality'],
        'employee_thresh': 1, 'revenue_thresho': '£0+', 'geographic_scop':
        ['UK'], 'key_requirement': [
        'Install and maintain firewall configuration',
        'Do not use vendor-supplied defaults',
        'Protect stored cardholder data',
        'Encrypt transmission of cardholder data',
        'Use and regularly update anti-virus software',
        'Develop and maintain secure systems',
        'Restrict access to cardholder data',
        'Assign unique ID to each user', 'Restrict physical access',
        'Track and monitor access to network resources',
        'Regularly test security systems',
        'Maintain information security policy'], 'control_domains': [
        'Network Security', 'Data Protection', 'Access Control',
        'Monitoring', 'Testing', 'Policy Management'], 'evidence_types': [
        'Network Scans', 'Penetration Test Reports', 'Access Logs',
        'Security Policies', 'Training Records', 'Incident Response Plans'],
        'complexity_scor': 7, 'implementation_': 20, 'estimated_cost_':
        '£20,000-£100,000', 'version': '1.0'}


def load_iso27001_uk_framework() ->Dict[str, Any]:
    """Load ISO 27001 UK-adapted framework with template integration"""
    return {'name': 'ISO27001_UK', 'display_name':
        'ISO 27001:2022 (UK Adaptation)', 'description':
        """
        International standard for Information Security Management Systems (ISMS)
        adapted for UK regulatory context and integrated with ISO 27001 templates.
        """
        , 'category': 'Cybersecurity', 'applicable_indu': ['all'],
        'employee_thresh': 10, 'revenue_thresho': '£1M+', 'geographic_scop':
        ['UK', 'Global'], 'key_requirement': [
        'Information Security Management System (ISMS)',
        'Risk assessment and treatment', 'Statement of Applicability (SoA)',
        'Information security policy', 'Asset inventory and classification',
        'Access control management', 'Cryptography controls',
        'Physical and environmental security', 'Operations security',
        'Communications security', 'System acquisition and development',
        'Supplier relationships', 'Incident management',
        'Business continuity', 'Compliance monitoring'], 'control_domains':
        ['Information Security Policies',
        'Organization of Information Security', 'Human Resource Security',
        'Asset Management', 'Access Control', 'Cryptography',
        'Physical Security', 'Operations Security',
        'Communications Security', 'System Development',
        'Supplier Relationships', 'Incident Management',
        'Business Continuity', 'Compliance'], 'evidence_types': [
        'ISMS Documentation', 'Risk Assessment Reports',
        'Statement of Applicability', 'Security Policies', 'Audit Reports',
        'Training Records', 'Incident Reports', 'Business Continuity Plans'
        ], 'complexity_scor': 9, 'implementation_': 32, 'estimated_cost_':
        '£50,000-£200,000', 'version': '1.0'}


def main() ->Any:
    """Main function to load UK compliance frameworks"""
    logger.info('Starting UK compliance frameworks loading...')
    db_session = next(get_db())
    loader = UKComplianceLoader(db_session=db_session)
    frameworks_data = [load_uk_gdpr_framework(), load_fca_framework(),
        load_cyber_essentials_framework(), load_pci_dss_uk_framework(),
        load_iso27001_uk_framework()]
    result = loader.load_frameworks(frameworks_data)
    logger.info('Loading completed:')
    logger.info('  Total processed: %s' % result.total_processed)
    logger.info('  Successfully loaded: %s' % len(result.loaded_frameworks))
    logger.info('  Skipped (already exist): %s' % len(result.
        skipped_frameworks))
    logger.info('  Errors: %s' % len(result.errors))
    if result.loaded_frameworks:
        logger.info('Loaded frameworks:')
        for framework in result.loaded_frameworks:
            logger.info('  - %s: %s' % (framework.name, framework.display_name),
                )
    if result.skipped_frameworks:
        logger.info('Skipped frameworks:')
        for name in result.skipped_frameworks:
            logger.info('  - %s' % name)
    if result.errors:
        logger.error('Errors encountered:')
        for error in result.errors:
            logger.error('  - %s' % error)
    db_session.close()
    return result.success


if __name__ == '__main__':
    success = main()
    if success:
        logger.info('✅ UK compliance frameworks loaded successfully')
    else:
        logger.error('❌ Failed to load UK compliance frameworks')
        sys.exit(1)
