#!/bin/bash

# Fix for VSCode crashes on AMD GPUs (Linux)
# This disables GPU acceleration which causes crashes on some AMD drivers

echo "🔧 Fixing VSCode GPU crash issue..."
echo ""
echo "This script will apply workarounds for AMD GPU crashes in VSCode"
echo ""

# Method 1: Add command line flags to VSCode desktop entry
echo "Method 1: Updating VSCode desktop entry..."
DESKTOP_FILE="$HOME/.local/share/applications/code.desktop"
if [ -f "/usr/share/applications/code.desktop" ]; then
    cp /usr/share/applications/code.desktop "$DESKTOP_FILE"
    sed -i 's/Exec=\/usr\/bin\/code/Exec=\/usr\/bin\/code --disable-gpu --disable-software-rasterizer/g' "$DESKTOP_FILE"
    echo "✓ Updated desktop entry with GPU disable flags"
fi

# Method 2: Create a wrapper script
echo ""
echo "Method 2: Creating VSCode wrapper script..."
cat > ~/vscode-no-gpu <<'EOF'
#!/bin/bash
# VSCode launcher with GPU acceleration disabled
code --disable-gpu --disable-software-rasterizer "$@"
EOF
chmod +x ~/vscode-no-gpu
echo "✓ Created ~/vscode-no-gpu wrapper script"

# Method 3: Set environment variables
echo ""
echo "Method 3: Setting environment variables..."
cat >> ~/.bashrc <<'EOF'

# VSCode AMD GPU fix
export DISABLE_WAYLAND=1
export ELECTRON_DISABLE_GPU=1
EOF
echo "✓ Added environment variables to ~/.bashrc"

# Method 4: VSCode settings
echo ""
echo "Method 4: Updating VSCode settings..."
VSCODE_SETTINGS="$HOME/.config/Code/User/settings.json"
mkdir -p "$HOME/.config/Code/User"

if [ -f "$VSCODE_SETTINGS" ]; then
    # Backup existing settings
    cp "$VSCODE_SETTINGS" "${VSCODE_SETTINGS}.backup"
fi

# Create or update settings
cat > "$VSCODE_SETTINGS" <<'EOF'
{
    "disable-hardware-acceleration": true,
    "disable-color-correct-rendering": true,
    "disable-chromium-sandbox": true,
    "window.titleBarStyle": "native",
    "workbench.colorTheme": "Default Dark+",
    "terminal.integrated.gpuAcceleration": "off",
    "editor.accessibilitySupport": "off"
}
EOF
echo "✓ Updated VSCode settings to disable GPU features"

# Method 5: Alternative launcher
echo ""
echo "Method 5: Creating alternative launcher..."
cat > ~/vscode-safe <<'EOF'
#!/bin/bash
# Safe mode VSCode launcher for AMD GPU issues
export DISABLE_WAYLAND=1
export ELECTRON_DISABLE_GPU=1
/usr/bin/code \
    --disable-gpu \
    --disable-software-rasterizer \
    --disable-gpu-sandbox \
    --disable-dev-shm-usage \
    --no-sandbox \
    "$@"
EOF
chmod +x ~/vscode-safe
echo "✓ Created ~/vscode-safe launcher"

echo ""
echo "========================================="
echo "✅ VSCode GPU fixes applied!"
echo ""
echo "🚀 To launch VSCode without GPU issues, use one of these methods:"
echo ""
echo "1. From terminal: ~/vscode-no-gpu"
echo "2. Safe mode: ~/vscode-safe"  
echo "3. Regular launch should work after restart"
echo ""
echo "⚠️  IMPORTANT: "
echo "   - Close all VSCode instances"
echo "   - Log out and log back in (or run: source ~/.bashrc)"
echo "   - Try launching VSCode with: ~/vscode-safe"
echo ""
echo "If crashes persist, try:"
echo "   code --disable-gpu --verbose"
echo "to see detailed error messages"
echo "========================================="