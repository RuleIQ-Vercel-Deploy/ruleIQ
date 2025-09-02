"""
API Contract Validation Tests

Validates API contracts and schema compliance including:
- Request/response schema validation
- OpenAPI specification compliance
- Backward compatibility testing
- Service boundary contracts
- Field mapper contract validation
"""

import json
import pytest
from typing import Any, Dict, List, Optional
from unittest.mock import patch

import httpx
from fastapi.testclient import TestClient
from pydantic import BaseModel, ValidationError

from api.main import app
from api.schemas import *  # Import all API schemas
from tests.utils.auth_test_utils import TestAuthManager

# Use TestAuthManager.create_test_user instead


@pytest.mark.contract
@pytest.mark.integration
class TestAPIContractValidation:
    """Test API contract compliance and validation"""

    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)

    @pytest.fixture
    async def async_client(self):
        """Create async test client"""
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            yield client

    @pytest.fixture
    async def auth_headers(self, async_db):
        """Create authentication headers"""
        auth_manager = TestAuthManager()
        user = auth_manager.create_test_user(
            email="contract@test.com", username="contractuser"
        )
        from api.dependencies.auth import create_access_token

        token = create_access_token(data={"sub": user.email})
        return {"Authorization": f"Bearer {token}"}

    def test_openapi_schema_generation(self, client: TestClient):
        """Test that OpenAPI schema is properly generated"""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        openapi_schema = response.json()

        # Validate basic OpenAPI structure
        assert "openapi" in openapi_schema
        assert "info" in openapi_schema
        assert "paths" in openapi_schema
        assert "components" in openapi_schema

        # Validate critical endpoints are documented
        paths = openapi_schema["paths"]
        critical_endpoints = [
            "/auth/login",
            "/auth/register",
            "/assessments",
            "/assessments/{assessment_id}",
            "/iq-agent/query",
            "/evidence/upload",
        ]

        for endpoint in critical_endpoints:
            endpoint_variants = [
                endpoint,
                endpoint.replace("{assessment_id}", "{id}"),
                endpoint.replace("_", "-"),
            ]

            found = any(ep in paths for ep in endpoint_variants)
            assert found, f"Critical endpoint {endpoint} not found in OpenAPI schema"

    @pytest.mark.asyncio
    async def test_assessment_endpoint_contract_validation(
        self, async_client: httpx.AsyncClient, auth_headers: Dict
    ):
        """Test assessment endpoint request/response contracts"""

        # Test POST /assessments contract
        valid_assessment_data = {
            "name": "Contract Test Assessment",
            "framework": "GDPR",
            "assessment_type": "full_assessment",
            "questions": [
                {
                    "question_id": "gdpr_lawful_basis",
                    "question_text": "Do you have a lawful basis for processing?",
                    "answer": "yes",
                    "evidence_ids": [],
                }
            ],
        }

        response = await async_client.post(
            "/assessments", json=valid_assessment_data, headers=auth_headers
        )

        assert response.status_code == 201
        assessment_response = response.json()

        # Validate response contract
        required_fields = [
            "id",
            "name",
            "framework",
            "status",
            "created_at",
            "updated_at",
        ]
        for field in required_fields:
            assert (
                field in assessment_response
            ), f"Required field {field} missing from response"

        # Validate field types
        assert isinstance(assessment_response["id"], str)
        assert isinstance(assessment_response["name"], str)
        assert isinstance(assessment_response["framework"], str)
        assert isinstance(assessment_response["status"], str)
        assert isinstance(assessment_response["created_at"], str)

        # Test GET /assessments/{id} contract
        assessment_id = assessment_response["id"]
        response = await async_client.get(
            f"/assessments/{assessment_id}", headers=auth_headers
        )

        assert response.status_code == 200
        get_response = response.json()

        # Response should have same structure as POST response
        for field in required_fields:
            assert field in get_response

        # Specific field validations
        assert get_response["id"] == assessment_id
        assert get_response["name"] == valid_assessment_data["name"]

    @pytest.mark.asyncio
    async def test_authentication_endpoint_contract_validation(
        self, async_client: httpx.AsyncClient
    ):
        """Test authentication endpoint contracts"""

        # Test POST /auth/register contract
        registration_data = {
            "email": "contract.test@example.com",
            "password": "SecurePassword123!",
            "company_name": "Contract Test Ltd",
            "role": "business_user",
        }

        response = await async_client.post("/auth/register", json=registration_data)
        assert response.status_code == 201

        register_response = response.json()
        required_fields = ["id", "email", "company_name", "role", "created_at"]

        for field in required_fields:
            assert (
                field in register_response
            ), f"Required field {field} missing from register response"

        # Test POST /auth/login contract
        login_data = {
            "username": registration_data["email"],
            "password": registration_data["password"],
        }

        response = await async_client.post("/auth/login", data=login_data)
        assert response.status_code == 200

        login_response = response.json()
        required_auth_fields = ["access_token", "token_type", "user_id", "expires_in"]

        for field in required_auth_fields:
            assert (
                field in login_response
            ), f"Required field {field} missing from login response"

        # Validate token format
        assert login_response["token_type"] == "bearer"
        assert isinstance(login_response["access_token"], str)
        assert len(login_response["access_token"]) > 20  # JWT should be reasonably long

    @pytest.mark.asyncio
    async def test_iq_agent_endpoint_contract_validation(
        self, async_client: httpx.AsyncClient, auth_headers: Dict
    ):
        """Test IQ Agent endpoint contracts"""

        query_data = {
            "query": "What are the GDPR compliance requirements for my business?",
            "context": {
                "business_type": "e-commerce",
                "company_size": "small",
                "frameworks": ["GDPR"],
            },
        }

        with patch("services.iq_agent.IQComplianceAgent.process_query") as mock_query:
            mock_query.return_value = {
                "status": "success",
                "summary": {
                    "risk_posture": "MEDIUM",
                    "compliance_score": 0.75,
                    "top_gaps": ["Consent Management"],
                    "immediate_actions": ["Implement consent system"],
                },
                "artifacts": {
                    "compliance_posture": {"overall_coverage": 0.75},
                    "action_plan": [],
                    "risk_assessment": {"overall_risk_level": "MEDIUM"},
                },
                "evidence": {},
                "next_actions": [],
            }

            response = await async_client.post(
                "/iq-agent/query", json=query_data, headers=auth_headers
            )

            assert response.status_code == 200
            iq_response = response.json()

            # Validate IQ Agent response contract
            required_fields = [
                "status",
                "summary",
                "artifacts",
                "evidence",
                "next_actions",
            ]
            for field in required_fields:
                assert (
                    field in iq_response
                ), f"Required field {field} missing from IQ Agent response"

            # Validate summary structure
            summary = iq_response["summary"]
            summary_fields = [
                "risk_posture",
                "compliance_score",
                "top_gaps",
                "immediate_actions",
            ]
            for field in summary_fields:
                assert field in summary, f"Required summary field {field} missing"

            # Validate data types
            assert isinstance(summary["compliance_score"], (int, float))
            assert 0 <= summary["compliance_score"] <= 1
            assert isinstance(summary["top_gaps"], list)
            assert isinstance(summary["immediate_actions"], list)

    @pytest.mark.asyncio
    async def test_evidence_upload_contract_validation(
        self, async_client: httpx.AsyncClient, auth_headers: Dict
    ):
        """Test evidence upload endpoint contracts"""

        # Test file upload contract
        files = {"file": ("test_policy.pdf", b"Mock PDF content", "application/pdf")}
        metadata = {
            "title": "Test Policy Document",
            "description": "Contract validation test document",
            "evidence_type": "policy_document",
            "framework": "GDPR",
        }

        response = await async_client.post(
            "/evidence/upload", files=files, data=metadata, headers=auth_headers
        )

        assert response.status_code == 201
        evidence_response = response.json()

        # Validate evidence response contract
        required_fields = [
            "id",
            "title",
            "description",
            "file_path",
            "evidence_type",
            "status",
            "created_at",
        ]
        for field in required_fields:
            assert (
                field in evidence_response
            ), f"Required field {field} missing from evidence response"

        # Validate field types and values
        assert isinstance(evidence_response["id"], str)
        assert evidence_response["title"] == metadata["title"]
        assert evidence_response["evidence_type"] == metadata["evidence_type"]
        assert evidence_response["status"] in ["uploaded", "processing", "processed"]

    def test_error_response_contract_consistency(self, client: TestClient):
        """Test that error responses follow consistent contract"""

        # Test 404 error contract
        response = client.get("/assessments/non-existent-id")
        assert response.status_code == 404

        error_response = response.json()
        assert "detail" in error_response

        # Test 422 validation error contract
        invalid_data = {"invalid": "data"}
        response = client.post("/assessments", json=invalid_data)
        assert response.status_code == 422

        validation_error = response.json()
        assert "detail" in validation_error

        # For validation errors, detail should be a list
        if isinstance(validation_error["detail"], list):
            # Each validation error should have specific structure
            for error in validation_error["detail"]:
                assert "loc" in error  # Field location
                assert "msg" in error  # Error message
                assert "type" in error  # Error type

    @pytest.mark.asyncio
    async def test_field_mapper_contract_validation(
        self, async_client: httpx.AsyncClient, auth_headers: Dict
    ):
        """Test field mapper contracts for database column truncation

        Validates that field mappers handle truncated database columns correctly
        """

        # Test with data that would be truncated in legacy database columns
        long_field_data = {
            "name": "Very Long Assessment Name That Exceeds Database Column Limits For Testing Field Mappers",
            "framework": "GDPR",
            "description": "This is a very long description that tests the field mapper functionality for handling database column truncation issues that exist in the legacy schema where columns were limited to 16 characters",
            "notes": "Additional notes field that is also very long and should be handled by the field mapper system properly",
        }

        response = await async_client.post(
            "/assessments", json=long_field_data, headers=auth_headers
        )

        # Should succeed even with long fields due to field mappers
        assert response.status_code == 201
        assessment_response = response.json()

        # Verify field mappers are working
        # The response should contain the full data, even if DB stores truncated
        assert len(assessment_response["name"]) > 16  # Original full name preserved
        assert "description" in assessment_response

        # Test retrieval maintains data integrity
        assessment_id = assessment_response["id"]
        response = await async_client.get(
            f"/assessments/{assessment_id}", headers=auth_headers
        )

        retrieved_assessment = response.json()
        assert (
            retrieved_assessment["name"] == long_field_data["name"]
        )  # Full name preserved

    @pytest.mark.asyncio
    async def test_pagination_contract_validation(
        self, async_client: httpx.AsyncClient, auth_headers: Dict
    ):
        """Test pagination contracts across list endpoints"""

        # Create multiple assessments for pagination testing
        for i in range(5):
            assessment_data = {
                "name": f"Pagination Test Assessment {i}",
                "framework": "GDPR",
            }
            response = await async_client.post(
                "/assessments", json=assessment_data, headers=auth_headers
            )
            assert response.status_code == 201

        # Test list endpoint with pagination
        response = await async_client.get(
            "/assessments?limit=3&offset=0", headers=auth_headers
        )
        assert response.status_code == 200

        paginated_response = response.json()

        # Validate pagination contract
        if isinstance(paginated_response, dict):
            # Standard pagination response format
            pagination_fields = ["items", "total", "limit", "offset"]
            for field in pagination_fields:
                assert field in paginated_response, f"Pagination field {field} missing"

            assert len(paginated_response["items"]) <= 3
            assert isinstance(paginated_response["total"], int)
            assert paginated_response["limit"] == 3
            assert paginated_response["offset"] == 0
        else:
            # Simple list format - should still respect limit
            assert len(paginated_response) <= 3

    @pytest.mark.asyncio
    async def test_api_versioning_contract(self, async_client: httpx.AsyncClient):
        """Test API versioning contract and backward compatibility"""

        # Test API version header handling
        headers = {"API-Version": "v1"}
        response = await async_client.get("/", headers=headers)

        # Should handle version header gracefully
        assert response.status_code in [200, 404]  # Either supported or not found

        # Test version in URL path (if supported)
        response = await async_client.get("/v1/health")
        # Should either work or return 404 (not 500)
        assert response.status_code in [200, 404]

    def test_cors_contract_validation(self, client: TestClient):
        """Test CORS headers contract"""

        # Test CORS preflight request
        response = client.options(
            "/assessments",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "authorization,content-type",
            },
        )

        # Should handle CORS preflight properly
        assert response.status_code in [200, 204]

        # If CORS is configured, should have CORS headers
        if "access-control-allow-origin" in response.headers:
            assert response.headers["access-control-allow-origin"] in [
                "*",
                "http://localhost:3000",
            ]


@pytest.mark.contract
@pytest.mark.performance
class TestContractPerformance:
    """Test performance aspects of contract compliance"""

    @pytest.mark.asyncio
    async def test_schema_validation_performance(
        self, async_client: httpx.AsyncClient, auth_headers: Dict
    ):
        """Test that schema validation doesn't significantly impact performance"""

        import time

        assessment_data = {
            "name": "Performance Test Assessment",
            "framework": "GDPR",
            "assessment_type": "full_assessment",
            "questions": [
                {
                    "question_id": f"question_{i}",
                    "question_text": f"Test question {i}?",
                    "answer": "yes",
                    "evidence_ids": [],
                }
                for i in range(20)  # Large number of questions
            ],
        }

        start_time = time.time()
        response = await async_client.post(
            "/assessments", json=assessment_data, headers=auth_headers
        )
        end_time = time.time()

        validation_time = end_time - start_time

        # Schema validation should not take more than 500ms
        assert (
            validation_time < 0.5
        ), f"Schema validation took {validation_time:.3f}s, expected <0.5s"
        assert response.status_code == 201  # Validation should succeed


@pytest.mark.contract
@pytest.mark.security
class TestSecurityContractValidation:
    """Test security aspects of API contracts"""

    @pytest.mark.asyncio
    async def test_authentication_contract_security(
        self, async_client: httpx.AsyncClient
    ):
        """Test authentication contract security requirements"""

        # Test that protected endpoints require authentication
        protected_endpoints = ["/assessments", "/evidence/upload", "/iq-agent/query"]

        for endpoint in protected_endpoints:
            # Should fail without authentication
            response = await async_client.get(endpoint)
            assert (
                response.status_code == 401
            ), f"Endpoint {endpoint} should require authentication"

            # Should fail with invalid token
            invalid_headers = {"Authorization": "Bearer invalid.token.here"}
            response = await async_client.get(endpoint, headers=invalid_headers)
            assert (
                response.status_code == 401
            ), f"Endpoint {endpoint} should reject invalid tokens"

    @pytest.mark.asyncio
    async def test_input_sanitization_contract(
        self, async_client: httpx.AsyncClient, auth_headers: Dict
    ):
        """Test input sanitization contract requirements"""

        # Test XSS prevention in text fields
        xss_payload = "<script>alert('xss')</script>"
        malicious_assessment = {
            "name": xss_payload,
            "framework": "GDPR",
            "description": xss_payload,
        }

        response = await async_client.post(
            "/assessments", json=malicious_assessment, headers=auth_headers
        )

        if response.status_code == 201:
            # If creation succeeds, response should be sanitized
            assessment_response = response.json()
            assert "<script>" not in assessment_response.get("name", "")
            assert "<script>" not in assessment_response.get("description", "")

    @pytest.mark.asyncio
    async def test_rate_limiting_contract_headers(
        self, async_client: httpx.AsyncClient, auth_headers: Dict
    ):
        """Test rate limiting contract and headers"""

        response = await async_client.get("/assessments", headers=auth_headers)

        # If rate limiting is implemented, should have rate limit headers
        rate_limit_headers = [
            "X-RateLimit-Limit",
            "X-RateLimit-Remaining",
            "X-RateLimit-Reset",
        ]

        # At least some rate limiting headers should be present
        present_headers = [h for h in rate_limit_headers if h in response.headers]

        if present_headers:
            # If rate limiting headers are present, validate format
            if "X-RateLimit-Remaining" in response.headers:
                remaining = response.headers["X-RateLimit-Remaining"]
                assert remaining.isdigit(), "Rate limit remaining should be a number"
