#!/bin/bash

echo "🔧 Fixing IDE Crashes with AMD GPU (Radeon Vega)"
echo "=================================================="
echo ""

# Detect which IDE we're dealing with
detect_ide() {
    if command -v code &> /dev/null; then
        echo "✓ VS Code detected"
        IDE="vscode"
    fi
    
    if command -v cursor &> /dev/null; then
        echo "✓ Cursor detected"
        IDE="cursor"
    fi
}

detect_ide

# 1. Clear GPU caches for both VS Code and Cursor
echo "1. Clearing GPU and shader caches..."
rm -rf ~/.config/Code/GPUCache/* 2>/dev/null
rm -rf ~/.config/Code/Cache/* 2>/dev/null
rm -rf ~/.config/Code/CachedData/* 2>/dev/null
rm -rf ~/.config/Code/Service\ Worker/CacheStorage/* 2>/dev/null
rm -rf ~/.config/Code/Crashpad/* 2>/dev/null

# Clear Cursor caches too
rm -rf ~/.config/Cursor/GPUCache/* 2>/dev/null
rm -rf ~/.config/Cursor/Cache/* 2>/dev/null
rm -rf ~/.config/Cursor/CachedData/* 2>/dev/null
rm -rf ~/.config/Cursor/Service\ Worker/CacheStorage/* 2>/dev/null
rm -rf ~/.config/Cursor/Crashpad/* 2>/dev/null

# Clear AMD shader cache
echo "2. Clearing AMD GPU shader cache..."
rm -rf ~/.cache/mesa_shader_cache/* 2>/dev/null
rm -rf ~/.cache/radv_shader_cache/* 2>/dev/null

# 2. Set AMD GPU environment variables
echo "3. Creating AMD GPU environment configuration..."
cat > ~/.config/amd_gpu_ide_fix.sh << 'EOF'
#!/bin/bash
# AMD GPU Stability Configuration for IDEs

# Disable GPU compositing for Electron apps
export DISABLE_LAYER_AMD_SWITCHABLE_GRAPHICS_1=1
export ELECTRON_DISABLE_GPU_COMPOSITING=1

# Use software rendering for WebGL
export WEBKIT_DISABLE_COMPOSITING_MODE=1

# AMD specific - disable some problematic features
export AMD_DEBUG=nodcc,nodpbb,nodfsm
export RADV_DEBUG=nocompute

# Mesa driver optimizations for stability
export MESA_GLSL_CACHE_DISABLE=0
export MESA_SHADER_CACHE_DISABLE=0
export MESA_GL_VERSION_OVERRIDE=4.5
export MESA_GLSL_VERSION_OVERRIDE=450

# Limit GPU memory usage
export RADV_PERFTEST=nosam

# Force single-threaded rendering for stability
export mesa_glthread=false
export GALLIUM_THREAD=0

# Disable hardware acceleration features that can cause crashes
export LIBGL_ALWAYS_SOFTWARE=0
export LIBGL_DRI3_DISABLE=1

# Run the command passed as arguments
exec "$@"
EOF

chmod +x ~/.config/amd_gpu_ide_fix.sh

# 3. Create launcher scripts for VS Code
echo "4. Creating VS Code launcher without GPU acceleration..."
cat > ~/vscode-amd-fix.sh << 'EOF'
#!/bin/bash
# Launch VS Code with AMD GPU crash prevention

# Source AMD GPU fixes
source ~/.config/amd_gpu_ide_fix.sh

# Launch VS Code with disabled GPU features
exec code \
    --disable-gpu \
    --disable-gpu-compositing \
    --disable-gpu-sandbox \
    --disable-software-rasterizer \
    --disable-dev-shm-usage \
    --no-sandbox \
    --disable-features=VaapiVideoDecoder \
    --disable-features=UseChromeOSDirectVideoDecoder \
    --use-gl=desktop \
    --disable-features=VaapiIgnoreDriverChecks \
    --ignore-gpu-blacklist \
    --disable-accelerated-2d-canvas \
    "$@"
EOF

chmod +x ~/vscode-amd-fix.sh

# 4. Create launcher script for Cursor
echo "5. Creating Cursor launcher without GPU acceleration..."
cat > ~/cursor-amd-fix.sh << 'EOF'
#!/bin/bash
# Launch Cursor with AMD GPU crash prevention

# Source AMD GPU fixes
source ~/.config/amd_gpu_ide_fix.sh

# Launch Cursor with disabled GPU features
exec cursor \
    --disable-gpu \
    --disable-gpu-compositing \
    --disable-gpu-sandbox \
    --disable-software-rasterizer \
    --disable-dev-shm-usage \
    --no-sandbox \
    --disable-features=VaapiVideoDecoder \
    --disable-features=UseChromeOSDirectVideoDecoder \
    --use-gl=desktop \
    --disable-features=VaapiIgnoreDriverChecks \
    --ignore-gpu-blacklist \
    --disable-accelerated-2d-canvas \
    "$@"
EOF

chmod +x ~/cursor-amd-fix.sh

# 5. Update VS Code settings to disable GPU
echo "6. Updating VS Code settings for GPU stability..."
mkdir -p ~/.config/Code/User
if [ -f ~/.config/Code/User/settings.json ]; then
    cp ~/.config/Code/User/settings.json ~/.config/Code/User/settings.json.backup
fi

cat > ~/.config/Code/User/gpu-settings.json << 'EOF'
{
    "disable-hardware-acceleration": true,
    "terminal.integrated.gpuAcceleration": "off",
    "editor.disableLayerHinting": true,
    "window.disableHardwareAcceleration": true,
    "workbench.colorTheme": "Default Dark+",
    "extensions.ignoreRecommendations": true,
    "telemetry.telemetryLevel": "off",
    "workbench.editor.limit.enabled": true,
    "workbench.editor.limit.value": 10,
    "editor.maxTokenizationLineLength": 20000,
    "files.maxMemoryForLargeFilesMB": 4096
}
EOF

# 6. Create Xorg configuration for AMD GPU (optional, requires sudo)
echo "7. Creating Xorg configuration for AMD GPU stability..."
cat > /tmp/20-amdgpu.conf << 'EOF'
Section "Device"
    Identifier "AMD"
    Driver "amdgpu"
    Option "TearFree" "true"
    Option "DRI" "3"
    Option "AccelMethod" "glamor"
    Option "SWCursor" "true"
EndSection
EOF

echo ""
echo "📝 Optional: Copy Xorg configuration (requires sudo):"
echo "   sudo cp /tmp/20-amdgpu.conf /etc/X11/xorg.conf.d/"
echo ""

# 7. Create desktop entries for the fixed launchers
echo "8. Creating desktop entries..."
cat > ~/.local/share/applications/vscode-amd-fix.desktop << EOF
[Desktop Entry]
Name=VS Code (AMD GPU Fix)
Comment=Code Editor with AMD GPU crash prevention
GenericName=Text Editor
Exec=$HOME/vscode-amd-fix.sh %F
Icon=vscode
Type=Application
StartupNotify=false
Categories=TextEditor;Development;IDE;
MimeType=text/plain;
Actions=new-empty-window;
Keywords=vscode;
EOF

cat > ~/.local/share/applications/cursor-amd-fix.desktop << EOF
[Desktop Entry]
Name=Cursor (AMD GPU Fix)
Comment=AI Code Editor with AMD GPU crash prevention
GenericName=Text Editor
Exec=$HOME/cursor-amd-fix.sh %F
Icon=cursor
Type=Application
StartupNotify=false
Categories=TextEditor;Development;IDE;
MimeType=text/plain;
Actions=new-empty-window;
Keywords=cursor;
EOF

# 8. Check current kernel parameters
echo "9. Checking kernel parameters..."
if ! grep -q "amdgpu.ppfeaturemask" /proc/cmdline; then
    echo ""
    echo "📝 Optional: Add kernel parameters for AMD GPU stability"
    echo "   Edit /etc/default/grub and add to GRUB_CMDLINE_LINUX_DEFAULT:"
    echo "   amdgpu.ppfeaturemask=0xffffffff amdgpu.dc=1 amdgpu.dpm=1"
    echo "   Then run: sudo update-grub"
fi

echo ""
echo "✅ AMD GPU fixes applied!"
echo ""
echo "🚀 How to launch your IDE with GPU fixes:"
echo ""
echo "For VS Code:"
echo "  ~/vscode-amd-fix.sh /home/omar/Documents/ruleIQ"
echo ""
echo "For Cursor:"
echo "  ~/cursor-amd-fix.sh /home/omar/Documents/ruleIQ"
echo ""
echo "Or use the desktop shortcuts in your application menu!"
echo ""
echo "⚠️  If crashes persist:"
echo "1. Reboot your system to clear GPU memory"
echo "2. Update your kernel: sudo apt update && sudo apt upgrade"
echo "3. Try the Mesa drivers from PPA:"
echo "   sudo add-apt-repository ppa:kisak/kisak-mesa"
echo "   sudo apt update && sudo apt upgrade"
echo ""
echo "📊 Monitor GPU usage with: watch -n 1 'radeontop'"
echo "📊 Check for crashes: journalctl -xe | grep -i 'gpu\|crash'"