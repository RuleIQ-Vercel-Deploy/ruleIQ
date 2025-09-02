import requests
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Import jose instead of jwt to match the server
from jose import jwt

# Get absolute path to .env.local
env_path = Path(__file__).parent / ".env.local"
print(f"Loading env from: {env_path}")
print(f"File exists: {env_path.exists()}")

# Load environment variables
load_dotenv(env_path)

# Get JWT_SECRET from environment
JWT_SECRET = os.getenv("JWT_SECRET")
print(f"JWT_SECRET loaded: {JWT_SECRET[:10] if JWT_SECRET else 'None'}...")

# Fallback to the default value used in settings.py if not set
if not JWT_SECRET:
    JWT_SECRET = "dev-secret-key-change-in-production"
    print("Using fallback JWT_SECRET")

BASE_URL = "http://localhost:8000/api/v1"


def create_test_token():
    """Creates a JWT token for a test user."""
    payload = {
        "sub": "testuser@example.com",
        "exp": datetime.utcnow() + timedelta(minutes=5),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def test_diagnostic_endpoint() -> None:
    """Test the diagnostic endpoint to verify server configuration."""
    url = "http://localhost:8000/debug/config"
    print(f"--- Testing {url} ---")
    try:
        r = requests.get(url)
        print(f"Status Code: {r.status_code}")
        print(f"Server Config: {json.dumps(r.json(), indent=2)}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    print("-" * 40)


def test_endpoint(endpoint, payload, token, stream=False) -> None:
    """Helper function to test an endpoint."""
    url = f"{BASE_URL}/ai-assessments{endpoint}"
    headers = {"Authorization": f"Bearer {token}"}
    print(f"--- Testing {url} ---")
    try:
        if stream:
            with requests.post(url, json=payload, headers=headers, stream=True) as r:
                print(f"Status Code: {r.status_code}")
                for chunk in r.iter_content(chunk_size=None):
                    if chunk:
                        print(f"Received chunk: {chunk.decode('utf-8')}")
        else:
            r = requests.post(url, json=payload, headers=headers)
            print(f"Status Code: {r.status_code}")
            print(f"Response: {r.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    print("-" * 20)


if __name__ == "__main__":
    # First test the diagnostic endpoint
    test_diagnostic_endpoint()

    token = create_test_token()
    print(f"Token created: {token[:50]}...")

    # Test Data
    help_payload = {
        "question_id": "test-q1",
        "question_text": "How should we implement access control?",
        "framework_id": "soc2",
    }

    followup_payload = {
        "framework_id": "soc2",
        "current_answers": {"test-q1": "We use RBAC."},
    }

    analysis_payload = {
        "assessment_results": {"test-q1": "We use RBAC."},
        "framework_id": "soc2",
        "business_profile_id": "test-profile-1",
    }

    recommendations_payload = {
        "gaps": [{"id": "gap1", "description": "No MFA for admins"}],
        "business_profile": {"name": "TestCo", "industry": "SaaS"},
    }

    # Test Execution
    test_endpoint("/soc2/help", help_payload, token)
    test_endpoint("/soc2/help/stream", help_payload, token, stream=True)
    test_endpoint("/followup", followup_payload, token)
    test_endpoint("/analysis", analysis_payload, token)
    test_endpoint("/analysis/stream", analysis_payload, token, stream=True)
    test_endpoint("/recommendations", recommendations_payload, token)
    test_endpoint(
        "/recommendations/stream", recommendations_payload, token, stream=True
    )
