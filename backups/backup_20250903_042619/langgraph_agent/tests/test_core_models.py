"""
Tests for core models and constants.
Validates JSON schema export and SafeFallbackResponse behavior.
"""

import json
from uuid import uuid4

import pytest
from pydantic import ValidationError

from langgraph_agent.core.models import (
    ComplianceProfile,
    Obligation,
    EvidenceItem,
    LegalReviewTicket,
    SafeFallbackResponse,
    GraphMessage,
    RouteDecision,
    ComplianceFramework,
    BusinessSector,
    RiskLevel,
    EvidenceType,
    get_model_schemas,
    get_safe_fallback_schema,
)
from langgraph_agent.core.constants import (
    SLO_P95_LATENCY_MS,
    ROUTER_THRESHOLDS,
    GRAPH_NODES,
    COMPLIANCE_FRAMEWORKS,
)


class TestConstants:
    """Test core constants are properly defined."""

    def test_slo_constraints(self):
        """Test SLO constants are within expected ranges."""
        assert SLO_P95_LATENCY_MS == 2500
        assert 0 < ROUTER_THRESHOLDS["rules_confidence"] <= 1.0
        assert 0 < ROUTER_THRESHOLDS["classifier_confidence"] <= 1.0

    def test_graph_nodes_defined(self):
        """Test all required graph nodes are defined."""
        required_nodes = [
            "router",
            "compliance_analyzer",
            "obligation_finder",
            "evidence_collector",
            "legal_reviewer",
            "autonomy_policy",
            "model",
        ]
        for node in required_nodes:
            assert node in GRAPH_NODES.values()

    def test_compliance_frameworks_align(self):
        """Test constants align with model enums."""
        model_frameworks = [f.value for f in ComplianceFramework]
        for framework in COMPLIANCE_FRAMEWORKS:
            assert framework in model_frameworks


class TestComplianceProfile:
    """Test ComplianceProfile model validation."""

    def test_valid_profile_creation(self):
        """Test creating a valid compliance profile."""
        profile = ComplianceProfile(
            company_id=uuid4(),
            business_name="Test Company Ltd",
            sector=BusinessSector.RETAIL,
            frameworks=[ComplianceFramework.GDPR, ComplianceFramework.UK_GDPR],
            geographical_scope=["UK", "EU"],
            employee_count=50,
            risk_tolerance=RiskLevel.MEDIUM,
        )

        assert profile.business_name == "Test Company Ltd"
        assert profile.sector == BusinessSector.RETAIL
        assert ComplianceFramework.GDPR in profile.frameworks
        assert profile.created_at is not None

    def test_gdpr_requires_geographical_scope(self):
        """Test GDPR compliance requires geographical scope."""
        with pytest.raises(ValidationError, match="Geographical scope required"):
            ComplianceProfile(
                company_id=uuid4(),
                business_name="Test Company Ltd",
                sector=BusinessSector.RETAIL,
                frameworks=[ComplianceFramework.GDPR],
                geographical_scope=[],  # Missing required scope
            )

    def test_frameworks_required(self):
        """Test at least one framework is required."""
        with pytest.raises(ValidationError, match="At least one compliance framework"):
            ComplianceProfile(
                company_id=uuid4(),
                business_name="Test Company Ltd",
                sector=BusinessSector.RETAIL,
                frameworks=[],  # Empty frameworks not allowed
            )


class TestObligation:
    """Test Obligation model validation."""

    def test_valid_obligation_creation(self):
        """Test creating a valid obligation."""
        obligation = Obligation(
            obligation_id="GDPR_DATA_001",
            framework=ComplianceFramework.GDPR,
            title="Data Processing Lawful Basis",
            description="Process personal data only with lawful basis",
            category="data_processing",
            mandatory=True,
            risk_level=RiskLevel.HIGH,
            applicable_sectors=[BusinessSector.RETAIL, BusinessSector.FINANCE],
        )

        assert obligation.obligation_id == "GDPR_DATA_001"
        assert obligation.framework == ComplianceFramework.GDPR
        assert obligation.mandatory is True
        assert BusinessSector.RETAIL in obligation.applicable_sectors

    def test_obligation_id_format_validation(self):
        """Test obligation ID follows required format."""
        with pytest.raises(ValidationError, match="Obligation ID must follow format"):
            Obligation(
                obligation_id="INVALID",  # Wrong format
                framework=ComplianceFramework.GDPR,
                title="Test Obligation",
                description="Test description",
                category="test",
            )


class TestSafeFallbackResponse:
    """Test SafeFallbackResponse behavior."""

    def test_safe_fallback_creation(self):
        """Test SafeFallbackResponse exactly as specified."""
        response = SafeFallbackResponse(
            error_message="Validation failed for user input",
            error_details={"field": "business_name", "issue": "too_short"},
        )

        assert response.status == "needs_review"
        assert response.error_message == "Validation failed for user input"
        assert response.error_details["field"] == "business_name"
        assert response.timestamp is not None

    def test_safe_fallback_status_validation(self):
        """Test status must be exactly 'needs_review'."""
        with pytest.raises(ValidationError, match="String should match pattern"):
            SafeFallbackResponse(
                status="invalid_status",  # Must be "needs_review"
                error_message="Test error",
                error_details={},
            )

    def test_safe_fallback_no_sensitive_data(self):
        """Test error details cannot contain sensitive information."""
        with pytest.raises(ValidationError, match="cannot contain sensitive key"):
            SafeFallbackResponse(
                error_message="Test error",
                error_details={"password": "secret123"},  # Sensitive key not allowed
            )


class TestEvidenceItem:
    """Test EvidenceItem model validation."""

    def test_valid_evidence_creation(self):
        """Test creating valid evidence item."""
        evidence = EvidenceItem(
            company_id=uuid4(),
            title="Privacy Policy Document",
            evidence_type=EvidenceType.POLICY_DOCUMENT,
            description="Current privacy policy",
            created_by=uuid4(),
            file_path="/documents/privacy_policy.pdf",
            frameworks=[ComplianceFramework.GDPR],
            related_obligations=["GDPR_PRIVACY_001"],
        )

        assert evidence.title == "Privacy Policy Document"
        assert evidence.evidence_type == EvidenceType.POLICY_DOCUMENT
        assert evidence.verified is False  # Default
        assert evidence.created_at is not None

    def test_file_path_validation(self):
        """Test file path must be absolute or URL."""
        with pytest.raises(ValidationError, match="File path must be absolute or URL"):
            EvidenceItem(
                company_id=uuid4(),
                title="Test Evidence",
                evidence_type=EvidenceType.POLICY_DOCUMENT,
                created_by=uuid4(),
                file_path="relative/path.pdf",  # Invalid relative path
            )


class TestLegalReviewTicket:
    """Test LegalReviewTicket model validation."""

    def test_valid_ticket_creation(self):
        """Test creating valid legal review ticket."""
        ticket = LegalReviewTicket(
            company_id=uuid4(),
            title="Privacy Policy Review",
            description="Review updated privacy policy for GDPR compliance",
            requested_by=uuid4(),
            content_type="policy",
            priority=RiskLevel.HIGH,
        )

        assert ticket.title == "Privacy Policy Review"
        assert ticket.status == "pending"  # Default
        assert ticket.priority == RiskLevel.HIGH
        assert ticket.created_at is not None

    def test_status_validation(self):
        """Test status must be from allowed values."""
        with pytest.raises(ValidationError, match="Status must be one of"):
            LegalReviewTicket(
                company_id=uuid4(),
                title="Test Ticket",
                description="Test description",
                requested_by=uuid4(),
                content_type="policy",
                status="invalid_status",  # Not in allowed list
            )


class TestGraphMessage:
    """Test GraphMessage model validation."""

    def test_valid_message_creation(self):
        """Test creating valid graph message."""
        message = GraphMessage(
            role="user",
            content="What GDPR obligations apply to my retail business?",
            tool_calls=None,
        )

        assert message.role == "user"
        assert "GDPR" in message.content
        assert message.timestamp is not None

    def test_role_validation(self):
        """Test role must be from allowed values."""
        with pytest.raises(ValidationError, match="String should match pattern"):
            GraphMessage(
                role="invalid_role",  # Must be user/assistant/system/tool
                content="Test message",
            )


class TestRouteDecision:
    """Test RouteDecision model validation."""

    def test_valid_decision_creation(self):
        """Test creating valid route decision."""
        decision = RouteDecision(
            route="compliance_analyzer",
            confidence=0.95,
            reasoning="High confidence match for compliance analysis keywords",
            method="rules",
            input_text="Analyze my business for GDPR compliance",
            company_id=uuid4(),
        )

        assert decision.route == "compliance_analyzer"
        assert decision.confidence == 0.95
        assert decision.method == "rules"
        assert decision.timestamp is not None

    def test_confidence_range_validation(self):
        """Test confidence must be between 0 and 1."""
        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            RouteDecision(
                route="test_route",
                confidence=-0.1,  # Invalid negative confidence
                reasoning="Test reasoning",
                method="rules",
                input_text="Test input",
                company_id=uuid4(),
            )


class TestJSONSchemaExport:
    """Test JSON schema export functionality."""

    def test_all_schemas_exportable(self):
        """Test all models export valid JSON schemas."""
        schemas = get_model_schemas()

        required_models = [
            "ComplianceProfile",
            "Obligation",
            "EvidenceItem",
            "LegalReviewTicket",
            "SafeFallbackResponse",
        ]

        for model_name in required_models:
            assert model_name in schemas
            schema = schemas[model_name]
            assert "properties" in schema
            assert "type" in schema
            assert schema["type"] == "object"

    def test_safe_fallback_schema(self):
        """Test SafeFallbackResponse schema export."""
        schema = get_safe_fallback_schema()

        assert schema["type"] == "object"
        assert "status" in schema["properties"]
        assert "error_message" in schema["properties"]
        assert "error_details" in schema["properties"]

        # Verify status has pattern constraint
        status_prop = schema["properties"]["status"]
        assert "pattern" in status_prop
        assert status_prop["pattern"] == "^needs_review$"

    def test_schemas_are_json_serializable(self):
        """Test all schemas can be JSON serialized."""
        schemas = get_model_schemas()

        try:
            json_str = json.dumps(schemas)
            parsed = json.loads(json_str)
            assert len(parsed) == len(schemas)
        except (TypeError, ValueError) as e:
            pytest.fail(f"Schemas are not JSON serializable: {e}")
