"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Implement API alignment fixes for ruleIQ codebase.
This script:
1. Removes duplicate endpoints
2. Standardizes parameter naming
3. Ensures all endpoints use /api/v1/ prefix
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
import json

class APIAlignmentFixer:

    """Class for APIAlignmentFixer"""
    def __init__(self):
        self.api_dir = Path('api')
        self.fixes_applied = []
        self.duplicate_handlers = {'/api/v1/health': 'monitoring',
            '/api/v1/metrics': 'monitoring', '/api/v1/me': 'auth',
            '/api/v1/plans': 'implementation', '/api/v1/recommendations':
            'frameworks', '/api/v1/circuit-breaker/status':
            'ai_optimization', '/api/v1/cache/metrics': 'ai_optimization',
            '/api/v1/generate-policy': 'ai_policy', '/api/v1/generate':
            'policies', '/api/v1/dashboard': 'dashboard'}

    def fix_parameter_naming(self, file_path: Path) ->List[str]:
        """Standardize parameter naming to use {id} format."""
        changes = []
        with open(file_path, 'r') as f:
            content = f.read()
            original_content = content
        param_replacements = [('\\{alertId\\}', '{id}'), ('\\{plan_id\\}',
            '{id}'), ('\\{task_id\\}', '{id}'), ('\\{profileId\\}', '{id}'),
            ('\\{reportId\\}', '{id}'), ('\\{session_token\\}', '{token}'),
            ('\\{model_name\\}', '{model}')]
        for old_param, new_param in param_replacements:
            if re.search(old_param, content):
                content = re.sub(old_param, new_param, content)
                changes.append(f'  Replaced {old_param} with {new_param}')
        if '{id}' in content:
            content = re.sub('def \\w+\\([^)]*\\bplan_id\\b', lambda m: m.
                group(0).replace('plan_id', 'id'), content)
            content = re.sub('def \\w+\\([^)]*\\btask_id\\b', lambda m: m.
                group(0).replace('task_id', 'id'), content)
            content = re.sub('def \\w+\\([^)]*\\balertId\\b', lambda m: m.
                group(0).replace('alertId', 'id'), content)
            content = re.sub('def \\w+\\([^)]*\\bprofileId\\b', lambda m: m
                .group(0).replace('profileId', 'id'), content)
            content = re.sub('def \\w+\\([^)]*\\breportId\\b', lambda m: m.
                group(0).replace('reportId', 'id'), content)
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
        return changes

    def remove_duplicate_endpoints(self, file_path: Path, router_name: str
        ) ->List[str]:
        """Remove duplicate endpoints that should exist in other routers."""
        changes = []
        with open(file_path, 'r') as f:
            content = f.read()
            original_content = content
        lines = content.split('\n')
        new_lines = []
        skip_until = -1
        for i, line in enumerate(lines):
            if i <= skip_until:
                continue
            route_match = re.match(
                '^@\\w+\\.(get|post|put|patch|delete)\\([\\\'"`]([^\\\'"`]+)[\\\'"`]'
                , line)
            if route_match:
                method = route_match.group(1).upper()
                path = route_match.group(2)
                full_path = f'/api/v1{path}' if not path.startswith('/api/'
                    ) else path
                should_keep = True
                for dup_path, keep_in_router in self.duplicate_handlers.items(
                    ):
                    if full_path == dup_path and router_name != keep_in_router:
                        should_keep = False
                        changes.append(
                            f'  Removed duplicate {method} {full_path} (kept in {keep_in_router})',
                            )
                        j = i + 1
                        while j < len(lines):
                            if lines[j] and not lines[j].startswith(' '
                                ) and not lines[j].startswith('\t'):
                                break
                            if re.match('^(def |class |@)', lines[j]):
                                break
                            j += 1
                        skip_until = j - 1
                        break
                if should_keep:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        new_content = '\n'.join(new_lines)
        new_content = re.sub('\\n\\n\\n+', '\n\n', new_content)
        if new_content != original_content:
            with open(file_path, 'w') as f:
                f.write(new_content)
        return changes

    def ensure_api_v1_prefix(self, file_path: Path) ->List[str]:
        """Ensure all endpoints use /api/v1/ prefix."""
        changes = []
        with open(file_path, 'r') as f:
            content = f.read()
            original_content = content
        if 'prefix=' in content:
            patterns = [('prefix=[\\\'"`]/([^/][^\\\'"`]*)[\\\'"`]',
                'prefix="/api/v1/\\1"'), (
                'prefix=[\\\'"`]([^/][^\\\'"`]*)[\\\'"`]',
                'prefix="/api/v1/\\1"'), (
                'prefix=[\\\'"`]/api/([^v][^\\\'"`]*)[\\\'"`]',
                'prefix="/api/v1/\\1"')]
            for pattern, replacement in patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    changes.append(f'  Updated router prefix to use /api/v1/')
        if content != original_content:
            with open(file_path, 'w') as f:
                f.write(content)
        return changes

    def fix_router_file(self, file_path: Path) ->Dict:
        """Apply all fixes to a router file."""
        router_name = file_path.stem
        all_changes = []
        prefix_changes = self.ensure_api_v1_prefix(file_path)
        all_changes.extend(prefix_changes)
        param_changes = self.fix_parameter_naming(file_path)
        all_changes.extend(param_changes)
        dup_changes = self.remove_duplicate_endpoints(file_path, router_name)
        all_changes.extend(dup_changes)
        return {'file': str(file_path), 'router': router_name, 'changes':
            all_changes}

    def run(self) ->None:
        """Run the API alignment fixes."""
        logger.info('🔧 Starting API Alignment Implementation')
        logger.info('=' * 80)
        results = []
        for router_file in self.api_dir.rglob('*.py'):
            with open(router_file, 'r') as f:
                content = f.read()
            if 'APIRouter' not in content and 'FastAPI' not in content:
                continue
            result = self.fix_router_file(router_file)
            if result['changes']:
                results.append(result)
                logger.info('\n📝 %s:' % result['router'])
                for change in result['changes']:
                    logger.info(change)
        with open('api-alignment-implementation.json', 'w') as f:
            json.dump({'timestamp': '2025-08-26', 'files_modified': len(
                results), 'changes': results}, f, indent=2)
        logger.info('\n' + '=' * 80)
        logger.info('✅ API Alignment Complete!')
        logger.info('   Modified %s router files' % len(results))
        logger.info('   Results saved to api-alignment-implementation.json')
        self.create_verification_script()

    def create_verification_script(self) ->None:
        """Create a script to verify the alignment."""
        verification_script = """#!/usr/bin/env python3
""\"Verify API alignment after fixes.""\"

import re
from pathlib import Path
from collections import defaultdict

issues = defaultdict(list)

# Check all routers
for router_file in Path("api").rglob("*.py"):
    with open(router_file, 'r') as f:
        content = f.read()
    
    if 'APIRouter' not in content:
        continue
    
    router_name = router_file.stem
    
    # Check for non-standard parameters
    params = re.findall(r'\\{([^}]+)\\}', content)
    for param in params:
        if param not in ['id', 'token', 'model', 'stage']:
            issues['non_standard_params'].append(f"{router_name}: {param}")
    
    # Check for missing /api/v1/ prefix
    if 'prefix=' in content:
        prefix_match = re.search(r'prefix=[\\'"`]([^\\'"`]+)[\\'"`]', content)
        if prefix_match:
            prefix = prefix_match.group(1)
            if not prefix.startswith('/api/v1'):
                issues['bad_prefix'].append(f"{router_name}: {prefix}")

# Report issues
if issues:
    logger.info("⚠️  Issues found:")
    for issue_type, items in issues.items():
        logger.info(f"\\n{issue_type}:")
        for item in items:
            logger.info(f"  - {item}")
else:
    logger.info("✅ All API endpoints properly aligned!")
"""
        with open('scripts/verify-api-alignment.py', 'w') as f:
            f.write(verification_script)
        os.chmod('scripts/verify-api-alignment.py', 493)

if __name__ == '__main__':
    fixer = APIAlignmentFixer()
    fixer.run()
