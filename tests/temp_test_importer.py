import pytest

# Test importing services
from services.business_service import create_or_update_business_profile
from services.policy_service import generate_compliance_policy
from services.assessment_service import AssessmentService
from services.framework_service import get_relevant_frameworks
from config.logging_config import get_logger
from config.settings import settings

def test_import_services():
    """This test checks if service modules can be imported without error."""
    assert True
