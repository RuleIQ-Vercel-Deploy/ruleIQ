"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Migrate all endpoints from JWT authentication to Stack Auth
This script will update all 140+ endpoints automatically
"""

import re
from pathlib import Path
from typing import List
REPLACEMENTS = [(
    'from api\\.dependencies\\.auth import get_current_active_user',
    'from api.dependencies.stack_auth import get_current_stack_user'), (
    'from api\\.dependencies\\.auth import get_current_user',
    'from api.dependencies.stack_auth import get_current_stack_user'), (
    'Depends\\(get_current_active_user\\)',
    'Depends(get_current_stack_user)'), ('Depends\\(get_current_user\\)',
    'Depends(get_current_stack_user)'), ('current_user: User = Depends',
    'current_user: dict = Depends'), ('user: User = Depends',
    'user: dict = Depends'), ('current_user\\.id', 'current_user["id"]'), (
    'user\\.id', 'user["id"]'), ('current_user\\.email',
    'current_user.get("primaryEmail", current_user.get("email", ""))'), (
    'user\\.email', 'user.get("primaryEmail", user.get("email", ""))'), (
    'current_user\\.username', 'current_user.get("displayName", "")'), (
    'user\\.username', 'user.get("displayName", "")')]


def get_router_files() ->List[Path]:
    """Get all router files that need migration"""
    router_dir = Path('api/routers')
    exclude_files = {'auth.py', 'google_auth.py', 'test_utils.py'}
    router_files = []
    for file in router_dir.glob('*.py'):
        if file.name not in exclude_files and not file.name.startswith('_'):
            router_files.append(file)
    return router_files


def backup_file(file_path: Path) ->None:
    """Create a backup of the file before modifying"""
    backup_path = file_path.with_suffix(f'{file_path.suffix}.backup')
    if not backup_path.exists():
        backup_path.write_text(file_path.read_text())
        logger.info('✅ Backed up: %s -> %s' % (file_path, backup_path))


def migrate_file(file_path: Path, dry_run: bool=False) ->List[str]:
    """Migrate a single file from JWT to Stack Auth"""
    changes = []
    content = file_path.read_text()
    for pattern, replacement in REPLACEMENTS:
        matches = list(re.finditer(pattern, content))
        if matches:
            for match in matches:
                changes.append(
                    f'  - Line {content[:match.start()].count(chr(10)) + 1}: {match.group()} -> {replacement}',
                    )
            content = re.sub(pattern, replacement, content)
    if ('from database import User' in content or
        'from database.models import User' in content):
        user_pattern = '\\bUser\\b(?!\\s*\\()'
        if re.search(user_pattern, content):
            changes.append(
                '  - Found User model references that may need manual review')
    if changes and not dry_run:
        backup_file(file_path)
        file_path.write_text(content)
        logger.info('✅ Migrated: %s (%s changes)' % (file_path, len(changes)))
    elif changes:
        logger.info('🔍 Would migrate: %s (%s changes)' % (file_path, len(
            changes)))
    return changes


def generate_migration_report(results: dict) ->None:
    """Generate a detailed migration report"""
    report_path = Path('STACK_AUTH_MIGRATION_REPORT.md')
    report = ['# Stack Auth Migration Report', '', '## Summary',
        f'- Total files analyzed: {len(results)}',
        f'- Files with changes: {sum(1 for changes in results.values() if changes)}'
        ,
        f'- Total changes: {sum(len(changes) for changes in results.values())}'
        , '', '## Details by File', '']
    for file_path, changes in results.items():
        if changes:
            report.append(f'### {file_path}')
            report.extend(changes)
            report.append('')
    report_path.write_text('\n'.join(report))
    logger.info('\n📄 Migration report saved to: %s' % report_path)


def main() ->None:
    """Run the migration"""
    logger.info('🚀 Stack Auth Migration Script')
    logger.info('=' * 50)
    if not Path('api/routers').exists():
        logger.info('❌ Error: Must run from project root directory')
        return
    response = input(
        """
This will migrate all router files from JWT to Stack Auth.
Create backups and continue? (yes/no): """,
        )
    if response.lower() != 'yes':
        logger.info('❌ Migration cancelled')
        return
    logger.info('\n📋 Performing dry run...')
    router_files = get_router_files()
    dry_run_results = {}
    for file_path in router_files:
        changes = migrate_file(file_path, dry_run=True)
        if changes:
            dry_run_results[str(file_path)] = changes
    if not dry_run_results:
        logger.info('\n✅ No changes needed - all files already migrated!')
        return
    print(
        f"""
📊 Dry run complete: {sum(len(c) for c in dry_run_results.values())} changes in {len(dry_run_results)} files""",
        )
    response = input('\nProceed with actual migration? (yes/no): ')
    if response.lower() != 'yes':
        logger.info('❌ Migration cancelled')
        return
    logger.info('\n🔧 Performing migration...')
    results = {}
    for file_path in router_files:
        changes = migrate_file(file_path, dry_run=False)
        results[str(file_path)] = changes
    generate_migration_report(results)
    logger.info('\n✅ Migration complete!')
    logger.info('\n⚠️  Important next steps:')
    logger.info(
        '1. Review the migration report: STACK_AUTH_MIGRATION_REPORT.md')
    logger.info(
        '2. Check for any User model references that need manual updates')
    logger.info('3. Run tests: pytest tests/')
    logger.info('4. Test each endpoint manually with Stack Auth tokens')
    logger.info('5. Update any service layer functions that expect User models',
        )


if __name__ == '__main__':
    main()
