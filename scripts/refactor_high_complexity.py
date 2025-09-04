#!/usr/bin/env python3
"""
Automated refactoring tool to reduce cognitive complexity in Python code
Targets functions with complexity > 15 for SonarCloud Grade A/B
"""

import ast
import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import json
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class ComplexityAnalyzer:
    """Analyzes and reports on code complexity"""
    
    def __init__(self, threshold: int = 15):
        self.threshold = threshold
        self.complex_functions = []
        
    def calculate_cognitive_complexity(self, node: ast.AST) -> int:
        """Calculate cognitive complexity of a function node"""
        calculator = ComplexityCalculator()
        calculator.visit(node)
        return calculator.complexity
    
    def analyze_file(self, file_path: Path) -> List[Dict]:
        """Analyze a single file for complex functions"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content, filename=str(file_path))
            issues = []
            
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                    
                complexity = self.calculate_cognitive_complexity(node)
                if complexity > self.threshold:
                    issues.append({
                        'file': str(file_path),
                        'function': node.name,
                        'line': node.lineno,
                        'complexity': complexity,
                        'reduction_needed': complexity - self.threshold
                    })
            
            return issues
            
        except (SyntaxError, UnicodeDecodeError) as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return []
    
    def find_complex_functions(self, project_root: Path) -> List[Dict]:
        """Find all functions exceeding complexity threshold"""
        exclude_dirs = {
            '__pycache__', '.venv', 'venv', 'env',
            'migrations', 'alembic', '.git', 'htmlcov',
            'backup', 'backup_*', 'node_modules'
        }
        
        all_issues = []
        
        for root, dirs, files in os.walk(project_root):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('backup')]
            
            for file in files:
                if not file.endswith('.py'):
                    continue
                    
                file_path = Path(root) / file
                issues = self.analyze_file(file_path)
                all_issues.extend(issues)
        
        # Sort by complexity (highest first)
        all_issues.sort(key=lambda x: x['complexity'], reverse=True)
        return all_issues


class ComplexityCalculator(ast.NodeVisitor):
    """Calculate cognitive complexity using visitor pattern"""
    
    def __init__(self):
        self.complexity = 0
        self.nesting_level = 0
    
    def _increment_complexity(self, increment: int = 1):
        """Increment complexity with nesting bonus"""
        self.complexity += increment + self.nesting_level
    
    def visit_If(self, node):
        """Visit If node - adds complexity"""
        self._increment_complexity()
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1
    
    def visit_While(self, node):
        """Visit While loop - adds complexity"""
        self._increment_complexity()
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1
    
    def visit_For(self, node):
        """Visit For loop - adds complexity"""
        self._increment_complexity()
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1
    
    def visit_ExceptHandler(self, node):
        """Visit exception handler - adds complexity"""
        self._increment_complexity()
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1
    
    def visit_With(self, node):
        """Visit With statement - adds complexity"""
        self._increment_complexity()
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1
    
    def visit_BoolOp(self, node):
        """Visit boolean operation - adds complexity for each operator"""
        self.complexity += len(node.values) - 1
        self.generic_visit(node)
    
    def visit_Lambda(self, node):
        """Visit lambda - adds complexity"""
        self._increment_complexity()
        self.generic_visit(node)
    
    def visit_ListComp(self, node):
        """Visit list comprehension - adds complexity"""
        self._increment_complexity()
        self.generic_visit(node)
    
    def visit_DictComp(self, node):
        """Visit dict comprehension - adds complexity"""
        self._increment_complexity()
        self.generic_visit(node)
    
    def visit_SetComp(self, node):
        """Visit set comprehension - adds complexity"""
        self._increment_complexity()
        self.generic_visit(node)


class RefactoringRecommender:
    """Provides refactoring recommendations for complex functions"""
    
    def __init__(self):
        self.recommendations = []
    
    def generate_recommendations(self, issues: List[Dict]) -> Dict[str, List[str]]:
        """Generate refactoring recommendations for each complex function"""
        recommendations = {}
        
        for issue in issues:
            file_path = issue['file']
            func_name = issue['function']
            complexity = issue['complexity']
            
            key = f"{file_path}:{func_name}"
            recommendations[key] = self._get_recommendations_for_complexity(complexity)
        
        return recommendations
    
    def _get_recommendations_for_complexity(self, complexity: int) -> List[str]:
        """Get specific recommendations based on complexity level"""
        recommendations = []
        
        if complexity > 30:
            recommendations.extend([
                "🔴 CRITICAL: Split this function into multiple smaller functions",
                "Consider using a class to encapsulate related functionality",
                "Extract complex conditional logic into separate methods"
            ])
        elif complexity > 20:
            recommendations.extend([
                "🟠 HIGH: Extract nested loops into separate functions",
                "Use early returns to reduce nesting levels",
                "Consider using guard clauses at the beginning"
            ])
        else:  # complexity > 15
            recommendations.extend([
                "🟡 MEDIUM: Simplify conditional logic",
                "Replace nested if-else with dictionary dispatch or strategy pattern",
                "Extract validation logic into separate functions"
            ])
        
        # Common recommendations
        recommendations.extend([
            "Use more descriptive variable names",
            "Add type hints for better clarity",
            "Consider breaking down long chains of operations"
        ])
        
        return recommendations


class AutoRefactorer:
    """Automatically apply simple refactoring patterns"""
    
    def __init__(self):
        self.refactoring_count = 0
    
    def apply_guard_clauses(self, file_path: Path) -> bool:
        """Apply guard clause pattern to reduce nesting"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            transformer = GuardClauseTransformer()
            modified_tree = transformer.visit(tree)
            
            if transformer.changes_made:
                # Convert back to source code
                import astor
                new_content = astor.to_source(modified_tree)
                
                # Write back
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                self.refactoring_count += transformer.changes_made
                return True
                
        except Exception as e:
            logger.error(f"Error refactoring {file_path}: {e}")
        
        return False


class GuardClauseTransformer(ast.NodeTransformer):
    """Transform nested if statements to use guard clauses"""
    
    def __init__(self):
        self.changes_made = 0
    
    def visit_FunctionDef(self, node):
        """Visit function definition and apply guard clause pattern"""
        # Look for pattern: if condition: large_block else: return/raise
        new_body = []
        
        for stmt in node.body:
            if self._is_invertible_if(stmt):
                # Convert to guard clause
                guard = self._create_guard_clause(stmt)
                new_body.extend(guard)
                self.changes_made += 1
            else:
                new_body.append(stmt)
        
        node.body = new_body
        return node
    
    def _is_invertible_if(self, node) -> bool:
        """Check if an if statement can be converted to guard clause"""
        if not isinstance(node, ast.If):
            return False
        
        # Check if else clause is simple (return or raise)
        if not node.orelse:
            return False
        
        if len(node.orelse) == 1:
            else_stmt = node.orelse[0]
            return isinstance(else_stmt, (ast.Return, ast.Raise))
        
        return False
    
    def _create_guard_clause(self, if_node: ast.If) -> List[ast.stmt]:
        """Create guard clause from if statement"""
        # Invert condition
        inverted_condition = ast.UnaryOp(op=ast.Not(), operand=if_node.test)
        
        # Create guard clause
        guard = ast.If(
            test=inverted_condition,
            body=if_node.orelse,
            orelse=[]
        )
        
        # Return guard followed by original if body
        return [guard] + if_node.body


def generate_quality_report(issues: List[Dict], recommendations: Dict) -> None:
    """Generate detailed quality report"""
    report = {
        'summary': {
            'total_complex_functions': len(issues),
            'files_affected': len(set(i['file'] for i in issues)),
            'total_complexity_reduction_needed': sum(i['reduction_needed'] for i in issues),
            'critical_functions': len([i for i in issues if i['complexity'] > 30]),
            'high_functions': len([i for i in issues if 20 < i['complexity'] <= 30]),
            'medium_functions': len([i for i in issues if 15 < i['complexity'] <= 20])
        },
        'top_10_complex_functions': issues[:10],
        'recommendations': recommendations
    }
    
    # Save report
    with open('complexity_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    logger.info("\n" + "=" * 80)
    logger.info("📊 CODE COMPLEXITY ANALYSIS REPORT")
    logger.info("=" * 80)
    
    logger.info(f"\n🎯 Functions exceeding complexity threshold (>15):")
    logger.info(f"   Total: {report['summary']['total_complex_functions']}")
    logger.info(f"   🔴 Critical (>30): {report['summary']['critical_functions']}")
    logger.info(f"   🟠 High (21-30): {report['summary']['high_functions']}")
    logger.info(f"   🟡 Medium (16-20): {report['summary']['medium_functions']}")
    
    logger.info(f"\n📁 Files affected: {report['summary']['files_affected']}")
    logger.info(f"📉 Total complexity reduction needed: {report['summary']['total_complexity_reduction_needed']}")
    
    if issues:
        logger.info("\n🔝 Top 5 Most Complex Functions:")
        for i, issue in enumerate(issues[:5], 1):
            file_name = Path(issue['file']).name
            logger.info(f"   {i}. {file_name}:{issue['function']} - Complexity: {issue['complexity']}")
    
    # Estimate quality grade
    grade = estimate_quality_grade(report['summary'])
    logger.info(f"\n🎯 Estimated Quality Grade: {grade}")
    
    if grade in ['A', 'B']:
        logger.info("✅ Code quality meets target!")
    else:
        logger.info("⚠️  Refactoring needed to achieve Grade A/B")


def estimate_quality_grade(summary: Dict) -> str:
    """Estimate SonarCloud quality grade based on complexity issues"""
    critical = summary['critical_functions']
    high = summary['high_functions']
    total = summary['total_complex_functions']
    
    if critical == 0 and total < 50:
        return 'A'
    elif critical < 5 and total < 100:
        return 'B'
    elif critical < 10 and total < 200:
        return 'C'
    elif critical < 20 and total < 400:
        return 'D'
    else:
        return 'E'


def main():
    """Main execution function"""
    project_root = Path(__file__).parent.parent
    
    logger.info("🔍 Analyzing code complexity in RuleIQ project...")
    
    # Analyze complexity
    analyzer = ComplexityAnalyzer(threshold=15)
    issues = analyzer.find_complex_functions(project_root)
    
    if not issues:
        logger.info("✅ No functions exceed complexity threshold!")
        return 0
    
    # Generate recommendations
    recommender = RefactoringRecommender()
    recommendations = recommender.generate_recommendations(issues)
    
    # Generate report
    generate_quality_report(issues, recommendations)
    
    # Save detailed results
    logger.info("\n📄 Detailed report saved to: complexity_report.json")
    
    # Provide actionable next steps
    logger.info("\n🚀 RECOMMENDED ACTIONS:")
    logger.info("1. Start with the most complex functions (see report)")
    logger.info("2. Apply guard clauses to reduce nesting")
    logger.info("3. Extract complex logic into smaller functions")
    logger.info("4. Use early returns to simplify control flow")
    logger.info("5. Consider using design patterns for complex conditionals")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())