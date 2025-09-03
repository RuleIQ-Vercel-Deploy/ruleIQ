"""
Setup test environment with Doppler integration.
This module ensures test environment variables are properly loaded.
"""

import os
import subprocess
import sys


def load_doppler_env():
    """Load environment variables from Doppler."""
    try:
        # Check if Doppler is available
        result = subprocess.run(
            ["doppler", "secrets", "download", "--no-file", "--format", "env"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse and set environment variables
        for line in result.stdout.strip().split('\n'):
            if '=' in line:
                key, value = line.split('=', 1)
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                os.environ[key] = value
                
        print("✓ Doppler environment variables loaded successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not load Doppler variables: {e}")
        return False
    except FileNotFoundError:
        print("Warning: Doppler CLI not found")
        return False


def setup_test_database_urls():
    """Setup test database URLs with proper configuration."""
    # Load from Doppler first
    doppler_loaded = load_doppler_env()
    
    # Set test-specific overrides
    # Always use the Docker test database configuration
    test_db_url = "postgresql://test_user:test_password@localhost:5433/ruleiq_test"
    os.environ["TEST_DATABASE_URL"] = test_db_url
    os.environ["DATABASE_URL"] = test_db_url
    print(f"✓ Using test database: {test_db_url}")
    
    # Set Redis URL for tests - always use test Redis on port 6380
    os.environ["REDIS_URL"] = "redis://localhost:6380/0"
    os.environ["REDIS_HOST"] = "localhost"
    os.environ["REDIS_PORT"] = "6380"
    os.environ["REDIS_DB"] = "0"
    print(f"✓ Using test Redis: {os.environ['REDIS_URL']}")
    
    # Set test environment flag
    os.environ["TESTING"] = "true"
    os.environ["ENVIRONMENT"] = "testing"
    
    # Disable external services in tests
    os.environ["DISABLE_EXTERNAL_APIS"] = "true"
    
    print("✓ Test environment configured successfully")


# Auto-execute when imported
if __name__ != "__main__":
    setup_test_database_urls()