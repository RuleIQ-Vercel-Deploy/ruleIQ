"""
LangSmith monitoring setup for debugging the question loop issue.
"""

import os


def setup_langsmith_monitoring():
    """Set up LangSmith monitoring for the assessment agent."""
    print("🔍 Setting up LangSmith monitoring for loop prevention...")

    # Check LangSmith configuration
    api_key = os.getenv("LANGCHAIN_API_KEY")
    project = os.getenv("LANGCHAIN_PROJECT", "ruleiq-assessment")
    tracing_enabled = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"

    print(f"LangSmith Project: {project}")
    print(f"Tracing Enabled: {tracing_enabled}")
    print(f"API Key Present: {'Yes' if api_key else 'No'}")

    return api_key is not None


def main() -> None:
    """Set up LangSmith monitoring."""
    print("🚀 LangSmith Monitoring Setup")
    success = setup_langsmith_monitoring()

    print("\n📋 Monitoring Tags in Enhanced Assessment Agent:")
    print("• detection_level: immediate_repetition")
    print("• detection_level: pattern_repetition")
    print("• detection_level: unanswered_accumulation")
    print("• loop_prevention_version: v3_enhanced")
    print("• routing_decision: continue/complete/error")

    if success:
        print("\n✅ LangSmith monitoring ready!")
    else:
        print("\n⚠️  Set LANGCHAIN_API_KEY to enable monitoring")


if __name__ == "__main__":
    main()
