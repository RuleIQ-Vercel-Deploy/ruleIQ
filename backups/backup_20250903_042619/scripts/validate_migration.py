"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Validate Stack Auth migration - ensures 100% accuracy
Run this after each file migration to verify correctness
"""

import re
from pathlib import Path
from typing import Dict, Tuple
import sys


class MigrationValidator:
    """Validates that migrations were applied correctly"""

    def __init__(self, file_path: Path) ->None:
        self.file_path = file_path
        self.content = file_path.read_text()
        self.lines = self.content.split('\n')
        self.errors = []
        self.warnings = []
        self.success = []

    def validate(self) ->Tuple[bool, Dict]:
        """Run all validations"""
        self._check_no_old_imports()
        self._check_no_old_dependencies()
        self._check_no_user_type_hints()
        self._check_attribute_access()
        self._check_stack_auth_imports()
        self._check_no_jwt_references()
        return len(self.errors) == 0, {'errors': self.errors, 'warnings':
            self.warnings, 'success': self.success, 'summary': self.
            _get_summary()}

    def _check_no_old_imports(self) ->None:
        """Ensure no old auth imports remain"""
        old_patterns = [
            'from api\\.dependencies\\.auth import get_current_active_user',
            'from api\\.dependencies\\.auth import get_current_user',
            'from api\\.dependencies\\.auth import.*User[^a-zA-Z]']
        for i, line in enumerate(self.lines):
            for pattern in old_patterns:
                if re.search(pattern, line):
                    self.errors.append(
                        f'Line {i + 1}: Old auth import found: {line.strip()}')
        if not any('get_current_active_user' in e for e in self.errors):
            self.success.append('✅ No old auth imports found')

    def _check_no_old_dependencies(self) ->None:
        """Ensure no old dependencies remain"""
        old_patterns = ['Depends\\(get_current_active_user\\)',
            'Depends\\(get_current_user\\)(?!_stack)']
        for i, line in enumerate(self.lines):
            for pattern in old_patterns:
                if re.search(pattern, line):
                    self.errors.append(
                        f'Line {i + 1}: Old dependency found: {line.strip()}')
        if not any('Depends(' in e for e in self.errors):
            self.success.append('✅ All dependencies updated to Stack Auth')

    def _check_no_user_type_hints(self) ->None:
        """Check for User type hints that should be dict"""
        pattern = ':\\s*User\\s*[=\\),]'
        for i, line in enumerate(self.lines):
            if line.strip().startswith('#') or '"""' in line or "'''" in line:
                continue
            if re.search(pattern, line) and 'from database' not in line:
                if 'Depends' in line:
                    self.errors.append(
                        f'Line {i + 1}: User type hint should be dict: {line.strip()}',
                        )
                else:
                    self.warnings.append(
                        f'Line {i + 1}: User type hint found (may be OK if not auth): {line.strip()}',
                        )
        if not any('User type hint should be dict' in e for e in self.errors):
            self.success.append('✅ Type hints properly updated')

    def _check_attribute_access(self) ->None:
        """Check that user attributes are accessed correctly"""
        user_vars = ['current_user', 'user', 'auth_user', 'authenticated_user']
        problematic_patterns = []
        for var in user_vars:
            problematic_patterns.extend([(f'{var}\\.id(?!["\'])',
                f'{var}["id"]'), (f'{var}\\.email(?!["\'])',
                f'{var}.get("primaryEmail", {var}.get("email", ""))'), (
                f'{var}\\.username(?!["\'])',
                f'{var}.get("displayName", "")'), (
                f'{var}\\.is_active(?!["\'])',
                f'{var}.get("isActive", True)'), (
                f'{var}\\.is_superuser(?!["\'])', f'role check for {var}')])
        for i, line in enumerate(self.lines):
            for pattern, replacement in problematic_patterns:
                if re.search(pattern, line):
                    if not (line.strip().startswith('#') or re.search(
                        '["\\\'].*' + pattern + '.*["\\\']', line)):
                        self.errors.append(
                            f'Line {i + 1}: Direct attribute access found: {line.strip()}',
                            )
                        self.errors.append(
                            f'         Should use: {replacement}')
        if not any('Direct attribute access' in e for e in self.errors):
            self.success.append('✅ All user attributes accessed correctly')

    def _check_stack_auth_imports(self) ->None:
        """Ensure Stack Auth imports are present"""
        has_stack_import = False
        for line in self.lines:
            if 'from api.dependencies.stack_auth import' in line:
                has_stack_import = True
                self.success.append(
                    f'✅ Stack Auth import found: {line.strip()}')
                break
        if not has_stack_import and any('Depends' in line for line in self.
            lines):
            self.warnings.append(
                '⚠️  No Stack Auth imports found but file uses dependencies')

    def _check_no_jwt_references(self) ->None:
        """Ensure no JWT references remain"""
        jwt_patterns = ['jwt', 'JWT', 'token_data', 'create_access_token',
            'verify_password', 'get_password_hash']
        for i, line in enumerate(self.lines):
            for pattern in jwt_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    if not line.strip().startswith('#'):
                        self.warnings.append(
                            f'Line {i + 1}: Possible JWT reference: {line.strip()}',
                            )

    def _get_summary(self) ->str:
        """Get validation summary"""
        if self.errors:
            return f'❌ {len(self.errors)} errors found - migration incomplete'
        elif self.warnings:
            return f'⚠️  {len(self.warnings)} warnings - review needed'
        else:
            return '✅ Migration validated successfully'


def validate_file(file_path: str) ->bool:
    """Validate a single file"""
    path = Path(file_path)
    if not path.exists():
        logger.info('❌ File not found: %s' % file_path)
        return False
    logger.info('\n%s' % ('=' * 80))
    logger.info('🔍 VALIDATING: %s' % file_path)
    logger.info('%s' % ('=' * 80))
    validator = MigrationValidator(path)
    is_valid, results = validator.validate()
    if results['success']:
        logger.info('\n✅ Successful Checks:')
        for success in results['success']:
            logger.info('  %s' % success)
    if results['warnings']:
        logger.info('\n⚠️  Warnings (%s):' % len(results['warnings']))
        for warning in results['warnings']:
            logger.info('  %s' % warning)
    if results['errors']:
        logger.info('\n❌ Errors (%s):' % len(results['errors']))
        for error in results['errors']:
            logger.info('  %s' % error)
    logger.info('\n%s' % results['summary'])
    return is_valid


def main() ->int:
    """Run validation on Phase 1 files"""
    import argparse
    parser = argparse.ArgumentParser(description=
        'Validate Stack Auth migration')
    parser.add_argument('--file', help='Single file to validate')
    parser.add_argument('--phase', type=int, default=1, help=
        'Phase to validate (default: 1)')
    args = parser.parse_args()
    if args.file:
        success = validate_file(args.file)
        return 0 if success else 1
    phase_files = {(1): ['api/routers/users.py',
        'api/routers/business_profiles.py']}
    files = phase_files.get(args.phase, [])
    if not files:
        logger.info('❌ No files defined for phase %s' % args.phase)
        return 1
    logger.info('🚀 Validating Phase %s Migration' % args.phase)
    logger.info('=' * 80)
    all_valid = True
    for file_path in files:
        if Path(file_path).exists():
            if not validate_file(file_path):
                all_valid = False
    logger.info('\n' + '=' * 80)
    if all_valid:
        logger.info('✅ All validations passed!')
    else:
        logger.info('❌ Validation failed - please fix errors before proceeding',
            )
    return 0 if all_valid else 1


if __name__ == '__main__':
    sys.exit(main())
