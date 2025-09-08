#!/bin/bash
# GPU Tunneling Setup - Forward RunPod GPU to local environment

set -e

RUNPOD_HOST="${RUNPOD_HOST:-your-runpod-ip}"
RUNPOD_PORT="${RUNPOD_PORT:-22}"
RUNPOD_USER="${RUNPOD_USER:-root}"

echo "🔗 Setting up GPU tunnel from RunPod to local environment..."

# Create SSH config for easy connection
cat > ~/.ssh/runpod_config << EOF
Host runpod-gpu
    HostName ${RUNPOD_HOST}
    Port ${RUNPOD_PORT}
    User ${RUNPOD_USER}
    ServerAliveInterval 60
    ServerAliveCountMax 3
    LocalForward 8000 localhost:8000
    LocalForward 6379 localhost:6379
    LocalForward 5432 localhost:5432
    RemoteForward 8001 localhost:8001
EOF

echo "📡 Starting GPU service tunnel..."

# Start AI service on RunPod that accepts requests
ssh -F ~/.ssh/runpod_config runpod-gpu << 'EOF'
cd /workspace/ruleiq
source /opt/ruleiq-env/bin/activate

# Start AI service endpoint
cat > gpu_ai_service.py << 'PYTHON'
import asyncio
import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import torch
from typing import Dict, Any, Optional

app = FastAPI(title="RunPod GPU AI Service")

class AIRequest(BaseModel):
    prompt: str
    model: str = "gemini-2.5-flash"
    max_tokens: int = 1000
    temperature: float = 0.1

class AIResponse(BaseModel):
    response: str
    model_used: str
    gpu_used: bool
    processing_time: float

@app.get("/health")
async def health_check():
    gpu_available = torch.cuda.is_available()
    gpu_count = torch.cuda.device_count() if gpu_available else 0
    return {
        "status": "healthy",
        "gpu_available": gpu_available,
        "gpu_count": gpu_count,
        "gpu_name": torch.cuda.get_device_name(0) if gpu_available else None
    }

@app.post("/ai/generate", response_model=AIResponse)
async def generate_ai_response(request: AIRequest):
    import time
    start_time = time.time()
    
    try:
        # Simulate AI processing with GPU acceleration
        # Replace this with actual AI model calls
        response_text = f"GPU-accelerated response to: {request.prompt[:100]}..."
        
        processing_time = time.time() - start_time
        
        return AIResponse(
            response=response_text,
            model_used=request.model,
            gpu_used=torch.cuda.is_available(),
            processing_time=processing_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
PYTHON

# Start the service in background
nohup python gpu_ai_service.py > gpu_service.log 2>&1 &
echo "🚀 GPU AI service started on port 8000"
EOF

echo "🔌 Creating local GPU client..."

# Create local client to use GPU service
cat > scripts/gpu_client.py << 'PYTHON'
import asyncio
import httpx
import json
from typing import Dict, Any, Optional

class RunPodGPUClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def health_check(self) -> Dict[str, Any]:
        """Check GPU service health"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def generate_ai_response(
        self, 
        prompt: str, 
        model: str = "gemini-2.5-flash",
        max_tokens: int = 1000,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """Generate AI response using GPU"""
        try:
            response = await self.client.post(
                f"{self.base_url}/ai/generate",
                json={
                    "prompt": prompt,
                    "model": model,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
            )
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    async def close(self):
        await self.client.aclose()

# Example usage
async def test_gpu_connection():
    client = RunPodGPUClient()
    
    # Check health
    health = await client.health_check()
    print("GPU Service Health:", json.dumps(health, indent=2))
    
    # Test AI generation
    if health.get("status") == "healthy":
        result = await client.generate_ai_response(
            "What is GDPR compliance?",
            model="gemini-2.5-flash"
        )
        print("AI Response:", json.dumps(result, indent=2))
    
    await client.close()

if __name__ == "__main__":
    asyncio.run(test_gpu_connection())
PYTHON

echo "✅ GPU tunnel setup complete!"
echo ""
echo "🔗 To connect to RunPod GPU:"
echo "ssh -F ~/.ssh/runpod_config runpod-gpu"
echo ""
echo "🧪 To test GPU connection:"
echo "python scripts/gpu_client.py"
echo ""
echo "🚀 To run tests with GPU acceleration:"
echo "./scripts/run_gpu_tests.sh ai"
