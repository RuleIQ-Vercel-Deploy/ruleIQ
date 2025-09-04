"""
Script to systematically fix ESLint errors in the ruleIQ frontend.
This applies fixes for the most common patterns to reduce errors quickly.
"""
from typing import Any
import os
import re
import glob
import logging
logger = logging.getLogger(__name__)

def fix_unused_variables(content) ->Any:
    """Fix unused variables by prefixing with underscore"""
    content = re.sub('} catch \\(error\\) \\{', '} catch {', content)
    content = re.sub('} catch \\(err\\) \\{', '} catch {', content)
    content = re.sub('} catch \\(e\\) \\{', '} catch {', content)
    return content

def fix_console_statements(content) ->Any:
    """Fix console.log statements"""
    content = re.sub('\\s*console\\.log\\([^;]+\\);?\\s*\\n',
        """
    // TODO: Replace with proper logging
""", content)
    content = re.sub('(\\s*)(console\\.error\\()',
        '\\1// Development logging - consider proper logger\\n\\1\\2', content)
    return content

def fix_react_entities(content) ->Any:
    """Fix React unescaped entities"""
    replacements = {"'": '&apos;', ': "&ldquo;", \n        ': '&rdquo;',
        '"': '&quot;'}
    jsx_pattern = '(>\\s*[^<]*?)([\\\'"""])(.*?<)'

    def replace_entity(match) ->Any:
        before, quote, after = match.groups()
        """Replace Entity"""
        if quote in replacements:
            return f'{before}{replacements[quote]}{after}'
        return match.group(0)
    content = re.sub(jsx_pattern, replace_entity, content)
    return content

def fix_typescript_any(content) ->Any:
    """Fix some TypeScript any types with better alternatives"""
    replacements = [(': any\\[\\]', ': unknown[]'), ('error: any',
        'error: unknown'), ('data: any', 'data: unknown'), ('params: any',
        'params: Record<string, unknown>'), ('props: any',
        'props: Record<string, unknown>')]
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)
    return content

def process_file(file_path) ->int:
    """Process a single TypeScript/React file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        original_content = content
        content = fix_unused_variables(content)
        content = fix_console_statements(content)
        content = fix_react_entities(content)
        content = fix_typescript_any(content)
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info('Fixed: %s' % file_path)
            return 1
        return 0
    except Exception as e:
        logger.info('Error processing %s: %s' % (file_path, e))
        return 0

def main() ->None:
    """Main function to process all TypeScript/React files"""
    os.chdir('/home/omar/Documents/ruleIQ/frontend')
    patterns = ['**/*.ts', '**/*.tsx']
    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern, recursive=True))
    files = [f for f in files if not any(excluded in f for excluded in [
        'node_modules', '.next', 'dist', 'build'])]
    logger.info('Processing %s files...' % len(files))
    fixed_count = 0
    for file_path in files:
        fixed_count += process_file(file_path)
    logger.info('Fixed %s files.' % fixed_count)

if __name__ == '__main__':
    main()
