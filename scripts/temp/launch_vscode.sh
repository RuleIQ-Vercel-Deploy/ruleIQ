#!/bin/bash

# Safe launcher for VSCode with RuleIQ project
# Prevents GPU-related crashes on AMD systems

echo "🚀 Launching VSCode for RuleIQ (GPU-safe mode)..."

# Set environment variables
export DISABLE_WAYLAND=1
export ELECTRON_DISABLE_GPU=1
export ELECTRON_NO_ATTACH_CONSOLE=1

# Kill any existing VSCode processes that might be stuck
pkill -f "code.*ruleIQ" 2>/dev/null

# Small delay
sleep 1

# Launch VSCode with all safety flags
/usr/bin/code \
    --disable-gpu \
    --disable-gpu-compositing \
    --disable-software-rasterizer \
    --disable-gpu-sandbox \
    --disable-dev-shm-usage \
    --disable-features=VaapiVideoDecoder \
    --use-gl=swiftshader \
    --no-sandbox \
    --verbose \
    /home/omar/Documents/ruleIQ 2>&1 | tee /tmp/vscode-ruleiq.log &

echo ""
echo "✅ VSCode launched in safe mode"
echo "📋 Logs are being written to: /tmp/vscode-ruleiq.log"
echo ""
echo "If VSCode crashes, check the log file for errors."
echo "You can also try: code --disable-gpu /home/omar/Documents/ruleIQ"