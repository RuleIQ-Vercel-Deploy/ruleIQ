#!/usr/bin/env python3
"""
Script to safely remove Celery code from the ruleIQ codebase.
Run this after confirming LangGraph is fully operational.

Usage: python scripts/sonar/remove-celery-code.py [--dry-run] [--backup] 
import os
import shutil
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

# Project root
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Files and directories to remove
FILES_TO_REMOVE = [
    "celery_app.py",
    "workers/evidence_tasks.py",
    "workers/compliance_tasks.py",
    "workers/notification_tasks.py",
    "workers/reporting_tasks.py",
    "workers/monitoring_tasks.py",
]

DEPENDENCIES_TO_REMOVE = [
    "celery",
    "redis",
    "flower",
    "kombu",
    "amqp",
    "vine",
    "billiard",
    "celery[redis]",
]

# Environment variables to flag for removal
ENV_VARS_TO_REMOVE = [
    "REDIS_URL",
    "CELERY_BROKER_URL",
    "CELERY_RESULT_BACKEND",
    "CELERY_TASK_SERIALIZER",
    "CELERY_RESULT_SERIALIZER",
]

# Import patterns to clean up
IMPORT_PATTERNS = [
    "    "    "from workers.evidence_tasks import",
    "from workers.compliance_tasks import",
    "from workers.notification_tasks import",
    "from workers.reporting_tasks import",
    "from workers.monitoring_tasks import",
    "from celery_app import",
]

class CeleryRemover:
    """Safely remove Celery code from the project."""
    
    def __init__(self, dry_run: bool = False, backup: bool = True):
        self.dry_run = dry_run
        self.backup = backup
        self.removed_files = []
        self.modified_files = []
        self.errors = []
        
    def run(self) -> Dict[str, any]: print("🔍 Starting Celery code removal process...")
        
        if self.backup and not self.dry_run:
            self.create_backup()
        
        # Step 1: Remove Celery files
        self.remove_celery_files()
        
        # Step 2: Clean up imports
        self.clean_imports()
        
        # Step 3: Update requirements files
        self.update_requirements()
        
        # Step 4: Flag environment variables
        self.flag_env_vars()
        
        # Step 5: Generate report
        report = self.generate_report()
        
        if not self.dry_run:
            self.save_report(report)
        
        return report
    
    def create_backup(self): backup_dir = PROJECT_ROOT / f"celery_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"📦 Creating backup at {backup_dir}")
        
        for file_path in FILES_TO_REMOVE:
            full_path = PROJECT_ROOT / file_path
            if full_path.exists():
                backup_path = backup_dir / file_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(full_path, backup_path)
                print(f"  ✓ Backed up {file_path}")
    
    def remove_celery_files(self): print("\n🗑️  Removing Celery files...")
        
        for file_path in FILES_TO_REMOVE:
            full_path = PROJECT_ROOT / file_path
            if full_path.exists():
                if self.dry_run:
                    print(f"  [DRY RUN] Would remove: {file_path}")
                else:
                    try:
                        full_path.unlink()
                        print(f"  ✓ Removed: {file_path}")
                        self.removed_files.append(str(file_path))
                    except Exception as e:
                        print(f"  ✗ Error removing {file_path}: {e}")
                        self.errors.append(f"Failed to remove {file_path}: {e}")
            else:
                print(f"  ⚠️  File not found: {file_path}")
    
    def clean_imports(self): print("\n🧹 Cleaning up imports...")
        
        python_files = list(PROJECT_ROOT.rglob("*.py"))
        
        for py_file in python_files:
            # Skip migration files and this script
            if "migration" in str(py_file).lower() or py_file == Path(__file__):
                continue
            
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                
                original_content = content
                modified = False
                
                lines = content.split('\n')
                new_lines = []
                
                for line in lines:
                    should_remove = False
                    for pattern in IMPORT_PATTERNS:
                        if pattern in line:
                            should_remove = True
                            break
                    
                    if not should_remove:
                        new_lines.append(line)
                    else:
                        modified = True
                        if self.dry_run:
                            print(f"  [DRY RUN] Would remove from {py_file.relative_to(PROJECT_ROOT)}: {line.strip()}")
                
                if modified and not self.dry_run:
                    content = '\n'.join(new_lines)
                    
                    # Clean up extra blank lines
                    while '\n\n\n' in content:
                        content = content.replace('\n\n\n', '\n\n')
                    
                    with open(py_file, 'w') as f:
                        f.write(content)
                    
                    self.modified_files.append(str(py_file.relative_to(PROJECT_ROOT)))
                    print(f"  ✓ Cleaned imports in {py_file.relative_to(PROJECT_ROOT)}")
                    
            except Exception as e:
                self.errors.append(f"Error processing {py_file}: {e}")
    
    def update_requirements(self): print("\n📦 Updating requirements files...")
        
        req_files = [
            "requirements.txt",
            "requirements-dev.txt",
            "pyproject.toml",
            "setup.py",
        ]
        
        for req_file in req_files:
            req_path = PROJECT_ROOT / req_file
            if not req_path.exists():
                continue
            
            try:
                with open(req_path, 'r') as f:
                    lines = f.readlines()
                
                new_lines = []
                modified = False
                
                for line in lines:
                    should_remove = False
                    for dep in DEPENDENCIES_TO_REMOVE:
                        if dep in line.lower():
                            should_remove = True
                            modified = True
                            if self.dry_run:
                                print(f"  [DRY RUN] Would remove from {req_file}: {line.strip()}")
                            break
                    
                    if not should_remove:
                        new_lines.append(line)
                
                if modified and not self.dry_run:
                    with open(req_path, 'w') as f:
                        f.writelines(new_lines)
                    print(f"  ✓ Updated {req_file}")
                    self.modified_files.append(req_file)
                    
            except Exception as e:
                self.errors.append(f"Error updating {req_file}: {e}")
    
    def flag_env_vars(self): print("\n🚩 Flagging environment variables...")
        
        env_files = [".env", ".env.local", ".env.example", ".env.template"]
        
        for env_file in env_files:
            env_path = PROJECT_ROOT / env_file
            if not env_path.exists():
                continue
            
            try:
                with open(env_path, 'r') as f:
                    content = f.read()
                
                for var in ENV_VARS_TO_REMOVE:
                    if var in content:
                        print(f"  ⚠️  Found {var} in {env_file} - manual removal recommended")
                        
            except Exception as e:
                self.errors.append(f"Error checking {env_file}: {e}")
    
    def generate_report(self) -> Dict[str, any]: report = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "removed_files": self.removed_files,
            "modified_files": self.modified_files,
            "errors": self.errors,
            "summary": {
                "files_removed": len(self.removed_files),
                "files_modified": len(self.modified_files),
                "errors_encountered": len(self.errors),
            },
            "next_steps": [
                "1. Run tests to ensure nothing is broken",
                "2. Remove environment variables from .env files",
                "3. Update Docker/deployment configs if needed",
                "4. Remove Redis service if not used elsewhere",
                "5. Update documentation",
            ]
        }
        
        return report
    
    def save_report(self, report: Dict[str, any]): report_path = PROJECT_ROOT / "scripts/sonar/celery_removal_report.json"
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Report saved to {report_path}")
    
    def print_summary(self, report: Dict[str, any]): print("\n" + "="*50)
        print("CELERY REMOVAL SUMMARY")
        print("="*50)
        
        if self.dry_run:
            print("🔍 DRY RUN MODE - No changes were made")
        
        print(f"\n📊 Statistics:")
        print(f"  • Files removed: {report['summary']['files_removed']}")
        print(f"  • Files modified: {report['summary']['files_modified']}")
        print(f"  • Errors: {report['summary']['errors_encountered']}")
        
        if report['errors']:
            print(f"\n⚠️  Errors encountered:")
            for error in report['errors']:
                print(f"  • {error}")
        
        print(f"\n📋 Next Steps:")
        for step in report['next_steps']:
            print(f"  {step}")

def main():
    """Main"""
    parser = argparse.ArgumentParser(
        description="Remove Celery code from ruleIQ codebase"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without making changes"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip creating backup (not recommended)"
    )
    
    args = parser.parse_args()
    
    remover = CeleryRemover(
        dry_run=args.dry_run,
        backup=not args.no_backup
    )
    
    report = remover.run()
    remover.print_summary(report)
    
    if args.dry_run:
        print("\n💡 To actually remove Celery code, run without --dry-run flag")
    else:
        print("\n✅ Celery code removal complete!")
        print("⚠️  Remember to run tests and check the application!")

if __name__ == "__main__":
    main()