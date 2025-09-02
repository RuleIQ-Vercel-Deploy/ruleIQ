#!/usr/bin/env python3
"""
Script to apply cost tracking decorators to all LangGraph nodes.
This ensures comprehensive cost tracking across the workflow.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# Define nodes that need cost tracking and their AI models
NODE_CONFIGS = {
    "langgraph_agent/nodes/reporting_nodes.py": [
        ("generate_report_node", "gpt-4"),
        ("reporting_node", "gpt-4"),
    ],
    "langgraph_agent/nodes/reporting_nodes_real.py": [
        ("generate_compliance_report", "gpt-4"),
        ("compliance_reporting_node", "gpt-4"),
    ],
    "langgraph_agent/nodes/rag_node.py": [
        ("rag_node", "gpt-4"),
        ("retrieve_documents", "text-embedding-ada-002"),
    ],
    "langgraph_agent/nodes/task_scheduler_node.py": [
        ("task_scheduler_node", None),  # No AI model used
        ("schedule_task", None),
    ],
}


def add_import_if_missing(file_path: Path) -> bool:
    """Add cost tracking import if not already present."""
    content = file_path.read_text()

    # Check if import already exists
    if "from langgraph_agent.utils.cost_tracking import track_node_cost" in content:
        print(f"  ✓ Import already exists in {file_path.name}")
        return False

    # Find the best place to add the import (after other langgraph imports)
    import_pattern = r"(from langgraph.*?import.*?\n)"
    matches = list(re.finditer(import_pattern, content))

    if matches:
        # Add after the last langgraph import
        last_match = matches[-1]
        insert_pos = last_match.end()
        new_content = (
            content[:insert_pos]
            + "from langgraph_agent.utils.cost_tracking import track_node_cost\n"
            + content[insert_pos:]
        )
    else:
        # Add after other imports
        import_end = content.find("\n\n")
        if import_end > 0:
            new_content = (
                content[:import_end]
                + "\nfrom langgraph_agent.utils.cost_tracking import track_node_cost\n"
                + content[import_end:]
            )
        else:
            # Add at the beginning
            new_content = (
                "from langgraph_agent.utils.cost_tracking import track_node_cost\n\n"
                + content
            )

    file_path.write_text(new_content)
    print(f"  ✓ Added import to {file_path.name}")
    return True


def add_decorator_to_function(
    file_path: Path, function_name: str, model_name: str = None
) -> bool:
    """Add cost tracking decorator to a specific function."""
    content = file_path.read_text()

    # Check if decorator already exists
    pattern = rf"@track_node_cost.*?\n.*?def {function_name}\("
    if re.search(pattern, content, re.DOTALL):
        print(f"    ✓ Decorator already exists for {function_name}")
        return False

    # Find the function definition
    func_pattern = rf"(async def|def) {function_name}\("
    match = re.search(func_pattern, content)

    if not match:
        print(f"    ✗ Function {function_name} not found")
        return False

    # Check if there are existing decorators
    func_start = match.start()

    # Look backwards for decorators
    lines_before = content[:func_start].split("\n")
    decorator_line = len(lines_before) - 1

    # Check if the previous line is a decorator
    if decorator_line > 0 and lines_before[-2].strip().startswith("@"):
        # Add after existing decorators
        indent = len(lines_before[-2]) - len(lines_before[-2].lstrip())
        decorator_text = " " * indent + "@track_node_cost("

        if model_name:
            decorator_text += f'node_name="{function_name}", model_name="{model_name}"'
        else:
            decorator_text += f'node_name="{function_name}", track_tokens=False'

        decorator_text += ")\n"

        # Insert before the function definition
        new_content = content[:func_start] + decorator_text + content[func_start:]
    else:
        # Add as the first decorator
        indent = len(match.group(0)) - len(match.group(0).lstrip())
        decorator_text = "@track_node_cost("

        if model_name:
            decorator_text += f'node_name="{function_name}", model_name="{model_name}"'
        else:
            decorator_text += f'node_name="{function_name}", track_tokens=False'

        decorator_text += ")\n" + " " * indent

        # Insert before the function definition
        new_content = content[:func_start] + decorator_text + content[func_start:]

    file_path.write_text(new_content)
    print(f"    ✓ Added decorator to {function_name}")
    return True


def main():
    """Apply cost tracking to all configured nodes."""
    print("Applying cost tracking to LangGraph nodes...")
    print("=" * 50)

    project_root = Path(__file__).parent.parent

    for file_path_str, functions in NODE_CONFIGS.items():
        file_path = project_root / file_path_str

        if not file_path.exists():
            print(f"\n✗ File not found: {file_path_str}")
            continue

        print(f"\nProcessing {file_path.name}:")

        # Add import if missing
        add_import_if_missing(file_path)

        # Add decorators to functions
        for func_name, model_name in functions:
            add_decorator_to_function(file_path, func_name, model_name)

    print("\n" + "=" * 50)
    print("✓ Cost tracking application complete!")

    # Create __init__ file for utils if it doesn't exist
    utils_init = project_root / "langgraph_agent/utils/__init__.py"
    if not utils_init.exists():
        utils_init.parent.mkdir(parents=True, exist_ok=True)
        utils_init.write_text('"""Utilities for LangGraph agent."""\n')
        print(f"✓ Created {utils_init}")


if __name__ == "__main__":
    main()
