# RuleIQ Performance Optimization Guide

## Overview

This document describes the comprehensive performance optimizations implemented for the RuleIQ backend, including database query optimization, caching strategies, connection pooling, and response compression.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Database Optimizations](#database-optimizations)
3. [Caching Layer](#caching-layer)
4. [Connection Pooling](#connection-pooling)
5. [Response Compression](#response-compression)
6. [Performance Monitoring](#performance-monitoring)
7. [Benchmarking](#benchmarking)
8. [Best Practices](#best-practices)

## Architecture Overview

The performance optimization system consists of several integrated components:

```
┌─────────────────────────────────────────────────┐
│                FastAPI Application              │
├─────────────────────────────────────────────────┤
│          Performance Middleware Layer           │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │ Response │ │  Request │ │   Metrics    │   │
│  │Compression│ │  Timing  │ │  Collection  │   │
│  └──────────┘ └──────────┘ └──────────────┘   │
├─────────────────────────────────────────────────┤
│              Service Layer                      │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │  Query   │ │  Cache   │ │   Batch      │   │
│  │Optimization│ │ Manager │ │  Processing  │   │
│  └──────────┘ └──────────┘ └──────────────┘   │
├─────────────────────────────────────────────────┤
│           Infrastructure Layer                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │   DB     │ │  Redis   │ │  Connection  │   │
│  │   Pool   │ │   Pool   │ │   Manager    │   │
│  └──────────┘ └──────────┘ └──────────────┘   │
└─────────────────────────────────────────────────┘
```

## Database Optimizations

### 1. Query Optimization

The `DatabaseOptimizer` class provides automatic query optimization:

```python
from infrastructure.performance import DatabaseOptimizer

# Initialize optimizer
optimizer = DatabaseOptimizer(session)

# Get index recommendations
recommendations = await optimizer.recommend_indexes()

# Analyze slow queries
slow_queries = await optimizer.analyze_slow_queries(threshold_ms=1000)

# Create recommended indexes
for rec in recommendations:
    await optimizer.create_index(rec.table, rec.columns)
```

### 2. N+1 Query Prevention

Use eager loading to prevent N+1 queries:

```python
from sqlalchemy.orm import selectinload, joinedload

# Optimized assessment query
stmt = (
    select(AssessmentSession)
    .options(
        joinedload(AssessmentSession.business_profile),
        selectinload(AssessmentSession.questions),
        selectinload(AssessmentSession.frameworks)
    )
)
```

### 3. Connection Pooling

Optimized database connection pool configuration:

```python
# config/settings.py
database_pool_size = 10          # Base pool size
database_max_overflow = 20       # Maximum overflow connections
database_pool_timeout = 30       # Connection timeout (seconds)
database_pool_recycle = 3600     # Recycle connections after 1 hour
```

The system automatically adjusts pool size based on system resources:
- 8+ CPUs, 16+ GB RAM: 2x base pool size
- 4+ CPUs, 8+ GB RAM: 1.5x base pool size
- Otherwise: Base pool size

### 4. Index Management

Essential indexes for performance:

```sql
-- Foreign key indexes (automatically recommended)
CREATE INDEX idx_business_profiles_user_id ON business_profiles(user_id);
CREATE INDEX idx_assessment_sessions_user_id ON assessment_sessions(user_id);
CREATE INDEX idx_assessment_sessions_business_profile_id ON assessment_sessions(business_profile_id);

-- Frequently queried columns
CREATE INDEX idx_assessment_sessions_status ON assessment_sessions(status);
CREATE INDEX idx_assessment_sessions_created_at ON assessment_sessions(created_at DESC);

-- Composite indexes for common queries
CREATE INDEX idx_assessment_sessions_user_status ON assessment_sessions(user_id, status);
```

## Caching Layer

### 1. Redis Cache Manager

The `CacheManager` provides a high-performance caching layer:

```python
from infrastructure.performance import CacheManager, cached

# Using the cache decorator
@cached(ttl=3600, prefix="user_profile")
async def get_user_profile(user_id: UUID):
    # Expensive database query
    return await db.query(UserProfile).filter_by(id=user_id).first()

# Manual cache operations
cache = await get_cache_manager()

# Set value with TTL
await cache.set("key", value, ttl=300)

# Get value
value = await cache.get("key")

# Batch operations for performance
await cache.mset({"key1": value1, "key2": value2}, ttl=600)
values = await cache.mget(["key1", "key2"])

# Pattern-based deletion
await cache.delete_pattern("assessment:*")
```

### 2. Query Result Caching

Cache database query results:

```python
from infrastructure.performance import cached_query

@cached_query(ttl=600, prefix="assessment:session")
async def get_assessment_session(db: AsyncSession, session_id: UUID):
    stmt = select(AssessmentSession).where(AssessmentSession.id == session_id)
    result = await db.execute(stmt)
    return result.scalars().first()
```

### 3. Cache TTL Strategy

Recommended TTL values for different data types:

| Data Type | TTL (seconds) | Reason |
|-----------|---------------|---------|
| User Profile | 3600 | Rarely changes |
| Assessment Session | 1800 | Active updates |
| Business Profile | 3600 | Infrequent changes |
| Compliance Framework | 7200 | Static data |
| Dashboard Stats | 300 | Real-time data |
| Framework List | 86400 | Rarely changes |

## Connection Pooling

### 1. Database Connection Pool

Optimized PostgreSQL connection pooling:

```python
from infrastructure.performance import get_pool_manager

pool_manager = await get_pool_manager()

# Get database session from pool
async with pool_manager.get_db_session() as session:
    # Use session
    await session.execute(query)

# Monitor pool statistics
stats = await pool_manager.get_pool_stats()
print(f"Active connections: {stats['database']['checked_out']}")
print(f"Available connections: {stats['database']['checked_in']}")
```

### 2. Redis Connection Pool

Optimized Redis connection pooling:

```python
# Get Redis client from pool
async with pool_manager.get_redis_client() as client:
    await client.set("key", "value")
    value = await client.get("key")
```

### 3. Pool Health Monitoring

```python
# Check pool health
health = await pool_manager.health_check()
print(f"Database healthy: {health['database']}")
print(f"Redis healthy: {health['redis']}")

# Get optimization recommendations
optimizations = await pool_manager.optimize_pools()
```

## Response Compression

### 1. Automatic Compression

Responses are automatically compressed using the best available algorithm:

- **Brotli**: Best compression ratio (priority 1)
- **Zstandard**: Fast compression (priority 2)
- **Gzip**: Universal support (priority 3)

### 2. Configuration

```python
# Compression is applied to:
- Responses > 1000 bytes
- Content types: JSON, HTML, CSS, JavaScript, XML, CSV
- Excluded paths: /health, /metrics, /docs

# Usage
from infrastructure.performance import CompressionMiddleware

app.add_middleware(
    CompressionMiddleware,
    minimum_size=1000,
    exclude_paths={'/health', '/metrics'}
)
```

## Performance Monitoring

### 1. Metrics Collection

The system automatically collects performance metrics:

```python
from infrastructure.performance import measure_performance, get_metrics

@measure_performance("api.endpoint")
async def api_endpoint():
    # Function execution is automatically timed
    pass

# Get metrics summary
metrics = get_metrics()
summary = metrics.get_metrics_summary()
slow_ops = metrics.get_slow_operations(threshold=1.0)
```

### 2. API Endpoints

Performance monitoring endpoints:

```bash
# Get performance metrics
GET /api/v1/performance/metrics

# Get database statistics
GET /api/v1/performance/database/stats?table_name=users

# Get cache statistics
GET /api/v1/performance/cache/stats

# Get connection pool statistics
GET /api/v1/performance/pool/stats

# Health check
GET /api/v1/performance/health

# Run benchmarks
GET /api/v1/performance/benchmark?component=database&iterations=100
```

### 3. Slow Request Detection

Requests exceeding the threshold (default 1.0s) are automatically logged:

```python
# config/settings.py
slow_request_threshold = 1.0  # seconds

# Slow requests are logged with details:
# - Method and path
# - Processing time
# - Status code
```

## Benchmarking

### 1. Running Benchmarks

Run the comprehensive benchmark suite:

```bash
cd scripts
python performance_benchmark.py
```

This runs benchmarks for:
- Database queries (simple, join, aggregation)
- Cache operations (get, set, delete, batch)
- Connection pools (concurrent requests)
- Query optimization analysis

### 2. Benchmark Results

Example benchmark results:

```
Database Queries Results:
--------------------------
simple_select:
  Mean:   0.45 ms
  Median: 0.42 ms
  P95:    0.68 ms
  P99:    0.95 ms

Cache Operations Results:
-------------------------
get_hit:
  Mean:   0.23 ms
  Median: 0.21 ms
  P95:    0.35 ms
  P99:    0.48 ms

Connection Pools Results:
------------------------
database_pool:
  Concurrent requests: 50
  Mean:   12.3 ms
  Max utilization: 85%
```

### 3. Performance Targets

Recommended performance targets:

| Operation | Target (P95) | Critical |
|-----------|-------------|----------|
| Simple SELECT | < 5ms | < 10ms |
| Complex JOIN | < 50ms | < 100ms |
| Cache GET | < 2ms | < 5ms |
| Cache SET | < 3ms | < 10ms |
| API Response | < 200ms | < 500ms |

## Best Practices

### 1. Query Optimization

- **Always use eager loading** for relationships to prevent N+1 queries
- **Add indexes** on foreign keys and frequently filtered columns
- **Use pagination** for large result sets
- **Batch operations** when processing multiple items

### 2. Caching Strategy

- **Cache at multiple levels**: Query results, computed values, API responses
- **Use appropriate TTLs** based on data volatility
- **Implement cache warming** for frequently accessed data
- **Monitor cache hit rates** and adjust strategies accordingly

### 3. Connection Management

- **Use connection pools** exclusively, never create connections manually
- **Monitor pool utilization** and adjust size as needed
- **Implement connection retry logic** for resilience
- **Use async operations** throughout the application

### 4. Response Optimization

- **Enable compression** for all text-based responses
- **Implement pagination** for list endpoints
- **Use field filtering** to reduce response size
- **Optimize JSON serialization** with fast libraries (orjson)

### 5. Monitoring and Alerting

- **Track key metrics**: Response times, error rates, cache hit rates
- **Set up alerts** for performance degradation
- **Regular benchmarking** to catch regressions
- **Profile production workloads** to identify bottlenecks

## Configuration Examples

### Development Environment

```python
# .env.local
DATABASE_POOL_SIZE=5
DATABASE_MAX_OVERFLOW=10
REDIS_MAX_CONNECTIONS=10
SLOW_REQUEST_THRESHOLD=2.0
ENABLE_PERFORMANCE_MONITORING=true
```

### Production Environment

```python
# .env.production
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=40
REDIS_MAX_CONNECTIONS=50
SLOW_REQUEST_THRESHOLD=1.0
ENABLE_PERFORMANCE_MONITORING=true
ENABLE_COMPRESSION=true
```

## Troubleshooting

### High Database Response Times

1. Check slow query log: `GET /api/v1/performance/database/stats`
2. Review index recommendations
3. Increase connection pool size if utilization > 80%
4. Consider query result caching

### Low Cache Hit Rates

1. Review TTL configurations
2. Identify frequently accessed uncached data
3. Implement cache warming for static data
4. Monitor cache evictions

### Connection Pool Exhaustion

1. Check pool statistics: `GET /api/v1/performance/pool/stats`
2. Identify long-running transactions
3. Increase pool size or optimize queries
4. Implement connection timeout handling

## Integration with Existing Code

To integrate optimizations into existing services:

```python
# services/optimized/example_service.py
from infrastructure.performance import (
    CacheManager,
    cached_query,
    measure_performance,
    EagerLoadingOptimizer
)

class OptimizedService:
    def __init__(self):
        self.cache = CacheManager()
        
    @measure_performance("service.operation")
    @cached_query(ttl=600)
    async def get_data(self, db: AsyncSession, id: UUID):
        # Optimized query with eager loading
        stmt = select(Model).options(
            selectinload(Model.relationship)
        ).where(Model.id == id)
        
        result = await db.execute(stmt)
        return result.scalars().first()
```

## Future Improvements

1. **Read Replicas**: Implement read/write splitting for database queries
2. **Query Plan Caching**: Cache prepared statements for frequently used queries
3. **Adaptive Caching**: Automatically adjust TTLs based on access patterns
4. **Distributed Caching**: Implement Redis Cluster for horizontal scaling
5. **GraphQL DataLoader**: Batch and cache GraphQL resolver queries
6. **CDN Integration**: Cache static assets and API responses at edge locations

## Conclusion

The performance optimization system provides comprehensive improvements across all layers of the application. By following the best practices and utilizing the provided tools, the RuleIQ backend can handle significant load while maintaining excellent response times.

For questions or issues, please refer to the monitoring endpoints or run the benchmark suite to identify specific bottlenecks.