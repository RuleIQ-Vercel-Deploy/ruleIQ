"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Establish proper Alembic baseline by consolidating migrations.

This script:
1. Removes the empty initial migration
2. Makes the comprehensive migration the new baseline
3. Ensures clean migration history for production deployment
"""

import os
import sys
import subprocess
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


def main() ->bool:
    """Establish Alembic baseline."""
    logger.info('🔧 Establishing Alembic baseline...')
    os.chdir(project_root)
    logger.info('📋 Checking current Alembic status...')
    result = subprocess.run([sys.executable, '-m', 'alembic', 'current'],
        capture_output=True, text=True)
    if result.returncode != 0:
        logger.info('❌ Failed to check Alembic status: %s' % result.stderr)
        return False
    logger.info('Current revision: %s' % result.stdout.strip())
    empty_migration = (project_root / 'alembic' / 'versions' /
        'cdd9337435cf_initial_empty_migration.py')
    if empty_migration.exists():
        logger.info('🗑️ Removing empty initial migration...')
        empty_migration.unlink()
        logger.info('✅ Empty migration removed')
    comprehensive_migration = (project_root / 'alembic' / 'versions' /
        '802adb6d1be8_add_check_constraint_to_compliance_.py')
    if comprehensive_migration.exists():
        logger.info('📝 Updating comprehensive migration to be baseline...')
        with open(comprehensive_migration, 'r') as f:
            content = f.read()
        updated_content = content.replace("down_revision = 'cdd9337435cf'",
            'down_revision = None')
        updated_content = updated_content.replace(
            '"Add check constraint to compliance_frameworks"',
            '"Baseline schema - comprehensive database structure"')
        with open(comprehensive_migration, 'w') as f:
            f.write(updated_content)
        logger.info('✅ Comprehensive migration updated as baseline')
    logger.info('🔄 Updating Alembic revision history...')
    result = subprocess.run([sys.executable, '-m', 'alembic', 'stamp',
        'head'], capture_output=True, text=True)
    if result.returncode != 0:
        logger.info('❌ Failed to stamp Alembic head: %s' % result.stderr)
        return False
    logger.info('✅ Alembic baseline established successfully!')
    logger.info('🔍 Verifying baseline setup...')
    result = subprocess.run([sys.executable, '-m', 'alembic', 'current'],
        capture_output=True, text=True)
    if result.returncode == 0:
        logger.info('✅ Current revision: %s' % result.stdout.strip())
        logger.info('🎉 Alembic baseline establishment complete!')
        return True
    else:
        logger.info('❌ Verification failed: %s' % result.stderr)
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
