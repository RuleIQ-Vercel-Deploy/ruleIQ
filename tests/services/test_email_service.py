"""Tests for the email service module."""

import pytest
from datetime import datetime, timedelta, UTC
from unittest.mock import Mock, patch, MagicMock
from uuid import uuid4
import base64
from typing import List, Dict, Any

from services.email_service import (
    EmailService,
    EmailMessage, 
    EmailTemplate,
    EmailAttachment,
    EmailRecipient,
    EmailCampaign,
    EmailValidator,
    EmailTracker,
    BounceHandler,
    UnsubscribeManager
)


class TestEmailService:
    """Test suite for EmailService."""

    @pytest.fixture
    def email_service(self):
        """Create an email service instance."""
        return EmailService()

    @pytest.fixture
    def mock_smtp(self):
        """Create a mock SMTP client."""
        with patch('services.email_service.smtplib.SMTP') as mock:
            yield mock

    @pytest.fixture
    def sample_email(self):
        """Create a sample email message."""
        return EmailMessage(
            from_address="noreply@ruleiq.com",
            to_addresses=["user@example.com"],
            subject="Test Email",
            body_html="<h1>Hello World</h1>",
            body_text="Hello World",
            reply_to="support@ruleiq.com"
        )

    @pytest.fixture
    def sample_recipient(self):
        """Create a sample email recipient."""
        return EmailRecipient(
            email="user@example.com",
            name="Test User",
            user_id=str(uuid4()),
            tags=["customer", "active"]
        )

    def test_send_email(self, email_service, sample_email, mock_smtp):
        """Test sending a basic email."""
        # Act
        result = email_service.send_email(sample_email)
        
        # Assert
        assert result.success is True
        assert result.message_id is not None
        mock_smtp.return_value.__enter__.return_value.send_message.assert_called_once()

    def test_send_email_with_attachments(self, email_service, mock_smtp):
        """Test sending email with attachments."""
        # Arrange
        email = EmailMessage(
            from_address="noreply@ruleiq.com",
            to_addresses=["user@example.com"],
            subject="Report Attached",
            body_text="Please find the report attached."
        )
        attachment = EmailAttachment(
            filename="report.pdf",
            content=b"PDF content here",
            content_type="application/pdf"
        )
        email.attachments = [attachment]
        
        # Act
        result = email_service.send_email(email)
        
        # Assert
        assert result.success is True
        mock_smtp.return_value.__enter__.return_value.send_message.assert_called_once()

    def test_send_templated_email(self, email_service, mock_smtp):
        """Test sending email using template."""
        # Arrange
        template = EmailTemplate(
            id="welcome",
            subject="Welcome to {{company}}",
            body_html="<h1>Welcome {{name}}</h1><p>Thank you for joining {{company}}.</p>",
            body_text="Welcome {{name}}. Thank you for joining {{company}}."
        )
        variables = {"name": "John Doe", "company": "RuleIQ"}
        recipient = "john@example.com"
        
        # Act
        with patch.object(email_service, 'get_template') as mock_template:
            mock_template.return_value = template
            result = email_service.send_templated_email(
                template_id="welcome",
                recipient=recipient,
                variables=variables
            )
        
        # Assert
        assert result.success is True
        assert "John Doe" in result.rendered_body
        assert "RuleIQ" in result.rendered_body

    def test_send_bulk_emails(self, email_service, mock_smtp):
        """Test sending bulk emails."""
        # Arrange
        recipients = [
            EmailRecipient(email="user1@example.com", name="User 1"),
            EmailRecipient(email="user2@example.com", name="User 2"),
            EmailRecipient(email="user3@example.com", name="User 3")
        ]
        template_id = "newsletter"
        
        # Act
        with patch.object(email_service, 'send_templated_email') as mock_send:
            mock_send.return_value = Mock(success=True, message_id="123")
            results = email_service.send_bulk(recipients, template_id)
        
        # Assert
        assert len(results) == 3
        assert all(r.success for r in results)
        assert mock_send.call_count == 3

    def test_validate_email_address(self, email_service):
        """Test email address validation."""
        # Arrange
        valid_emails = [
            "user@example.com",
            "john.doe@company.co.uk",
            "test+tag@domain.org"
        ]
        invalid_emails = [
            "invalid.email",
            "@domain.com",
            "user@",
            "user @domain.com",
            ""
        ]
        
        # Act & Assert
        validator = EmailValidator()
        for email in valid_emails:
            assert validator.is_valid(email) is True
        
        for email in invalid_emails:
            assert validator.is_valid(email) is False

    def test_validate_email_domain(self, email_service):
        """Test email domain validation."""
        # Arrange
        email = "user@example.com"
        
        # Act
        with patch('services.email_service.dns.resolver.resolve') as mock_dns:
            mock_dns.return_value = [Mock(exchange="mail.example.com")]
            validator = EmailValidator()
            result = validator.validate_domain(email)
        
        # Assert
        assert result.has_mx_record is True
        assert result.is_valid is True

    def test_create_email_campaign(self, email_service):
        """Test creating an email campaign."""
        # Arrange
        campaign = EmailCampaign(
            name="Product Launch",
            subject="Introducing Our New Features",
            template_id="product_launch",
            recipient_list_id="all_customers",
            scheduled_time=datetime.now(UTC) + timedelta(days=1)
        )
        
        # Act
        result = email_service.create_campaign(campaign)
        
        # Assert
        assert result.campaign_id is not None
        assert result.status == "scheduled"
        assert result.recipient_count > 0

    def test_track_email_open(self, email_service):
        """Test tracking email opens."""
        # Arrange
        message_id = "msg_123456"
        user_agent = "Mozilla/5.0"
        ip_address = "192.168.1.100"
        
        # Act
        tracker = EmailTracker()
        result = tracker.track_open(message_id, user_agent, ip_address)
        
        # Assert
        assert result.success is True
        assert result.event_type == "open"
        assert result.timestamp is not None

    def test_track_email_click(self, email_service):
        """Test tracking email link clicks."""
        # Arrange
        message_id = "msg_123456"
        link_url = "https://ruleiq.com/features"
        user_agent = "Mozilla/5.0"
        
        # Act
        tracker = EmailTracker()
        result = tracker.track_click(message_id, link_url, user_agent)
        
        # Assert
        assert result.success is True
        assert result.event_type == "click"
        assert result.link_url == link_url

    def test_handle_bounce(self, email_service):
        """Test handling email bounces."""
        # Arrange
        bounce_data = {
            "message_id": "msg_123456",
            "recipient": "invalid@example.com",
            "bounce_type": "hard",
            "bounce_reason": "Mailbox does not exist",
            "timestamp": datetime.now(UTC)
        }
        
        # Act
        handler = BounceHandler()
        result = handler.process_bounce(bounce_data)
        
        # Assert
        assert result.processed is True
        assert result.action == "suppress_recipient"
        assert result.bounce_type == "hard"

    def test_handle_soft_bounce(self, email_service):
        """Test handling soft bounces."""
        # Arrange
        bounce_data = {
            "message_id": "msg_789012",
            "recipient": "user@example.com",
            "bounce_type": "soft",
            "bounce_reason": "Mailbox full",
            "attempt_count": 2
        }
        
        # Act
        handler = BounceHandler()
        result = handler.process_bounce(bounce_data)
        
        # Assert
        assert result.processed is True
        assert result.action == "retry_later"
        assert result.retry_after is not None

    def test_unsubscribe_user(self, email_service):
        """Test unsubscribing a user."""
        # Arrange
        email = "user@example.com"
        reason = "No longer interested"
        
        # Act
        manager = UnsubscribeManager()
        result = manager.unsubscribe(email, reason)
        
        # Assert
        assert result.success is True
        assert result.email == email
        assert result.unsubscribed_at is not None

    def test_check_subscription_status(self, email_service):
        """Test checking subscription status."""
        # Arrange
        subscribed_email = "active@example.com"
        unsubscribed_email = "inactive@example.com"
        
        # Act
        manager = UnsubscribeManager()
        with patch.object(manager, '_get_status') as mock_status:
            mock_status.side_effect = [True, False]
            is_subscribed = manager.is_subscribed(subscribed_email)
            is_unsubscribed = manager.is_subscribed(unsubscribed_email)
        
        # Assert
        assert is_subscribed is True
        assert is_unsubscribed is False

    def test_resubscribe_user(self, email_service):
        """Test resubscribing a user."""
        # Arrange
        email = "user@example.com"
        
        # Act
        manager = UnsubscribeManager()
        result = manager.resubscribe(email)
        
        # Assert
        assert result.success is True
        assert result.resubscribed_at is not None

    def test_email_queue_management(self, email_service):
        """Test email queue management."""
        # Arrange
        emails = [
            {"to": "user1@example.com", "priority": "high"},
            {"to": "user2@example.com", "priority": "low"},
            {"to": "user3@example.com", "priority": "normal"}
        ]
        
        # Act
        for email in emails:
            email_service.queue_email(email)
        
        next_email = email_service.get_next_queued_email()
        
        # Assert
        assert next_email["priority"] == "high"
        assert next_email["to"] == "user1@example.com"

    @pytest.mark.asyncio
    async def test_email_retry_logic(self, email_service, sample_email):
        """Test email retry logic for failed sends."""
        # Arrange
        max_retries = 3
        
        # Act
        with patch.object(email_service, '_send_raw') as mock_send:
            mock_send.side_effect = [Exception("Failed"), Exception("Failed"), True]
            result = await email_service.send_with_retry(sample_email, max_retries)
        
        # Assert
        assert result.success is True
        assert result.retry_count == 2
        assert mock_send.call_count == 3

    def test_email_template_rendering(self, email_service):
        """Test email template rendering with complex variables."""
        # Arrange
        template = EmailTemplate(
            id="order_confirmation",
            subject="Order #{{order_id}} Confirmed",
            body_html="""
            <h1>Thank you, {{customer.name}}!</h1>
            <p>Your order total: ${{order.total}}</p>
            <ul>
            {% for item in order.items %}
                <li>{{item.name}} - ${{item.price}}</li>
            {% endfor %}
            </ul>
            """
        )
        variables = {
            "order_id": "12345",
            "customer": {"name": "John Doe"},
            "order": {
                "total": "99.99",
                "items": [
                    {"name": "Product A", "price": "49.99"},
                    {"name": "Product B", "price": "50.00"}
                ]
            }
        }
        
        # Act
        rendered = email_service.render_template(template, variables)
        
        # Assert
        assert "12345" in rendered.subject
        assert "John Doe" in rendered.body
        assert "99.99" in rendered.body
        assert "Product A" in rendered.body

    def test_email_analytics(self, email_service):
        """Test email campaign analytics."""
        # Arrange
        campaign_id = "campaign_123"
        
        # Act
        with patch.object(email_service, '_get_campaign_stats') as mock_stats:
            mock_stats.return_value = {
                "sent": 1000,
                "delivered": 950,
                "opened": 400,
                "clicked": 150,
                "bounced": 50,
                "unsubscribed": 5
            }
            analytics = email_service.get_campaign_analytics(campaign_id)
        
        # Assert
        assert analytics.delivery_rate == 0.95
        assert analytics.open_rate == 0.42  # 400/950
        assert analytics.click_rate == 0.16  # 150/950
        assert analytics.bounce_rate == 0.05

    def test_email_personalization(self, email_service):
        """Test email personalization based on user data."""
        # Arrange
        user_data = {
            "name": "Jane",
            "company": "TechCorp",
            "role": "CTO",
            "interests": ["compliance", "security"],
            "last_login": datetime.now(UTC) - timedelta(days=5)
        }
        
        # Act
        personalized_content = email_service.personalize_email(
            template_id="weekly_digest",
            user_data=user_data
        )
        
        # Assert
        assert user_data["name"] in personalized_content.greeting
        assert "compliance" in personalized_content.recommended_content
        assert personalized_content.urgency == "re-engage"  # Due to 5 days inactive

    def test_spam_score_check(self, email_service, sample_email):
        """Test checking email spam score."""
        # Act
        with patch('services.email_service.spamassassin_client') as mock_spam:
            mock_spam.check.return_value = {"score": 2.5, "is_spam": False}
            result = email_service.check_spam_score(sample_email)
        
        # Assert
        assert result.score == 2.5
        assert result.is_spam is False
        assert result.can_send is True

    def test_email_scheduling(self, email_service, sample_email):
        """Test scheduling emails for future delivery."""
        # Arrange
        send_time = datetime.now(UTC) + timedelta(hours=24)
        
        # Act
        result = email_service.schedule_email(sample_email, send_time)
        
        # Assert
        assert result.scheduled_id is not None
        assert result.scheduled_time == send_time
        assert result.status == "scheduled"