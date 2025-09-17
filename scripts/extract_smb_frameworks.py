"""
Extract SMB-relevant framework obligations from ISO standards and other frameworks.
Based on actual content fetched from official sources.
"""
import logging
logger = logging.getLogger(__name__)
import json
from pathlib import Path
from datetime import datetime
from typing import Any
import hashlib
SMB_FRAMEWORKS = {'ISO 27001:2022': {'title':
    'Information Security Management System', 'source':
    'https://www.iso.org/standard/27001', 'core_principles': [
    'Confidentiality', 'Integrity', 'Availability'], 'obligations': [{'id':
    'ISO27001-SMB-001', 'title':
    'Establish Information Security Management System', 'description':
    'Establish an ISMS to ensure confidentiality, integrity and availability of information'
    , 'requirement':
    'Organizations must establish, implement, maintain and continually improve an information security management system'
    , 'smb_guidance':
    'Scale ISMS implementation to organization size and complexity',
    'category': 'ISMS Establishment', 'priority': 'critical'}, {'id':
    'ISO27001-SMB-002', 'title': 'Risk-Based Security Approach',
    'description':
    "Apply a risk management process adapted to organization's size",
    'requirement':
    'Implement risk assessment and treatment processes to identify and address security risks'
    , 'smb_guidance':
    'Use simplified risk assessment methodology appropriate for SMB resources',
    'category': 'Risk Management', 'priority': 'critical'}, {'id':
    'ISO27001-SMB-003', 'title': 'Secure All Information Formats',
    'description':
    'Secure information across all formats (paper, cloud, digital)',
    'requirement':
    'Protection must cover all forms of information regardless of storage medium'
    , 'smb_guidance': 'Focus on most critical information assets first',
    'category': 'Information Protection', 'priority': 'high'}, {'id':
    'ISO27001-SMB-004', 'title': 'Prepare People, Processes and Technology',
    'description':
    'Prepare people, processes, and technology to face cyber risks',
    'requirement':
    'Integrate security awareness and controls across human, process and technical dimensions'
    , 'smb_guidance':
    'Prioritize employee training and basic technical controls', 'category':
    'Security Integration', 'priority': 'high'}, {'id': 'ISO27001-SMB-005',
    'title': 'Management Oversight', 'description':
    'Ensure management oversight to protect organizational data',
    'requirement':
    'Top management must demonstrate leadership and commitment to the ISMS',
    'smb_guidance':
    'Assign clear security responsibilities even in small teams',
    'category': 'Leadership', 'priority': 'critical'}, {'id':
    'ISO27001-SMB-006', 'title': 'Context Understanding', 'description':
    'Determine external and internal issues relevant to ISMS',
    'requirement':
    'Organization must understand its context and stakeholder requirements',
    'smb_guidance': 'Document key business relationships and dependencies',
    'category': 'Context', 'priority': 'medium'}, {'id': 'ISO27001-SMB-007',
    'title': 'Scope Definition', 'description':
    'Define boundaries and applicability of ISMS', 'requirement':
    'Clearly define what is included and excluded from ISMS scope',
    'smb_guidance':
    'Start with core business processes and expand gradually', 'category':
    'Scope', 'priority': 'high'}, {'id': 'ISO27001-SMB-008', 'title':
    'Continuous Improvement', 'description':
    'Continuously identify and address evolving security risks',
    'requirement':
    'Implement processes for continual improvement of the ISMS',
    'smb_guidance': 'Regular quarterly reviews suitable for SMBs',
    'category': 'Improvement', 'priority': 'medium'}, {'id':
    'ISO27001-SMB-009', 'title': 'Incident Response', 'description':
    'Establish incident management procedures', 'requirement':
    'Define and implement information security incident management processes',
    'smb_guidance':
    'Create simple incident response checklist and contact list',
    'category': 'Incident Management', 'priority': 'critical'}, {'id':
    'ISO27001-SMB-010', 'title': 'Access Control', 'description':
    'Implement access control based on business requirements',
    'requirement':
    'Limit access to information and information processing facilities',
    'smb_guidance': 'Use role-based access control with regular reviews',
    'category': 'Access Management', 'priority': 'critical'}]},
    'ISO 9001:2015': {'title': 'Quality Management System', 'source':
    'https://www.iso.org/standard/62085.html', 'core_principles': [
    'Customer Focus', 'Leadership', 'Process Approach', 'Improvement'],
    'obligations': [{'id': 'ISO9001-SMB-001', 'title':
    'Understand Organizational Context', 'description':
    'Determine internal and external factors affecting QMS', 'requirement':
    'Organization must determine external and internal issues relevant to its purpose'
    , 'smb_guidance': 'Simple SWOT analysis sufficient for SMBs',
    'category': 'Context', 'priority': 'high'}, {'id': 'ISO9001-SMB-002',
    'title': 'Leadership Commitment', 'description':
    'Top management must actively engage in QMS', 'requirement':
    'Top management shall demonstrate leadership and commitment to the quality management system'
    , 'smb_guidance': 'Owner/CEO involvement essential in SMBs', 'category':
    'Leadership', 'priority': 'critical'}, {'id': 'ISO9001-SMB-003',
    'title': 'Quality Objectives', 'description':
    'Establish clear quality objectives and policies', 'requirement':
    'Organization shall establish quality objectives at relevant functions and levels'
    , 'smb_guidance': '3-5 measurable quality goals appropriate for SMBs',
    'category': 'Planning', 'priority': 'high'}, {'id': 'ISO9001-SMB-004',
    'title': 'Resource Allocation', 'description':
    'Allocate necessary resources for QMS', 'requirement':
    'Organization shall determine and provide resources needed for QMS',
    'smb_guidance': 'Focus resources on customer-critical processes',
    'category': 'Support', 'priority': 'high'}, {'id': 'ISO9001-SMB-005',
    'title': 'Customer Requirements', 'description':
    'Meet customer requirements and increase satisfaction', 'requirement':
    'Organization shall determine and meet customer requirements',
    'smb_guidance': 'Regular customer feedback surveys and reviews',
    'category': 'Operation', 'priority': 'critical'}, {'id':
    'ISO9001-SMB-006', 'title': 'Performance Evaluation', 'description':
    'Monitor and measure QMS performance', 'requirement':
    'Organization shall monitor, measure, analyze and evaluate QMS performance'
    , 'smb_guidance': 'Monthly KPI dashboard tracking key metrics',
    'category': 'Performance', 'priority': 'high'}, {'id':
    'ISO9001-SMB-007', 'title': 'Continuous Improvement', 'description':
    'Systematically enhance quality management system', 'requirement':
    'Organization shall continually improve the QMS', 'smb_guidance':
    'Implement simple PDCA cycle for improvements', 'category':
    'Improvement', 'priority': 'medium'}, {'id': 'ISO9001-SMB-008', 'title':
    'Document Control', 'description': 'Manage documented information',
    'requirement': 'Control documents and records required by the QMS',
    'smb_guidance': 'Use cloud-based document management for SMBs',
    'category': 'Documentation', 'priority': 'medium'}, {'id':
    'ISO9001-SMB-009', 'title': 'Risk-Based Thinking', 'description':
    'Address potential risks and opportunities', 'requirement':
    'Determine risks and opportunities that need to be addressed',
    'smb_guidance': 'Simple risk register with quarterly updates',
    'category': 'Risk Management', 'priority': 'high'}, {'id':
    'ISO9001-SMB-010', 'title': 'Internal Audit', 'description':
    'Conduct internal audits at planned intervals', 'requirement':
    'Organization shall conduct internal audits', 'smb_guidance':
    'Annual internal audit cycle sufficient for SMBs', 'category': 'Audit',
    'priority': 'medium'}]}, 'ISO 14001:2015': {'title':
    'Environmental Management System', 'source':
    'https://www.iso.org/standard/60857.html', 'core_principles': [
    'Environmental Protection', 'Legal Compliance', 'Continual Improvement'
    ], 'obligations': [{'id': 'ISO14001-SMB-001', 'title':
    'Environmental Impact Assessment', 'description':
    'Identify environmental aspects and impacts', 'requirement':
    'Determine environmental aspects of activities, products and services',
    'smb_guidance':
    'Focus on main environmental impacts of core operations', 'category':
    'Environmental Aspects', 'priority': 'high'}, {'id': 'ISO14001-SMB-002',
    'title': 'Legal Compliance', 'description':
    'Comply with environmental legal regulations', 'requirement':
    'Identify and have access to applicable legal requirements',
    'smb_guidance':
    'Use compliance calendar for key environmental regulations', 'category':
    'Compliance', 'priority': 'critical'}, {'id': 'ISO14001-SMB-003',
    'title': 'Environmental Policy', 'description':
    'Establish environmental policy appropriate to organization',
    'requirement': 'Top management shall establish an environmental policy',
    'smb_guidance':
    'One-page policy covering key environmental commitments', 'category':
    'Leadership', 'priority': 'high'}, {'id': 'ISO14001-SMB-004', 'title':
    'Minimize Environmental Footprint', 'description':
    'Proactively minimize environmental footprint', 'requirement':
    'Implement actions to address environmental aspects', 'smb_guidance':
    'Start with energy, waste, and water reduction', 'category':
    'Environmental Performance', 'priority': 'high'}, {'id':
    'ISO14001-SMB-005', 'title': 'Emergency Preparedness', 'description':
    'Prepare for environmental emergencies', 'requirement':
    'Establish processes to prepare for and respond to emergencies',
    'smb_guidance':
    'Simple spill response and emergency contact procedures', 'category':
    'Emergency Response', 'priority': 'critical'}, {'id':
    'ISO14001-SMB-006', 'title': 'Environmental Objectives', 'description':
    'Set measurable environmental objectives', 'requirement':
    'Establish environmental objectives at relevant functions',
    'smb_guidance': '3-5 SMART environmental goals per year', 'category':
    'Planning', 'priority': 'medium'}, {'id': 'ISO14001-SMB-007', 'title':
    'Operational Control', 'description':
    'Control operations with significant environmental aspects',
    'requirement':
    'Establish operational controls for environmental aspects',
    'smb_guidance': 'Focus controls on highest impact activities',
    'category': 'Operation', 'priority': 'high'}, {'id': 'ISO14001-SMB-008',
    'title': 'Performance Monitoring', 'description':
    'Monitor environmental performance', 'requirement':
    'Monitor and measure key environmental performance indicators',
    'smb_guidance': 'Track basic metrics: energy, waste, water monthly',
    'category': 'Monitoring', 'priority': 'medium'}]}, 'ISO 31000:2018': {
    'title': 'Risk Management Guidelines', 'source':
    'https://www.iso.org/standard/65694.html', 'core_principles': [
    'Integrated', 'Structured', 'Customized', 'Inclusive'], 'obligations':
    [{'id': 'ISO31000-SMB-001', 'title': 'Risk Management Framework',
    'description': 'Establish framework for risk management', 'requirement':
    'Organization should establish a framework for managing risk',
    'smb_guidance': 'Simple risk register and quarterly review process',
    'category': 'Framework', 'priority': 'high'}, {'id': 'ISO31000-SMB-002',
    'title': 'Risk Identification', 'description':
    'Systematically identify risks', 'requirement':
    'Identify risks that could affect objectives', 'smb_guidance':
    'Brainstorming sessions with key staff quarterly', 'category':
    'Risk Assessment', 'priority': 'critical'}, {'id': 'ISO31000-SMB-003',
    'title': 'Risk Analysis', 'description': 'Analyze identified risks',
    'requirement': 'Understand the nature of risk and determine risk level',
    'smb_guidance': 'Use simple likelihood x impact matrix', 'category':
    'Risk Assessment', 'priority': 'high'}, {'id': 'ISO31000-SMB-004',
    'title': 'Risk Evaluation', 'description':
    'Evaluate risks for treatment priority', 'requirement':
    'Compare risk analysis results with risk criteria', 'smb_guidance':
    'Focus on top 10 risks for SMBs', 'category': 'Risk Assessment',
    'priority': 'high'}, {'id': 'ISO31000-SMB-005', 'title':
    'Risk Treatment', 'description': 'Implement risk treatment options',
    'requirement':
    'Select and implement appropriate risk treatment options',
    'smb_guidance': 'Accept, avoid, reduce or transfer based on resources',
    'category': 'Risk Treatment', 'priority': 'critical'}, {'id':
    'ISO31000-SMB-006', 'title': 'Risk Communication', 'description':
    'Communicate risk information', 'requirement':
    'Ensure risk information is communicated to stakeholders',
    'smb_guidance': 'Monthly risk updates to management team', 'category':
    'Communication', 'priority': 'medium'}, {'id': 'ISO31000-SMB-007',
    'title': 'Risk Monitoring', 'description': 'Monitor and review risks',
    'requirement': 'Regularly monitor and review risk management process',
    'smb_guidance': 'Quarterly risk register review and update', 'category':
    'Monitoring', 'priority': 'medium'}]}, 'ISO 37301:2021': {'title':
    'Compliance Management System', 'source':
    'https://www.upguard.com/blog/iso-37301-guide', 'core_principles': [
    'Ethics', 'Compliance Culture', 'Risk-Based', 'Continuous Improvement'],
    'obligations': [{'id': 'ISO37301-SMB-001', 'title':
    'Compliance Risk Assessment', 'description':
    'Conduct compliance risk assessments', 'requirement':
    'Identify and assess compliance risks', 'smb_guidance':
    'Annual compliance risk assessment with quarterly updates', 'category':
    'Risk Assessment', 'priority': 'critical'}, {'id': 'ISO37301-SMB-002',
    'title': 'Compliance Officer', 'description':
    'Establish compliance officer responsibilities', 'requirement':
    'Assign compliance management responsibilities', 'smb_guidance':
    'Part-time compliance role acceptable for SMBs', 'category':
    'Leadership', 'priority': 'high'}, {'id': 'ISO37301-SMB-003', 'title':
    'Compliance Objectives', 'description':
    'Implement compliance objectives', 'requirement':
    'Establish compliance objectives and planning to achieve them',
    'smb_guidance': '3-5 key compliance goals annually', 'category':
    'Planning', 'priority': 'high'}, {'id': 'ISO37301-SMB-004', 'title':
    'Internal Controls', 'description':
    'Develop internal compliance controls', 'requirement':
    'Establish and maintain compliance controls', 'smb_guidance':
    'Focus on high-risk compliance areas first', 'category': 'Operation',
    'priority': 'critical'}, {'id': 'ISO37301-SMB-005', 'title':
    'Compliance Training', 'description':
    'Build organizational compliance awareness', 'requirement':
    'Ensure compliance awareness and competence', 'smb_guidance':
    'Annual compliance training for all staff', 'category': 'Support',
    'priority': 'high'}, {'id': 'ISO37301-SMB-006', 'title':
    'Compliance Monitoring', 'description':
    'Perform internal compliance audits', 'requirement':
    'Monitor compliance performance', 'smb_guidance':
    'Annual audit cycle with spot checks', 'category':
    'Performance Evaluation', 'priority': 'medium'}, {'id':
    'ISO37301-SMB-007', 'title': 'Compliance Culture', 'description':
    'Promote culture of compliance', 'requirement':
    'Foster ethical behavior and compliance culture', 'smb_guidance':
    'Lead by example with clear tone from the top', 'category': 'Culture',
    'priority': 'high'}, {'id': 'ISO37301-SMB-008', 'title':
    'Whistleblowing', 'description': 'Establish reporting mechanisms',
    'requirement': 'Enable reporting of compliance concerns',
    'smb_guidance': 'Simple anonymous reporting channel', 'category':
    'Communication', 'priority': 'critical'}]}, 'NIST CSF 2.0': {'title':
    'NIST Cybersecurity Framework', 'source':
    'https://www.nist.gov/cyberframework', 'core_principles': ['Identify',
    'Protect', 'Detect', 'Respond', 'Recover', 'Govern'], 'obligations': [{
    'id': 'NIST-SMB-001', 'title': 'Asset Management', 'description':
    'Identify and manage cybersecurity assets', 'requirement':
    'Maintain inventory of organizational systems, assets, and data',
    'smb_guidance': 'Simple spreadsheet of critical IT assets and data',
    'category': 'Identify', 'priority': 'critical'}, {'id': 'NIST-SMB-002',
    'title': 'Risk Assessment', 'description': 'Assess cybersecurity risks',
    'requirement':
    'Identify and assess cybersecurity risks to operations and assets',
    'smb_guidance': 'Annual cybersecurity risk assessment', 'category':
    'Identify', 'priority': 'high'}, {'id': 'NIST-SMB-003', 'title':
    'Access Control', 'description': 'Protect through access control',
    'requirement':
    'Limit access to assets and facilities to authorized users',
    'smb_guidance': 'Implement MFA and least privilege access', 'category':
    'Protect', 'priority': 'critical'}, {'id': 'NIST-SMB-004', 'title':
    'Data Security', 'description': 'Protect data at rest and in transit',
    'requirement': 'Implement data protection measures', 'smb_guidance':
    'Encrypt sensitive data and use secure connections', 'category':
    'Protect', 'priority': 'critical'}, {'id': 'NIST-SMB-005', 'title':
    'Security Training', 'description': 'Train users on cybersecurity',
    'requirement': 'Provide cybersecurity awareness training',
    'smb_guidance': 'Quarterly security awareness training', 'category':
    'Protect', 'priority': 'high'}, {'id': 'NIST-SMB-006', 'title':
    'Continuous Monitoring', 'description': 'Detect cybersecurity events',
    'requirement': 'Implement continuous monitoring capabilities',
    'smb_guidance': 'Basic SIEM or log monitoring tools', 'category':
    'Detect', 'priority': 'high'}, {'id': 'NIST-SMB-007', 'title':
    'Incident Response Plan', 'description':
    'Respond to detected incidents', 'requirement':
    'Maintain and test incident response procedures', 'smb_guidance':
    'Simple incident response checklist and contacts', 'category':
    'Respond', 'priority': 'critical'}, {'id': 'NIST-SMB-008', 'title':
    'Recovery Planning', 'description': 'Plan for recovery from incidents',
    'requirement': 'Maintain recovery plans and procedures', 'smb_guidance':
    'Basic backup and recovery procedures', 'category': 'Recover',
    'priority': 'high'}, {'id': 'NIST-SMB-009', 'title':
    'Supply Chain Risk', 'description': 'Manage supply chain cybersecurity',
    'requirement': 'Assess and manage supply chain risks', 'smb_guidance':
    'Vendor security questionnaire for critical suppliers', 'category':
    'Identify', 'priority': 'medium'}, {'id': 'NIST-SMB-010', 'title':
    'Governance Structure', 'description':
    'Establish cybersecurity governance', 'requirement':
    'Define roles and responsibilities for cybersecurity', 'smb_guidance':
    'Clear security roles even in small teams', 'category': 'Govern',
    'priority': 'high'}]}}


def extract_smb_framework_obligations() ->Any:
    """Extract SMB-relevant obligations from frameworks."""
    all_obligations = []
    framework_summary = {'title': 'SMB Compliance Framework Suite',
        'description':
        'Comprehensive framework obligations for Small and Medium Businesses',
        'created_at': datetime.now().isoformat(), 'total_frameworks': len(
        SMB_FRAMEWORKS), 'total_obligations': 0, 'frameworks': {}}
    for framework_name, framework_data in SMB_FRAMEWORKS.items():
        logger.info('\nProcessing %s...' % framework_name)
        framework_obligations = []
        for obligation in framework_data['obligations']:
            obl_hash = hashlib.md5(f"{framework_name}_{obligation['id']}".
                encode()).hexdigest()[:8]
            obligation_entry = {'obligation_id': f'SMB-{obl_hash}',
                'framework': framework_name, 'framework_title':
                framework_data['title'], 'source_url': framework_data[
                'source'], 'id': obligation['id'], 'title': obligation[
                'title'], 'description': obligation['description'],
                'requirement': obligation['requirement'], 'smb_guidance':
                obligation['smb_guidance'], 'category': obligation[
                'category'], 'priority': obligation['priority'],
                'core_principles': framework_data.get('core_principles', []
                ), 'implementation_level': 'SMB', 'created_at': datetime.
                now().isoformat()}
            framework_obligations.append(obligation_entry)
            all_obligations.append(obligation_entry)
        framework_summary['frameworks'][framework_name] = {'title':
            framework_data['title'], 'source': framework_data['source'],
            'core_principles': framework_data.get('core_principles', []),
            'obligation_count': len(framework_obligations), 'categories':
            list(set(o['category'] for o in framework_obligations))}
        logger.info('  - Extracted %s obligations' % len(framework_obligations),
            )
    framework_summary['total_obligations'] = len(all_obligations)
    manifest_path = Path(
        '/home/omar/Documents/ruleIQ/data/manifests/smb_frameworks_manifest.json',
        )
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {'title': 'SMB Framework Compliance Manifest', 'description':
        'Extracted obligations from ISO standards and frameworks for SMBs',
        'created_at': datetime.now().isoformat(), 'source':
        'Official ISO and framework documentation', 'total_obligations':
        len(all_obligations), 'frameworks': framework_summary['frameworks'],
        'obligations': all_obligations}
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    logger.info('\n%s' % ('=' * 80))
    logger.info('SMB FRAMEWORK EXTRACTION COMPLETE')
    logger.info('%s' % ('=' * 80))
    logger.info('Total Frameworks: %s' % len(SMB_FRAMEWORKS))
    logger.info('Total Obligations: %s' % len(all_obligations))
    logger.info('Manifest saved to: %s' % manifest_path)
    logger.info('\nFramework Breakdown:')
    for framework, details in framework_summary['frameworks'].items():
        logger.info('  - %s: %s obligations' % (framework, details[
            'obligation_count']))
    return manifest


if __name__ == '__main__':
    extract_smb_framework_obligations()
