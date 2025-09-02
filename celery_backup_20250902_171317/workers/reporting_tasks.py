"""
from __future__ import annotations
import requests

Celery background tasks for report generation and distribution, with async support.
"""
import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID
from celery.utils.log import get_task_logger
from core.exceptions import ApplicationException, BusinessLogicException, DatabaseException, IntegrationException, NotFoundException
from database.db_setup import get_async_db
from services.reporting.pdf_generator import PDFGenerator
from services.reporting.report_generator import ReportGenerator
from services.reporting.report_scheduler import ReportScheduler
logger = get_task_logger(__name__)

def _send_email_sync(recipient_emails: List[str], subject: str, body: str, attachments: Optional[List[Dict[str, Any]]]=None) -> bool:
    """Sends an email. This remains synchronous as smtplib is blocking."""
    try:
        logger.info(f"Mock sending email to {', '.join(recipient_emails)} with subject: {subject}")
        if attachments:
            logger.info(f'With {len(attachments)} attachments.')
        return True
    except (ValueError, TypeError) as e:
        logger.error(f'Failed to send email: {e}', exc_info=True)
        return False

async def _generate_and_distribute_report_async(schedule_id_str: str):
    """Async helper to generate and distribute a scheduled report."""
    schedule_id = UUID(schedule_id_str)
    async for db in get_async_db():
        scheduler = ReportScheduler(db)
        try:
            schedule = await scheduler.get_schedule(schedule_id)
            if not schedule.active:
                logger.info(f'Schedule {schedule_id} is inactive, skipping.')
                return {'status': 'skipped', 'reason': 'schedule_inactive'}
            report_generator = ReportGenerator(db)
            report_data = await report_generator.generate_report(schedule.user_id, schedule.business_profile_id, schedule.report_type, schedule.report_format)
            attachment = None
            if schedule.report_format == 'pdf':
                pdf_generator = PDFGenerator(report_data)
                pdf_content = pdf_generator.generate()
                attachment = {'filename': f"{schedule.report_type.replace(' ', '_')}_{datetime.now(timezone.utc).strftime('%Y%m%d')}.pdf", 'content': pdf_content}
            html_content = report_data.get('html_content', 'Please find your scheduled compliance report attached.')
            distribution_success = _send_email_sync(schedule.recipients, f'Your Scheduled Report: {schedule.report_type}', html_content, attachments=[attachment] if attachment else None)
            await scheduler.update_schedule_status(schedule_id, 'success', distribution_success)
            return {'status': 'completed', 'schedule_id': str(schedule_id), 'distribution_successful': distribution_success}
        except NotFoundException as e:
            logger.error(f'Report generation failed for schedule {schedule_id}: {e}')
            raise
        except (DatabaseException, BusinessLogicException, IntegrationException) as e:
            logger.error(f'A handled error occurred for schedule {schedule_id}: {e}')
            await scheduler.update_schedule_status(schedule_id, 'failed')
            raise
        except (OSError, requests.RequestException, Exception):
            logger.critical(f'An unexpected error occurred for schedule {schedule_id}', exc_info=True)
            try:
                await scheduler.update_schedule_status(schedule_id, 'failed')
            except Exception as update_e:
                logger.error(f'Could not even update schedule {schedule_id} to failed status: {update_e}')
            raise

async def _send_report_summary_notifications_async():
    """Async helper to send summary notifications about report activity."""
    async for db in get_async_db():
        scheduler = ReportScheduler(db)
        active_schedules = await scheduler.get_active_schedules()
        user_summaries = {}
        for schedule in active_schedules:
            user_id = schedule.user_id
            if user_id not in user_summaries:
                user_summaries[user_id] = {'schedules': [], 'total_reports': 0, 'user': schedule.user}
            user_summaries[user_id]['schedules'].append(schedule)
            user_summaries[user_id]['total_reports'] += 1
        notifications_sent = 0
        for user_id, summary in user_summaries.items():
            user = summary['user']
            if user and user.email:
                logger.info(f"Would send summary to {user.email} for {summary['total_reports']} scheduled reports")
                notifications_sent += 1
        return {'status': 'completed', 'notifications_sent': notifications_sent, 'users_processed': len(user_summaries)}

@celery_app.task(bind=True, autoretry_for=(DatabaseException, Exception), retry_kwargs={'max_retries': 5, 'countdown': 120}, retry_backoff=True, retry_backoff_max=600, retry_jitter=True, rate_limit='2/m')
def generate_and_distribute_report(self, schedule_id: str) -> Any:
    """Celery task to generate and distribute a report by running the async helper."""
    try:
        return asyncio.run(_generate_and_distribute_report_async(schedule_id))
    except ApplicationException as e:
        logger.warning(f'Report generation for {schedule_id} failed with a handled error: {e}')
    except (ValueError, TypeError) as e:
        logger.error(f'Unhandled exception in celery task for schedule {schedule_id}. Retrying...', exc_info=True)
        self.retry(exc=e)

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 90}, retry_backoff=True, retry_backoff_max=400, retry_jitter=True, rate_limit='5/m')
def generate_report_on_demand(self, user_id: str, profile_id: str, report_type: str, recipients: List[str]) -> Dict[str, Any]:
    """Mock task for on-demand report generation."""
    logger.info(f'On-demand report for user {user_id}, profile {profile_id}')
    _send_email_sync(recipients, f'Your On-Demand Report: {report_type}', 'Here is your on-demand report.')
    return {'status': 'completed'}

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60}, retry_backoff=True, retry_backoff_max=300, retry_jitter=True, rate_limit='1/h')
def cleanup_old_reports(self) -> Dict[str, Any]:
    """Mock task for cleaning up old reports."""
    logger.info('Running mock cleanup for old reports.')
    return {'status': 'completed', 'cleaned_reports': 0}

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 5, 'countdown': 45}, retry_backoff=True, retry_backoff_max=300, retry_jitter=True, rate_limit='10/m')
def send_report_summary_notifications(self) -> Any:
    """Celery task to send summary notifications by running the async helper."""
    try:
        return asyncio.run(_send_report_summary_notifications_async())
    except (ValueError, TypeError) as e:
        logger.error(f'Report summary notifications failed: {e}', exc_info=True)
        return {'status': 'error', 'reason': str(e)}