"""
Tests for YOLO Configuration Manager
"""

import os
import pytest
import tempfile
import yaml
from pathlib import Path
import time
import jsonschema

# Import the config manager
import sys
sys.path.append(str(Path(__file__).parent.parent))
from config_manager import ConfigManager, YOLOConfig


class TestConfigManager:
    """Test suite for ConfigManager."""

    @pytest.fixture
    def temp_config_file(self):
        """Create a temporary config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_data = {
                "system": {
                    "mode": "active",
                    "log_level": "DEBUG",
                    "state_file": "test-state.json",
                    "enable_telemetry": True
                },
                "agent_limits": {
                    "dev": 12000,
                    "qa": 7000
                },
                "context": {
                    "summarization_threshold": 0.8,
                    "refresh_strategy": "priority_based"
                },
                "retry": {
                    "max_attempts": 5,
                    "backoff_factor": 1.5
                }
            }
            yaml.dump(config_data, f)
            temp_path = f.name

        yield temp_path

        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_load_config_from_file(self, temp_config_file):
        """Test loading configuration from file."""
        manager = ConfigManager(temp_config_file)

        assert manager.config is not None
        assert manager.config.system['mode'] == 'active'
        assert manager.config.system['log_level'] == 'DEBUG'
        assert manager.config.agent_limits['dev'] == 12000
        assert manager.config.agent_limits['qa'] == 7000
        assert manager.config.context['summarization_threshold'] == 0.8
        assert manager.config.retry['max_attempts'] == 5

    def test_load_default_config(self):
        """Test loading default configuration when file doesn't exist."""
        manager = ConfigManager("non-existent-file.yaml")

        assert manager.config is not None
        assert manager.config.system['mode'] == 'active'
        assert manager.config.agent_limits['dev'] == 10000
        assert manager.config.agent_limits['qa'] == 6000

    def test_environment_override(self, temp_config_file):
        """Test environment variable overrides."""
        # Set environment variables
        os.environ['YOLO_AGENT_LIMITS_DEV'] = '15000'
        os.environ['YOLO_SYSTEM_MODE'] = 'paused'
        os.environ['YOLO_RETRY_MAX_ATTEMPTS'] = '7'
        os.environ['YOLO_CONTEXT_ARCHIVE_OLD_CONTEXT'] = 'false'

        try:
            manager = ConfigManager(temp_config_file)

            assert manager.config.agent_limits['dev'] == 15000
            assert manager.config.system['mode'] == 'paused'
            assert manager.config.retry['max_attempts'] == 7
            assert manager.config.context.get('archive_old_context') == False
        finally:
            # Cleanup environment
            del os.environ['YOLO_AGENT_LIMITS_DEV']
            del os.environ['YOLO_SYSTEM_MODE']
            del os.environ['YOLO_RETRY_MAX_ATTEMPTS']
            del os.environ['YOLO_CONTEXT_ARCHIVE_OLD_CONTEXT']

    def test_get_agent_limit(self, temp_config_file):
        """Test getting agent token limits."""
        manager = ConfigManager(temp_config_file)

        assert manager.config.get_agent_limit('dev') == 12000
        assert manager.config.get_agent_limit('qa') == 7000
        assert manager.config.get_agent_limit('unknown') == 5000  # Default
        assert manager.config.get_agent_limit('DEV') == 12000  # Case insensitive

    def test_get_config_value(self, temp_config_file):
        """Test getting configuration values by path."""
        manager = ConfigManager(temp_config_file)

        assert manager.get('system.mode') == 'active'
        assert manager.get('agent_limits.dev') == 12000
        assert manager.get('retry.backoff_factor') == 1.5
        assert manager.get('non.existent.path', 'default') == 'default'

    def test_config_validation(self):
        """Test configuration validation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            # Invalid config - agent limit too high
            invalid_config = {
                "system": {"mode": "active"},
                "agent_limits": {"dev": 100000}  # Max is 50000
            }
            yaml.dump(invalid_config, f)
            temp_path = f.name

        try:
            manager = ConfigManager(temp_path)
            # Should load defaults on validation error
            assert manager.config.agent_limits['dev'] == 10000  # Default value
        finally:
            os.unlink(temp_path)

    def test_invalid_yaml(self):
        """Test handling of invalid YAML."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_path = f.name

        try:
            manager = ConfigManager(temp_path)
            # Should load defaults on parse error
            assert manager.config is not None
            assert manager.config.system['mode'] == 'active'
        finally:
            os.unlink(temp_path)

    def test_hot_reload(self, temp_config_file):
        """Test configuration hot reload."""
        manager = ConfigManager(temp_config_file)

        # Initial value
        assert manager.config.agent_limits['dev'] == 12000

        # Modify the file
        with open(temp_config_file, 'r') as f:
            config_data = yaml.safe_load(f)

        config_data['agent_limits']['dev'] = 14000

        with open(temp_config_file, 'w') as f:
            yaml.dump(config_data, f)

        # Give the watcher time to detect the change
        time.sleep(0.5)

        # Manual reload (since file watcher might not work in tests)
        manager.reload()

        # Check updated value
        assert manager.config.agent_limits['dev'] == 14000

        # Stop watcher
        manager.stop_watcher()

    def test_config_dataclass(self):
        """Test YOLOConfig dataclass."""
        config_dict = {
            "system": {"mode": "active"},
            "agent_limits": {"dev": 10000},
            "context": {"summarization_threshold": 0.7},
            "retry": {"max_attempts": 3},
            "safety": {"require_human_for": []},
            "workflow": {"default_timeout_seconds": 300},
            "monitoring": {"metrics_port": 9090}
        }

        config = YOLOConfig.from_dict(config_dict)

        assert config.system['mode'] == 'active'
        assert config.get_agent_limit('dev') == 10000
        assert config.get_agent_limit('unknown') == 5000

    def test_type_conversion(self):
        """Test environment variable type conversion."""
        os.environ['YOLO_TEST_INT'] = '42'
        os.environ['YOLO_TEST_FLOAT'] = '3.14'
        os.environ['YOLO_TEST_BOOL_TRUE'] = 'true'
        os.environ['YOLO_TEST_BOOL_FALSE'] = 'false'
        os.environ['YOLO_TEST_STRING'] = 'hello'

        try:
            manager = ConfigManager("non-existent.yaml")

            # Manually test the _set_nested method
            test_dict = {}
            manager._set_nested(test_dict, ['test', 'int'], '42')
            manager._set_nested(test_dict, ['test', 'float'], '3.14')
            manager._set_nested(test_dict, ['test', 'bool_true'], 'true')
            manager._set_nested(test_dict, ['test', 'bool_false'], 'false')
            manager._set_nested(test_dict, ['test', 'string'], 'hello')

            assert test_dict['test']['int'] == 42
            assert test_dict['test']['float'] == 3.14
            assert test_dict['test']['bool_true'] == True
            assert test_dict['test']['bool_false'] == False
            assert test_dict['test']['string'] == 'hello'
        finally:
            # Cleanup
            for key in list(os.environ.keys()):
                if key.startswith('YOLO_TEST_'):
                    del os.environ[key]

    def test_nested_config_get(self, temp_config_file):
        """Test getting nested configuration values."""
        manager = ConfigManager(temp_config_file)

        # Test nested dictionary access
        assert manager.get('system.mode') == 'active'
        assert manager.get('retry.backoff_factor') == 1.5

        # Test with default
        assert manager.get('non.existent', 'default') == 'default'
        assert manager.get('system.non_existent', None) is None

    def test_config_schema_validation(self):
        """Test that config schema is properly defined."""
        schema = ConfigManager.CONFIG_SCHEMA

        # Valid config should pass
        valid_config = {
            "system": {"mode": "active"},
            "agent_limits": {"dev": 10000}
        }
        jsonschema.validate(valid_config, schema)

        # Invalid mode should fail
        with pytest.raises(jsonschema.ValidationError):
            invalid_config = {
                "system": {"mode": "invalid_mode"},
                "agent_limits": {"dev": 10000}
            }
            jsonschema.validate(invalid_config, schema)

        # Agent limit too high should fail
        with pytest.raises(jsonschema.ValidationError):
            invalid_config = {
                "system": {"mode": "active"},
                "agent_limits": {"dev": 100000}
            }
            jsonschema.validate(invalid_config, schema)

    def test_multiple_instances(self, temp_config_file):
        """Test multiple ConfigManager instances."""
        manager1 = ConfigManager(temp_config_file)
        manager2 = ConfigManager(temp_config_file)

        # Both should load the same config
        assert manager1.config.system['mode'] == manager2.config.system['mode']
        assert manager1.config.agent_limits['dev'] == manager2.config.agent_limits['dev']

        # Stop watchers
        manager1.stop_watcher()
        manager2.stop_watcher()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
