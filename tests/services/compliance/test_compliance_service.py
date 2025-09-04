"""
Comprehensive tests for compliance service core logic.
Tests framework management, assessment processing, and compliance scoring.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import json

from services.compliance_service import (
    ComplianceService, ComplianceScore, ComplianceGap,
    FrameworkRequirement, AssessmentResponse
)
from core.exceptions import BusinessLogicException, NotFoundException, ValidationException


@pytest.mark.unit
class TestComplianceService:
    """Unit tests for ComplianceService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return AsyncMock()
    
    @pytest.fixture
    def compliance_service(self, mock_db):
        """Create ComplianceService instance"""
        return ComplianceService(mock_db)
    
    @pytest.fixture
    def sample_framework(self):
        """Sample compliance framework"""
        return {
            'id': 1,
            'name': 'GDPR',
            'version': '2016/679',
            'requirements': [
                {
                    'id': 'GDPR-1',
                    'title': 'Lawful basis',
                    'description': 'Must have lawful basis for processing',
                    'category': 'Legal',
                    'priority': 'high'
                },
                {
                    'id': 'GDPR-2',
                    'title': 'Data minimization',
                    'description': 'Only process necessary data',
                    'category': 'Technical',
                    'priority': 'medium'
                }
            ]
        }
    
    @pytest.fixture
    def sample_assessment(self):
        """Sample assessment data"""
        return {
            'id': str(uuid4()),
            'framework_id': 1,
            'business_id': str(uuid4()),
            'status': 'in_progress',
            'responses': {
                'GDPR-1': {
                    'compliant': True,
                    'evidence': ['privacy_policy.pdf'],
                    'notes': 'Documented lawful basis'
                },
                'GDPR-2': {
                    'compliant': False,
                    'evidence': [],
                    'notes': 'Need to implement data minimization'
                }
            },
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        }
    
    @pytest.mark.asyncio
    async def test_calculate_compliance_score(self, compliance_service, sample_assessment):
        """Test compliance score calculation"""
        score = await compliance_service.calculate_compliance_score(
            sample_assessment['responses'],
            total_requirements=10
        )
        
        assert isinstance(score, ComplianceScore)
        assert 0 <= score.percentage <= 100
        assert score.compliant_count == 1
        assert score.total_count == 10
        assert score.percentage == 10.0
    
    @pytest.mark.asyncio
    async def test_calculate_compliance_score_weighted(self, compliance_service):
        """Test weighted compliance score calculation"""
        responses = {
            'REQ-1': {'compliant': True, 'weight': 3},
            'REQ-2': {'compliant': False, 'weight': 1},
            'REQ-3': {'compliant': True, 'weight': 2}
        }
        
        score = await compliance_service.calculate_weighted_score(responses)
        
        # (3 + 2) / (3 + 1 + 2) = 5/6 = 83.33%
        assert score.percentage == pytest.approx(83.33, 0.01)
        assert score.weighted is True
    
    @pytest.mark.asyncio
    async def test_identify_compliance_gaps(self, compliance_service, sample_framework, sample_assessment):
        """Test identification of compliance gaps"""
        gaps = await compliance_service.identify_gaps(
            sample_framework['requirements'],
            sample_assessment['responses']
        )
        
        assert len(gaps) == 1
        assert gaps[0].requirement_id == 'GDPR-2'
        assert gaps[0].severity == 'medium'
        assert 'data minimization' in gaps[0].description.lower()
    
    @pytest.mark.asyncio
    async def test_generate_recommendations(self, compliance_service):
        """Test recommendation generation for gaps"""
        gaps = [
            ComplianceGap(
                requirement_id='GDPR-2',
                title='Data minimization',
                description='Not implementing data minimization',
                severity='high'
            ),
            ComplianceGap(
                requirement_id='GDPR-7',
                title='Data breach notification',
                description='No breach notification process',
                severity='critical'
            )
        ]
        
        recommendations = await compliance_service.generate_recommendations(gaps)
        
        assert len(recommendations) >= 2
        assert any('breach' in r.lower() for r in recommendations)
        assert any('minimization' in r.lower() for r in recommendations)
    
    @pytest.mark.asyncio
    async def test_create_assessment(self, compliance_service, mock_db):
        """Test creating new assessment"""
        mock_db.add = Mock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        assessment = await compliance_service.create_assessment(
            framework_id=1,
            business_id=str(uuid4()),
            user_id=str(uuid4())
        )
        
        assert assessment is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_assessment_response(self, compliance_service, mock_db):
        """Test updating assessment response"""
        assessment_id = str(uuid4())
        requirement_id = 'GDPR-1'
        
        mock_db.execute = AsyncMock()
        mock_db.commit = AsyncMock()
        
        response = AssessmentResponse(
            compliant=True,
            evidence=['document.pdf'],
            notes='Implemented successfully',
            validated_by='auditor@example.com'
        )
        
        updated = await compliance_service.update_response(
            assessment_id,
            requirement_id,
            response
        )
        
        assert updated is True
        mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_validate_evidence(self, compliance_service):
        """Test evidence validation"""
        evidence_files = [
            {'name': 'policy.pdf', 'size': 1024000, 'type': 'application/pdf'},
            {'name': 'screenshot.png', 'size': 500000, 'type': 'image/png'},
            {'name': 'malicious.exe', 'size': 100000, 'type': 'application/x-executable'}
        ]
        
        valid, invalid = await compliance_service.validate_evidence(evidence_files)
        
        assert len(valid) == 2
        assert len(invalid) == 1
        assert invalid[0]['name'] == 'malicious.exe'
    
    @pytest.mark.asyncio
    async def test_get_framework_requirements(self, compliance_service, mock_db):
        """Test retrieving framework requirements"""
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [
            Mock(id='REQ-1', title='Requirement 1'),
            Mock(id='REQ-2', title='Requirement 2')
        ]
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        requirements = await compliance_service.get_framework_requirements(1)
        
        assert len(requirements) == 2
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_complete_assessment(self, compliance_service, mock_db):
        """Test marking assessment as complete"""
        assessment_id = str(uuid4())
        
        mock_db.execute = AsyncMock()
        mock_db.commit = AsyncMock()
        
        # Mock getting assessment
        mock_assessment = Mock()
        mock_assessment.responses = {
            'REQ-1': {'compliant': True},
            'REQ-2': {'compliant': True}
        }
        mock_assessment.total_requirements = 2
        
        with patch.object(compliance_service, 'get_assessment', return_value=mock_assessment):
            result = await compliance_service.complete_assessment(assessment_id)
            
            assert result['status'] == 'completed'
            assert result['score']['percentage'] == 100.0
    
    @pytest.mark.asyncio
    async def test_export_assessment_report(self, compliance_service):
        """Test exporting assessment report"""
        assessment_data = {
            'id': str(uuid4()),
            'framework': 'GDPR',
            'score': {'percentage': 75.0, 'compliant_count': 15, 'total_count': 20},
            'gaps': [
                {'requirement': 'GDPR-2', 'severity': 'high'}
            ],
            'responses': {}
        }
        
        report = await compliance_service.export_report(
            assessment_data,
            format='json'
        )
        
        assert 'assessment_id' in report
        assert report['compliance_score'] == 75.0
        assert len(report['gaps']) == 1
    
    @pytest.mark.asyncio
    async def test_benchmark_compliance(self, compliance_service, mock_db):
        """Test compliance benchmarking against industry"""
        mock_result = Mock()
        mock_result.scalar_one_or_none.return_value = 72.5  # Industry average
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        benchmark = await compliance_service.benchmark_score(
            score=80.0,
            industry='technology'
        )
        
        assert benchmark['user_score'] == 80.0
        assert benchmark['industry_average'] == 72.5
        assert benchmark['above_average'] is True
    
    @pytest.mark.asyncio
    async def test_assessment_history(self, compliance_service, mock_db):
        """Test retrieving assessment history"""
        mock_result = Mock()
        mock_result.scalars.return_value.all.return_value = [
            Mock(
                id=str(uuid4()),
                created_at=datetime.now(timezone.utc) - timedelta(days=30),
                score=65.0
            ),
            Mock(
                id=str(uuid4()),
                created_at=datetime.now(timezone.utc) - timedelta(days=15),
                score=75.0
            ),
            Mock(
                id=str(uuid4()),
                created_at=datetime.now(timezone.utc),
                score=85.0
            )
        ]
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        history = await compliance_service.get_assessment_history(
            business_id=str(uuid4()),
            limit=10
        )
        
        assert len(history) == 3
        assert history[0].score < history[-1].score  # Shows improvement
    
    @pytest.mark.asyncio
    async def test_compliance_trends(self, compliance_service):
        """Test analyzing compliance trends"""
        history = [
            {'date': '2024-01-01', 'score': 60.0},
            {'date': '2024-02-01', 'score': 65.0},
            {'date': '2024-03-01', 'score': 75.0},
            {'date': '2024-04-01', 'score': 72.0}
        ]
        
        trends = await compliance_service.analyze_trends(history)
        
        assert trends['overall_trend'] == 'improving'
        assert trends['average_improvement'] > 0
        assert 'forecast' in trends
    
    @pytest.mark.asyncio
    async def test_requirement_prioritization(self, compliance_service):
        """Test prioritizing requirements by risk"""
        requirements = [
            FrameworkRequirement(
                id='REQ-1',
                title='Critical requirement',
                risk_level='critical',
                effort='low'
            ),
            FrameworkRequirement(
                id='REQ-2',
                title='Low priority',
                risk_level='low',
                effort='high'
            ),
            FrameworkRequirement(
                id='REQ-3',
                title='Quick win',
                risk_level='medium',
                effort='low'
            )
        ]
        
        prioritized = await compliance_service.prioritize_requirements(requirements)
        
        assert prioritized[0].id == 'REQ-1'  # Critical first
        assert prioritized[1].id == 'REQ-3'  # Quick win second
        assert prioritized[2].id == 'REQ-2'  # Low priority last
    
    @pytest.mark.asyncio
    async def test_automated_evidence_mapping(self, compliance_service):
        """Test automated mapping of evidence to requirements"""
        evidence_files = [
            {'name': 'privacy_policy.pdf', 'tags': ['privacy', 'gdpr']},
            {'name': 'security_audit.pdf', 'tags': ['security', 'iso27001']},
            {'name': 'data_retention.xlsx', 'tags': ['data', 'retention', 'gdpr']}
        ]
        
        requirements = [
            {'id': 'GDPR-1', 'keywords': ['privacy', 'policy']},
            {'id': 'GDPR-2', 'keywords': ['data', 'retention']},
            {'id': 'ISO-1', 'keywords': ['security', 'audit']}
        ]
        
        mapping = await compliance_service.map_evidence_to_requirements(
            evidence_files,
            requirements
        )
        
        assert 'privacy_policy.pdf' in mapping['GDPR-1']
        assert 'data_retention.xlsx' in mapping['GDPR-2']
        assert 'security_audit.pdf' in mapping['ISO-1']


@pytest.mark.integration
class TestComplianceServiceIntegration:
    """Integration tests for ComplianceService"""
    
    @pytest.mark.asyncio
    async def test_full_assessment_workflow(self, db_session):
        """Test complete assessment workflow"""
        service = ComplianceService(db_session)
        
        # Create assessment
        assessment = await service.create_assessment(
            framework_id=1,
            business_id=str(uuid4()),
            user_id=str(uuid4())
        )
        
        # Update responses
        for req_id in ['REQ-1', 'REQ-2', 'REQ-3']:
            response = AssessmentResponse(
                compliant=req_id != 'REQ-2',  # REQ-2 non-compliant
                evidence=[f'{req_id}_evidence.pdf'],
                notes=f'Response for {req_id}'
            )
            await service.update_response(assessment.id, req_id, response)
        
        # Calculate score
        score = await service.calculate_compliance_score(
            assessment.responses,
            total_requirements=3
        )
        
        assert score.percentage == pytest.approx(66.67, 0.01)
        
        # Identify gaps
        gaps = await service.identify_gaps(
            [{'id': 'REQ-2', 'title': 'Gap requirement'}],
            assessment.responses
        )
        
        assert len(gaps) == 1
        
        # Generate recommendations
        recommendations = await service.generate_recommendations(gaps)
        assert len(recommendations) > 0
        
        # Complete assessment
        result = await service.complete_assessment(assessment.id)
        assert result['status'] == 'completed'
    
    @pytest.mark.asyncio
    async def test_concurrent_assessments(self, db_session):
        """Test handling multiple concurrent assessments"""
        import asyncio
        service = ComplianceService(db_session)
        
        # Create multiple assessments concurrently
        tasks = [
            service.create_assessment(
                framework_id=1,
                business_id=str(uuid4()),
                user_id=str(uuid4())
            )
            for _ in range(5)
        ]
        
        assessments = await asyncio.gather(*tasks)
        
        assert len(assessments) == 5
        assert all(a.id is not None for a in assessments)
        assert len(set(a.id for a in assessments)) == 5  # All unique
    
    @pytest.mark.asyncio
    async def test_performance_large_assessment(self, db_session):
        """Test performance with large number of requirements"""
        import time
        service = ComplianceService(db_session)
        
        # Create assessment with many requirements
        responses = {
            f'REQ-{i}': {
                'compliant': i % 2 == 0,
                'evidence': [f'evidence_{i}.pdf'],
                'notes': f'Response {i}'
            }
            for i in range(100)
        }
        
        start = time.time()
        score = await service.calculate_compliance_score(responses, 100)
        duration = time.time() - start
        
        assert score.percentage == 50.0
        assert duration < 1.0  # Should complete within 1 second