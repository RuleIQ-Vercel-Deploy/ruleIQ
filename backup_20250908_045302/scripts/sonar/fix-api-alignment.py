"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Comprehensive API Alignment Fix Script
Fixes both backend and frontend to use consistent naming
"""

import os
import re
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Any
PROJECT_ROOT = Path(__file__).parent.parent
ROUTERS_DIR = PROJECT_ROOT / 'api' / 'routers'
FRONTEND_API_DIR = PROJECT_ROOT / 'frontend' / 'lib' / 'api'
MAIN_PY = PROJECT_ROOT / 'main.py'


class APIAlignmentFixer:

    def __init__(self):
        self.changes = []
        self.backend_endpoints = {}
        self.frontend_endpoints = {}

    def analyze_backend(self) ->Any:
        """Analyze all backend endpoints"""
        logger.info('🔍 Analyzing Backend Endpoints...')
        with open(MAIN_PY, 'r') as f:
            main_content = f.read()
        router_pattern = (
            'app\\.include_router\\(([^,]+)\\.router,\\s*prefix="([^"]+)"')
        routers = re.findall(router_pattern, main_content)
        for router_name, prefix in routers:
            router_file = ROUTERS_DIR / f'{router_name}.py'
            if router_file.exists():
                endpoints = self.extract_backend_endpoints(router_file, prefix)
                self.backend_endpoints[router_name] = {'prefix': prefix,
                    'endpoints': endpoints}
        return self.backend_endpoints

    def extract_backend_endpoints(self, filepath: Path, prefix: str) ->List[
        Dict]:
        """Extract endpoints from a router file"""
        with open(filepath, 'r') as f:
            content = f.read()
        endpoint_pattern = '@router\\.(get|post|put|patch|delete)\\("([^"]+)"'
        endpoints = re.findall(endpoint_pattern, content)
        result = []
        for method, path in endpoints:
            full_path = f'{prefix}{path}' if not path.startswith('/'
                ) else f'{prefix}{path}'
            result.append({'method': method.upper(), 'path': path,
                'full_path': full_path, 'has_trailing_slash': path.endswith
                ('/'), 'has_underscore': '_' in path and '{' not in path})
        return result

    def analyze_frontend(self) ->Any:
        """Analyze all frontend API calls"""
        logger.info('🔍 Analyzing Frontend API Calls...')
        for service_file in FRONTEND_API_DIR.glob('*.service.ts'):
            endpoints = self.extract_frontend_endpoints(service_file)
            if endpoints:
                self.frontend_endpoints[service_file.stem] = endpoints
        return self.frontend_endpoints

    def extract_frontend_endpoints(self, filepath: Path) ->List[Dict]:
        """Extract API calls from frontend service file"""
        with open(filepath, 'r') as f:
            content = f.read()
        pattern = (
            'apiClient\\.(get|post|put|patch|delete|request|publicGet|publicPost)<[^>]*>\\([\\\'"`]([^\\\'"`]+)[\\\'"`]'
            )
        matches = re.findall(pattern, content)
        result = []
        for method, endpoint in matches:
            actual_endpoint = endpoint if endpoint.startswith('/api'
                ) else f'/api/v1{endpoint}'
            result.append({'method': method.upper(), 'original': endpoint,
                'transformed': actual_endpoint, 'line': self.
                get_line_number(content, endpoint)})
        return result

    def get_line_number(self, content: str, search_str: str) ->int:
        """Get line number of a string in content"""
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if search_str in line:
                return i
        return 0

    def find_mismatches(self) ->Any:
        """Find mismatches between frontend and backend"""
        logger.info('\n🔍 Finding Mismatches...')
        mismatches = {'trailing_slash': [], 'missing_backend': [],
            'missing_frontend': [], 'path_param_mismatch': []}
        all_backend = {}
        for router, data in self.backend_endpoints.items():
            for endpoint in data['endpoints']:
                key = f"{endpoint['method']} {endpoint['full_path']}"
                all_backend[key] = endpoint
        for service, endpoints in self.frontend_endpoints.items():
            for endpoint in endpoints:
                method = endpoint['method']
                path = endpoint['transformed']
                key = f'{method} {path}'
                if key in all_backend:
                    continue
                key_slash = f'{method} {path}/'
                if key_slash in all_backend:
                    mismatches['trailing_slash'].append({'service': service,
                        'frontend': path, 'backend': f'{path}/', 'line':
                        endpoint['line']})
                    continue
                path_base = re.sub('/\\d+', '/{id}', path)
                found = False
                for backend_key, backend_endpoint in all_backend.items():
                    if backend_key.startswith(method) and self.paths_match(path
                        , backend_endpoint['full_path']):
                        mismatches['path_param_mismatch'].append({'service':
                            service, 'frontend': path, 'backend':
                            backend_endpoint['full_path'], 'line': endpoint
                            ['line']})
                        found = True
                        break
                if not found:
                    mismatches['missing_backend'].append({'service':
                        service, 'endpoint': endpoint['original'], 'method':
                        method, 'line': endpoint['line']})
        return mismatches

    def paths_match(self, frontend_path: str, backend_path: str) ->bool:
        """Check if paths match with parameter substitution"""
        frontend_pattern = re.sub('/\\d+', '/[^/]+', frontend_path)
        frontend_pattern = re.sub('/\\$\\{[^}]+\\}', '/[^/]+', frontend_pattern
            )
        backend_pattern = re.sub('/\\{[^}]+\\}', '/[^/]+', backend_path)
        return frontend_pattern == backend_pattern

    def generate_fixes(self, mismatches: Dict) ->Any:
        """Generate fix recommendations"""
        logger.info('\n📝 Generating Fixes...')
        fixes = {'backend_fixes': [], 'frontend_fixes': [],
            'new_endpoints_needed': []}
        for mismatch in mismatches['trailing_slash']:
            fixes['backend_fixes'].append({'type': 'remove_trailing_slash',
                'endpoint': mismatch['backend'], 'fix_to': mismatch[
                'frontend']})
        for missing in mismatches['missing_backend']:
            fixes['new_endpoints_needed'].append({'method': missing[
                'method'], 'endpoint': missing['endpoint'], 'service':
                missing['service']})
        return fixes

    def apply_backend_fixes(self, dry_run: bool=True) ->None:
        """Apply fixes to backend files"""
        logger.info('\n🛠️  Applying Backend Fixes...')
        if dry_run:
            logger.info('   (DRY RUN - No changes will be made)')
        for router_file in ROUTERS_DIR.glob('*.py'):
            with open(router_file, 'r') as f:
                content = f.read()
            original = content
            content = re.sub(
                '(@router\\.(get|post|put|patch|delete)\\("([^"]+)/"\\))',
                '@router.\\2("\\3")', content)
            content = re.sub('\\{session_id\\}', '{id}', content)
            content = re.sub('\\{assessment_id\\}', '{id}', content)
            content = re.sub('\\{profile_id\\}', '{id}', content)
            content = re.sub('\\{policy_id\\}', '{id}', content)
            content = re.sub('\\{evidence_id\\}', '{id}', content)
            if content != original:
                if not dry_run:
                    with open(router_file, 'w') as f:
                        f.write(content)
                logger.info('   ✅ Fixed %s' % router_file.name)

    def generate_report(self, mismatches: Dict, fixes: Dict) ->Any:
        """Generate detailed report"""
        report = {'timestamp': subprocess.check_output(['date', '-Iseconds'
            ]).decode().strip(), 'summary': {'total_frontend_endpoints':
            sum(len(e) for e in self.frontend_endpoints.values()),
            'total_backend_endpoints': sum(len(d['endpoints']) for d in
            self.backend_endpoints.values()), 'trailing_slash_issues': len(
            mismatches['trailing_slash']), 'missing_backend': len(
            mismatches['missing_backend']), 'path_param_mismatches': len(
            mismatches['path_param_mismatch'])}, 'mismatches': mismatches,
            'fixes': fixes}
        with open(PROJECT_ROOT / 'api-alignment-report.json', 'w') as f:
            json.dump(report, f, indent=2)
        return report


def main() ->None:
    """Main execution"""
    logger.info('🚀 RuleIQ API Alignment Fixer')
    logger.info('=' * 80)
    fixer = APIAlignmentFixer()
    backend = fixer.analyze_backend()
    frontend = fixer.analyze_frontend()
    mismatches = fixer.find_mismatches()
    fixes = fixer.generate_fixes(mismatches)
    report = fixer.generate_report(mismatches, fixes)
    logger.info('\n' + '=' * 80)
    logger.info('📊 ANALYSIS SUMMARY\n')
    logger.info('Backend Endpoints: %s' % report['summary'][
        'total_backend_endpoints'])
    logger.info('Frontend API Calls: %s' % report['summary'][
        'total_frontend_endpoints'])
    logger.info('Trailing Slash Issues: %s' % report['summary'][
        'trailing_slash_issues'])
    logger.info('Missing Backend Endpoints: %s' % report['summary'][
        'missing_backend'])
    logger.info('Path Parameter Mismatches: %s' % report['summary'][
        'path_param_mismatches'])
    if mismatches['trailing_slash']:
        logger.info('\n⚠️  Trailing Slash Issues:')
        for item in mismatches['trailing_slash'][:5]:
            logger.info('   - %s: %s → %s' % (item['service'], item[
                'frontend'], item['backend']))
    if mismatches['missing_backend']:
        logger.info('\n❌ Missing Backend Endpoints:')
        for item in mismatches['missing_backend'][:10]:
            print(
                f"   - {item['method']} {item['endpoint']} ({item['service']}.ts:{item['line']})"
                )
    logger.info('\n' + '=' * 80)
    logger.info('\n📝 RECOMMENDED ACTIONS:\n')
    logger.info('1. Fix trailing slashes in backend (quick win)')
    logger.info('2. Standardize parameter names to use {id}')
    logger.info('3. Implement missing backend endpoints')
    logger.info('4. Update frontend services to match backend patterns')
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--fix':
        logger.info('\n🛠️  Applying fixes...')
        fixer.apply_backend_fixes(dry_run=False)
        logger.info('\n✅ Backend fixes applied!')
        logger.info('\n⚠️  Remember to:')
        logger.info('1. Test all endpoints')
        logger.info('2. Update frontend services')
        logger.info('3. Run integration tests')
    else:
        logger.info(
            '\n💡 Run with --fix flag to apply backend fixes automatically')
        logger.info('   python scripts/fix-api-alignment.py --fix')
    logger.info('\n📄 Detailed report saved to api-alignment-report.json')


if __name__ == '__main__':
    main()
