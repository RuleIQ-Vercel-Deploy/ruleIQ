#!/bin/bash
# Sync ruleIQ code to RunPod GPU instance

# Configuration - UPDATE THESE WITH YOUR RUNPOD DETAILS
RUNPOD_IP="your-runpod-ip"  # Get this from RunPod dashboard
RUNPOD_PORT="22"            # Usually 22, check RunPod dashboard
RUNPOD_USER="root"          # Usually root

LOCAL_DIR="/home/omar/Documents/ruleIQ"
REMOTE_DIR="/workspace/ruleiq"

echo "🚀 Syncing ruleIQ to RunPod GPU..."
echo "Local: $LOCAL_DIR"
echo "Remote: $RUNPOD_USER@$RUNPOD_IP:$REMOTE_DIR"

# Sync code (excluding unnecessary files)
rsync -avz --progress --delete \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='node_modules' \
    --exclude='frontend/dist' \
    --exclude='frontend/.next' \
    --exclude='*.log' \
    "$LOCAL_DIR/" \
    "$RUNPOD_USER@$RUNPOD_IP:$REMOTE_DIR/"

echo "✅ Sync complete!"

# Optional: Run tests immediately after sync
read -p "🧪 Run tests on RunPod now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🚀 Running tests on RunPod..."
    ssh "$RUNPOD_USER@$RUNPOD_IP" -p "$RUNPOD_PORT" << 'EOF'
cd /workspace/ruleiq
./run_tests.sh
EOF
fi
