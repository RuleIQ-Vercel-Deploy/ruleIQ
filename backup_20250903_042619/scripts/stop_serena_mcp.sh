#!/bin/bash

# Serena MCP Server Stop Script for ruleIQ
# This script stops the running Serena MCP server

set -e

# Configuration
RULEIQ_PATH="/home/omar/Documents/ruleIQ"
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

# Stop the Serena MCP server
stop_server() {
    if [ ! -f "$PID_FILE" ]; then
        warn "No PID file found - server may not be running"
        return 0
    fi
    
    local pid=$(cat "$PID_FILE")
    
    if ps -p "$pid" > /dev/null 2>&1; then
        log "Stopping Serena MCP server (PID: $pid)..."
        
        # Try graceful shutdown first
        kill "$pid"
        
        # Wait up to 10 seconds for graceful shutdown
        local count=0
        while ps -p "$pid" > /dev/null 2>&1 && [ $count -lt 10 ]; do
            sleep 1
            count=$((count + 1))
        done
        
        # Force kill if still running
        if ps -p "$pid" > /dev/null 2>&1; then
            warn "Graceful shutdown failed, forcing termination..."
            kill -9 "$pid"
            sleep 1
        fi
        
        # Verify the process is stopped
        if ps -p "$pid" > /dev/null 2>&1; then
            error "Failed to stop Serena MCP server"
            exit 1
        else
            log "Serena MCP server stopped successfully"
        fi
    else
        warn "Server process not found - may have already stopped"
    fi
    
    # Clean up PID file
    rm -f "$PID_FILE"
}

# Main script logic
main() {
    case "${1:-stop}" in
        "stop")
            stop_server
            ;;
        "force")
            info "Force stopping all Serena MCP processes..."
            pkill -f "serena.mcp" && log "All Serena MCP processes terminated" || warn "No Serena MCP processes found"
            rm -f "$PID_FILE"
            ;;
        "help")
            echo "Usage: $0 [stop|force|help]"
            echo ""
            echo "Commands:"
            echo "  stop    - Stop the Serena MCP server gracefully (default)"
            echo "  force   - Force kill all Serena MCP processes"
            echo "  help    - Show this help message"
            ;;
        *)
            error "Unknown command: $1"
            info "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"