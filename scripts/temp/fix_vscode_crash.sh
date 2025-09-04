#!/bin/bash

echo "🔧 Fixing VS Code Error 133 Crash Issue"
echo "======================================="

# 1. Clear VS Code caches
echo "1. Clearing VS Code caches..."
rm -rf ~/.config/Code/Cache/* 2>/dev/null
rm -rf ~/.config/Code/CachedData/* 2>/dev/null
rm -rf ~/.config/Code/GPUCache/* 2>/dev/null
rm -rf ~/.config/Code/Service\ Worker/CacheStorage/* 2>/dev/null
rm -rf ~/.config/Code/Service\ Worker/ScriptCache/* 2>/dev/null
rm -rf ~/.config/Code/Crashpad/* 2>/dev/null

# 2. Clear extension host cache
echo "2. Clearing extension host cache..."
rm -rf ~/.config/Code/CachedExtensionVSIXs/* 2>/dev/null
rm -rf ~/.config/Code/CachedExtensions/* 2>/dev/null

# 3. Reset workspace storage for this project
echo "3. Resetting workspace storage..."
WORKSPACE_ID=$(echo -n "file:///home/omar/Documents/ruleIQ" | md5sum | cut -d' ' -f1)
rm -rf ~/.config/Code/User/workspaceStorage/*$WORKSPACE_ID* 2>/dev/null

# 4. Disable GPU acceleration (common cause of error 133)
echo "4. Creating VS Code launch configuration without GPU..."
cat > ~/vscode-no-gpu.sh << 'EOF'
#!/bin/bash
code --disable-gpu --disable-gpu-sandbox --disable-software-rasterizer "$@"
EOF
chmod +x ~/vscode-no-gpu.sh

# 5. Increase file watcher limit
echo "5. Increasing file watcher limit..."
echo "fs.inotify.max_user_watches=524288" | sudo tee -a /etc/sysctl.conf > /dev/null
sudo sysctl -p > /dev/null 2>&1

# 6. Clear Python extension cache
echo "6. Clearing Python extension cache..."
rm -rf ~/.cache/ms-python.python/* 2>/dev/null
rm -rf ~/.cache/pylance/* 2>/dev/null

# 7. Reset VS Code settings for this workspace
echo "7. Creating clean VS Code settings..."
mkdir -p .vscode
cat > .vscode/settings.json.clean << 'EEOF'
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.languageServer": "Pylance",
  "files.watcherExclude": {
    "**/.git/objects/**": true,
    "**/.git/subtree-cache/**": true,
    "**/node_modules/**": true,
    "**/.venv/**": true,
    "**/__pycache__/**": true,
    "**/.pytest_cache/**": true
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/bower_components": true,
    "**/*.code-search": true,
    "**/.venv": true,
    "**/__pycache__": true
  },
  "extensions.autoUpdate": false,
  "extensions.autoCheckUpdates": false,
  "telemetry.telemetryLevel": "off",
  "workbench.editor.limit.enabled": true,
  "workbench.editor.limit.value": 10,
  "terminal.integrated.gpuAcceleration": "off",
  "window.zoomLevel": 0,
  "editor.maxTokenizationLineLength": 20000,
  "files.maxMemoryForLargeFilesMB": 4096
}
EEOF

echo ""
echo "✅ Fixes applied!"
echo ""
echo "📝 To complete the fix:"
echo "1. Close VS Code completely"
echo "2. Run VS Code with: ~/vscode-no-gpu.sh /home/omar/Documents/ruleIQ"
echo "   OR"
echo "   code --disable-gpu /home/omar/Documents/ruleIQ"
echo ""
echo "3. If still crashing, try disabling extensions:"
echo "   code --disable-extensions /home/omar/Documents/ruleIQ"
echo ""
echo "4. Once stable, re-enable extensions one by one to find the problematic one"
echo ""
echo "Alternative: Use the workspace file:"
echo "   code --disable-gpu ruleiq.code-workspace"