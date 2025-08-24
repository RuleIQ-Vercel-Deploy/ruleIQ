#!/usr/bin/env python3
"""
Clean up duplicate and unused API endpoints
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set

PROJECT_ROOT = Path(__file__).parent.parent
ROUTERS_DIR = PROJECT_ROOT / "api" / "routers"
MAIN_PY = PROJECT_ROOT / "main.py"

class DuplicateCleaner:
    def __init__(self):
        self.changes = []
        
    def load_duplicate_report(self):
        """Load the duplicate analysis report"""
        report_file = PROJECT_ROOT / "duplicate-analysis-report.json"
        if report_file.exists():
            with open(report_file, 'r') as f:
                return json.load(f)
        return None
    
    def consolidate_semantic_duplicates(self, dry_run=True):
        """Consolidate semantic duplicates"""
        print("🔧 Consolidating Semantic Duplicates...")
        
        consolidation_plan = {
            # Auth consolidation - keep /api/v1/auth/me, remove /api/v1/users/me
            'getcurrentuser': {
                'keep': 'GET /api/v1/auth/me',
                'remove': ['GET /api/v1/users/me'],
                'reason': 'Auth endpoint is the canonical source for current user'
            },
            # Circuit breaker consolidation - keep main namespace, remove duplicates
            'getcircuitbreakerstatus': {
                'keep': 'GET /api/v1/ai/optimization/circuit-breaker/status',
                'remove': [
                    'GET /api/v1/ai-assessments/circuit-breaker/status',
                    'GET /api/ai/assessments/circuit-breaker/status'
                ],
                'reason': 'Centralize circuit breaker in optimization namespace'
            },
            'resetcircuitbreaker': {
                'keep': 'POST /api/v1/ai/optimization/circuit-breaker/reset',
                'remove': [
                    'POST /api/v1/ai-assessments/circuit-breaker/reset',
                    'POST /api/ai/assessments/circuit-breaker/reset'
                ],
                'reason': 'Centralize circuit breaker in optimization namespace'
            },
            # Cache metrics consolidation
            'getaicachemetrics': {
                'keep': 'GET /api/v1/ai/optimization/cache/metrics',
                'remove': [
                    'GET /api/v1/ai-assessments/cache/metrics',
                    'GET /api/ai/assessments/cache/metrics',
                    'GET /api/v1/chat/cache/metrics'
                ],
                'reason': 'Centralize cache metrics in optimization namespace'
            },
            # Quality trends consolidation
            'getqualitytrends': {
                'keep': 'GET /api/v1/evidence/quality/trends',
                'remove': ['GET /api/v1/chat/quality/trends'],
                'reason': 'Evidence is the source of truth for quality metrics'
            }
        }
        
        for pattern, plan in consolidation_plan.items():
            print(f"\n  Pattern: {pattern}")
            print(f"    Keep: {plan['keep']}")
            print(f"    Remove: {', '.join(plan['remove'])}")
            print(f"    Reason: {plan['reason']}")
            
            if not dry_run:
                for endpoint in plan['remove']:
                    self.remove_endpoint(endpoint)
        
        return consolidation_plan
    
    def remove_endpoint(self, endpoint: str):
        """Remove an endpoint from router files"""
        method, path = endpoint.split(' ', 1)
        method = method.lower()
        
        # Extract the base path without prefix
        path_parts = path.split('/')
        if 'api' in path_parts[1]:
            # Remove /api/v1/ or /api/admin/ etc
            base_path = '/' + '/'.join(path_parts[3:]) if len(path_parts) > 3 else '/'
        else:
            base_path = path
        
        # Find the router file
        for router_file in ROUTERS_DIR.glob("*.py"):
            with open(router_file, 'r') as f:
                content = f.read()
            
            # Pattern to find and remove the endpoint
            pattern = rf'@router\.{method}\("{re.escape(base_path)}".*?\)[\s\S]*?(?=@router\.|$)'
            
            if re.search(pattern, content):
                # Comment out instead of removing for safety
                replacement = lambda m: f"# REMOVED: Duplicate endpoint\n# {m.group(0)}"
                new_content = re.sub(pattern, replacement, content)
                
                with open(router_file, 'w') as f:
                    f.write(new_content)
                
                self.changes.append(f"Removed {endpoint} from {router_file.name}")
                return True
        
        return False
    
    def clean_namespace_duplicates(self, dry_run=True):
        """Clean up namespace duplicates by removing deprecated namespaces"""
        print("\n🔧 Cleaning Namespace Duplicates...")
        
        # Define deprecated namespaces to remove
        deprecated_namespaces = [
            '/api/ai/assessments/',  # Old AI namespace
            '/api/v1/ai-assessments/',  # Hyphenated version
        ]
        
        for namespace in deprecated_namespaces:
            print(f"\n  Removing deprecated namespace: {namespace}")
            
            if not dry_run:
                # Find and comment out routers with deprecated namespaces
                self.remove_namespace_routes(namespace)
        
        return deprecated_namespaces
    
    def remove_namespace_routes(self, namespace: str):
        """Remove or comment out routes in a deprecated namespace"""
        # Update main.py to comment out deprecated router inclusions
        with open(MAIN_PY, 'r') as f:
            content = f.read()
        
        # Pattern to find router inclusions with this namespace
        pattern = rf'(app\.include_router\([^)]*prefix="{re.escape(namespace[:-1])}"[^)]*\))'
        
        if re.search(pattern, content):
            # Comment out the line
            new_content = re.sub(pattern, r'# DEPRECATED: \1', content)
            
            with open(MAIN_PY, 'w') as f:
                f.write(new_content)
            
            self.changes.append(f"Commented out namespace {namespace} in main.py")
    
    def identify_safe_removals(self):
        """Identify endpoints that are safe to remove"""
        report = self.load_duplicate_report()
        if not report:
            return []
        
        safe_to_remove = []
        
        # Test utilities can be removed in production
        test_endpoints = [
            'DELETE /api/test-utils/cleanup-test-users',
            'GET /api/test-utils/health'
        ]
        
        # Old deprecated endpoints
        deprecated_endpoints = [
            'GET /api/ai/assessments/cache/metrics',
            'GET /api/ai/assessments/circuit-breaker/status',
            'POST /api/ai/assessments/circuit-breaker/reset',
            'GET /api/v1/ai-assessments/cache/metrics',
            'GET /api/v1/ai-assessments/circuit-breaker/status',
            'POST /api/v1/ai-assessments/circuit-breaker/reset'
        ]
        
        safe_to_remove.extend(test_endpoints)
        safe_to_remove.extend(deprecated_endpoints)
        
        return safe_to_remove
    
    def generate_cleanup_plan(self):
        """Generate a comprehensive cleanup plan"""
        print("\n" + "=" * 80)
        print("🧹 API CLEANUP PLAN")
        print("=" * 80)
        
        report = self.load_duplicate_report()
        if not report:
            print("❌ No duplicate analysis report found. Run analyze-duplicates.py first.")
            return
        
        # 1. Semantic duplicates to consolidate
        semantic_plan = self.consolidate_semantic_duplicates(dry_run=True)
        
        # 2. Namespace duplicates to clean
        namespace_plan = self.clean_namespace_duplicates(dry_run=True)
        
        # 3. Safe removals
        safe_removals = self.identify_safe_removals()
        
        print("\n🗑️  SAFE TO REMOVE:")
        for endpoint in safe_removals[:10]:
            print(f"    - {endpoint}")
        if len(safe_removals) > 10:
            print(f"    ... and {len(safe_removals) - 10} more")
        
        # Summary
        print("\n" + "=" * 80)
        print("📊 CLEANUP SUMMARY:")
        print(f"  Semantic duplicates to consolidate: {len(semantic_plan)}")
        print(f"  Deprecated namespaces to remove: {len(namespace_plan)}")
        print(f"  Safe endpoints to remove: {len(safe_removals)}")
        
        total_reduction = len(semantic_plan) * 2 + len(safe_removals)
        print(f"\n  Total endpoint reduction: ~{total_reduction} endpoints")
        print(f"  From: 166 endpoints")
        print(f"  To: ~{166 - total_reduction} endpoints")
        
        return {
            'semantic_consolidation': semantic_plan,
            'namespace_cleanup': namespace_plan,
            'safe_removals': safe_removals
        }
    
    def execute_cleanup(self, cautious=True):
        """Execute the cleanup plan"""
        print("\n🚀 EXECUTING CLEANUP...")
        
        if cautious:
            print("  (Running in cautious mode - only safe changes)")
            
            # 1. Consolidate semantic duplicates
            print("\n1. Consolidating semantic duplicates...")
            self.consolidate_semantic_duplicates(dry_run=False)
            
            # 2. Don't remove namespaces yet - needs more testing
            print("\n2. Skipping namespace removal (needs testing)")
            
            print("\n✅ Cautious cleanup complete!")
        else:
            print("  (Running in full mode - all changes)")
            # Full cleanup including namespace removal
            self.consolidate_semantic_duplicates(dry_run=False)
            self.clean_namespace_duplicates(dry_run=False)
            
            print("\n✅ Full cleanup complete!")
        
        if self.changes:
            print("\n📝 Changes made:")
            for change in self.changes[:20]:
                print(f"    - {change}")
            if len(self.changes) > 20:
                print(f"    ... and {len(self.changes) - 20} more")
        
        return self.changes

def main():
    import sys
    
    cleaner = DuplicateCleaner()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--execute':
        # Execute cleanup
        cautious = '--full' not in sys.argv
        changes = cleaner.execute_cleanup(cautious=cautious)
        
        print(f"\n💾 Total changes: {len(changes)}")
        print("\n⚠️  Remember to:")
        print("  1. Review all changes with git diff")
        print("  2. Test all affected endpoints")
        print("  3. Update frontend if needed")
        print("  4. Run integration tests")
    else:
        # Just show the plan
        plan = cleaner.generate_cleanup_plan()
        
        print("\n💡 To execute cleanup:")
        print("  Cautious mode (recommended): python scripts/cleanup-duplicates.py --execute")
        print("  Full mode: python scripts/cleanup-duplicates.py --execute --full")
        
        # Save plan to file
        with open(PROJECT_ROOT / "cleanup-plan.json", 'w') as f:
            json.dump(plan, f, indent=2, default=str)
        
        print("\n📄 Cleanup plan saved to cleanup-plan.json")

if __name__ == "__main__":
    main()