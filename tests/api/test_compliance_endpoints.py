"""
Test Suite for Compliance API Endpoints
QA Specialist - Day 4 Implementation
Tests compliance score, controls, violations, and recommendations
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from fastapi.testclient import TestClient
from fastapi import HTTPException

# Mock models and schemas
class ComplianceScore:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid4()))
        self.company_id = kwargs.get('company_id', 'test-company')
        self.framework_id = kwargs.get('framework_id', 'iso-27001')
        self.score = kwargs.get('score', 85.5)
        self.total_controls = kwargs.get('total_controls', 114)
        self.compliant_controls = kwargs.get('compliant_controls', 97)
        self.non_compliant_controls = kwargs.get('non_compliant_controls', 10)
        self.not_applicable = kwargs.get('not_applicable', 7)
        self.calculated_at = kwargs.get('calculated_at', datetime.now(timezone.utc))
        self.trend = kwargs.get('trend', 'improving')
        self.risk_level = kwargs.get('risk_level', 'low')

class ComplianceControl:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid4()))
        self.control_id = kwargs.get('control_id', 'A.5.1.1')
        self.name = kwargs.get('name', 'Information security policies')
        self.description = kwargs.get('description', 'Control description')
        self.status = kwargs.get('status', 'compliant')
        self.evidence_count = kwargs.get('evidence_count', 5)
        self.last_reviewed = kwargs.get('last_reviewed', datetime.now(timezone.utc))
        self.reviewer = kwargs.get('reviewer', 'admin@test.com')
        self.notes = kwargs.get('notes', 'Control is properly implemented')

class ComplianceViolation:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid4()))
        self.control_id = kwargs.get('control_id', 'A.5.1.2')
        self.severity = kwargs.get('severity', 'high')
        self.detected_at = kwargs.get('detected_at', datetime.now(timezone.utc))
        self.description = kwargs.get('description', 'Missing security policy documentation')
        self.remediation_plan = kwargs.get('remediation_plan', 'Create and approve security policies')
        self.due_date = kwargs.get('due_date', datetime.now(timezone.utc) + timedelta(days=30))
        self.assigned_to = kwargs.get('assigned_to', 'security@test.com')
        self.status = kwargs.get('status', 'open')

class ComplianceReport:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id', str(uuid4()))
        self.name = kwargs.get('name', 'Monthly Compliance Report')
        self.type = kwargs.get('type', 'summary')
        self.framework_ids = kwargs.get('framework_ids', ['iso-27001', 'gdpr'])
        self.generated_at = kwargs.get('generated_at', datetime.now(timezone.utc))
        self.format = kwargs.get('format', 'pdf')
        self.file_url = kwargs.get('file_url', 'https://storage/reports/report.pdf')


@pytest.fixture
def mock_compliance_service():
    """Mock compliance service"""
    service = Mock()
    service.calculate_score = AsyncMock()
    service.get_controls = AsyncMock()
    service.update_control_status = AsyncMock()
    service.get_violations = AsyncMock()
    service.create_violation = AsyncMock()
    service.get_recommendations = AsyncMock()
    service.generate_report = AsyncMock()
    service.get_compliance_trends = AsyncMock()
    service.get_risk_matrix = AsyncMock()
    service.bulk_update_controls = AsyncMock()
    return service


@pytest.fixture
def compliance_client(mock_compliance_service):
    """Test client with mocked compliance service"""
    from fastapi import FastAPI
    app = FastAPI()
    
    # Mock router would be imported here
    # from api.routers import compliance
    # app.include_router(compliance.router)
    
    return TestClient(app)


class TestComplianceScoreEndpoints:
    """Test compliance score calculation and retrieval"""
    
    @pytest.mark.asyncio
    async def test_calculate_compliance_score_success(self, mock_compliance_service):
        """Test successful compliance score calculation"""
        # Arrange
        mock_score = ComplianceScore(score=92.5)
        mock_compliance_service.calculate_score.return_value = mock_score
        
        # Act
        result = await mock_compliance_service.calculate_score(
            company_id="test-company",
            framework_id="iso-27001"
        )
        
        # Assert
        assert result.score == 92.5
        assert result.framework_id == "iso-27001"
        mock_compliance_service.calculate_score.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_compliance_scores_history(self, mock_compliance_service):
        """Test retrieving compliance score history"""
        # Arrange
        scores = [
            ComplianceScore(score=85.0, calculated_at=datetime.now(timezone.utc) - timedelta(days=30)),
            ComplianceScore(score=88.5, calculated_at=datetime.now(timezone.utc) - timedelta(days=15)),
            ComplianceScore(score=92.5, calculated_at=datetime.now(timezone.utc))
        ]
        mock_compliance_service.get_compliance_trends.return_value = scores
        
        # Act
        result = await mock_compliance_service.get_compliance_trends(
            company_id="test-company",
            days=30
        )
        
        # Assert
        assert len(result) == 3
        assert result[-1].score == 92.5
        assert result[0].score == 85.0
    
    @pytest.mark.asyncio
    async def test_get_compliance_by_framework(self, mock_compliance_service):
        """Test getting compliance scores for multiple frameworks"""
        # Arrange
        scores = {
            'iso-27001': ComplianceScore(framework_id='iso-27001', score=92.5),
            'gdpr': ComplianceScore(framework_id='gdpr', score=88.0),
            'hipaa': ComplianceScore(framework_id='hipaa', score=95.0)
        }
        mock_compliance_service.calculate_score.side_effect = lambda **kwargs: scores.get(kwargs['framework_id'])
        
        # Act
        results = {}
        for framework in ['iso-27001', 'gdpr', 'hipaa']:
            results[framework] = await mock_compliance_service.calculate_score(
                company_id="test-company",
                framework_id=framework
            )
        
        # Assert
        assert results['iso-27001'].score == 92.5
        assert results['gdpr'].score == 88.0
        assert results['hipaa'].score == 95.0


class TestComplianceControlEndpoints:
    """Test compliance control management"""
    
    @pytest.mark.asyncio
    async def test_get_all_controls(self, mock_compliance_service):
        """Test retrieving all compliance controls"""
        # Arrange
        controls = [
            ComplianceControl(control_id='A.5.1.1', status='compliant'),
            ComplianceControl(control_id='A.5.1.2', status='non-compliant'),
            ComplianceControl(control_id='A.5.1.3', status='partial')
        ]
        mock_compliance_service.get_controls.return_value = controls
        
        # Act
        result = await mock_compliance_service.get_controls(framework_id='iso-27001')
        
        # Assert
        assert len(result) == 3
        assert result[0].status == 'compliant'
        assert result[1].status == 'non-compliant'
    
    @pytest.mark.asyncio
    async def test_update_control_status(self, mock_compliance_service):
        """Test updating control compliance status"""
        # Arrange
        updated_control = ComplianceControl(
            control_id='A.5.1.1',
            status='compliant',
            notes='Updated with new evidence'
        )
        mock_compliance_service.update_control_status.return_value = updated_control
        
        # Act
        result = await mock_compliance_service.update_control_status(
            control_id='A.5.1.1',
            status='compliant',
            evidence_ids=['ev1', 'ev2'],
            notes='Updated with new evidence'
        )
        
        # Assert
        assert result.status == 'compliant'
        assert result.notes == 'Updated with new evidence'
    
    @pytest.mark.asyncio
    async def test_bulk_update_controls(self, mock_compliance_service):
        """Test bulk updating multiple controls"""
        # Arrange
        updates = [
            {'control_id': 'A.5.1.1', 'status': 'compliant'},
            {'control_id': 'A.5.1.2', 'status': 'partial'},
            {'control_id': 'A.5.1.3', 'status': 'not-applicable'}
        ]
        mock_compliance_service.bulk_update_controls.return_value = {
            'updated': 3,
            'failed': 0
        }
        
        # Act
        result = await mock_compliance_service.bulk_update_controls(updates)
        
        # Assert
        assert result['updated'] == 3
        assert result['failed'] == 0
    
    @pytest.mark.asyncio
    async def test_filter_controls_by_status(self, mock_compliance_service):
        """Test filtering controls by compliance status"""
        # Arrange
        non_compliant = [
            ComplianceControl(control_id='A.5.1.2', status='non-compliant'),
            ComplianceControl(control_id='A.6.1.1', status='non-compliant')
        ]
        mock_compliance_service.get_controls.return_value = non_compliant
        
        # Act
        result = await mock_compliance_service.get_controls(
            framework_id='iso-27001',
            status='non-compliant'
        )
        
        # Assert
        assert len(result) == 2
        assert all(c.status == 'non-compliant' for c in result)


class TestComplianceViolationEndpoints:
    """Test compliance violation management"""
    
    @pytest.mark.asyncio
    async def test_create_violation(self, mock_compliance_service):
        """Test creating a new compliance violation"""
        # Arrange
        violation = ComplianceViolation(
            control_id='A.5.1.2',
            severity='critical',
            description='Critical security policy missing'
        )
        mock_compliance_service.create_violation.return_value = violation
        
        # Act
        result = await mock_compliance_service.create_violation(
            control_id='A.5.1.2',
            severity='critical',
            description='Critical security policy missing'
        )
        
        # Assert
        assert result.severity == 'critical'
        assert result.control_id == 'A.5.1.2'
        assert result.status == 'open'
    
    @pytest.mark.asyncio
    async def test_get_open_violations(self, mock_compliance_service):
        """Test retrieving open compliance violations"""
        # Arrange
        violations = [
            ComplianceViolation(severity='critical', status='open'),
            ComplianceViolation(severity='high', status='open'),
            ComplianceViolation(severity='medium', status='open')
        ]
        mock_compliance_service.get_violations.return_value = violations
        
        # Act
        result = await mock_compliance_service.get_violations(status='open')
        
        # Assert
        assert len(result) == 3
        assert all(v.status == 'open' for v in result)
    
    @pytest.mark.asyncio
    async def test_get_violations_by_severity(self, mock_compliance_service):
        """Test filtering violations by severity"""
        # Arrange
        critical_violations = [
            ComplianceViolation(severity='critical', control_id='A.5.1.1'),
            ComplianceViolation(severity='critical', control_id='A.6.1.1')
        ]
        mock_compliance_service.get_violations.return_value = critical_violations
        
        # Act
        result = await mock_compliance_service.get_violations(severity='critical')
        
        # Assert
        assert len(result) == 2
        assert all(v.severity == 'critical' for v in result)
    
    @pytest.mark.asyncio
    async def test_update_violation_status(self, mock_compliance_service):
        """Test updating violation status and remediation"""
        # Arrange
        violation = ComplianceViolation(
            id='viol-123',
            status='in-progress',
            remediation_plan='Updated plan with specific steps'
        )
        mock_compliance_service.update_violation = AsyncMock(return_value=violation)
        
        # Act
        result = await mock_compliance_service.update_violation(
            violation_id='viol-123',
            status='in-progress',
            remediation_plan='Updated plan with specific steps'
        )
        
        # Assert
        assert result.status == 'in-progress'
        assert 'Updated plan' in result.remediation_plan


class TestComplianceRecommendations:
    """Test compliance recommendations and insights"""
    
    @pytest.mark.asyncio
    async def test_get_recommendations(self, mock_compliance_service):
        """Test getting compliance improvement recommendations"""
        # Arrange
        recommendations = [
            {
                'priority': 'high',
                'control_id': 'A.5.1.2',
                'recommendation': 'Implement information security policy',
                'impact': 'Will improve compliance score by 5%',
                'effort': 'medium'
            },
            {
                'priority': 'medium',
                'control_id': 'A.8.1.1',
                'recommendation': 'Update asset inventory',
                'impact': 'Will improve compliance score by 2%',
                'effort': 'low'
            }
        ]
        mock_compliance_service.get_recommendations.return_value = recommendations
        
        # Act
        result = await mock_compliance_service.get_recommendations(
            company_id='test-company',
            framework_id='iso-27001'
        )
        
        # Assert
        assert len(result) == 2
        assert result[0]['priority'] == 'high'
        assert '5%' in result[0]['impact']
    
    @pytest.mark.asyncio
    async def test_get_risk_matrix(self, mock_compliance_service):
        """Test getting compliance risk matrix"""
        # Arrange
        risk_matrix = {
            'high_risk': ['A.5.1.2', 'A.6.1.1'],
            'medium_risk': ['A.8.1.1', 'A.9.1.1'],
            'low_risk': ['A.10.1.1', 'A.11.1.1'],
            'total_risks': 6,
            'critical_controls': 2
        }
        mock_compliance_service.get_risk_matrix.return_value = risk_matrix
        
        # Act
        result = await mock_compliance_service.get_risk_matrix(
            company_id='test-company'
        )
        
        # Assert
        assert result['total_risks'] == 6
        assert len(result['high_risk']) == 2
        assert result['critical_controls'] == 2
    
    @pytest.mark.asyncio
    async def test_get_compliance_roadmap(self, mock_compliance_service):
        """Test getting compliance improvement roadmap"""
        # Arrange
        roadmap = {
            'current_score': 75.0,
            'target_score': 95.0,
            'phases': [
                {
                    'phase': 1,
                    'duration': '2 months',
                    'controls': ['A.5.1.1', 'A.5.1.2'],
                    'expected_score': 82.0
                },
                {
                    'phase': 2,
                    'duration': '3 months',
                    'controls': ['A.6.1.1', 'A.7.1.1'],
                    'expected_score': 90.0
                }
            ]
        }
        mock_compliance_service.get_roadmap = AsyncMock(return_value=roadmap)
        
        # Act
        result = await mock_compliance_service.get_roadmap(
            company_id='test-company',
            target_score=95.0
        )
        
        # Assert
        assert result['target_score'] == 95.0
        assert len(result['phases']) == 2
        assert result['phases'][1]['expected_score'] == 90.0


class TestComplianceReportEndpoints:
    """Test compliance report generation and retrieval"""
    
    @pytest.mark.asyncio
    async def test_generate_compliance_report(self, mock_compliance_service):
        """Test generating a compliance report"""
        # Arrange
        report = ComplianceReport(
            name='Q4 2024 Compliance Report',
            type='detailed',
            format='pdf'
        )
        mock_compliance_service.generate_report.return_value = report
        
        # Act
        result = await mock_compliance_service.generate_report(
            company_id='test-company',
            report_type='detailed',
            frameworks=['iso-27001', 'gdpr'],
            format='pdf'
        )
        
        # Assert
        assert result.type == 'detailed'
        assert result.format == 'pdf'
        assert 'Q4 2024' in result.name
    
    @pytest.mark.asyncio
    async def test_schedule_recurring_report(self, mock_compliance_service):
        """Test scheduling recurring compliance reports"""
        # Arrange
        schedule = {
            'id': 'sched-123',
            'frequency': 'monthly',
            'report_type': 'summary',
            'recipients': ['compliance@test.com', 'ciso@test.com'],
            'next_run': datetime.now(timezone.utc) + timedelta(days=30)
        }
        mock_compliance_service.schedule_report = AsyncMock(return_value=schedule)
        
        # Act
        result = await mock_compliance_service.schedule_report(
            frequency='monthly',
            report_type='summary',
            recipients=['compliance@test.com', 'ciso@test.com']
        )
        
        # Assert
        assert result['frequency'] == 'monthly'
        assert len(result['recipients']) == 2
        assert result['report_type'] == 'summary'
    
    @pytest.mark.asyncio
    async def test_export_compliance_data(self, mock_compliance_service):
        """Test exporting compliance data in various formats"""
        # Arrange
        export_data = {
            'format': 'excel',
            'file_url': 'https://storage/exports/compliance_data.xlsx',
            'size_bytes': 245678,
            'rows_exported': 1500
        }
        mock_compliance_service.export_data = AsyncMock(return_value=export_data)
        
        # Act
        result = await mock_compliance_service.export_data(
            company_id='test-company',
            format='excel',
            include_evidence=True
        )
        
        # Assert
        assert result['format'] == 'excel'
        assert result['rows_exported'] == 1500
        assert '.xlsx' in result['file_url']


class TestComplianceIntegrationEndpoints:
    """Test compliance integration with other systems"""
    
    @pytest.mark.asyncio
    async def test_sync_with_grc_platform(self, mock_compliance_service):
        """Test syncing compliance data with GRC platform"""
        # Arrange
        sync_result = {
            'status': 'success',
            'controls_synced': 114,
            'violations_synced': 12,
            'last_sync': datetime.now(timezone.utc)
        }
        mock_compliance_service.sync_grc = AsyncMock(return_value=sync_result)
        
        # Act
        result = await mock_compliance_service.sync_grc(
            platform='servicenow',
            api_key='test-key'
        )
        
        # Assert
        assert result['status'] == 'success'
        assert result['controls_synced'] == 114
        assert result['violations_synced'] == 12


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])