"""
Manages scheduled report generation using the Celery Beat scheduler.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from celery.schedules import crontab
from sqlalchemy.orm import Session
import json

from celery_app import celery_app
from database.db_setup import get_db

class ReportSchedule:
    """Model for storing report schedule configuration."""
    
    def __init__(self, 
                 schedule_id: str,
                 user_id: str,
                 business_profile_id: str,
                 report_type: str,
                 frequency: str,
                 parameters: Dict[str, Any],
                 recipients: List[str],
                 active: bool = True,
                 created_at: datetime = None):
        self.schedule_id = schedule_id
        self.user_id = user_id
        self.business_profile_id = business_profile_id
        self.report_type = report_type
        self.frequency = frequency
        self.parameters = parameters
        self.recipients = recipients
        self.active = active
        self.created_at = created_at or datetime.utcnow()

class ReportScheduler:
    """Service to create, manage, and delete report schedules."""
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
        # In a real implementation, you'd store schedules in the database
        # For now, we'll use in-memory storage for demonstration
        self._schedules: Dict[str, ReportSchedule] = {}
    
    def create_schedule(self, 
                       user_id: str,
                       business_profile_id: str,
                       report_type: str,
                       frequency: str,
                       parameters: Dict[str, Any],
                       recipients: List[str],
                       schedule_config: Dict[str, Any] = None) -> str:
        """Creates a new report generation schedule."""
        
        schedule_id = str(uuid4())
        schedule_config = schedule_config or {}
        
        # Validate frequency
        valid_frequencies = ['daily', 'weekly', 'monthly']
        if frequency not in valid_frequencies:
            raise ValueError(f"Invalid frequency. Must be one of: {valid_frequencies}")
        
        # Create schedule object
        report_schedule = ReportSchedule(
            schedule_id=schedule_id,
            user_id=user_id,
            business_profile_id=business_profile_id,
            report_type=report_type,
            frequency=frequency,
            parameters=parameters,
            recipients=recipients
        )
        
        # Store in memory (in real implementation, save to database)
        self._schedules[schedule_id] = report_schedule
        
        # Create Celery Beat schedule
        task_name = f"scheduled_report_{schedule_id}"
        cron_schedule = self._create_cron_schedule(frequency, schedule_config)
        
        # Add to Celery Beat schedule
        celery_app.conf.beat_schedule[task_name] = {
            'task': 'workers.reporting_tasks.generate_and_distribute_report',
            'schedule': cron_schedule,
            'args': (schedule_id,),
            'options': {'queue': 'reports'}
        }
        
        # In a real system, you would need to reload the beat schedule
        # This in-memory update is for demonstration
        
        return schedule_id
    
    def update_schedule(self, schedule_id: str, updates: Dict[str, Any]) -> bool:
        """Updates an existing report schedule."""
        
        if schedule_id not in self._schedules:
            return False
        
        schedule = self._schedules[schedule_id]
        
        # Update allowed fields
        allowed_updates = ['frequency', 'parameters', 'recipients', 'active']
        for field, value in updates.items():
            if field in allowed_updates:
                setattr(schedule, field, value)
        
        # If frequency was updated, recreate the Celery schedule
        if 'frequency' in updates:
            self.delete_schedule(schedule_id)
            self.create_schedule(
                schedule.user_id,
                schedule.business_profile_id,
                schedule.report_type,
                schedule.frequency,
                schedule.parameters,
                schedule.recipients
            )
        
        return True
    
    def delete_schedule(self, schedule_id: str) -> bool:
        """Removes a report generation task from the schedule."""
        
        task_name = f"scheduled_report_{schedule_id}"
        
        # Remove from Celery Beat schedule
        if task_name in celery_app.conf.beat_schedule:
            del celery_app.conf.beat_schedule[task_name]
        
        # Remove from memory storage
        if schedule_id in self._schedules:
            del self._schedules[schedule_id]
            return True
        
        return False
    
    def get_schedule(self, schedule_id: str) -> Optional[ReportSchedule]:
        """Gets a specific schedule by ID."""
        return self._schedules.get(schedule_id)
    
    def list_user_schedules(self, user_id: str) -> List[ReportSchedule]:
        """Lists all schedules for a specific user."""
        return [
            schedule for schedule in self._schedules.values()
            if schedule.user_id == user_id
        ]
    
    def get_active_schedules(self) -> List[ReportSchedule]:
        """Gets all active schedules."""
        return [
            schedule for schedule in self._schedules.values()
            if schedule.active
        ]
    
    def _create_cron_schedule(self, frequency: str, config: Dict[str, Any]) -> crontab:
        """Creates a crontab schedule based on frequency and configuration."""
        
        if frequency == 'daily':
            hour = config.get('hour', 8)
            minute = config.get('minute', 0)
            return crontab(hour=hour, minute=minute)
        
        elif frequency == 'weekly':
            hour = config.get('hour', 8)
            minute = config.get('minute', 0)
            day_of_week = config.get('day_of_week', 1)  # Monday
            return crontab(hour=hour, minute=minute, day_of_week=day_of_week)
        
        elif frequency == 'monthly':
            hour = config.get('hour', 8)
            minute = config.get('minute', 0)
            day_of_month = config.get('day_of_month', 1)  # First day of month
            return crontab(hour=hour, minute=minute, day_of_month=day_of_month)
        
        else:
            raise ValueError(f"Unsupported frequency: {frequency}")
    
    def execute_schedule(self, schedule_id: str) -> Dict[str, Any]:
        """Manually executes a scheduled report (for testing)."""
        
        schedule = self.get_schedule(schedule_id)
        if not schedule:
            return {"error": "Schedule not found"}
        
        if not schedule.active:
            return {"error": "Schedule is inactive"}
        
        # Trigger the report generation task
        from workers.reporting_tasks import generate_and_distribute_report
        
        try:
            # Execute the task synchronously for immediate results
            result = generate_and_distribute_report.delay(schedule_id)
            
            return {
                "status": "success",
                "task_id": result.id,
                "schedule_id": schedule_id,
                "executed_at": datetime.utcnow().isoformat()
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "schedule_id": schedule_id
            }
    
    def get_schedule_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Gets statistics about report schedules."""
        
        schedules = self._schedules.values()
        
        if user_id:
            schedules = [s for s in schedules if s.user_id == user_id]
        
        stats = {
            "total_schedules": len(schedules),
            "active_schedules": len([s for s in schedules if s.active]),
            "inactive_schedules": len([s for s in schedules if not s.active]),
            "by_frequency": {},
            "by_report_type": {},
            "total_recipients": 0
        }
        
        for schedule in schedules:
            # Count by frequency
            freq = schedule.frequency
            stats["by_frequency"][freq] = stats["by_frequency"].get(freq, 0) + 1
            
            # Count by report type
            report_type = schedule.report_type
            stats["by_report_type"][report_type] = stats["by_report_type"].get(report_type, 0) + 1
            
            # Count total recipients
            stats["total_recipients"] += len(schedule.recipients)
        
        return stats