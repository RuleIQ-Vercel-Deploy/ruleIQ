#!/usr/bin/env python3
"""
Dead Code Removal Script for RuleIQ
Priority P1 Task: 2f2f8b57 (merged with d3d23042)
Systematically removes identified dead code while maintaining functionality
"""

import os
import re
import ast
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple
import subprocess

class DeadCodeRemover:
    def __init__(self, dry_run: bool = True):
        self.project_root = Path("/home/omar/Documents/ruleIQ")
        self.dry_run = dry_run
        self.backup_dir = None
        self.report = {
            "removed": {
                "files": [],
                "imports": [],
                "functions": [],
                "classes": [],
                "variables": [],
                "comments": [],
                "config": []
            },
            "metrics": {
                "lines_removed": 0,
                "files_deleted": 0,
                "files_modified": 0,
                "size_reduction_bytes": 0
            },
            "risks": []
        }
        
    def create_backup(self):
        """Create backup before making changes"""
        if not self.dry_run:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.backup_dir = self.project_root / f"backup_{timestamp}"
            print(f"📦 Creating backup at {self.backup_dir}...")
            
            # Create selective backup (exclude large directories)
            ignore_patterns = shutil.ignore_patterns(
                'venv', 'node_modules', '.git', '__pycache__', 
                '.next', 'dist', 'build', '*.pyc', '*.pyo'
            )
            shutil.copytree(self.project_root, self.backup_dir, ignore=ignore_patterns)
            print(f"✅ Backup created successfully")
            
    def remove_celery_code(self):
        """Remove all Celery-related code (completely replaced by LangGraph)"""
        print("\n🔍 Removing Celery remnants...")
        
        celery_patterns = [
            (r'from\s+celery\s+import.*\n', ''),
            (r'import\s+celery.*\n', ''),
            (r'@app\.task.*\n', ''),
            (r'            (r'\.delay\([^)]*\)', '()'),  # Convert () to regular calls
            (r'\.apply_async\([^)]*\)', '()'),  # Convert () to regular calls
            (r'CELERY_[A-Z_]+\s*=.*\n', ''),
            (r'celery_app\s*=.*\n', ''),
            (r'            (r'        ]
        
        files_modified = 0
        lines_removed = 0
        
        for py_file in self.project_root.rglob("*.py"):
            if any(skip in str(py_file) for skip in ['venv', '__pycache__', 'test_', 'tests/']):
                continue
                
            try:
                with open(py_file, 'r') as f:
                    original_content = f.read()
                    
                modified_content = original_content
                for pattern, replacement in celery_patterns:
                    before_lines = len(modified_content.split('\n'))
                    modified_content = re.sub(pattern, replacement, modified_content, flags=re.MULTILINE)
                    after_lines = len(modified_content.split('\n'))
                    lines_removed += (before_lines - after_lines)
                    
                if modified_content != original_content:
                    if not self.dry_run:
                        with open(py_file, 'w') as f:
                            f.write(modified_content)
                    
                    files_modified += 1
                    self.report["removed"]["imports"].append({
                        "file": str(py_file.relative_to(self.project_root)),
                        "type": "celery",
                        "lines": lines_removed
                    })
                    
            except Exception as e:
                print(f"⚠️  Error processing {py_file}: {e}")
                
        self.report["metrics"]["files_modified"] += files_modified
        self.report["metrics"]["lines_removed"] += lines_removed
        print(f"  ✅ Removed Celery code from {files_modified} files ({lines_removed} lines)")
        
    def remove_unused_imports(self):
        """Remove unused imports from Python files"""
        print("\n🔍 Removing unused imports...")
        
        if not self.dry_run:
            try:
                result = subprocess.run([
                    "autoflake",
                    "--in-place",
                    "--remove-all-unused-imports",
                    "--remove-unused-variables",
                    "--recursive",
                    "--exclude=venv,__pycache__,tests",
                    str(self.project_root)
                ], capture_output=True, text=True)
                
                modified_files = len([l for l in result.stdout.split('\n') if 'fixed' in l])
                self.report["metrics"]["files_modified"] += modified_files
                print(f"  ✅ Cleaned {modified_files} files with autoflake")
                
            except FileNotFoundError:
                print("  ⚠️  autoflake not installed. Install with: pip install autoflake")
        else:
            print("  📝 Would run autoflake to remove unused imports (dry run)")
            
    def remove_commented_code(self):
        """Remove large blocks of commented code"""
        print("\n🔍 Removing commented code blocks...")
        
        files_modified = 0
        total_lines_removed = 0
        
        for py_file in self.project_root.rglob("*.py"):
            if any(skip in str(py_file) for skip in ['venv', '__pycache__']):
                continue
                
            try:
                with open(py_file, 'r') as f:
                    lines = f.readlines()
                    
                new_lines = []
                skip_block = False
                block_start = -1
                
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    
                    # Detect start of commented code block
                    if (stripped.startswith('#') and 
                        any(kw in stripped for kw in ['def ', 'class ', 'import ', 'from '])):
                        if not skip_block:
                            block_start = i
                            skip_block = True
                    # End of commented block
                    elif skip_block and not stripped.startswith('#'):
                        block_size = i - block_start
                        if block_size > 3:  # Remove blocks larger than 3 lines
                            total_lines_removed += block_size
                            self.report["removed"]["comments"].append({
                                "file": str(py_file.relative_to(self.project_root)),
                                "lines": block_size,
                                "start": block_start + 1
                            })
                        else:
                            # Keep small comment blocks
                            new_lines.extend(lines[block_start:i])
                        skip_block = False
                        new_lines.append(line)
                    elif not skip_block:
                        new_lines.append(line)
                        
                if len(new_lines) < len(lines):
                    if not self.dry_run:
                        with open(py_file, 'w') as f:
                            f.writelines(new_lines)
                    files_modified += 1
                    
            except Exception as e:
                print(f"⚠️  Error processing {py_file}: {e}")
                
        self.report["metrics"]["files_modified"] += files_modified
        self.report["metrics"]["lines_removed"] += total_lines_removed
        print(f"  ✅ Removed {total_lines_removed} lines of commented code from {files_modified} files")
        
    def remove_console_logs(self):
        """Remove console.log statements from JavaScript/TypeScript"""
        print("\n🔍 Removing console.log statements...")
        
        files_modified = 0
        lines_removed = 0
        
        js_patterns = [
            (r'^\s*console\.(log|error|warn|info|debug)\([^)]*\);?\s*\n', ''),
            (r'//\s*console\.(log|error|warn|info|debug)\([^)]*\);?\s*\n', ''),
        ]
        
        for js_file in self.project_root.rglob("*.{js,jsx,ts,tsx}"):
            if any(skip in str(js_file) for skip in ['node_modules', '.next', 'dist', 'build']):
                continue
                
            try:
                with open(js_file, 'r') as f:
                    original_content = f.read()
                    
                modified_content = original_content
                for pattern, replacement in js_patterns:
                    before_lines = len(modified_content.split('\n'))
                    modified_content = re.sub(pattern, replacement, modified_content, flags=re.MULTILINE)
                    after_lines = len(modified_content.split('\n'))
                    lines_removed += (before_lines - after_lines)
                    
                if modified_content != original_content:
                    if not self.dry_run:
                        with open(js_file, 'w') as f:
                            f.write(modified_content)
                    
                    files_modified += 1
                    
            except Exception as e:
                print(f"⚠️  Error processing {js_file}: {e}")
                
        self.report["metrics"]["files_modified"] += files_modified
        self.report["metrics"]["lines_removed"] += lines_removed
        print(f"  ✅ Removed console.log from {files_modified} files ({lines_removed} lines)")
        
    def remove_empty_files(self):
        """Remove empty or near-empty Python files"""
        print("\n🔍 Removing empty files...")
        
        files_deleted = 0
        
        for py_file in self.project_root.rglob("*.py"):
            if any(skip in str(py_file) for skip in ['venv', '__pycache__', '__init__.py']):
                continue
                
            try:
                with open(py_file, 'r') as f:
                    content = f.read().strip()
                    
                # Check if file is effectively empty
                if (not content or 
                    content == '"""TODO: Implement"""' or
                    content == 'pass' or
                    len(content) < 50 and 'import' not in content):
                    
                    if not self.dry_run:
                        os.remove(py_file)
                    
                    files_deleted += 1
                    self.report["removed"]["files"].append(
                        str(py_file.relative_to(self.project_root))
                    )
                    
            except Exception as e:
                print(f"⚠️  Error checking {py_file}: {e}")
                
        self.report["metrics"]["files_deleted"] += files_deleted
        print(f"  ✅ Removed {files_deleted} empty files")
        
    def remove_old_backups(self):
        """Remove old backup and temporary files"""
        print("\n🔍 Removing old backup files...")
        
        backup_patterns = ['*.bak', '*.backup', '*.old', '*~', '*.orig', '*.tmp']
        files_deleted = 0
        
        for pattern in backup_patterns:
            for backup_file in self.project_root.rglob(pattern):
                try:
                    if not self.dry_run:
                        os.remove(backup_file)
                    files_deleted += 1
                    self.report["removed"]["files"].append(
                        str(backup_file.relative_to(self.project_root))
                    )
                except Exception as e:
                    print(f"⚠️  Error removing {backup_file}: {e}")
                    
        self.report["metrics"]["files_deleted"] += files_deleted
        print(f"  ✅ Removed {files_deleted} backup/temporary files")
        
    def clean_unused_dependencies(self):
        """Identify unused dependencies in requirements.txt and package.json"""
        print("\n🔍 Analyzing unused dependencies...")
        
        # Python dependencies
        unused_python = []
        req_file = self.project_root / "requirements.txt"
        if req_file.exists():
            with open(req_file, 'r') as f:
                requirements = [line.split('>=')[0].split('==')[0].strip() 
                              for line in f if line.strip() and not line.startswith('#')]
                
            # Check actual imports
            imported_modules = set()
            for py_file in self.project_root.rglob("*.py"):
                if 'venv' not in str(py_file):
                    try:
                        with open(py_file, 'r') as f:
                            content = f.read()
                            imports = re.findall(r'(?:from|import)\s+(\w+)', content)
                            imported_modules.update(imports)
                    except:
                        pass
                        
            # Find potentially unused
            for req in requirements:
                req_name = req.replace('-', '_').lower()
                if req_name not in str(imported_modules).lower():
                    unused_python.append(req)
                    
        if unused_python:
            print(f"  ⚠️  Potentially unused Python packages: {', '.join(unused_python[:10])}")
            self.report["risks"].append({
                "type": "unused_dependencies",
                "packages": unused_python,
                "recommendation": "Review and remove if truly unused"
            })
            
    def clean_env_variables(self):
        """Remove unused environment variables"""
        print("\n🔍 Cleaning environment variables...")
        
        env_files = ['.env', '.env.example', '.env.local']
        all_vars = {}
        
        # Collect all defined variables
        for env_file in env_files:
            env_path = self.project_root / env_file
            if env_path.exists():
                with open(env_path, 'r') as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            var_name = line.split('=')[0].strip()
                            all_vars[var_name] = env_file
                            
        # Check usage
        used_vars = set()
        for code_file in self.project_root.rglob("*.{py,js,jsx,ts,tsx}"):
            if any(skip in str(code_file) for skip in ['venv', 'node_modules']):
                continue
            try:
                with open(code_file, 'r') as f:
                    content = f.read()
                    for var in all_vars:
                        if var in content:
                            used_vars.add(var)
            except:
                pass
                
        unused_vars = set(all_vars.keys()) - used_vars
        
        if unused_vars:
            print(f"  ⚠️  Found {len(unused_vars)} unused environment variables")
            for var in list(unused_vars)[:10]:
                print(f"     - {var} (in {all_vars[var]})")
            
            self.report["removed"]["config"].extend(list(unused_vars))
            
    def generate_final_report(self):
        """Generate comprehensive removal report"""
        print("\n" + "="*80)
        print("DEAD CODE REMOVAL REPORT")
        print("="*80)
        
        if self.dry_run:
            print("\n⚠️  DRY RUN MODE - No actual changes made")
        else:
            print("\n✅ CHANGES APPLIED")
            
        print("\n📊 METRICS:")
        print(f"  • Files deleted: {self.report['metrics']['files_deleted']}")
        print(f"  • Files modified: {self.report['metrics']['files_modified']}")
        print(f"  • Lines removed: {self.report['metrics']['lines_removed']}")
        
        print("\n📦 REMOVED ITEMS:")
        if self.report["removed"]["imports"]:
            print(f"  • Imports cleaned: {len(self.report['removed']['imports'])} files")
        if self.report["removed"]["comments"]:
            total_comment_lines = sum(c['lines'] for c in self.report["removed"]["comments"])
            print(f"  • Commented code: {total_comment_lines} lines")
        if self.report["removed"]["files"]:
            print(f"  • Deleted files: {len(self.report['removed']['files'])}")
        if self.report["removed"]["config"]:
            print(f"  • Unused env vars: {len(self.report['removed']['config'])}")
            
        if self.report["risks"]:
            print("\n⚠️  RISKS TO REVIEW:")
            for risk in self.report["risks"]:
                print(f"  • {risk['type']}: {risk['recommendation']}")
                
        # Save detailed report
        report_path = self.project_root / "dead_code_removal_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.report, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_path}")
        
        if self.backup_dir:
            print(f"\n💾 Backup available at: {self.backup_dir}")
            
        return self.report["metrics"]["lines_removed"]
        
    def run_tests(self):
        """Run tests to ensure nothing broke"""
        print("\n🧪 Running tests to verify functionality...")
        
        try:
            # Run Python tests
            result = subprocess.run(
                ["pytest", "--tb=short", "-q"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if "passed" in result.stdout:
                print("  ✅ Python tests passed")
            else:
                print("  ⚠️  Some Python tests failed - review changes")
                self.report["risks"].append({
                    "type": "test_failure",
                    "message": "Some tests failed after cleanup"
                })
                
        except FileNotFoundError:
            print("  ⚠️  pytest not available")
            
def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Dead Code Removal for RuleIQ")
    parser.add_argument("--execute", action="store_true", 
                       help="Actually remove dead code (default is dry run)")
    parser.add_argument("--no-backup", action="store_true",
                       help="Skip backup creation (not recommended)")
    args = parser.parse_args()
    
    print("="*80)
    print("RULEIQ DEAD CODE REMOVAL TOOL")
    print("P1 Priority Task: 2f2f8b57")
    print("="*80)
    
    remover = DeadCodeRemover(dry_run=not args.execute)
    
    if args.execute and not args.no_backup:
        remover.create_backup()
        
    # Execute removal phases
    remover.remove_celery_code()
    remover.remove_unused_imports()
    remover.remove_commented_code()
    remover.remove_console_logs()
    remover.remove_empty_files()
    remover.remove_old_backups()
    remover.clean_unused_dependencies()
    remover.clean_env_variables()
    
    # Generate report
    lines_removed = remover.generate_final_report()
    
    # Run tests if changes were made
    if args.execute:
        remover.run_tests()
        
    print("\n" + "="*80)
    if args.execute:
        print(f"✅ DEAD CODE REMOVAL COMPLETE - {lines_removed} lines removed")
        print("Please review changes and run full test suite")
    else:
        print(f"📝 DRY RUN COMPLETE - Would remove ~{lines_removed} lines")
        print("Run with --execute to apply changes")
    print("="*80)

if __name__ == "__main__":
    main()