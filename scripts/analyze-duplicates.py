"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Analyze and identify duplicate API endpoints in the ruleIQ codebase
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict
PROJECT_ROOT = Path(__file__).parent.parent
ROUTERS_DIR = PROJECT_ROOT / 'api' / 'routers'
MAIN_PY = PROJECT_ROOT / 'main.py'

class DuplicateAnalyzer:

    def __init__(self):
        self.endpoints = defaultdict(list)
        self.functionality_map = defaultdict(list)

    def analyze_routers(self) ->Any:
        """Analyze all router files for endpoints"""
        logger.info('🔍 Analyzing Router Files...\n')
        with open(MAIN_PY, 'r') as f:
            main_content = f.read()
        router_pattern = (
            'app\\.include_router\\(([^,]+)\\.router,\\s*prefix="([^"]+)"')
        routers = re.findall(router_pattern, main_content)
        for router_name, prefix in routers:
            router_file = ROUTERS_DIR / f'{router_name}.py'
            if router_file.exists():
                self.extract_endpoints(router_file, prefix, router_name)
        return self.endpoints

    def extract_endpoints(self, filepath: Path, prefix: str, router_name: str
        ) ->None:
        """Extract endpoints from a router file"""
        with open(filepath, 'r') as f:
            content = f.read()
        endpoint_pattern = (
            '@router\\.(get|post|put|patch|delete)\\("([^"]+)".*?\\)\\s*(?:async\\s+)?def\\s+(\\w+)',
            )
        matches = re.findall(endpoint_pattern, content, re.DOTALL)
        for method, path, function_name in matches:
            full_path = f'{prefix}{path}' if not path.startswith('/'
                ) else f'{prefix}{path}'
            endpoint_key = f'{method.upper()} {full_path}'
            self.endpoints[endpoint_key].append({'router': router_name,
                'function': function_name, 'file': filepath.name, 'prefix':
                prefix, 'path': path})
            self.functionality_map[function_name].append({'endpoint':
                endpoint_key, 'router': router_name})

    def find_duplicates(self) ->Any:
        """Find different types of duplicates"""
        duplicates = {'exact_duplicates': [], 'semantic_duplicates': [],
            'namespace_duplicates': [], 'unused_endpoints': []}
        for endpoint, locations in self.endpoints.items():
            if len(locations) > 1:
                duplicates['exact_duplicates'].append({'endpoint': endpoint,
                    'locations': locations})
        self.find_semantic_duplicates(duplicates)
        self.find_namespace_duplicates(duplicates)
        return duplicates

    def find_semantic_duplicates(self, duplicates) ->None:
        """Find endpoints that appear to do the same thing"""
        function_groups = defaultdict(list)
        for func_name, endpoints in self.functionality_map.items():
            normalized = func_name.lower().replace('_', '')
            function_groups[normalized].extend(endpoints)
        for normalized, endpoints in function_groups.items():
            if len(endpoints) > 1:
                routers = set(e['router'] for e in endpoints)
                if len(routers) > 1:
                    duplicates['semantic_duplicates'].append({
                        'function_pattern': normalized, 'endpoints': endpoints},
                        )

    def find_namespace_duplicates(self, duplicates) ->None:
        """Find same resources exposed through different API namespaces"""
        namespace_patterns = {'/api/v1/': [], '/api/admin/': [], '/api/ai/':
            [], '/api/freemium/': []}
        for endpoint, locations in self.endpoints.items():
            for namespace in namespace_patterns:
                if namespace in endpoint:
                    resource = endpoint.split(namespace)[1].split(' ')[0
                        ] if namespace in endpoint else ''
                    namespace_patterns[namespace].append({'endpoint':
                        endpoint, 'resource': resource, 'locations': locations},
                        )
        resource_map = defaultdict(list)
        for namespace, endpoints in namespace_patterns.items():
            for ep in endpoints:
                if ep['resource']:
                    resource_map[ep['resource']].append({'namespace':
                        namespace, 'endpoint': ep['endpoint']})
        for resource, occurrences in resource_map.items():
            if len(occurrences) > 1:
                duplicates['namespace_duplicates'].append({'resource':
                    resource, 'occurrences': occurrences})

    def analyze_usage(self) ->List[Any]:
        """Analyze which endpoints are actually used by frontend"""
        report_file = PROJECT_ROOT / 'api-alignment-report.json'
        if report_file.exists():
            with open(report_file, 'r') as f:
                report = json.load(f)
            all_backend = set()
            for endpoint in self.endpoints.keys():
                all_backend.add(endpoint)
            frontend_calls = set()
            if 'mismatches' in report:
                for category in report['mismatches'].values():
                    if isinstance(category, list):
                        for item in category:
                            if 'endpoint' in item:
                                frontend_calls.add(item.get('method', 'GET'
                                    ) + ' ' + item['endpoint'])
            unused = all_backend - frontend_calls
            return list(unused)
        return []

    def generate_report(self, duplicates) ->Dict[str, Any]:
        """Generate a detailed report"""
        logger.info('=' * 80)
        logger.info('📊 DUPLICATE ENDPOINT ANALYSIS REPORT')
        logger.info('=' * 80)
        if duplicates['exact_duplicates']:
            logger.info(
                '\n❌ EXACT DUPLICATES (Same endpoint registered multiple times):',
                )
            for dup in duplicates['exact_duplicates']:
                logger.info('\n  %s:' % dup['endpoint'])
                for loc in dup['locations']:
                    logger.info('    - %s -> %s()' % (loc['file'], loc[
                        'function']))
        else:
            logger.info('\n✅ No exact duplicates found')
        if duplicates['semantic_duplicates']:
            print(
                '\n⚠️  SEMANTIC DUPLICATES (Similar functionality in different routers):',
                )
            for dup in duplicates['semantic_duplicates']:
                logger.info('\n  Pattern: %s' % dup['function_pattern'])
                for ep in dup['endpoints']:
                    logger.info('    - %s (%s.py)' % (ep['endpoint'], ep[
                        'router']))
        else:
            logger.info('\n✅ No semantic duplicates found')
        if duplicates['namespace_duplicates']:
            logger.info(
                '\n🔄 NAMESPACE DUPLICATES (Same resource in multiple namespaces):',
                )
            for dup in duplicates['namespace_duplicates']:
                logger.info('\n  Resource: %s' % dup['resource'])
                for occ in dup['occurrences']:
                    logger.info('    - %s' % occ['endpoint'])
        else:
            logger.info('\n✅ No namespace duplicates found')
        unused = self.analyze_usage()
        if unused:
            logger.info('\n🗑️  POTENTIALLY UNUSED ENDPOINTS (%s total):' %
                len(unused))
            for endpoint in sorted(unused)[:20]:
                logger.info('    - %s' % endpoint)
            if len(unused) > 20:
                logger.info('    ... and %s more' % (len(unused) - 20))
        logger.info('\n' + '=' * 80)
        logger.info('📈 SUMMARY:')
        logger.info('  Total endpoints analyzed: %s' % len(self.endpoints))
        logger.info('  Exact duplicates: %s' % len(duplicates[
            'exact_duplicates']))
        logger.info('  Semantic duplicates: %s' % len(duplicates[
            'semantic_duplicates']))
        logger.info('  Namespace duplicates: %s' % len(duplicates[
            'namespace_duplicates']))
        logger.info('  Potentially unused: %s' % len(unused))
        logger.info('\n💡 RECOMMENDATIONS:')
        logger.info('  1. Remove exact duplicates immediately')
        logger.info('  2. Consolidate semantic duplicates where possible')
        logger.info('  3. Review namespace duplicates for consistency')
        logger.info('  4. Verify and remove unused endpoints')
        logger.info(
            '  5. Consider API versioning strategy for namespace organization')
        return {'total_endpoints': len(self.endpoints), 'duplicates':
            duplicates, 'unused_count': len(unused)}

def main() ->None:
    analyzer = DuplicateAnalyzer()
    endpoints = analyzer.analyze_routers()
    duplicates = analyzer.find_duplicates()
    report = analyzer.generate_report(duplicates)
    with open(PROJECT_ROOT / 'duplicate-analysis-report.json', 'w') as f:
        json.dump({'endpoints': {k: v for k, v in endpoints.items()},
            'duplicates': duplicates, 'summary': report}, f, indent=2)
    logger.info('\n📄 Detailed report saved to duplicate-analysis-report.json')

if __name__ == '__main__':
    main()
