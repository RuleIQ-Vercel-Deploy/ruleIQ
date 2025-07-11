"""
AI Services Module Initialization

Imports and registers all AI tools for function calling support.
"""

# Import tool modules to trigger registration
from . import assessment_tools, evidence_tools, regulation_tools  # noqa: F401

# Import assistant
from .assistant import ComplianceAssistant

# Import core tools functionality
from .tools import (
    BaseTool,
    ToolExecutor,
    ToolRegistry,
    ToolResult,
    ToolType,
    execute_tool,
    get_tool_schemas,
    register_tool,
    tool_executor,
    tool_registry,
)

__all__ = [
    "BaseTool",
    "ComplianceAssistant",
    "ToolExecutor",
    "ToolRegistry",
    "ToolResult",
    "ToolType",
    "execute_tool",
    "get_tool_schemas",
    "register_tool",
    "tool_executor",
    "tool_registry",
]
