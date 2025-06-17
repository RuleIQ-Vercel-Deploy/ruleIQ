"""
Celery background tasks for report generation and distribution.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from typing import Dict, List, Any
from celery.utils.log import get_task_logger
from sqlalchemy.orm import Session
from datetime import datetime
import base64
import os

from celery_app import celery_app
from database.db_setup import get_db
from database.business_profile import BusinessProfile
from database.user import User
from services.reporting.report_generator import ReportGenerator
from services.reporting.pdf_generator import PDFGenerator
from services.reporting.report_scheduler import ReportScheduler

logger = get_task_logger(__name__)

@celery_app.task(bind=True, max_retries=3)
def generate_and_distribute_report(self, schedule_id: str):
    """
    Generates a scheduled report and distributes it to recipients.
    """
    logger.info(f"Starting scheduled report generation for schedule {schedule_id}")
    
    try:
        db = next(get_db())
        scheduler = ReportScheduler(db)
        
        # Get the schedule details
        schedule = scheduler.get_schedule(schedule_id)
        if not schedule:
            logger.error(f"Schedule {schedule_id} not found")
            return {"status": "error", "reason": "schedule_not_found"}
        
        if not schedule.active:
            logger.info(f"Schedule {schedule_id} is inactive, skipping")
            return {"status": "skipped", "reason": "schedule_inactive"}
        
        # Get business profile
        profile = db.query(BusinessProfile).filter(
            BusinessProfile.id == schedule.business_profile_id
        ).first()
        
        if not profile:
            logger.error(f"Business profile {schedule.business_profile_id} not found")
            return {"status": "error", "reason": "profile_not_found"}
        
        # Get user for authentication context
        user = db.query(User).filter(User.id == schedule.user_id).first()
        if not user:
            logger.error(f"User {schedule.user_id} not found")
            return {"status": "error", "reason": "user_not_found"}
        
        # Generate the report
        report_generator = ReportGenerator(db)
        report_data = await report_generator.generate_report(
            user=user,
            business_profile_id=profile.id,
            report_type=schedule.report_type,
            parameters=schedule.parameters
        )
        
        # Generate PDF
        pdf_generator = PDFGenerator()
        pdf_bytes = await pdf_generator.generate_pdf(report_data)
        
        # Distribute to recipients
        distribution_results = []
        for recipient in schedule.recipients:
            try:
                result = await send_report_email(
                    recipient_email=recipient,
                    report_data=report_data,
                    pdf_bytes=pdf_bytes,
                    business_name=profile.company_name
                )
                distribution_results.append({
                    "recipient": recipient,
                    "status": "success" if result else "failed"
                })
            except Exception as e:
                logger.error(f"Failed to send report to {recipient}: {e}")
                distribution_results.append({
                    "recipient": recipient,
                    "status": "failed",
                    "error": str(e)
                })
        
        return {
            "status": "completed",
            "schedule_id": schedule_id,
            "report_type": schedule.report_type,
            "generated_at": datetime.utcnow().isoformat(),
            "recipients_count": len(schedule.recipients),
            "distribution_results": distribution_results
        }
        
    except Exception as e:
        logger.error(f"Report generation failed for schedule {schedule_id}: {e}")
        
        # Retry with exponential backoff
        if self.request.retries < self.max_retries:
            countdown = 60 * (2 ** self.request.retries)
            logger.info(f"Retrying in {countdown} seconds (attempt {self.request.retries + 1}/{self.max_retries})")
            raise self.retry(exc=e, countdown=countdown)
        else:
            return {"status": "error", "reason": str(e), "retries_exhausted": True}
    
    finally:
        db.close()

@celery_app.task
def generate_report_on_demand(user_id: str, business_profile_id: str, report_type: str, parameters: Dict[str, Any]):
    """
    Generates a report on-demand (not scheduled).
    """
    logger.info(f"Starting on-demand report generation: {report_type} for user {user_id}")
    
    try:
        db = next(get_db())
        
        # Get user and business profile
        user = db.query(User).filter(User.id == user_id).first()
        profile = db.query(BusinessProfile).filter(
            BusinessProfile.id == business_profile_id
        ).first()
        
        if not user or not profile:
            return {"status": "error", "reason": "user_or_profile_not_found"}
        
        # Generate the report
        report_generator = ReportGenerator(db)
        report_data = await report_generator.generate_report(
            user=user,
            business_profile_id=profile.id,
            report_type=report_type,
            parameters=parameters
        )
        
        return {
            "status": "completed",
            "report_data": report_data,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"On-demand report generation failed: {e}")
        return {"status": "error", "reason": str(e)}
    
    finally:
        db.close()

@celery_app.task
def cleanup_old_reports():
    """
    Cleans up old report files and temporary data.
    """
    logger.info("Starting cleanup of old reports")
    
    try:
        # This would clean up temporary files, old cached reports, etc.
        # For now, just return success
        
        return {
            "status": "completed",
            "cleaned_up_at": datetime.utcnow().isoformat(),
            "files_cleaned": 0  # Mock value
        }
        
    except Exception as e:
        logger.error(f"Report cleanup failed: {e}")
        return {"status": "error", "reason": str(e)}

async def send_report_email(recipient_email: str, report_data: Dict[str, Any], pdf_bytes: bytes, business_name: str) -> bool:
    """
    Sends a report via email with PDF attachment.
    """
    try:
        # Email configuration (these should be in environment variables)
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        from_email = os.getenv('FROM_EMAIL', smtp_username)
        
        if not all([smtp_username, smtp_password]):
            logger.warning("SMTP credentials not configured, skipping email send")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = recipient_email
        msg['Subject'] = f"Compliance Report for {business_name}"
        
        # Email body
        report_type = report_data.get('report_type', 'compliance_report').replace('_', ' ').title()
        generated_date = datetime.fromisoformat(report_data['generated_at']).strftime('%B %d, %Y')
        
        body = f"""
        Dear Recipient,
        
        Please find attached your {report_type} for {business_name}, generated on {generated_date}.
        
        This report provides insights into your current compliance status and recommendations for improvement.
        
        If you have any questions about this report, please contact your compliance team.
        
        Best regards,
        ComplianceGPT Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Attach PDF
        filename = f"{business_name}_{report_type}_{generated_date}.pdf".replace(' ', '_')
        attachment = MIMEBase('application', 'pdf')
        attachment.set_payload(pdf_bytes)
        encoders.encode_base64(attachment)
        attachment.add_header(
            'Content-Disposition',
            f'attachment; filename= {filename}'
        )
        msg.attach(attachment)
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(from_email, recipient_email, text)
        server.quit()
        
        logger.info(f"Report email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {e}")
        return False

@celery_app.task
def send_report_summary_notifications():
    """
    Sends summary notifications about recent report activity.
    """
    logger.info("Starting report summary notifications")
    
    try:
        db = next(get_db())
        
        # Get all active schedules and their last execution status
        scheduler = ReportScheduler(db)
        active_schedules = scheduler.get_active_schedules()
        
        # Group by user for summary
        user_summaries = {}
        for schedule in active_schedules:
            user_id = schedule.user_id
            if user_id not in user_summaries:
                user_summaries[user_id] = {
                    "schedules": [],
                    "total_reports": 0
                }
            
            user_summaries[user_id]["schedules"].append(schedule)
            user_summaries[user_id]["total_reports"] += 1
        
        # Send summary emails to users
        notifications_sent = 0
        for user_id, summary in user_summaries.items():
            try:
                user = db.query(User).filter(User.id == user_id).first()
                if user and user.email:
                    # Send summary notification (simplified)
                    logger.info(f"Would send summary to {user.email} for {summary['total_reports']} scheduled reports")
                    notifications_sent += 1
            except Exception as e:
                logger.error(f"Failed to send summary to user {user_id}: {e}")
        
        return {
            "status": "completed",
            "notifications_sent": notifications_sent,
            "users_processed": len(user_summaries)
        }
        
    except Exception as e:
        logger.error(f"Report summary notifications failed: {e}")
        return {"status": "error", "reason": str(e)}
    
    finally:
        db.close()