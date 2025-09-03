"""
Alerting System for RuleIQ

Provides intelligent alerting with multiple channels:
- Sentry alerts
- Email notifications
- Webhook notifications
- Slack integration (optional)
- In-app alerts dashboard
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from collections import defaultdict

import aiohttp
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import settings
from database.db_setup import get_async_db
from monitoring.sentry_config import capture_message

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertCategory(str, Enum):
    """Alert categories."""
    SECURITY = "security"
    PERFORMANCE = "performance"
    AVAILABILITY = "availability"
    ERROR = "error"
    CAPACITY = "capacity"
    BUSINESS = "business"
    COMPLIANCE = "compliance"


class AlertChannel(str, Enum):
    """Alert notification channels."""
    SENTRY = "sentry"
    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"
    IN_APP = "in_app"
    LOG = "log"


@dataclass
class Alert:
    """Alert definition."""
    id: str
    title: str
    message: str
    severity: AlertSeverity
    category: AlertCategory
    component: str
    metadata: Dict[str, Any]
    timestamp: datetime
    resolved: bool = False
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    notification_sent: bool = False
    channels_notified: List[AlertChannel] = None
    
    def __post_init__(self):
        if self.channels_notified is None:
            self.channels_notified = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        result["timestamp"] = self.timestamp.isoformat()
        result["resolved_at"] = self.resolved_at.isoformat() if self.resolved_at else None
        result["channels_notified"] = [c.value for c in self.channels_notified]
        return result


@dataclass
class AlertRule:
    """Alert rule definition."""
    name: str
    condition: str  # Expression to evaluate
    threshold: float
    duration: int  # Seconds the condition must be true
    severity: AlertSeverity
    category: AlertCategory
    channels: List[AlertChannel]
    cooldown: int = 300  # Seconds before re-alerting
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        result["channels"] = [c.value for c in self.channels]
        return result


class AlertManager:
    """Centralized alert management system."""
    
    def __init__(self):
        """Initialize alert manager."""
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.alert_rules: List[AlertRule] = []
        self.last_alert_times: Dict[str, datetime] = {}
        self.condition_start_times: Dict[str, datetime] = {}
        self.max_history_size = 1000
        
        # Initialize default alert rules
        self._init_default_rules()
    
    def _init_default_rules(self):
        """Initialize default alert rules."""
        self.alert_rules = [
            # Database alerts
            AlertRule(
                name="database_connection_pool_high",
                condition="database.pool_utilization > threshold",
                threshold=85.0,
                duration=60,
                severity=AlertSeverity.HIGH,
                category=AlertCategory.CAPACITY,
                channels=[AlertChannel.SENTRY, AlertChannel.IN_APP]
            ),
            AlertRule(
                name="database_connection_pool_critical",
                condition="database.pool_utilization > threshold",
                threshold=95.0,
                duration=30,
                severity=AlertSeverity.CRITICAL,
                category=AlertCategory.CAPACITY,
                channels=[AlertChannel.SENTRY, AlertChannel.EMAIL, AlertChannel.IN_APP]
            ),
            AlertRule(
                name="database_slow_queries",
                condition="database.avg_query_time_ms > threshold",
                threshold=1000.0,
                duration=120,
                severity=AlertSeverity.MEDIUM,
                category=AlertCategory.PERFORMANCE,
                channels=[AlertChannel.IN_APP, AlertChannel.LOG]
            ),
            
            # API performance alerts
            AlertRule(
                name="api_high_response_time",
                condition="api.p95_response_time_ms > threshold",
                threshold=2000.0,
                duration=60,
                severity=AlertSeverity.MEDIUM,
                category=AlertCategory.PERFORMANCE,
                channels=[AlertChannel.IN_APP, AlertChannel.LOG]
            ),
            AlertRule(
                name="api_critical_response_time",
                condition="api.p99_response_time_ms > threshold",
                threshold=5000.0,
                duration=30,
                severity=AlertSeverity.HIGH,
                category=AlertCategory.PERFORMANCE,
                channels=[AlertChannel.SENTRY, AlertChannel.IN_APP]
            ),
            
            # Error rate alerts
            AlertRule(
                name="high_error_rate",
                condition="api.error_rate > threshold",
                threshold=5.0,
                duration=60,
                severity=AlertSeverity.HIGH,
                category=AlertCategory.ERROR,
                channels=[AlertChannel.SENTRY, AlertChannel.IN_APP]
            ),
            AlertRule(
                name="critical_error_rate",
                condition="api.error_rate > threshold",
                threshold=10.0,
                duration=30,
                severity=AlertSeverity.CRITICAL,
                category=AlertCategory.ERROR,
                channels=[AlertChannel.SENTRY, AlertChannel.EMAIL, AlertChannel.IN_APP]
            ),
            
            # Resource alerts
            AlertRule(
                name="high_memory_usage",
                condition="system.memory_percent > threshold",
                threshold=settings.memory_warning_threshold,
                duration=120,
                severity=AlertSeverity.MEDIUM,
                category=AlertCategory.CAPACITY,
                channels=[AlertChannel.IN_APP, AlertChannel.LOG]
            ),
            AlertRule(
                name="critical_memory_usage",
                condition="system.memory_percent > threshold",
                threshold=settings.memory_critical_threshold,
                duration=60,
                severity=AlertSeverity.CRITICAL,
                category=AlertCategory.CAPACITY,
                channels=[AlertChannel.SENTRY, AlertChannel.EMAIL, AlertChannel.IN_APP]
            ),
            AlertRule(
                name="high_disk_usage",
                condition="system.disk_percent > threshold",
                threshold=settings.disk_warning_threshold,
                duration=300,
                severity=AlertSeverity.MEDIUM,
                category=AlertCategory.CAPACITY,
                channels=[AlertChannel.IN_APP, AlertChannel.LOG]
            ),
            AlertRule(
                name="critical_disk_usage",
                condition="system.disk_percent > threshold",
                threshold=settings.disk_critical_threshold,
                duration=120,
                severity=AlertSeverity.CRITICAL,
                category=AlertCategory.CAPACITY,
                channels=[AlertChannel.SENTRY, AlertChannel.EMAIL, AlertChannel.IN_APP]
            ),
            
            # Security alerts
            AlertRule(
                name="multiple_failed_logins",
                condition="security.failed_login_rate > threshold",
                threshold=10.0,
                duration=60,
                severity=AlertSeverity.HIGH,
                category=AlertCategory.SECURITY,
                channels=[AlertChannel.SENTRY, AlertChannel.EMAIL, AlertChannel.IN_APP]
            ),
            AlertRule(
                name="suspicious_activity",
                condition="security.suspicious_requests > threshold",
                threshold=5.0,
                duration=30,
                severity=AlertSeverity.CRITICAL,
                category=AlertCategory.SECURITY,
                channels=[AlertChannel.SENTRY, AlertChannel.EMAIL, AlertChannel.IN_APP]
            ),
            
            # Business metrics alerts
            AlertRule(
                name="low_compliance_score",
                condition="business.avg_compliance_score < threshold",
                threshold=50.0,
                duration=3600,
                severity=AlertSeverity.INFO,
                category=AlertCategory.BUSINESS,
                channels=[AlertChannel.IN_APP]
            ),
            AlertRule(
                name="high_ai_costs",
                condition="ai.daily_cost > threshold",
                threshold=100.0,
                duration=300,
                severity=AlertSeverity.MEDIUM,
                category=AlertCategory.BUSINESS,
                channels=[AlertChannel.EMAIL, AlertChannel.IN_APP]
            ),
            AlertRule(
                name="ai_budget_exceeded",
                condition="ai.monthly_cost > threshold",
                threshold=settings.ai_monthly_budget_limit,
                duration=60,
                severity=AlertSeverity.CRITICAL,
                category=AlertCategory.BUSINESS,
                channels=[AlertChannel.EMAIL, AlertChannel.SENTRY, AlertChannel.IN_APP]
            ),
        ]
    
    def create_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity,
        category: AlertCategory,
        component: str,
        metadata: Optional[Dict[str, Any]] = None,
        channels: Optional[List[AlertChannel]] = None
    ) -> Alert:
        """Create a new alert."""
        alert_id = f"{component}_{category}_{datetime.now(timezone.utc).timestamp()}"
        
        alert = Alert(
            id=alert_id,
            title=title,
            message=message,
            severity=severity,
            category=category,
            component=component,
            metadata=metadata or {},
            timestamp=datetime.now(timezone.utc),
            channels_notified=[]
        )
        
        # Store alert
        self.active_alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Trim history if needed
        if len(self.alert_history) > self.max_history_size:
            self.alert_history = self.alert_history[-self.max_history_size:]
        
        # Send notifications
        if channels:
            asyncio.create_task(self._send_notifications(alert, channels))
        
        return alert
    
    async def _send_notifications(self, alert: Alert, channels: List[AlertChannel]) -> None:
        """Send alert notifications to specified channels."""
        for channel in channels:
            try:
                if channel == AlertChannel.SENTRY:
                    await self._send_to_sentry(alert)
                elif channel == AlertChannel.EMAIL:
                    await self._send_email_notification(alert)
                elif channel == AlertChannel.WEBHOOK:
                    await self._send_webhook_notification(alert)
                elif channel == AlertChannel.SLACK:
                    await self._send_slack_notification(alert)
                elif channel == AlertChannel.IN_APP:
                    await self._store_in_app_alert(alert)
                elif channel == AlertChannel.LOG:
                    self._log_alert(alert)
                
                alert.channels_notified.append(channel)
                
            except Exception as e:
                logger.error(f"Failed to send alert to {channel}: {e}")
        
        alert.notification_sent = True
    
    async def _send_to_sentry(self, alert: Alert) -> None:
        """Send alert to Sentry."""
        level = "error" if alert.severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH] else "warning"
        
        capture_message(
            f"[{alert.severity.upper()}] {alert.title}",
            level=level,
            context={
                "alert": alert.to_dict(),
                "category": alert.category,
                "component": alert.component
            }
        )
    
    async def _send_email_notification(self, alert: Alert) -> None:
        """Send email notification for alert."""
        # TODO: Implement email sending
        # This would integrate with an email service like SendGrid or AWS SES
        logger.info(f"Email alert would be sent: {alert.title}")
    
    async def _send_webhook_notification(self, alert: Alert) -> None:
        """Send webhook notification for alert."""
        webhook_url = os.getenv("ALERT_WEBHOOK_URL")
        if not webhook_url:
            return
        
        async with aiohttp.ClientSession() as session:
            payload = {
                "alert": alert.to_dict(),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "environment": settings.environment
            }
            
            try:
                async with session.post(
                    webhook_url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status >= 400:
                        logger.error(f"Webhook notification failed with status {response.status}")
            except Exception as e:
                logger.error(f"Failed to send webhook notification: {e}")
    
    async def _send_slack_notification(self, alert: Alert) -> None:
        """Send Slack notification for alert."""
        slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        if not slack_webhook:
            return
        
        # Format message for Slack
        color = {
            AlertSeverity.CRITICAL: "danger",
            AlertSeverity.HIGH: "warning",
            AlertSeverity.MEDIUM: "warning",
            AlertSeverity.LOW: "#36a64f",
            AlertSeverity.INFO: "#2eb886"
        }.get(alert.severity, "#808080")
        
        slack_message = {
            "attachments": [{
                "color": color,
                "title": f"[{alert.severity.upper()}] {alert.title}",
                "text": alert.message,
                "fields": [
                    {"title": "Component", "value": alert.component, "short": True},
                    {"title": "Category", "value": alert.category, "short": True},
                    {"title": "Environment", "value": settings.environment, "short": True},
                    {"title": "Time", "value": alert.timestamp.isoformat(), "short": True}
                ],
                "footer": "RuleIQ Monitoring",
                "ts": int(alert.timestamp.timestamp())
            }]
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    slack_webhook,
                    json=slack_message,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status >= 400:
                        logger.error(f"Slack notification failed with status {response.status}")
            except Exception as e:
                logger.error(f"Failed to send Slack notification: {e}")
    
    async def _store_in_app_alert(self, alert: Alert) -> None:
        """Store alert for in-app display."""
        # This is handled by keeping the alert in active_alerts
        # The API endpoints will retrieve from there
        pass
    
    def _log_alert(self, alert: Alert) -> None:
        """Log alert to application logs."""
        log_level = {
            AlertSeverity.CRITICAL: logging.CRITICAL,
            AlertSeverity.HIGH: logging.ERROR,
            AlertSeverity.MEDIUM: logging.WARNING,
            AlertSeverity.LOW: logging.INFO,
            AlertSeverity.INFO: logging.INFO
        }.get(alert.severity, logging.INFO)
        
        logger.log(
            log_level,
            f"ALERT [{alert.severity}] {alert.title}: {alert.message}",
            extra={
                "alert_id": alert.id,
                "category": alert.category,
                "component": alert.component,
                "metadata": alert.metadata
            }
        )
    
    def evaluate_rules(self, metrics: Dict[str, Any]) -> List[Alert]:
        """Evaluate alert rules against current metrics."""
        triggered_alerts = []
        current_time = datetime.now(timezone.utc)
        
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
            
            # Check cooldown
            last_alert = self.last_alert_times.get(rule.name)
            if last_alert and (current_time - last_alert).total_seconds() < rule.cooldown:
                continue
            
            # Evaluate condition
            try:
                # Simple threshold evaluation for now
                # In production, you'd use a proper expression evaluator
                metric_value = self._get_metric_value(metrics, rule.condition)
                
                if metric_value is not None and metric_value > rule.threshold:
                    # Check duration requirement
                    condition_start = self.condition_start_times.get(rule.name)
                    
                    if condition_start is None:
                        # First time condition is true
                        self.condition_start_times[rule.name] = current_time
                    elif (current_time - condition_start).total_seconds() >= rule.duration:
                        # Condition has been true for required duration
                        alert = self.create_alert(
                            title=f"{rule.name.replace('_', ' ').title()}",
                            message=f"Metric {rule.condition} is {metric_value:.2f}, threshold is {rule.threshold:.2f}",
                            severity=rule.severity,
                            category=rule.category,
                            component=rule.condition.split('.')[0],
                            metadata={
                                "rule": rule.name,
                                "metric_value": metric_value,
                                "threshold": rule.threshold,
                                "duration": rule.duration
                            },
                            channels=rule.channels
                        )
                        
                        triggered_alerts.append(alert)
                        self.last_alert_times[rule.name] = current_time
                        self.condition_start_times.pop(rule.name, None)
                else:
                    # Condition is false, reset timer
                    self.condition_start_times.pop(rule.name, None)
                    
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.name}: {e}")
        
        return triggered_alerts
    
    def _get_metric_value(self, metrics: Dict[str, Any], condition: str) -> Optional[float]:
        """Extract metric value from condition expression."""
        # Simple implementation - extract metric path
        # Format: "category.metric > threshold"
        parts = condition.split(" > ")[0].split(".")
        
        value = metrics
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
        
        return float(value) if value is not None else None
    
    def resolve_alert(
        self,
        alert_id: str,
        resolved_by: str,
        resolution_notes: Optional[str] = None
    ) -> bool:
        """Resolve an active alert."""
        alert = self.active_alerts.get(alert_id)
        if not alert:
            return False
        
        alert.resolved = True
        alert.resolved_at = datetime.now(timezone.utc)
        alert.resolved_by = resolved_by
        alert.resolution_notes = resolution_notes
        
        # Remove from active alerts
        self.active_alerts.pop(alert_id, None)
        
        return True
    
    def get_active_alerts(
        self,
        severity: Optional[AlertSeverity] = None,
        category: Optional[AlertCategory] = None
    ) -> List[Alert]:
        """Get active alerts with optional filtering."""
        alerts = list(self.active_alerts.values())
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        if category:
            alerts = [a for a in alerts if a.category == category]
        
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of current alert status."""
        active_alerts = list(self.active_alerts.values())
        
        severity_counts = defaultdict(int)
        category_counts = defaultdict(int)
        
        for alert in active_alerts:
            severity_counts[alert.severity] = severity_counts[alert.severity] + 1
            category_counts[alert.category] = category_counts[alert.category] + 1
        
        return {
            "total_active": len(active_alerts),
            "by_severity": dict(severity_counts),
            "by_category": dict(category_counts),
            "most_recent": active_alerts[-1].to_dict() if active_alerts else None,
            "oldest_unresolved": active_alerts[0].to_dict() if active_alerts else None
        }


# Global alert manager instance
_alert_manager: Optional[AlertManager] = None


def get_alert_manager() -> AlertManager:
    """Get or create the global alert manager instance."""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager()
    return _alert_manager


async def run_alert_evaluation_loop(interval: int = 30) -> None:
    """Run alert evaluation in a background loop."""
    from monitoring.metrics import get_metrics_collector
    
    alert_manager = get_alert_manager()
    metrics_collector = get_metrics_collector()
    
    while True:
        try:
            # Get current metrics
            metrics_summary = metrics_collector.get_metrics_summary()
            
            # Evaluate alert rules
            triggered_alerts = alert_manager.evaluate_rules(metrics_summary)
            
            if triggered_alerts:
                logger.info(f"Triggered {len(triggered_alerts)} new alerts")
            
        except Exception as e:
            logger.error(f"Error in alert evaluation loop: {e}")
        
        await asyncio.sleep(interval)