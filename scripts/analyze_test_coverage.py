#!/usr/bin/env python3
"""
Test Coverage Analysis and Enhancement Script
Task ID: 17d37db3 - Test Coverage Enhancement
Target: 70% coverage for Day 4 of P3 Group A
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestCoverageAnalyzer:
    """Analyze test coverage and identify gaps."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.coverage_data = {}
        self.uncovered_files = []
        self.low_coverage_files = []
        
    def run_coverage(self) -> Dict:
        """Run pytest with coverage and capture results."""
        logger.info("Running test coverage analysis...")
        
        # Run pytest with coverage
        cmd = [
            "python", "-m", "pytest",
            "--cov=.",
            "--cov-report=json:coverage.json",
            "--cov-report=term-missing",
            "--tb=short",
            "-q"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            # Load coverage data
            coverage_file = self.project_root / "coverage.json"
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    self.coverage_data = json.load(f)
                    
            return self.coverage_data
            
        except subprocess.TimeoutExpired:
            logger.error("Coverage analysis timed out")
            return {}
        except Exception as e:
            logger.error(f"Error running coverage: {e}")
            return {}
    
    def analyze_gaps(self) -> Dict:
        """Analyze coverage gaps and prioritize files needing tests."""
        if not self.coverage_data:
            logger.warning("No coverage data available")
            return {}
            
        files = self.coverage_data.get('files', {})
        total_stats = self.coverage_data.get('totals', {})
        
        # Current coverage percentage
        current_coverage = total_stats.get('percent_covered', 0)
        logger.info(f"Current Overall Coverage: {current_coverage:.2f}%")
        
        # Categorize files by coverage
        for filepath, file_data in files.items():
            # Skip test files and non-source files
            if any(skip in filepath for skip in ['test_', '/tests/', '__pycache__', '.pyc']):
                continue
                
            coverage_percent = file_data.get('summary', {}).get('percent_covered', 0)
            missing_lines = file_data.get('missing_lines', [])
            
            if coverage_percent == 0:
                self.uncovered_files.append({
                    'file': filepath,
                    'lines': file_data.get('summary', {}).get('num_statements', 0),
                    'missing': len(missing_lines)
                })
            elif coverage_percent < 60:
                self.low_coverage_files.append({
                    'file': filepath,
                    'coverage': coverage_percent,
                    'lines': file_data.get('summary', {}).get('num_statements', 0),
                    'missing': len(missing_lines),
                    'missing_lines': missing_lines[:10]  # First 10 uncovered lines
                })
        
        # Sort by potential impact (lines of code * (100 - coverage))
        self.uncovered_files.sort(key=lambda x: x['lines'], reverse=True)
        self.low_coverage_files.sort(
            key=lambda x: x['lines'] * (100 - x['coverage']), 
            reverse=True
        )
        
        return {
            'current_coverage': current_coverage,
            'target_coverage': 70,
            'gap': 70 - current_coverage,
            'uncovered_files': self.uncovered_files[:10],
            'low_coverage_files': self.low_coverage_files[:15],
            'total_files': len(files),
            'files_with_zero_coverage': len(self.uncovered_files),
            'files_below_60_percent': len(self.low_coverage_files)
        }
    
    def identify_critical_paths(self) -> List[str]:
        """Identify critical business logic paths that need testing."""
        critical_paths = []
        
        # Define critical path patterns
        critical_patterns = [
            'api/routers/',  # API endpoints
            'services/ai/',  # AI services
            'services/compliance',  # Compliance logic
            'services/assessment',  # Assessment services
            'api/dependencies/',  # Authentication/Authorization
            'database/models/',  # Database models
            'services/reporting/',  # Reporting services
            'api/middleware/',  # Middleware components
        ]
        
        for pattern in critical_patterns:
            for filepath, file_data in self.coverage_data.get('files', {}).items():
                if pattern in filepath:
                    coverage = file_data.get('summary', {}).get('percent_covered', 0)
                    if coverage < 70:
                        critical_paths.append({
                            'file': filepath,
                            'coverage': coverage,
                            'priority': 'HIGH' if coverage < 40 else 'MEDIUM'
                        })
        
        return critical_paths
    
    def generate_test_plan(self) -> Dict:
        """Generate a test plan to reach 70% coverage."""
        gaps = self.analyze_gaps()
        critical_paths = self.identify_critical_paths()
        
        # Calculate how many lines need coverage
        current_coverage = gaps['current_coverage']
        coverage_gap = gaps['gap']
        
        test_plan = {
            'current_coverage': current_coverage,
            'target_coverage': 70,
            'coverage_gap': coverage_gap,
            'priority_files': [],
            'estimated_tests_needed': 0
        }
        
        # Prioritize files for testing
        priority_files = []
        
        # 1. Critical paths with low coverage
        for path in critical_paths[:5]:
            priority_files.append({
                'file': path['file'],
                'current_coverage': path['coverage'],
                'priority': path['priority'],
                'test_type': 'unit + integration'
            })
        
        # 2. Uncovered files with significant code
        for file in self.uncovered_files[:5]:
            if file['lines'] > 50:
                priority_files.append({
                    'file': file['file'],
                    'current_coverage': 0,
                    'priority': 'HIGH',
                    'test_type': 'unit',
                    'lines_to_cover': file['lines']
                })
        
        # 3. Low coverage files with high impact
        for file in self.low_coverage_files[:10]:
            if file['lines'] > 30:
                priority_files.append({
                    'file': file['file'],
                    'current_coverage': file['coverage'],
                    'priority': 'MEDIUM',
                    'test_type': 'unit',
                    'lines_to_cover': file['missing']
                })
        
        test_plan['priority_files'] = priority_files
        test_plan['estimated_tests_needed'] = len(priority_files) * 5  # Avg 5 tests per file
        
        return test_plan
    
    def report(self) -> str:
        """Generate a comprehensive coverage report."""
        gaps = self.analyze_gaps()
        test_plan = self.generate_test_plan()
        
        report = []
        report.append("=" * 80)
        report.append("TEST COVERAGE ANALYSIS REPORT")
        report.append("Task ID: 17d37db3 - Test Coverage Enhancement")
        report.append("=" * 80)
        report.append("")
        
        report.append(f"📊 CURRENT STATUS:")
        report.append(f"  • Current Coverage: {gaps['current_coverage']:.2f}%")
        report.append(f"  • Target Coverage: {gaps['target_coverage']}%")
        report.append(f"  • Coverage Gap: {gaps['gap']:.2f}%")
        report.append(f"  • Total Files: {gaps['total_files']}")
        report.append(f"  • Files with 0% Coverage: {gaps['files_with_zero_coverage']}")
        report.append(f"  • Files Below 60%: {gaps['files_below_60_percent']}")
        report.append("")
        
        report.append("🎯 TOP PRIORITY FILES FOR TESTING:")
        for i, file in enumerate(test_plan['priority_files'][:10], 1):
            report.append(f"  {i}. {file['file']}")
            report.append(f"     Coverage: {file['current_coverage']:.1f}% | Priority: {file['priority']} | Type: {file['test_type']}")
        report.append("")
        
        report.append("📋 TEST PLAN TO REACH 70%:")
        report.append(f"  • Estimated Tests Needed: {test_plan['estimated_tests_needed']}")
        report.append(f"  • Focus Areas:")
        report.append(f"    - API Endpoints (Critical)")
        report.append(f"    - Service Layer (High Priority)")
        report.append(f"    - Database Models (Medium Priority)")
        report.append(f"    - Utility Functions (Low Priority)")
        report.append("")
        
        if self.uncovered_files[:5]:
            report.append("⚠️  COMPLETELY UNCOVERED FILES (Top 5):")
            for file in self.uncovered_files[:5]:
                report.append(f"  • {file['file']} ({file['lines']} lines)")
        report.append("")
        
        report.append("✅ RECOMMENDATIONS:")
        report.append("  1. Start with critical API endpoints lacking tests")
        report.append("  2. Add integration tests for service layer")
        report.append("  3. Cover error handling and edge cases")
        report.append("  4. Use pytest fixtures to reduce test duplication")
        report.append("  5. Focus on business logic over boilerplate")
        report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """Main execution function."""
    project_root = Path("/home/omar/Documents/ruleIQ")
    
    analyzer = TestCoverageAnalyzer(project_root)
    
    # Run coverage analysis
    coverage_data = analyzer.run_coverage()
    
    if not coverage_data:
        logger.error("Failed to get coverage data")
        sys.exit(1)
    
    # Generate and print report
    report = analyzer.report()
    print(report)
    
    # Save report to file
    report_file = project_root / "coverage_analysis_report.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    logger.info(f"Report saved to {report_file}")
    
    # Generate test plan JSON
    test_plan = analyzer.generate_test_plan()
    plan_file = project_root / "test_enhancement_plan.json"
    with open(plan_file, 'w') as f:
        json.dump(test_plan, f, indent=2)
    
    logger.info(f"Test plan saved to {plan_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())