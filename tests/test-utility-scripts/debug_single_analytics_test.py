#!/usr/bin/env python
"""Debug single analytics test."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest

# Run single test with full output
if __name__ == "__main__":
    exit_code = pytest.main(
        [
            "tests/integration/api/test_analytics_endpoints.py::TestAnalyticsEndpoints::test_analytics_dashboard_success",
            "-xvs",
            "--tb=short",
            "-p",
            "no:warnings",
        ]
    )
    sys.exit(exit_code)
