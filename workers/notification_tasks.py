"""
Celery background tasks for sending notifications and alerts.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from celery.utils.log import get_task_logger
from sqlalchemy.orm import Session
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

from celery_app import celery_app
from database.db_setup import get_db
from database.business_profile import BusinessProfile
from database.user import User

logger = get_task_logger(__name__)

@celery_app.task
def send_compliance_alert(user_id: str, alert_type: str, alert_data: Dict[str, Any]):
    """
    Sends a compliance alert notification to a user.
    """
    logger.info(f"Sending compliance alert to user {user_id}: {alert_type}")
    
    try:
        db = next(get_db())
        
        # Get user information
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logger.error(f"User {user_id} not found")
            return {"status": "error", "reason": "user_not_found"}
        
        # Prepare notification content based on alert type
        subject, body = _prepare_alert_content(alert_type, alert_data, user)
        
        # Send notification (mock implementation)
        notification_result = _send_email_notification(user.email, subject, body)
        
        return {
            "status": "sent",
            "user_id": user_id,
            "alert_type": alert_type,
            "notification_method": notification_result["method"]
        }
        
    except Exception as e:
        logger.error(f"Failed to send compliance alert to user {user_id}: {e}")
        return {"status": "error", "reason": str(e)}
    finally:
        db.close()

@celery_app.task
def send_weekly_summary(user_id: str):
    """
    Sends a weekly compliance summary to a user.
    """
    logger.info(f"Sending weekly summary to user {user_id}")
    
    try:
        db = next(get_db())
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return {"status": "error", "reason": "user_not_found"}
        
        profile = db.query(BusinessProfile).filter(BusinessProfile.user_id == user_id).first()
        if not profile:
            return {"status": "error", "reason": "profile_not_found"}
        
        # Generate weekly summary data
        summary_data = _generate_weekly_summary(profile, db)
        
        subject = f"Weekly Compliance Summary - {profile.company_name}"
        body = _format_weekly_summary(summary_data)
        
        notification_result = _send_email_notification(user.email, subject, body)
        
        return {
            "status": "sent",
            "user_id": user_id,
            "summary_data": summary_data
        }
        
    except Exception as e:
        logger.error(f"Failed to send weekly summary to user {user_id}: {e}")
        return {"status": "error", "reason": str(e)}
    finally:
        db.close()

@celery_app.task
def send_evidence_expiry_notifications():
    """
    Sends notifications for evidence items that are expiring soon.
    """
    logger.info("Checking for evidence expiry notifications")
    
    try:
        db = next(get_db())
        
        # Find evidence expiring in the next 7 days
        notification_window = datetime.utcnow() + timedelta(days=7)
        
        # Mock implementation - in real system, query for evidence with expiry dates
        expiring_evidence = []  # Would contain actual evidence items
        
        notifications_sent = 0
        for evidence in expiring_evidence:
            try:
                # Send expiry notification
                send_compliance_alert.delay(
                    evidence.user_id,
                    "evidence_expiring",
                    {
                        "evidence_id": evidence.id,
                        "evidence_name": evidence.evidence_name,
                        "expires_at": notification_window.isoformat()
                    }
                )
                notifications_sent += 1
                
            except Exception as e:
                logger.error(f"Failed to send expiry notification for evidence {evidence.id}: {e}")
        
        return {
            "status": "completed",
            "notifications_sent": notifications_sent,
            "expiring_items": len(expiring_evidence)
        }
        
    except Exception as e:
        logger.error(f"Evidence expiry notification check failed: {e}")
        return {"status": "error", "reason": str(e)}
    finally:
        db.close()

# Helper functions
def _prepare_alert_content(alert_type: str, alert_data: Dict[str, Any], user) -> tuple[str, str]:
    """
    Prepares email subject and body based on alert type.
    """
    if alert_type == "expired_evidence":
        subject = "Action Required: Evidence Items Have Expired"
        body = f"""
        Dear {user.username},
        
        {alert_data.get('count', 0)} of your evidence items have expired and need to be renewed.
        
        Please log in to your ComplianceGPT dashboard to review and update your evidence.
        
        Best regards,
        ComplianceGPT Team
        """
    elif alert_type == "evidence_expiring":
        subject = "Reminder: Evidence Expiring Soon"
        body = f"""
        Dear {user.username},
        
        Your evidence item "{alert_data.get('evidence_name', 'Unknown')}" will expire soon.
        
        Please review and renew this evidence to maintain your compliance status.
        
        Best regards,
        ComplianceGPT Team
        """
    else:
        subject = "Compliance Alert"
        body = f"""
        Dear {user.username},
        
        We have a compliance update for your account.
        
        Please log in to your dashboard for more details.
        
        Best regards,
        ComplianceGPT Team
        """
    
    return subject, body

def _send_email_notification(email: str, subject: str, body: str) -> Dict[str, Any]:
    """
    Sends an email notification (mock implementation).
    """
    # Mock email sending - in production, use proper SMTP settings
    logger.info(f"Mock email sent to {email}: {subject}")
    
    return {
        "method": "email",
        "recipient": email,
        "sent_at": datetime.utcnow().isoformat(),
        "status": "delivered"  # Mock status
    }

def _generate_weekly_summary(profile: BusinessProfile, db: Session) -> Dict[str, Any]:
    """
    Generates weekly summary data for a business profile.
    """
    from database.evidence_item import EvidenceItem
    
    # Calculate summary metrics
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    # Count evidence items added this week
    new_evidence_count = db.query(EvidenceItem).filter(
        EvidenceItem.user_id == str(profile.user_id),
        EvidenceItem.created_at > week_ago
    ).count()
    
    # Total evidence count
    total_evidence_count = db.query(EvidenceItem).filter(
        EvidenceItem.user_id == str(profile.user_id)
    ).count()
    
    return {
        "company_name": profile.company_name,
        "week_period": f"{week_ago.strftime('%Y-%m-%d')} to {datetime.utcnow().strftime('%Y-%m-%d')}",
        "new_evidence_this_week": new_evidence_count,
        "total_evidence_items": total_evidence_count,
        "compliance_score": 85.0,  # Mock score
        "pending_actions": 3,  # Mock actions
        "frameworks": profile.compliance_frameworks or []
    }

def _format_weekly_summary(summary_data: Dict[str, Any]) -> str:
    """
    Formats the weekly summary data into an email body.
    """
    return f"""
    Weekly Compliance Summary for {summary_data['company_name']}
    Period: {summary_data['week_period']}
    
    📊 This Week's Activity:
    • New evidence items collected: {summary_data['new_evidence_this_week']}
    • Total evidence items: {summary_data['total_evidence_items']}
    • Current compliance score: {summary_data['compliance_score']}%
    
    ⚠️ Items requiring attention: {summary_data['pending_actions']}
    
    🛡️ Active frameworks: {', '.join(summary_data['frameworks']) if summary_data['frameworks'] else 'None configured'}
    
    Log in to your dashboard to review detailed progress and take any necessary actions.
    
    Best regards,
    ComplianceGPT Team
    """