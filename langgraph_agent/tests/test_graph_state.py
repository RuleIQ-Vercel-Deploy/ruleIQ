"""
Tests for LangGraph state management.
Validates state creation, updates, and helper functions.
"""

from datetime import datetime
from uuid import uuid4

from langgraph_agent.graph.state import (
    create_initial_state,
    update_state_metadata,
    add_error_to_state,
    should_interrupt,
    get_state_summary,
)
from langgraph_agent.core.models import SafeFallbackResponse


class TestCreateInitialState:
    """Test initial state creation."""

    def test_create_basic_initial_state(self) -> None:
        """Test creating basic initial state."""
        company_id = uuid4()
        user_input = "What GDPR obligations apply to my retail business?"

        state = create_initial_state(company_id=company_id, user_input=user_input)

        assert state["company_id"] == company_id
        assert len(state["messages"]) == 1
        assert state["messages"][0].role == "user"
        assert state["messages"][0].content == user_input
        assert state["next_node"] == "router"
        assert state["current_node"] is None
        assert state["turn_count"] == 1
        assert state["error_count"] == 0
        assert state["autonomy_level"] == 2  # Default trusted_advisor

    def test_create_initial_state_with_full_params(self) -> None:
        """Test creating initial state with all parameters."""
        company_id = uuid4()
        user_id = uuid4()
        thread_id = "test_thread_123"
        user_input = "Help me with compliance"
        autonomy_level = 3

        state = create_initial_state(
            company_id=company_id,
            user_input=user_input,
            thread_id=thread_id,
            user_id=user_id,
            autonomy_level=autonomy_level,
        )

        assert state["thread_id"] == thread_id
        assert state["user_id"] == user_id
        assert state["autonomy_level"] == autonomy_level
        assert state["meta"]["session_id"] == thread_id

    def test_initial_state_timestamps(self) -> None:
        """Test timestamps are set correctly."""
        company_id = uuid4()
        before_creation = datetime.utcnow()

        state = create_initial_state(company_id=company_id, user_input="Test input")

        after_creation = datetime.utcnow()

        assert before_creation <= state["start_time"] <= after_creation
        assert before_creation <= state["last_updated"] <= after_creation
        assert before_creation <= state["messages"][0].timestamp <= after_creation


class TestUpdateStateMetadata:
    """Test state metadata updates."""

    def test_update_metadata_increments_turn_count(self) -> None:
        """Test metadata update increments turn count."""
        state = create_initial_state(company_id=uuid4(), user_input="Test")

        original_turn_count = state["turn_count"]
        original_time = state["last_updated"]

        updated_state = update_state_metadata(state)

        assert updated_state["turn_count"] == original_turn_count + 1
        assert updated_state["last_updated"] > original_time

    def test_update_metadata_preserves_other_fields(self) -> None:
        """Test metadata update doesn't change other fields."""
        state = create_initial_state(company_id=uuid4(), user_input="Test")

        original_company_id = state["company_id"]
        original_messages = state["messages"].copy()

        updated_state = update_state_metadata(state)

        assert updated_state["company_id"] == original_company_id
        assert len(updated_state["messages"]) == len(original_messages)


class TestAddErrorToState:
    """Test error handling in state."""

    def test_add_error_to_state(self) -> None:
        """Test adding error to state."""
        state = create_initial_state(company_id=uuid4(), user_input="Test")

        error = SafeFallbackResponse(
            error_message="Test error occurred", error_details={"field": "test_field"}
        )

        original_error_count = state["error_count"]
        updated_state = add_error_to_state(state, error)

        assert len(updated_state["errors"]) == 1
        assert updated_state["errors"][0] == error
        assert updated_state["error_count"] == original_error_count + 1

    def test_multiple_errors_accumulate(self) -> None:
        """Test multiple errors accumulate correctly."""
        state = create_initial_state(company_id=uuid4(), user_input="Test")

        error1 = SafeFallbackResponse(error_message="First error", error_details={})

        error2 = SafeFallbackResponse(error_message="Second error", error_details={})

        state = add_error_to_state(state, error1)
        state = add_error_to_state(state, error2)

        assert len(state["errors"]) == 2
        assert state["error_count"] == 2
        assert state["errors"][0].error_message == "First error"
        assert state["errors"][1].error_message == "Second error"


class TestShouldInterrupt:
    """Test interrupt logic."""

    def test_should_interrupt_with_explicit_interrupt(self) -> None:
        """Test interrupt when explicitly requested."""
        state = create_initial_state(company_id=uuid4(), user_input="Test")

        state["interrupt_before"] = "legal_reviewer"

        assert should_interrupt(state, "legal_reviewer") is True
        assert should_interrupt(state, "compliance_analyzer") is False

    def test_should_interrupt_with_human_review(self) -> None:
        """Test interrupt when human review required."""
        state = create_initial_state(company_id=uuid4(), user_input="Test")

        state["requires_human_review"] = True

        assert should_interrupt(state, "any_node") is True

    def test_should_interrupt_with_error_threshold(self) -> None:
        """Test interrupt when error threshold exceeded."""
        state = create_initial_state(company_id=uuid4(), user_input="Test")

        # Add 3 errors to hit threshold
        for i in range(3):
            error = SafeFallbackResponse(error_message=f"Error {i}", error_details={})
            state = add_error_to_state(state, error)

        assert should_interrupt(state, "any_node") is True

    def test_should_interrupt_with_turn_limit(self) -> None:
        """Test interrupt when turn limit exceeded."""
        state = create_initial_state(company_id=uuid4(), user_input="Test")

        state["turn_count"] = 20  # Hit turn limit

        assert should_interrupt(state, "any_node") is True

    def test_should_not_interrupt_normal_conditions(self) -> None:
        """Test no interrupt under normal conditions."""
        state = create_initial_state(company_id=uuid4(), user_input="Test")

        assert should_interrupt(state, "any_node") is False


class TestGetStateSummary:
    """Test state summary generation."""

    def test_get_basic_state_summary(self) -> None:
        """Test basic state summary generation."""
        company_id = uuid4()
        state = create_initial_state(company_id=company_id, user_input="Test input")

        summary = get_state_summary(state)

        assert summary["company_id"] == str(company_id)
        assert summary["turn_count"] == 1
        assert summary["message_count"] == 1
        assert summary["current_node"] is None
        assert summary["next_node"] == "router"
        assert summary["route"] is None
        assert summary["error_count"] == 0
        assert summary["tool_call_count"] == 0
        assert summary["autonomy_level"] == 2
        assert summary["requires_review"] is False

    def test_get_state_summary_with_route(self) -> None:
        """Test state summary with route decision."""
        from langgraph_agent.core.models import RouteDecision

        state = create_initial_state(company_id=uuid4(), user_input="Test input")

        route = RouteDecision(
            route="compliance_analyzer",
            confidence=0.95,
            reasoning="High confidence match",
            method="rules",
            input_text="Test input",
            company_id=state["company_id"],
        )

        state["route"] = route
        state["selected_frameworks"] = ["GDPR", "UK_GDPR"]

        summary = get_state_summary(state)

        assert summary["route"] == "compliance_analyzer"
        assert summary["frameworks"] == ["GDPR", "UK_GDPR"]

    def test_get_state_summary_with_obligations_and_evidence(self) -> None:
        """Test state summary with obligations and evidence."""
        from langgraph_agent.core.models import (
            Obligation,
            EvidenceItem,
            ComplianceFramework,
            EvidenceType,
        )

        state = create_initial_state(company_id=uuid4(), user_input="Test input")

        # Add mock obligation
        obligation = Obligation(
            obligation_id="GDPR_DATA_001",
            framework=ComplianceFramework.GDPR,
            title="Test Obligation",
            description="Test description",
            category="data_processing",
        )
        state["relevant_obligations"] = [obligation]

        # Add mock evidence
        evidence = EvidenceItem(
            company_id=state["company_id"],
            title="Test Evidence",
            evidence_type=EvidenceType.POLICY_DOCUMENT,
            created_by=uuid4(),
        )
        state["collected_evidence"] = [evidence]

        summary = get_state_summary(state)

        assert summary["obligations_found"] == 1
        assert summary["evidence_collected"] == 1
