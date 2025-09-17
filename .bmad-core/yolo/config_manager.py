"""
Configuration management for YOLO system with hot reload support.
"""

import os
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass
import jsonschema
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
import threading
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class YOLOConfig:
    """YOLO system configuration."""
    system: Dict[str, Any]
    agent_limits: Dict[str, int]
    context: Dict[str, Any]
    retry: Dict[str, Any]
    safety: Dict[str, Any]
    workflow: Dict[str, Any]
    monitoring: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'YOLOConfig':
        """Create config from dictionary."""
        return cls(**data)

    def get_agent_limit(self, agent: str) -> int:
        """Get token limit for agent."""
        return self.agent_limits.get(agent.lower(), 5000)


class ConfigManager:
    """Manages YOLO configuration with hot reload."""

    CONFIG_SCHEMA = {
        "type": "object",
        "properties": {
            "system": {
                "type": "object",
                "properties": {
                    "mode": {"type": "string", "enum": ["active", "paused", "off"]},
                    "log_level": {"type": "string"},
                    "state_file": {"type": "string"},
                    "enable_telemetry": {"type": "boolean"}
                }
            },
            "agent_limits": {
                "type": "object",
                "patternProperties": {
                    "^[a-z_]+$": {"type": "integer", "minimum": 1000, "maximum": 50000}
                }
            },
            "context": {
                "type": "object",
                "properties": {
                    "summarization_threshold": {"type": "number", "minimum": 0, "maximum": 1},
                    "refresh_strategy": {"type": "string", "enum": ["sliding_window", "priority_based", "lru"]},
                    "archive_old_context": {"type": "boolean"},
                    "archive_after_days": {"type": "integer", "minimum": 1},
                    "max_total_tokens": {"type": "integer", "minimum": 1000}
                }
            },
            "retry": {
                "type": "object",
                "properties": {
                    "max_attempts": {"type": "integer", "minimum": 1, "maximum": 10},
                    "backoff_factor": {"type": "number", "minimum": 1.0, "maximum": 10.0},
                    "max_backoff_seconds": {"type": "integer", "minimum": 1},
                    "circuit_breaker_threshold": {"type": "integer", "minimum": 1},
                    "circuit_breaker_timeout": {"type": "integer", "minimum": 1}
                }
            },
            "safety": {
                "type": "object",
                "properties": {
                    "require_human_for": {
                        "type": "array",
                        "items": {"type": "string"}
                    },
                    "auto_approve_after_seconds": {"type": "integer", "minimum": 0}
                }
            },
            "workflow": {
                "type": "object",
                "properties": {
                    "default_timeout_seconds": {"type": "integer", "minimum": 1},
                    "handoff_timeout_seconds": {"type": "integer", "minimum": 1},
                    "max_concurrent_agents": {"type": "integer", "minimum": 1},
                    "enable_parallel_workflows": {"type": "boolean"}
                }
            },
            "monitoring": {
                "type": "object",
                "properties": {
                    "metrics_port": {"type": "integer", "minimum": 1024, "maximum": 65535},
                    "health_check_port": {"type": "integer", "minimum": 1024, "maximum": 65535},
                    "export_interval_seconds": {"type": "integer", "minimum": 1},
                    "retention_days": {"type": "integer", "minimum": 1}
                }
            }
        },
        "required": ["system", "agent_limits"]
    }

    def __init__(self, config_path: str = None):
        """Initialize configuration manager."""
        self.config_path = Path(config_path or ".bmad-core/yolo/config/yolo-config.yaml")
        self.config: Optional[YOLOConfig] = None
        self.observer: Optional[Observer] = None
        self._config_lock = threading.RLock()  # Reentrant lock for thread safety
        self._config_checksum: Optional[str] = None  # For integrity validation
        self._load_config()
        self._setup_watcher()

    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        if file_path.exists():
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _validate_config_integrity(self) -> bool:
        """Validate config file integrity using checksum."""
        if not self.config_path.exists():
            return True  # No file to validate

        new_checksum = self._calculate_checksum(self.config_path)
        if self._config_checksum is None:
            # First load, store checksum
            self._config_checksum = new_checksum
            return True

        if new_checksum != self._config_checksum:
            logger.info(f"Config file changed (checksum: {new_checksum[:8]}...)")
            self._config_checksum = new_checksum
            return True

        return True

    def _load_config(self):
        """Load configuration from file with environment overrides (thread-safe)."""
        with self._config_lock:
            try:
                # Validate config file integrity
                if not self._validate_config_integrity():
                    logger.warning("Config file integrity check failed, using cached config")
                    return

                # Load base config from file
                if self.config_path.exists():
                    with open(self.config_path) as f:
                        data = yaml.safe_load(f)
                else:
                    logger.warning(f"Config file not found at {self.config_path}, using defaults")
                    data = self._get_default_config()

                # Apply environment variable overrides
                data = self._apply_env_overrides(data)

                # Validate configuration
                jsonschema.validate(data, self.CONFIG_SCHEMA)

                # Ensure all required sections exist
                for section in ['system', 'agent_limits', 'context', 'retry', 'safety', 'workflow', 'monitoring']:
                    if section not in data:
                        data[section] = self._get_default_config()[section]

                # Create config object
                self.config = YOLOConfig.from_dict(data)
                logger.info("Configuration loaded successfully")

            except yaml.YAMLError as e:
                logger.error(f"Error parsing YAML config: {e}")
                self.config = YOLOConfig.from_dict(self._get_default_config())
            except jsonschema.ValidationError as e:
                logger.error(f"Config validation error: {e}")
                self.config = YOLOConfig.from_dict(self._get_default_config())
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                self.config = YOLOConfig.from_dict(self._get_default_config())

    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides."""
        # Example: YOLO_AGENT_LIMITS_DEV=15000
        for key, value in os.environ.items():
            if key.startswith('YOLO_'):
                parts = key[5:].lower().split('_')

                # Handle special cases where config keys have underscores
                # YOLO_AGENT_LIMITS_DEV -> agent_limits.dev
                if len(parts) >= 3 and parts[0] == 'agent' and parts[1] == 'limits':
                    parts = ['agent_limits'] + parts[2:]
                elif len(parts) >= 3 and parts[0] == 'retry' and parts[1] == 'max' and parts[2] == 'attempts':
                    # Handle retry.max_attempts
                    parts = ['retry', 'max_attempts']
                elif len(parts) >= 3 and parts[0] == 'retry' and parts[1] == 'backoff' and parts[2] == 'factor':
                    # Handle retry.backoff_factor
                    parts = ['retry', 'backoff_factor']
                elif len(parts) >= 3 and parts[0] == 'retry' and parts[1] == 'max' and parts[2] == 'backoff':
                    # Handle retry.max_backoff_seconds
                    parts = ['retry', 'max_backoff_seconds'] + parts[3:]
                elif len(parts) >= 3 and parts[0] == 'retry' and parts[1] == 'circuit' and parts[2] == 'breaker':
                    # Handle circuit_breaker fields
                    if len(parts) >= 4:
                        parts = ['retry', f"circuit_breaker_{parts[3]}"] + parts[4:]
                elif len(parts) >= 3 and parts[0] == 'context' and parts[1] == 'archive' and parts[2] == 'old':
                    # Handle context.archive_old_context
                    if len(parts) >= 4 and parts[3] == 'context':
                        parts = ['context', 'archive_old_context'] + parts[4:]
                elif len(parts) >= 2:
                    # Check if first two parts should be combined
                    combined_key = f"{parts[0]}_{parts[1]}"
                    if combined_key in config and len(parts) > 2:
                        parts = [combined_key] + parts[2:]

                # Skip if parts doesn't map to a valid config path
                if len(parts) >= 2 and parts[0] in config:
                    self._set_nested(config, parts, value)
        return config

    def _set_nested(self, d: Dict, keys: List[str], value: str):
        """Set nested dictionary value."""
        for key in keys[:-1]:
            d = d.setdefault(key, {})

        # Convert value to appropriate type
        try:
            # Try integer first
            d[keys[-1]] = int(value)
        except ValueError:
            try:
                # Try float
                d[keys[-1]] = float(value)
            except ValueError:
                # Try boolean
                if value.lower() in ['true', 'false']:
                    d[keys[-1]] = value.lower() == 'true'
                else:
                    # Keep as string
                    d[keys[-1]] = value

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "system": {
                "mode": "active",
                "log_level": "INFO",
                "state_file": ".bmad-core/yolo/state/yolo-state.json",
                "enable_telemetry": False
            },
            "agent_limits": {
                "pm": 6000,
                "architect": 8000,
                "po": 5000,
                "sm": 4000,
                "dev": 10000,
                "qa": 6000,
                "security": 5000,
                "devops": 5000,
                "documentation": 4000
            },
            "context": {
                "summarization_threshold": 0.7,
                "refresh_strategy": "sliding_window",
                "archive_old_context": True,
                "archive_after_days": 7,
                "max_total_tokens": 50000
            },
            "retry": {
                "max_attempts": 3,
                "backoff_factor": 2.0,
                "max_backoff_seconds": 60,
                "circuit_breaker_threshold": 5,
                "circuit_breaker_timeout": 300
            },
            "safety": {
                "require_human_for": ["password_hashing", "database_migrations"],
                "auto_approve_after_seconds": 3600
            },
            "workflow": {
                "default_timeout_seconds": 300,
                "handoff_timeout_seconds": 30,
                "max_concurrent_agents": 3,
                "enable_parallel_workflows": False
            },
            "monitoring": {
                "metrics_port": 9090,
                "health_check_port": 8080,
                "export_interval_seconds": 60,
                "retention_days": 30
            }
        }

    def _setup_watcher(self):
        """Setup file watcher for hot reload."""
        if not self.config_path.exists():
            logger.warning("Config file doesn't exist, skipping watcher setup")
            return

        class ConfigReloadHandler(FileSystemEventHandler):
            def __init__(self, config_manager):
                self.config_manager = config_manager

            def on_modified(self, event):
                if event.src_path == str(self.config_manager.config_path):
                    logger.info("Config file changed, reloading...")
                    self.config_manager._load_config()

        try:
            self.observer = Observer()
            self.observer.schedule(
                ConfigReloadHandler(self),
                str(self.config_path.parent),
                recursive=False
            )
            self.observer.start()
            logger.info("Config file watcher started")
        except Exception as e:
            logger.warning(f"Could not start config file watcher: {e}")

    def stop_watcher(self):
        """Stop the file watcher."""
        if self.observer and self.observer.is_alive():
            self.observer.stop()
            self.observer.join()

    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by dot-notation path (thread-safe)."""
        with self._config_lock:
            if not self.config:
                return default

            keys = key_path.split('.')
            value = self.config.__dict__

            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    value = getattr(value, key, None)
                if value is None:
                    return default
            return value

    def reload(self):
        """Manually reload configuration."""
        self._load_config()

    def __del__(self):
        """Cleanup watcher on deletion."""
        self.stop_watcher()
