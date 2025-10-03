#!/usr/bin/bash
# Serena Log Rotation Script
# Rotates logs when they exceed size limits

CLAUDE_DIR="/home/omar/Documents/ruleIQ/.claude"
MAX_SIZE=1048576   # 1MB in bytes (more aggressive rotation)
KEEP_ARCHIVES=5    # Number of old logs to keep

# Function to rotate a single log file
rotate_log() {
    local log_file="$1"
    local log_name=$(basename "$log_file")

    if [ ! -f "$log_file" ]; then
        return 0
    fi

    # Get file size (cross-platform)
    local size=$(stat -f%z "$log_file" 2>/dev/null || stat -c%s "$log_file" 2>/dev/null || echo 0)

    if [ "$size" -gt "$MAX_SIZE" ]; then
        echo "🔄 Rotating $log_name ($(numfmt --to=iec-i --suffix=B $size 2>/dev/null || echo ${size}B))"

        # Rotate existing archives
        for i in $(seq $((KEEP_ARCHIVES - 1)) -1 1); do
            if [ -f "$log_file.$i.gz" ]; then
                mv "$log_file.$i.gz" "$log_file.$((i + 1)).gz"
            fi
        done

        # Compress and archive current log
        gzip -c "$log_file" > "$log_file.1.gz"

        # Truncate current log
        > "$log_file"

        # Remove old archives beyond keep limit
        find "$CLAUDE_DIR" -name "${log_name}.*.gz" -type f | sort -V | head -n -$KEEP_ARCHIVES | xargs -r rm

        echo "✅ $log_name rotated successfully"
    fi
}

# Main execution
main() {
    echo "📦 Starting log rotation check..."

    # Rotate all Serena logs
    rotate_log "$CLAUDE_DIR/serena-init.log"
    rotate_log "$CLAUDE_DIR/serena-monitor.log"

    # Clean up very old archives (> 30 days)
    find "$CLAUDE_DIR" -name "*.log.*.gz" -type f -mtime +30 -delete

    echo "✅ Log rotation check complete"
}

# Run if executed directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi