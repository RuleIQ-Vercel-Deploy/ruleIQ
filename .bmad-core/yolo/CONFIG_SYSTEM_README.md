# YOLO Configuration System

## Overview
The YOLO Configuration System provides centralized, flexible configuration management for the YOLO autonomous workflow system. It supports YAML configuration files, environment variable overrides, runtime hot reload, and validation.

## Features
- **YAML Configuration**: Human-readable configuration format
- **Environment Variable Overrides**: Override any configuration value via environment variables
- **Hot Reload**: Automatically reload configuration when file changes (useful for development)
- **Validation**: JSON Schema validation ensures configuration correctness
- **Default Fallback**: Sensible defaults when configuration file is missing

## Configuration Structure

### System Configuration
```yaml
system:
  mode: active  # active, paused, off
  log_level: INFO
  state_file: .bmad-core/yolo/state/yolo-state.json
  enable_telemetry: true
```

### Agent Token Limits
```yaml
agent_limits:
  pm: 6000
  architect: 8000
  po: 5000
  dev: 10000
  qa: 6000
```

### Context Management
```yaml
context:
  summarization_threshold: 0.7
  refresh_strategy: sliding_window  # sliding_window, priority_based, lru
  archive_old_context: true
  max_total_tokens: 50000
```

### Retry Configuration
```yaml
retry:
  max_attempts: 3
  backoff_factor: 2.0
  max_backoff_seconds: 60
```

### Safety Settings
```yaml
safety:
  require_human_for:
    - password_hashing
    - database_migrations
    - deployment_prod
  auto_approve_after_seconds: 3600
```

## Usage

### Basic Usage
```python
from config_manager import ConfigManager

# Load configuration
config_manager = ConfigManager()
config = config_manager.config

# Access configuration values
mode = config.system['mode']
dev_limit = config.get_agent_limit('dev')
```

### Dot-notation Access
```python
# Get nested values using dot notation
mode = config_manager.get('system.mode')
limit = config_manager.get('agent_limits.dev')
retry = config_manager.get('retry.max_attempts', default=3)
```

### Environment Variable Override
Set environment variables with the prefix `YOLO_` to override configuration values:

```bash
# Override agent limits
export YOLO_AGENT_LIMITS_DEV=15000

# Override system mode
export YOLO_SYSTEM_MODE=paused

# Override retry settings
export YOLO_RETRY_MAX_ATTEMPTS=5
```

### Custom Configuration File
```python
# Use a custom configuration file
config_manager = ConfigManager('/path/to/custom-config.yaml')
```

### Manual Reload
```python
# Manually reload configuration
config_manager.reload()
```

## Integration with YOLO System

The YOLO orchestrator automatically uses the configuration system:

```python
class YOLOOrchestrator:
    def __init__(self, config_path: Optional[str] = None):
        # Configuration is automatically loaded
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.config
        
        # Apply configuration to system
        self.state.mode = YOLOMode(self.config.system['mode'])
        
        # Apply agent token limits to context manager
        if self.context_manager:
            for agent, limit in self.config.agent_limits.items():
                self.context_manager.AGENT_CONTEXT_LIMITS[agent] = limit
```

## Configuration Validation

The system validates configuration against a JSON schema to ensure:
- Required fields are present
- Values are within acceptable ranges
- Data types are correct

Example validation rules:
- Agent token limits: 1,000 - 50,000 tokens
- Retry max attempts: 1 - 10
- Port numbers: 1024 - 65535

## Files

- `config/yolo-config.yaml` - Default configuration file
- `config_manager.py` - Configuration management implementation
- `tests/test_config_manager.py` - Comprehensive test suite
- `example_config_usage.py` - Usage examples

## Testing

Run the configuration tests:
```bash
python3 -m pytest tests/test_config_manager.py -v
```

## Best Practices

1. **Use Environment Variables for Deployment**: Override production settings via environment variables rather than modifying config files
2. **Version Control Config Templates**: Keep configuration templates in version control, but not production configs with secrets
3. **Validate on Startup**: Always validate configuration on application startup
4. **Use Defaults Wisely**: Provide sensible defaults that work for development
5. **Document Configuration**: Keep configuration well-documented with comments in YAML

## Migration from Hardcoded Values

To migrate from hardcoded values:

1. Identify all hardcoded configuration values
2. Add them to the YAML configuration schema
3. Update code to read from configuration
4. Test with different configuration values
5. Document the new configuration options

## Troubleshooting

### Configuration Not Loading
- Check file path is correct
- Verify YAML syntax is valid
- Check file permissions

### Environment Override Not Working
- Ensure variable starts with `YOLO_`
- Use underscores to separate nested keys
- Check variable is exported (not just set)

### Hot Reload Not Working
- Verify watchdog is installed
- Check file system supports file watching
- Ensure configuration file exists

## Future Enhancements
- Configuration profiles (dev, staging, prod)
- Remote configuration source support
- Configuration change history
- Secret management integration
- Configuration UI/dashboard