#!/usr/bin/env python3
"""
JWT Authentication Fix Verification Script

This script verifies that the JWT authentication is working correctly
by ensuring both client and server use the same JWT library and secret.
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Optional

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_status(message, status="info") -> None:
    """Print colored status messages"""
    if status == "success":
        print(f"{GREEN}✓ {message}{RESET}")
    elif status == "error":
        print(f"{RED}✗ {message}{RESET}")
    elif status == "warning":
        print(f"{YELLOW}! {message}{RESET}")
    else:
        print(f"{BLUE}→ {message}{RESET}")


def check_prerequisites() -> bool:
    """Check if all required libraries are installed"""
    print_status("Checking prerequisites...")

    # Check python-jose
    try:
        from jose import jwt

        print_status("python-jose is installed", "success")
    except ImportError:
        print_status("python-jose is NOT installed", "error")
        print_status("Install with: pip install python-jose[cryptography]", "warning")
        return False

    # Check if .env.local exists
    env_path = Path(".env.local")
    if env_path.exists():
        print_status(".env.local file exists", "success")
    else:
        print_status(".env.local file NOT found", "error")
        return False

    return True


def kill_existing_servers() -> None:
    """Kill any existing uvicorn processes"""
    print_status("Killing existing server processes...")

    # Kill uvicorn processes
    subprocess.run(["pkill", "-f", "uvicorn"], capture_output=True)
    subprocess.run(["pkill", "-f", "python.*main:app"], capture_output=True)

    time.sleep(2)
    print_status("Server processes killed", "success")


def start_server():
    """Start the FastAPI server"""
    print_status("Starting FastAPI server...")

    # Start server in background
    process = subprocess.Popen(
        ["uvicorn", "api.main:app", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    # Wait for server to start
    print_status("Waiting for server to start...")
    time.sleep(5)

    # Check if server is running
    import requests

    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print_status("Server started successfully", "success")
            return process
        else:
            print_status(f"Server returned status {response.status_code}", "error")
            return None
    except:
        print_status("Server failed to start", "error")
        return None


def test_jwt_authentication() -> Optional[bool]:
    """Test JWT authentication with the correct library"""
    print_status("Testing JWT authentication...")

    import requests
    from jose import jwt
    from datetime import datetime, timedelta
    from dotenv import load_dotenv

    # Load environment
    load_dotenv(".env.local")
    JWT_SECRET = os.getenv("JWT_SECRET", "dev-jwt-secret-key-change-for-production")

    print_status(f"JWT_SECRET loaded: {JWT_SECRET[:10]}...")

    # Check server config
    try:
        response = requests.get("http://localhost:8000/debug/config")
        if response.status_code == 200:
            config = response.json()
            print_status("Server configuration retrieved:", "success")
            print(f"  - Server JWT Secret: {config.get('jwt_secret_first_10')}...")
            print(f"  - Server working dir: {config.get('working_directory')}")

            # Compare secrets
            if config.get("jwt_secret_first_10") == JWT_SECRET[:10]:
                print_status("JWT secrets match!", "success")
            else:
                print_status("JWT secrets DO NOT match!", "error")
                return False
    except Exception as e:
        print_status(f"Failed to get server config: {e}", "error")

    # Create token
    payload = {
        "sub": "testuser@example.com",
        "exp": datetime.utcnow() + timedelta(minutes=5),
        "type": "access",  # Added this field which might be required
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    print_status(f"Token created: {token[:50]}...", "success")

    # Test protected endpoint
    headers = {"Authorization": f"Bearer {token}"}
    test_payload = {
        "question_id": "test-q1",
        "question_text": "How should we implement access control?",
        "framework_id": "soc2",
    }

    url = "http://localhost:8000/api/v1/ai-assessments/soc2/help"
    print_status(f"Testing endpoint: {url}")

    try:
        response = requests.post(url, json=test_payload, headers=headers, timeout=10)

        if response.status_code == 200:
            print_status("Authentication successful!", "success")
            print_status("Response received from AI endpoint", "success")
            return True
        elif response.status_code == 401:
            print_status("Authentication failed (401)", "error")
            print(f"Response: {response.text}")
            return False
        else:
            print_status(f"Unexpected status code: {response.status_code}", "warning")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print_status(f"Request failed: {e}", "error")
        return False


def main() -> Optional[int]:
    """Main execution function"""
    print(f"\n{BLUE}{'=' * 60}{RESET}")
    print(f"{BLUE}JWT Authentication Fix Verification{RESET}")
    print(f"{BLUE}{'=' * 60}{RESET}\n")

    # Step 1: Check prerequisites
    if not check_prerequisites():
        print_status("Prerequisites check failed. Please install missing dependencies.", "error")
        return 1

    print()

    # Step 2: Kill existing servers
    kill_existing_servers()

    print()

    # Step 3: Start server
    server_process = start_server()
    if not server_process:
        print_status("Failed to start server", "error")
        return 1

    print()

    # Step 4: Test authentication
    try:
        success = test_jwt_authentication()

        if success:
            print(f"\n{GREEN}{'=' * 60}{RESET}")
            print(f"{GREEN}JWT AUTHENTICATION IS WORKING!{RESET}")
            print(f"{GREEN}{'=' * 60}{RESET}")
            return 0
        else:
            print(f"\n{RED}{'=' * 60}{RESET}")
            print(f"{RED}JWT AUTHENTICATION FAILED{RESET}")
            print(f"{RED}{'=' * 60}{RESET}")

            print("\nTroubleshooting steps:")
            print("1. Check that .env.local contains: JWT_SECRET=your-secret-key")
            print("2. Ensure the secret doesn't contain quotes or spaces")
            print("3. Try restarting with: pkill -f uvicorn && uvicorn api.main:app --reload")
            print("4. Check server logs for any startup errors")
            return 1

    finally:
        # Clean up
        print_status("\nStopping server...")
        server_process.terminate()
        server_process.wait()
        print_status("Server stopped", "success")


if __name__ == "__main__":
    sys.exit(main())
