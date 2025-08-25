# Serena MCP Persistent Initialization Protocol - V2 (Updated)

## Key Changes in V2
- **REMOVED**: No checking for project-specific RAG systems during initialization
- **CLARIFIED**: Only use Archon MCP's RAG system (archon:perform_rag_query and archon:search_code_examples)
- **SIMPLIFIED**: Focus on Serena activation and verification only

## Initialization Components (Unchanged)

### Multi-Layer Hook System
The hook configuration provides **comprehensive persistence** through multiple trigger points:

1. **SessionStart**: Full initialization with verification script
2. **UserPromptSubmit**: Quick reactivation check before each user interaction  
3. **PreToolUse**: Environment verification for Serena tools + general tools
4. **Stop**: State preservation for next session
5. **SubagentStop**: Additional persistence checks

### Scripts Created

#### 1. serena-persistent-init.sh
- **Location**: `/home/omar/Documents/ruleIQ/.claude/serena-persistent-init.sh`
- **Function**: Comprehensive Serena activation with recovery mechanisms
- **Features**:
  - Virtual environment activation
  - Environment variable setup
  - Persistence flag creation
  - Recovery attempts on failure
  - Cross-session state preservation

#### 2. serena-verification.py  
- **Location**: `/home/omar/Documents/ruleIQ/.claude/serena-verification.py`
- **Function**: Comprehensive Python environment and project verification
- **Checks**:
  - Project structure integrity
  - Python import capabilities
  - Module accessibility (PolicyGenerator, ComplianceFramework)
  - Persistence flag management
  - Status JSON file creation

#### 3. serena-monitor.sh
- **Location**: `/home/omar/Documents/ruleIQ/.claude/serena-monitor.sh`
- **Function**: Quick status checks and reactivation
- **Commands**:
  - `status` - Check current Serena status
  - `reactivate` - Reactivate if inactive
  - `force-reactivate` - Force reactivation regardless of status

## RAG System Clarification

### Use ONLY Archon MCP RAG
- **archon:perform_rag_query()** - For searching documentation and patterns
- **archon:search_code_examples()** - For finding code examples

### DO NOT Check Project RAG
- The project has internal RAG implementations (services/agentic_rag.py, etc.)
- These are application-specific and NOT for development assistance
- No need to verify or check these during Serena initialization
- Focus only on Archon's knowledge base for development support

## What Serena Should Do on Initialization

1. **Activate Serena MCP** for enhanced code intelligence
2. **Verify Python environment** and project structure
3. **Set persistence flags** for cross-session state
4. **Log status** for monitoring

## What Serena Should NOT Do

1. **Don't check for project-specific RAG systems**
2. **Don't analyze internal RAG implementations** 
3. **Don't confuse project RAG with Archon RAG**

## Manual Commands Available

```bash
# Quick status check
/home/omar/Documents/ruleIQ/.claude/serena-monitor.sh status

# Force reactivation
/home/omar/Documents/ruleIQ/.claude/serena-monitor.sh force-reactivate

# Full initialization
/home/omar/Documents/ruleIQ/.claude/serena-persistent-init.sh

# View logs
tail -f /home/omar/Documents/ruleIQ/.claude/serena-init.log
```

## Implementation Status: UPDATED ✅

The Serena initialization protocol has been simplified to focus only on core activation and verification, without checking for project-specific RAG systems. Use only Archon MCP's RAG capabilities for development assistance.