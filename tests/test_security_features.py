"""
Test security features including rate limiting, audit logging, and email alerts.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from services.rate_limiting import RateLimitService
from services.security_alerts import SecurityAlertService
from database.user import User
from database.rbac import AuditLog


@pytest.mark.asyncio
class TestRateLimiting:
    """Test AI feature rate limiting."""
    
    async def test_rate_limit_check_allowed(self):
        """Test rate limit check when usage is within limits."""
        # Create mock database session
        mock_db = AsyncMock(spec=AsyncSession)
        mock_user = MagicMock(spec=User)
        mock_user.id = uuid4()
        
        # Mock the query result to return 5 uses (under limit of 10)
        mock_result = MagicMock()
        mock_result.scalar.return_value = 5
        mock_db.execute.return_value = mock_result
        
        # Check rate limit
        result = await RateLimitService.check_rate_limit(
            db=mock_db,
            user=mock_user,
            feature="ai_assessment",
            check_only=True
        )
        
        assert result["allowed"] is True
        assert result["daily_limit"] == 10
        assert result["used_today"] == 5
        assert result["remaining"] == 5
    
    async def test_rate_limit_check_exceeded(self):
        """Test rate limit check when usage exceeds limits."""
        # Create mock database session
        mock_db = AsyncMock(spec=AsyncSession)
        mock_user = MagicMock(spec=User)
        mock_user.id = uuid4()
        
        # Mock the query result to return 10 uses (at limit)
        mock_result = MagicMock()
        mock_result.scalar.return_value = 10
        mock_db.execute.return_value = mock_result
        
        # Check rate limit - should raise exception unless check_only=True
        result = await RateLimitService.check_rate_limit(
            db=mock_db,
            user=mock_user,
            feature="ai_assessment",
            check_only=True
        )
        
        assert result["allowed"] is False
        assert result["daily_limit"] == 10
        assert result["used_today"] == 10
        assert result["remaining"] == 0
    
    async def test_rate_limit_exception_when_exceeded(self):
        """Test that rate limit raises HTTPException when exceeded and not check_only."""
        # Create mock database session
        mock_db = AsyncMock(spec=AsyncSession)
        mock_user = MagicMock(spec=User)
        mock_user.id = uuid4()
        
        # Mock the query results
        mock_count_result = MagicMock()
        mock_count_result.scalar.return_value = 11  # Over limit
        
        mock_oldest_result = MagicMock()
        mock_oldest_result.scalar.return_value = datetime.utcnow() - timedelta(hours=12)
        
        mock_db.execute.side_effect = [mock_count_result, mock_oldest_result]
        
        # Should raise HTTPException
        with pytest.raises(HTTPException) as exc_info:
            await RateLimitService.check_rate_limit(
                db=mock_db,
                user=mock_user,
                feature="ai_assessment",
                check_only=False
            )
        
        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in exc_info.value.detail["error"]


@pytest.mark.asyncio
class TestSecurityAlerts:
    """Test security alert functionality."""
    
    async def test_check_failed_logins_under_threshold(self):
        """Test failed login check when under threshold."""
        # Create mock database session
        mock_db = AsyncMock(spec=AsyncSession)
        mock_user = MagicMock(spec=User)
        mock_user.id = uuid4()
        
        # Mock query result - only 2 failed attempts (under threshold of 3)
        mock_result = MagicMock()
        mock_result.scalar.return_value = 2
        mock_db.execute.return_value = mock_result
        
        should_alert = await SecurityAlertService.check_failed_logins(
            db=mock_db,
            user=mock_user,
            ip_address="192.168.1.1"
        )
        
        assert should_alert is False
    
    async def test_check_failed_logins_exceeds_threshold(self):
        """Test failed login check when threshold is exceeded."""
        # Create mock database session
        mock_db = AsyncMock(spec=AsyncSession)
        mock_user = MagicMock(spec=User)
        mock_user.id = uuid4()
        
        # Mock query result - 3 failed attempts (at threshold)
        mock_result = MagicMock()
        mock_result.scalar.return_value = 3
        mock_db.execute.return_value = mock_result
        
        should_alert = await SecurityAlertService.check_failed_logins(
            db=mock_db,
            user=mock_user,
            ip_address="192.168.1.1"
        )
        
        assert should_alert is True
    
    @patch('services.security_alerts.aiosmtplib.send')
    @patch.dict('os.environ', {
        'SMTP_HOST': 'smtp.test.com',
        'SMTP_PORT': '587',
        'SMTP_USER': 'test@test.com',
        'SMTP_PASSWORD': 'testpass',
        'FRONTEND_URL': 'https://app.test.com'
    })
    async def test_send_failed_login_alert(self, mock_smtp_send):
        """Test sending failed login alert email."""
        mock_user = MagicMock(spec=User)
        mock_user.email = "user@test.com"
        
        # Mock SMTP send to complete successfully
        mock_smtp_send.return_value = None
        
        await SecurityAlertService.send_failed_login_alert(
            user=mock_user,
            failed_attempts=3,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        
        # Verify SMTP send was called
        mock_smtp_send.assert_called_once()
        
        # Check that the message was constructed correctly
        call_args = mock_smtp_send.call_args
        message = call_args[0][0]
        
        assert message["Subject"] == "Security Alert: Multiple Failed Login Attempts"
        assert message["To"] == "user@test.com"
    
    async def test_log_and_check_login_attempt_success(self):
        """Test logging successful login attempt."""
        # Create mock database session
        mock_db = AsyncMock(spec=AsyncSession)
        mock_user = MagicMock(spec=User)
        mock_user.id = uuid4()
        
        # Mock for adding audit log
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        
        await SecurityAlertService.log_and_check_login_attempt(
            db=mock_db,
            user=mock_user,
            success=True,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0"
        )
        
        # Verify audit log was added
        mock_db.add.assert_called_once()
        audit_log = mock_db.add.call_args[0][0]
        assert isinstance(audit_log, AuditLog)
        assert audit_log.action == "login_success"
        assert audit_log.severity == "info"
        assert audit_log.ip_address == "192.168.1.1"
    
    @patch('services.security_alerts.asyncio.create_task')
    async def test_log_and_check_login_attempt_failure_triggers_alert(self, mock_create_task):
        """Test that failed login attempt triggers alert when threshold exceeded."""
        # Create mock database session
        mock_db = AsyncMock(spec=AsyncSession)
        mock_user = MagicMock(spec=User)
        mock_user.id = uuid4()
        
        # Mock for adding audit log
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        
        # Mock check_failed_logins to return True (should send alert)
        # First execute for adding log, second for checking threshold, third for counting
        mock_result1 = MagicMock()
        mock_result1.scalar.return_value = 3  # At threshold
        
        mock_result2 = MagicMock()
        mock_result2.scalar.return_value = 3  # Total count
        
        mock_db.execute.side_effect = [mock_result1, mock_result2]
        
        # Patch check_failed_logins
        with patch.object(SecurityAlertService, 'check_failed_logins', return_value=True):
            await SecurityAlertService.log_and_check_login_attempt(
                db=mock_db,
                user=mock_user,
                success=False,
                ip_address="192.168.1.1",
                user_agent="Mozilla/5.0"
            )
        
        # Verify audit log was added for failed attempt
        mock_db.add.assert_called_once()
        audit_log = mock_db.add.call_args[0][0]
        assert audit_log.action == "login_failure"
        assert audit_log.severity == "warning"
        
        # Verify alert task was created
        mock_create_task.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])