#!/usr/bin/env python3
"""
Dead Code Removal Script for RuleIQ
Safely removes identified dead code patterns from the codebase
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict

def backup_files(files: List[Path]) -> str:
    """Create backup of files before modification"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"backup_dead_code_{timestamp}")
    backup_dir.mkdir(exist_ok=True)
    
    cwd = Path.cwd()
    for file in files:
        if file.exists():
            try:
                # Make paths absolute for consistency
                file_abs = file.resolve()
                cwd_abs = cwd.resolve()
                
                # Get relative path
                if file_abs.is_relative_to(cwd_abs):
                    rel_path = file_abs.relative_to(cwd_abs)
                else:
                    # Skip files outside the project
                    continue
                    
                backup_path = backup_dir / rel_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file, backup_path)
            except Exception as e:
                print(f"  ⚠️ Could not backup {file}: {e}")
    
    print(f"✅ Backup created in {backup_dir}")
    return str(backup_dir)

def remove_celery_imports(content: str) -> str:
    """Remove Celery-related imports"""
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Skip Celery imports
        if re.match(r'^\s*(from celery import|import celery)', line):
            continue
        # Skip Celery decorators
        if re.match(r'^\s*@(task|periodic_task|shared_task)', line):
            continue
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def remove_commented_code(content: str) -> str:
    """Remove commented out code blocks"""
    lines = content.split('\n')
    cleaned_lines = []
    
    for line in lines:
        # Keep TODO/FIXME comments
        if re.search(r'#\s*(TODO|FIXME|HACK|XXX)', line):
            cleaned_lines.append(line)
        # Remove commented code
        elif re.match(r'^\s*#.*\b(def|class|import|from)\b', line):
            continue
        else:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def clean_file(file_path: Path) -> Tuple[bool, int]:
    """Clean a single file and return if modified and lines removed"""
    if not file_path.exists() or '.venv' in str(file_path) or '__pycache__' in str(file_path):
        return False, 0
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        original_lines = len(original_content.split('\n'))
        
        # Apply cleaning transformations
        cleaned_content = original_content
        cleaned_content = remove_celery_imports(cleaned_content)
        cleaned_content = remove_commented_code(cleaned_content)
        
        # Remove multiple blank lines
        cleaned_content = re.sub(r'\n\n\n+', '\n\n', cleaned_content)
        
        cleaned_lines = len(cleaned_content.split('\n'))
        lines_removed = original_lines - cleaned_lines
        
        if cleaned_content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            return True, lines_removed
        
        return False, 0
        
    except Exception as e:
        print(f"  ⚠️ Error processing {file_path}: {e}")
        return False, 0

def main():
    """Main execution function"""
    print("🧹 RuleIQ Dead Code Removal Script")
    print("=" * 50)
    
    # Find all Python files
    py_files = list(Path('.').rglob('*.py'))
    
    # Exclude certain directories
    excluded_dirs = {'.venv', '__pycache__', 'node_modules', 'backup_', '.git'}
    py_files = [
        f for f in py_files 
        if not any(excluded in str(f) for excluded in excluded_dirs)
    ]
    
    print(f"📁 Found {len(py_files)} Python files to process")
    
    # Create backup
    backup_dir = backup_files(py_files)
    
    # Process files
    modified_files = []
    total_lines_removed = 0
    
    print("\n🔍 Processing files...")
    for file in py_files:
        modified, lines_removed = clean_file(file)
        if modified:
            modified_files.append((file, lines_removed))
            total_lines_removed += lines_removed
            print(f"  ✓ {file}: {lines_removed} lines removed")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Summary:")
    print(f"  Files modified: {len(modified_files)}")
    print(f"  Total lines removed: {total_lines_removed}")
    print(f"  Backup location: {backup_dir}")
    
    if modified_files:
        print("\n📝 Modified files:")
        for file, lines in sorted(modified_files, key=lambda x: x[1], reverse=True)[:10]:
            print(f"    {file}: {lines} lines")
    
    print("\n✅ Dead code removal complete!")
    print("⚠️  Remember to run tests to ensure everything still works!")
    
    return total_lines_removed

if __name__ == "__main__":
    lines_removed = main()
    exit(0 if lines_removed > 0 else 1)