#!/bin/bash
# Quick RunPod Setup for ruleIQ Testing
# Copy this script to your RunPod instance and run it

set -e

echo "🚀 Setting up ruleIQ on RunPod GPU..."

# Update and install essentials
apt-get update
apt-get install -y git curl wget python3-pip postgresql-client redis-tools htop

# Install Python dependencies
pip install --upgrade pip
pip install \
    pytest pytest-asyncio pytest-xdist pytest-benchmark \
    fastapi uvicorn sqlalchemy asyncpg psycopg2-binary \
    redis python-jose passlib bcrypt httpx \
    google-generativeai torch

# Set up environment
export CUDA_VISIBLE_DEVICES=0
export PYTEST_WORKERS=4
export AI_ENABLE_GPU=true

# Create test runner
cat > run_tests.sh << 'EOF'
#!/bin/bash
echo "🧪 Running ruleIQ tests on GPU..."

# Show GPU status
nvidia-smi --query-gpu=name,memory.used,memory.total --format=csv,noheader

# Run the original 39 failed tests with GPU acceleration
echo "🎯 Running AI optimization tests..."
python -m pytest tests/integration/test_ai_optimization_endpoints.py -v -n 4

echo "⚡ Running performance tests..."
python -m pytest tests/performance/ -v -n 4 --benchmark-only

echo "🔒 Running security tests..."
python -m pytest tests/security/test_authentication.py::TestAuthenticationSecurity::test_session_management_security -v

echo "💼 Running business service tests..."
python -m pytest tests/test_services.py::TestBusinessService -v

echo "📋 Running evidence flow tests..."
python -m pytest tests/integration/test_evidence_flow.py::TestAPIEndpointsIntegration::test_business_profile_to_evidence_workflow -v

echo "✅ GPU testing complete!"
EOF

chmod +x run_tests.sh

echo "✅ RunPod setup complete!"
echo "🚀 To run tests: ./run_tests.sh"
echo "📊 To monitor GPU: watch -n 1 nvidia-smi"
