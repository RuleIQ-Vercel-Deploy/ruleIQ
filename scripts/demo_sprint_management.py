#!/usr/bin/env python3
"""
Sprint Management Demo for ruleIQ Project
Demonstrates the complete sprint management system functionality
"""

import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sprint_management import SprintManager, Priority, StoryStatus


def demo_sprint_management() -> None:
    """Comprehensive demonstration of sprint management capabilities"""

    print("🚀 ruleIQ Sprint Management System Demo")
    print("=" * 60)
    print()

    # Initialize the sprint manager
    manager = SprintManager(data_dir=".demo_sprint_data")

    # Step 1: Initialize Sprint
    print("📋 STEP 1: Initialize Sprint")
    print("-" * 30)

    sprint_data = {
        "id": "demo_sprint_2",
        "name": "Sprint 2: Evidence Classification & Design System",
        "goal": "Complete RBAC, implement evidence auto-classification, and finalize teal design system migration",
        "start_date": "2025-08-01",
        "end_date": "2025-08-15",
        "capacity_hours": 120.0,
        "velocity_target": 40,
        "team_members": ["Lead Developer", "Frontend Developer", "AI Engineer"],
    }

    sprint = manager.init_sprint(sprint_data)
    print(f"✅ Sprint '{sprint.name}' initialized")
    print(f"   📅 Duration: {sprint.start_date} to {sprint.end_date}")
    print(f"   🎯 Goal: {sprint.goal}")
    print(f"   👥 Team: {', '.join(sprint.team_members)}")
    print()

    # Step 2: Generate Stories
    print("📝 STEP 2: Generate User Stories")
    print("-" * 30)

    stories = manager.generate_sprint_stories(sprint.id, {})
    print(f"✅ Generated {len(stories)} user stories based on ruleIQ roadmap:")

    for story in stories:
        priority_icon = {
            Priority.CRITICAL: "🔴",
            Priority.HIGH: "🟠",
            Priority.MEDIUM: "🟡",
            Priority.LOW: "🟢",
        }
        print(f"   {priority_icon[story.priority]} {story.id}: {story.title}")
        print(
            f"      📊 {story.story_points} points | ⏱️ {story.estimated_hours}h | 🏷️ {story.feature_area}"
        )
    print()

    # Step 3: Analyze Stories
    print("🔍 STEP 3: Analyze Stories")
    print("-" * 30)

    analysis = manager.analyze_stories(stories)
    print("📊 Analysis Results:")
    print(f"   📝 Total Stories: {analysis['total_stories']}")
    print(f"   📊 Total Story Points: {analysis['total_story_points']}")
    print(f"   ⏱️  Total Hours: {analysis['total_estimated_hours']}")
    print()

    print("🔥 Priority Distribution:")
    for priority, count in analysis["priority_breakdown"].items():
        if count > 0:
            print(f"   {priority}: {count} stories")
    print()

    print("🏗️ Feature Areas:")
    for area, data in analysis["feature_area_breakdown"].items():
        print(f"   {area}: {data['count']} stories ({data['story_points']} pts)")
    print()

    if analysis["recommendations"]:
        print("💡 Recommendations:")
        for rec in analysis["recommendations"]:
            print(f"   • {rec}")
        print()

    # Step 4: Decompose Stories
    print("🔧 STEP 4: Decompose Stories into Tasks")
    print("-" * 30)

    decomposed_stories = manager.decompose_stories(stories)

    # Show decomposition for first two stories as example
    for i, story in enumerate(decomposed_stories[:2]):
        if story.tasks:
            print(f"📖 {story.id}: {story.title}")
            print(f"   ✅ Decomposed into {len(story.tasks)} implementation tasks:")

            for task in story.tasks:
                print(f"      • {task.id}: {task.title} ({task.estimated_hours}h)")
            print()

    # Step 5: Track Progress (Mock)
    print("📈 STEP 5: Track Sprint Progress")
    print("-" * 30)

    # Simulate some progress
    stories[0].status = StoryStatus.DONE  # RBAC completed
    stories[0].actual_hours = 30.0
    stories[1].status = StoryStatus.IN_PROGRESS  # Design system in progress
    stories[1].actual_hours = 15.0

    print("📊 Sprint Progress Update:")
    print(f"   ✅ RBAC System: COMPLETED ({stories[0].story_points} points)")
    print(f"   🔄 Design System: IN PROGRESS ({stories[1].story_points} points)")
    print(f"   ⏳ Evidence Classifier: PENDING ({stories[2].story_points} points)")
    print()

    completed_points = sum(
        s.story_points for s in stories if s.status == StoryStatus.DONE
    )
    total_points = sum(s.story_points for s in stories)
    completion_rate = (completed_points / total_points) * 100

    print(
        f"📊 Overall Progress: {completed_points}/{total_points} points ({completion_rate:.1f}%)"
    )
    print()

    # Step 6: Show Recommendations
    print("💡 STEP 6: Sprint Recommendations")
    print("-" * 30)

    recommendations = [
        "✅ RBAC completion puts sprint ahead of schedule",
        "🎨 Focus on design system testing to ensure quality",
        "🤖 Begin evidence classifier development early",
        "📊 Consider parallel testing of completed features",
        "⚠️  Monitor scope creep on design system migration",
    ]

    print("Based on current progress and project context:")
    for rec in recommendations:
        print(f"   {rec}")
    print()

    # Step 7: Next Steps
    print("🎯 STEP 7: Next Sprint Planning")
    print("-" * 30)

    next_sprint_items = [
        "🚀 Sprint 3: Advanced Features & Polish",
        "📊 Compliance Insights Engine enhancement",
        "🔍 Advanced evidence analysis capabilities",
        "📈 Performance optimization and monitoring",
        "🧪 Comprehensive end-to-end testing",
        "📱 Mobile responsiveness improvements",
    ]

    print("Potential Sprint 3 priorities:")
    for item in next_sprint_items:
        print(f"   {item}")
    print()

    print("🎉 Demo Complete!")
    print("=" * 60)
    print("Sprint management system successfully demonstrated!")
    print()
    print("📁 Demo data saved to: .demo_sprint_data/")
    print("🔧 Run individual commands:")
    print("   python sprint_cli.py status")
    print("   python sprint_cli.py generate-stories")
    print("   python sprint_cli.py analyze-stories")
    print("   python sprint_cli.py decompose-stories")


def demo_cli_commands() -> None:
    """Demonstrate CLI command usage"""
    print("\n🖥️  CLI Commands Demo")
    print("=" * 40)

    commands = [
        ("python sprint_cli.py status", "Show current project status"),
        ("python sprint_cli.py init-sprint", "Initialize new sprint"),
        ("python sprint_cli.py generate-stories", "Generate user stories"),
        ("python sprint_cli.py analyze-stories", "Analyze story risks"),
        ("python sprint_cli.py decompose-stories", "Break down into tasks"),
        ("python sprint_cli.py track-progress", "Track implementation progress"),
    ]

    print("Available CLI commands:")
    for cmd, description in commands:
        print(f"   {cmd}")
        print(f"      {description}")
        print()


if __name__ == "__main__":
    try:
        demo_sprint_management()
        demo_cli_commands()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback

        traceback.print_exc()
