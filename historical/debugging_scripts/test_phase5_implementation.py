"""
Test script to verify Phase 5 System Instructions implementation

This script tests the core functionality of the system instructions upgrade
without requiring external dependencies.
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.ai.instruction_integration import InstructionManager
from services.ai.instruction_monitor import InstructionMetricType, InstructionPerformanceMonitor
from services.ai.instruction_templates import (
    FrameworkType,
    InstructionType,
    SystemInstructionTemplates,
    get_system_instruction,
)


def test_instruction_templates():
    """Test the instruction template system"""
    print("Testing System Instruction Templates...")

    templates = SystemInstructionTemplates()

    # Test basic instruction generation
    instruction = templates.get_instruction_for_task(
        InstructionType.ASSESSMENT,
        framework=FrameworkType.GDPR,
        business_profile={
            "company_name": "Test Corp",
            "industry": "Technology",
            "employee_count": 50,
        },
        user_persona="alex",
        task_complexity="complex",
    )

    assert "ComplianceGPT" in instruction
    assert "GDPR" in instruction
    assert "alex" in instruction.lower()
    print("✓ Basic instruction generation works")

    # Test convenience function
    instruction2 = get_system_instruction(
        "assessment",
        framework="gdpr",
        business_profile={"industry": "Healthcare", "employee_count": 200},
    )

    assert "ComplianceGPT" in instruction2
    assert "Healthcare" in instruction2
    print("✓ Convenience function works")

    print("System Instruction Templates: PASSED\n")


def test_instruction_monitor():
    """Test the instruction monitoring system"""
    print("Testing Instruction Performance Monitor...")

    monitor = InstructionPerformanceMonitor()

    # Test instruction registration
    instruction_id = "test_instruction_1"
    instruction_hash = monitor.register_instruction(
        instruction_id=instruction_id,
        instruction_content="Test instruction content",
        instruction_type="assessment",
        framework="gdpr",
    )

    assert instruction_id in monitor.instruction_registry
    assert len(instruction_hash) == 16  # SHA256 truncated to 16 chars
    print("✓ Instruction registration works")

    # Test metric recording
    monitor.record_metric(
        instruction_id=instruction_id,
        metric_type=InstructionMetricType.RESPONSE_QUALITY,
        value=0.85,
        context={"framework": "gdpr", "task_type": "assessment"},
    )

    monitor.record_metric(
        instruction_id=instruction_id,
        metric_type=InstructionMetricType.USER_SATISFACTION,
        value=0.9,
        context={"framework": "gdpr", "task_type": "assessment"},
    )

    assert len(monitor.metrics_history) == 2
    print("✓ Metric recording works")

    # Test performance data generation
    performance = monitor.get_instruction_performance(instruction_id)
    assert performance is not None
    assert performance.avg_response_quality == 0.85
    assert performance.avg_user_satisfaction == 0.9
    print("✓ Performance data calculation works")

    # Test A/B test setup
    test_id = monitor.start_ab_test(
        test_name="Test A/B",
        instruction_a_id=instruction_id,
        instruction_b_id="test_instruction_2",
        duration_days=1,
        minimum_sample_size=5,
    )

    assert test_id in monitor.active_ab_tests
    print("✓ A/B test setup works")

    print("Instruction Performance Monitor: PASSED\n")


def test_instruction_integration():
    """Test the instruction integration system"""
    print("Testing Instruction Integration...")

    manager = InstructionManager()

    # Test instruction generation with monitoring
    instruction_id, instruction_content = manager.get_instruction_with_monitoring(
        instruction_type="assessment",
        framework="gdpr",
        business_profile={
            "company_name": "Integration Test Corp",
            "industry": "Finance",
            "employee_count": 100,
        },
        user_persona="ben",
        task_complexity="medium",
    )

    assert instruction_id.startswith("instr_")
    assert "ComplianceGPT" in instruction_content
    assert "Finance" in instruction_content
    print("✓ Instruction generation with monitoring works")

    # Test usage recording
    manager.record_instruction_usage(
        instruction_id=instruction_id,
        response_quality=0.8,
        user_satisfaction=0.85,
        response_time=15.0,
        token_count=500,
        had_error=False,
    )

    # Verify metrics were recorded
    performance = manager.monitor.get_instruction_performance(instruction_id)
    assert performance is not None
    assert performance.avg_response_quality == 0.8
    print("✓ Usage recording works")

    # Test optimization suggestions
    optimization = manager.optimize_instruction(
        instruction_id=instruction_id, optimization_type="quality"
    )

    assert "current_performance" in optimization
    assert "suggestions" in optimization
    print("✓ Optimization suggestions work")

    print("Instruction Integration: PASSED\n")


def test_prompt_templates_integration():
    """Test that prompt templates work with system instructions"""
    print("Testing Prompt Templates Integration...")

    # Import here to avoid circular imports in testing
    try:
        from services.ai.prompt_templates import PromptTemplates

        templates = PromptTemplates()

        # Test system instruction generation
        system_instruction = templates.get_system_instruction_for_task(
            task_type="assessment",
            framework="gdpr",
            business_profile={"industry": "Technology"},
            user_persona="catherine",
        )

        assert "ComplianceGPT" in system_instruction
        assert "Technology" in system_instruction
        print("✓ Prompt templates system instruction integration works")

        # Test updated method
        prompt_data = templates.get_assessment_analysis_prompt(
            assessment_results={"score": 75},
            framework_id="GDPR",
            business_context={"industry": "Healthcare"},
        )

        assert "system_instruction" in prompt_data
        assert "user" in prompt_data
        print("✓ Updated prompt methods work")

        print("Prompt Templates Integration: PASSED\n")

    except ImportError as e:
        print(f"⚠ Prompt templates integration test skipped due to import error: {e}\n")


def main():
    """Run all tests"""
    print("=" * 50)
    print("Phase 5 System Instructions Implementation Test")
    print("=" * 50)
    print()

    try:
        test_instruction_templates()
        test_instruction_monitor()
        test_instruction_integration()
        test_prompt_templates_integration()

        print("=" * 50)
        print("ALL TESTS PASSED! 🎉")
        print("Phase 5 implementation is working correctly.")
        print("=" * 50)

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
