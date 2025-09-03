"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Fix React unescaped entities by replacing them with proper JSX escaping
"""

from typing import Any, Dict, List, Optional
import os
import re
import glob

def fix_react_entities(content: str) ->Any:
    """Fix React unescaped entities"""
    patterns_and_replacements = [('&apos;', "'"), ('&quot;', '"'), (
        '&ldquo;', '"'), ('&rdquo;', '"'), ('&lsquo;', "'"), ('&rsquo;',
        "'"), ('&#39;', "'"), ('&#34;', '"'), ('&amp;', '&'), ('&lt;', '<'),
        ('&gt;', '>')]
    modified = False
    original_content = content
    for pattern, replacement in patterns_and_replacements:
        new_content = re.sub(pattern, replacement, content)
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
                modified_content, was_modified = fix_react_entities(
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
    logger.info('🔧 Fixing React unescaped entities...')
    modified_count = process_files()
    logger.info('\n✅ React entity fixes complete! Modified %s files.' %
        modified_count)
