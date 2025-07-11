#!/usr/bin/env python
"""Debug analytics test to capture the actual error"""

import sys
import os

# Add the project root to sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest

# Run the specific test with detailed output
if __name__ == "__main__":
    # Run with maximum verbosity and capture turned off
    exit_code = pytest.main([
        "tests/integration/api/test_analytics_endpoints.py::TestAnalyticsEndpoints::test_analytics_dashboard_success",
        "-xvs",
        "--tb=short",
        "--capture=no",
        "--log-cli-level=DEBUG"
    ])
    
    sys.exit(exit_code)