#!/bin/bash
# RunPod GPU Environment Setup for ruleIQ Backend Testing
# Run this script on your RunPod instance to set up the testing environment

set -e

echo "🚀 Setting up ruleIQ Backend Testing Environment on RunPod GPU..."

# Update system packages
echo "📦 Updating system packages..."
apt-get update && apt-get upgrade -y

# Install essential tools
echo "🔧 Installing essential tools..."
apt-get install -y \
    git \
    curl \
    wget \
    vim \
    htop \
    tmux \
    postgresql-client \
    redis-tools \
    build-essential \
    software-properties-common

# Install Python 3.11+ if not available
echo "🐍 Setting up Python environment..."
if ! command -v python3.11 &> /dev/null; then
    add-apt-repository ppa:deadsnakes/ppa -y
    apt-get update
    apt-get install -y python3.11 python3.11-venv python3.11-dev python3-pip
fi

# Create Python virtual environment
echo "📁 Creating Python virtual environment..."
python3.11 -m venv /opt/ruleiq-env
source /opt/ruleiq-env/bin/activate

# Upgrade pip and install essential packages
pip install --upgrade pip setuptools wheel

# Install PyTorch with CUDA support for GPU acceleration
echo "🔥 Installing PyTorch with CUDA support..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Install Google AI SDK for Gemini models
echo "🤖 Installing AI dependencies..."
pip install google-generativeai google-cloud-aiplatform

# Install testing and development dependencies
echo "🧪 Installing testing dependencies..."
pip install \
    pytest \
    pytest-asyncio \
    pytest-cov \
    pytest-xdist \
    pytest-benchmark \
    httpx \
    fastapi \
    uvicorn \
    sqlalchemy \
    asyncpg \
    psycopg2-binary \
    redis \
    python-jose \
    passlib \
    bcrypt

# Install additional performance tools
pip install \
    numpy \
    pandas \
    aiofiles \
    asyncio-throttle \
    memory-profiler \
    line-profiler

# Set up environment variables
echo "⚙️ Setting up environment variables..."
cat > /opt/ruleiq-env/.env << EOF
# RunPod GPU Configuration
CUDA_VISIBLE_DEVICES=0
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
OMP_NUM_THREADS=4

# Testing Configuration
PYTEST_WORKERS=4
PYTEST_GPU_ENABLED=true
AI_MODEL_CACHE_SIZE=1000
AI_BATCH_SIZE=32

# Database Configuration (update with your actual DB)
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database
REDIS_URL=redis://localhost:6379/0

# AI Configuration
GOOGLE_API_KEY=your_api_key_here
AI_MODEL_PROVIDER=google
AI_MODEL_NAME=gemini-2.5-flash
AI_ENABLE_GPU=true
EOF

# Create activation script
cat > /opt/ruleiq-env/activate_ruleiq.sh << 'EOF'
#!/bin/bash
source /opt/ruleiq-env/bin/activate
export $(cat /opt/ruleiq-env/.env | xargs)
echo "🚀 ruleIQ Environment Activated on RunPod GPU!"
echo "GPU Status:"
nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader,nounits
EOF

chmod +x /opt/ruleiq-env/activate_ruleiq.sh

# Install NVIDIA monitoring tools
echo "📊 Setting up GPU monitoring..."
pip install gpustat nvidia-ml-py3

# Create test runner script
cat > /opt/ruleiq-env/run_gpu_tests.sh << 'EOF'
#!/bin/bash
source /opt/ruleiq-env/activate_ruleiq.sh

echo "🧪 Running ruleIQ Tests on GPU..."
echo "Available GPUs:"
gpustat

# Run tests with GPU optimization
cd /workspace/ruleiq

# Run AI-related tests with GPU acceleration
echo "🤖 Running AI optimization tests..."
pytest tests/integration/test_ai_optimization_endpoints.py \
    tests/unit/services/test_ai_*.py \
    -v --tb=short \
    -n ${PYTEST_WORKERS:-4} \
    --benchmark-only \
    --cov=services/ai \
    --cov-report=html:gpu_test_coverage

# Run performance tests
echo "⚡ Running performance tests..."
pytest tests/performance/ \
    -v --tb=short \
    -n ${PYTEST_WORKERS:-4} \
    --benchmark-sort=mean

# Run full test suite with parallel execution
echo "🔄 Running full test suite..."
pytest tests/ \
    -v --tb=short \
    -n ${PYTEST_WORKERS:-4} \
    --maxfail=10 \
    --durations=20 \
    --cov=. \
    --cov-report=html:full_gpu_coverage \
    --cov-report=term-missing
EOF

chmod +x /opt/ruleiq-env/run_gpu_tests.sh

echo "✅ RunPod GPU environment setup complete!"
echo ""
echo "🚀 To activate the environment:"
echo "source /opt/ruleiq-env/activate_ruleiq.sh"
echo ""
echo "🧪 To run GPU-accelerated tests:"
echo "/opt/ruleiq-env/run_gpu_tests.sh"
echo ""
echo "📊 To monitor GPU usage:"
echo "watch -n 1 gpustat"
