# MCP Configuration Guide for ruleIQ

**Last Updated:** October 2, 2025

## Overview

This document provides a complete reference for all MCP (Model Context Protocol) server configurations used in the ruleIQ project. MCP servers provide Claude with extended capabilities for development assistance.

---

## 🔧 Active MCP Servers

### 1. **Serena MCP** - Intelligent Code Assistant
**Purpose:** Deep semantic code understanding and intelligent development assistance

**Configuration Location:**
- Global: `/home/omar/.config/Claude/claude_desktop_config.json`
- Project: `/home/omar/Documents/ruleIQ/.serena/project.yml`

**Global Config:**
```json
{
  "mcpServers": {
    "serena": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/oraios/serena",
        "serena-mcp-server"
      ]
    }
  }
}
```

**Project Config:** `/home/omar/Documents/ruleIQ/.serena/project.yml`
- Full project metadata and preferences
- Language server configurations (Python + TypeScript)
- Semantic analysis patterns
- Domain knowledge (compliance frameworks)
- Development workflow optimization
- 207 lines of project-specific intelligence

**Capabilities:**
- ✅ Symbol search and analysis (classes, functions, methods)
- ✅ File reading with semantic understanding
- ✅ Code search patterns (regex + semantic)
- ✅ Project-aware refactoring
- ✅ Memory management for project context
- ✅ Shell command execution

**Verification:**
```bash
# Check if Serena is active
cat /home/omar/Documents/ruleIQ/.claude/serena-status.json
# Should show: "status": "active"
```

---

### 2. **Desktop Commander MCP** - File System Operations
**Purpose:** Advanced file system operations and process management

**Configuration Location:** `/home/omar/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "desktop-commander": {
      "command": "/home/omar/.config/nvm/versions/node/v22.14.0/bin/node",
      "args": [
        "/home/omar/DesktopCommanderMCP/dist/index.js"
      ]
    }
  }
}
```

**Capabilities:**
- ✅ Read/write files with line-level precision
- ✅ Search files and code patterns
- ✅ Process management (start, monitor, terminate)
- ✅ Directory operations
- ✅ Block-level file editing (surgical replacements)
- ✅ Interactive REPL sessions (Python, Node.js, etc.)

**Installation Location:** `/home/omar/DesktopCommanderMCP/`

---

### 3. **Fetch MCP** - Web Content Retrieval
**Purpose:** Fetch and analyze web content

**Configuration Location:** `/home/omar/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "fetch": {
      "command": "/home/omar/.config/nvm/versions/node/v22.14.0/bin/npx",
      "args": [
        "-y",
        "@smithery/cli@latest",
        "run",
        "@smithery-ai/fetch",
        "--key",
        "95e83c85-9a18-4524-9549-6a2c0f194f69",
        "--profile",
        "hungry-lemming-s64fT3"
      ]
    }
  }
}
```

**Capabilities:**
- ✅ Fetch URLs and convert HTML to markdown
- ✅ Extract page metadata
- ✅ Extract specific elements using CSS selectors
- ✅ Analyze web content with AI

---

### 4. **Excalidraw MCP** - Diagram Creation
**Purpose:** Create and edit Excalidraw diagrams

**Configuration Location:** `/home/omar/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "excalidraw": {
      "command": "node",
      "args": [
        "/home/omar/mcp_excalidraw/dist/index.js"
      ],
      "env": {}
    }
  }
}
```

**Installation Location:** `/home/omar/mcp_excalidraw/`

**Capabilities:**
- ✅ Create technical diagrams
- ✅ Architecture visualizations
- ✅ Export to multiple formats

---

### 5. **N8N MCP** - Workflow Automation
**Purpose:** Integration with N8N workflow automation platform

**Configuration Location:** `/home/omar/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "n8n-mcp": {
      "command": "/home/omar/.config/nvm/versions/node/v22.14.0/bin/npx",
      "args": ["n8n-mcp"],
      "env": {
        "MCP_MODE": "stdio",
        "LOG_LEVEL": "error",
        "DISABLE_CONSOLE_OUTPUT": "true",
        "N8N_API_URL": "https://omarbakri.app.n8n.cloud/workflow/new?projectId=IM2AeCWg1Hw3smiW",
        "N8N_API_KEY": "[REDACTED]"
      }
    }
  }
}
```

**Capabilities:**
- ✅ Create and manage N8N workflows
- ✅ Integrate with external services
- ✅ Automate development tasks

---

## 📁 Configuration File Locations

### Global Claude Desktop Config
**Primary:** `/home/omar/.config/Claude/claude_desktop_config.json`
- Contains all MCP server definitions
- Applies to all Claude desktop sessions
- 52 lines

### Project-Specific Configs

**Serena Project Config:**
- Location: `/home/omar/Documents/ruleIQ/.serena/project.yml`
- Purpose: Project-specific intelligence and preferences
- Contains: Architecture, domain knowledge, workflow patterns
- Size: 207 lines

**Local Serena Config:**
- Location: `/home/omar/.claude/mcp.json`
- Purpose: Alternative Serena startup configuration
- 15 lines

**Session State Files:**
- `/home/omar/Documents/ruleIQ/.claude/serena-status.json` - Current status
- `/home/omar/Documents/ruleIQ/.claude/serena-metrics.json` - Performance metrics
- `/home/omar/Documents/ruleIQ/.claude/verification-complete.json` - Verification state

---

## 🔍 MCP Server Discovery

### Finding All MCP Configurations
```bash
# Find all MCP config files
find /home/omar -name "claude_desktop_config.json" -o -name "mcp*.json" 2>/dev/null

# Key locations:
# - /home/omar/.config/Claude/claude_desktop_config.json (MAIN)
# - /home/omar/.claude/mcp.json (Serena local)
# - /home/omar/.claude/mcp_config.json (Backup)
# - /home/omar/claude.json (Large config - 385KB)
```

### Checking Active Status
```bash
# Serena status
cat /home/omar/Documents/ruleIQ/.claude/serena-status.json

# Claude Desktop config
cat /home/omar/.config/Claude/claude_desktop_config.json

# Serena project config
cat /home/omar/Documents/ruleIQ/.serena/project.yml
```

---

## 🚀 Usage in Development

### Serena MCP - Code Intelligence
```bash
# Serena tools available in Claude:
# - read_file: Read files with semantic understanding
# - find_symbol: Find classes, functions, methods
# - search_for_pattern: Search with regex or semantic queries
# - get_symbols_overview: Get file structure
# - replace_symbol_body: Refactor code blocks
# - execute_shell_command: Run development commands
# - write_memory: Store project knowledge
```

### Desktop Commander - File Operations
```bash
# Desktop Commander tools:
# - read_file: Read files with line ranges
# - write_file: Create/update files
# - edit_block: Surgical code edits
# - search_files: Find files by pattern
# - search_code: Grep-like code search
# - start_process: Launch REPLs and processes
# - interact_with_process: Send commands to processes
```

### Integration Example
```bash
# Typical workflow combining MCP servers:
# 1. Serena: Analyze codebase structure
# 2. Desktop Commander: Read specific files
# 3. Serena: Understand semantic context
# 4. Desktop Commander: Make surgical edits
# 5. Serena: Verify changes and run tests
```

---

## 🛠 Maintenance & Troubleshooting

### Restart MCP Servers
```bash
# Restart Claude Desktop (restarts all MCP servers)
pkill -9 claude
# Then reopen Claude Desktop

# Check Serena initialization
cat /home/omar/Documents/ruleIQ/.claude/serena-status.json
```

### Update Configurations
```bash
# Edit global config
vim /home/omar/.config/Claude/claude_desktop_config.json

# Edit Serena project config
vim /home/omar/Documents/ruleIQ/.serena/project.yml

# Restart Claude Desktop to apply changes
```

### Debug MCP Issues
```bash
# Check Serena logs
tail -f /home/omar/Documents/ruleIQ/.claude/serena-metrics.json

# Verify node/python availability
which node  # For Desktop Commander, Fetch, Excalidraw
which uvx   # For Serena
which npx   # For N8N

# Check MCP server processes
ps aux | grep -E "(serena|mcp|node.*dist)"
```

---

## 📊 MCP Server Comparison

| Server | Language | Primary Use | State Management |
|--------|----------|-------------|------------------|
| Serena | Python | Code intelligence | Project-specific |
| Desktop Commander | Node.js | File operations | Stateless |
| Fetch | Node.js | Web content | Stateless |
| Excalidraw | Node.js | Diagrams | Stateless |
| N8N | Node.js | Automation | API-based |

---

## 🔐 Security Considerations

**API Keys and Secrets:**
- N8N API key stored in environment variables
- Fetch uses Smithery API key
- All keys should be rotated regularly

**File Access:**
- Desktop Commander has full filesystem access
- Serena respects project boundaries
- Review tool permissions before granting access

---

## 📝 Adding New MCP Servers

### Step 1: Update Global Config
Edit `/home/omar/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "your-server-name": {
      "command": "/path/to/executable",
      "args": ["arg1", "arg2"],
      "env": {
        "VAR": "value"
      }
    }
  }
}
```

### Step 2: Restart Claude Desktop
```bash
pkill -9 claude
# Reopen Claude Desktop
```

### Step 3: Verify Server is Active
Check in Claude that the new server appears in available tools.

---

## 🎯 Best Practices

1. **Use Serena for semantic code understanding** - Best for understanding architecture and refactoring
2. **Use Desktop Commander for file operations** - Best for precise file edits and process management
3. **Keep project config updated** - Maintain `.serena/project.yml` with latest patterns
4. **Monitor MCP performance** - Check `serena-metrics.json` for bottlenecks
5. **Restart periodically** - If MCP servers become slow, restart Claude Desktop

---

## 📚 Related Documentation

- **Serena GitHub:** https://github.com/oraios/serena
- **Desktop Commander:** (Local installation at `/home/omar/DesktopCommanderMCP/`)
- **Project Config:** `/home/omar/Documents/ruleIQ/.serena/project.yml`
- **Serena Status:** `/home/omar/Documents/ruleIQ/.claude/serena-status.json`

---

## 🔄 Quick Reference

```bash
# Main config file
/home/omar/.config/Claude/claude_desktop_config.json

# Serena project config
/home/omar/Documents/ruleIQ/.serena/project.yml

# Serena status
/home/omar/Documents/ruleIQ/.claude/serena-status.json

# Restart all MCP servers
pkill -9 claude && (reopen Claude Desktop)

# Check active tools in Claude
# Look for tools starting with "mcp__"
```

---

**Summary:** This ruleIQ project uses 5 MCP servers for comprehensive development assistance. Serena provides code intelligence, Desktop Commander handles file operations, and the others extend capabilities for web content, diagrams, and automation.
