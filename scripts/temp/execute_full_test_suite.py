#!/usr/bin/env python3
"""
Execute RuleIQ full test suite with proper setup.
P0 Task: Fix Test Infrastructure (799f27b3)
"""

import subprocess
import sys
import time
import re
from pathlib import Path
from collections import defaultdict
from datetime import datetime

class TestSuiteRunner:
    """Manage test suite execution."""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.test_results = {}
        
    def run_command(self, cmd, timeout=300, check=False):
        """Execute shell command."""
        print(f"  → {cmd[:100]}...")
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                check=check
            )
            return result.stdout, result.stderr, result.returncode
        except subprocess.TimeoutExpired:
            print(f"  ⏱️ Command timed out after {timeout}s")
            return "", "Timeout", -1
        except subprocess.CalledProcessError as e:
            return e.stdout or "", e.stderr or "", e.returncode
    
    def setup_environment(self):
        """Setup test environment."""
        print("\n" + "="*70)
        print("🔧 ENVIRONMENT SETUP")
        print("="*70)
        
        # 1. Install missing dependencies
        print("\n📦 Installing dependencies...")
        
        # Missing deps
        if Path("requirements-missing.txt").exists():
            stdout, stderr, code = self.run_command(
                ".venv/bin/pip install -r requirements-missing.txt"
            )
            if code == 0:
                print("  ✅ Missing dependencies installed")
            else:
                print(f"  ⚠️ Some dependencies failed to install")
        
        # Main requirements
        stdout, stderr, code = self.run_command(
            ".venv/bin/pip install -q --upgrade -r requirements.txt",
            timeout=120
        )
        if code == 0:
            print("  ✅ Main requirements up to date")
        
        # 2. Setup Docker containers
        print("\n🐳 Setting up Docker containers...")
        
        containers = [
            {
                'name': 'ruleiq-test-postgres',
                'image': 'postgres:15-alpine',
                'port': '5433:5432',
                'env': [
                    'POSTGRES_DB=test_ruleiq',
                    'POSTGRES_USER=test_user', 
                    'POSTGRES_PASSWORD=test_password'
                ]
            },
            {
                'name': 'ruleiq-test-redis',
                'image': 'redis:7-alpine',
                'port': '6380:6379',
                'env': []
            }
        ]
        
        for container in containers:
            # Check if running
            stdout, _, _ = self.run_command(
                f"docker ps --filter name={container['name']} --format '{{{{.Names}}}}'"
            )
            
            if container['name'] in stdout:
                print(f"  ✅ {container['name']} already running")
            else:
                # Try to start existing
                stdout, stderr, code = self.run_command(
                    f"docker start {container['name']}"
                )
                
                if code != 0:
                    # Create new container
                    env_str = ' '.join([f'-e {e}' for e in container['env']])
                    cmd = f"docker run -d --name {container['name']} {env_str} -p {container['port']} {container['image']}"
                    stdout, stderr, code = self.run_command(cmd)
                    
                    if code == 0:
                        print(f"  ✅ Created and started {container['name']}")
                    else:
                        print(f"  ❌ Failed to start {container['name']}")
                else:
                    print(f"  ✅ Started {container['name']}")
        
        # Wait for containers
        print("\n⏳ Waiting for services to be ready...")
        time.sleep(3)
        
        # 3. Fix imports
        print("\n🔧 Fixing test imports...")
        if Path("fix_test_imports.py").exists():
            stdout, stderr, code = self.run_command(
                ".venv/bin/python fix_test_imports.py",
                timeout=60
            )
            if code == 0:
                print("  ✅ Import fixes applied")
        
        return True
    
    def collect_tests(self):
        """Collect and analyze tests."""
        print("\n" + "="*70)
        print("📊 TEST COLLECTION")
        print("="*70)
        
        stdout, stderr, code = self.run_command(
            ".venv/bin/python -m pytest --collect-only -q",
            timeout=30
        )
        
        # Parse results
        test_count = 0
        error_count = 0
        test_files = set()
        
        for line in stdout.split('\n'):
            if 'collected' in line:
                match = re.search(r'collected (\d+)', line)
                if match:
                    test_count = int(match.group(1))
            
            if '<Module' in line:
                match = re.search(r'<Module ([^>]+)>', line)
                if match:
                    test_files.add(match.group(1))
        
        # Count errors
        error_count = stderr.count('ERROR') + stderr.count('ImportError')
        
        print(f"\n📈 Collection Summary:")
        print(f"  • Tests collected: {test_count}/2610")
        print(f"  • Test files: {len(test_files)}")
        print(f"  • Collection errors: {error_count}")
        
        self.test_results['collected'] = test_count
        self.test_results['errors'] = error_count
        
        return test_count, error_count
    
    def run_tests(self):
        """Run the full test suite."""
        print("\n" + "="*70)
        print("🧪 RUNNING TEST SUITE")
        print("="*70)
        
        print("\nThis will take several minutes...")
        
        # Run with appropriate options
        stdout, stderr, code = self.run_command(
            ".venv/bin/python -m pytest -v --tb=short --no-header -q",
            timeout=600  # 10 minutes max
        )
        
        # Parse results
        results = {
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'errors': 0,
            'xfailed': 0,
            'xpassed': 0
        }
        
        # Find summary line
        for line in stdout.split('\n'):
            if 'passed' in line or 'failed' in line:
                # Extract all counts
                for key in results.keys():
                    match = re.search(rf'(\d+) {key}', line)
                    if match:
                        results[key] = int(match.group(1))
        
        # Store results
        self.test_results.update(results)
        
        # Calculate totals
        total_run = sum(results.values())
        if total_run == 0:
            # Fallback counting
            total_run = stdout.count('PASSED') + stdout.count('FAILED') + stdout.count('ERROR')
            results['passed'] = stdout.count('PASSED')
            results['failed'] = stdout.count('FAILED') 
            results['errors'] = stdout.count('ERROR')
        
        return results, stdout, stderr
    
    def analyze_failures(self, stdout, stderr):
        """Analyze test failures."""
        print("\n" + "="*70)
        print("🔍 FAILURE ANALYSIS")
        print("="*70)
        
        failures = defaultdict(list)
        
        # Parse failure types
        for line in (stdout + stderr).split('\n'):
            if 'FAILED' in line or 'ERROR' in line:
                test_name = ""
                error_type = "Unknown"
                
                if '::' in line:
                    parts = line.split('::')
                    test_file = parts[0].split()[-1] if parts[0] else ""
                    test_name = '::'.join(parts[1:]).split('-')[0].strip() if len(parts) > 1 else ""
                    
                    # Determine error type
                    if 'AssertionError' in line:
                        error_type = "Assertion"
                    elif 'fixture' in line.lower():
                        error_type = "Fixture"
                    elif 'ImportError' in line:
                        error_type = "Import"
                    elif 'AttributeError' in line:
                        error_type = "Attribute"
                    elif 'connection' in line.lower():
                        error_type = "Connection"
                    elif 'TypeError' in line:
                        error_type = "Type"
                    
                    if test_name:
                        failures[error_type].append(f"{test_file}::{test_name}")
        
        # Print categorized failures
        if failures:
            print("\n📋 Failure Categories:")
            for error_type, tests in sorted(failures.items(), key=lambda x: -len(x[1])):
                print(f"\n  {error_type} Errors ({len(tests)} tests):")
                for test in tests[:3]:  # Show first 3
                    print(f"    • {test}")
                if len(tests) > 3:
                    print(f"    ... and {len(tests)-3} more")
        
        return failures
    
    def generate_report(self):
        """Generate final report."""
        print("\n" + "="*70)
        print("📊 FINAL REPORT")
        print("="*70)
        
        # Time taken
        duration = (datetime.now() - self.start_time).total_seconds()
        
        # Results summary
        collected = self.test_results.get('collected', 0)
        passed = self.test_results.get('passed', 0)
        failed = self.test_results.get('failed', 0)
        errors = self.test_results.get('errors', 0)
        skipped = self.test_results.get('skipped', 0)
        
        total = passed + failed + errors + skipped
        
        print(f"\n🕐 Duration: {duration:.1f} seconds")
        print(f"\n📈 Test Results:")
        print(f"  • Collected:    {collected}/2610 tests")
        print(f"  • Executed:     {total} tests")
        print(f"  • ✅ Passed:    {passed} ({passed*100/total if total else 0:.1f}%)")
        print(f"  • ❌ Failed:    {failed}")
        print(f"  • 💥 Errors:    {errors}")
        print(f"  • ⏭️ Skipped:   {skipped}")
        
        # Pass rate
        if total > 0:
            pass_rate = passed * 100 / total
            print(f"\n🎯 Pass Rate: {pass_rate:.1f}%")
            
            if pass_rate >= 95:
                print("  ✅ EXCELLENT - Target achieved!")
            elif pass_rate >= 80:
                print("  🟡 GOOD - Minor fixes needed")
            elif pass_rate >= 60:
                print("  🟠 FAIR - Significant work required")
            else:
                print("  🔴 CRITICAL - Major issues to resolve")
        
        # Critical issues
        print(f"\n⚠️ Critical Issues:")
        
        issues = []
        if collected < 2600:
            issues.append(f"Only {collected}/2610 tests can be collected (fix imports)")
        if errors > 10:
            issues.append(f"{errors} test collection errors (fix fixtures)")
        if failed > 100:
            issues.append(f"{failed} test failures (needs immediate attention)")
        
        if issues:
            for issue in issues:
                print(f"  • {issue}")
        else:
            print("  ✅ No critical issues!")
        
        # Next steps
        print(f"\n🔧 Next Steps:")
        
        if collected < 2600:
            print("  1. Fix remaining import errors")
            print("     Run: .venv/bin/python fix_test_imports.py")
        
        if errors > 0:
            print("  2. Fix test collection errors")
            print("     Run: .venv/bin/pytest --collect-only 2>&1 | grep ERROR")
        
        if failed > 0:
            print("  3. Fix failing tests by category")
            print("     Run: .venv/bin/pytest -k 'test_name' -vv")
        
        if passed == total and total >= 2600:
            print("  ✅ All tests passing! Ready for deployment.")
        
        return pass_rate if total > 0 else 0
    
    def run(self):
        """Main execution flow."""
        print("="*70)
        print("🚀 RuleIQ FULL TEST SUITE EXECUTION")
        print("="*70)
        print(f"Started at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Setup
            if not self.setup_environment():
                print("\n❌ Environment setup failed")
                return False
            
            # Collect
            test_count, error_count = self.collect_tests()
            
            if test_count == 0:
                print("\n❌ No tests could be collected")
                return False
            
            # Run tests
            results, stdout, stderr = self.run_tests()
            
            # Analyze failures
            if results['failed'] > 0 or results['errors'] > 0:
                self.analyze_failures(stdout, stderr)
            
            # Generate report
            pass_rate = self.generate_report()
            
            # Save detailed logs
            with open("test_execution_full.log", "w") as f:
                f.write(f"Test Execution Log - {datetime.now()}\n")
                f.write("="*70 + "\n\n")
                f.write("STDOUT:\n")
                f.write(stdout)
                f.write("\n\nSTDERR:\n")
                f.write(stderr)
            
            print(f"\n📝 Detailed logs saved to: test_execution_full.log")
            
            # Return success if pass rate > 95%
            return pass_rate >= 95
            
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            end_time = datetime.now()
            total_time = (end_time - self.start_time).total_seconds()
            print(f"\n⏱️ Total execution time: {total_time:.1f} seconds")
            print("="*70)

def main():
    """Entry point."""
    runner = TestSuiteRunner()
    success = runner.run()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()