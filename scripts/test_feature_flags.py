#!/usr/bin/env python3
"""
Feature Flags System Integration Test
Tests the complete feature flag implementation
"""

import asyncio
import time
from datetime import datetime, timedelta

# Add parent directory to path
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.feature_flag_service import (
    EnhancedFeatureFlagService,
    FeatureFlagConfig,
    feature_flag
)


async def test_basic_evaluation():
    """Test basic feature flag evaluation"""
    print("=" * 60)
    print("Testing Basic Feature Flag Evaluation")
    print("=" * 60)

    service = EnhancedFeatureFlagService()

    # Test evaluation of AUTH_MIDDLEWARE_V2_ENABLED flag
    enabled, reason = await service.is_enabled_for_user(
        "AUTH_MIDDLEWARE_V2_ENABLED",
        user_id="test_user",
        environment="production"
    )

    print("Flag: AUTH_MIDDLEWARE_V2_ENABLED")
    print(f"Enabled: {enabled}")
    print(f"Reason: {reason}")
    print()


async def test_percentage_rollout():
    """Test percentage-based rollout"""
    print("=" * 60)
    print("Testing Percentage Rollout")
    print("=" * 60)

    service = EnhancedFeatureFlagService()

    # Create a test flag with 50% rollout
    config = FeatureFlagConfig(
        name="test_percentage_flag",
        enabled=True,
        percentage=50,
        environments=["testing"]
    )

    # Test with multiple users
    enabled_count = 0
    total_users = 100

    for i in range(total_users):
        # Simulate evaluation (would normally hit database)
        flag_data = {
            "name": "test_percentage_flag",
            "enabled": True,
            "percentage": 50,
            "whitelist": [],
            "blacklist": [],
            "environments": ["testing"]
        }

        enabled, reason = service._evaluate_flag(
            flag_data,
            f"user_{i}",
            "testing"
        )

        if enabled:
            enabled_count += 1

    print(f"Total users: {total_users}")
    print(f"Enabled for: {enabled_count} users ({enabled_count}%)")
    print("Expected: ~50% (actual variance is normal)")
    print()


async def test_user_targeting():
    """Test user whitelist and blacklist"""
    print("=" * 60)
    print("Testing User Targeting")
    print("=" * 60)

    service = EnhancedFeatureFlagService()

    flag_data = {
        "name": "targeted_feature",
        "enabled": False,  # Disabled by default
        "percentage": 0,
        "whitelist": ["vip_user", "beta_tester"],
        "blacklist": ["banned_user"],
        "environments": ["production"]
    }

    # Test whitelist (should be enabled even though flag is disabled)
    enabled, reason = service._evaluate_flag(flag_data, "vip_user", "production")
    print(f"VIP User: Enabled={enabled}, Reason={reason}")

    # Test blacklist (should be disabled even if in whitelist)
    flag_data["blacklist"] = ["vip_user"]
    enabled, reason = service._evaluate_flag(flag_data, "vip_user", "production")
    print(f"Blacklisted VIP: Enabled={enabled}, Reason={reason}")

    # Test regular user (should be disabled)
    enabled, reason = service._evaluate_flag(flag_data, "regular_user", "production")
    print(f"Regular User: Enabled={enabled}, Reason={reason}")
    print()


async def test_environment_overrides():
    """Test environment-specific configurations"""
    print("=" * 60)
    print("Testing Environment Overrides")
    print("=" * 60)

    service = EnhancedFeatureFlagService()

    flag_data = {
        "name": "env_specific_feature",
        "enabled": False,
        "percentage": 0,
        "whitelist": [],
        "blacklist": [],
        "environment_overrides": {
            "development": True,
            "staging": True,
            "production": False
        },
        "environments": ["development", "staging", "production"]
    }

    # Test different environments
    for env in ["development", "staging", "production"]:
        enabled, reason = service._evaluate_flag(flag_data, "user123", env)
        print(f"{env}: Enabled={enabled}, Reason={reason}")
    print()


async def test_temporal_controls():
    """Test time-based feature flags"""
    print("=" * 60)
    print("Testing Temporal Controls")
    print("=" * 60)

    service = EnhancedFeatureFlagService()

    # Test expired flag
    expired_flag = {
        "name": "expired_feature",
        "enabled": True,
        "percentage": 100,
        "whitelist": [],
        "blacklist": [],
        "environments": ["production"],
        "expires_at": (datetime.utcnow() - timedelta(days=1)).isoformat()
    }

    enabled, reason = service._evaluate_flag(expired_flag, "user123", "production")
    print(f"Expired Flag: Enabled={enabled}, Reason={reason}")

    # Test future flag
    future_flag = {
        "name": "future_feature",
        "enabled": True,
        "percentage": 100,
        "whitelist": [],
        "blacklist": [],
        "environments": ["production"],
        "starts_at": (datetime.utcnow() + timedelta(days=1)).isoformat()
    }

    enabled, reason = service._evaluate_flag(future_flag, "user123", "production")
    print(f"Future Flag: Enabled={enabled}, Reason={reason}")

    # Test active flag
    active_flag = {
        "name": "active_feature",
        "enabled": True,
        "percentage": 100,
        "whitelist": [],
        "blacklist": [],
        "environments": ["production"],
        "starts_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
    }

    enabled, reason = service._evaluate_flag(active_flag, "user123", "production")
    print(f"Active Flag: Enabled={enabled}, Reason={reason}")
    print()


async def test_performance():
    """Test performance meets <1ms requirement"""
    print("=" * 60)
    print("Testing Performance (<1ms requirement)")
    print("=" * 60)

    service = EnhancedFeatureFlagService()

    # Prepare flag data (simulating cache hit)
    flag_data = {
        "name": "performance_test",
        "enabled": True,
        "percentage": 50,
        "whitelist": ["user1", "user2", "user3"],
        "blacklist": ["user4", "user5"],
        "environments": ["production"],
        "environment_overrides": {"staging": False}
    }

    # Warm up
    for _ in range(10):
        service._evaluate_flag(flag_data, "test_user", "production")

    # Measure performance
    iterations = 1000
    start_time = time.perf_counter()

    for i in range(iterations):
        enabled, reason = service._evaluate_flag(
            flag_data,
            f"user_{i}",
            "production"
        )

    elapsed_time = time.perf_counter() - start_time
    avg_time_ms = (elapsed_time / iterations) * 1000

    print(f"Iterations: {iterations}")
    print(f"Total time: {elapsed_time:.3f} seconds")
    print(f"Average per evaluation: {avg_time_ms:.3f} ms")
    print("Performance goal: <1ms")
    print("✓ PASSED" if avg_time_ms < 1.0 else "✗ FAILED")
    print()


async def test_decorator():
    """Test the feature flag decorator"""
    print("=" * 60)
    print("Testing Feature Flag Decorator")
    print("=" * 60)

    # Define test functions with decorator
    @feature_flag("enabled_feature")
    async def enabled_function():
        return "Feature is enabled!"

    @feature_flag("disabled_feature", fallback=lambda: "Fallback activated")
    async def disabled_function():
        return "This should not be returned"

    # Mock the service to control flag state
    from unittest.mock import patch, AsyncMock

    with patch('services.feature_flag_service.EnhancedFeatureFlagService') as MockService:
        mock_service = MockService.return_value

        # Test enabled feature
        mock_service.is_enabled_for_user = AsyncMock(return_value=(True, "enabled"))
        result = await enabled_function()
        print(f"Enabled feature result: {result}")

        # Test disabled feature with fallback
        mock_service.is_enabled_for_user = AsyncMock(return_value=(False, "disabled"))
        result = await disabled_function()
        print(f"Disabled feature result: {result}")

    print()


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("FEATURE FLAGS SYSTEM INTEGRATION TEST")
    print("=" * 60 + "\n")

    try:
        await test_basic_evaluation()
        await test_percentage_rollout()
        await test_user_targeting()
        await test_environment_overrides()
        await test_temporal_controls()
        await test_performance()
        await test_decorator()

        print("=" * 60)
        print("✓ ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
