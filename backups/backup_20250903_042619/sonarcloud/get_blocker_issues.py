"""
Get all BLOCKER issues from SonarCloud for systematic fixing
"""
from typing import Any, Tuple
import logging
logger = logging.getLogger(__name__)
import os
import requests
import json
from collections import defaultdict
SONAR_TOKEN = os.getenv('SONARCLOUD_TOKEN', '')
SONAR_URL = 'https://sonarcloud.io/api'
PROJECT_KEY = 'ruliq-compliance-platform'

def get_blocker_issues() -> Any:
    """Fetch all blocker-level issues from SonarCloud"""
    url = f'{SONAR_URL}/issues/search'
    all_issues = []
    page = 1
    while True:
        params = {'componentKeys': PROJECT_KEY, 'severities': 'BLOCKER', 'resolved': 'false', 'ps': 100, 'p': page}
        headers = {'Authorization': f'Bearer {SONAR_TOKEN}'}
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            logger.info(f'Error: {response.status_code}')
            break
        data = response.json()
        issues = data.get('issues', [])
        all_issues.extend(issues)
        total = data.get('total', 0)
        if len(all_issues) >= total or not issues:
            break
        page += 1
    return all_issues

def categorize_issues(issues) -> Tuple[Any, ...]:
    """Categorize issues by type, rule, and file"""
    by_type = defaultdict(list)
    by_rule = defaultdict(list)
    by_file = defaultdict(list)
    for issue in issues:
        issue_type = issue.get('type', 'UNKNOWN')
        rule = issue.get('rule', 'unknown')
        component = issue.get('component', 'unknown')
        if ':' in component:
            file_path = component.split(':', 1)[1]
        else:
            file_path = component
        by_type[issue_type].append(issue)
        by_rule[rule].append(issue)
        by_file[file_path].append(issue)
    return (by_type, by_rule, by_file)

def main() -> None:
    logger.info('\n' + '=' * 60)
    """Main"""
    logger.info('SONARCLOUD BLOCKER ISSUES ANALYSIS')
    logger.info('=' * 60)
    logger.info('\nFetching blocker issues...')
    issues = get_blocker_issues()
    logger.info(f'Total blocker issues: {len(issues)}')
    by_type, by_rule, by_file = categorize_issues(issues)
    logger.info('\n📊 ISSUES BY TYPE:')
    logger.info('-' * 40)
    for issue_type, type_issues in sorted(by_type.items()):
        logger.info(f'{issue_type}: {len(type_issues)}')
    logger.info('\n📋 TOP VIOLATIONS BY RULE:')
    logger.info('-' * 40)
    sorted_rules = sorted(by_rule.items(), key=lambda x: len(x[1]), reverse=True)
    for rule, rule_issues in sorted_rules[:10]:
        lang, rule_id = rule.split(':', 1) if ':' in rule else ('', rule)
        logger.info(f'[{lang}] {rule_id}: {len(rule_issues)} violations')
        if rule_issues:
            first_issue = rule_issues[0]
            logger.info(f"  Example: {first_issue.get('message', 'No message')[:100]}...")
    logger.info('\n📁 FILES WITH MOST BLOCKERS:')
    logger.info('-' * 40)
    sorted_files = sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True)
    for file_path, file_issues in sorted_files[:10]:
        logger.info(f'{file_path}: {len(file_issues)} issues')
    logger.info('\n📝 CREATING DETAILED REPORT...')
    with open('sonarcloud/BLOCKER_ISSUES_DETAILED.md', 'w') as f:
        f.write('# SonarCloud BLOCKER Issues - Detailed Report\n\n')
        f.write(f'Total Blocker Issues: {len(issues)}\n\n')
        f.write('## Issues by Rule (for systematic fixing)\n\n')
        for rule, rule_issues in sorted_rules:
            lang, rule_id = rule.split(':', 1) if ':' in rule else ('', rule)
            f.write(f'### [{lang}] {rule_id} - {len(rule_issues)} violations\n\n')
            if rule_issues:
                first_issue = rule_issues[0]
                f.write(f"**Rule:** {first_issue.get('message', 'No description')}\n\n")
                f.write('**Affected files:**\n')
                files_for_rule = defaultdict(list)
                for issue in rule_issues:
                    component = issue.get('component', '')
                    if ':' in component:
                        file_path = component.split(':', 1)[1]
                        line = issue.get('line', '?')
                        files_for_rule[file_path].append(line)
                for file_path, lines in sorted(files_for_rule.items()):
                    lines_str = ', '.join((str(l) for l in sorted(set(lines))))
                    f.write(f'- `{file_path}` (lines: {lines_str})\n')
                f.write('\n')
    logger.info('✅ Detailed report saved to: sonarcloud/BLOCKER_ISSUES_DETAILED.md')
    logger.info('\n🔧 SUGGESTED FIX ORDER:')
    logger.info('-' * 40)
    logger.info('Based on issue count and impact, fix in this order:')
    for i, (rule, rule_issues) in enumerate(sorted_rules[:5], 1):
        lang, rule_id = rule.split(':', 1) if ':' in rule else ('', rule)
        logger.info(f'{i}. [{lang}] {rule_id} ({len(rule_issues)} issues)')
        if rule_issues:
            logger.info(f"   {rule_issues[0].get('message', '')[:80]}...")
    logger.info('\n' + '=' * 60)
if __name__ == '__main__':
    main()