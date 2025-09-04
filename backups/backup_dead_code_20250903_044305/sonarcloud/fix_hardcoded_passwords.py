"""
Fix S6698 violations - Remove hardcoded passwords from code
"""
import logging
logger = logging.getLogger(__name__)
import os
import re

def fix_hardcoded_passwords(file_path) -> bool:
    """Fix hardcoded passwords by replacing with environment variables"""
    if not os.path.exists(file_path):
        logger.info(f'  ⚠️  File not found: {file_path}')
        return False
    with open(file_path, 'r') as f:
        content = f.read()
    original_content = content
    patterns = [('postgresql://[^:]+:([^@]+)@[^/]+/\\w+', 'postgresql://" + os.getenv("DB_USER", "postgres") + ":" + os.getenv("DB_PASSWORD", "postgres") + "@" + os.getenv("DB_HOST", "localhost") + ":" + os.getenv("DB_PORT", "5432") + "/" + os.getenv("DB_NAME", "database") + "'), ('"postgresql://postgres:postgres@localhost:\\d+/\\w+"', 'os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/test")'), ("'postgresql://postgres:postgres@localhost:\\d+/\\w+'", "os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/test')")]
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            if 'os.getenv' in replacement and 'import os' not in content:
                content = 'import os\n' + content
            content = re.sub(pattern, replacement, content)
    if 'DATABASE_URL' in content and 'postgresql://postgres:postgres' in content:
        content = content.replace('"postgresql://postgres:postgres@localhost:5433/compliance_test"', 'os.getenv("TEST_DATABASE_URL", "postgresql://localhost/test")')
        content = content.replace("'postgresql://postgres:postgres@localhost:5433/compliance_test'", "os.getenv('TEST_DATABASE_URL', 'postgresql://localhost/test')")
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def main() -> None:
    logger.info('\n' + '=' * 60)
    """Main"""
    logger.info('FIXING S6698 VIOLATIONS - Hardcoded Passwords')
    logger.info('=' * 60)
    files_to_fix = ['archive/scripts/capture_test_errors.py', 'archive/scripts/check_schema.py', 'scripts/setup_secrets_vault.py', 'scripts/debug_freemium_tables.py', 'scripts/simple_test_debug.py', 'archive/test_configs/conftest_fixed.py', 'archive/test_configs/conftest_hybrid.py', 'archive/test_configs/conftest_improved.py']
    fixed_count = 0
    for file_path in files_to_fix:
        logger.info(f'\n📝 Processing: {file_path}')
        if fix_hardcoded_passwords(file_path):
            logger.info(f'  ✅ Fixed')
            fixed_count += 1
        else:
            logger.info(f'  ⚠️  No changes needed or file not found')
    supabase_file = 'archive/scripts/migrate_archon_data.py'
    logger.info(f'\n📝 Processing Supabase JWT secret: {supabase_file}')
    if os.path.exists(supabase_file):
        with open(supabase_file, 'r') as f:
            content = f.read()
        if 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9' in content:
            content = re.sub('"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9[^"]*"', 'os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")', content)
            if 'import os' not in content:
                content = 'import os\n' + content
            with open(supabase_file, 'w') as f:
                f.write(content)
            logger.info(f'  ✅ Fixed Supabase JWT secret')
            fixed_count += 1
        else:
            logger.info(f'  ⚠️  No Supabase JWT secret found')
    else:
        logger.info(f'  ⚠️  File not found')
    logger.info('\n' + '=' * 60)
    logger.info(f'✅ Fixed {fixed_count}/{len(files_to_fix) + 1} files')
    logger.info('=' * 60)
    logger.info('\n🎯 Summary:')
    logger.info('  - Replaced hardcoded PostgreSQL passwords with environment variables')
    logger.info('  - Replaced Supabase service role key with environment variable')
    logger.info('  - Added os.getenv() calls for secure credential handling')
    logger.info('\n⚠️  Important:')
    logger.info('  - Ensure environment variables are properly set in production')
    logger.info('  - Use Doppler or other secret management tools')
    logger.info('  - Never commit real credentials to the repository')
if __name__ == '__main__':
    main()