# Serena MCP Monitoring & Health Check Guide

## Overview

This guide covers the monitoring and health check tools added to prevent and detect Serena MCP memory leaks and instance duplication issues.

## Components

### 1. Lock File Prevention (`serena-monitor.sh`)

**Purpose:** Prevent concurrent reactivations from creating duplicate instances.

**How it works:**
- Acquires lock before reactivation (PID-based lock file)
- Checks for stale locks (process not running)
- Waits up to 5 seconds for lock availability
- Automatically releases lock on exit

**Lock file location:** `.claude/serena.lock`

### 2. Metrics Logging (`serena-metrics.json`)

**Purpose:** Track instance count, zombie processes, and reactivation events over time.

**Metrics tracked:**
- `instance_count` - Number of running Serena MCP instances
- `zombie_count` - Number of zombie Serena processes
- `action` - Event type (status_check, reactivate_success, etc.)
- `timestamp` - ISO 8601 UTC timestamp

**Retention:** Last 100 entries (FIFO)

**File location:** `.claude/serena-metrics.json`

**Sample entry:**
```json
{
  "timestamp": "2025-09-30T16:37:50Z",
  "instance_count": 1,
  "zombie_count": 0,
  "action": "status_check"
}
```

### 3. Health Monitor (`serena-health-monitor.sh`)

**Purpose:** Continuous monitoring with automated alerting and reporting.

**Features:**
- Checks every 60 seconds
- Detects multiple instances (threshold: 2+)
- Detects zombie processes (threshold: 1+)
- Monitors memory usage (alert at 300+ MB)
- Generates hourly health reports
- Analyzes 24-hour trends

**Usage:**

```bash
# Run in foreground (for testing)
bash .claude/serena-health-monitor.sh

# Run in background (for continuous monitoring)
nohup bash .claude/serena-health-monitor.sh > /dev/null 2>&1 &

# Stop background monitor
pkill -f serena-health-monitor
```

**Log location:** `.claude/serena-health.log`

**Sample output:**
```
[2025-09-30 17:45:00] ✅ HEALTHY | Instances: 1 | Zombies: 0 | Memory: 175MB
[2025-09-30 17:46:00] ⚠️  WARNING | Instances: 3 | Zombies: 0 | Memory: 525MB | Issues: Multiple instances: 3 High memory: 525MB
```

## Monitoring Commands

### Check Current Status

```bash
# Quick status check
bash .claude/serena-monitor.sh status

# Count running instances
pgrep -fc "serena start-mcp-server.*ruleIQ"

# Check for zombies
ps aux | grep -E "serena.*<defunct>"

# View recent metrics
cat .claude/serena-metrics.json | python3 -m json.tool | tail -50
```

### View Logs

```bash
# Monitor log (reactivation events)
tail -f .claude/serena-monitor.log

# Health log (continuous monitoring)
tail -f .claude/serena-health.log

# View last health report
grep -A 20 "Health Report" .claude/serena-health.log | tail -25
```

### Check Memory Usage

```bash
# Total memory of all Serena processes
ps aux | grep "serena start-mcp-server.*ruleIQ" | grep -v grep | awk '{sum+=$6} END {print sum/1024 "MB"}'

# Detailed per-process breakdown
ps aux | grep serena | grep -v grep
```

### Manual Cleanup

```bash
# Kill all Serena instances
pkill -f "serena start-mcp-server.*ruleIQ"

# Kill zombies
ps aux | grep -E "serena.*<defunct>" | awk '{print $2}' | xargs kill -9

# Clean up lock file
rm -f .claude/serena.lock

# Clean up old logs (rotate manually)
bash .claude/log-rotation.sh
```

## Alert Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| Instance Count | > 2 | ⚠️  WARNING - Investigate duplication |
| Zombie Count | ≥ 1 | ⚠️  WARNING - Cleanup triggered |
| Memory Usage | > 300 MB | ⚠️  WARNING - Multiple instances likely |
| Lock File Age | > 5 minutes | Stale lock removed automatically |
| Log File Size | > 1 MB | Auto-rotation triggered |

## Health Score Calculation

The health monitor calculates a health score based on warning events:

```
Health Score = 100 - (warnings × 100 / total_checks)
```

- **90-100%**: Excellent - No significant issues
- **70-89%**: Good - Occasional warnings
- **50-69%**: Fair - Frequent warnings, needs attention
- **Below 50%**: Poor - Persistent issues, immediate action required

## Troubleshooting

### Problem: Multiple instances keep appearing

**Diagnosis:**
```bash
# Check how many instances
pgrep -fc "serena start-mcp-server.*ruleIQ"

# View recent metrics
tail -20 .claude/serena-metrics.json
```

**Solution:**
```bash
# Kill all instances
pkill -f "serena start-mcp-server.*ruleIQ"

# Clear lock file
rm -f .claude/serena.lock

# Test reactivation
bash .claude/serena-monitor.sh reactivate
```

### Problem: Lock file stuck

**Diagnosis:**
```bash
# Check lock file
cat .claude/serena.lock

# Check if PID is running
kill -0 $(cat .claude/serena.lock)
```

**Solution:**
```bash
# Remove stale lock
rm -f .claude/serena.lock

# Lock will be auto-removed on next reactivation if PID is dead
```

### Problem: Metrics not logging

**Diagnosis:**
```bash
# Check if metrics file exists and is writable
ls -la .claude/serena-metrics.json

# Test metrics logging manually
bash .claude/serena-monitor.sh status
```

**Solution:**
```bash
# Recreate metrics file
echo '{"metrics": []}' > .claude/serena-metrics.json
chmod 664 .claude/serena-metrics.json
```

### Problem: High memory usage

**Diagnosis:**
```bash
# Check instance count
pgrep -fc "serena start-mcp-server.*ruleIQ"

# Check memory per process
ps aux | grep serena | grep -v grep
```

**Expected:** 1 instance × 175 MB = 175 MB total
**Warning:** 2+ instances × 175 MB = 350+ MB total

**Solution:**
```bash
# Kill duplicates (keeps newest)
pgrep -f "serena start-mcp-server.*ruleIQ" | head -n -1 | xargs kill
```

## Integration with Claude Code

### Hooks Configuration

The monitoring is integrated with Claude Code hooks:

**SessionStart** → Initializes Serena and starts monitoring
**UserPromptSubmit** → Checks status, reactivates if needed (with lock protection)

### Automatic Actions

1. **Duplicate Detection** - Kills all but the newest instance
2. **Zombie Cleanup** - Removes defunct processes automatically
3. **Lock Management** - Prevents concurrent reactivations
4. **Metrics Logging** - Tracks all status checks and reactivations
5. **Log Rotation** - Prevents unbounded log growth (1 MB threshold)

## Best Practices

1. **Monitor Regularly**
   - Run health monitor in background during development
   - Check metrics weekly: `cat .claude/serena-metrics.json`

2. **Clean Up After Sessions**
   - Serena instances should auto-cleanup when Claude exits
   - Manually verify: `pgrep -fc "serena start-mcp-server.*ruleIQ"`

3. **Review Logs**
   - Check for warning patterns in `.claude/serena-health.log`
   - Investigate any health score drops below 80%

4. **Prevent Lock Starvation**
   - If lock acquisition fails repeatedly, check for stuck processes
   - Lock timeout is 5 seconds - should rarely be hit

5. **Archive Old Metrics**
   - Metrics file keeps last 100 entries
   - For long-term analysis, archive periodically:
     ```bash
     cp .claude/serena-metrics.json .claude/serena-metrics-$(date +%Y%m%d).json
     ```

## Performance Impact

### Expected Overhead

- **Metrics logging:** ~10ms per event (Python JSON append)
- **Lock acquisition:** ~1ms (file operations)
- **Health checks:** ~50ms every 60s (process counting)
- **Total:** < 0.1% CPU, < 1 MB memory

### Optimization

The system is optimized for minimal impact:
- Lock checks use PID signals (no process spawning)
- Metrics kept to last 100 entries (bounded memory)
- Health checks run at 60s intervals (configurable)
- Logs auto-rotate at 1 MB (prevents unbounded growth)

## Future Enhancements

Potential improvements for consideration:

1. **Prometheus Export** - Expose metrics for Grafana dashboards
2. **Email Alerts** - Notify on persistent warnings
3. **Auto-Remediation** - Kill duplicates automatically without waiting
4. **Instance Registry** - Centralized tracking across multiple projects
5. **Performance Profiling** - Track Serena response times and throughput
