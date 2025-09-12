# Feature Flags System Documentation

## Overview

The RuleIQ Feature Flags System provides a robust, high-performance mechanism for controlling feature rollouts with <1ms access time. It supports percentage-based rollouts, user targeting, environment-specific configurations, and comprehensive audit trails.

## Table of Contents

1. [Architecture](#architecture)
2. [Key Features](#key-features)
3. [Usage Guide](#usage-guide)
4. [API Reference](#api-reference)
5. [Configuration](#configuration)
6. [Performance](#performance)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Architecture

### Components

```
┌─────────────────────────────────────────────────────────┐
│                     API Layer                            │
│            (FastAPI Endpoints for Management)            │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                  Service Layer                           │
│         (EnhancedFeatureFlagService)                    │
│   - Evaluation Logic                                     │
│   - Cache Management                                     │
│   - Performance Tracking                                 │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
┌───────────────────┐               ┌───────────────────┐
│   Redis Cache     │               │   PostgreSQL DB   │
│   (60s TTL)       │               │   (Persistent)    │
│   <1ms access     │               │   Audit Trail     │
└───────────────────┘               └───────────────────┘
```

### Data Flow

1. **Evaluation Request** → Check Redis Cache → Return if hit
2. **Cache Miss** → Load from PostgreSQL → Cache in Redis → Return
3. **Updates** → Write to PostgreSQL → Invalidate Redis Cache → Create Audit Log

## Key Features

### 1. Environment-Specific Overrides

```python
# Configure different behaviors per environment
flag_config = {
    "environment_overrides": {
        "development": True,
        "staging": True,
        "production": False
    }
}
```

### 2. Percentage Rollouts

```python
# Gradual rollout to 25% of users
flag_config = {
    "enabled": True,
    "percentage": 25.0  # 25% of users will see the feature
}
```

### 3. User Targeting

```python
# Whitelist specific users
flag_config = {
    "whitelist": ["user123", "beta_tester_456"],
    "blacklist": ["problematic_user_789"]
}
```

### 4. Temporal Controls

```python
# Time-based feature flags
flag_config = {
    "starts_at": "2025-01-15T00:00:00Z",
    "expires_at": "2025-02-15T23:59:59Z"
}
```

## Usage Guide

### Basic Usage with Decorator

```python
from services.feature_flag_service import feature_flag

@feature_flag("new_dashboard")
async def get_dashboard_data(user_id: str):
    """This function only executes if the feature flag is enabled"""
    return {"data": "new dashboard"}
```

### With Fallback Function

```python
async def old_dashboard(user_id: str):
    return {"data": "legacy dashboard"}

@feature_flag("new_dashboard", fallback=old_dashboard)
async def get_dashboard_data(user_id: str):
    return {"data": "new dashboard"}
```

### Direct Service Usage

```python
from services.feature_flag_service import get_feature_flag_service

service = get_feature_flag_service()

# Check if feature is enabled for user
enabled, reason = await service.is_enabled_for_user(
    flag_name="ai_assistant",
    user_id="user123",
    environment="production"
)

if enabled:
    # Feature is enabled
    activate_ai_assistant()
else:
    # Feature is disabled
    print(f"AI Assistant disabled: {reason}")
```

### Updating Feature Flags

```python
from services.feature_flag_service import FeatureFlagConfig

config = FeatureFlagConfig(
    name="new_feature",
    enabled=True,
    percentage=50,
    whitelist=["beta_user_1"],
    environments=["staging", "production"]
)

await service.update_flag(
    flag_name="new_feature",
    config=config,
    user_id="admin",
    reason="Increasing rollout to 50%"
)
```

## API Reference

### Endpoints

#### List All Feature Flags
```http
GET /api/v1/feature-flags
```

Query Parameters:
- `environment`: Filter by environment
- `tag`: Filter by tag
- `enabled`: Filter by enabled status
- `skip`: Pagination offset
- `limit`: Number of results

#### Get Specific Feature Flag
```http
GET /api/v1/feature-flags/{flag_name}
```

#### Create Feature Flag
```http
POST /api/v1/feature-flags
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "new_feature",
  "description": "A new feature",
  "enabled": false,
  "percentage": 0,
  "whitelist": [],
  "blacklist": [],
  "environments": ["development"]
}
```

#### Update Feature Flag
```http
PUT /api/v1/feature-flags/{flag_name}
Authorization: Bearer {token}
Content-Type: application/json

{
  "enabled": true,
  "percentage": 25,
  "reason": "Starting gradual rollout"
}
```

#### Evaluate Feature Flag
```http
POST /api/v1/feature-flags/{flag_name}/evaluate
Content-Type: application/json

{
  "user_id": "user123",
  "environment": "production"
}
```

Response:
```json
{
  "flag_name": "new_feature",
  "enabled": true,
  "reason": "percentage",
  "evaluation_time_ms": 0.45
}
```

#### Bulk Evaluate Feature Flags
```http
POST /api/v1/feature-flags/evaluate-bulk
Content-Type: application/json

{
  "flag_names": ["feature1", "feature2", "feature3"],
  "user_id": "user123",
  "environment": "production"
}
```

#### Get Audit Trail
```http
GET /api/v1/feature-flags/{flag_name}/audit
Authorization: Bearer {token}
```

#### Get Metrics
```http
GET /api/v1/feature-flags/metrics/{flag_name}?hours=24
Authorization: Bearer {token}
```

## Configuration

### Environment Variables

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=50

# Feature Flag Defaults
FF_CACHE_TTL=60  # Cache TTL in seconds
FF_ENABLE_METRICS=true
```

### Database Schema

The system uses four main tables:

1. **feature_flags**: Main flag configuration
2. **feature_flag_audits**: Change history
3. **feature_flag_evaluations**: Usage analytics
4. **feature_flag_groups**: Logical grouping

### Redis Cache Structure

```
ff:{flag_name}                    # Main flag cache
ff:{flag_name}:user:{user_id}    # User-specific cache
ff:metrics:{flag_name}:{hour}    # Hourly metrics
```

## Performance

### Benchmarks

- **Cache Hit**: < 0.5ms
- **Cache Miss**: < 10ms (includes DB query + cache write)
- **Bulk Evaluation (10 flags)**: < 5ms
- **Cache TTL**: 60 seconds
- **Concurrent Evaluations**: 10,000+ per second

### Optimization Techniques

1. **Redis Connection Pooling**: Max 50 connections
2. **LRU Cache**: In-memory caching for hot flags
3. **Consistent Hashing**: Deterministic user bucketing
4. **Batch Operations**: Bulk evaluation support
5. **Async Processing**: Non-blocking I/O

## Best Practices

### 1. Naming Conventions

```python
# Use descriptive, hierarchical names
"feature.module.specific_feature"
"ui.dashboard.new_layout"
"api.v2.enhanced_endpoints"
```

### 2. Gradual Rollouts

```python
# Start small and increase gradually
Day 1: 5%
Day 3: 25%
Day 7: 50%
Day 14: 100%
```

### 3. Environment Strategy

```python
# Test in lower environments first
Development → Staging → Production (5%) → Production (100%)
```

### 4. Monitoring

- Track evaluation metrics
- Monitor cache hit rates
- Set up alerts for errors
- Review audit logs regularly

### 5. Clean Up

- Remove old/unused flags
- Archive completed rollouts
- Document flag purposes

## Troubleshooting

### Common Issues

#### 1. Flag Not Found
```python
# Check if flag exists in database
SELECT * FROM feature_flags WHERE name = 'flag_name';
```

#### 2. Cache Issues
```python
# Manually invalidate cache
await service.invalidate_cache("flag_name")

# Check Redis connection
redis-cli ping
```

#### 3. Performance Degradation
```python
# Check cache hit rate
GET ff:metrics:flag_name:2025010915

# Monitor Redis memory
redis-cli INFO memory
```

#### 4. Inconsistent Behavior
```python
# Verify user hashing
hash_value = service._hash_user_id("flag_name", "user_id")
print(f"User hash: {hash_value}, Enabled: {hash_value < percentage}")
```

### Debug Mode

Enable debug logging:
```python
import logging
logging.getLogger("services.feature_flag_service").setLevel(logging.DEBUG)
```

## Migration Guide

### From Static Configuration

Before:
```python
if settings.ENABLE_NEW_FEATURE:
    # Feature code
```

After:
```python
@feature_flag("new_feature")
def feature_code():
    # Feature code
```

### Database Migration

Run the Alembic migration:
```bash
alembic upgrade head
```

## Security Considerations

1. **Authentication Required**: Management endpoints require JWT authentication
2. **Audit Trail**: All changes are logged with user information
3. **Rate Limiting**: API endpoints are rate-limited
4. **Input Validation**: All inputs are validated with Pydantic
5. **SQL Injection Protection**: Using SQLAlchemy ORM

## Examples

### A/B Testing
```python
@feature_flag("experiment_variant_a")
async def variant_a():
    return {"variant": "A"}

@feature_flag("experiment_variant_b")
async def variant_b():
    return {"variant": "B"}
```

### Feature Sunset
```python
flag_config = {
    "name": "legacy_feature",
    "enabled": True,
    "expires_at": "2025-03-01T00:00:00Z",
    "metadata": {
        "deprecation_notice": "This feature will be removed on March 1, 2025"
    }
}
```

### Emergency Kill Switch
```python
# Immediately disable feature for all users
await service.update_flag(
    "problematic_feature",
    FeatureFlagConfig(enabled=False, percentage=0),
    reason="Emergency: Critical bug discovered"
)
```

## Support

For questions or issues:
1. Check this documentation
2. Review the test suite in `tests/test_feature_flags.py`
3. Check audit logs for flag history
4. Contact the platform team

## License

Copyright © 2025 RuleIQ. All rights reserved.