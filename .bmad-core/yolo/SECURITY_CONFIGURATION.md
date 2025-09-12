# YOLO Configuration Security Guide

## Environment Variable Security Best Practices

### Overview
The YOLO configuration system supports environment variable overrides, which can be powerful but also pose security risks if not handled properly. This guide outlines best practices for secure configuration management.

## Security Considerations

### 1. Sensitive Data in Environment Variables

**Risk**: Environment variables can be exposed through:
- Process listings (`ps aux`)
- Environment dumps in error logs
- Container inspection
- Memory dumps

**Mitigation**:
- Never store passwords, API keys, or secrets in environment variables
- Use secret management systems (e.g., HashiCorp Vault, AWS Secrets Manager)
- Load secrets at runtime from secure stores

### 2. Environment Variable Naming Convention

The YOLO system uses the prefix `YOLO_` for all configuration overrides:

```bash
# Safe configuration overrides
export YOLO_SYSTEM_MODE=active
export YOLO_AGENT_LIMITS_DEV=15000
export YOLO_RETRY_MAX_ATTEMPTS=5

# NEVER DO THIS - Sensitive data exposure
export YOLO_API_KEY=secret123  # BAD!
export YOLO_DATABASE_PASSWORD=pass123  # BAD!
```

### 3. Configuration File Security

**File Permissions**:
```bash
# Set restrictive permissions on config files
chmod 600 .bmad-core/yolo/config/yolo-config.yaml
chown $USER:$USER .bmad-core/yolo/config/yolo-config.yaml
```

**File Integrity**:
- The system now validates file integrity using SHA256 checksums
- Changes are logged with checksum prefix for audit trail
- Unexpected changes trigger warnings

### 4. Secure Configuration Hierarchy

1. **Default Values** (Least Privileged)
   - Safe, minimal configuration
   - Production-ready defaults

2. **Configuration File** (Controlled)
   - Version controlled
   - Code reviewed
   - No secrets

3. **Environment Variables** (Runtime)
   - Non-sensitive overrides only
   - Deployment-specific settings
   - Feature flags

4. **Secret Store** (Most Secure)
   - API keys, passwords
   - Certificates
   - Encryption keys

## Implementation Examples

### Safe Environment Variable Usage

```python
# Good - Non-sensitive configuration
os.environ['YOLO_SYSTEM_MODE'] = 'active'
os.environ['YOLO_AGENT_LIMITS_QA'] = '8000'
os.environ['YOLO_MONITORING_METRICS_PORT'] = '9091'

# Bad - Sensitive data in environment
os.environ['YOLO_DATABASE_PASSWORD'] = 'secret'  # NO!
os.environ['YOLO_API_TOKEN'] = 'token123'  # NO!
```

### Secure Secret Loading Pattern

```python
import os
from pathlib import Path

class SecureConfigManager(ConfigManager):
    """Extended config manager with secure secret loading."""
    
    def load_secrets(self):
        """Load secrets from secure store."""
        # Option 1: Load from secure file
        secrets_file = Path('/run/secrets/yolo-secrets')
        if secrets_file.exists() and secrets_file.stat().st_mode & 0o077 == 0:
            with open(secrets_file) as f:
                secrets = json.load(f)
                # Apply secrets to config (not environment)
                self._apply_secrets(secrets)
        
        # Option 2: Load from secret manager
        if 'VAULT_ADDR' in os.environ:
            vault_client = VaultClient()
            secrets = vault_client.get_secrets('yolo/')
            self._apply_secrets(secrets)
    
    def _apply_secrets(self, secrets: Dict[str, Any]):
        """Apply secrets to configuration securely."""
        # Store in memory only, never in files or environment
        self.config.secrets = secrets
```

## Security Checklist

### Development Environment
- [ ] No production secrets in development configs
- [ ] Use `.env.example` files without real values
- [ ] Add `.env` to `.gitignore`

### Production Deployment
- [ ] Config files have restrictive permissions (600 or 640)
- [ ] Environment variables contain no secrets
- [ ] Secrets loaded from secure store at runtime
- [ ] Audit logging enabled for config changes
- [ ] Config file integrity validation active

### Code Review Checklist
- [ ] No hardcoded secrets in code
- [ ] No secrets in configuration files
- [ ] Environment variable names don't suggest sensitive data
- [ ] Proper error handling doesn't expose config values

## Monitoring and Auditing

### Configuration Change Detection

The system logs configuration changes:
```
INFO: Config file changed (checksum: a3f2b8c1...)
WARNING: Config file integrity check failed, using cached config
```

### Recommended Monitoring
1. Monitor config file changes
2. Alert on unexpected environment variables
3. Track configuration reload events
4. Audit access to secret stores

## Common Vulnerabilities and Fixes

### 1. Environment Variable Injection
**Vulnerability**: Untrusted input used in environment variable names
```python
# Bad
var_name = f"YOLO_{user_input}"
os.environ[var_name] = value
```

**Fix**: Validate and whitelist allowed configuration keys
```python
# Good
ALLOWED_KEYS = ['system_mode', 'agent_limits_dev', ...]
if user_input in ALLOWED_KEYS:
    var_name = f"YOLO_{user_input.upper()}"
    os.environ[var_name] = value
```

### 2. Config File Path Traversal
**Vulnerability**: User-controlled config file paths
```python
# Bad
config = ConfigManager(user_provided_path)
```

**Fix**: Validate and restrict file paths
```python
# Good
config_path = Path(user_provided_path).resolve()
if not config_path.is_relative_to(ALLOWED_CONFIG_DIR):
    raise SecurityError("Invalid config path")
```

### 3. Logging Sensitive Configuration
**Vulnerability**: Config values in logs
```python
# Bad
logger.info(f"Config loaded: {config}")
```

**Fix**: Sanitize logs
```python
# Good
logger.info(f"Config loaded from {config_path}")
# Log only non-sensitive metadata
```

## Emergency Response

### If Secrets Are Exposed

1. **Immediate Actions**:
   - Rotate all exposed credentials
   - Revoke exposed API keys
   - Change all passwords

2. **Investigation**:
   - Review logs for unauthorized access
   - Check git history for committed secrets
   - Audit environment variable usage

3. **Prevention**:
   - Implement secret scanning in CI/CD
   - Use pre-commit hooks to detect secrets
   - Regular security audits

## Tools and Resources

### Secret Detection Tools
- **git-secrets**: Prevents committing secrets
- **truffleHog**: Scans git history for secrets
- **detect-secrets**: Pre-commit hook for secret detection

### Secret Management Solutions
- **HashiCorp Vault**: Enterprise secret management
- **AWS Secrets Manager**: Cloud-native secret store
- **Kubernetes Secrets**: Container orchestration secrets
- **Docker Secrets**: Container runtime secrets

## Conclusion

Security is a shared responsibility. While the YOLO configuration system provides integrity checking and secure loading mechanisms, proper usage and deployment practices are essential for maintaining security.

Remember: **Never store secrets in environment variables or configuration files**. Always use dedicated secret management solutions for sensitive data.