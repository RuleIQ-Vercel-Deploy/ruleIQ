"""
Celery application configuration for running background tasks such as
evidence collection, processing, and compliance monitoring.
"""

import os

from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the Celery application
celery_app = Celery(
    "compliancegpt",
    broker=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    backend=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    include=[
        "workers.evidence_tasks",
        "workers.compliance_tasks",
        "workers.notification_tasks",
        "workers.reporting_tasks",
    ],
)

# Load configuration from a separate config file or apply directly
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=1800,  # 30 minutes
    worker_prefetch_multiplier=1,
    # Add result backend settings
    result_expires=3600,  # Results expire after 1 hour
    task_always_eager=False,  # Set to True for testing without Redis
    # Worker configuration
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Define the schedule for periodic tasks using Celery Beat
celery_app.conf.beat_schedule = {
    # Runs daily at 2:00 AM UTC to collect evidence from all integrations
    "daily-evidence-collection": {
        "task": "workers.evidence_tasks.collect_all_integrations",
        "schedule": crontab(hour=2, minute=0),
        "options": {"queue": "evidence"},
    },
    # Runs hourly to process any newly collected, unprocessed evidence
    "process-pending-evidence": {
        "task": "workers.evidence_tasks.process_pending_evidence",
        "schedule": crontab(minute=0),
        "options": {"queue": "evidence"},
    },
    # Runs weekly on Monday at 3:00 AM UTC to update compliance scores
    "update-compliance-scores": {
        "task": "workers.compliance_tasks.update_all_compliance_scores",
        "schedule": crontab(hour=3, minute=0, day_of_week=1),
        "options": {"queue": "compliance"},
    },
    # Runs daily at 1:00 AM UTC to check for expired evidence
    "check-evidence-expiry": {
        "task": "workers.evidence_tasks.check_evidence_expiry",
        "schedule": crontab(hour=1, minute=0),
        "options": {"queue": "evidence"},
    },
    # Runs every 6 hours to sync integration statuses
    "sync-integration-status": {
        "task": "workers.evidence_tasks.sync_integration_status",
        "schedule": crontab(minute=0, hour="*/6"),
        "options": {"queue": "evidence"},
    },
    # Runs daily at 4:00 AM UTC to generate compliance reports
    "generate-compliance-reports": {
        "task": "workers.compliance_tasks.generate_daily_reports",
        "schedule": crontab(hour=4, minute=0),
        "options": {"queue": "compliance"},
    },
    # Runs weekly on Sunday at 5:00 AM UTC to clean up old reports
    "cleanup-old-reports": {
        "task": "workers.reporting_tasks.cleanup_old_reports",
        "schedule": crontab(hour=5, minute=0, day_of_week=0),
        "options": {"queue": "reports"},
    },
    # Runs monthly on the 1st at 6:00 AM UTC to send report summaries
    "send-report-summaries": {
        "task": "workers.reporting_tasks.send_report_summary_notifications",
        "schedule": crontab(hour=6, minute=0, day_of_month=1),
        "options": {"queue": "reports"},
    },
}

# Define task routing to separate workloads into different queues
celery_app.conf.task_routes = {
    "workers.evidence_tasks.*": {"queue": "evidence"},
    "workers.compliance_tasks.*": {"queue": "compliance"},
    "workers.notification_tasks.*": {"queue": "notifications"},
    "workers.reporting_tasks.*": {"queue": "reports"},
}

# Configure different queue priorities
celery_app.conf.task_default_queue = "default"
celery_app.conf.task_default_exchange = "default"
celery_app.conf.task_default_routing_key = "default"

# Queue configuration
celery_app.conf.task_queues = {
    "evidence": {
        "exchange": "evidence",
        "routing_key": "evidence",
    },
    "compliance": {
        "exchange": "compliance",
        "routing_key": "compliance",
    },
    "notifications": {
        "exchange": "notifications",
        "routing_key": "notifications",
    },
    "reports": {
        "exchange": "reports",
        "routing_key": "reports",
    },
}

# Error handling configuration
celery_app.conf.task_reject_on_worker_lost = True
celery_app.conf.task_acks_late = True

# Monitoring configuration
celery_app.conf.worker_send_task_events = True
celery_app.conf.task_send_sent_event = True

if __name__ == "__main__":
    celery_app.start()
