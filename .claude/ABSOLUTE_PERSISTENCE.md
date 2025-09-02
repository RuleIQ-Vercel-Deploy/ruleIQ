# Serena Absolute Persistence System

## Multi-Layer Persistence Architecture

### Layer 1: Flag-Based Quick Check
- **Files**: `serena-active.flag`, `serena-session.flag`
- **Check Frequency**: Every command
- **Timeout**: 2 minutes

### Layer 2: Heartbeat System
- **File**: `serena-heartbeat`
- **Update Frequency**: Every 10 seconds
- **Timeout**: 60 seconds

### Layer 3: Process Monitoring
- **PID File**: `serena.pid`, `serena-daemon.pid`
- **Checks**: Process existence via kill -0
- **Recovery**: Automatic restart

### Layer 4: Python Daemon
- **Script**: `serena-daemon.py`
- **Features**:
  - Continuous monitoring
  - Auto-activation
  - Thread-based heartbeat
  - Signal handling

### Layer 5: Systemd Service (Optional)
- **Service**: `serena-persistence.service`
- **Auto-restart**: Always
- **Resource limits**: 512MB RAM, 10% CPU

## Activation Methods

### Method 1: Shell Script
```bash
bash .claude/serena-absolute-persistence.sh
```

### Method 2: Python Daemon
```bash
python3 .claude/serena-daemon.py &
```

### Method 3: Systemd Service
```bash
# Install service (one-time)
sudo cp .claude/serena-persistence.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable serena-persistence
sudo systemctl start serena-persistence
```

## How It Ensures Absolute Persistence

1. **Multiple Check Points**: 
   - Flag files (fast check)
   - JSON status (deep check)
   - Process PID (system check)
   - Heartbeat (liveness check)

2. **Automatic Recovery**:
   - Any failed check triggers immediate reactivation
   - Multiple activation methods tried in sequence
   - Background daemon ensures continuous monitoring

3. **Lock Prevention**:
   - File locking prevents concurrent checks
   - PID tracking prevents duplicate daemons
   - Heartbeat prevents stale locks

4. **Fault Tolerance**:
   - Survives terminal closes
   - Survives SSH disconnects
   - Survives system load spikes
   - Auto-recovers from crashes

## Quick Commands

### Start Absolute Persistence
```bash
# Start daemon
python3 .claude/serena-daemon.py &

# Or use shell script
bash .claude/serena-absolute-persistence.sh
```

### Check Status
```bash
# Quick check
ls -la .claude/*.flag

# Detailed check
cat .claude/serena-status.json

# Process check
ps aux | grep serena-daemon
```

### Force Reactivation
```bash
# Remove all flags to force reactivation
rm -f .claude/*.flag .claude/serena-heartbeat
bash .claude/serena-absolute-persistence.sh
```

## Integration with Claude

Add to your session start:
```bash
# Ensure daemon is running
pgrep -f serena-daemon.py || python3 .claude/serena-daemon.py &
```

## Monitoring

Check daemon logs:
```bash
tail -f .claude/serena-daemon.log
```

## Benefits

1. **Zero Downtime**: Serena never goes inactive
2. **Fast Checks**: Flag-based checks are instant
3. **Self-Healing**: Automatic recovery from any failure
4. **Resource Efficient**: Minimal CPU/RAM usage
5. **Logging**: Complete audit trail
6. **Scalable**: Works with multiple sessions

This system ensures Serena persistence is ABSOLUTE - it cannot fail.