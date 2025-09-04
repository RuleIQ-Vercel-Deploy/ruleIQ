#!/bin/bash
# Hybrid GPU Testing Script - Run AI tests on RunPod, others locally

set -e

# Configuration
RUNPOD_HOST="${RUNPOD_HOST:-your-runpod-ip}"
RUNPOD_PORT="${RUNPOD_PORT:-22}"
RUNPOD_USER="${RUNPOD_USER:-root}"
LOCAL_PROJECT_DIR="/home/omar/Documents/ruleIQ"
REMOTE_PROJECT_DIR="/workspace/ruleiq"

echo "🚀 ruleIQ Hybrid GPU Testing"
echo "Local: $(pwd)"
echo "Remote: ${RUNPOD_USER}@${RUNPOD_HOST}:${REMOTE_PROJECT_DIR}"

# Function to sync code to RunPod
sync_to_runpod() {
    echo "📦 Syncing code to RunPod..."
    rsync -avz --delete \
        --exclude='.git' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.pytest_cache' \
        --exclude='node_modules' \
        --exclude='frontend/dist' \
        --exclude='frontend/.next' \
        "${LOCAL_PROJECT_DIR}/" \
        "${RUNPOD_USER}@${RUNPOD_HOST}:${REMOTE_PROJECT_DIR}/"
}

# Function to run tests on RunPod
run_gpu_tests() {
    local test_pattern="$1"
    local extra_args="$2"
    
    echo "🔥 Running GPU tests: $test_pattern"
    ssh "${RUNPOD_USER}@${RUNPOD_HOST}" -p "${RUNPOD_PORT}" << EOF
cd ${REMOTE_PROJECT_DIR}
source /opt/ruleiq-env/bin/activate
export CUDA_VISIBLE_DEVICES=0
export PYTEST_GPU_ENABLED=true

# Run the tests
python -m pytest ${test_pattern} ${extra_args} \
    -v --tb=short \
    -n 4 \
    --benchmark-only \
    --durations=10
EOF
}

# Function to run tests locally
run_local_tests() {
    local test_pattern="$1"
    local extra_args="$2"
    
    echo "💻 Running local tests: $test_pattern"
    cd "${LOCAL_PROJECT_DIR}"
    python -m pytest ${test_pattern} ${extra_args} \
        -v --tb=short \
        --maxfail=5
}

# Main execution
case "${1:-all}" in
    "sync")
        sync_to_runpod
        ;;
    "ai")
        sync_to_runpod
        run_gpu_tests "tests/integration/test_ai_optimization_endpoints.py tests/unit/services/test_ai_*.py" "--benchmark-sort=mean"
        ;;
    "performance")
        sync_to_runpod
        run_gpu_tests "tests/performance/" "--benchmark-autosave"
        ;;
    "security")
        run_local_tests "tests/security/" ""
        ;;
    "business")
        run_local_tests "tests/test_services.py::TestBusinessService" ""
        ;;
    "evidence")
        run_local_tests "tests/integration/test_evidence_flow.py" ""
        ;;
    "failed39")
        echo "🎯 Running the original 39 failed tests with GPU acceleration..."
        sync_to_runpod
        
        # AI tests on GPU
        run_gpu_tests "tests/integration/test_ai_optimization_endpoints.py" ""
        
        # Performance tests on GPU  
        run_gpu_tests "tests/performance/" ""
        
        # Other tests locally
        run_local_tests "tests/security/test_authentication.py::TestAuthenticationSecurity::test_session_management_security" ""
        run_local_tests "tests/test_services.py::TestBusinessService" ""
        run_local_tests "tests/integration/test_evidence_flow.py::TestAPIEndpointsIntegration::test_business_profile_to_evidence_workflow" ""
        ;;
    "all")
        echo "🔄 Running full test suite with GPU acceleration..."
        sync_to_runpod
        
        # Run AI and performance tests on GPU
        run_gpu_tests "tests/integration/test_ai_*.py tests/performance/ tests/unit/services/test_ai_*.py" "--cov=services/ai"
        
        # Run remaining tests locally
        run_local_tests "tests/security/ tests/test_services.py tests/integration/test_evidence_flow.py" "--cov=api --cov=database"
        ;;
    *)
        echo "Usage: $0 [sync|ai|performance|security|business|evidence|failed39|all]"
        echo ""
        echo "Commands:"
        echo "  sync        - Sync code to RunPod"
        echo "  ai          - Run AI tests on GPU"
        echo "  performance - Run performance tests on GPU"
        echo "  security    - Run security tests locally"
        echo "  business    - Run business service tests locally"
        echo "  evidence    - Run evidence flow tests locally"
        echo "  failed39    - Run the original 39 failed tests optimally"
        echo "  all         - Run full test suite with optimal distribution"
        exit 1
        ;;
esac

echo "✅ Testing complete!"
