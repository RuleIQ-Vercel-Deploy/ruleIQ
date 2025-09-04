"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Script to apply cost tracking decorators to all LangGraph nodes.
This ensures comprehensive cost tracking across the workflow.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple
NODE_CONFIGS = {'langgraph_agent/nodes/reporting_nodes.py': [(
    'generate_report_node', 'gpt-4'), ('reporting_node', 'gpt-4')],
    'langgraph_agent/nodes/reporting_nodes_real.py': [(
    'generate_compliance_report', 'gpt-4'), ('compliance_reporting_node',
    'gpt-4')], 'langgraph_agent/nodes/rag_node.py': [('rag_node', 'gpt-4'),
    ('retrieve_documents', 'text-embedding-ada-002')],
    'langgraph_agent/nodes/task_scheduler_node.py': [('task_scheduler_node',
    None), ('schedule_task', None)]}


def add_import_if_missing(file_path: Path) ->bool:
    """Add cost tracking import if not already present."""
    content = file_path.read_text()
    if ('from langgraph_agent.utils.cost_tracking import track_node_cost' in
        content):
        logger.info('  ✓ Import already exists in %s' % file_path.name)
        return False
    import_pattern = '(from langgraph.*?import.*?\\n)'
    matches = list(re.finditer(import_pattern, content))
    if matches:
        last_match = matches[-1]
        insert_pos = last_match.end()
        new_content = (content[:insert_pos] +
            """from langgraph_agent.utils.cost_tracking import track_node_cost
"""
             + content[insert_pos:])
    else:
        import_end = content.find('\n\n')
        if import_end > 0:
            new_content = (content[:import_end] +
                """
from langgraph_agent.utils.cost_tracking import track_node_cost
"""
                 + content[import_end:])
        else:
            new_content = (
                'from langgraph_agent.utils.cost_tracking import track_node_cost\n\n'
                 + content)
    file_path.write_text(new_content)
    logger.info('  ✓ Added import to %s' % file_path.name)
    return True


def add_decorator_to_function(file_path: Path, function_name: str,
    model_name: str=None) ->bool:
    """Add cost tracking decorator to a specific function."""
    content = file_path.read_text()
    pattern = f'@track_node_cost.*?\\n.*?def {function_name}\\('
    if re.search(pattern, content, re.DOTALL):
        logger.info('    ✓ Decorator already exists for %s' % function_name)
        return False
    func_pattern = f'(async def|def) {function_name}\\('
    match = re.search(func_pattern, content)
    if not match:
        logger.info('    ✗ Function %s not found' % function_name)
        return False
    func_start = match.start()
    lines_before = content[:func_start].split('\n')
    decorator_line = len(lines_before) - 1
    if decorator_line > 0 and lines_before[-2].strip().startswith('@'):
        indent = len(lines_before[-2]) - len(lines_before[-2].lstrip())
        decorator_text = ' ' * indent + '@track_node_cost('
        if model_name:
            decorator_text += (
                f'node_name="{function_name}", model_name="{model_name}"')
        else:
            decorator_text += (
                f'node_name="{function_name}", track_tokens=False')
        decorator_text += ')\n'
        new_content = content[:func_start] + decorator_text + content[
            func_start:]
    else:
        indent = len(match.group(0)) - len(match.group(0).lstrip())
        decorator_text = '@track_node_cost('
        if model_name:
            decorator_text += (
                f'node_name="{function_name}", model_name="{model_name}"')
        else:
            decorator_text += (
                f'node_name="{function_name}", track_tokens=False')
        decorator_text += ')\n' + ' ' * indent
        new_content = content[:func_start] + decorator_text + content[
            func_start:]
    file_path.write_text(new_content)
    logger.info('    ✓ Added decorator to %s' % function_name)
    return True


def main() ->None:
    """Apply cost tracking to all configured nodes."""
    logger.info('Applying cost tracking to LangGraph nodes...')
    logger.info('=' * 50)
    project_root = Path(__file__).parent.parent
    for file_path_str, functions in NODE_CONFIGS.items():
        file_path = project_root / file_path_str
        if not file_path.exists():
            logger.info('\n✗ File not found: %s' % file_path_str)
            continue
        logger.info('\nProcessing %s:' % file_path.name)
        add_import_if_missing(file_path)
        for func_name, model_name in functions:
            add_decorator_to_function(file_path, func_name, model_name)
    logger.info('\n' + '=' * 50)
    logger.info('✓ Cost tracking application complete!')
    utils_init = project_root / 'langgraph_agent/utils/__init__.py'
    if not utils_init.exists():
        utils_init.parent.mkdir(parents=True, exist_ok=True)
        utils_init.write_text('"""Utilities for LangGraph agent."""\n')
        logger.info('✓ Created %s' % utils_init)


if __name__ == '__main__':
    main()
