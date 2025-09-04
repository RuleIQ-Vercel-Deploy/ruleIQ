#!/bin/bash

# Serena MCP Server Startup Script for ruleIQ
# This script starts the Serena MCP server with ruleIQ-specific configuration
# for intelligent development assistance through Claude Desktop

set -e

# Configuration
SERENA_PATH="/home/omar/serena"
RULEIQ_PATH="/home/omar/Documents/ruleIQ"
LOG_FILE="$RULEIQ_PATH/serena-mcp.log"
PID_FILE="$RULEIQ_PATH/.serena_mcp.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
log() {
    echo -e "${GREEN}[Serena MCP]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[Serena MCP WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[Serena MCP ERROR]${NC} $1"
}

info() {
    echo -e "${BLUE}[Serena MCP INFO]${NC} $1"
}

# Check if Serena is installed
check_serena_installation() {
    if [ ! -d "$SERENA_PATH" ]; then
        error "Serena installation not found at $SERENA_PATH"
        error "Please ensure Serena MCP Server is installed"
        exit 1
    fi
    
    if [ ! -f "$SERENA_PATH/src/serena/mcp.py" ]; then
        error "Serena MCP module not found"
        error "Please check your Serena installation"
        exit 1
    fi
    
    log "Serena installation verified"
}

# Check if ruleIQ project configuration exists
check_project_config() {
    if [ ! -f "$RULEIQ_PATH/.serena/project.yml" ]; then
        error "ruleIQ Serena configuration not found"
        error "Expected: $RULEIQ_PATH/.serena/project.yml"
        error "Please run the project configuration setup first"
        exit 1
    fi
    
    log "ruleIQ project configuration found"
}

# Check if MCP server is already running
check_running_server() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            warn "Serena MCP server is already running (PID: $pid)"
            info "Use 'scripts/stop_serena_mcp.sh' to stop the server first"
            exit 1
        else
            # PID file exists but process is not running, clean up
            rm -f "$PID_FILE"
        fi
    fi
}

# Start the Serena MCP server
start_server() {
    log "Starting Serena MCP server for ruleIQ..."
    
    # Change to Serena directory
    cd "$SERENA_PATH"
    
    # Start the server in the background
    nohup python -m serena.mcp \
        --context ide-assistant \
        --project "$RULEIQ_PATH" \
        --config "$RULEIQ_PATH/.serena/project.yml" \
        > "$LOG_FILE" 2>&1 &
    
    local server_pid=$!
    echo "$server_pid" > "$PID_FILE"
    
    # Wait a moment and check if the server started successfully
    sleep 3
    
    if ps -p "$server_pid" > /dev/null 2>&1; then
        log "Serena MCP server started successfully"
        info "PID: $server_pid"
        info "Log file: $LOG_FILE"
        info "Project: $RULEIQ_PATH"
        info "Context: ide-assistant"
        echo ""
        info "To connect from Claude Desktop, use this MCP server configuration:"
        echo ""
        echo "  {\"command\": \"python\", \"args\": [\"-m\", \"serena.mcp\", \"--context\", \"ide-assistant\", \"--project\", \"$RULEIQ_PATH\"], \"cwd\": \"$SERENA_PATH\"}"
        echo ""
    else
        error "Failed to start Serena MCP server"
        error "Check the log file for details: $LOG_FILE"
        rm -f "$PID_FILE"
        exit 1
    fi
}

# Display server status
show_status() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            log "Serena MCP server is running (PID: $pid)"
            info "Log file: $LOG_FILE"
            info "Recent log entries:"
            tail -10 "$LOG_FILE" 2>/dev/null || echo "No recent log entries"
        else
            warn "PID file exists but server is not running"
            rm -f "$PID_FILE"
        fi
    else
        info "Serena MCP server is not running"
    fi
}

# Main script logic
main() {
    case "${1:-start}" in
        "start")
            log "Initializing Serena MCP server for ruleIQ..."
            check_serena_installation
            check_project_config
            check_running_server
            start_server
            ;;
        "status")
            show_status
            ;;
        "logs")
            if [ -f "$LOG_FILE" ]; then
                info "Showing recent Serena MCP logs..."
                tail -20 "$LOG_FILE"
            else
                warn "No log file found at $LOG_FILE"
            fi
            ;;
        "help")
            echo "Usage: $0 [start|status|logs|help]"
            echo ""
            echo "Commands:"
            echo "  start   - Start the Serena MCP server (default)"
            echo "  status  - Show server status"
            echo "  logs    - Show recent log entries"
            echo "  help    - Show this help message"
            echo ""
            echo "The server will be configured for ruleIQ development with:"
            echo "  - Context: ide-assistant"
            echo "  - Project: $RULEIQ_PATH"
            echo "  - Config: $RULEIQ_PATH/.serena/project.yml"
            ;;
        *)
            error "Unknown command: $1"
            info "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Handle script interruption
cleanup() {
    warn "Script interrupted"
    exit 1
}

trap cleanup SIGINT SIGTERM

# Run main function with all arguments
main "$@"