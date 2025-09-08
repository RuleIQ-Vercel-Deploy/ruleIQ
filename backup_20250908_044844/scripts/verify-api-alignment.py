"""Verify API alignment after fixes."""
import logging
logger = logging.getLogger(__name__)
from typing import Any, Dict, List, Optional
import re
from pathlib import Path
from collections import defaultdict
issues = defaultdict(list)
for router_file in Path('api').rglob('*.py'):
    with open(router_file, 'r') as f:
        content = f.read()
    if 'APIRouter' not in content:
        continue
    router_name = router_file.stem
    params = re.findall('\\{([^}]+)\\}', content)
    for param in params:
        if param not in ['id', 'token', 'model', 'stage']:
            issues['non_standard_params'].append(f'{router_name}: {param}')
    if 'prefix=' in content:
        prefix_match = re.search('prefix=[\\\'"`]([^\\\'"`]+)[\\\'"`]', content,
            )
        if prefix_match:
            prefix = prefix_match.group(1)
            if not prefix.startswith('/api/v1'):
                issues['bad_prefix'].append(f'{router_name}: {prefix}')
if issues:
    logger.info('⚠️  Issues found:')
    for issue_type, items in issues.items():
        logger.info('\n%s:' % issue_type)
        for item in items:
            logger.info('  - %s' % item)
else:
    logger.info('✅ All API endpoints properly aligned!')
