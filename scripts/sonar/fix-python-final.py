"""Final comprehensive Python linting fix script."""
import logging
logger = logging.getLogger(__name__)
import os
import re
import subprocess

def run_ruff_autofix() -> None:
    """Run ruff with autofix for simple issues."""
    logger.info('Running ruff autofix...')
    subprocess.run(['ruff', 'check', 'api', '--fix', '--unsafe-fixes'], cwd='/home/omar/Documents/ruleIQ', capture_output=True)
    subprocess.run(['ruff', 'format', 'api'], cwd='/home/omar/Documents/ruleIQ', capture_output=True)

def fix_specific_files() -> None:
    """Fix specific known issues in files."""
    fixes = {'/home/omar/Documents/ruleIQ/api/auth.py': [('f"\\[AUTH DEBUG\\] JWT Secret for decoding: {settings\\.jwt_secret\\[:10\\] if settings\\.jwt_secret else \\\'None\\\'}..."', 'f"[AUTH DEBUG] JWT Secret: {settings.jwt_secret[:10] if settings.jwt_secret else \'None\'}..."')], '/home/omar/Documents/ruleIQ/api/clients/aws_client.py': [('\\brule\\.get\\("FromPort"\\) == 22\\b', 'rule.get("FromPort") == SSH_PORT'), ('\\brule\\.get\\("FromPort"\\) == 3389\\b', 'rule.get("FromPort") == RDP_PORT')], '/home/omar/Documents/ruleIQ/api/clients/base_api_client.py': [('response\\.status == 429', 'response.status == HTTP_TOO_MANY_REQUESTS'), ('response\\.status == 401', 'response.status == HTTP_UNAUTHORIZED'), ('response\\.status >= 500', 'response.status >= HTTP_INTERNAL_ERROR'), ('response\\.status >= 400', 'response.status >= HTTP_BAD_REQUEST'), ('total_seconds\\(\\) > 3600', 'total_seconds() > HOUR_IN_SECONDS')], '/home/omar/Documents/ruleIQ/api/dependencies/auth.py': [('if len\\(password\\) < 8:', 'if len(password) < MIN_PASSWORD_LENGTH:'), ('time_until_expiry\\.total_seconds\\(\\) < 300', 'time_until_expiry.total_seconds() < TOKEN_EXPIRY_WARNING')], '/home/omar/Documents/ruleIQ/api/dependencies/file.py': [('if len\\(name\\) > 100:', 'if len(name) > MAX_FILENAME_LENGTH:'), ('if pk_count > 100:', 'if pk_count > MAX_PK_COUNT:'), ('if exif_size > 65535:', 'if exif_size > MAX_EXIF_SIZE:')]}
    constants = {'/home/omar/Documents/ruleIQ/api/clients/aws_client.py': '\nSSH_PORT = 22\nRDP_PORT = 3389\n', '/home/omar/Documents/ruleIQ/api/clients/base_api_client.py': '\nHTTP_BAD_REQUEST = 400\nHTTP_UNAUTHORIZED = 401\nHTTP_TOO_MANY_REQUESTS = 429\nHTTP_INTERNAL_ERROR = 500\nHOUR_IN_SECONDS = 3600\n', '/home/omar/Documents/ruleIQ/api/dependencies/auth.py': '\nMIN_PASSWORD_LENGTH = 8\nTOKEN_EXPIRY_WARNING = 300\n', '/home/omar/Documents/ruleIQ/api/dependencies/file.py': '\nMAX_FILENAME_LENGTH = 100\nMAX_PK_COUNT = 100\nMAX_EXIF_SIZE = 65535\n'}
    for filepath, const_block in constants.items():
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            lines = content.split('\n')
            import_end = 0
            for i, line in enumerate(lines):
                if line.strip() and (not line.startswith('import')) and (not line.startswith('from')) and (not line.startswith('#')):
                    if i > 0 and any((lines[j].startswith(('import', 'from')) for j in range(max(0, i - 5), i))):
                        import_end = i
                        break
            const_lines = const_block.strip().split('\n')
            needs_adding = False
            for const_line in const_lines:
                if const_line.strip():
                    const_name = const_line.split(' = ')[0].strip()
                    if const_name and const_name not in content:
                        needs_adding = True
                        break
            if needs_adding and import_end > 0:
                lines.insert(import_end, const_block)
                content = '\n'.join(lines)
                with open(filepath, 'w') as f:
                    f.write(content)
                logger.info(f'Added constants to {filepath}')
    for filepath, replacements in fixes.items():
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            for pattern, replacement in replacements:
                content = re.sub(pattern, replacement, content)
            with open(filepath, 'w') as f:
                f.write(content)
            logger.info(f'Fixed specific issues in {filepath}')

def fix_long_lines() -> None:
    """Fix long lines in Python files."""
    result = subprocess.run(['ruff', 'check', 'api', '--select=E501'], capture_output=True, text=True, cwd='/home/omar/Documents/ruleIQ')
    for line in result.stdout.split('\n'):
        if 'E501' in line and '.py:' in line:
            parts = line.split(':')
            if len(parts) >= 2:
                filepath = '/home/omar/Documents/ruleIQ/' + parts[0].strip()
                try:
                    line_num = int(parts[1])
                    if os.path.exists(filepath):
                        with open(filepath, 'r') as f:
                            lines = f.readlines()
                        if line_num <= len(lines):
                            long_line = lines[line_num - 1]
                            if 'f"' in long_line or "f'" in long_line:
                                if '{' in long_line and '}' in long_line:
                                    indent = len(long_line) - len(long_line.lstrip())
                                    if len(long_line) > 100:
                                        break_pos = 80
                                        for char in [',', ' ', '.']:
                                            pos = long_line.rfind(char, 60, 90)
                                            if pos > 0:
                                                break_pos = pos + 1
                                                break
                                        lines[line_num - 1] = long_line[:break_pos] + '"\n' + ' ' * (indent + 4) + 'f"' + long_line[break_pos:]
                            elif '"$select":' in long_line:
                                indent = len(long_line) - len(long_line.lstrip())
                                if ',' in long_line:
                                    parts = long_line.split(',')
                                    if len(parts) > 2:
                                        lines[line_num - 1] = ','.join(parts[:2]) + ',"\n'
                                        lines.insert(line_num, ' ' * (indent + 4) + '"' + ','.join(parts[2:]))
                            elif '#' in long_line and (not long_line.strip().startswith('#')):
                                code_part = long_line.split('#')[0].rstrip()
                                comment_part = '#' + long_line.split('#', 1)[1]
                                if len(code_part) <= 100:
                                    continue
                                indent = len(long_line) - len(long_line.lstrip())
                                lines[line_num - 1] = ' ' * indent + comment_part
                                lines.insert(line_num, code_part + '\n')
                        with open(filepath, 'w') as f:
                            f.writelines(lines)
                except (ValueError, IndexError):
                    continue

def fix_annotations() -> None:
    """Fix missing type annotations."""
    files_to_fix = {'/home/omar/Documents/ruleIQ/api/clients/base_api_client.py': [('async def __aenter__(self):', 'async def __aenter__(self) -> "BaseAPIClient":'), ('async def __aexit__(self, exc_type, exc_val, exc_tb):', 'async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:')], '/home/omar/Documents/ruleIQ/api/clients/google_workspace_client.py': [('def from_authorized_user_info(cls, info, scopes):', 'def from_authorized_user_info(cls, info, scopes) -> "Credentials":')]}
    for filepath, replacements in files_to_fix.items():
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                content = f.read()
            for old, new in replacements:
                content = content.replace(old, new)
            with open(filepath, 'w') as f:
                f.write(content)
            logger.info(f'Fixed annotations in {filepath}')

def main() -> None:
    """Main execution."""
    logger.info('Starting final Python linting fixes...\n')
    run_ruff_autofix()
    fix_specific_files()
    logger.info('\nFixing long lines...')
    fix_long_lines()
    logger.info('\nFixing type annotations...')
    fix_annotations()
    run_ruff_autofix()
    result = subprocess.run(['ruff', 'check', 'api', '--statistics'], capture_output=True, text=True, cwd='/home/omar/Documents/ruleIQ')
    logger.info('\n' + '=' * 50)
    logger.info('Final statistics:')
    logger.info(result.stdout)
    result = subprocess.run(['ruff', 'check', 'api'], capture_output=True, text=True, cwd='/home/omar/Documents/ruleIQ')
    remaining = len([l for l in result.stdout.split('\n') if l.strip()])
    logger.info(f'\n✅ Remaining issues: {remaining}')
if __name__ == '__main__':
    main()
