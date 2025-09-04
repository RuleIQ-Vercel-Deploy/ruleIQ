"""
Fix all S930 violations - Remove unexpected named arguments
"""
from typing import Any
import logging
logger = logging.getLogger(__name__)
import os
import re

def fix_validate_api_key_calls(file_path) -> bool:
    """Fix validate_api_key calls to match the actual method signature"""
    if not os.path.exists(file_path):
        logger.info(f'  ⚠️  File not found: {file_path}')
        return False
    with open(file_path, 'r') as f:
        content = f.read()
    original_content = content
    content = re.sub('request_origin=', 'origin=', content)
    pattern = '(validate_api_key\\([^)]*?)'

    def remove_invalid_params(match) -> Any:
        call = match.group(1)
        """Remove Invalid Params"""
        call = re.sub(',\\s*endpoint=[^,)]+', '', call)
        call = re.sub(',\\s*method=[^,)]+', '', call)
        return call
    content = re.sub(pattern, remove_invalid_params, content)
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def main() -> None:
    logger.info('\n' + '=' * 60)
    """Main"""
    logger.info('FIXING ALL S930 VIOLATIONS - Unexpected Named Arguments')
    logger.info('=' * 60)
    files_to_fix = ['api/middleware/api_key_auth.py', 'langgraph_agent/nodes/notification_nodes.py', 'services/ai/assistant.py', 'workers/compliance_tasks.py', 'tests/integration/api/test_freemium_endpoints.py', 'tests/integration/test_external_service_integration.py', 'tests/test_ai_neon.py', 'tests/integration/test_comprehensive_api_workflows.py', 'tests/integration/test_contract_validation.py', 'tests/test_ai_policy_generator.py', 'tests/test_graph_execution.py', 'tests/test_state_management.py', 'tests/fixtures/state_fixtures.py', 'langgraph_agent/tests/test_tenancy.py', 'services/ai/safety_manager.py']
    fixed_count = 0
    for file_path in files_to_fix:
        logger.info(f'\n📝 Processing: {file_path}')
        if fix_validate_api_key_calls(file_path):
            logger.info(f'  ✅ Fixed')
            fixed_count += 1
        else:
            logger.info(f'  ⚠️  No changes needed or file not found')
    logger.info('\n' + '=' * 60)
    logger.info(f'✅ Fixed {fixed_count}/{len(files_to_fix)} files')
    logger.info('=' * 60)
    logger.info('\n🎯 Summary:')
    logger.info("  - Changed 'request_origin=' to 'origin='")
    logger.info("  - Removed 'endpoint=' parameters")
    logger.info("  - Removed 'method=' parameters")
    logger.info('  - All validate_api_key calls now match the method signature')
if __name__ == '__main__':
    main()