#!/usr/bin/env python3
"""
Execute Dead Code Analysis for P1 Task
This script performs the actual analysis and provides actionable results
"""

import os
import re
import subprocess
from pathlib import Path
from collections import defaultdict
import json

def analyze_celery_remnants(): print("\n🔍 ANALYZING CELERY REMNANTS...")
    celery_files = []
    project_root = Path("/home/omar/Documents/ruleIQ")
    
    celery_patterns = [
        r'celery',
        r'Celery',
        r'@app\.task',
        r'        r'\.delay\(',
        r'\.apply_async\(',
        r'CELERY_',
        r'broker_url',
        r'result_backend'
    ]
    
    for py_file in project_root.rglob("*.py"):
        if 'venv' in str(py_file) or '__pycache__' in str(py_file):
            continue
            
        try:
            with open(py_file, 'r') as f:
                content = f.read()
                for pattern in celery_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        celery_files.append(str(py_file.relative_to(project_root)))
                        break
        except:
            pass
            
    return celery_files

def analyze_commented_code(): print("\n🔍 ANALYZING COMMENTED CODE BLOCKS...")
    project_root = Path("/home/omar/Documents/ruleIQ")
    commented_blocks = defaultdict(list)
    
    for py_file in project_root.rglob("*.py"):
        if 'venv' in str(py_file) or '__pycache__' in str(py_file):
            continue
            
        try:
            with open(py_file, 'r') as f:
                lines = f.readlines()
                
            current_block = []
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped.startswith('#') and any(kw in stripped for kw in ['def ', 'class ', 'import ', 'if ']):
                    current_block.append(i)
                elif current_block and not stripped.startswith('#'):
                    if len(current_block) > 3:
                        commented_blocks[str(py_file.relative_to(project_root))].append({
                            "start": current_block[0],
                            "end": current_block[-1],
                            "lines": len(current_block)
                        })
                    current_block = []
        except:
            pass
            
    return dict(commented_blocks)

def analyze_console_logs(): print("\n🔍 ANALYZING CONSOLE.LOG STATEMENTS...")
    project_root = Path("/home/omar/Documents/ruleIQ")
    console_files = defaultdict(int)
    
    for js_file in project_root.rglob("*.{js,jsx,ts,tsx}"):
        if 'node_modules' in str(js_file) or '.next' in str(js_file):
            continue
            
        try:
            with open(js_file, 'r') as f:
                content = f.read()
                count = len(re.findall(r'console\.(log|error|warn|info|debug)', content))
                if count > 0:
                    console_files[str(js_file.relative_to(project_root))] = count
        except:
            pass
            
    return dict(console_files)

def analyze_empty_files(): print("\n🔍 ANALYZING EMPTY FILES...")
    project_root = Path("/home/omar/Documents/ruleIQ")
    empty_files = []
    
    for py_file in project_root.rglob("*.py"):
        if 'venv' in str(py_file) or '__pycache__' in str(py_file) or '__init__.py' in str(py_file):
            continue
            
        try:
            file_size = os.path.getsize(py_file)
            if file_size < 100:  # Less than 100 bytes is likely empty or minimal
                with open(py_file, 'r') as f:
                    content = f.read().strip()
                    if not content or content == 'pass' or 'TODO' in content:
                        empty_files.append(str(py_file.relative_to(project_root)))
        except:
            pass
            
    return empty_files

def analyze_unused_imports(): print("\n🔍 ANALYZING UNUSED IMPORTS...")
    project_root = Path("/home/omar/Documents/ruleIQ")
    
    # Run a quick flake8 check for unused imports
    try:
        result = subprocess.run(
            ["flake8", "--select=F401", "--count", str(project_root)],
            capture_output=True,
            text=True,
            timeout=10
        )
        unused_count = result.stdout.strip()
        if unused_count and unused_count.isdigit():
            return int(unused_count)
    except:
        pass
        
    return 0

def analyze_old_files(): print("\n🔍 ANALYZING OLD/BACKUP FILES...")
    project_root = Path("/home/omar/Documents/ruleIQ")
    old_files = []
    
    patterns = ['*.bak', '*.backup', '*.old', '*~', '*.orig', '*.tmp', '*.swp']
    for pattern in patterns:
        old_files.extend([str(f.relative_to(project_root)) for f in project_root.rglob(pattern)])
        
    return old_files

def analyze_test_skips(): print("\n🔍 ANALYZING SKIPPED TESTS...")
    project_root = Path("/home/omar/Documents/ruleIQ")
    skipped_tests = defaultdict(list)
    
    for test_file in project_root.rglob("test_*.py"):
        try:
            with open(test_file, 'r') as f:
                content = f.read()
                
            # Find @pytest.skip or @unittest.skip
            skips = re.findall(r'@(?:pytest\.)?skip(?:if)?.*\n.*def\s+(\w+)', content)
            if skips:
                skipped_tests[str(test_file.relative_to(project_root))] = skips
        except:
            pass
            
    return dict(skipped_tests)

def main(): print("="*80)
    print("DEAD CODE ANALYSIS FOR RULEIQ")
    print("P1 Task: 2f2f8b57 (merged with d3d23042)")
    print("="*80)
    
    results = {
        "celery_remnants": analyze_celery_remnants(),
        "commented_code": analyze_commented_code(),
        "console_logs": analyze_console_logs(),
        "empty_files": analyze_empty_files(),
        "unused_imports": analyze_unused_imports(),
        "old_files": analyze_old_files(),
        "skipped_tests": analyze_test_skips()
    }
    
    # Calculate metrics
    total_issues = 0
    estimated_lines = 0
    
    print("\n" + "="*80)
    print("ANALYSIS RESULTS")
    print("="*80)
    
    # Celery remnants
    if results["celery_remnants"]:
        print(f"\n📦 CELERY REMNANTS: {len(results['celery_remnants'])} files")
        for file in results["celery_remnants"][:5]:
            print(f"  • {file}")
        if len(results["celery_remnants"]) > 5:
            print(f"  ... and {len(results['celery_remnants']) - 5} more files")
        total_issues += len(results["celery_remnants"])
        estimated_lines += len(results["celery_remnants"]) * 20
        
    # Commented code
    if results["commented_code"]:
        total_blocks = sum(len(blocks) for blocks in results["commented_code"].values())
        total_comment_lines = sum(
            block["lines"] 
            for blocks in results["commented_code"].values() 
            for block in blocks
        )
        print(f"\n📦 COMMENTED CODE: {total_blocks} blocks ({total_comment_lines} lines)")
        for file, blocks in list(results["commented_code"].items())[:3]:
            print(f"  • {file}: {len(blocks)} blocks")
        total_issues += total_blocks
        estimated_lines += total_comment_lines
        
    # Console logs
    if results["console_logs"]:
        total_logs = sum(results["console_logs"].values())
        print(f"\n📦 CONSOLE.LOG STATEMENTS: {total_logs} found in {len(results['console_logs'])} files")
        for file, count in list(results["console_logs"].items())[:5]:
            print(f"  • {file}: {count} statements")
        total_issues += total_logs
        estimated_lines += total_logs
        
    # Empty files
    if results["empty_files"]:
        print(f"\n📦 EMPTY FILES: {len(results['empty_files'])} files")
        for file in results["empty_files"][:5]:
            print(f"  • {file}")
        total_issues += len(results["empty_files"])
        estimated_lines += len(results["empty_files"]) * 10
        
    # Unused imports
    if results["unused_imports"]:
        print(f"\n📦 UNUSED IMPORTS: ~{results['unused_imports']} found")
        total_issues += results["unused_imports"]
        estimated_lines += results["unused_imports"]
        
    # Old files
    if results["old_files"]:
        print(f"\n📦 OLD/BACKUP FILES: {len(results['old_files'])} files")
        for file in results["old_files"][:5]:
            print(f"  • {file}")
        total_issues += len(results["old_files"])
        
    # Skipped tests
    if results["skipped_tests"]:
        total_skipped = sum(len(tests) for tests in results["skipped_tests"].values())
        print(f"\n📦 SKIPPED TESTS: {total_skipped} tests in {len(results['skipped_tests'])} files")
        for file, tests in list(results["skipped_tests"].items())[:3]:
            print(f"  • {file}: {', '.join(tests)}")
        total_issues += total_skipped
        
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Total dead code issues: {total_issues}")
    print(f"Estimated removable lines: ~{estimated_lines}")
    print(f"Files affected: {len(set(results['celery_remnants'] + list(results['commented_code'].keys()) + list(results['console_logs'].keys()) + results['empty_files'] + results['old_files']))}")
    
    # Save detailed report
    report_path = Path("/home/omar/Documents/ruleIQ/dead_code_analysis_report.json")
    with open(report_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n📄 Detailed report saved to: {report_path}")
    
    # Recommendations
    print("\n" + "="*80)
    print("RECOMMENDED ACTIONS")
    print("="*80)
    print("1. Run: python scripts/dead_code_removal.py --execute")
    print("2. This will create a backup and remove dead code")
    print("3. Run tests after removal to ensure nothing breaks")
    print("4. Commit changes if all tests pass")
    
    return total_issues, estimated_lines

if __name__ == "__main__":
    issues, lines = main()
    print(f"\n✅ Analysis complete: {issues} issues, ~{lines} lines can be removed")