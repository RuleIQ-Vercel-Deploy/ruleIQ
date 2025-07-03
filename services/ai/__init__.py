"""
AI Services Module Initialization

Imports and registers all AI tools for function calling support.
"""

# Import tool modules to trigger registration
from . import assessment_tools
from . import regulation_tools  
from . import evidence_tools

# Import core tools functionality
from .tools import (
    BaseTool,
    ToolResult, 
    ToolType,
    ToolRegistry,
    ToolExecutor,
    tool_registry,
    tool_executor,
    register_tool,
    get_tool_schemas,
    execute_tool
)

# Import assistant
from .assistant import ComplianceAssistant

__all__ = [
    "ComplianceAssistant",
    "BaseTool",
    "ToolResult",
    "ToolType", 
    "ToolRegistry",
    "ToolExecutor",
    "tool_registry",
    "tool_executor",
    "register_tool",
    "get_tool_schemas",
    "execute_tool"
]