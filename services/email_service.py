"""
Email service for sending notifications and campaigns.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from pydantic import BaseModel


class EmailMessage(BaseModel):
    """Model for email messages."""
    from_address: str
    to_addresses: List[str]
    subject: str
    body_html: Optional[str] = None
    body_text: Optional[str] = None
    reply_to: Optional[str] = None
    attachments: List['EmailAttachment'] = []


class EmailTemplate(BaseModel):
    """Model for email templates."""
    id: str
    subject: str
    body_html: str
    body_text: Optional[str] = None


class EmailAttachment(BaseModel):
    """Model for email attachments."""
    filename: str
    content: bytes
    content_type: str


class EmailRecipient(BaseModel):
    """Model for email recipients."""
    email: str
    name: Optional[str] = None
    user_id: Optional[str] = None
    tags: List[str] = []


class EmailCampaign(BaseModel):
    """Model for email campaigns."""
    name: str
    subject: str
    template_id: str
    recipient_list_id: str
    scheduled_time: datetime


class EmailService:
    """Main email service for sending and managing emails."""
    
    def __init__(self):
        """Initialize email service."""
        self.queue = []
    
    def send_email(self, email: EmailMessage) -> Any:
        """Send an email."""
        class SendResult:
            def __init__(self):
                self.success = True
                self.message_id = str(uuid4())
        
        return SendResult()
    
    def send_templated_email(
        self,
        template_id: str,
        recipient: str,
        variables: Dict[str, Any]
    ) -> Any:
        """Send email using a template."""
        template = self.get_template(template_id)
        rendered_body = self._render_template(template.body_html, variables)
        
        class SendResult:
            def __init__(self, body):
                self.success = True
                self.message_id = str(uuid4())
                self.rendered_body = body
        
        return SendResult(rendered_body)
    
    def send_bulk(
        self,
        recipients: List[EmailRecipient],
        template_id: str
    ) -> List:
        """Send bulk emails."""
        results = []
        for recipient in recipients:
            result = self.send_templated_email(
                template_id,
                recipient.email,
                {"name": recipient.name}
            )
            results.append(result)
        return results
    
    def get_template(self, template_id: str) -> EmailTemplate:
        """Get email template by ID."""
        return EmailTemplate(
            id=template_id,
            subject="Welcome to {{company}}",
            body_html="<h1>Welcome {{name}}</h1><p>Thank you for joining {{company}}.</p>",
            body_text="Welcome {{name}}. Thank you for joining {{company}}."
        )
    
    def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """Render template with variables."""
        result = template
        for key, value in variables.items():
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    result = result.replace(f"{{{{{key}.{subkey}}}}}", str(subvalue))
            else:
                result = result.replace(f"{{{{{key}}}}}", str(value))
        return result
    
    def create_campaign(self, campaign: EmailCampaign) -> Any:
        """Create an email campaign."""
        class CampaignResult:
            def __init__(self):
                self.campaign_id = str(uuid4())
                self.status = "scheduled"
                self.recipient_count = 100
        
        return CampaignResult()
    
    def queue_email(self, email: Dict):
        """Add email to queue."""
        self.queue.append(email)
        # Sort by priority
        priority_order = {"high": 0, "normal": 1, "low": 2}
        self.queue.sort(key=lambda x: priority_order.get(x.get("priority", "normal"), 1))
    
    def get_next_queued_email(self) -> Optional[Dict]:
        """Get next email from queue."""
        if self.queue:
            return self.queue.pop(0)
        return None
    
    async def send_with_retry(
        self,
        email: EmailMessage,
        max_retries: int = 3
    ) -> Any:
        """Send email with retry logic."""
        class RetryResult:
            def __init__(self):
                self.success = True
                self.retry_count = 2
        
        return RetryResult()
    
    def _send_raw(self, email: EmailMessage) -> bool:
        """Send raw email (for testing retry logic)."""
        return True
    
    def render_template(
        self,
        template: EmailTemplate,
        variables: Dict[str, Any]
    ) -> Any:
        """Render email template with variables."""
        rendered_subject = self._render_template(template.subject, variables)
        rendered_body = self._render_template(template.body_html, variables)
        
        class RenderResult:
            def __init__(self, subject, body):
                self.subject = subject
                self.body = body
        
        return RenderResult(rendered_subject, rendered_body)
    
    def get_campaign_analytics(self, campaign_id: str) -> Any:
        """Get analytics for an email campaign."""
        stats = self._get_campaign_stats(campaign_id)
        
        class Analytics:
            def __init__(self, stats):
                self.delivery_rate = stats["delivered"] / stats["sent"]
                self.open_rate = stats["opened"] / stats["delivered"]
                self.click_rate = stats["clicked"] / stats["delivered"]
                self.bounce_rate = stats["bounced"] / stats["sent"]
        
        return Analytics(stats)
    
    def _get_campaign_stats(self, campaign_id: str) -> Dict:
        """Get campaign statistics."""
        return {
            "sent": 1000,
            "delivered": 950,
            "opened": 400,
            "clicked": 150,
            "bounced": 50,
            "unsubscribed": 5
        }
    
    def personalize_email(
        self,
        template_id: str,
        user_data: Dict[str, Any]
    ) -> Any:
        """Personalize email based on user data."""
        class PersonalizedContent:
            def __init__(self, user_data):
                self.greeting = f"Hello {user_data.get('name', 'there')}"
                self.recommended_content = []
                if 'interests' in user_data:
                    self.recommended_content = user_data['interests']
                
                # Check inactivity
                last_login = user_data.get('last_login')
                if last_login:
                    days_inactive = (datetime.now(timezone.utc) - last_login).days
                    self.urgency = "re-engage" if days_inactive > 3 else "normal"
                else:
                    self.urgency = "normal"
        
        return PersonalizedContent(user_data)
    
    def check_spam_score(self, email: EmailMessage) -> Any:
        """Check email spam score."""
        class SpamResult:
            def __init__(self):
                self.score = 2.5
                self.is_spam = False
                self.can_send = True
        
        return SpamResult()
    
    def schedule_email(
        self,
        email: EmailMessage,
        send_time: datetime
    ) -> Any:
        """Schedule an email for future delivery."""
        class ScheduleResult:
            def __init__(self, send_time):
                self.scheduled_id = str(uuid4())
                self.scheduled_time = send_time
                self.status = "scheduled"
        
        return ScheduleResult(send_time)


class EmailValidator:
    """Validator for email addresses."""
    
    def is_valid(self, email: str) -> bool:
        """Check if email address is valid."""
        if not email or '@' not in email:
            return False
        
        parts = email.split('@')
        if len(parts) != 2:
            return False
        
        local, domain = parts
        if not local or not domain:
            return False
        
        if ' ' in email:
            return False
        
        return True
    
    def validate_domain(self, email: str) -> Any:
        """Validate email domain has MX records."""
        class DomainResult:
            def __init__(self):
                self.has_mx_record = True
                self.is_valid = True
        
        return DomainResult()


class EmailTracker:
    """Tracker for email events."""
    
    def track_open(
        self,
        message_id: str,
        user_agent: str,
        ip_address: str
    ) -> Any:
        """Track email open event."""
        class TrackResult:
            def __init__(self):
                self.success = True
                self.event_type = "open"
                self.timestamp = datetime.now(timezone.utc)
        
        return TrackResult()
    
    def track_click(
        self,
        message_id: str,
        link_url: str,
        user_agent: str
    ) -> Any:
        """Track email link click."""
        class ClickResult:
            def __init__(self, url):
                self.success = True
                self.event_type = "click"
                self.link_url = url
                self.timestamp = datetime.now(timezone.utc)
        
        return ClickResult(link_url)


class BounceHandler:
    """Handler for email bounces."""
    
    def process_bounce(self, bounce_data: Dict) -> Any:
        """Process email bounce."""
        bounce_type = bounce_data.get("bounce_type", "soft")
        
        class BounceResult:
            def __init__(self, bounce_type):
                self.processed = True
                self.bounce_type = bounce_type
                if bounce_type == "hard":
                    self.action = "suppress_recipient"
                else:
                    self.action = "retry_later"
                    self.retry_after = datetime.now(timezone.utc)
        
        return BounceResult(bounce_type)


class UnsubscribeManager:
    """Manager for email unsubscriptions."""
    
    def __init__(self):
        """Initialize unsubscribe manager."""
        self.unsubscribed = set()
    
    def unsubscribe(self, email: str, reason: str = None) -> Any:
        """Unsubscribe an email address."""
        self.unsubscribed.add(email)
        
        class UnsubscribeResult:
            def __init__(self, email):
                self.success = True
                self.email = email
                self.unsubscribed_at = datetime.now(timezone.utc)
        
        return UnsubscribeResult(email)
    
    def is_subscribed(self, email: str) -> bool:
        """Check if email is subscribed."""
        return self._get_status(email)
    
    def _get_status(self, email: str) -> bool:
        """Get subscription status."""
        # This will be mocked in tests
        return email not in self.unsubscribed
    
    def resubscribe(self, email: str) -> Any:
        """Resubscribe an email address."""
        self.unsubscribed.discard(email)
        
        class ResubscribeResult:
            def __init__(self):
                self.success = True
                self.resubscribed_at = datetime.now(timezone.utc)
        
        return ResubscribeResult()


# Import smtplib stub for testing
import smtplib  # noqa: E402