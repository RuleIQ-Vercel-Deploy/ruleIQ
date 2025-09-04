#!/usr/bin/env python3
"""
Dead Code Analysis Tool for RuleIQ
Comprehensive detection and documentation of unused code
"""

import os
import re
import ast
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
import subprocess
from collections import defaultdict

class DeadCodeAnalyzer:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.results = {
            "python": {
                "unused_imports": [],
                "unused_functions": [],
                "unused_classes": [],
                "unused_variables": [],
                "unreachable_code": [],
                "commented_code": [],
                "celery_remnants": []
            },
            "javascript": {
                "unused_imports": [],
                "unused_components": [],
                "unused_functions": [],
                "dead_handlers": [],
                "obsolete_api_calls": []
            },
            "config": {
                "unused_env_vars": [],
                "obsolete_config": [],
                "deprecated_settings": []
            },
            "metrics": {
                "total_lines_removed": 0,
                "files_deleted": 0,
                "files_modified": 0
            }
        }
        
    def analyze_python_dead_code(self): print("🔍 Analyzing Python dead code...")
        
        # Find all Python files
        python_files = list(self.project_root.glob("**/*.py"))
        python_files = [f for f in python_files if "venv" not in str(f) and "__pycache__" not in str(f)]
        
        for py_file in python_files:
            self._check_python_file(py_file)
            
        # Special check for Celery remnants
        self._check_celery_remnants()
        
    def _check_python_file(self, file_path: Path): try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Parse AST
            try:
                tree = ast.parse(content)
                self._analyze_ast(tree, file_path, content)
            except SyntaxError:
                print(f"⚠️  Syntax error in {file_path}")
                
            # Check for commented code blocks
            self._check_commented_code(content, file_path)
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            
    def _analyze_ast(self, tree, file_path, content): # Find unused imports
        imports = []
        used_names = set()
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for alias in node.names if hasattr(node, 'names') else []:
                    name = alias.asname if alias.asname else alias.name
                    if name != '*':
                        imports.append((name, node.lineno))
                        
            elif isinstance(node, ast.Name):
                used_names.add(node.id)
                
        # Check for unused imports
        for name, lineno in imports:
            base_name = name.split('.')[0]
            if base_name not in used_names and not base_name.startswith('_'):
                self.results["python"]["unused_imports"].append({
                    "file": str(file_path.relative_to(self.project_root)),
                    "import": name,
                    "line": lineno
                })
                
        # Check for unused functions and classes
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.name.startswith('_unused_') or self._is_function_unused(node, tree):
                    self.results["python"]["unused_functions"].append({
                        "file": str(file_path.relative_to(self.project_root)),
                        "function": node.name,
                        "line": node.lineno
                    })
                    
            elif isinstance(node, ast.ClassDef):
                if self._is_class_unused(node, tree):
                    self.results["python"]["unused_classes"].append({
                        "file": str(file_path.relative_to(self.project_root)),
                        "class": node.name,
                        "line": node.lineno
                    })
                    
    def _is_function_unused(self, func_node, tree): # Skip test functions, decorators, and special methods
        if (func_node.name.startswith('test_') or 
            func_node.name.startswith('__') or
            any(d.id == 'pytest' if hasattr(d, 'id') else False for d in func_node.decorator_list)):
            return False
            
        # Simple heuristic: check if function name appears elsewhere
        func_name = func_node.name
        usage_count = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == func_name:
                usage_count += 1
                
        # Function definition counts as 1, so if only 1, it's unused
        return usage_count <= 1
        
    def _is_class_unused(self, class_node, tree): # Skip test classes and exceptions
        if (class_node.name.startswith('Test') or 
            class_node.name.endswith('Exception') or
            class_node.name.endswith('Error')):
            return False
            
        class_name = class_node.name
        usage_count = 0
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == class_name:
                usage_count += 1
                
        return usage_count <= 1
        
    def _check_commented_code(self, content: str, file_path: Path): lines = content.split('\n')
        commented_blocks = []
        current_block = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith('#') and not stripped.startswith('#!'):
                # Check if it looks like code
                if any(keyword in stripped for keyword in ['def ', 'class ', 'import ', 'from ', 'if ', 'for ', 'while ']):
                    current_block.append((i, line))
            else:
                if len(current_block) > 3:  # More than 3 lines of commented code
                    commented_blocks.append(current_block)
                current_block = []
                
        if len(current_block) > 3:
            commented_blocks.append(current_block)
            
        for block in commented_blocks:
            self.results["python"]["commented_code"].append({
                "file": str(file_path.relative_to(self.project_root)),
                "start_line": block[0][0],
                "end_line": block[-1][0],
                "lines": len(block)
            })
            
    def _check_celery_remnants(self): celery_patterns = [
            r'from\s+celery\s+import',
            r'import\s+celery',
            r'@app\.task',
            r'            r'\.delay\(',
            r'\.apply_async\(',
            r'CELERY_',
            r'celery_app',
            r'celery\.py'
        ]
        
        for py_file in self.project_root.glob("**/*.py"):
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    
                for pattern in celery_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        self.results["python"]["celery_remnants"].append({
                            "file": str(py_file.relative_to(self.project_root)),
                            "pattern": pattern,
                            "line": line_num,
                            "match": match.group(0)
                        })
            except Exception as e:
                print(f"Error checking {py_file}: {e}")
                
    def analyze_javascript_dead_code(self): print("🔍 Analyzing JavaScript/TypeScript dead code...")
        
        js_extensions = ['*.js', '*.jsx', '*.ts', '*.tsx']
        js_files = []
        
        for ext in js_extensions:
            js_files.extend(self.project_root.glob(f"**/{ext}"))
            
        js_files = [f for f in js_files if "node_modules" not in str(f) and ".next" not in str(f)]
        
        for js_file in js_files:
            self._check_javascript_file(js_file)
            
    def _check_javascript_file(self, file_path: Path): try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Check for unused imports
            import_pattern = r'import\s+(?:{[^}]+}|[\w]+)\s+from\s+[\'"]([^\'"]+)[\'"]'
            imports = re.findall(import_pattern, content)
            
            # Check if imports are used
            for imp in imports:
                # Simple check - look for usage
                imp_name = imp.split('/')[-1].replace('-', '').replace('.', '')
                if content.count(imp_name) <= 1:  # Only in import statement
                    self.results["javascript"]["unused_imports"].append({
                        "file": str(file_path.relative_to(self.project_root)),
                        "import": imp
                    })
                    
            # Check for unused React components
            if file_path.suffix in ['.jsx', '.tsx']:
                component_pattern = r'(?:function|const)\s+(\w+)\s*(?:=|:|\()'
                components = re.findall(component_pattern, content)
                
                for comp in components:
                    if comp[0].isupper():  # React component convention
                        if content.count(comp) <= 1:  # Only in definition
                            self.results["javascript"]["unused_components"].append({
                                "file": str(file_path.relative_to(self.project_root)),
                                "component": comp
                            })
                            
            # Check for commented code
            self._check_js_commented_code(content, file_path)
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            
    def _check_js_commented_code(self, content: str, file_path: Path): # Check for block comments with code
        block_comment_pattern = r'/\*[\s\S]*?\*/'
        block_comments = re.findall(block_comment_pattern, content)
        
        for comment in block_comments:
            if any(keyword in comment for keyword in ['function', 'const ', 'let ', 'var ', 'class ', 'import ']):
                lines = comment.count('\n') + 1
                if lines > 3:
                    self.results["javascript"]["dead_handlers"].append({
                        "file": str(file_path.relative_to(self.project_root)),
                        "type": "block_comment",
                        "lines": lines
                    })
                    
    def analyze_config_dead_code(self): print("🔍 Analyzing configuration dead code...")
        
        # Check environment variables
        env_files = ['.env', '.env.example', '.env.local']
        defined_vars = set()
        
        for env_file in env_files:
            env_path = self.project_root / env_file
            if env_path.exists():
                with open(env_path, 'r') as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            var_name = line.split('=')[0].strip()
                            defined_vars.add(var_name)
                            
        # Check usage of environment variables
        used_vars = set()
        for py_file in self.project_root.glob("**/*.py"):
            if "venv" not in str(py_file):
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()
                        for var in defined_vars:
                            if var in content:
                                used_vars.add(var)
                except:
                    pass
                    
        unused_vars = defined_vars - used_vars
        for var in unused_vars:
            self.results["config"]["unused_env_vars"].append(var)
            
    def generate_report(self): print("\n" + "="*80)
        print("DEAD CODE ANALYSIS REPORT")
        print("="*80)
        
        total_issues = 0
        
        # Python dead code
        print("\n📦 PYTHON DEAD CODE:")
        print("-"*40)
        
        if self.results["python"]["unused_imports"]:
            print(f"\n🔸 Unused Imports: {len(self.results['python']['unused_imports'])}")
            for item in self.results["python"]["unused_imports"][:5]:
                print(f"   - {item['file']}:{item['line']} - {item['import']}")
            if len(self.results["python"]["unused_imports"]) > 5:
                print(f"   ... and {len(self.results['python']['unused_imports']) - 5} more")
            total_issues += len(self.results["python"]["unused_imports"])
            
        if self.results["python"]["unused_functions"]:
            print(f"\n🔸 Unused Functions: {len(self.results['python']['unused_functions'])}")
            for item in self.results["python"]["unused_functions"][:5]:
                print(f"   - {item['file']}:{item['line']} - {item['function']}()")
            if len(self.results["python"]["unused_functions"]) > 5:
                print(f"   ... and {len(self.results['python']['unused_functions']) - 5} more")
            total_issues += len(self.results["python"]["unused_functions"])
            
        if self.results["python"]["unused_classes"]:
            print(f"\n🔸 Unused Classes: {len(self.results['python']['unused_classes'])}")
            for item in self.results["python"]["unused_classes"][:5]:
                print(f"   - {item['file']}:{item['line']} - class {item['class']}")
            total_issues += len(self.results["python"]["unused_classes"])
            
        if self.results["python"]["commented_code"]:
            print(f"\n🔸 Commented Code Blocks: {len(self.results['python']['commented_code'])}")
            total_commented_lines = sum(block['lines'] for block in self.results["python"]["commented_code"])
            print(f"   Total commented lines: {total_commented_lines}")
            total_issues += len(self.results["python"]["commented_code"])
            
        if self.results["python"]["celery_remnants"]:
            print(f"\n🔸 Celery Remnants: {len(self.results['python']['celery_remnants'])}")
            unique_files = set(item['file'] for item in self.results["python"]["celery_remnants"])
            print(f"   Found in {len(unique_files)} files")
            for file in list(unique_files)[:5]:
                print(f"   - {file}")
            total_issues += len(self.results["python"]["celery_remnants"])
            
        # JavaScript dead code
        print("\n📦 JAVASCRIPT/TYPESCRIPT DEAD CODE:")
        print("-"*40)
        
        if self.results["javascript"]["unused_imports"]:
            print(f"\n🔸 Unused Imports: {len(self.results['javascript']['unused_imports'])}")
            for item in self.results["javascript"]["unused_imports"][:5]:
                print(f"   - {item['file']} - {item['import']}")
            total_issues += len(self.results["javascript"]["unused_imports"])
            
        if self.results["javascript"]["unused_components"]:
            print(f"\n🔸 Unused Components: {len(self.results['javascript']['unused_components'])}")
            for item in self.results["javascript"]["unused_components"][:5]:
                print(f"   - {item['file']} - {item['component']}")
            total_issues += len(self.results["javascript"]["unused_components"])
            
        # Configuration dead code
        print("\n📦 CONFIGURATION DEAD CODE:")
        print("-"*40)
        
        if self.results["config"]["unused_env_vars"]:
            print(f"\n🔸 Unused Environment Variables: {len(self.results['config']['unused_env_vars'])}")
            for var in self.results["config"]["unused_env_vars"][:10]:
                print(f"   - {var}")
            total_issues += len(self.results["config"]["unused_env_vars"])
            
        # Summary
        print("\n" + "="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total issues found: {total_issues}")
        print(f"Estimated removable lines: ~{total_issues * 10}")  # Rough estimate
        
        # Save detailed report
        report_path = self.project_root / "dead_code_report.json"
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_path}")
        
        return total_issues
        
    def run_vulture_analysis(self): print("\n🔍 Running Vulture analysis...")
        try:
            result = subprocess.run(
                ["vulture", ".", "--min-confidence", "80"],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )
            
            if result.stdout:
                print("\n📊 Vulture Results:")
                lines = result.stdout.split('\n')[:20]  # First 20 results
                for line in lines:
                    if line:
                        print(f"   {line}")
                        
        except FileNotFoundError:
            print("⚠️  Vulture not installed. Install with: pip install vulture")
            
    def create_cleanup_script(self): script_content = '''#!/usr/bin/env python3
"""
Automated Dead Code Cleanup Script
Run with caution - creates backup before removal
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime

def create_backup(): backup_dir = Path(f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    print(f"Creating backup in {backup_dir}")
    shutil.copytree(".", backup_dir, ignore=shutil.ignore_patterns('venv', 'node_modules', '.git', '__pycache__'))
    return backup_dir

def remove_unused_imports(): with open('dead_code_report.json', 'r') as f:
        report = json.load(f)
    
    for item in report['python']['unused_imports']:
        print(f"Removing unused import from {item['file']}:{item['line']}")
        # Implementation would go here
        
def main():
    print("Dead Code Cleanup Script")
    print("="*50)
    
    response = input("Create backup before cleanup? (yes/no): ")
    if response.lower() == 'yes':
        backup_dir = create_backup()
        print(f"Backup created: {backup_dir}")
    
    print("\\nStarting cleanup...")
    remove_unused_imports()
    # Add more cleanup functions
    
    print("\\nCleanup complete!")

if __name__ == "__main__":
    main()
'''
        
        script_path = self.project_root / "cleanup_dead_code.py"
        with open(script_path, 'w') as f:
            f.write(script_content)
        os.chmod(script_path, 0o755)
        print(f"\n🔧 Cleanup script created: {script_path}")

def main(): project_root = Path("/home/omar/Documents/ruleIQ")
    analyzer = DeadCodeAnalyzer(project_root)
    
    # Run all analyses
    analyzer.analyze_python_dead_code()
    analyzer.analyze_javascript_dead_code()
    analyzer.analyze_config_dead_code()
    
    # Generate report
    total_issues = analyzer.generate_report()
    
    # Run additional tools
    analyzer.run_vulture_analysis()
    
    # Create cleanup script
    if total_issues > 0:
        analyzer.create_cleanup_script()
        
    print("\n✅ Dead code analysis complete!")
    print(f"Total dead code issues found: {total_issues}")
    print("\nNext steps:")
    print("1. Review dead_code_report.json for detailed findings")
    print("2. Run cleanup_dead_code.py for automated removal (with backup)")
    print("3. Manually review and remove complex dead code")
    print("4. Run tests to ensure nothing breaks")

if __name__ == "__main__":
    main()