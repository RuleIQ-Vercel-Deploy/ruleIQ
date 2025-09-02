"""
from __future__ import annotations

Celery background tasks for sending notifications and alerts, with async support.
"""
import asyncio
import smtplib
from typing import Any, Dict
from uuid import UUID
from celery.utils.log import get_task_logger
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from celery_app import celery_app
from core.exceptions import BusinessLogicException, DatabaseException, IntegrationException, NotFoundException
from database.db_setup import get_async_db
from database.user import User
logger = get_task_logger(__name__)

def _send_email_notification(recipient_email: str, subject: str, body: str) -> Dict[str, Any]:
    """Sends an email notification. This remains a synchronous function."""
    try:
        logger.info(f"Mock sending email to {recipient_email} with subject: '{subject}'")
        return {'method': 'email', 'status': 'sent'}
    except smtplib.SMTPException as e:
        logger.error(f'SMTP error while sending email to {recipient_email}: {e}', exc_info=True)
        raise IntegrationException(f'Failed to send email due to SMTP error: {e}') from e
    except Exception as e:
        logger.error(f'Failed to send email to {recipient_email}: {e}', exc_info=True)
        raise IntegrationException(f'An unexpected error occurred while sending email to {recipient_email}.') from e

def _prepare_alert_content(alert_type: str, alert_data: Dict[str, Any], user: User) -> tuple[str, str]:
    """Prepares the subject and body for an alert email."""
    subject = f"Compliance Alert: {alert_type.replace('_', ' ').title()}"
    body = f"Dear {user.full_name or 'User'},\n\nA new compliance alert requires your attention: "
    body += f"{alert_data.get('details', 'No details provided')}."
    return (subject, body)

def _format_weekly_summary(summary_data: Dict[str, Any], user: User) -> tuple[str, str]:
    """Formats the weekly summary data into an email-friendly format."""
    subject = 'Your Weekly Compliance Summary'
    body = f"Dear {user.full_name or 'User'},\n\nHere is your compliance summary for the past week:\n"
    body += f"- New Evidence Items: {summary_data.get('new_evidence_count', 0)}\n"
    body += f"- Average Quality Score: {summary_data.get('avg_quality_score', 'N/A')}\n"
    return (subject, body)

async def _send_compliance_alert_async(user_id_str: str, alert_type: str, alert_data: Dict[str, Any]) -> Dict[str, Any]:
    """Async helper to send a single compliance alert."""
    user_id = UUID(user_id_str)
    async for db in get_async_db():
        try:
            user_res = await db.execute(select(User).where(User.id == user_id))
            user = user_res.scalars().first()
            if not user:
                raise NotFoundException(f'User with ID {user_id} not found.')
            subject, body = _prepare_alert_content(alert_type, alert_data, user)
            return _send_email_notification(user.email, subject, body)
        except SQLAlchemyError as e:
            logger.error(f'Database error while fetching user {user_id} for alert: {e}', exc_info=True)
            raise DatabaseException(f'Failed to fetch user {user_id} for alert.') from e

async def _send_weekly_summary_async(user_id_str: str) -> Dict[str, Any]:
    """Async helper to generate and send a weekly summary."""
    user_id = UUID(user_id_str)
    async for db in get_async_db():
        try:
            user_res = await db.execute(select(User).where(User.id == user_id))
            user = user_res.scalars().first()
            if not user:
                raise NotFoundException(f'User with ID {user_id} not found.')
            summary_data = {'new_evidence_count': 5, 'avg_quality_score': 85.5}
            subject, body = _format_weekly_summary(summary_data, user)
            return _send_email_notification(user.email, subject, body)
        except SQLAlchemyError as e:
            logger.error(f'Database error while fetching user {user_id} for summary: {e}', exc_info=True)
            raise DatabaseException(f'Failed to fetch user {user_id} for summary.') from e

async def _broadcast_notification_async(subject: str, message: str) -> int:
    """Async helper to broadcast a notification to all active users."""
    async for db in get_async_db():
        try:
            users_res = await db.execute(select(User).where(User.is_active))
            users = users_res.scalars().all()
            for user in users:
                _send_email_notification(user.email, subject, message)
            return len(users)
        except SQLAlchemyError as e:
            logger.error(f'Database error during broadcast: {e}', exc_info=True)
            raise DatabaseException('Failed to fetch users for broadcast.') from e

@celery_app.task(bind=True, autoretry_for=(DatabaseException, Exception), retry_kwargs={'max_retries': 5, 'countdown': 30}, retry_backoff=True, retry_backoff_max=300, retry_jitter=True, rate_limit='20/m')
def send_compliance_alert(self, user_id: str, alert_type: str, alert_data: Dict[str, Any]) -> Any:
    """Sends a compliance alert to a specific user."""
    logger.info(f"Sending compliance alert '{alert_type}' to user {user_id}")
    try:
        return asyncio.run(_send_compliance_alert_async(user_id, alert_type, alert_data))
    except (NotFoundException, BusinessLogicException) as e:
        logger.warning(f'Business logic error for compliance alert to user {user_id}, not retrying: {e}')
    except Exception as e:
        logger.critical(f'Unexpected, non-retriable error for compliance alert to user {user_id}: {e}', exc_info=True)
        raise

@celery_app.task(bind=True, autoretry_for=(DatabaseException, Exception), retry_kwargs={'max_retries': 5, 'countdown': 45}, retry_backoff=True, retry_backoff_max=300, retry_jitter=True, rate_limit='10/m')
def send_weekly_summary(self, user_id: str) -> Any:
    """Sends a weekly compliance summary to a user."""
    logger.info(f'Sending weekly summary to user {user_id}')
    try:
        return asyncio.run(_send_weekly_summary_async(user_id))
    except (NotFoundException, BusinessLogicException) as e:
        logger.warning(f'Business logic error for weekly summary to user {user_id}, not retrying: {e}')
    except Exception as e:
        logger.critical(f'Unexpected, non-retriable error for weekly summary to user {user_id}: {e}', exc_info=True)
        raise

@celery_app.task(bind=True, autoretry_for=(DatabaseException, Exception), retry_kwargs={'max_retries': 5, 'countdown': 60}, retry_backoff=True, retry_backoff_max=300, retry_jitter=True, rate_limit='5/m')
def broadcast_notification(self, subject: str, message: str) -> Dict[str, Any]:
    """Broadcasts a notification to all active users."""
    logger.info(f'Broadcasting notification: {subject}')
    try:
        user_count = asyncio.run(_broadcast_notification_async(subject, message))
        return {'status': 'completed', 'users_notified': user_count}
    except Exception as e:
        logger.critical(f'Unexpected, non-retriable error during broadcast: {e}', exc_info=True)
        raise