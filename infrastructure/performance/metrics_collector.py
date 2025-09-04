"""
Performance metrics collection and monitoring.

Tracks and reports performance metrics for optimization.
"""

import time
import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
from functools import wraps
import statistics

logger = logging.getLogger(__name__)


@dataclass
class MetricPoint:
    """Single metric data point."""
    name: str
    value: float
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    

@dataclass
class PerformanceMetric:
    """Performance metric with statistics."""
    name: str
    count: int = 0
    total: float = 0.0
    min_value: float = float('inf')
    max_value: float = float('-inf')
    values: List[float] = field(default_factory=list)
    
    @property
    def mean(self) -> float: return self.total / self.count if self.count > 0 else 0.0
        
    @property
    def median(self) -> float: return statistics.median(self.values) if self.values else 0.0
        
    @property
    def p95(self) -> float: if not self.values:
            return 0.0
        sorted_values = sorted(self.values)
        index = int(len(sorted_values) * 0.95)
        return sorted_values[min(index, len(sorted_values) - 1)]
        
    @property
    def p99(self) -> float: if not self.values:
            return 0.0
        sorted_values = sorted(self.values)
        index = int(len(sorted_values) * 0.99)
        return sorted_values[min(index, len(sorted_values) - 1)]
        
    def add_value(self, value: float) -> None: self.count += 1
        self.total += value
        self.min_value = min(self.min_value, value)
        self.max_value = max(self.max_value, value)
        self.values.append(value)
        
        # Keep only last 1000 values to prevent memory bloat
        if len(self.values) > 1000:
            self.values = self.values[-1000:]


class PerformanceMetrics:
    """
    Collects and manages performance metrics.
    """
    
    def __init__(self):
        self.metrics: Dict[str, PerformanceMetric] = {}
        self.timers: Dict[str, float] = {}
        self.counters: Dict[str, int] = {}
        self._enabled = True
        
    def enable(self) -> None: self._enabled = True
        
    def disable(self) -> None: self._enabled = False
        
    def record_time(self, name: str, duration: float, tags: Optional[Dict[str, str]] = None) -> None: if not self._enabled:
            return
            
        metric_name = f"{name}{'.' + '.'.join(f'{k}={v}' for k, v in tags.items()) if tags else ''}"
        
        if metric_name not in self.metrics:
            self.metrics[metric_name] = PerformanceMetric(name=metric_name)
            
        self.metrics[metric_name].add_value(duration)
        
        # Log slow operations
        if duration > 1.0:
            logger.warning(f"Slow operation detected: {name} took {duration:.2f}s")
            
    def increment_counter(self, name: str, value: int = 1) -> None: if not self._enabled:
            return
            
        self.counters[name] = self.counters.get(name, 0) + value
        
    def start_timer(self, name: str) -> None: if not self._enabled:
            return
            
        self.timers[name] = time.perf_counter()
        
    def stop_timer(self, name: str) -> float: if not self._enabled or name not in self.timers:
            return 0.0
            
        duration = time.perf_counter() - self.timers[name]
        del self.timers[name]
        self.record_time(name, duration)
        return duration
        
    @asynccontextmanager
    async def measure(self, name: str, tags: Optional[Dict[str, str]] = None): start = time.perf_counter()
        try:
            yield
        finally:
            if self._enabled:
                duration = time.perf_counter() - start
                self.record_time(name, duration, tags)
                
    def get_metrics_summary(self) -> Dict[str, Any]: summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'timings': {},
            'counters': self.counters.copy()
        }
        
        for name, metric in self.metrics.items():
            if metric.count > 0:
                summary['timings'][name] = {
                    'count': metric.count,
                    'mean': round(metric.mean, 3),
                    'median': round(metric.median, 3),
                    'min': round(metric.min_value, 3),
                    'max': round(metric.max_value, 3),
                    'p95': round(metric.p95, 3),
                    'p99': round(metric.p99, 3)
                }
                
        return summary
        
    def get_slow_operations(self, threshold: float = 1.0) -> List[Dict[str, Any]]: slow_ops = []
        
        for name, metric in self.metrics.items():
            if metric.max_value > threshold:
                slow_ops.append({
                    'name': name,
                    'max_time': metric.max_value,
                    'mean_time': metric.mean,
                    'count': metric.count,
                    'p95': metric.p95
                })
                
        return sorted(slow_ops, key=lambda x: x['max_time'], reverse=True)
        
    def reset(self) -> None: self.metrics.clear()
        self.timers.clear()
        self.counters.clear()


def measure_performance(name: str, tags: Optional[Dict[str, str]] = None): Decorator for measuring function performance.
    """
    def decorator(func):
        """Decorator"""
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                metrics = get_metrics()
                """Async Wrapper"""
                async with metrics.measure(name or func.__name__, tags):
                    return await func(*args, **kwargs)
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                """Sync Wrapper"""
                metrics = get_metrics()
                start = time.perf_counter()
                try:
                    return func(*args, **kwargs)
                finally:
                    duration = time.perf_counter() - start
                    metrics.record_time(name or func.__name__, duration, tags)
            return sync_wrapper
    return decorator


class QueryPerformanceTracker:
    """
    Tracks database query performance.
    """
    
    def __init__(self, metrics: PerformanceMetrics):
        self.metrics = metrics
        self.query_patterns: Dict[str, List[float]] = {}
        
    def track_query(self, query_type: str, duration: float, row_count: int = 0) -> None: # Record base metric
        self.metrics.record_time(
            f"db.query.{query_type}",
            duration,
            {'rows': str(row_count)}
        )
        
        # Track pattern
        if query_type not in self.query_patterns:
            self.query_patterns[query_type] = []
        self.query_patterns[query_type].append(duration)
        
        # Keep only recent queries
        if len(self.query_patterns[query_type]) > 100:
            self.query_patterns[query_type] = self.query_patterns[query_type][-100:]
            
        # Check for performance degradation
        if len(self.query_patterns[query_type]) >= 10:
            recent_avg = statistics.mean(self.query_patterns[query_type][-10:])
            overall_avg = statistics.mean(self.query_patterns[query_type])
            
            if recent_avg > overall_avg * 1.5:
                logger.warning(
                    f"Query performance degradation detected for {query_type}: "
                    f"recent avg {recent_avg:.3f}s vs overall {overall_avg:.3f}s"
                )
                
    def get_query_stats(self) -> Dict[str, Any]: stats = {}
        
        for query_type, durations in self.query_patterns.items():
            if durations:
                stats[query_type] = {
                    'count': len(durations),
                    'mean': statistics.mean(durations),
                    'median': statistics.median(durations),
                    'min': min(durations),
                    'max': max(durations),
                    'stdev': statistics.stdev(durations) if len(durations) > 1 else 0
                }
                
        return stats


class CachePerformanceTracker:
    """
    Tracks cache performance metrics.
    """
    
    def __init__(self, metrics: PerformanceMetrics):
        self.metrics = metrics
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.deletes = 0
        
    def record_hit(self) -> None: self.hits += 1
        self.metrics.increment_counter('cache.hit')
        
    def record_miss(self) -> None: self.misses += 1
        self.metrics.increment_counter('cache.miss')
        
    def record_set(self, duration: float) -> None: self.sets += 1
        self.metrics.record_time('cache.set', duration)
        
    def record_delete(self, duration: float) -> None: self.deletes += 1
        self.metrics.record_time('cache.delete', duration)
        
    @property
    def hit_rate(self) -> float: total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0
        
    def get_stats(self) -> Dict[str, Any]: return {
            'hits': self.hits,
            'misses': self.misses,
            'sets': self.sets,
            'deletes': self.deletes,
            'hit_rate': f"{self.hit_rate:.1%}",
            'total_requests': self.hits + self.misses
        }


# Singleton instance
_metrics_instance: Optional[PerformanceMetrics] = None


def get_metrics() -> PerformanceMetrics: global _metrics_instance
    if _metrics_instance is None:
        _metrics_instance = PerformanceMetrics()
    return _metrics_instance