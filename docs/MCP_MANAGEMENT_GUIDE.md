# MCP Management Guide for ruleIQ

## Overview

The MCP (Model Context Protocol) Control Center provides centralized management for all MCP servers used in the ruleIQ project. This guide covers everything you need to manage, monitor, and troubleshoot the MCP infrastructure.

## Quick Start

### Command Line Interface

```bash
# Check status of all servers
mcp-control status

# Start all servers
mcp-control start all

# Stop specific server
mcp-control stop archon

# Restart a server
mcp-control restart serena

# System health check
mcp-control health
```

### Web Dashboard

Access the visual dashboard at: http://localhost:8501

```bash
# Start the dashboard
cd /home/omar/mcp-manager && streamlit run mcp_dashboard.py
```

## MCP Servers for ruleIQ

### 1. **Archon Server** (📋)
- **Purpose**: Task management and knowledge base for ruleIQ
- **Port**: 8080
- **Status Check**: `mcp-control status | grep -A 4 Archon`
- **Key Features**:
  - Project and task tracking
  - Document versioning
  - Knowledge retrieval (RAG)
  - Code examples search

### 2. **Serena MCP** (🧠)
- **Purpose**: Semantic code analysis and memory management
- **Port**: 9121
- **Status Check**: `mcp-control status | grep -A 4 Serena`
- **Key Features**:
  - Symbol-based code navigation
  - Memory management
  - Code refactoring tools
  - Pattern searching

### 3. **Playwright MCP** (🎭)
- **Purpose**: Browser automation and testing
- **Key Features**:
  - Web scraping
  - E2E testing
  - Browser automation
  - Screenshot capture

### 4. **Filesystem MCP** (📁)
- **Purpose**: File system access for ruleIQ project
- **Path**: `/home/omar/Documents/ruleIQ`
- **Key Features**:
  - File operations
  - Directory management
  - Search capabilities

### 5. **Docker MCP Gateway** (🐳)
- **Purpose**: Docker container management
- **Command**: `docker mcp gateway run`
- **Configuration**: Added to Claude Desktop as `MCP_DOCKER`
- **Key Features**:
  - Container orchestration
  - Image management
  - Network configuration
  - MCP server containerization
  - Secure container execution

### 6. **TestSprite MCP** (🧪)
- **Purpose**: Test generation and management
- **Key Features**:
  - Automated test generation
  - Test suite management
  - Coverage analysis

### 7. **Context7 MCP** (💾)
- **Purpose**: Context management and caching
- **Key Features**:
  - Context preservation
  - Caching strategies
  - Session management

### 8. **Sequential Thinking MCP** (🔄)
- **Purpose**: Step-by-step reasoning and planning
- **Key Features**:
  - Logical reasoning
  - Planning workflows
  - Decision trees

### 9. **Desktop Commander MCP** (🖥️)
- **Purpose**: Desktop automation and file management
- **Key Features**:
  - Desktop automation
  - File operations
  - System commands

## Common Operations

### Starting the MCP Infrastructure

```bash
# 1. Check current status
mcp-control status

# 2. Start all servers
mcp-control start all

# 3. Verify all are running
mcp-control health
```

### Troubleshooting

#### Server Won't Start
```bash
# Check if port is in use
lsof -i :8080  # For Archon
lsof -i :9121  # For Serena

# Kill existing process if needed
pkill -f archon
pkill -f serena-mcp
```

#### Zombie Processes
```bash
# Check for zombies
mcp-control health

# Clean up zombies
ps aux | grep defunct
kill -9 <PID>
```

#### High Memory Usage
```bash
# Check memory per server
mcp-control status -v

# Restart memory-intensive servers
mcp-control restart testsprite
mcp-control restart context7
```

## Integration with ruleIQ

### Using Archon for Task Management

```python
# In Claude Code, use MCP tools directly
mcp__archon__list_tasks(
    filter_by="status",
    filter_value="todo",
    project_id="342d657c-fb73-4f71-9b6e-302857319aac"
)

# Update task status
mcp__archon__update_task(
    task_id="task-id",
    status="doing"
)
```

### Using Serena for Code Analysis

```python
# Find symbols in code
mcp__serena__find_symbol(
    name_path="ComplianceAssistant",
    include_body=True
)

# Search patterns
mcp__serena__search_for_pattern(
    pattern="def.*process_message"
)
```

## Monitoring & Maintenance

### Daily Health Check Routine

1. **Morning Check**:
   ```bash
   mcp-control health
   mcp-control status
   ```

2. **Memory Monitoring**:
   - Restart servers using >500MB if not actively used
   - Check for memory leaks in long-running servers

3. **Log Review**:
   - Check Streamlit dashboard logs for errors
   - Review MCP server output for issues

### Performance Optimization

- **Selective Starting**: Only start servers you need
  ```bash
  mcp-control start archon
  mcp-control start serena
  ```

- **Resource Limits**: Servers are configured with memory limits
  - Docker containers: 2GB limit
  - Monitor with: `mcp-control status -v`

## Configuration

### Server Configuration File

Location: `/home/omar/.mcp-manager/servers.json`

```json
{
  "archon": {
    "name": "Archon Server",
    "port": 8080,
    "process_name": "archon",
    "start_cmd": "cd /home/omar/Archon && make dev",
    "icon": "📋",
    "description": "Task management and knowledge base for ruleIQ"
  }
}
```

### Adding New Servers

1. Edit `/home/omar/.mcp-manager/servers.json`
2. Add server configuration
3. Restart the dashboard or use `mcp-control status`

## Best Practices

1. **Start Only What You Need**: Don't run all servers if not required
2. **Regular Health Checks**: Run `mcp-control health` daily
3. **Clean Shutdowns**: Always use `mcp-control stop` instead of killing processes
4. **Monitor Resources**: Keep an eye on memory and CPU usage
5. **Use Archon for Tasks**: Always check and update tasks in Archon
6. **Backup Configuration**: Keep a copy of `servers.json`

## Emergency Procedures

### Complete System Reset

```bash
# 1. Stop all servers
mcp-control stop all

# 2. Clean up any zombies
ps aux | grep -E "mcp|serena|archon" | grep defunct
# Kill any found zombies

# 3. Clear any port conflicts
lsof -i :8080
lsof -i :9121
# Kill processes using these ports

# 4. Restart servers
mcp-control start all

# 5. Verify health
mcp-control health
```

### Dashboard Not Loading

```bash
# 1. Check if Streamlit is running
ps aux | grep streamlit

# 2. Kill existing instance
pkill -f streamlit

# 3. Restart dashboard
cd /home/omar/mcp-manager
streamlit run mcp_dashboard.py
```

## Support & Troubleshooting

For issues specific to:
- **Archon**: Check project at `/home/omar/Archon`
- **Serena**: Check installation at `/home/omar/serena`
- **Dashboard**: Review `/home/omar/mcp-manager/mcp_dashboard.py`

## Quick Reference Card

```
Command                           Description
-------                           -----------
mcp-control status               Show all server status
mcp-control start <server|all>  Start server(s)
mcp-control stop <server|all>   Stop server(s)
mcp-control restart <server>    Restart a server
mcp-control health              System health check
mcp-control list                List available servers
mcp-control help                Show help message

Dashboard: http://localhost:8501
```

---

*Last Updated: 2025-08-31*
*Project: ruleIQ Compliance Automation Platform*