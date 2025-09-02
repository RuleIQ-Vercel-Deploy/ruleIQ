"""
from __future__ import annotations
import logging

# Constants
DEFAULT_RETRIES = 5

logger = logging.getLogger(__name__)

Dry run of Stack Auth migration to show what changes would be made
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
    exclude_files = {'auth.py', 'google_auth.py', 'test_utils.py',
        'stack_auth.py'}
    router_files = []
    for file in router_dir.glob('*.py'):
        if file.name not in exclude_files and not file.name.startswith('_'):
            router_files.append(file)
    return router_files


def analyze_file(file_path: Path) ->List[str]:
    """Analyze a single file for needed changes"""
    changes = []
    content = file_path.read_text()
    lines = content.split('\n')
    for pattern, replacement in REPLACEMENTS:
        for line_num, line in enumerate(lines, 1):
            if re.search(pattern, line):
                changes.append(
                    f'  Line {line_num}: {line.strip()} -> would change to use Stack Auth'
                    )
    for line_num, line in enumerate(lines, 1):
        if ('from database import User' in line or 
            'from database.models import User' in line):
            changes.append(
                f'  Line {line_num}: {line.strip()} -> User model import found, needs review'
                )
    user_type_pattern = ':\\s*User\\s*[=\\)]'
    for line_num, line in enumerate(lines, 1):
        if re.search(user_type_pattern, line):
            changes.append(
                f'  Line {line_num}: {line.strip()} -> User type hint needs updating to dict'
                )
    return changes


def main() ->None:
    """Run the dry-run analysis"""
    logger.info('🔍 Stack Auth Migration Dry Run')
    logger.info('=' * 70)
    logger.info('\nThis is a DRY RUN - no files will be modified')
    logger.info('\nAnalyzing router files for needed changes...')
    logger.info('-' * 70)
    if not Path('api/routers').exists():
        logger.info('❌ Error: Must run from project root directory')
        return
    router_files = sorted(get_router_files())
    total_changes = 0
    files_needing_changes = 0
    results = {}
    for file_path in router_files:
        changes = analyze_file(file_path)
        if changes:
            results[file_path] = changes
            files_needing_changes += 1
            total_changes += len(changes)
            logger.info('\n📄 %s' % file_path)
            logger.info('   Found %s changes needed:' % len(changes))
            for change in changes[:5]:
                logger.info('   %s' % change)
            if len(changes) > DEFAULT_RETRIES:
                logger.info('   ... and %s more changes' % (len(changes) - 5))
    logger.info('\n' + '=' * 70)
    logger.info('📊 DRY RUN SUMMARY')
    logger.info('=' * 70)
    logger.info('Total files analyzed: %s' % len(router_files))
    logger.info('Files needing changes: %s' % files_needing_changes)
    logger.info('Total changes needed: %s' % total_changes)
    if files_needing_changes > 0:
        logger.info('\n📋 Files that need migration:')
        for file_path in results:
            logger.info('  - %s (%s changes)' % (file_path, len(results[
                file_path])))
    logger.info('\n✅ Dry run complete - no files were modified')
    logger.info('\nTo perform the actual migration, you would need to:')
    logger.info('1. Back up all router files')
    logger.info('2. Run the migration script with confirmation')
    logger.info('3. Test all endpoints with Stack Auth tokens')
    logger.info('4. Update any service layer code that expects User models')


if __name__ == '__main__':
    main()
