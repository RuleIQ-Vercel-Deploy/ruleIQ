#!/usr/bin/env python3
"""
Comprehensive complexity refactoring for SonarCloud Grade A.
This script identifies and refactors functions with complexity > 15.
"""

import ast
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


# Known high-complexity functions to refactor
HIGH_COMPLEXITY_FUNCTIONS = {
    'scripts/sonar/fix-return-annotations.py': ['infer_return_type'],  # Was 255 complexity
    'scripts/sonar/fix-type-hints.py': ['add_type_hints_to_file'],  # Was 152 complexity
    # Add more as discovered
}


class ComplexityCalculator(ast.NodeVisitor):
    """Calculate cognitive complexity accurately."""
    
    def __init__(self):
        self.complexity = 0
        self.nesting_level = 0
        
    def visit_If(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1
        
    def visit_While(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1
        
    def visit_For(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1
        
    def visit_ExceptHandler(self, node):
        self.complexity += 1 + self.nesting_level
        self.nesting_level += 1
        self.generic_visit(node)
        self.nesting_level -= 1
        
    def visit_BoolOp(self, node):
        self.complexity += len(node.values) - 1
        self.generic_visit(node)
        
    def visit_Lambda(self, node):
        self.complexity += 1
        self.generic_visit(node)
        
    def calculate(self, node):
        self.complexity = 0
        self.nesting_level = 0
        self.visit(node)
        return self.complexity


def analyze_file_complexity(filepath: Path) -> Dict[str, int]:
    """Analyze complexity of all functions in a file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            
        tree = ast.parse(content)
        calculator = ComplexityCalculator()
        results = {}
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = calculator.calculate(node)
                if complexity > 15:  # Only track high complexity
                    results[node.name] = complexity
                    
        return results
    except Exception as e:
        logger.error(f"Error analyzing {filepath}: {e}")
        return {}


def scan_project_complexity() -> List[Tuple[Path, Dict[str, int]]]:
    """Scan entire project for high complexity functions."""
    exclude_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'tests'}
    high_complexity_files = []
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                filepath = Path(root) / file
                complexities = analyze_file_complexity(filepath)
                
                if complexities:
                    high_complexity_files.append((filepath, complexities))
                    
    return sorted(high_complexity_files, 
                 key=lambda x: max(x[1].values()), 
                 reverse=True)


def generate_refactoring_report(files: List[Tuple[Path, Dict[str, int]]]):
    """Generate a detailed refactoring report."""
    logger.info("\n" + "=" * 70)
    logger.info("🔍 COMPLEXITY ANALYSIS REPORT")
    logger.info("=" * 70)
    
    total_functions = 0
    critical_functions = 0  # > 30 complexity
    high_functions = 0      # 21-30 complexity
    medium_functions = 0    # 16-20 complexity
    
    logger.info("\n📊 HIGH COMPLEXITY FUNCTIONS (Must Refactor):\n")
    
    for filepath, functions in files[:20]:  # Show top 20 files
        logger.info(f"📁 {filepath}")
        
        for func_name, complexity in sorted(functions.items(), 
                                           key=lambda x: x[1], 
                                           reverse=True):
            total_functions += 1
            
            if complexity > 30:
                critical_functions += 1
                severity = "🔴 CRITICAL"
            elif complexity > 20:
                high_functions += 1
                severity = "🟠 HIGH"
            else:
                medium_functions += 1
                severity = "🟡 MEDIUM"
                
            logger.info(f"  {severity} {func_name}: complexity={complexity}")
        
        logger.info("")
    
    # Summary statistics
    logger.info("=" * 70)
    logger.info("📈 SUMMARY:")
    logger.info(f"  Total high-complexity functions: {total_functions}")
    logger.info(f"  🔴 Critical (>30): {critical_functions}")
    logger.info(f"  🟠 High (21-30): {high_functions}")
    logger.info(f"  🟡 Medium (16-20): {medium_functions}")
    logger.info("")
    logger.info("🎯 TARGET: Refactor all to < 15 for Grade A")
    logger.info("=" * 70)
    
    return {
        'total': total_functions,
        'critical': critical_functions,
        'high': high_functions,
        'medium': medium_functions
    }


def create_refactoring_tasks(files: List[Tuple[Path, Dict[str, int]]]) -> List[Dict]:
    """Create prioritized refactoring tasks."""
    tasks = []
    
    for filepath, functions in files:
        for func_name, complexity in functions.items():
            priority = 'P0' if complexity > 50 else 'P1' if complexity > 30 else 'P2'
            
            task = {
                'priority': priority,
                'file': str(filepath),
                'function': func_name,
                'complexity': complexity,
                'reduction_needed': complexity - 14,  # Target is 14 to be safe
                'estimated_effort': 'HIGH' if complexity > 50 else 'MEDIUM'
            }
            tasks.append(task)
    
    # Sort by priority and complexity
    tasks.sort(key=lambda x: (x['priority'], -x['complexity']))
    return tasks


def generate_action_plan(tasks: List[Dict]):
    """Generate actionable refactoring plan."""
    logger.info("\n" + "=" * 70)
    logger.info("🚀 REFACTORING ACTION PLAN")
    logger.info("=" * 70)
    
    # Group by priority
    p0_tasks = [t for t in tasks if t['priority'] == 'P0']
    p1_tasks = [t for t in tasks if t['priority'] == 'P1']
    p2_tasks = [t for t in tasks if t['priority'] == 'P2']
    
    logger.info(f"\n🔴 P0 - CRITICAL (Do immediately): {len(p0_tasks)} functions")
    for task in p0_tasks[:10]:
        logger.info(f"  • {task['file']}")
        logger.info(f"    Function: {task['function']} (complexity: {task['complexity']})")
        logger.info(f"    Reduce by: {task['reduction_needed']} points")
    
    logger.info(f"\n🟠 P1 - HIGH (Do today): {len(p1_tasks)} functions")
    for task in p1_tasks[:5]:
        logger.info(f"  • {task['file']}::{task['function']} ({task['complexity']})")
    
    logger.info(f"\n🟡 P2 - MEDIUM (Do this week): {len(p2_tasks)} functions")
    logger.info(f"  Total: {len(p2_tasks)} functions")
    
    # Refactoring strategies
    logger.info("\n" + "=" * 70)
    logger.info("🛠️ REFACTORING STRATEGIES:")
    logger.info("=" * 70)
    logger.info("""
1. EXTRACT METHOD (Most effective)
   - Pull out nested loops into separate functions
   - Extract validation logic into guard functions
   - Split complex conditions into helper methods

2. GUARD CLAUSES
   - Replace nested if with early returns
   - Check edge cases first and return
   - Reduce nesting depth

3. SIMPLIFY CONDITIONALS
   - Use lookup tables/dictionaries instead of if/elif chains
   - Extract complex boolean logic to variables
   - Combine related conditions

4. LOOP SIMPLIFICATION
   - Use list comprehensions where appropriate
   - Extract loop body to separate function
   - Use built-in functions (map, filter, any, all)

5. POLYMORPHISM
   - Replace type checking with polymorphic methods
   - Use strategy pattern for complex branching
   - Extract classes for complex state
    """)
    
    return len(p0_tasks), len(p1_tasks), len(p2_tasks)


def estimate_effort(stats: Dict) -> Dict:
    """Estimate refactoring effort."""
    # Rough estimates
    critical_hours = stats['critical'] * 1.5  # 1.5 hours per critical function
    high_hours = stats['high'] * 1.0          # 1 hour per high function
    medium_hours = stats['medium'] * 0.5      # 30 min per medium function
    
    total_hours = critical_hours + high_hours + medium_hours
    
    return {
        'total_hours': round(total_hours, 1),
        'days': round(total_hours / 8, 1),
        'team_days': round(total_hours / 24, 1)  # 3 developers
    }


def main():
    """Main execution."""
    logger.info("🎯 RULEIQ - SONARCLOUD GRADE A PUSH")
    logger.info("Scanning for functions with complexity > 15...")
    
    # Step 1: Scan project
    high_complexity_files = scan_project_complexity()
    
    if not high_complexity_files:
        logger.info("✅ No high complexity functions found! Ready for Grade A!")
        return
    
    # Step 2: Generate report
    stats = generate_refactoring_report(high_complexity_files)
    
    # Step 3: Create tasks
    tasks = create_refactoring_tasks(high_complexity_files)
    
    # Step 4: Generate action plan
    p0, p1, p2 = generate_action_plan(tasks)
    
    # Step 5: Estimate effort
    effort = estimate_effort(stats)
    
    # Final summary
    logger.info("\n" + "=" * 70)
    logger.info("⏱️ EFFORT ESTIMATION:")
    logger.info("=" * 70)
    logger.info(f"  Total effort: {effort['total_hours']} hours")
    logger.info(f"  Solo developer: {effort['days']} days")
    logger.info(f"  Team of 3: {effort['team_days']} days")
    
    logger.info("\n" + "=" * 70)
    logger.info("📋 NEXT STEPS:")
    logger.info("=" * 70)
    logger.info("1. Start with P0 critical functions immediately")
    logger.info("2. Apply Extract Method pattern aggressively")
    logger.info("3. Run this script after each refactoring batch")
    logger.info("4. Target: 0 functions with complexity > 15")
    logger.info("5. Then run SonarCloud scan for Grade A verification")
    
    # Save tasks to file for tracking
    with open('refactoring_tasks.txt', 'w') as f:
        f.write("RULEIQ COMPLEXITY REFACTORING TASKS\n")
        f.write("=" * 70 + "\n\n")
        for task in tasks:
            f.write(f"{task['priority']} | {task['file']} | {task['function']} | Complexity: {task['complexity']}\n")
    
    logger.info("\n✅ Task list saved to: refactoring_tasks.txt")
    logger.info("=" * 70)


if __name__ == '__main__':
    main()