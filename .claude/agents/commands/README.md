# Claude Code "/" Commands for RuleIQ Refactoring

## ✅ Setup Complete!

Your Claude Code commands are now ready in `.claude/commands/`

## 🚀 Quick Start

Run this command in Claude Code to initialize everything:

```
/refactor-init
```

## 📋 Available Commands

| Command | Purpose |
|---------|---------|
| `/refactor-init` | Initialize the refactoring environment and launch the menu |
| `/refactor-analyze` | Analyze codebase to identify patterns needing change |
| `/refactor-state` | Show exact code changes for state management migration |
| `/refactor-validate` | Validate refactoring progress and show what's complete |
| `/refactor-help` | Show available commands and usage |

## 🔄 Recommended Workflow

1. **Initialize (first time only):**
   ```
   /refactor-init
   ```
   This will:
   - Set up virtual environment
   - Install dependencies
   - Create backups
   - Launch the refactoring menu

2. **Analyze your codebase:**
   ```
   /refactor-analyze
   ```
   Shows what needs to be changed in each file

3. **Apply state management changes:**
   ```
   /refactor-state
   ```
   Shows exact before/after code for `app/app.py`

4. **Validate your progress:**
   ```
   /refactor-validate
   ```
   Checks what's been completed and what remains

## 📁 Command Locations

All commands are located in:
```
/home/omar/Documents/ruleIQ/.claude/commands/
```

- `refactor-init` - Full initialization script
- `refactor-analyze` - Analysis script  
- `refactor-state` - State migration guide
- `refactor-validate` - Progress validator
- `refactor-help` - Help documentation

## 💡 How It Works

Each command:
1. Shows exact file locations
2. Displays current code to find
3. Provides new code to replace it with
4. Includes line numbers for easy navigation

## 🎯 Example Usage

In Claude Code, simply type:

```
/refactor-analyze
```

This will analyze your codebase and show:
- Current AgentState implementation
- Number of try-except blocks to centralize
- Custom RAG functions to replace
- Celery tasks to migrate

Then follow up with specific refactoring commands as needed.

## ✨ Ready to Start!

Begin with:
```
/refactor-init
```

This will set up everything and present you with the interactive menu to guide you through the complete refactoring process.
