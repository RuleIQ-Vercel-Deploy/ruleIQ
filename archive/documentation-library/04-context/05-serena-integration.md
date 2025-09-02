# Serena MCP Server Integration Context

## Purpose & Responsibility

Serena MCP Server provides semantic code understanding and intelligent development assistance for the ruleIQ compliance automation platform through Language Server Protocol (LSP) integration and Model Context Protocol (MCP) connectivity.

## Architecture Overview

### **Integration Design Pattern**
- **Pattern**: MCP Server with semantic code analysis capabilities
- **Approach**: Language Server Protocol (LSP) for symbol-level understanding
- **Integration**: Claude Desktop MCP client connecting to Serena server

### **Core Technology Stack**
```
Serena MCP Server: Python-based semantic coding agent toolkit
├── Language Servers: LSP integration for multi-language support
│   ├── Python: pyright/jedi for backend analysis
│   ├── TypeScript/JavaScript: For frontend code analysis
│   └── Multi-language: Java, C#, Rust, Go, Ruby, C++, PHP
├── MCP Protocol: Model Context Protocol for Claude Desktop
├── Semantic Tools: Symbol-level code operations and analysis
└── Configuration: Four-layer hierarchy system
```

## Dependencies

### **Incoming Dependencies**
- **Claude Desktop**: Primary MCP client consuming Serena services
- **ruleIQ Development**: Semantic code analysis and editing requests
- **IDE Integration**: Real-time code intelligence and assistance
- **Context Management**: Project-specific knowledge and patterns

### **Outgoing Dependencies**
- **Language Servers**: LSP servers for each supported programming language
- **ruleIQ Codebase**: Target codebase for semantic analysis
- **Project Configuration**: `.serena/project.yml` for ruleIQ-specific settings
- **Global Configuration**: `serena_config.yml` for system-wide settings

## Key Interfaces

### **MCP Server Endpoints**
```python
# Core semantic operations available through MCP
find_symbol(symbol_name, file_path=None)
# - Purpose: Locate symbols (functions, classes, variables) across codebase
# - Context: Symbol-level code understanding vs text search
# - Output: Precise symbol locations with context

replace_symbol_body(symbol_name, new_body, file_path)
# - Purpose: Replace function/method bodies with semantic precision
# - Context: Maintains proper indentation and syntax
# - Output: Accurate code modifications

search_for_pattern(pattern, language=None)
# - Purpose: Semantic pattern matching across multiple files
# - Context: Language-aware pattern recognition
# - Output: Contextual matches with surrounding code

get_symbol_references(symbol_name, file_path)
# - Purpose: Find all references to a symbol throughout codebase
# - Context: Cross-file reference analysis
# - Output: Complete usage mapping

analyze_code_context(file_path, line_number)
# - Purpose: Provide contextual analysis at specific code locations
# - Context: Semantic understanding of surrounding code
# - Output: Context-aware development suggestions
```

### **Configuration Interface**
```yaml
# .serena/project.yml (ruleIQ-specific configuration)
project:
  name: "ruleIQ"
  type: "full-stack-web-application"
  languages:
    - python
    - typescript
    - javascript
  
context:
  mode: "ide-assistant"
  focus_areas:
    - "backend/api"
    - "backend/services"
    - "frontend/components"
    - "database/models"
  
semantic_analysis:
  python:
    language_server: "pyright"
    include_patterns:
      - "api/**/*.py"
      - "services/**/*.py"
      - "database/**/*.py"
    exclude_patterns:
      - "__pycache__/**"
      - "venv/**"
  
  typescript:
    language_server: "typescript-language-server"
    include_patterns:
      - "frontend/**/*.ts"
      - "frontend/**/*.tsx"
    exclude_patterns:
      - "node_modules/**"
      - ".next/**"
```

## Implementation Context

### **Installation and Setup**
- **Installation Path**: `/home/omar/serena/`
- **Dependency Management**: `uv` (Python package manager)
- **Task Orchestration**: `poe` (task runner)
- **Configuration**: Four-layer hierarchy system

### **Integration with ruleIQ Development**

#### **Backend Development Enhancement**
```python
# Example: Semantic analysis of ruleIQ AI services
# Serena can understand the relationship between:
services/ai/assistant.py
├── ComplianceAssistant class
├── get_assessment_help() method
├── Dependencies: circuit_breaker, cache_manager
└── Usage: api/routers/ai_assessments.py

# Intelligent refactoring capabilities:
# - Symbol-level renaming across entire codebase
# - Method signature changes with automatic call-site updates
# - Import management and dependency analysis
```

#### **Frontend Development Enhancement**
```typescript
// Example: React component analysis
// Serena understands TypeScript/React patterns:
frontend/components/assessments/QuestionRenderer.tsx
├── QuestionRenderer component
├── Props interface: QuestionRendererProps
├── Hooks usage: useForm, useFieldArray
├── Dependencies: react-hook-form, zod
└── Usage: app/(dashboard)/assessments/[id]/page.tsx

// Semantic operations:
// - Component refactoring with prop updates
// - Hook dependency analysis
// - Type-safe modifications
```

#### **Database Schema Intelligence**
```python
# Example: SQLAlchemy model understanding
database/business_profile.py
├── BusinessProfile model
├── Relationships: User, AssessmentSession, EvidenceItem
├── Field mappings: handles_persona -> handles_personal_data
└── Migration impact: alembic/versions/*.py

# Serena capabilities:
# - Model relationship analysis
# - Field renaming with ORM updates
# - Migration generation guidance
```

### **Development Workflow Integration**

#### **Quality Assurance Commands**
```bash
# Serena-integrated development cycle
cd /home/omar/serena

# 1. Code analysis and modification through MCP
# (Interactive through Claude Desktop)

# 2. Quality assurance pipeline
uv run poe format      # Code formatting
uv run poe lint        # Linting analysis  
uv run poe type-check  # Type checking
uv run poe test        # Test execution

# 3. ruleIQ-specific validation
cd /home/omar/Documents/ruleIQ
pnpm typecheck         # Frontend type checking
pnpm lint             # Frontend linting
pytest tests/         # Backend testing
```

#### **MCP Server Startup**
```bash
# Manual startup for development
cd /home/omar/serena
python -m serena.mcp --context ide-assistant --project /home/omar/Documents/ruleIQ

# Automatic startup (if configured)
# Should be integrated into scripts/init_dev_environment.sh
```

## Change Impact Analysis

### **Risk Factors**
- **Language Server Dependencies**: LSP server availability for each language
- **Configuration Complexity**: Four-layer configuration management
- **MCP Protocol Stability**: Dependency on MCP protocol specification
- **Performance Impact**: Language server startup and analysis overhead

### **Integration Benefits**
- **Semantic Precision**: Symbol-level code understanding vs text manipulation
- **Cross-Language Analysis**: Unified approach for Python backend and TypeScript frontend
- **Context Awareness**: Deep understanding of ruleIQ architecture and patterns
- **Development Velocity**: Intelligent code assistance and automated refactoring

### **Testing Requirements**
- **MCP Connectivity**: Verify Claude Desktop can connect to Serena server
- **Language Server Integration**: Test LSP functionality for Python and TypeScript
- **Project Context Loading**: Validate ruleIQ-specific configuration
- **Semantic Operations**: Test symbol finding, replacement, and analysis

## Current Status

### **Integration Status**
- **Installation**: ✅ Serena installed at `/home/omar/serena/`
- **Configuration**: 🔄 ruleIQ-specific `.serena/project.yml` needs creation
- **MCP Server**: 🔄 Manual startup required, auto-startup integration pending
- **Claude Desktop**: 🔄 MCP client configuration needed

### **Recommended Actions**
1. **Create Project Configuration**: Generate `.serena/project.yml` for ruleIQ
2. **Test MCP Connectivity**: Verify Claude Desktop can connect to Serena
3. **Integrate Startup**: Add Serena startup to `scripts/init_dev_environment.sh`
4. **Validate Semantic Operations**: Test symbol analysis on ruleIQ codebase

### **Development Context**
- **Current Phase**: Week 1 Day 3 - AI SDK Optimization Project
- **Serena Integration**: Enhancement tool for development workflow
- **Focus Areas**: Backend AI services, frontend components, database models
- **Quality Goals**: Maintain 98% test passing rate with semantic precision

---

**Document Metadata**
- Created: 2025-01-07
- Version: 1.0.0
- Authors: AI Assistant
- Review Status: Initial Draft
- Next Review: 2025-01-14
- Integration Status: Configuration pending, ready for setup