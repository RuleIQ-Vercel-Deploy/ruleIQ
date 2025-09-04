"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Script to update all router files from Stack Auth to JWT authentication
"""

import re
from pathlib import Path


def update_file(file_path) ->bool:
    """Update a single file to use JWT auth instead of Stack Auth"""
    logger.info('Updating %s...' % file_path)
    with open(file_path, 'r') as f:
        content = f.read()
    original_content = content
    content = re.sub(
        'from api\\.dependencies\\.stack_auth import get_current_stack_user(?:, get_current_user)?(?:, User)?'
        ,
        """from api.dependencies.auth import get_current_active_user
from database.user import User"""
        , content)
    content = re.sub('current_user: dict = Depends\\(get_current_stack_user\\)'
        , 'current_user: User = Depends(get_current_active_user)', content)
    content = re.sub('Depends\\(get_current_stack_user\\)',
        'Depends(get_current_active_user)', content)
    content = re.sub('current_user\\["id"\\]', 'str(current_user.id)', content)
    content = re.sub('current_user\\[\\"email\\"\\]', 'current_user.email',
        content)
    content = re.sub('current_user\\.get\\("id"\\)', 'str(current_user.id)',
        content)
    content = re.sub('current_user\\.get\\("email"\\)',
        'current_user.email', content)
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        logger.info('✅ Updated %s' % file_path)
        return True
    else:
        logger.info('⏭️  No changes needed for %s' % file_path)
        return False


def main() ->None:
    """Main function to update all router files"""
    router_dir = Path('api/routers')
    files_to_update = []
    for py_file in router_dir.glob('*.py'):
        if py_file.name == '__init__.py':
            continue
        with open(py_file, 'r') as f:
            content = f.read()
            if 'get_current_stack_user' in content:
                files_to_update.append(py_file)
    logger.info('Found %s files to update:' % len(files_to_update))
    for file_path in files_to_update:
        logger.info('  - %s' % file_path)
    logger.info('\nStarting updates...')
    updated_count = 0
    for file_path in files_to_update:
        if update_file(file_path):
            updated_count += 1
    logger.info('\n✅ Successfully updated %s files' % updated_count)
    logger.info('🔧 Manual review may be needed for complex usage patterns')


if __name__ == '__main__':
    main()
