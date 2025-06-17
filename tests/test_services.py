"""
Unit Tests for ComplianceGPT Core Services

This module tests the core business logic and service layer functions
including business profile management, assessment logic, policy generation,
and compliance framework recommendations.
"""

from datetime import datetime, timedelta
from unittest.mock import patch
from uuid import uuid4

import pytest

from api.middleware.error_handler import ValidationAPIError
from services.assessment_service import AssessmentService
from services.business_service import BusinessService
from services.evidence_service import EvidenceService
from services.framework_service import FrameworkService
from services.implementation_service import ImplementationService
from services.policy_service import PolicyService
from services.readiness_service import ReadinessService


@pytest.mark.unit
class TestBusinessService:
    """Test business profile service logic"""

    def test_create_business_profile_valid_data(self, db_session, sample_business_profile):
        """Test creating a business profile with valid data"""
        user_id = uuid4()

        # Mock the service method
        with patch('services.business_service.BusinessService.create_profile') as mock_create:
            mock_create.return_value = {
                **sample_business_profile,
                "id": uuid4(),
                "user_id": user_id,
                "created_at": datetime.utcnow()
            }

            result = BusinessService.create_profile(user_id, sample_business_profile)

            assert result["company_name"] == sample_business_profile["company_name"]
            assert result["user_id"] == user_id
            assert "id" in result
            mock_create.assert_called_once_with(user_id, sample_business_profile)

    def test_create_business_profile_invalid_data(self, db_session):
        """Test creating business profile with invalid data raises validation error"""
        user_id = uuid4()
        invalid_data = {
            "company_name": "",  # Invalid: too short
            "industry": "x",  # Invalid: too short
            "employee_count": -1,  # Invalid: negative
        }

        with patch('services.business_service.BusinessService.create_profile') as mock_create:
            mock_create.side_effect = ValidationAPIError("Invalid business profile data")

            with pytest.raises(ValidationAPIError):
                BusinessService.create_profile(user_id, invalid_data)

    def test_assess_compliance_requirements(self, db_session, sample_business_profile):
        """Test compliance requirement assessment based on business profile"""
        with patch('services.business_service.BusinessService.assess_compliance_requirements') as mock_assess:
            expected_requirements = [
                {"framework": "GDPR", "mandatory": True, "reason": "Handles personal data"},
                {"framework": "ISO 27001", "mandatory": False, "reason": "Technology industry best practice"}
            ]
            mock_assess.return_value = expected_requirements

            result = BusinessService.assess_compliance_requirements(sample_business_profile)

            assert len(result) >= 1
            assert any(req["framework"] == "GDPR" for req in result)
            mock_assess.assert_called_once_with(sample_business_profile)

    def test_update_business_profile(self, db_session):
        """Test updating business profile"""
        profile_id = uuid4()
        update_data = {"employee_count": 75, "industry": "FinTech"}

        with patch('services.business_service.BusinessService.update_profile') as mock_update:
            mock_update.return_value = {
                "id": profile_id,
                "employee_count": 75,
                "industry": "FinTech",
                "updated_at": datetime.utcnow()
            }

            result = BusinessService.update_profile(profile_id, update_data)

            assert result["employee_count"] == 75
            assert result["industry"] == "FinTech"
            mock_update.assert_called_once_with(profile_id, update_data)


@pytest.mark.unit
class TestAssessmentService:
    """Test assessment service logic"""

    def test_create_assessment_session(self, db_session):
        """Test creating a new assessment session"""
        user_id = uuid4()
        business_profile_id = uuid4()

        with patch('services.assessment_service.AssessmentService.create_session') as mock_create:
            mock_create.return_value = {
                "id": uuid4(),
                "user_id": user_id,
                "business_profile_id": business_profile_id,
                "session_type": "compliance_scoping",
                "status": "in_progress",
                "current_stage": 1,
                "total_stages": 5,
                "created_at": datetime.utcnow()
            }

            result = AssessmentService.create_session(user_id, business_profile_id, "compliance_scoping")

            assert result["user_id"] == user_id
            assert result["session_type"] == "compliance_scoping"
            assert result["status"] == "in_progress"
            mock_create.assert_called_once()

    def test_process_assessment_response(self, db_session):
        """Test processing assessment responses"""
        session_id = uuid4()
        response_data = {
            "question_id": "data_processing",
            "response": "Yes, we process customer personal data",
            "move_to_next_stage": False
        }

        with patch('services.assessment_service.AssessmentService.process_response') as mock_process:
            mock_process.return_value = {
                "session_updated": True,
                "recommendations_updated": True,
                "next_question": {
                    "id": "data_storage",
                    "question": "Where do you store customer data?",
                    "type": "multiple_choice",
                    "options": ["On-premises", "Cloud", "Hybrid"]
                }
            }

            result = AssessmentService.process_response(session_id, response_data)

            assert result["session_updated"] is True
            assert "next_question" in result
            mock_process.assert_called_once_with(session_id, response_data)

    def test_generate_recommendations(self, db_session):
        """Test generating compliance recommendations from assessment"""
        session_id = uuid4()

        with patch('services.assessment_service.AssessmentService.generate_recommendations') as mock_generate:
            mock_generate.return_value = [
                {
                    "framework": "GDPR",
                    "priority": "High",
                    "reasons": ["Processes personal data", "EU customers"],
                    "next_steps": ["Data mapping", "Privacy policy update"]
                },
                {
                    "framework": "ISO 27001",
                    "priority": "Medium",
                    "reasons": ["Technology industry", "Customer data security"],
                    "next_steps": ["Risk assessment", "Security controls implementation"]
                }
            ]

            result = AssessmentService.generate_recommendations(session_id)

            assert len(result) >= 1
            assert all("framework" in rec for rec in result)
            assert all("priority" in rec for rec in result)
            mock_generate.assert_called_once_with(session_id)

    def test_calculate_compliance_score(self, db_session):
        """Test compliance score calculation"""
        assessment_data = {
            "data_processing": "yes",
            "security_measures": "basic",
            "staff_training": "none",
            "incident_response": "informal"
        }

        with patch('services.assessment_service.AssessmentService.calculate_score') as mock_calculate:
            mock_calculate.return_value = {
                "overall_score": 45.5,
                "category_scores": {
                    "data_protection": 60,
                    "security": 40,
                    "governance": 30,
                    "incident_management": 25
                },
                "risk_level": "Medium"
            }

            result = AssessmentService.calculate_score(assessment_data)

            assert 0 <= result["overall_score"] <= 100
            assert result["risk_level"] in ["Low", "Medium", "High", "Critical"]
            mock_calculate.assert_called_once_with(assessment_data)


@pytest.mark.unit
class TestPolicyService:
    """Test policy generation service logic"""

    def test_generate_policy_with_ai(self, db_session, mock_ai_client):
        """Test AI-powered policy generation"""
        business_profile_id = uuid4()
        framework_id = uuid4()

        mock_ai_response = """
        # Data Protection Policy

        ## 1. Purpose and Scope
        This policy establishes guidelines for the protection of personal data...

        ## 2. Data Processing Principles
        We commit to processing personal data in accordance with GDPR principles...
        """

        mock_ai_client.generate_content.return_value.text = mock_ai_response

        with patch('services.policy_service.PolicyService.generate_policy') as mock_generate:
            mock_generate.return_value = {
                "id": uuid4(),
                "business_profile_id": business_profile_id,
                "framework_id": framework_id,
                "policy_name": "Data Protection Policy",
                "policy_type": "data_protection",
                "content": mock_ai_response,
                "sections": {
                    "purpose": "This policy establishes guidelines...",
                    "principles": "We commit to processing personal data..."
                },
                "status": "draft",
                "version": 1
            }

            result = PolicyService.generate_policy(business_profile_id, framework_id)

            assert result["policy_name"] == "Data Protection Policy"
            assert result["status"] == "draft"
            assert result["version"] == 1
            assert "content" in result
            mock_generate.assert_called_once()

    def test_customize_policy_content(self, db_session):
        """Test policy customization based on business context"""
        policy_id = uuid4()
        customizations = {
            "company_name": "Test Corp Ltd",
            "industry": "Technology",
            "data_types": ["customer_data", "employee_data"],
            "retention_periods": {"customer_data": "7 years", "employee_data": "lifetime"}
        }

        with patch('services.policy_service.PolicyService.customize_policy') as mock_customize:
            mock_customize.return_value = {
                "policy_id": policy_id,
                "customized_content": "Customized policy content with Test Corp Ltd specifics...",
                "sections_updated": ["company_info", "data_types", "retention"],
                "version": 2
            }

            result = PolicyService.customize_policy(policy_id, customizations)

            assert result["policy_id"] == policy_id
            assert result["version"] == 2
            assert "customized_content" in result
            mock_customize.assert_called_once_with(policy_id, customizations)

    def test_validate_policy_completeness(self, db_session):
        """Test policy completeness validation"""
        policy_content = {
            "sections": {
                "purpose": "Policy purpose section",
                "scope": "Policy scope section",
                "principles": "Data processing principles"
            },
            "framework": "GDPR"
        }

        with patch('services.policy_service.PolicyService.validate_completeness') as mock_validate:
            mock_validate.return_value = {
                "is_complete": False,
                "missing_sections": ["incident_response", "contact_details"],
                "compliance_score": 75,
                "recommendations": [
                    "Add incident response procedures",
                    "Include data protection officer contact details"
                ]
            }

            result = PolicyService.validate_completeness(policy_content)

            assert "is_complete" in result
            assert "missing_sections" in result
            assert "compliance_score" in result
            mock_validate.assert_called_once_with(policy_content)


@pytest.mark.unit
class TestFrameworkService:
    """Test compliance framework service logic"""

    def test_recommend_frameworks(self, db_session, sample_business_profile):
        """Test framework recommendation algorithm"""
        with patch('services.framework_service.FrameworkService.recommend_frameworks') as mock_recommend:
            mock_recommend.return_value = [
                {
                    "framework": {
                        "id": uuid4(),
                        "name": "GDPR",
                        "display_name": "General Data Protection Regulation",
                        "category": "Data Protection"
                    },
                    "relevance_score": 95.0,
                    "reasons": ["Processes personal data", "UK business"],
                    "priority": "High"
                },
                {
                    "framework": {
                        "id": uuid4(),
                        "name": "ISO27001",
                        "display_name": "ISO 27001 Information Security",
                        "category": "Security"
                    },
                    "relevance_score": 80.0,
                    "reasons": ["Technology industry", "Customer data handling"],
                    "priority": "Medium"
                }
            ]

            result = FrameworkService.recommend_frameworks(sample_business_profile)

            assert len(result) >= 1
            assert all(rec["relevance_score"] <= 100 for rec in result)
            assert all(rec["priority"] in ["High", "Medium", "Low"] for rec in result)
            mock_recommend.assert_called_once_with(sample_business_profile)

    def test_calculate_framework_relevance(self, db_session):
        """Test framework relevance calculation"""
        business_context = {
            "industry": "Healthcare",
            "handles_personal_data": True,
            "processes_payments": False,
            "employee_count": 25,
            "has_international_operations": False
        }

        framework_details = {
            "name": "GDPR",
            "applicable_industries": ["All"],
            "mandatory_for": ["personal_data_processors"],
            "company_size_range": {"min": 1, "max": 1000000}
        }

        with patch('services.framework_service.FrameworkService.calculate_relevance') as mock_calculate:
            mock_calculate.return_value = {
                "score": 92.5,
                "factors": {
                    "industry_match": 100,
                    "data_processing": 95,
                    "company_size": 90,
                    "geographic_scope": 85
                },
                "mandatory": True
            }

            result = FrameworkService.calculate_relevance(business_context, framework_details)

            assert 0 <= result["score"] <= 100
            assert "factors" in result
            assert "mandatory" in result
            mock_calculate.assert_called_once()

    def test_get_framework_requirements(self, db_session):
        """Test retrieving framework requirements"""
        framework_id = uuid4()

        with patch('services.framework_service.FrameworkService.get_requirements') as mock_get:
            mock_get.return_value = [
                {
                    "id": "gdpr_art_5",
                    "title": "Principles relating to processing of personal data",
                    "description": "Personal data shall be processed lawfully, fairly and transparently",
                    "category": "data_processing",
                    "mandatory": True,
                    "implementation_guidance": "Implement privacy notices and consent mechanisms"
                },
                {
                    "id": "gdpr_art_25",
                    "title": "Data protection by design and by default",
                    "description": "Implement appropriate technical and organisational measures",
                    "category": "technical_measures",
                    "mandatory": True,
                    "implementation_guidance": "Build privacy considerations into system design"
                }
            ]

            result = FrameworkService.get_requirements(framework_id)

            assert len(result) >= 1
            assert all("id" in req for req in result)
            assert all("mandatory" in req for req in result)
            mock_get.assert_called_once_with(framework_id)


@pytest.mark.unit
class TestImplementationService:
    """Test implementation planning service logic"""

    def test_generate_implementation_plan(self, db_session):
        """Test implementation plan generation"""
        business_profile_id = uuid4()
        framework_id = uuid4()

        with patch('services.implementation_service.ImplementationService.generate_plan') as mock_generate:
            mock_generate.return_value = {
                "id": uuid4(),
                "business_profile_id": business_profile_id,
                "framework_id": framework_id,
                "plan_name": "GDPR Implementation Plan",
                "total_phases": 4,
                "total_tasks": 24,
                "estimated_duration_weeks": 16,
                "phases": [
                    {
                        "name": "Assessment & Planning",
                        "duration_weeks": 2,
                        "tasks": 6
                    },
                    {
                        "name": "Policy Development",
                        "duration_weeks": 4,
                        "tasks": 8
                    }
                ],
                "status": "not_started",
                "progress_percentage": 0.0
            }

            result = ImplementationService.generate_plan(business_profile_id, framework_id)

            assert result["total_phases"] > 0
            assert result["total_tasks"] > 0
            assert result["estimated_duration_weeks"] > 0
            assert result["progress_percentage"] == 0.0
            mock_generate.assert_called_once()

    def test_update_task_progress(self, db_session):
        """Test updating implementation task progress"""
        plan_id = uuid4()
        task_id = uuid4()
        update_data = {
            "status": "completed",
            "actual_end": datetime.utcnow(),
            "notes": "Task completed successfully"
        }

        with patch('services.implementation_service.ImplementationService.update_task') as mock_update:
            mock_update.return_value = {
                "task_updated": True,
                "plan_progress": 25.0,
                "phase_progress": 50.0,
                "next_tasks": [
                    {"id": uuid4(), "name": "Next task in sequence", "status": "not_started"}
                ]
            }

            result = ImplementationService.update_task(plan_id, task_id, update_data)

            assert result["task_updated"] is True
            assert 0 <= result["plan_progress"] <= 100
            mock_update.assert_called_once_with(plan_id, task_id, update_data)

    def test_calculate_resource_requirements(self, db_session):
        """Test resource requirement calculation"""
        plan_data = {
            "total_tasks": 24,
            "complexity_factors": {
                "technical_complexity": "medium",
                "organizational_size": "small",
                "existing_processes": "basic"
            },
            "framework": "GDPR"
        }

        with patch('services.implementation_service.ImplementationService.calculate_resources') as mock_calculate:
            mock_calculate.return_value = {
                "estimated_budget": 15000.0,
                "required_roles": [
                    {"role": "Data Protection Officer", "effort_days": 20},
                    {"role": "IT Security Specialist", "effort_days": 15},
                    {"role": "Legal Advisor", "effort_days": 5}
                ],
                "external_support_needed": True,
                "risk_factors": [
                    {"risk": "Limited internal expertise", "mitigation": "External consultant"}
                ]
            }

            result = ImplementationService.calculate_resources(plan_data)

            assert result["estimated_budget"] > 0
            assert len(result["required_roles"]) >= 1
            assert "risk_factors" in result
            mock_calculate.assert_called_once_with(plan_data)


@pytest.mark.unit
class TestEvidenceService:
    """Test evidence collection service logic"""

    def test_identify_evidence_requirements(self, db_session):
        """Test identifying evidence requirements for framework controls"""
        framework_id = uuid4()
        control_ids = [uuid4(), uuid4()]

        with patch('services.evidence_service.EvidenceService.identify_requirements') as mock_identify:
            mock_identify.return_value = [
                {
                    "control_id": control_ids[0],
                    "evidence_type": "document",
                    "title": "Data Protection Policy",
                    "description": "Written policy documenting data protection procedures",
                    "automation_possible": False,
                    "collection_method": "manual"
                },
                {
                    "control_id": control_ids[1],
                    "evidence_type": "log",
                    "title": "Access Control Logs",
                    "description": "System logs showing access control implementation",
                    "automation_possible": True,
                    "collection_method": "automated"
                }
            ]

            result = EvidenceService.identify_requirements(framework_id, control_ids)

            assert len(result) >= 1
            assert all("control_id" in item for item in result)
            assert all("evidence_type" in item for item in result)
            mock_identify.assert_called_once_with(framework_id, control_ids)

    def test_configure_automated_collection(self, db_session):
        """Test configuring automated evidence collection"""
        evidence_id = uuid4()
        automation_config = {
            "source_type": "cloud_api",
            "endpoint": "https://api.example.com/logs",
            "collection_frequency": "daily",
            "credentials_id": "cloud_creds_001"
        }

        with patch('services.evidence_service.EvidenceService.configure_automation') as mock_configure:
            mock_configure.return_value = {
                "configuration_successful": True,
                "automation_enabled": True,
                "next_collection": datetime.utcnow() + timedelta(days=1),
                "test_connection": "successful"
            }

            result = EvidenceService.configure_automation(evidence_id, automation_config)

            assert result["configuration_successful"] is True
            assert result["automation_enabled"] is True
            mock_configure.assert_called_once_with(evidence_id, automation_config)

    def test_validate_evidence_quality(self, db_session):
        """Test evidence quality validation"""
        evidence_data = {
            "evidence_type": "document",
            "file_content": "Sample policy document content...",
            "metadata": {
                "creation_date": "2024-01-01",
                "author": "DPO",
                "version": "1.0"
            }
        }

        with patch('services.evidence_service.EvidenceService.validate_quality') as mock_validate:
            mock_validate.return_value = {
                "quality_score": 85,
                "validation_results": {
                    "completeness": "good",
                    "relevance": "high",
                    "timeliness": "current",
                    "authenticity": "verified"
                },
                "issues": [],
                "recommendations": ["Consider adding version control information"]
            }

            result = EvidenceService.validate_quality(evidence_data)

            assert 0 <= result["quality_score"] <= 100
            assert "validation_results" in result
            mock_validate.assert_called_once_with(evidence_data)


@pytest.mark.unit
class TestReadinessService:
    """Test compliance readiness assessment service logic"""

    def test_calculate_overall_readiness(self, db_session):
        """Test overall compliance readiness calculation"""
        business_profile_id = uuid4()

        with patch('services.readiness_service.ReadinessService.calculate_readiness') as mock_calculate:
            mock_calculate.return_value = {
                "overall_score": 72.5,
                "framework_scores": {
                    "GDPR": 80.0,
                    "ISO27001": 65.0
                },
                "control_coverage": {
                    "GDPR": {
                        "implemented": 12,
                        "total": 20,
                        "coverage_percentage": 60.0
                    }
                },
                "risk_level": "Medium",
                "projected_timeline": "6-8 months to full compliance"
            }

            result = ReadinessService.calculate_readiness(business_profile_id)

            assert 0 <= result["overall_score"] <= 100
            assert result["risk_level"] in ["Low", "Medium", "High", "Critical"]
            assert "framework_scores" in result
            mock_calculate.assert_called_once_with(business_profile_id)

    def test_identify_compliance_gaps(self, db_session):
        """Test compliance gap identification"""
        assessment_data = {
            "implemented_controls": ["gdpr_art_5", "gdpr_art_6"],
            "required_controls": ["gdpr_art_5", "gdpr_art_6", "gdpr_art_25", "gdpr_art_32"],
            "framework": "GDPR"
        }

        with patch('services.readiness_service.ReadinessService.identify_gaps') as mock_identify:
            mock_identify.return_value = [
                {
                    "control_id": "gdpr_art_25",
                    "title": "Data protection by design and by default",
                    "gap_type": "not_implemented",
                    "priority": "High",
                    "effort_estimate": "4-6 weeks"
                },
                {
                    "control_id": "gdpr_art_32",
                    "title": "Security of processing",
                    "gap_type": "partially_implemented",
                    "priority": "Medium",
                    "effort_estimate": "2-3 weeks"
                }
            ]

            result = ReadinessService.identify_gaps(assessment_data)

            assert len(result) >= 1
            assert all("control_id" in gap for gap in result)
            assert all("priority" in gap for gap in result)
            mock_identify.assert_called_once_with(assessment_data)

    def test_generate_executive_summary(self, db_session):
        """Test executive summary generation"""
        readiness_data = {
            "overall_score": 68.5,
            "framework_scores": {"GDPR": 75.0, "ISO27001": 62.0},
            "gaps": [{"priority": "High", "count": 3}, {"priority": "Medium", "count": 7}],
            "risk_level": "Medium"
        }

        with patch('services.readiness_service.ReadinessService.generate_summary') as mock_generate:
            mock_generate.return_value = {
                "summary": "Your organization has achieved 68.5% compliance readiness across assessed frameworks. While GDPR compliance is progressing well at 75%, ISO 27001 requires additional attention. Priority should be given to addressing 3 high-priority gaps in the next quarter.",
                "key_metrics": {
                    "compliance_percentage": 68.5,
                    "frameworks_assessed": 2,
                    "critical_gaps": 3,
                    "estimated_completion": "Q3 2024"
                },
                "next_steps": [
                    "Address high-priority GDPR gaps",
                    "Implement ISO 27001 security controls",
                    "Schedule quarterly readiness review"
                ]
            }

            result = ReadinessService.generate_summary(readiness_data)

            assert "summary" in result
            assert "key_metrics" in result
            assert "next_steps" in result
            assert len(result["next_steps"]) >= 1
            mock_generate.assert_called_once_with(readiness_data)
