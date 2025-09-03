"""
Performance monitoring and optimization API endpoints.

Provides endpoints for monitoring system performance and optimization controls.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_db
from auth.dependencies import get_current_user
from database.user import User

from infrastructure.performance import (
    get_metrics,
    get_cache_manager,
    get_pool_manager,
    DatabaseOptimizer,
    QueryAnalyzer
)

router = APIRouter(prefix="/performance", tags=["Performance"])


@router.get("/metrics")
async def get_performance_metrics(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get current performance metrics.
    
    Returns comprehensive performance statistics including:
    - Query performance metrics
    - Cache hit rates
    - Connection pool statistics
    - Response time distributions
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
        
    metrics = get_metrics()
    cache_manager = await get_cache_manager()
    pool_manager = await get_pool_manager()
    
    # Gather all metrics
    performance_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "metrics": metrics.get_metrics_summary(),
        "slow_operations": metrics.get_slow_operations(),
        "pool_stats": await pool_manager.get_pool_stats(),
        "cache_stats": {
            "enabled": cache_manager._initialized,
            "connection_status": "connected" if cache_manager._redis_client else "disconnected"
        }
    }
    
    return performance_data


@router.get("/database/stats")
async def get_database_statistics(
    table_name: Optional[str] = Query(None, description="Specific table to analyze"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get database performance statistics.
    
    Provides:
    - Table sizes and row counts
    - Index usage statistics
    - Slow query analysis
    - Optimization recommendations
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
        
    optimizer = DatabaseOptimizer(db)
    
    if table_name:
        # Get stats for specific table
        stats = await optimizer.get_table_statistics(table_name)
        indexes = await optimizer.analyze_table_indexes(table_name)
        
        return {
            "table": table_name,
            "statistics": stats,
            "indexes": indexes
        }
    else:
        # Get overall database stats
        recommendations = await optimizer.recommend_indexes()
        slow_queries = await optimizer.analyze_slow_queries()
        
        return {
            "recommendations": [
                {
                    "table": rec.table,
                    "columns": rec.columns,
                    "reason": rec.reason,
                    "priority": rec.priority,
                    "estimated_improvement": rec.estimated_improvement
                }
                for rec in recommendations
            ],
            "slow_queries": slow_queries,
            "analysis_timestamp": datetime.utcnow().isoformat()
        }


@router.post("/database/optimize")
async def optimize_database(
    action: str = Query(..., description="Optimization action: vacuum, analyze, create_index"),
    table_name: str = Query(..., description="Table to optimize"),
    columns: Optional[List[str]] = Query(None, description="Columns for index creation"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Perform database optimization actions.
    
    Available actions:
    - vacuum: Run VACUUM on table
    - analyze: Run ANALYZE on table
    - create_index: Create index on specified columns
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
        
    optimizer = DatabaseOptimizer(db)
    
    if action == "vacuum":
        success = await optimizer.vacuum_analyze_table(table_name)
        return {
            "action": "vacuum",
            "table": table_name,
            "success": success,
            "message": f"VACUUM ANALYZE {'completed' if success else 'failed'} for {table_name}"
        }
        
    elif action == "analyze":
        success = await optimizer.vacuum_analyze_table(table_name)
        return {
            "action": "analyze",
            "table": table_name,
            "success": success,
            "message": f"ANALYZE {'completed' if success else 'failed'} for {table_name}"
        }
        
    elif action == "create_index":
        if not columns:
            raise HTTPException(status_code=400, detail="Columns required for index creation")
            
        success = await optimizer.create_index(table_name, columns)
        index_name = f"idx_{table_name}_{'_'.join(columns)}"
        
        return {
            "action": "create_index",
            "table": table_name,
            "columns": columns,
            "index_name": index_name,
            "success": success,
            "message": f"Index {'created' if success else 'creation failed'}"
        }
        
    else:
        raise HTTPException(status_code=400, detail=f"Unknown action: {action}")


@router.get("/cache/stats")
async def get_cache_statistics(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get cache performance statistics.
    
    Returns:
    - Hit/miss rates
    - Cache size information
    - Most frequently cached keys
    - Cache effectiveness metrics
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
        
    cache_manager = await get_cache_manager()
    metrics = get_metrics()
    
    # Get cache-specific metrics
    cache_stats = {
        "enabled": cache_manager._initialized,
        "connection_status": "connected" if cache_manager._redis_client else "disconnected"
    }
    
    if cache_manager._redis_client:
        try:
            # Get Redis info
            info = await cache_manager._redis_client.info()
            cache_stats.update({
                "memory_used": info.get("used_memory_human", "unknown"),
                "memory_peak": info.get("used_memory_peak_human", "unknown"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": (
                    info.get("keyspace_hits", 0) / 
                    (info.get("keyspace_hits", 0) + info.get("keyspace_misses", 1))
                    if info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0) > 0
                    else 0
                )
            })
        except Exception as e:
            cache_stats["error"] = str(e)
            
    return cache_stats


@router.post("/cache/clear")
async def clear_cache(
    pattern: Optional[str] = Query(None, description="Pattern to match keys for deletion"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Clear cache entries.
    
    Parameters:
    - pattern: Optional pattern to match specific keys (e.g., "assessment:*")
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
        
    cache_manager = await get_cache_manager()
    
    if pattern:
        deleted = await cache_manager.delete_pattern(pattern)
        return {
            "action": "clear_pattern",
            "pattern": pattern,
            "deleted_keys": deleted,
            "message": f"Deleted {deleted} keys matching pattern {pattern}"
        }
    else:
        # Clear all cache (be careful!)
        if cache_manager._redis_client:
            await cache_manager._redis_client.flushdb()
            return {
                "action": "clear_all",
                "message": "All cache entries cleared"
            }
        else:
            return {
                "action": "clear_all",
                "message": "Cache not available",
                "success": False
            }


@router.get("/pool/stats")
async def get_connection_pool_statistics(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get connection pool statistics.
    
    Returns:
    - Database pool utilization
    - Redis pool utilization
    - Connection health status
    - Optimization recommendations
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
        
    pool_manager = await get_pool_manager()
    
    stats = await pool_manager.get_pool_stats()
    health = await pool_manager.health_check()
    optimizations = await pool_manager.optimize_pools()
    
    return {
        "statistics": stats,
        "health": health,
        "optimizations": optimizations,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/pool/optimize")
async def optimize_connection_pools(
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Apply connection pool optimizations.
    
    Dynamically adjusts pool sizes based on current usage patterns.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
        
    pool_manager = await get_pool_manager()
    
    # Get optimization recommendations
    optimizations = await pool_manager.optimize_pools()
    
    if not optimizations:
        return {
            "message": "No optimizations needed",
            "current_stats": await pool_manager.get_pool_stats()
        }
        
    # Note: Actual pool resizing would require recreating the engine
    # This is a simplified version that returns recommendations
    
    return {
        "message": "Optimization recommendations generated",
        "recommendations": optimizations,
        "note": "Manual configuration update required to apply these changes"
    }


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive health check endpoint.
    
    Returns system health status without requiring authentication.
    """
    pool_manager = await get_pool_manager()
    cache_manager = await get_cache_manager()
    metrics = get_metrics()
    
    # Perform health checks
    pool_health = await pool_manager.health_check()
    
    # Calculate overall health
    all_healthy = all(pool_health.values())
    
    # Get basic metrics
    metrics_summary = metrics.get_metrics_summary()
    slow_ops = len(metrics.get_slow_operations())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "database": pool_health.get("database", False),
            "redis": pool_health.get("redis", False),
            "cache": cache_manager._initialized
        },
        "metrics": {
            "slow_operations": slow_ops,
            "total_requests": metrics_summary.get("counters", {}).get("requests", 0)
        }
    }


@router.get("/benchmark")
async def run_benchmark(
    component: str = Query(..., description="Component to benchmark: database, cache, api"),
    iterations: int = Query(100, description="Number of iterations"),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Run performance benchmarks.
    
    Executes synthetic benchmarks to measure system performance.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
        
    import time
    import asyncio
    
    results = {
        "component": component,
        "iterations": iterations,
        "results": {}
    }
    
    if component == "database":
        # Simple database benchmark
        db = await get_async_db().__anext__()
        times = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            await db.execute(text("SELECT 1"))
            times.append(time.perf_counter() - start)
            
        results["results"] = {
            "mean_ms": statistics.mean(times) * 1000,
            "median_ms": statistics.median(times) * 1000,
            "min_ms": min(times) * 1000,
            "max_ms": max(times) * 1000,
            "p95_ms": sorted(times)[int(len(times) * 0.95)] * 1000 if times else 0
        }
        
    elif component == "cache":
        # Cache benchmark
        cache_manager = await get_cache_manager()
        times = []
        
        for i in range(iterations):
            key = f"benchmark:{i}"
            value = {"test": i, "data": "x" * 100}
            
            # Write benchmark
            start = time.perf_counter()
            await cache_manager.set(key, value)
            write_time = time.perf_counter() - start
            
            # Read benchmark
            start = time.perf_counter()
            await cache_manager.get(key)
            read_time = time.perf_counter() - start
            
            times.append({"write": write_time, "read": read_time})
            
            # Cleanup
            await cache_manager.delete(key)
            
        write_times = [t["write"] for t in times]
        read_times = [t["read"] for t in times]
        
        results["results"] = {
            "write": {
                "mean_ms": statistics.mean(write_times) * 1000,
                "median_ms": statistics.median(write_times) * 1000,
                "min_ms": min(write_times) * 1000,
                "max_ms": max(write_times) * 1000
            },
            "read": {
                "mean_ms": statistics.mean(read_times) * 1000,
                "median_ms": statistics.median(read_times) * 1000,
                "min_ms": min(read_times) * 1000,
                "max_ms": max(read_times) * 1000
            }
        }
        
    else:
        raise HTTPException(status_code=400, detail=f"Unknown component: {component}")
        
    return results