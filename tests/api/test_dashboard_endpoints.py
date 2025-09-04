"""
Test suite for Dashboard API endpoints
P3 Task: Test Coverage Enhancement - Day 2
"""

import pytest
from datetime import datetime, UTC, timedelta
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.routers import dashboard
from api.schemas.models import (
    ComplianceStatusResponse as DashboardMetrics,
    ComplianceStatusResponse as ComplianceOverview, 
    AssessmentSessionResponse as AssessmentSummary,
    ComplianceStatusResponse as TrendData,
    ComplianceStatusResponse as RiskMatrix,
    ComplianceStatusResponse as ActivityFeed
)
from database import User


class TestDashboardEndpoints:
    """Test suite for dashboard and analytics endpoints"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        mock = AsyncMock(spec=AsyncSession)
        return mock
    
    @pytest.fixture
    def mock_user(self):
        """Mock authenticated user"""
        return User(
            id="test-user-123",
            email="test@example.com",
            is_active=True,
            organization_id="org-123",
            role="admin"
        )
    
    @pytest.mark.asyncio
    async def test_get_dashboard_metrics(self, mock_db, mock_user):
        """Test getting main dashboard metrics"""
        # Arrange
        with patch('api.routers.dashboard.get_dashboard_service') as mock_service:
            mock_service.return_value.get_metrics = AsyncMock(
                return_value={
                    "compliance_score": 0.85,
                    "total_assessments": 25,
                    "active_assessments": 5,
                    "completed_assessments": 20,
                    "total_policies": 15,
                    "approved_policies": 12,
                    "total_evidence": 150,
                    "validated_evidence": 120,
                    "open_gaps": 8,
                    "critical_risks": 2,
                    "upcoming_deadlines": 3
                }
            )
            
            # Act
            response = await dashboard.get_dashboard_metrics(
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["compliance_score"] == 0.85
            assert response["total_assessments"] == 25
            assert response["validated_evidence"] == 120
    
    @pytest.mark.asyncio
    async def test_get_compliance_overview(self, mock_db, mock_user):
        """Test getting compliance overview by framework"""
        # Arrange
        with patch('api.routers.dashboard.get_dashboard_service') as mock_service:
            mock_service.return_value.get_compliance_overview = AsyncMock(
                return_value={
                    "frameworks": [
                        {
                            "framework_id": "fw-iso27001",
                            "framework_name": "ISO 27001",
                            "compliance_score": 0.88,
                            "requirements_total": 114,
                            "requirements_met": 100,
                            "requirements_partial": 10,
                            "requirements_not_met": 4
                        },
                        {
                            "framework_id": "fw-gdpr",
                            "framework_name": "GDPR",
                            "compliance_score": 0.92,
                            "requirements_total": 99,
                            "requirements_met": 91,
                            "requirements_partial": 6,
                            "requirements_not_met": 2
                        }
                    ],
                    "overall_score": 0.90
                }
            )
            
            # Act
            response = await dashboard.get_compliance_overview(
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert len(response["frameworks"]) == 2
            assert response["overall_score"] == 0.90
            assert response["frameworks"][0]["compliance_score"] == 0.88
    
    @pytest.mark.asyncio
    async def test_get_assessment_summary(self, mock_db, mock_user):
        """Test getting assessment summary statistics"""
        # Arrange
        with patch('api.routers.dashboard.get_dashboard_service') as mock_service:
            mock_service.return_value.get_assessment_summary = AsyncMock(
                return_value={
                    "by_status": {
                        "draft": 2,
                        "in_progress": 5,
                        "under_review": 3,
                        "completed": 20
                    },
                    "by_type": {
                        "self_assessment": 15,
                        "external_audit": 10,
                        "gap_analysis": 5
                    },
                    "recent_assessments": [
                        {
                            "id": "assess-1",
                            "name": "Q4 Security Assessment",
                            "status": "completed",
                            "completion_date": "2024-01-15T10:00:00Z"
                        }
                    ],
                    "average_completion_time": 14.5  # days
                }
            )
            
            # Act
            response = await dashboard.get_assessment_summary(
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["by_status"]["completed"] == 20
            assert response["average_completion_time"] == 14.5
    
    @pytest.mark.asyncio
    async def test_get_trend_data(self, mock_db, mock_user):
        """Test getting trend data for charts"""
        # Arrange
        with patch('api.routers.dashboard.get_dashboard_service') as mock_service:
            mock_service.return_value.get_trend_data = AsyncMock(
                return_value={
                    "compliance_trend": [
                        {"date": "2024-01-01", "score": 0.75},
                        {"date": "2024-02-01", "score": 0.80},
                        {"date": "2024-03-01", "score": 0.85}
                    ],
                    "assessment_trend": [
                        {"date": "2024-01-01", "count": 5},
                        {"date": "2024-02-01", "count": 8},
                        {"date": "2024-03-01", "count": 12}
                    ],
                    "risk_trend": [
                        {"date": "2024-01-01", "high": 5, "medium": 10, "low": 15},
                        {"date": "2024-02-01", "high": 3, "medium": 8, "low": 20},
                        {"date": "2024-03-01", "high": 2, "medium": 6, "low": 25}
                    ]
                }
            )
            
            # Act
            response = await dashboard.get_trend_data(
                db=mock_db,
                current_user=mock_user,
                period="quarterly",
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2024, 3, 31)
            )
            
            # Assert
            assert len(response["compliance_trend"]) == 3
            assert response["compliance_trend"][-1]["score"] == 0.85
            assert response["risk_trend"][-1]["high"] == 2
    
    @pytest.mark.asyncio
    async def test_get_risk_matrix(self, mock_db, mock_user):
        """Test getting risk matrix data"""
        # Arrange
        with patch('api.routers.dashboard.get_dashboard_service') as mock_service:
            mock_service.return_value.get_risk_matrix = AsyncMock(
                return_value={
                    "matrix": [
                        {
                            "likelihood": "high",
                            "impact": "high",
                            "count": 2,
                            "risks": ["Data breach", "Compliance violation"]
                        },
                        {
                            "likelihood": "medium",
                            "impact": "high",
                            "count": 3,
                            "risks": ["System downtime", "Key person loss", "Vendor failure"]
                        },
                        {
                            "likelihood": "low",
                            "impact": "low",
                            "count": 10,
                            "risks": ["Minor incidents"]
                        }
                    ],
                    "total_risks": 15,
                    "critical_risks": 2,
                    "risk_appetite": "moderate"
                }
            )
            
            # Act
            response = await dashboard.get_risk_matrix(
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert response["total_risks"] == 15
            assert response["critical_risks"] == 2
            assert len(response["matrix"]) == 3
    
    @pytest.mark.asyncio
    async def test_get_activity_feed(self, mock_db, mock_user):
        """Test getting recent activity feed"""
        # Arrange
        with patch('api.routers.dashboard.get_dashboard_service') as mock_service:
            mock_service.return_value.get_activity_feed = AsyncMock(
                return_value={
                    "activities": [
                        {
                            "id": "act-1",
                            "type": "assessment_completed",
                            "title": "Security Assessment Completed",
                            "description": "Q4 2024 security assessment has been completed",
                            "user": "John Doe",
                            "timestamp": datetime.now(UTC).isoformat(),
                            "metadata": {"assessment_id": "assess-123"}
                        },
                        {
                            "id": "act-2",
                            "type": "policy_approved",
                            "title": "Policy Approved",
                            "description": "Data Protection Policy v2.0 approved",
                            "user": "Jane Smith",
                            "timestamp": (datetime.now(UTC) - timedelta(hours=2)).isoformat(),
                            "metadata": {"policy_id": "pol-456"}
                        }
                    ],
                    "total": 25,
                    "unread": 5
                }
            )
            
            # Act
            response = await dashboard.get_activity_feed(
                db=mock_db,
                current_user=mock_user,
                limit=10,
                offset=0
            )
            
            # Assert
            assert len(response["activities"]) == 2
            assert response["total"] == 25
            assert response["unread"] == 5
    
    @pytest.mark.asyncio
    async def test_get_upcoming_deadlines(self, mock_db, mock_user):
        """Test getting upcoming deadlines and tasks"""
        # Arrange
        with patch('api.routers.dashboard.get_dashboard_service') as mock_service:
            mock_service.return_value.get_upcoming_deadlines = AsyncMock(
                return_value={
                    "deadlines": [
                        {
                            "id": "deadline-1",
                            "title": "ISO 27001 Certification Renewal",
                            "due_date": (datetime.now(UTC) + timedelta(days=7)).isoformat(),
                            "priority": "high",
                            "type": "certification",
                            "days_remaining": 7
                        },
                        {
                            "id": "deadline-2",
                            "title": "Quarterly Security Review",
                            "due_date": (datetime.now(UTC) + timedelta(days=14)).isoformat(),
                            "priority": "medium",
                            "type": "assessment",
                            "days_remaining": 14
                        }
                    ],
                    "overdue": [
                        {
                            "id": "deadline-3",
                            "title": "Policy Review",
                            "due_date": (datetime.now(UTC) - timedelta(days=2)).isoformat(),
                            "priority": "high",
                            "days_overdue": 2
                        }
                    ]
                }
            )
            
            # Act
            response = await dashboard.get_upcoming_deadlines(
                db=mock_db,
                current_user=mock_user,
                days_ahead=30
            )
            
            # Assert
            assert len(response["deadlines"]) == 2
            assert len(response["overdue"]) == 1
            assert response["deadlines"][0]["days_remaining"] == 7
    
    @pytest.mark.asyncio
    async def test_get_team_performance(self, mock_db, mock_user):
        """Test getting team performance metrics"""
        # Arrange
        with patch('api.routers.dashboard.get_dashboard_service') as mock_service:
            mock_service.return_value.get_team_performance = AsyncMock(
                return_value={
                    "team_members": [
                        {
                            "user_id": "user-1",
                            "name": "John Doe",
                            "assessments_completed": 5,
                            "policies_reviewed": 3,
                            "evidence_validated": 25,
                            "average_completion_time": 2.5  # days
                        },
                        {
                            "user_id": "user-2",
                            "name": "Jane Smith",
                            "assessments_completed": 8,
                            "policies_reviewed": 5,
                            "evidence_validated": 40,
                            "average_completion_time": 1.8  # days
                        }
                    ],
                    "team_average_completion": 2.1,
                    "total_team_output": {
                        "assessments": 13,
                        "policies": 8,
                        "evidence": 65
                    }
                }
            )
            
            # Act
            response = await dashboard.get_team_performance(
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert len(response["team_members"]) == 2
            assert response["team_average_completion"] == 2.1
            assert response["total_team_output"]["assessments"] == 13
    
    @pytest.mark.asyncio
    async def test_export_dashboard_report(self, mock_db, mock_user):
        """Test exporting dashboard data as report"""
        # Arrange
        with patch('api.routers.dashboard.get_dashboard_service') as mock_service:
            mock_service.return_value.export_report = AsyncMock(
                return_value={
                    "format": "pdf",
                    "filename": "dashboard_report_2024_03.pdf",
                    "size": 2048000,
                    "download_url": "/api/reports/download/report-123"
                }
            )
            
            # Act
            response = await dashboard.export_dashboard_report(
                db=mock_db,
                current_user=mock_user,
                format="pdf",
                include_charts=True,
                period="monthly"
            )
            
            # Assert
            assert response["format"] == "pdf"
            assert "dashboard_report" in response["filename"]
    
    @pytest.mark.asyncio
    async def test_get_compliance_gaps(self, mock_db, mock_user):
        """Test getting compliance gaps analysis"""
        # Arrange
        with patch('api.routers.dashboard.get_dashboard_service') as mock_service:
            mock_service.return_value.get_compliance_gaps = AsyncMock(
                return_value={
                    "gaps": [
                        {
                            "requirement_id": "req-1",
                            "requirement_name": "Access Control Policy",
                            "framework": "ISO 27001",
                            "gap_type": "missing",
                            "priority": "high",
                            "remediation_effort": "medium"
                        },
                        {
                            "requirement_id": "req-2",
                            "requirement_name": "Data Encryption",
                            "framework": "GDPR",
                            "gap_type": "partial",
                            "priority": "critical",
                            "remediation_effort": "high"
                        }
                    ],
                    "total_gaps": 15,
                    "critical_gaps": 3,
                    "estimated_remediation_time": "45 days"
                }
            )
            
            # Act
            response = await dashboard.get_compliance_gaps(
                db=mock_db,
                current_user=mock_user,
                framework_id=None
            )
            
            # Assert
            assert len(response["gaps"]) == 2
            assert response["total_gaps"] == 15
            assert response["critical_gaps"] == 3
    
    @pytest.mark.asyncio
    async def test_get_ai_insights(self, mock_db, mock_user):
        """Test getting AI-generated insights"""
        # Arrange
        with patch('api.routers.dashboard.get_ai_service') as mock_ai_service:
            mock_ai_service.return_value.generate_insights = AsyncMock(
                return_value={
                    "insights": [
                        {
                            "type": "trend",
                            "title": "Improving Compliance Trend",
                            "description": "Compliance score has improved by 15% over the last quarter",
                            "confidence": 0.92,
                            "recommendations": ["Continue current practices", "Focus on remaining gaps"]
                        },
                        {
                            "type": "risk",
                            "title": "Potential Risk Area",
                            "description": "Access control policies need immediate attention",
                            "confidence": 0.88,
                            "recommendations": ["Review access logs", "Update user permissions"]
                        }
                    ],
                    "generated_at": datetime.now(UTC).isoformat()
                }
            )
            
            # Act
            response = await dashboard.get_ai_insights(
                db=mock_db,
                current_user=mock_user
            )
            
            # Assert
            assert len(response["insights"]) == 2
            assert response["insights"][0]["type"] == "trend"
            assert response["insights"][0]["confidence"] == 0.92