#!/usr/bin/env python3
"""
Example usage of the YOLO Configuration System
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from config_manager import ConfigManager

def main():
    """Demonstrate configuration system usage."""
    
    print("=== YOLO Configuration System Demo ===\n")
    
    # Load configuration
    config_manager = ConfigManager()
    config = config_manager.config
    
    # Display current configuration
    print("1. Current Configuration:")
    print(f"   System Mode: {config.system['mode']}")
    print(f"   Log Level: {config.system['log_level']}")
    print(f"   Dev Agent Token Limit: {config.get_agent_limit('dev')}")
    print(f"   QA Agent Token Limit: {config.get_agent_limit('qa')}")
    print(f"   Retry Max Attempts: {config.retry['max_attempts']}")
    print(f"   Context Refresh Strategy: {config.context['refresh_strategy']}")
    print()
    
    # Demonstrate dot-notation access
    print("2. Dot-notation Configuration Access:")
    print(f"   system.mode = {config_manager.get('system.mode')}")
    print(f"   agent_limits.dev = {config_manager.get('agent_limits.dev')}")
    print(f"   retry.backoff_factor = {config_manager.get('retry.backoff_factor')}")
    print()
    
    # Demonstrate environment override
    print("3. Environment Variable Override Demo:")
    print("   Setting YOLO_AGENT_LIMITS_DEV=15000")
    os.environ['YOLO_AGENT_LIMITS_DEV'] = '15000'
    
    # Reload to pick up environment changes
    config_manager.reload()
    print(f"   Dev Agent Token Limit after override: {config_manager.config.get_agent_limit('dev')}")
    
    # Clean up
    del os.environ['YOLO_AGENT_LIMITS_DEV']
    print()
    
    # Show safety configurations
    print("4. Safety Configurations:")
    print(f"   Operations requiring human approval: {config.safety['require_human_for']}")
    print(f"   Auto-approve timeout: {config.safety['auto_approve_after_seconds']} seconds")
    print()
    
    # Show workflow configurations
    print("5. Workflow Configurations:")
    print(f"   Default timeout: {config.workflow['default_timeout_seconds']} seconds")
    print(f"   Handoff timeout: {config.workflow['handoff_timeout_seconds']} seconds")
    print(f"   Max concurrent agents: {config.workflow['max_concurrent_agents']}")
    print(f"   Parallel workflows enabled: {config.workflow['enable_parallel_workflows']}")
    print()
    
    # Show monitoring configurations
    print("6. Monitoring Configurations:")
    print(f"   Metrics port: {config.monitoring['metrics_port']}")
    print(f"   Health check port: {config.monitoring['health_check_port']}")
    print(f"   Export interval: {config.monitoring['export_interval_seconds']} seconds")
    print()
    
    print("=== Configuration System Demo Complete ===")
    
    # Clean up watcher
    config_manager.stop_watcher()

if __name__ == "__main__":
    main()