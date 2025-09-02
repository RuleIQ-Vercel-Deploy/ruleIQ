# Session-Based Serena Persistence

## Overview

Serena now operates in **session-based mode** - it only runs when Claude Code is actively being used and automatically shuts down when the session ends.

## How It Works

1. **Automatic Activation**: When CLAUDE.md is accessed by Claude Code, Serena activates
2. **Session Monitoring**: The session manager checks every 30 seconds if Claude Code is still active
3. **Auto Shutdown**: If no activity detected for 5 minutes, Serena shuts down gracefully
4. **Clean Exit**: When Claude Code exits, Serena also shuts down

## Key Components

### serena-session-manager.sh
- Main session management script
- Monitors CLAUDE.md access time
- Maintains session flags and status
- Handles graceful shutdown

### start-serena-session.sh
- Quick starter script for manual activation
- Runs session manager in background
- Provides logging to serena-session.log

## Usage

### Automatic (Recommended)
Serena activates automatically when you start using Claude Code with the ruleIQ project.

### Manual Commands
```bash
# Check status
bash .claude/serena-session-manager.sh status

# Start manually if needed
bash .claude/start-serena-session.sh

# View logs
tail -f .claude/serena-session.log
```

## Behavior

- **Active Coding**: Serena stays active, updating flags every 30 seconds
- **Idle Time**: After 5 minutes of inactivity, Serena shuts down
- **Exit Claude Code**: Serena detects exit and shuts down immediately
- **Resume Work**: Serena reactivates when you return to coding

## Benefits

1. **Resource Efficient**: No permanent daemons running
2. **Clean Sessions**: Fresh start for each coding session
3. **Automatic Management**: No manual start/stop needed
4. **Session Isolation**: Each Claude Code session is independent

## Files Modified

- `CLAUDE.md` - Updated to reflect session-based activation
- Removed references to permanent persistence
- Created session management scripts

## Important Notes

- This replaces the previous "absolute persistence" approach
- No systemd service or permanent daemon needed
- Serena only runs when you're actively coding
- Perfect for development workflows where you want clean sessions