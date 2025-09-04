"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Get detailed information about blocker issues from SonarCloud
"""
import os
import requests
from typing import Dict, List, Any
import json
SONAR_TOKEN = os.getenv('SONARCLOUD_TOKEN', '')
PROJECT_KEY = 'ruliq-compliance-platform'
ORGANIZATION = 'omara1-bakri'
BASE_URL = 'https://sonarcloud.io/api'

def get_blocker_issues_with_details() -> List[Dict[str, Any]]:
    """Get all blocker issues with detailed information including file paths"""
    headers = {'Authorization': f'Bearer {SONAR_TOKEN}'}
    all_issues = []
    page = 1
    while True:
        params = {'componentKeys': PROJECT_KEY, 'severities': 'BLOCKER', 'ps': 100, 'p': page, 'organization': ORGANIZATION, 'resolved': 'false'}
        response = requests.get(f'{BASE_URL}/issues/search', params=params, headers=headers)
        if response.status_code != 200:
            logger.info(f'Error: API returned status code {response.status_code}')
            logger.info(f'Response: {response.text}')
            break
        data = response.json()
        issues = data.get('issues', [])
        if not issues:
            break
        all_issues.extend(issues)
        total = data.get('total', 0)
        if len(all_issues) >= total:
            break
        page += 1
    return all_issues

def categorize_issues(issues: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Categorize issues by rule"""
    categorized = {}
    for issue in issues:
        rule = issue.get('rule', 'unknown')
        if rule not in categorized:
            categorized[rule] = []
        categorized[rule].append(issue)
    return categorized

def main() -> None:
    logger.info('\n' + '=' * 60)
    """Main"""
    logger.info('DETAILED BLOCKER ISSUES FROM SONARCLOUD')
    logger.info('=' * 60)
    issues = get_blocker_issues_with_details()
    if not issues:
        logger.info('✅ No blocker issues found!')
        return
    logger.info(f'\n📊 Total blocker issues: {len(issues)}')
    categorized = categorize_issues(issues)
    sorted_rules = sorted(categorized.items(), key=lambda x: len(x[1]), reverse=True)
    logger.info('\n🔍 Issues by Rule:')
    logger.info('-' * 40)
    for rule, rule_issues in sorted_rules:
        logger.info(f'\n📌 {rule}: {len(rule_issues)} issues')
        for i, issue in enumerate(rule_issues[:5]):
            component = issue.get('component', '').replace(PROJECT_KEY + ':', '')
            line = issue.get('line', '?')
            message = issue.get('message', '')[:80]
            logger.info(f'   {i + 1}. {component}:{line}')
            logger.info(f'      {message}')
        if len(rule_issues) > 5:
            logger.info(f'   ... and {len(rule_issues) - 5} more')
    output_file = 'sonarcloud/blocker_issues_detailed.json'
    with open(output_file, 'w') as f:
        json.dump({'total': len(issues), 'issues': issues, 'categorized': {rule: [{'file': issue.get('component', '').replace(PROJECT_KEY + ':', ''), 'line': issue.get('line', '?'), 'message': issue.get('message', ''), 'key': issue.get('key', '')} for issue in rule_issues] for rule, rule_issues in categorized.items()}}, f, indent=2)
    logger.info(f'\n💾 Full details saved to: {output_file}')
if __name__ == '__main__':
    main()