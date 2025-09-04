#!/bin/bash
# Script to cleanly restart the FastAPI server and test JWT authentication

echo "=== JWT Authentication Debug Script ==="
echo

# Step 1: Kill any existing FastAPI processes
echo "1. Killing existing FastAPI processes..."
pkill -f "uvicorn" || true
pkill -f "python.*main:app" || true
sleep 2

# Step 2: Show environment
echo "2. Checking environment..."
echo "Current directory: $(pwd)"
echo ".env.local exists: $([ -f .env.local ] && echo 'Yes' || echo 'No')"
echo

# Step 3: Run the standalone JWT test
echo "3. Running standalone JWT test..."
python debug_jwt.py
echo

# Step 4: Start the server in the background
echo "4. Starting FastAPI server..."
uvicorn api.main:app --reload=false --port 8000 &
SERVER_PID=$!
echo "Server PID: $SERVER_PID"
sleep 5  # Give server time to start

# Step 5: Test the diagnostic endpoint
echo "5. Testing diagnostic endpoint..."
curl -s http://localhost:8000/debug/config | python -m json.tool
echo

# Step 6: Run the fixed test script
echo "6. Running fixed AI assessment tests..."
python ai_assessment_test_fixed.py

# Step 7: Kill the server
echo
echo "7. Stopping server..."
kill $SERVER_PID

echo
echo "=== Test Complete ==="
