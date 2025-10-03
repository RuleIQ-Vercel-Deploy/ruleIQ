#!/bin/bash
# Silent Serena MCP initialization - minimal context consumption
export SERENA_SILENT=1
export RULEIQ_PROJECT_PATH="/home/omar/Documents/ruleIQ"
export SERENA_ACTIVE=true
source /home/omar/Documents/ruleIQ/.venv/bin/activate 2>/dev/null
exit 0