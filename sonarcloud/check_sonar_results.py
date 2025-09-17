"""
Check SonarCloud analysis results for the ruleIQ project
"""
from typing import Any, Optional
import logging
logger = logging.getLogger(__name__)
import os
import requests
from datetime import datetime
SONAR_TOKEN = os.getenv('SONARCLOUD_TOKEN', '')
SONAR_URL = 'https://sonarcloud.io/api'
PROJECT_KEY = 'ruliq-compliance-platform'
ORGANIZATION = 'omara1-bakri'

def get_project_status() -> Optional[Any]:
    """Get overall project quality gate status"""
    url = f'{SONAR_URL}/qualitygates/project_status'
    params = {'projectKey': PROJECT_KEY}
    headers = {'Authorization': f'Bearer {SONAR_TOKEN}'}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def get_project_measures() -> Optional[Any]:
    """Get detailed project metrics"""
    url = f'{SONAR_URL}/measures/component'
    metrics = ['bugs', 'vulnerabilities', 'code_smells', 'security_hotspots', 'coverage', 'duplicated_lines_density', 'ncloc', 'sqale_index', 'reliability_rating', 'security_rating', 'sqale_rating']
    params = {'component': PROJECT_KEY, 'metricKeys': ','.join(metrics)}
    headers = {'Authorization': f'Bearer {SONAR_TOKEN}'}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def get_issues_summary() -> Optional[Any]:
    """Get summary of issues by type and severity"""
    url = f'{SONAR_URL}/issues/search'
    params = {'componentKeys': PROJECT_KEY, 'facets': 'types,severities,rules', 'ps': 1}
    headers = {'Authorization': f'Bearer {SONAR_TOKEN}'}
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        return response.json()
    return None

def format_rating(rating) -> Any:
    """Convert numeric rating to letter grade"""
    rating_map = {'1.0': 'A', '2.0': 'B', '3.0': 'C', '4.0': 'D', '5.0': 'E'}
    return rating_map.get(rating, rating)

def main() -> None:
    logger.info('\n' + '=' * 60)
    logger.info('SONARCLOUD ANALYSIS REPORT - ruleIQ Compliance Platform')
    logger.info('=' * 60)
    logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f'Project: {PROJECT_KEY}')
    logger.info(f'Organization: {ORGANIZATION}')
    logger.info('\n📊 QUALITY GATE STATUS')
    logger.info('-' * 40)
    status = get_project_status()
    if status:
        gate_status = status.get('projectStatus', {}).get('status', 'UNKNOWN')
        emoji = '✅' if gate_status == 'OK' else '❌'
        logger.info(f'{emoji} Quality Gate: {gate_status}')
        conditions = status.get('projectStatus', {}).get('conditions', [])
        if conditions:
            logger.info('\nFailed Conditions:')
            for condition in conditions:
                if condition.get('status') != 'OK':
                    metric = condition.get('metricKey', '')
                    actual = condition.get('actualValue', '')
                    error = condition.get('errorThreshold', '')
                    logger.info(f'  • {metric}: {actual} (threshold: {error})')
    logger.info('\n📈 PROJECT METRICS')
    logger.info('-' * 40)
    measures = get_project_measures()
    if measures:
        metrics = {}
        for measure in measures.get('component', {}).get('measures', []):
            metrics[measure['metric']] = measure.get('value', '0')
        logger.info(f"Lines of Code: {metrics.get('ncloc', '0')}")
        logger.info(f"Code Coverage: {metrics.get('coverage', '0')}%")
        logger.info(f"Duplicated Lines: {metrics.get('duplicated_lines_density', '0')}%")
        logger.info(f"Technical Debt: {metrics.get('sqale_index', '0')} minutes")
        logger.info('\nRatings:')
        logger.info(f"  • Reliability: {format_rating(metrics.get('reliability_rating', '0'))}")
        logger.info(f"  • Security: {format_rating(metrics.get('security_rating', '0'))}")
        logger.info(f"  • Maintainability: {format_rating(metrics.get('sqale_rating', '0'))}")
    logger.info('\n🐛 ISSUES SUMMARY')
    logger.info('-' * 40)
    issues = get_issues_summary()
    if issues:
        total = issues.get('total', 0)
        logger.info(f'Total Issues: {total}')
        logger.info('\nBy Type:')
        type_facets = next((f for f in issues.get('facets', []) if f['property'] == 'types'), None)
        if type_facets:
            for value in type_facets.get('values', []):
                issue_type = value['val']
                count = value['count']
                emoji_map = {'BUG': '🐛', 'VULNERABILITY': '🔒', 'CODE_SMELL': '💨', 'SECURITY_HOTSPOT': '🔥'}
                emoji = emoji_map.get(issue_type, '📌')
                logger.info(f'  {emoji} {issue_type}: {count}')
        logger.info('\nBy Severity:')
        severity_facets = next((f for f in issues.get('facets', []) if f['property'] == 'severities'), None)
        if severity_facets:
            for value in severity_facets.get('values', []):
                severity = value['val']
                count = value['count']
                emoji_map = {'BLOCKER': '🚫', 'CRITICAL': '🔴', 'MAJOR': '🟠', 'MINOR': '🟡', 'INFO': 'ℹ️'}
                emoji = emoji_map.get(severity, '•')
                logger.info(f'  {emoji} {severity}: {count}')
        logger.info('\nTop 5 Rule Violations:')
        rule_facets = next((f for f in issues.get('facets', []) if f['property'] == 'rules'), None)
        if rule_facets:
            for i, value in enumerate(rule_facets.get('values', [])[:5], 1):
                rule = value['val']
                count = value['count']
                if ':' in rule:
                    lang, rule_id = rule.split(':', 1)
                    logger.info(f'  {i}. [{lang}] {rule_id}: {count} violations')
                else:
                    logger.info(f'  {i}. {rule}: {count} violations')
    logger.info('\n' + '=' * 60)
    logger.info('🔗 View full report: https://sonarcloud.io/summary/overall?id=ruliq-compliance-platform')
    logger.info('=' * 60 + '\n')
if __name__ == '__main__':
    main()
