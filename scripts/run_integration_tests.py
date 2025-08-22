#!/usr/bin/env python3
"""
Integration Test Execution Script for ruleIQ

Comprehensive script to run integration tests with different configurations:
- API workflow integration tests
- External service integration tests  
- Contract validation tests
- Performance integration tests
- Security integration tests

Usage:
    python scripts/run_integration_tests.py --suite all
    python scripts/run_integration_tests.py --suite api-workflows
    python scripts/run_integration_tests.py --suite external-services
    python scripts/run_integration_tests.py --suite contracts
    python scripts/run_integration_tests.py --suite performance
"""

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pytest


class IntegrationTestRunner:
    """Manages execution of integration test suites"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_results = {}
        self.start_time = None
        self.end_time = None

    def setup_environment(self) -> bool:
        """Setup test environment and validate dependencies"""
        print("🔧 Setting up integration test environment...")
        
        # Check if we're in the virtual environment
        if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("❌ Virtual environment not activated")
            print("Please run: source .venv/bin/activate")
            return False
        
        # Check required environment variables
        required_env_vars = [
            'DATABASE_URL',
            'JWT_SECRET_KEY',
        ]
        
        missing_vars = []
        for var in required_env_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
            return False
        
        # Check if test database is accessible
        try:
            from database.db_setup import init_db
            print("✅ Database connection validated")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
        
        print("✅ Environment setup completed")
        return True

    async def run_test_suite(self, suite_name: str, 
                           additional_args: List[str] = None) -> Tuple[bool, Dict]:
        """Run a specific test suite"""
        
        if additional_args is None:
            additional_args = []
        
        suite_configs = {
            "api-workflows": {
                "description": "API Workflow Integration Tests",
                "test_files": ["tests/integration/test_comprehensive_api_workflows.py"],
                "markers": ["integration", "api"],
                "timeout": 300,
                "parallelism": 2
            },
            "external-services": {
                "description": "External Service Integration Tests", 
                "test_files": ["tests/integration/test_external_service_integration.py"],
                "markers": ["integration", "external"],
                "timeout": 600,
                "parallelism": 1  # Sequential for external services
            },
            "contracts": {
                "description": "API Contract Validation Tests",
                "test_files": ["tests/integration/test_contract_validation.py"],
                "markers": ["contract", "integration"],
                "timeout": 180,
                "parallelism": 4
            },
            "database": {
                "description": "Database Integration Tests",
                "test_files": ["tests/integration/database/"],
                "markers": ["integration", "database"],
                "timeout": 240,
                "parallelism": 2
            },
            "security": {
                "description": "Security Integration Tests",
                "test_files": ["tests/integration/security/", "tests/security/"],
                "markers": ["integration", "security"],
                "timeout": 300,
                "parallelism": 2
            },
            "performance": {
                "description": "Performance Integration Tests",
                "test_files": ["tests/integration/", "tests/performance/"],
                "markers": ["integration", "performance"],
                "timeout": 900,
                "parallelism": 1  # Sequential for performance tests
            },
            "ai-services": {
                "description": "AI Service Integration Tests",
                "test_files": ["tests/integration/", "tests/ai/"],
                "markers": ["integration", "ai"],
                "timeout": 450,
                "parallelism": 2
            },
            "e2e": {
                "description": "End-to-End Integration Tests",
                "test_files": ["tests/e2e/", "tests/integration/"],
                "markers": ["e2e", "integration"],
                "timeout": 600,
                "parallelism": 1
            }
        }
        
        if suite_name not in suite_configs:
            print(f"❌ Unknown test suite: {suite_name}")
            print(f"Available suites: {', '.join(suite_configs.keys())}")
            return False, {}
        
        config = suite_configs[suite_name]
        print(f"\n🚀 Running {config['description']}")
        print(f"Timeout: {config['timeout']}s | Parallelism: {config['parallelism']}")
        
        # Build pytest command
        cmd = ["python", "-m", "pytest"]
        
        # Add test files/directories
        for test_path in config["test_files"]:
            if os.path.exists(test_path):
                cmd.append(test_path)
        
        # Add markers
        if config["markers"]:
            marker_expr = " and ".join(config["markers"])
            cmd.extend(["-m", marker_expr])
        
        # Add parallelism
        if config["parallelism"] > 1:
            cmd.extend(["-n", str(config["parallelism"]), "--dist", "worksteal"])
        
        # Add common options
        cmd.extend([
            "--tb=short",
            "--maxfail=5",
            "--timeout", str(config["timeout"]),
            "--verbose",
            "--durations=10",
            "--disable-warnings"
        ])
        
        # Add additional arguments
        cmd.extend(additional_args)
        
        # Run tests
        start_time = time.time()
        print(f"Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root, 
                                  capture_output=True, text=True, timeout=config['timeout'] + 60)
            
            end_time = time.time()
            duration = end_time - start_time
            
            success = result.returncode == 0
            
            test_results = {
                "suite": suite_name,
                "success": success,
                "duration": duration,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd)
            }
            
            if success:
                print(f"✅ {config['description']} completed successfully in {duration:.1f}s")
            else:
                print(f"❌ {config['description']} failed in {duration:.1f}s")
                print(f"Return code: {result.returncode}")
                if result.stderr:
                    print("STDERR:")
                    print(result.stderr[-1000:])  # Last 1000 chars
            
            return success, test_results
            
        except subprocess.TimeoutExpired:
            print(f"⏰ {config['description']} timed out after {config['timeout'] + 60}s")
            return False, {
                "suite": suite_name,
                "success": False,
                "duration": config['timeout'] + 60,
                "error": "timeout",
                "timeout": True
            }
        except Exception as e:
            print(f"❌ Error running {config['description']}: {e}")
            return False, {
                "suite": suite_name, 
                "success": False,
                "error": str(e)
            }

    async def run_all_suites(self, selected_suites: List[str] = None,
                           additional_args: List[str] = None) -> Dict:
        """Run all integration test suites"""
        
        if selected_suites is None:
            selected_suites = [
                "api-workflows",
                "contracts", 
                "database",
                "external-services",
                "ai-services",
                "security",
                "performance"
            ]
        
        print(f"🎯 Running {len(selected_suites)} integration test suites")
        
        self.start_time = time.time()
        results = {}
        
        for suite in selected_suites:
            success, suite_results = await self.run_test_suite(suite, additional_args)
            results[suite] = suite_results
            
            if not success and "--continue-on-failure" not in (additional_args or []):
                print(f"❌ Suite {suite} failed, stopping execution")
                break
        
        self.end_time = time.time()
        
        return results

    def generate_report(self, results: Dict) -> str:
        """Generate comprehensive test report"""
        
        report_lines = []
        report_lines.append("# Integration Test Execution Report")
        report_lines.append(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.start_time and self.end_time:
            total_duration = self.end_time - self.start_time
            report_lines.append(f"**Total Duration**: {total_duration:.1f}s")
        
        report_lines.append("")
        
        # Summary
        total_suites = len(results)
        successful_suites = sum(1 for r in results.values() if r.get("success", False))
        failed_suites = total_suites - successful_suites
        
        report_lines.append("## Summary")
        report_lines.append(f"- **Total Suites**: {total_suites}")
        report_lines.append(f"- **Successful**: {successful_suites}")
        report_lines.append(f"- **Failed**: {failed_suites}")
        report_lines.append(f"- **Success Rate**: {(successful_suites/total_suites*100):.1f}%")
        report_lines.append("")
        
        # Detailed Results
        report_lines.append("## Detailed Results")
        report_lines.append("")
        
        for suite_name, result in results.items():
            status = "✅ PASSED" if result.get("success", False) else "❌ FAILED"
            duration = result.get("duration", 0)
            
            report_lines.append(f"### {suite_name} - {status}")
            report_lines.append(f"**Duration**: {duration:.1f}s")
            
            if "returncode" in result:
                report_lines.append(f"**Return Code**: {result['returncode']}")
            
            if "error" in result:
                report_lines.append(f"**Error**: {result['error']}")
            
            if result.get("timeout", False):
                report_lines.append("**Status**: Timed out")
            
            # Add stdout/stderr snippets for failures
            if not result.get("success", False):
                if "stderr" in result and result["stderr"]:
                    report_lines.append("**Error Output**:")
                    report_lines.append("```")
                    report_lines.append(result["stderr"][-500:])  # Last 500 chars
                    report_lines.append("```")
            
            report_lines.append("")
        
        # Performance Summary
        report_lines.append("## Performance Summary")
        suite_durations = [(name, r.get("duration", 0)) for name, r in results.items()]
        suite_durations.sort(key=lambda x: x[1], reverse=True)
        
        for suite_name, duration in suite_durations:
            report_lines.append(f"- **{suite_name}**: {duration:.1f}s")
        
        report_lines.append("")
        
        # Recommendations
        report_lines.append("## Recommendations")
        
        if failed_suites > 0:
            report_lines.append("### Failed Suites")
            for suite_name, result in results.items():
                if not result.get("success", False):
                    report_lines.append(f"- **{suite_name}**: Review logs and fix failing tests")
        
        # Performance recommendations
        slow_suites = [(name, dur) for name, dur in suite_durations if dur > 300]  # 5+ minutes
        if slow_suites:
            report_lines.append("### Performance Optimization")
            for suite_name, duration in slow_suites:
                report_lines.append(f"- **{suite_name}**: Consider optimization ({duration:.1f}s)")
        
        return "\n".join(report_lines)

    def save_report(self, results: Dict, output_path: str = None):
        """Save test report to file"""
        
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"integration_test_report_{timestamp}.md"
        
        report_content = self.generate_report(results)
        
        with open(output_path, 'w') as f:
            f.write(report_content)
        
        print(f"📊 Test report saved to: {output_path}")
        
        # Also save JSON results
        json_path = output_path.replace('.md', '.json')
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"📄 JSON results saved to: {json_path}")


async def main():
    """Main execution function"""
    
    parser = argparse.ArgumentParser(description="Run ruleIQ integration tests")
    parser.add_argument("--suite", choices=[
        "all", "api-workflows", "external-services", "contracts", 
        "database", "security", "performance", "ai-services", "e2e"
    ], default="all", help="Test suite to run")
    
    parser.add_argument("--report", help="Output report file path")
    parser.add_argument("--continue-on-failure", action="store_true",
                       help="Continue running suites even if one fails")
    parser.add_argument("--parallel", type=int, help="Override parallelism level")
    parser.add_argument("--timeout", type=int, help="Override timeout (seconds)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--markers", help="Additional pytest markers")
    
    args = parser.parse_args()
    
    runner = IntegrationTestRunner()
    
    # Setup environment
    if not runner.setup_environment():
        sys.exit(1)
    
    # Build additional pytest arguments
    additional_args = []
    
    if args.continue_on_failure:
        additional_args.append("--continue-on-failure")
    
    if args.parallel:
        additional_args.extend(["-n", str(args.parallel)])
    
    if args.timeout:
        additional_args.extend(["--timeout", str(args.timeout)])
    
    if args.verbose:
        additional_args.append("-vv")
    
    if args.markers:
        additional_args.extend(["-m", args.markers])
    
    # Run tests
    try:
        if args.suite == "all":
            results = await runner.run_all_suites(additional_args=additional_args)
        else:
            success, suite_result = await runner.run_test_suite(args.suite, additional_args)
            results = {args.suite: suite_result}
        
        # Generate and save report
        runner.save_report(results, args.report)
        
        # Print summary
        successful_suites = sum(1 for r in results.values() if r.get("success", False))
        total_suites = len(results)
        
        print(f"\n🎉 Integration test execution completed!")
        print(f"✅ {successful_suites}/{total_suites} suites passed")
        
        if successful_suites == total_suites:
            print("🚀 All integration tests passed!")
            sys.exit(0)
        else:
            print(f"❌ {total_suites - successful_suites} suites failed")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())