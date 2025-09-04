#!/usr/bin/env python3
"""
Performance benchmark script for RuleIQ backend.

Runs comprehensive performance tests and generates reports.
"""

import asyncio
import time
import statistics
import json
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select

from config.settings import settings
from database import Base, User, BusinessProfile, AssessmentSession
from infrastructure.performance import (
    CacheManager,
    ConnectionPoolManager,
    DatabaseOptimizer,
    PerformanceMetrics
)


class PerformanceBenchmark:
    """
    Comprehensive performance benchmark suite.
    """
    
    def __init__(self):
        self.results = {}
        self.engine = None
        self.session_factory = None
        self.cache_manager = None
        self.pool_manager = None
        self.metrics = PerformanceMetrics()
        
    async def setup(self):
        """Setup benchmark environment."""
        print("Setting up benchmark environment...")
        
        # Initialize database
        self.engine = create_async_engine(
            settings.database_url,
            pool_size=20,
            max_overflow=40
        )
        self.session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Initialize cache
        self.cache_manager = CacheManager()
        await self.cache_manager.initialize()
        
        # Initialize pool manager
        self.pool_manager = ConnectionPoolManager()
        await self.pool_manager.initialize()
        
        print("Setup complete!")
        
    async def teardown(self):
        """Cleanup benchmark environment."""
        print("Cleaning up...")
        
        if self.cache_manager:
            await self.cache_manager.close()
            
        if self.pool_manager:
            await self.pool_manager.cleanup()
            
        if self.engine:
            await self.engine.dispose()
            
    async def benchmark_database_queries(self, iterations: int = 100):
        """Benchmark database query performance."""
        print(f"\nBenchmarking database queries ({iterations} iterations)...")
        
        results = {
            "simple_select": [],
            "join_query": [],
            "aggregation": [],
            "bulk_insert": [],
            "indexed_search": []
        }
        
        async with self.session_factory() as session:
            # Simple SELECT
            for _ in range(iterations):
                start = time.perf_counter()
                await session.execute(text("SELECT 1"))
                results["simple_select"].append(time.perf_counter() - start)
                
            # JOIN query
            for _ in range(min(iterations, 50)):  # Fewer iterations for complex queries
                start = time.perf_counter()
                query = text("""
                    SELECT u.id, u.email, bp.company_name
                    FROM users u
                    LEFT JOIN business_profiles bp ON u.id = bp.user_id
                    LIMIT 10
                """)
                await session.execute(query)
                results["join_query"].append(time.perf_counter() - start)
                
            # Aggregation query
            for _ in range(min(iterations, 50)):
                start = time.perf_counter()
                query = text("""
                    SELECT COUNT(*) as total,
                           AVG(EXTRACT(EPOCH FROM (NOW() - created_at))) as avg_age
                    FROM users
                """)
                await session.execute(query)
                results["aggregation"].append(time.perf_counter() - start)
                
        # Calculate statistics
        stats = {}
        for query_type, times in results.items():
            if times:
                stats[query_type] = {
                    "count": len(times),
                    "mean_ms": statistics.mean(times) * 1000,
                    "median_ms": statistics.median(times) * 1000,
                    "min_ms": min(times) * 1000,
                    "max_ms": max(times) * 1000,
                    "stdev_ms": statistics.stdev(times) * 1000 if len(times) > 1 else 0,
                    "p95_ms": sorted(times)[int(len(times) * 0.95)] * 1000 if times else 0,
                    "p99_ms": sorted(times)[int(len(times) * 0.99)] * 1000 if times else 0
                }
                
        self.results["database_queries"] = stats
        self._print_stats("Database Queries", stats)
        
    async def benchmark_cache_operations(self, iterations: int = 1000):
        """Benchmark cache operations."""
        print(f"\nBenchmarking cache operations ({iterations} iterations)...")
        
        results = {
            "set": [],
            "get_hit": [],
            "get_miss": [],
            "delete": [],
            "mset": [],
            "mget": []
        }
        
        # Prepare test data
        test_data = {
            "small": {"id": 1, "name": "test"},
            "medium": {"data": "x" * 1000, "items": list(range(100))},
            "large": {"content": "x" * 10000, "nested": {str(i): i for i in range(100)}}
        }
        
        # SET operations
        for i in range(iterations):
            key = f"bench:set:{i}"
            value = test_data["medium"]
            
            start = time.perf_counter()
            await self.cache_manager.set(key, value, ttl=60)
            results["set"].append(time.perf_counter() - start)
            
        # GET operations (hits)
        for i in range(min(iterations, 100)):
            key = f"bench:set:{i}"
            
            start = time.perf_counter()
            await self.cache_manager.get(key)
            results["get_hit"].append(time.perf_counter() - start)
            
        # GET operations (misses)
        for i in range(iterations):
            key = f"bench:miss:{i}"
            
            start = time.perf_counter()
            await self.cache_manager.get(key)
            results["get_miss"].append(time.perf_counter() - start)
            
        # DELETE operations
        for i in range(min(iterations, 100)):
            key = f"bench:set:{i}"
            
            start = time.perf_counter()
            await self.cache_manager.delete(key)
            results["delete"].append(time.perf_counter() - start)
            
        # Batch operations
        batch_size = 10
        for i in range(0, min(iterations, 100), batch_size):
            # MSET
            batch_data = {
                f"bench:mset:{i+j}": test_data["small"]
                for j in range(batch_size)
            }
            
            start = time.perf_counter()
            await self.cache_manager.mset(batch_data, ttl=60)
            results["mset"].append(time.perf_counter() - start)
            
            # MGET
            keys = list(batch_data.keys())
            start = time.perf_counter()
            await self.cache_manager.mget(keys)
            results["mget"].append(time.perf_counter() - start)
            
        # Cleanup
        await self.cache_manager.delete_pattern("bench:*")
        
        # Calculate statistics
        stats = {}
        for op_type, times in results.items():
            if times:
                stats[op_type] = {
                    "count": len(times),
                    "mean_ms": statistics.mean(times) * 1000,
                    "median_ms": statistics.median(times) * 1000,
                    "min_ms": min(times) * 1000,
                    "max_ms": max(times) * 1000,
                    "p95_ms": sorted(times)[int(len(times) * 0.95)] * 1000 if times else 0,
                    "p99_ms": sorted(times)[int(len(times) * 0.99)] * 1000 if times else 0
                }
                
        self.results["cache_operations"] = stats
        self._print_stats("Cache Operations", stats)
        
    async def benchmark_connection_pools(self, concurrent_requests: int = 50):
        """Benchmark connection pool performance."""
        print(f"\nBenchmarking connection pools ({concurrent_requests} concurrent requests)...")
        
        results = {
            "database_pool": [],
            "redis_pool": []
        }
        
        # Database pool benchmark
        async def db_task():
            start = time.perf_counter()
            """Db Task"""
            async with self.pool_manager.get_db_session() as session:
                await session.execute(text("SELECT 1"))
            return time.perf_counter() - start
            
        # Redis pool benchmark
        async def redis_task():
            start = time.perf_counter()
            """Redis Task"""
            async with self.pool_manager.get_redis_client() as client:
                await client.ping()
            return time.perf_counter() - start
            
        # Run concurrent database requests
        print("Testing database pool...")
        db_tasks = [db_task() for _ in range(concurrent_requests)]
        db_times = await asyncio.gather(*db_tasks)
        results["database_pool"] = db_times
        
        # Run concurrent Redis requests
        print("Testing Redis pool...")
        redis_tasks = [redis_task() for _ in range(concurrent_requests)]
        redis_times = await asyncio.gather(*redis_tasks)
        results["redis_pool"] = redis_times
        
        # Get pool statistics
        pool_stats = await self.pool_manager.get_pool_stats()
        
        # Calculate statistics
        stats = {}
        for pool_type, times in results.items():
            if times:
                stats[pool_type] = {
                    "concurrent_requests": len(times),
                    "mean_ms": statistics.mean(times) * 1000,
                    "median_ms": statistics.median(times) * 1000,
                    "min_ms": min(times) * 1000,
                    "max_ms": max(times) * 1000,
                    "p95_ms": sorted(times)[int(len(times) * 0.95)] * 1000,
                    "total_time_ms": sum(times) * 1000
                }
                
        stats["pool_utilization"] = pool_stats
        
        self.results["connection_pools"] = stats
        self._print_stats("Connection Pools", stats)
        
    async def benchmark_query_optimization(self):
        """Benchmark query optimization techniques."""
        print("\nBenchmarking query optimization...")
        
        results = {}
        
        async with self.session_factory() as session:
            optimizer = DatabaseOptimizer(session)
            
            # Get optimization recommendations
            recommendations = await optimizer.recommend_indexes()
            
            # Analyze slow queries
            slow_queries = await optimizer.analyze_slow_queries(threshold_ms=100)
            
            # Get table statistics
            table_stats = {}
            for table in ["users", "business_profiles", "assessment_sessions"]:
                try:
                    stats = await optimizer.get_table_statistics(table)
                    table_stats[table] = stats
                except:
                    pass
                    
            results = {
                "index_recommendations": len(recommendations),
                "slow_queries_found": len(slow_queries),
                "table_statistics": table_stats,
                "recommendations": [
                    {
                        "table": r.table,
                        "columns": r.columns,
                        "reason": r.reason,
                        "priority": r.priority
                    }
                    for r in recommendations[:5]  # Top 5 recommendations
                ]
            }
            
        self.results["query_optimization"] = results
        print(f"Found {len(recommendations)} index recommendations")
        print(f"Found {len(slow_queries)} slow queries")
        
    def _print_stats(self, category: str, stats: Dict[str, Any]):
        """Print statistics in a readable format."""
        print(f"\n{category} Results:")
        print("-" * 50)
        
        for operation, metrics in stats.items():
            if isinstance(metrics, dict) and "mean_ms" in metrics:
                print(f"\n{operation}:")
                print(f"  Mean:   {metrics['mean_ms']:.2f} ms")
                print(f"  Median: {metrics['median_ms']:.2f} ms")
                print(f"  Min:    {metrics['min_ms']:.2f} ms")
                print(f"  Max:    {metrics['max_ms']:.2f} ms")
                if "p95_ms" in metrics:
                    print(f"  P95:    {metrics['p95_ms']:.2f} ms")
                if "p99_ms" in metrics:
                    print(f"  P99:    {metrics['p99_ms']:.2f} ms")
                    
    def generate_report(self):
        """Generate comprehensive benchmark report."""
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "environment": {
                "database_url": settings.database_url.split("@")[1] if "@" in settings.database_url else "local",
                "redis_url": settings.redis_url,
                "pool_size": settings.database_pool_size,
                "max_overflow": settings.database_max_overflow
            },
            "results": self.results,
            "summary": self._generate_summary()
        }
        
        # Save to file
        filename = f"benchmark_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w") as f:
            json.dump(report, f, indent=2, default=str)
            
        print(f"\nReport saved to {filename}")
        return report
        
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate summary of benchmark results."""
        summary = {
            "database_performance": "GOOD",
            "cache_performance": "GOOD",
            "pool_efficiency": "GOOD",
            "recommendations": []
        }
        
        # Check database performance
        if "database_queries" in self.results:
            simple_select = self.results["database_queries"].get("simple_select", {})
            if simple_select.get("mean_ms", 0) > 10:
                summary["database_performance"] = "NEEDS_OPTIMIZATION"
                summary["recommendations"].append("Database queries are slow, consider connection pooling optimization")
                
        # Check cache performance
        if "cache_operations" in self.results:
            cache_get = self.results["cache_operations"].get("get_hit", {})
            if cache_get.get("mean_ms", 0) > 5:
                summary["cache_performance"] = "NEEDS_OPTIMIZATION"
                summary["recommendations"].append("Cache operations are slow, check Redis connection")
                
        # Check pool efficiency
        if "connection_pools" in self.results:
            db_pool = self.results["connection_pools"].get("database_pool", {})
            if db_pool.get("mean_ms", 0) > 50:
                summary["pool_efficiency"] = "NEEDS_OPTIMIZATION"
                summary["recommendations"].append("Connection pool may be undersized")
                
        return summary


async def main():
    """Run comprehensive performance benchmark."""
    print("=" * 60)
    print("RuleIQ Performance Benchmark Suite")
    print("=" * 60)
    
    benchmark = PerformanceBenchmark()
    
    try:
        # Setup
        await benchmark.setup()
        
        # Run benchmarks
        await benchmark.benchmark_database_queries(iterations=100)
        await benchmark.benchmark_cache_operations(iterations=500)
        await benchmark.benchmark_connection_pools(concurrent_requests=50)
        await benchmark.benchmark_query_optimization()
        
        # Generate report
        report = benchmark.generate_report()
        
        # Print summary
        print("\n" + "=" * 60)
        print("BENCHMARK SUMMARY")
        print("=" * 60)
        
        summary = report["summary"]
        print(f"\nDatabase Performance: {summary['database_performance']}")
        print(f"Cache Performance: {summary['cache_performance']}")
        print(f"Pool Efficiency: {summary['pool_efficiency']}")
        
        if summary["recommendations"]:
            print("\nRecommendations:")
            for rec in summary["recommendations"]:
                print(f"  - {rec}")
                
    finally:
        # Cleanup
        await benchmark.teardown()
        
    print("\nBenchmark complete!")


if __name__ == "__main__":
    asyncio.run(main())