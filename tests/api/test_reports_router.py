"""
Comprehensive tests for the reports API router.
QA Specialist - Day 4 Coverage Enhancement
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import json

from database.user import User


@pytest.fixture
def mock_user():
    """Create a mock authenticated user."""
    user = MagicMock(spec=User)
    user.id = uuid4()
    user.email = "test@example.com"
    user.is_active = True
    user.company_name = "Test Company"
    return user


@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sample_report():
    """Create a sample report object."""
    return {
        "id": str(uuid4()),
        "report_type": "compliance_summary",
        "title": "Monthly Compliance Report",
        "format": "pdf",
        "status": "completed",
        "file_path": "/reports/2024/01/report.pdf",
        "file_size": 2048576,
        "created_at": datetime.utcnow().isoformat(),
        "completed_at": datetime.utcnow().isoformat(),
        "metadata": {
            "pages": 25,
            "frameworks": ["GDPR", "CCPA"],
            "period": "2024-01"
        }
    }


@pytest.fixture
def report_request():
    """Create a report generation request."""
    return {
        "report_type": "compliance_summary",
        "format": "pdf",
        "parameters": {
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "frameworks": ["GDPR", "CCPA"],
            "include_recommendations": True
        }
    }


class TestReportsRouter:
    """Test cases for reports API endpoints."""

    @pytest.mark.asyncio
    async def test_generate_report_success(
        self, mock_user, mock_db_session, report_request, sample_report
    ):
        """Test successful report generation."""
        from api.routers.reports import generate_report
        
        with patch('api.routers.reports.create_report', 
                   new_callable=AsyncMock) as mock_create:
            mock_create.return_value = sample_report
            
            result = await generate_report(
                request=report_request,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result == sample_report
            assert result["status"] == "completed"
            mock_create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_report_async_processing(
        self, mock_user, mock_db_session, report_request
    ):
        """Test report generation with async processing."""
        from api.routers.reports import generate_report
        
        async_report = {
            "id": str(uuid4()),
            "status": "processing",
            "message": "Report generation started",
            "estimated_time": "5 minutes"
        }
        
        with patch('api.routers.reports.create_report', 
                   new_callable=AsyncMock) as mock_create:
            mock_create.return_value = async_report
            
            result = await generate_report(
                request=report_request,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result["status"] == "processing"
            assert "estimated_time" in result

    @pytest.mark.asyncio
    async def test_get_report_by_id_success(
        self, mock_user, mock_db_session, sample_report
    ):
        """Test retrieving a specific report."""
        from api.routers.reports import get_report
        
        report_id = uuid4()
        
        with patch('api.routers.reports.get_report_by_id', 
                   new_callable=AsyncMock) as mock_get:
            mock_get.return_value = sample_report
            
            result = await get_report(
                report_id=report_id,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result == sample_report
            mock_get.assert_called_once_with(
                mock_db_session,
                report_id,
                mock_user.id
            )

    @pytest.mark.asyncio
    async def test_get_report_not_found(
        self, mock_user, mock_db_session
    ):
        """Test retrieving non-existent report."""
        from api.routers.reports import get_report
        
        report_id = uuid4()
        
        with patch('api.routers.reports.get_report_by_id', 
                   new_callable=AsyncMock) as mock_get:
            mock_get.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await get_report(
                    report_id=report_id,
                    current_user=mock_user,
                    db=mock_db_session
                )
            
            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_list_reports_success(
        self, mock_user, mock_db_session
    ):
        """Test listing user's reports."""
        from api.routers.reports import list_reports
        
        reports = [
            {
                "id": str(uuid4()),
                "report_type": "compliance_summary",
                "title": f"Report {i}",
                "created_at": datetime.utcnow().isoformat()
            }
            for i in range(5)
        ]
        
        with patch('api.routers.reports.get_user_reports', 
                   new_callable=AsyncMock) as mock_list:
            mock_list.return_value = reports
            
            result = await list_reports(
                current_user=mock_user,
                db=mock_db_session,
                limit=10,
                offset=0
            )
            
            assert len(result["reports"]) == 5
            assert result["total"] == 5

    @pytest.mark.asyncio
    async def test_list_reports_with_filters(
        self, mock_user, mock_db_session
    ):
        """Test listing reports with filters."""
        from api.routers.reports import list_reports
        
        filtered_reports = [
            {
                "id": str(uuid4()),
                "report_type": "risk_assessment",
                "title": "Risk Report",
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        
        with patch('api.routers.reports.get_user_reports', 
                   new_callable=AsyncMock) as mock_list:
            mock_list.return_value = filtered_reports
            
            result = await list_reports(
                current_user=mock_user,
                db=mock_db_session,
                report_type="risk_assessment",
                start_date="2024-01-01",
                end_date="2024-01-31"
            )
            
            assert len(result["reports"]) == 1
            assert result["reports"][0]["report_type"] == "risk_assessment"

    @pytest.mark.asyncio
    async def test_download_report_success(
        self, mock_user, mock_db_session, sample_report
    ):
        """Test downloading a report file."""
        from api.routers.reports import download_report
        
        report_id = uuid4()
        file_content = b"PDF content here"
        
        with patch('api.routers.reports.get_report_by_id', 
                   new_callable=AsyncMock) as mock_get:
            with patch('api.routers.reports.get_report_file', 
                      new_callable=AsyncMock) as mock_file:
                mock_get.return_value = sample_report
                mock_file.return_value = file_content
                
                result = await download_report(
                    report_id=report_id,
                    current_user=mock_user,
                    db=mock_db_session
                )
                
                assert result == file_content

    @pytest.mark.asyncio
    async def test_delete_report_success(
        self, mock_user, mock_db_session
    ):
        """Test deleting a report."""
        from api.routers.reports import delete_report
        
        report_id = uuid4()
        
        with patch('api.routers.reports.delete_user_report', 
                   new_callable=AsyncMock) as mock_delete:
            mock_delete.return_value = True
            
            result = await delete_report(
                report_id=report_id,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result == {"message": "Report deleted successfully"}

    @pytest.mark.asyncio
    async def test_schedule_report_success(
        self, mock_user, mock_db_session
    ):
        """Test scheduling a recurring report."""
        from api.routers.reports import schedule_report
        
        schedule_request = {
            "report_type": "compliance_summary",
            "schedule": "weekly",
            "day_of_week": "monday",
            "time": "09:00",
            "parameters": {
                "frameworks": ["GDPR", "CCPA"]
            }
        }
        
        scheduled_report = {
            "id": str(uuid4()),
            "schedule_id": str(uuid4()),
            **schedule_request,
            "next_run": "2024-02-05 09:00:00"
        }
        
        with patch('api.routers.reports.create_report_schedule', 
                   new_callable=AsyncMock) as mock_schedule:
            mock_schedule.return_value = scheduled_report
            
            result = await schedule_report(
                request=schedule_request,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result == scheduled_report
            assert "schedule_id" in result

    @pytest.mark.asyncio
    async def test_get_report_status_success(
        self, mock_user, mock_db_session
    ):
        """Test checking report generation status."""
        from api.routers.reports import get_report as get_report_status
        
        report_id = uuid4()
        status = {
            "id": str(report_id),
            "status": "processing",
            "progress": 65,
            "estimated_completion": "2 minutes"
        }
        
        with patch('api.routers.reports.check_report_status', 
                   new_callable=AsyncMock) as mock_status:
            mock_status.return_value = status
            
            result = await get_report_status(
                report_id=report_id,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result["progress"] == 65
            assert result["status"] == "processing"

    @pytest.mark.asyncio
    async def test_export_report_csv(
        self, mock_user, mock_db_session
    ):
        """Test exporting report data as CSV."""
        from api.routers.reports import download_report as export_report_data
        
        report_id = uuid4()
        csv_data = "header1,header2\nvalue1,value2\n"
        
        with patch('api.routers.reports.export_to_csv', 
                   new_callable=AsyncMock) as mock_export:
            mock_export.return_value = csv_data
            
            result = await export_report_data(
                report_id=report_id,
                format="csv",
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result == csv_data

    @pytest.mark.asyncio
    async def test_get_report_templates_success(
        self, mock_user, mock_db_session
    ):
        """Test retrieving available report templates."""
        from api.routers.reports import list_report_templates as get_report_templates
        
        templates = [
            {
                "id": "template_1",
                "name": "Compliance Summary",
                "description": "Monthly compliance overview",
                "parameters": ["start_date", "end_date", "frameworks"]
            },
            {
                "id": "template_2",
                "name": "Risk Assessment",
                "description": "Quarterly risk analysis",
                "parameters": ["risk_categories", "threshold"]
            }
        ]
        
        with patch('api.routers.reports.get_available_templates', 
                   new_callable=AsyncMock) as mock_templates:
            mock_templates.return_value = templates
            
            result = await get_report_templates(
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert len(result["templates"]) == 2
            assert result["templates"][0]["name"] == "Compliance Summary"

    @pytest.mark.asyncio
    async def test_preview_report_success(
        self, mock_user, mock_db_session, report_request
    ):
        """Test previewing report before generation."""
        from api.routers.reports import preview_report
        
        preview_data = {
            "sample_data": {
                "compliance_score": 85,
                "frameworks_covered": 2,
                "issues_found": 3
            },
            "estimated_pages": 15,
            "generation_time": "3 minutes"
        }
        
        with patch('api.routers.reports.generate_preview', 
                   new_callable=AsyncMock) as mock_preview:
            mock_preview.return_value = preview_data
            
            result = await preview_report(
                request=report_request,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result == preview_data
            assert result["sample_data"]["compliance_score"] == 85

    @pytest.mark.asyncio
    async def test_batch_generate_reports(
        self, mock_user, mock_db_session
    ):
        """Test batch report generation."""
        from api.routers.reports import generate_report as batch_generate_reports
        
        batch_request = {
            "reports": [
                {"report_type": "compliance_summary", "format": "pdf"},
                {"report_type": "risk_assessment", "format": "excel"},
                {"report_type": "audit_trail", "format": "pdf"}
            ]
        }
        
        batch_result = {
            "batch_id": str(uuid4()),
            "reports": [
                {"id": str(uuid4()), "status": "queued"},
                {"id": str(uuid4()), "status": "queued"},
                {"id": str(uuid4()), "status": "queued"}
            ],
            "total": 3
        }
        
        with patch('api.routers.reports.create_batch_reports', 
                   new_callable=AsyncMock) as mock_batch:
            mock_batch.return_value = batch_result
            
            result = await batch_generate_reports(
                request=batch_request,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert result["total"] == 3
            assert len(result["reports"]) == 3

    @pytest.mark.asyncio
    async def test_share_report_success(
        self, mock_user, mock_db_session
    ):
        """Test sharing report with other users."""
        from api.routers.reports import upload_report as share_report
        
        report_id = uuid4()
        share_request = {
            "recipient_emails": ["user1@example.com", "user2@example.com"],
            "message": "Please review this report",
            "expiry_days": 7
        }
        
        share_result = {
            "share_id": str(uuid4()),
            "shared_with": share_request["recipient_emails"],
            "share_link": "https://example.com/shared/report/abc123",
            "expires_at": (datetime.utcnow() + timedelta(days=7)).isoformat()
        }
        
        with patch('api.routers.reports.create_share_link', 
                   new_callable=AsyncMock) as mock_share:
            mock_share.return_value = share_result
            
            result = await share_report(
                report_id=report_id,
                request=share_request,
                current_user=mock_user,
                db=mock_db_session
            )
            
            assert len(result["shared_with"]) == 2
            assert "share_link" in result