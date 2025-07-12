# SuperClaude Configuration

## 🚀 Core Coding Agents (Quick Reference)

### Just describe what you need - the right agent auto-activates!

| **Agent** | **Trigger Phrases** | **Direct Command** | **Purpose** |
|-----------|-------------------|-------------------|-------------|
| **🏗️ FullStack Builder** | "build", "create", "implement" | `/build --feature` | Complete features from UI to database |
| **🔍 Debug Detective** | "bug", "error", "not working" | `/troubleshoot` | Systematic problem investigation |
| **🛡️ Security Guardian** | "secure", "vulnerability", "audit" | `/scan --security` | Security audits & hardening |
| **⚡ Performance Optimizer** | "slow", "optimize", "faster" | `/optimize --performance` | Speed & resource improvements |
| **🧹 Code Refactorer** | "clean", "messy", "refactor" | `/improve --quality` | Clean code & reduce tech debt |
| **🧪 Test Engineer** | "test", "coverage", "e2e" | `/test --comprehensive` | Testing strategy & implementation |

### 💡 Usage Examples
```bash
# Natural language (recommended)
"Build a user profile page with avatar upload"
"This API endpoint is returning 500 errors" 
"Check if our authentication is secure"
"The dashboard takes 5 seconds to load"
"Clean up this legacy component"
"Write tests for the checkout flow"

# Power user flags (optional)
--think         # Deeper analysis (4K tokens)
--ultrathink    # Critical analysis (32K tokens)  
--uc           # UltraCompressed mode (70% token savings)
--dry-run      # Preview without execution
--plan         # Show execution plan first
```

### 🎯 Auto-Detection Examples
- **React/Vue files** → FullStack Builder activates
- **Error messages** → Debug Detective investigates
- **Performance issues** → Performance Optimizer engages
- **Multiple files** → Automatic todo list creation
- **Complex tasks** → Sequential analysis with evidence

### 📋 Combined Agent Example
```bash
"Build a secure, fast user dashboard with tests"
# Automatically chains:
# 1. FullStack Builder → Creates dashboard
# 2. Security Guardian → Validates security  
# 3. Performance Optimizer → Optimizes speed
# 4. Test Engineer → Adds comprehensive tests
```

### 🔧 Advanced Features

#### **Thinking Modes**
- `--think`: Multi-file analysis (4K tokens)
- `--think-hard`: Deep architectural analysis (10K tokens)
- `--ultrathink`: Critical system redesign (32K tokens)

#### **MCP Integration**
- `--c7`: Context7 for library documentation
- `--seq`: Sequential for complex analysis
- `--magic`: Magic UI components
- `--pup`: Puppeteer browser automation
- `--all-mcp`: Enable all MCP servers

#### **Task Management**
- **3+ steps** → Auto-triggers TodoList
- **High-risk operations** → Requires todos
- **6+ files** → Auto-coordination mode

### 📁 Project Structure
```
.claude/                    # Claude configuration
├── settings.local.json     # Basic permissions
├── shared/                 # Shared configurations
│   ├── superclaude-core.yml
│   ├── superclaude-mcp.yml
│   ├── superclaude-rules.yml
│   └── superclaude-personas.yml
.claudedocs/               # Claude documentation
├── tasks/                 # Level 1 persistent tasks
├── reports/               # Analysis reports
├── metrics/               # Performance metrics
└── checkpoints/           # Save states
```

### 🚀 Quick Start Commands

```bash
# New feature
/build --init --feature --react --magic

# Security audit
/scan --security --owasp --strict

# Performance check
/analyze --performance --profile

# Code cleanup
/improve --quality --iterate

# Full test suite
/test --coverage --e2e --pup
```

### 📚 Full Documentation
For complete SuperClaude documentation, see the configuration files in `.claude/shared/`
