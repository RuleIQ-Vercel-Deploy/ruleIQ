"""
Database monitoring service for connection pool and session lifecycle tracking.
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from config.logging_config import get_logger
from database.db_setup import get_engine_info

logger = get_logger(__name__)


class AlertLevel(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class PoolMetrics:
    """Database connection pool metrics."""

    timestamp: datetime
    pool_size: int
    checked_in: int
    checked_out: int
    overflow: int
    total_connections: int
    utilization_percent: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {**asdict(self), "timestamp": self.timestamp.isoformat()}


@dataclass
class SessionMetrics:
    """Async session lifecycle metrics."""

    timestamp: datetime
    active_sessions: int
    total_sessions_created: int
    total_sessions_closed: int
    average_session_duration: float
    long_running_sessions: int

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {**asdict(self), "timestamp": self.timestamp.isoformat()}


@dataclass
class DatabaseAlert:
    """Database monitoring alert."""

    timestamp: datetime
    level: AlertLevel
    metric: str
    value: float
    threshold: float
    message: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {**asdict(self), "timestamp": self.timestamp.isoformat(), "level": self.level.value}


class DatabaseMonitor:
    """Database connection pool and session monitoring service."""

    def __init__(self) -> None:
        self.pool_metrics_history: List[PoolMetrics] = []
        self.session_metrics_history: List[SessionMetrics] = []
        self.alerts: List[DatabaseAlert] = []
        self.session_tracker = SessionTracker()

        # Configurable thresholds
        self.thresholds = {
            "pool_utilization_warning": 70.0,  # %
            "pool_utilization_critical": 85.0,  # %
            "overflow_warning": 5,  # connections
            "overflow_critical": 15,  # connections
            "long_running_session_warning": 300.0,  # seconds
            "session_leak_warning": 50,  # active sessions
        }

        # Metrics retention (keep last 24 hours)
        self.metrics_retention_hours = 24

    def collect_pool_metrics(self) -> Optional[PoolMetrics]:
        """Collect current connection pool metrics."""
        try:
            engine_info = get_engine_info()

            # Focus on async pool as it's primary for the application
            if not engine_info.get("async_engine_initialized"):
                logger.warning("Async engine not initialized, cannot collect pool metrics")
                return None

            pool_size = engine_info.get("async_pool_size", 0)
            checked_in = engine_info.get("async_pool_checked_in", 0)
            checked_out = engine_info.get("async_pool_checked_out", 0)
            overflow = engine_info.get("async_pool_overflow", 0)

            total_connections = checked_in + checked_out
            utilization_percent = (total_connections / max(pool_size, 1)) * 100

            metrics = PoolMetrics(
                timestamp=datetime.utcnow(),
                pool_size=pool_size,
                checked_in=checked_in,
                checked_out=checked_out,
                overflow=overflow,
                total_connections=total_connections,
                utilization_percent=utilization_percent,
            )

            # Store metrics
            self.pool_metrics_history.append(metrics)
            self._cleanup_old_metrics()

            # Check for alerts
            self._check_pool_alerts(metrics)

            return metrics

        except Exception as e:
            logger.error(f"Error collecting pool metrics: {e}")
            return None

    def collect_session_metrics(self) -> SessionMetrics:
        """Collect current session lifecycle metrics."""
        session_stats = self.session_tracker.get_stats()

        metrics = SessionMetrics(
            timestamp=datetime.utcnow(),
            active_sessions=session_stats["active_sessions"],
            total_sessions_created=session_stats["total_created"],
            total_sessions_closed=session_stats["total_closed"],
            average_session_duration=session_stats["average_duration"],
            long_running_sessions=session_stats["long_running_count"],
        )

        # Store metrics
        self.session_metrics_history.append(metrics)
        self._cleanup_old_metrics()

        # Check for alerts
        self._check_session_alerts(metrics)

        return metrics

    def _check_pool_alerts(self, metrics: PoolMetrics) -> None:
        """Check pool metrics against thresholds and create alerts"""
        if not metrics or not self.thresholds:
            return

        # Pool utilization alerts
        if metrics.utilization_percent >= self.thresholds["pool_utilization_critical"]:
            self._create_alert(
                AlertLevel.CRITICAL,
                "pool_utilization",
                metrics.utilization_percent,
                self.thresholds["pool_utilization_critical"],
                (
                    f"Critical pool utilization: {metrics.utilization_percent:.1f}% "
                    f"({metrics.total_connections}/{metrics.pool_size} connections)"
                ),
            )
        elif metrics.utilization_percent >= self.thresholds["pool_utilization_warning"]:
            self._create_alert(
                AlertLevel.WARNING,
                "pool_utilization",
                metrics.utilization_percent,
                self.thresholds["pool_utilization_warning"],
                (
                    f"High pool utilization: {metrics.utilization_percent:.1f}% "
                    f"({metrics.total_connections}/{metrics.pool_size} connections)"
                ),
            )

        # Overflow alerts
        if metrics.overflow >= self.thresholds["overflow_critical"]:
            self._create_alert(
                AlertLevel.CRITICAL,
                "pool_overflow",
                metrics.overflow,
                self.thresholds["overflow_critical"],
                f"Critical pool overflow: {metrics.overflow} overflow connections",
            )
        elif metrics.overflow >= self.thresholds["overflow_warning"]:
            self._create_alert(
                AlertLevel.WARNING,
                "pool_overflow",
                metrics.overflow,
                self.thresholds["overflow_warning"],
                f"Pool overflow detected: {metrics.overflow} overflow connections",
            )

    def _check_session_alerts(self, metrics: SessionMetrics) -> None:
        """Check session metrics against thresholds and create alerts"""
        if not metrics or not self.thresholds:
            return

        # Long-running session alerts
        if metrics.long_running_sessions >= self.thresholds["long_running_session_critical"]:
            self._create_alert(
                AlertLevel.CRITICAL,
                "long_running_sessions",
                metrics.long_running_sessions,
                self.thresholds["long_running_session_critical"],
                (
                    f"Long-running sessions detected: {metrics.long_running_sessions} sessions "
                    f"running longer than {self.thresholds['long_running_session_warning']}s"
                ),
            )
        elif metrics.long_running_sessions >= self.thresholds["long_running_session_warning"]:
            self._create_alert(
                AlertLevel.WARNING,
                "long_running_sessions",
                metrics.long_running_sessions,
                self.thresholds["long_running_session_warning"],
                f"Potential session leak: {metrics.active_sessions} active sessions",
            )

    def _create_alert(
        self, level: AlertLevel, metric: str, value: float, threshold: float, message: str
    ) -> None:
        """Create and store an alert."""
        alert = DatabaseAlert(
            timestamp=datetime.utcnow(),
            level=level,
            metric=metric,
            value=value,
            threshold=threshold,
            message=message,
        )

        self.alerts.append(alert)

        # Log the alert
        log_method = {
            AlertLevel.INFO: logger.info,
            AlertLevel.WARNING: logger.warning,
            AlertLevel.CRITICAL: logger.error,
        }[level]

        log_method(f"Database Alert [{level.value.upper()}]: {message}")

        # Keep only recent alerts (last 24 hours)
        cutoff = datetime.utcnow() - timedelta(hours=24)
        self.alerts = [a for a in self.alerts if a.timestamp > cutoff]

    def _cleanup_old_metrics(self) -> None:
        """Remove old metrics to prevent memory growth."""
        cutoff = datetime.utcnow() - timedelta(hours=self.metrics_retention_hours)

        self.pool_metrics_history = [m for m in self.pool_metrics_history if m.timestamp > cutoff]
        self.session_metrics_history = [
            m for m in self.session_metrics_history if m.timestamp > cutoff
        ]

    def get_current_status(self) -> Dict[str, Any]:
        """Get current database monitoring status."""
        pool_metrics = self.collect_pool_metrics()
        session_metrics = self.collect_session_metrics()

        # Get recent alerts (last hour)
        recent_alerts = [
            a for a in self.alerts if a.timestamp > datetime.utcnow() - timedelta(hours=1)
        ]

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "pool_metrics": pool_metrics.to_dict() if pool_metrics else None,
            "session_metrics": session_metrics.to_dict(),
            "recent_alerts": [a.to_dict() for a in recent_alerts],
            "alert_counts": {
                "critical": len([a for a in recent_alerts if a.level == AlertLevel.CRITICAL]),
                "warning": len([a for a in recent_alerts if a.level == AlertLevel.WARNING]),
                "info": len([a for a in recent_alerts if a.level == AlertLevel.INFO]),
            },
            "thresholds": self.thresholds,
        }


class SessionTracker:
    """Track async session lifecycle for monitoring."""

    def __init__(self) -> None:
        self.active_sessions: Dict[str, datetime] = {}
        self.total_created = 0
        self.total_closed = 0
        self.session_durations: List[float] = []

    def session_created(self, session_id: str) -> None:
        """Record session creation."""
        self.active_sessions[session_id] = datetime.utcnow()
        self.total_created += 1

    def session_closed(self, session_id: str) -> None:
        """Record session closure."""
        if session_id in self.active_sessions:
            start_time = self.active_sessions.pop(session_id)
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.session_durations.append(duration)
            self.total_closed += 1

            # Keep only recent durations for average calculation
            if len(self.session_durations) > 1000:
                self.session_durations = self.session_durations[-500:]

    def get_stats(self) -> Dict[str, Any]:
        """Get current session statistics."""
        now = datetime.utcnow()
        long_running_threshold = 300  # 5 minutes

        long_running_count = sum(
            1
            for start_time in self.active_sessions.values()
            if (now - start_time).total_seconds() > long_running_threshold
        )

        avg_duration = (
            sum(self.session_durations) / len(self.session_durations)
            if self.session_durations
            else 0.0
        )

        return {
            "active_sessions": len(self.active_sessions),
            "total_created": self.total_created,
            "total_closed": self.total_closed,
            "average_duration": avg_duration,
            "long_running_count": long_running_count,
        }


# Global monitor instance
database_monitor = DatabaseMonitor()
