"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Single-file Stack Auth migration with mandatory dry run
Follows the migration plan schema exactly
"""

import argparse
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import sys
MIGRATION_PATTERNS = [{'pattern':
    'from api\\.dependencies\\.auth import get_current_active_user',
    'replacement':
    'from api.dependencies.stack_auth import get_current_stack_user',
    'description':
    'Import: get_current_active_user -> get_current_stack_user'}, {
    'pattern': 'from api\\.dependencies\\.auth import get_current_user',
    'replacement':
    'from api.dependencies.stack_auth import get_current_stack_user',
    'description': 'Import: get_current_user -> get_current_stack_user'}, {
    'pattern':
    'from api\\.dependencies\\.auth import get_current_active_user, get_current_user'
    , 'replacement':
    'from api.dependencies.stack_auth import get_current_stack_user',
    'description':
    'Import: Combined auth imports -> get_current_stack_user'}, {'pattern':
    'from api\\.dependencies\\.auth import get_current_user, get_current_active_user'
    , 'replacement':
    'from api.dependencies.stack_auth import get_current_stack_user',
    'description':
    'Import: Combined auth imports -> get_current_stack_user'}, {'pattern':
    'Depends\\(get_current_active_user\\)', 'replacement':
    'Depends(get_current_stack_user)', 'description':
    'Dependency: get_current_active_user -> get_current_stack_user'}, {
    'pattern': 'Depends\\(get_current_user\\)', 'replacement':
    'Depends(get_current_stack_user)', 'description':
    'Dependency: get_current_user -> get_current_stack_user'}]
TYPE_PATTERNS = [{'pattern': '(\\w+):\\s*User\\s*=\\s*Depends',
    'replacement': '\\1: dict = Depends', 'description':
    'Type hint: User -> dict'}]
ATTRIBUTE_PATTERNS = [{'pattern': '(\\w+)\\.id\\b', 'replacement':
    '\\1["id"]', 'description': "Attribute: .id -> ['id']", 'user_vars': [
    'current_user', 'user', 'auth_user', 'authenticated_user']}, {'pattern':
    '(\\w+)\\.email\\b', 'replacement':
    '\\1.get("primaryEmail", \\1.get("email", ""))', 'description':
    "Attribute: .email -> .get('primaryEmail', ...)", 'user_vars': [
    'current_user', 'user', 'auth_user', 'authenticated_user']}, {'pattern':
    '(\\w+)\\.username\\b', 'replacement': '\\1.get("displayName", "")',
    'description': "Attribute: .username -> .get('displayName', '')",
    'user_vars': ['current_user', 'user', 'auth_user', 'authenticated_user'
    ]}, {'pattern': '(\\w+)\\.is_active\\b', 'replacement':
    '\\1.get("isActive", True)', 'description':
    "Attribute: .is_active -> .get('isActive', True)", 'user_vars': [
    'current_user', 'user', 'auth_user', 'authenticated_user']}, {'pattern':
    '(\\w+)\\.is_superuser\\b', 'replacement':
    'any(r.get("name") == "admin" for r in \\1.get("roles", []))',
    'description': 'Attribute: .is_superuser -> role check', 'user_vars': [
    'current_user', 'user', 'auth_user', 'authenticated_user']}]


def analyze_file(file_path: Path) ->Dict[str, List[Dict]]:
    """Analyze a file and return all needed changes"""
    content = file_path.read_text()
    lines = content.split('\n')
    changes = {'imports': [], 'dependencies': [], 'type_hints': [],
        'attributes': [], 'user_imports': []}
    for i, line in enumerate(lines):
        if re.search('from database(?:\\.models)? import.*\\bUser\\b', line):
            changes['user_imports'].append({'line': i + 1, 'content': line.
                strip(), 'action':
                'Review if User model is needed beyond type hints'})
    for pattern_info in MIGRATION_PATTERNS:
        pattern = pattern_info['pattern']
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                category = 'imports' if 'import' in pattern else 'dependencies'
                changes[category].append({'line': i + 1, 'content': line.
                    strip(), 'pattern': pattern, 'replacement':
                    pattern_info['replacement'], 'description':
                    pattern_info['description']})
    for pattern_info in TYPE_PATTERNS:
        pattern = pattern_info['pattern']
        for i, line in enumerate(lines):
            if re.search(pattern, line):
                changes['type_hints'].append({'line': i + 1, 'content':
                    line.strip(), 'pattern': pattern, 'replacement':
                    pattern_info['replacement'], 'description':
                    pattern_info['description']})
    for pattern_info in ATTRIBUTE_PATTERNS:
        pattern = pattern_info['pattern']
        for i, line in enumerate(lines):
            matches = re.finditer(pattern, line)
            for match in matches:
                var_name = match.group(1)
                if var_name in pattern_info['user_vars']:
                    changes['attributes'].append({'line': i + 1, 'content':
                        line.strip(), 'pattern': pattern, 'match': match.
                        group(0), 'replacement': pattern_info['replacement'
                        ], 'description': pattern_info['description']})
    return changes


def print_dry_run_report(file_path: Path, changes: Dict[str, List[Dict]]
    ) ->int:
    """Print detailed dry run report"""
    total_changes = sum(len(v) for v in changes.values())
    logger.info('\n%s' % ('=' * 80))
    logger.info('DRY RUN REPORT: %s' % file_path)
    logger.info('%s' % ('=' * 80))
    logger.info('Total changes needed: %s' % total_changes)
    if total_changes == 0:
        logger.info(
            "✅ No changes needed - file already migrated or doesn't use auth")
        return 0
    if changes['imports']:
        logger.info('\n📦 Import Changes (%s)' % len(changes['imports']))
        logger.info('-' * 40)
        for change in changes['imports']:
            logger.info('  Line %s: %s' % (change['line'], change[
                'description']))
            logger.info('    From: %s' % change['content'])
            logger.info('    To:   %s' % change['replacement'])
    if changes['user_imports']:
        logger.info('\n⚠️  User Model Imports (%s) - Need Review' % len(
            changes['user_imports']))
        logger.info('-' * 40)
        for change in changes['user_imports']:
            logger.info('  Line %s: %s' % (change['line'], change['content']))
            logger.info('    Action: %s' % change['action'])
    if changes['dependencies']:
        logger.info('\n🔗 Dependency Changes (%s)' % len(changes[
            'dependencies']))
        logger.info('-' * 40)
        for change in changes['dependencies']:
            logger.info('  Line %s: %s' % (change['line'], change[
                'description']))
    if changes['type_hints']:
        logger.info('\n📝 Type Hint Changes (%s)' % len(changes['type_hints']))
        logger.info('-' * 40)
        for change in changes['type_hints']:
            logger.info('  Line %s: %s' % (change['line'], change[
                'description']))
            logger.info('    From: %s' % change['content'])
    if changes['attributes']:
        logger.info('\n🔍 Attribute Access Changes (%s)' % len(changes[
            'attributes']))
        logger.info('-' * 40)
        for change in changes['attributes']:
            logger.info('  Line %s: %s' % (change['line'], change[
                'description']))
            logger.info('    In: %s' % change['content'])
            print(
                f"    Change: {change['match']} -> {change['description'].split('->')[-1].strip()}",
                )
    return total_changes


def apply_migrations(file_path: Path, changes: Dict[str, List[Dict]]) ->str:
    """Apply all migrations to file content"""
    content = file_path.read_text()
    all_changes = []
    for category, change_list in changes.items():
        if category != 'user_imports':
            all_changes.extend(change_list)
    all_changes.sort(key=lambda x: x['line'], reverse=True)
    lines = content.split('\n')
    for change in all_changes:
        line_idx = change['line'] - 1
        if line_idx < len(lines):
            old_line = lines[line_idx]
            if 'pattern' in change and 'replacement' in change:
                if isinstance(change['replacement'], str) and not change[
                    'replacement'].startswith('\\1'):
                    new_line = re.sub(change['pattern'], change[
                        'replacement'], old_line)
                else:
                    new_line = re.sub(change['pattern'], change[
                        'replacement'], old_line)
                lines[line_idx] = new_line
    return '\n'.join(lines)


def create_backup(file_path: Path) ->Path:
    """Create timestamped backup"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = file_path.with_suffix(f'.{timestamp}.jwt-backup')
    shutil.copy2(file_path, backup_path)
    return backup_path


def main() ->int:
    parser = argparse.ArgumentParser(description=
        'Migrate single file to Stack Auth')
    parser.add_argument('--file', required=True, help='Path to file to migrate',
        )
    parser.add_argument('--dry-run', action='store_true', default=True,
        help='Perform dry run (default: True)')
    parser.add_argument('--execute', action='store_true', help=
        'Execute migration (requires explicit flag)')
    args = parser.parse_args()
    file_path = Path(args.file)
    if not file_path.exists():
        logger.info('❌ Error: File not found: %s' % file_path)
        return 1
    changes = analyze_file(file_path)
    total_changes = print_dry_run_report(file_path, changes)
    if total_changes == 0:
        return 0
    if not args.execute:
        logger.info('\n%s' % ('=' * 80))
        logger.info('ℹ️  This was a DRY RUN. No files were modified.')
        logger.info('To execute migration, run with --execute flag')
        logger.info('%s' % ('=' * 80))
        return 0
    logger.info('\n%s' % ('=' * 80))
    logger.info('🚀 EXECUTING MIGRATION')
    logger.info('%s' % ('=' * 80))
    backup_path = create_backup(file_path)
    logger.info('✅ Backup created: %s' % backup_path)
    new_content = apply_migrations(file_path, changes)
    file_path.write_text(new_content)
    logger.info('✅ Migration applied to: %s' % file_path)
    logger.info('\n📋 Next Steps:')
    logger.info('1. Run tests: pytest tests/test_%s.py -v' % file_path.stem)
    print(
        "2. Test with curl: curl -H 'Authorization: Bearer <stack-token>' http://localhost:8000/api/...",
        )
    logger.info('3. If issues, restore: cp %s %s' % (backup_path, file_path))
    print(
        f"4. Commit: git add {file_path} && git commit -m 'feat: migrate {file_path.stem} to Stack Auth'",
        )
    return 0


if __name__ == '__main__':
    sys.exit(main())
