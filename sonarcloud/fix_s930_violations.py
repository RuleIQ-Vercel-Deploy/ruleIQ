"""
Fix S930 violations - Remove unexpected named arguments
"""
import logging
logger = logging.getLogger(__name__)
import os
import re
FIXES = [{'file': 'api/dependencies/auth.py', 'pattern': 'request_origin=request\\.headers\\.get\\(\\"Origin\\"\\)', 'replacement': 'origin=request.headers.get("Origin")', 'lines': [323]}, {'file': 'api/dependencies/auth.py', 'pattern': 'endpoint=str\\(request\\.url\\.path\\)', 'replacement': '', 'lines': [324]}, {'file': 'api/dependencies/auth.py', 'pattern': 'method=request\\.method,', 'replacement': '', 'lines': [325]}, {'file': 'api/middleware/api_key_auth.py', 'pattern': 'request_origin=', 'replacement': 'origin=', 'lines': [125, 127, 128]}, {'file': 'langgraph_agent/nodes/notification_nodes.py', 'pattern': 'request_origin=', 'replacement': 'origin=', 'lines': [851, 852, 857, 858, 862, 863]}, {'file': 'services/ai/assistant.py', 'pattern': 'request_origin=', 'replacement': 'origin=', 'lines': [4518, 4519, 4520, 4521, 4522, 4523, 4524]}, {'file': 'workers/compliance_tasks.py', 'pattern': 'request_origin=', 'replacement': 'origin=', 'lines': [40, 84]}]

def fix_file(file_path, fixes) -> bool:
    """Fix a single file"""
    if not os.path.exists(file_path):
        logger.info(f'⚠️  File not found: {file_path}')
        return False
    with open(file_path, 'r') as f:
        lines = f.readlines()
    modified = False
    for fix in fixes:
        for line_num in fix['lines']:
            idx = line_num - 1
            if idx < len(lines):
                old_line = lines[idx]
                if fix['replacement']:
                    new_line = re.sub(fix['pattern'], fix['replacement'], old_line)
                elif fix['pattern'] in old_line:
                    if old_line.strip().startswith(fix['pattern'].replace('\\(', '(').replace('\\)', ')')):
                        new_line = ''
                    else:
                        new_line = re.sub(fix['pattern'] + ',?\\s*', '', old_line)
                else:
                    new_line = old_line
                if new_line != old_line:
                    lines[idx] = new_line
                    modified = True
                    logger.info(f'  Fixed line {line_num}')
    if modified:
        with open(file_path, 'w') as f:
            f.writelines(lines)
        return True
    return False

def main() -> None:
    logger.info('\n' + '=' * 60)
    logger.info('FIXING S930 VIOLATIONS - Unexpected Named Arguments')
    logger.info('=' * 60)
    fixes_by_file = {}
    for fix in FIXES:
        file_path = fix['file']
        if file_path not in fixes_by_file:
            fixes_by_file[file_path] = []
        fixes_by_file[file_path].append(fix)
    total_fixed = 0
    for file_path, file_fixes in fixes_by_file.items():
        logger.info(f'\n📝 Processing: {file_path}')
        if fix_file(file_path, file_fixes):
            total_fixed += 1
            logger.info(f'  ✅ Fixed {len(file_fixes)} issues')
        else:
            logger.info(f'  ⚠️  No changes made')
    logger.info('\n' + '=' * 60)
    logger.info(f'✅ Fixed files: {total_fixed}/{len(fixes_by_file)}')
    logger.info('=' * 60)
    logger.info('\n🔧 Fixing test files with similar issues...')
    test_files = ['tests/integration/api/test_freemium_endpoints.py', 'tests/integration/test_external_service_integration.py', 'tests/test_ai_neon.py', 'tests/integration/test_comprehensive_api_workflows.py', 'tests/integration/test_contract_validation.py', 'tests/test_ai_policy_generator.py', 'tests/test_graph_execution.py', 'tests/test_state_management.py', 'tests/fixtures/state_fixtures.py', 'langgraph_agent/tests/test_tenancy.py', 'services/ai/safety_manager.py']
    for test_file in test_files:
        if os.path.exists(test_file):
            with open(test_file, 'r') as f:
                content = f.read()
            new_content = re.sub('request_origin=', 'origin=', content)
            new_content = re.sub(',\\s*endpoint=[^,\\)]+', '', new_content)
            new_content = re.sub(',\\s*method=[^,\\)]+', '', new_content)
            if new_content != content:
                with open(test_file, 'w') as f:
                    f.write(new_content)
                logger.info(f'✅ Fixed: {test_file}')
if __name__ == '__main__':
    main()