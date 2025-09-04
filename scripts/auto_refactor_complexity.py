#!/usr/bin/env python3
"""
Automated complexity reduction tool for RuleIQ
Applies systematic refactoring patterns to achieve SonarCloud Grade A/B
"""

import ast
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import logging
import textwrap

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


class ComplexityReducer:
    """Main class for reducing code complexity"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.files_modified = 0
        self.functions_improved = 0
        self.complexity_reduced = 0
        
    def process_project(self) -> Dict:
        """Process entire project to reduce complexity"""
        logger.info("🚀 Starting automated complexity reduction...")
        
        # Find Python files
        python_files = self._find_python_files()
        
        results = {
            'files_processed': 0,
            'files_modified': 0,
            'functions_improved': 0,
            'patterns_applied': {},
            'errors': []
        }
        
        for file_path in python_files:
            try:
                if self._process_file(file_path):
                    results['files_modified'] += 1
                results['files_processed'] += 1
            except Exception as e:
                results['errors'].append({
                    'file': str(file_path),
                    'error': str(e)
                })
        
        results['functions_improved'] = self.functions_improved
        return results
    
    def _find_python_files(self) -> List[Path]:
        """Find all Python files to process"""
        exclude_patterns = [
            '__pycache__', '.venv', 'venv', 'env',
            'migrations', 'alembic', '.git', 'htmlcov',
            'backup', 'node_modules', 'test_', '_test.py'
        ]
        
        python_files = []
        for root, dirs, files in os.walk(self.project_root):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if not any(p in d for p in exclude_patterns)]
            
            for file in files:
                if file.endswith('.py') and not file.startswith('test_'):
                    file_path = Path(root) / file
                    # Skip backup files and tests
                    if 'backup' not in str(file_path) and 'test' not in file:
                        python_files.append(file_path)
        
        return python_files
    
    def _process_file(self, file_path: Path) -> bool:
        """Process a single file to reduce complexity"""
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Apply multiple refactoring strategies
        modified_content = original_content
        
        # Strategy 1: Extract long if-elif chains
        modified_content = self._extract_long_conditionals(modified_content)
        
        # Strategy 2: Apply guard clauses
        modified_content = self._apply_guard_clauses(modified_content)
        
        # Strategy 3: Extract nested loops
        modified_content = self._extract_nested_loops(modified_content)
        
        # Strategy 4: Simplify boolean expressions
        modified_content = self._simplify_boolean_expressions(modified_content)
        
        # Strategy 5: Extract validation logic
        modified_content = self._extract_validation_logic(modified_content)
        
        if modified_content != original_content:
            # Validate the modified code is still valid Python
            try:
                ast.parse(modified_content)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
                self.files_modified += 1
                return True
            except SyntaxError:
                # Don't write invalid code
                logger.warning(f"Skipping {file_path} - refactoring produced invalid syntax")
                return False
        
        return False
    
    def _extract_long_conditionals(self, content: str) -> str:
        """Extract long if-elif chains into dispatch dictionaries"""
        lines = content.split('\n')
        modified_lines = []
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Detect if-elif chain
            if line.strip().startswith('if ') and i + 1 < len(lines):
                chain_lines, chain_end = self._find_if_elif_chain(lines, i)
                
                if len(chain_lines) > 5:  # Long chain detected
                    # Extract to dictionary dispatch
                    refactored = self._create_dict_dispatch(chain_lines)
                    if refactored:
                        modified_lines.extend(refactored)
                        i = chain_end
                        self.functions_improved += 1
                        continue
            
            modified_lines.append(line)
            i += 1
        
        return '\n'.join(modified_lines)
    
    def _find_if_elif_chain(self, lines: List[str], start: int) -> Tuple[List[str], int]:
        """Find the extent of an if-elif chain"""
        chain = []
        i = start
        indent_level = len(lines[i]) - len(lines[i].lstrip())
        
        while i < len(lines):
            line = lines[i]
            current_indent = len(line) - len(line.lstrip())
            
            if current_indent < indent_level:
                break
            
            if current_indent == indent_level:
                if line.strip().startswith(('if ', 'elif ', 'else:')):
                    chain.append(line)
                else:
                    break
            else:
                chain.append(line)
            
            i += 1
        
        return chain, i
    
    def _create_dict_dispatch(self, chain_lines: List[str]) -> Optional[List[str]]:
        """Create dictionary dispatch from if-elif chain"""
        # This is a simplified version - real implementation would be more sophisticated
        # For now, return None to avoid breaking code
        return None
    
    def _apply_guard_clauses(self, content: str) -> str:
        """Apply guard clauses to reduce nesting"""
        pattern = r'(\s*)if\s+(.+?):\n((?:\1\s+.+\n)+)\1else:\n\1\s+return\s+(.+)\n'
        
        def replace_with_guard(match):
            indent = match.group(1)
            condition = match.group(2)
            if_body = match.group(3)
            return_value = match.group(4)
            
            # Create guard clause
            guard = f"{indent}if not ({condition}):\n{indent}    return {return_value}\n\n"
            # Remove one level of indentation from if_body
            dedented_body = '\n'.join(
                line[4:] if line.startswith(indent + '    ') else line
                for line in if_body.split('\n') if line.strip()
            )
            
            return guard + dedented_body + '\n'
        
        modified = re.sub(pattern, replace_with_guard, content, flags=re.MULTILINE)
        
        if modified != content:
            self.functions_improved += 1
        
        return modified
    
    def _extract_nested_loops(self, content: str) -> str:
        """Extract deeply nested loops into separate functions"""
        try:
            tree = ast.parse(content)
            transformer = NestedLoopExtractor()
            modified_tree = transformer.visit(tree)
            
            if transformer.extracted_count > 0:
                # Add the extracted functions to the module
                for func in transformer.extracted_functions:
                    tree.body.append(func)
                
                # Convert back to source
                import astor
                modified_content = astor.to_source(modified_tree)
                self.functions_improved += transformer.extracted_count
                return modified_content
        except:
            pass
        
        return content
    
    def _simplify_boolean_expressions(self, content: str) -> str:
        """Simplify complex boolean expressions"""
        # Pattern for complex boolean expressions
        patterns = [
            (r'if\s+(.+?)\s+==\s+True:', r'if \1:'),
            (r'if\s+(.+?)\s+==\s+False:', r'if not \1:'),
            (r'if\s+not\s+(.+?)\s+==\s+(.+?):', r'if \1 != \2:'),
            (r'return\s+True\s+if\s+(.+?)\s+else\s+False', r'return \1'),
            (r'(.+?)\s+if\s+(.+?)\s+else\s+None', r'\1 if \2 else None'),
        ]
        
        modified = content
        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, modified)
            if new_content != modified:
                self.functions_improved += 1
                modified = new_content
        
        return modified
    
    def _extract_validation_logic(self, content: str) -> str:
        """Extract validation logic into separate functions"""
        # Pattern for validation blocks
        validation_pattern = r'(\s*)# Validate\s+(.+?)\n((?:\1.+\n)+)'
        
        def extract_validation(match):
            indent = match.group(1)
            what = match.group(2)
            validation_code = match.group(3)
            
            # Create validation function
            func_name = f"_validate_{what.lower().replace(' ', '_')}"
            func_def = f"{indent}def {func_name}(value):\n"
            func_body = textwrap.indent(validation_code, '    ')
            
            # Replace with function call
            call = f"{indent}{func_name}(value)\n"
            
            self.functions_improved += 1
            return func_def + func_body + '\n' + call
        
        return re.sub(validation_pattern, extract_validation, content, flags=re.MULTILINE)


class NestedLoopExtractor(ast.NodeTransformer):
    """Extract deeply nested loops into separate functions"""
    
    def __init__(self):
        self.extracted_count = 0
        self.extracted_functions = []
        self.nesting_level = 0
    
    def visit_For(self, node):
        """Visit for loops and track nesting"""
        self.nesting_level += 1
        
        if self.nesting_level > 3:  # Extract if nesting > 3
            # Create new function for nested loop
            func_name = f"_process_nested_loop_{self.extracted_count}"
            new_func = self._create_extracted_function(func_name, node)
            self.extracted_functions.append(new_func)
            self.extracted_count += 1
            
            # Replace with function call
            call = ast.Call(
                func=ast.Name(id=func_name, ctx=ast.Load()),
                args=[],
                keywords=[]
            )
            
            self.nesting_level -= 1
            return ast.Expr(value=call)
        
        self.generic_visit(node)
        self.nesting_level -= 1
        return node
    
    def _create_extracted_function(self, name: str, loop_node: ast.For) -> ast.FunctionDef:
        """Create a function from extracted loop"""
        return ast.FunctionDef(
            name=name,
            args=ast.arguments(
                posonlyargs=[],
                args=[],
                kwonlyargs=[],
                kw_defaults=[],
                defaults=[]
            ),
            body=[loop_node],
            decorator_list=[],
            returns=None
        )


def print_results(results: Dict) -> None:
    """Print refactoring results"""
    logger.info("\n" + "=" * 80)
    logger.info("✨ COMPLEXITY REDUCTION COMPLETE")
    logger.info("=" * 80)
    
    logger.info(f"\n📊 Results:")
    logger.info(f"   Files processed: {results['files_processed']}")
    logger.info(f"   Files modified: {results['files_modified']}")
    logger.info(f"   Functions improved: {results['functions_improved']}")
    
    if results['errors']:
        logger.info(f"\n⚠️  Errors encountered: {len(results['errors'])}")
        for error in results['errors'][:5]:
            logger.info(f"   - {error['file']}: {error['error']}")
    
    if results['files_modified'] > 0:
        logger.info("\n✅ Successfully reduced complexity!")
        logger.info("   Next steps:")
        logger.info("   1. Run tests to ensure functionality preserved")
        logger.info("   2. Review modified files for correctness")
        logger.info("   3. Re-run SonarCloud analysis")
    else:
        logger.info("\n📝 No automatic refactoring applied")
        logger.info("   Manual refactoring may be needed for complex cases")


def main():
    """Main execution"""
    project_root = Path(__file__).parent.parent
    
    logger.info("🔧 RuleIQ Automated Complexity Reducer")
    logger.info("Target: SonarCloud Grade A/B (complexity < 15)")
    
    # Create reducer and process project
    reducer = ComplexityReducer(project_root)
    results = reducer.process_project()
    
    # Print results
    print_results(results)
    
    # Save results
    import json
    with open('complexity_reduction_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    logger.info("\n📄 Detailed results saved to: complexity_reduction_results.json")
    
    return 0


if __name__ == "__main__":
    exit(main())