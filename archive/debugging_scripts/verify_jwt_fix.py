"""
from __future__ import annotations
import json
import logging
logger = logging.getLogger(__name__)

JWT Authentication Fix Verification Script

This script verifies that the JWT authentication is working correctly
by ensuring both client and server use the same JWT library and secret.
"""
import os
import sys
import time
import subprocess
from pathlib import Path
from typing import Optional, Any
GREEN = '\x1b[92m'
RED = '\x1b[91m'
YELLOW = '\x1b[93m'
BLUE = '\x1b[94m'
RESET = '\x1b[0m'

def print_status(message, status='info') -> None:
    """Print colored status messages"""
    if status == 'success':
        logger.info(f'{GREEN}✓ {message}{RESET}')
    elif status == 'error':
        logger.info(f'{RED}✗ {message}{RESET}')
    elif status == 'warning':
        logger.info(f'{YELLOW}! {message}{RESET}')
    else:
        logger.info(f'{BLUE}→ {message}{RESET}')

def check_prerequisites() -> bool:
    """Check if all required libraries are installed"""
    print_status('Checking prerequisites...')
    try:
        from jose import jwt
        print_status('python-jose is installed', 'success')
    except ImportError:
        print_status('python-jose is NOT installed', 'error')
        print_status('Install with: pip install python-jose[cryptography]', 'warning')
        return False
    env_path = Path('.env.local')
    if env_path.exists():
        print_status('.env.local file exists', 'success')
    else:
        print_status('.env.local file NOT found', 'error')
        return False
    return True

def kill_existing_servers() -> None:
    """Kill any existing uvicorn processes"""
    print_status('Killing existing server processes...')
    subprocess.run(['pkill', '-f', 'uvicorn'], capture_output=True)
    subprocess.run(['pkill', '-f', 'python.*main:app'], capture_output=True)
    time.sleep(2)
    print_status('Server processes killed', 'success')

def start_server() -> Optional[Any]:
    """Start the FastAPI server"""
    print_status('Starting FastAPI server...')
    process = subprocess.Popen(['uvicorn', 'api.main:app', '--port', '8000'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    print_status('Waiting for server to start...')
    time.sleep(5)
    import requests
    try:
        response = requests.get('http://localhost:8000/health')
        if response.status_code == 200:
            print_status('Server started successfully', 'success')
            return process
        else:
            print_status(f'Server returned status {response.status_code}', 'error')
            return None
    except requests.RequestException:
        print_status('Server failed to start', 'error')
        return None

def test_jwt_authentication() -> Optional[bool]:
    """Test JWT authentication with the correct library"""
    print_status('Testing JWT authentication...')
    import requests
    from jose import jwt
    from datetime import datetime, timedelta, timezone
    from dotenv import load_dotenv
    load_dotenv('.env.local')
    JWT_SECRET = os.getenv('JWT_SECRET', 'dev-jwt-secret-key-change-for-production')
    print_status(f'JWT_SECRET loaded: {JWT_SECRET[:10]}...')
    try:
        response = requests.get('http://localhost:8000/debug/config')
        if response.status_code == 200:
            config = response.json()
            print_status('Server configuration retrieved:', 'success')
            logger.info(f"  - Server JWT Secret: {config.get('jwt_secret_first_10')}...")
            logger.info(f"  - Server working dir: {config.get('working_directory')}")
            if config.get('jwt_secret_first_10') == JWT_SECRET[:10]:
                print_status('JWT secrets match!', 'success')
            else:
                print_status('JWT secrets DO NOT match!', 'error')
                return False
    except (json.JSONDecodeError, requests.RequestException, KeyError) as e:
        print_status(f'Failed to get server config: {e}', 'error')
    payload = {'sub': 'testuser@example.com', 'exp': datetime.now(timezone.utc) + timedelta(minutes=5), 'type': 'access'}
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    print_status(f'Token created: {token[:50]}...', 'success')
    headers = {'Authorization': f'Bearer {token}'}
    test_payload = {'question_id': 'test-q1', 'question_text': 'How should we implement access control?', 'framework_id': 'soc2'}
    url = 'http://localhost:8000/api/v1/ai-assessments/soc2/help'
    print_status(f'Testing endpoint: {url}')
    try:
        response = requests.post(url, json=test_payload, headers=headers, timeout=10)
        if response.status_code == 200:
            print_status('Authentication successful!', 'success')
            print_status('Response received from AI endpoint', 'success')
            return True
        elif response.status_code == 401:
            print_status('Authentication failed (401)', 'error')
            logger.info(f'Response: {response.text}')
            return False
        else:
            print_status(f'Unexpected status code: {response.status_code}', 'warning')
            logger.info(f'Response: {response.text}')
            return False
    except (json.JSONDecodeError, requests.RequestException) as e:
        print_status(f'Request failed: {e}', 'error')
        return False

def main() -> Optional[int]:
    """Main execution function"""
    logger.info(f"\n{BLUE}{'=' * 60}{RESET}")
    logger.info(f'{BLUE}JWT Authentication Fix Verification{RESET}')
    logger.info(f"{BLUE}{'=' * 60}{RESET}\n")
    if not check_prerequisites():
        print_status('Prerequisites check failed. Please install missing dependencies.', 'error')
        return 1
    logger.info()
    kill_existing_servers()
    logger.info()
    server_process = start_server()
    if not server_process:
        print_status('Failed to start server', 'error')
        return 1
    logger.info()
    try:
        success = test_jwt_authentication()
        if success:
            logger.info(f"\n{GREEN}{'=' * 60}{RESET}")
            logger.info(f'{GREEN}JWT AUTHENTICATION IS WORKING!{RESET}')
            logger.info(f"{GREEN}{'=' * 60}{RESET}")
            return 0
        else:
            logger.info(f"\n{RED}{'=' * 60}{RESET}")
            logger.info(f'{RED}JWT AUTHENTICATION FAILED{RESET}')
            logger.info(f"{RED}{'=' * 60}{RESET}")
            logger.info('\nTroubleshooting steps:')
            logger.info('1. Check that .env.local contains: JWT_SECRET=your-secret-key')
            logger.info("2. Ensure the secret doesn't contain quotes or spaces")
            print('3. Try restarting with: pkill -f uvicorn && uvicorn api.main:app --reload')
            logger.info('4. Check server logs for any startup errors')
            return 1
    finally:
        print_status('\nStopping server...')
        server_process.terminate()
        server_process.wait()
        print_status('Server stopped', 'success')
if __name__ == '__main__':
    sys.exit(main())
