"""
Celery background tasks for compliance scoring and monitoring.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from celery.utils.log import get_task_logger
from sqlalchemy.orm import Session

from celery_app import celery_app
from database.db_setup import get_db
from database.business_profile import BusinessProfile
from database.evidence_item import EvidenceItem
from services.readiness_service import calculate_readiness_score

logger = get_task_logger(__name__)

@celery_app.task
def update_all_compliance_scores():
    """
    Updates compliance scores for all business profiles.
    """
    logger.info("Starting compliance score updates for all profiles")
    
    try:
        db = next(get_db())
        
        # Get all business profiles
        profiles = db.query(BusinessProfile).all()
        
        updated_count = 0
        for profile in profiles:
            try:
                # Calculate new readiness score
                readiness_data = calculate_readiness_score(str(profile.id), db)
                
                # Update profile with new score (mock implementation)
                # In real implementation, you would have a compliance_score field
                logger.debug(f"Updated compliance score for profile {profile.id}: {readiness_data.get('overall_score', 0)}")
                updated_count += 1
                
            except Exception as e:
                logger.error(f"Failed to update compliance score for profile {profile.id}: {e}")
        
        db.commit()
        
        return {
            "status": "completed",
            "updated_profiles": updated_count,
            "total_profiles": len(profiles)
        }
        
    except Exception as e:
        logger.error(f"Compliance score update failed: {e}")
        return {"status": "error", "reason": str(e)}
    finally:
        db.close()

@celery_app.task
def generate_daily_reports():
    """
    Generates daily compliance reports for all active profiles.
    """
    logger.info("Starting daily compliance report generation")
    
    try:
        db = next(get_db())
        
        # Get profiles that need daily reports
        profiles = db.query(BusinessProfile).all()
        
        generated_count = 0
        for profile in profiles:
            try:
                # Generate report (mock implementation)
                report_data = {
                    "profile_id": str(profile.id),
                    "generated_at": datetime.utcnow().isoformat(),
                    "type": "daily_compliance_summary",
                    "data": {
                        "compliance_score": 85.0,  # Mock score
                        "evidence_count": 10,  # Mock count
                        "pending_actions": 3   # Mock actions
                    }
                }
                
                logger.debug(f"Generated daily report for profile {profile.id}")
                generated_count += 1
                
            except Exception as e:
                logger.error(f"Failed to generate report for profile {profile.id}: {e}")
        
        return {
            "status": "completed",
            "generated_reports": generated_count,
            "total_profiles": len(profiles)
        }
        
    except Exception as e:
        logger.error(f"Daily report generation failed: {e}")
        return {"status": "error", "reason": str(e)}
    finally:
        db.close()

@celery_app.task
def check_compliance_alerts():
    """
    Checks for compliance issues that require immediate attention.
    """
    logger.info("Checking for compliance alerts")
    
    try:
        db = next(get_db())
        
        alerts = []
        profiles = db.query(BusinessProfile).all()
        
        for profile in profiles:
            try:
                # Check for expired evidence
                expired_evidence = db.query(EvidenceItem).filter(
                    EvidenceItem.user_id == str(profile.user_id),
                    EvidenceItem.collection_notes.like('%"expired": true%')
                ).count()
                
                if expired_evidence > 0:
                    alerts.append({
                        "profile_id": str(profile.id),
                        "type": "expired_evidence",
                        "count": expired_evidence,
                        "severity": "medium"
                    })
                
                # Check for low compliance scores (mock)
                # In real implementation, check actual compliance scores
                
            except Exception as e:
                logger.error(f"Failed to check alerts for profile {profile.id}: {e}")
        
        return {
            "status": "completed", 
            "alerts_count": len(alerts),
            "alerts": alerts
        }
        
    except Exception as e:
        logger.error(f"Compliance alert check failed: {e}")
        return {"status": "error", "reason": str(e)}
    finally:
        db.close()