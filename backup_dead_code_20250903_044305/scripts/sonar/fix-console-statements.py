"""
Fix console statements by replacing them with TODO comments or proper logging patterns
"""
from typing import Any, Tuple
import logging
logger = logging.getLogger(__name__)
import os
import re
import glob


def fix_console_statements(content) ->Tuple[Any, ...]:
    """Replace console statements with appropriate alternatives"""
    patterns_and_replacements = [(
        '(\\s*)// Development logging - consider proper logger\\s*\\n\\s*console\\.error\\([^;]+\\);'
        ,
        '\\1// TODO: Replace with proper logging\\n\\1// console.error(...);'
        ), ('(\\s*)console\\.log\\([^;]+\\);',
        '\\1// TODO: Replace with proper logging'), (
        '(\\s*)console\\.error\\([^;]+\\);',
        '\\1// TODO: Replace with proper logging'), (
        '(\\s*)console\\.warn\\([^;]+\\);',
        '\\1// TODO: Replace with proper logging'), (
        '(\\s*)console\\.info\\([^;]+\\);',
        '\\1// TODO: Replace with proper logging'), (
        '(\\s*)console\\.debug\\([^;]+\\);',
        '\\1// TODO: Replace with proper logging')]
    modified = False
    for pattern, replacement in patterns_and_replacements:
        new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        if new_content != content:
            modified = True
            content = new_content
    return content, modified


def process_files() ->Any:
    """Process all TypeScript/JavaScript files in the frontend directory"""
    patterns = ['app/**/*.tsx', 'app/**/*.ts', 'components/**/*.tsx',
        'components/**/*.ts', 'lib/**/*.tsx', 'lib/**/*.ts']
    files_processed = 0
    files_modified = 0
    for pattern in patterns:
        for file_path in glob.glob(pattern, recursive=True):
            try:
                if 'node_modules' in file_path or '.next' in file_path:
                    continue
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_content = f.read()
                modified_content, was_modified = fix_console_statements(
                    original_content)
                if was_modified:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(modified_content)
                    logger.info('✓ Fixed: %s' % file_path)
                    files_modified += 1
                files_processed += 1
            except Exception as e:
                logger.info('✗ Error processing %s: %s' % (file_path, e))
    logger.info('\nProcessed %s files' % files_processed)
    logger.info('Modified %s files' % files_modified)
    return files_modified


if __name__ == '__main__':
    logger.info('🔧 Fixing console statements...')
    modified_count = process_files()
    logger.info('\n✅ Console statement fixes complete! Modified %s files.' %
        modified_count)
