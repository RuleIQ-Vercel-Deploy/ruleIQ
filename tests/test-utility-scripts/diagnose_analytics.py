#!/usr/bin/env python
"""Diagnose analytics endpoint issue."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from unittest.mock import AsyncMock, patch
from tests.test_app import create_test_app
from fastapi.testclient import TestClient
from tests.conftest import TEST_USER_ID
from database.user import User

# Create test app
app = create_test_app()

# Create test client without auth for now
with TestClient(app) as client:
    # Test direct endpoint access
    print("Testing direct endpoint access:")

    # First test without auth
    response = client.get("/api/chat/analytics/dashboard")
    print(f"Without auth - Status: {response.status_code}, Response: {response.text[:200]}")

    # Mock auth
    def override_get_current_user():
        return User(id=TEST_USER_ID, email="test@example.com", is_active=True)

    from api.dependencies.auth import get_current_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    # Test with mocked analytics monitor
    with patch("services.ai.analytics_monitor.get_analytics_monitor") as mock_monitor:
        mock_instance = AsyncMock()
        mock_instance.get_dashboard_data.return_value = {"test": "data"}
        mock_monitor.return_value = mock_instance

        response = client.get("/api/chat/analytics/dashboard")
        print(f"\nWith auth and mock - Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Response: {response.text}")
        else:
            print("Success!")

        # Check if the mock was called
        print(f"Mock called: {mock_monitor.called}")
        if mock_monitor.called:
            print(
                f"Mock instance get_dashboard_data called: {mock_instance.get_dashboard_data.called}"
            )
