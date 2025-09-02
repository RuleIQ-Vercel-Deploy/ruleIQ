"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Sprint Management Demo for ruleIQ Project
Demonstrates the complete sprint management system functionality
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from sprint_management import SprintManager, Priority, StoryStatus


def demo_sprint_management() ->None:
    """Comprehensive demonstration of sprint management capabilities"""
    logger.info('🚀 ruleIQ Sprint Management System Demo')
    logger.info('=' * 60)
    logger.info()
    manager = SprintManager(data_dir='.demo_sprint_data')
    logger.info('📋 STEP 1: Initialize Sprint')
    logger.info('-' * 30)
    sprint_data = {'id': 'demo_sprint_2', 'name':
        'Sprint 2: Evidence Classification & Design System', 'goal':
        'Complete RBAC, implement evidence auto-classification, and finalize teal design system migration'
        , 'start_date': '2025-08-01', 'end_date': '2025-08-15',
        'capacity_hours': 120.0, 'velocity_target': 40, 'team_members': [
        'Lead Developer', 'Frontend Developer', 'AI Engineer']}
    sprint = manager.init_sprint(sprint_data)
    logger.info("✅ Sprint '%s' initialized" % sprint.name)
    logger.info('   📅 Duration: %s to %s' % (sprint.start_date, sprint.
        end_date))
    logger.info('   🎯 Goal: %s' % sprint.goal)
    logger.info('   👥 Team: %s' % ', '.join(sprint.team_members))
    logger.info()
    logger.info('📝 STEP 2: Generate User Stories')
    logger.info('-' * 30)
    stories = manager.generate_sprint_stories(sprint.id, {})
    logger.info('✅ Generated %s user stories based on ruleIQ roadmap:' %
        len(stories))
    for story in stories:
        priority_icon = {Priority.CRITICAL: '🔴', Priority.HIGH: '🟠',
            Priority.MEDIUM: '🟡', Priority.LOW: '🟢'}
        logger.info('   %s %s: %s' % (priority_icon[story.priority], story.
            id, story.title))
        print(
            f'      📊 {story.story_points} points | ⏱️ {story.estimated_hours}h | 🏷️ {story.feature_area}',
            )
    logger.info()
    logger.info('🔍 STEP 3: Analyze Stories')
    logger.info('-' * 30)
    analysis = manager.analyze_stories(stories)
    logger.info('📊 Analysis Results:')
    logger.info('   📝 Total Stories: %s' % analysis['total_stories'])
    logger.info('   📊 Total Story Points: %s' % analysis['total_story_points'])
    logger.info('   ⏱️  Total Hours: %s' % analysis['total_estimated_hours'])
    logger.info()
    logger.info('🔥 Priority Distribution:')
    for priority, count in analysis['priority_breakdown'].items():
        if count > 0:
            logger.info('   %s: %s stories' % (priority, count))
    logger.info()
    logger.info('🏗️ Feature Areas:')
    for area, data in analysis['feature_area_breakdown'].items():
        logger.info('   %s: %s stories (%s pts)' % (area, data['count'],
            data['story_points']))
    logger.info()
    if analysis['recommendations']:
        logger.info('💡 Recommendations:')
        for rec in analysis['recommendations']:
            logger.info('   • %s' % rec)
        logger.info()
    logger.info('🔧 STEP 4: Decompose Stories into Tasks')
    logger.info('-' * 30)
    decomposed_stories = manager.decompose_stories(stories)
    for i, story in enumerate(decomposed_stories[:2]):
        if story.tasks:
            logger.info('📖 %s: %s' % (story.id, story.title))
            logger.info('   ✅ Decomposed into %s implementation tasks:' %
                len(story.tasks))
            for task in story.tasks:
                logger.info('      • %s: %s (%sh)' % (task.id, task.title,
                    task.estimated_hours))
            logger.info()
    logger.info('📈 STEP 5: Track Sprint Progress')
    logger.info('-' * 30)
    stories[0].status = StoryStatus.DONE
    stories[0].actual_hours = 30.0
    stories[1].status = StoryStatus.IN_PROGRESS
    stories[1].actual_hours = 15.0
    logger.info('📊 Sprint Progress Update:')
    logger.info('   ✅ RBAC System: COMPLETED (%s points)' % stories[0].
        story_points)
    logger.info('   🔄 Design System: IN PROGRESS (%s points)' % stories[1].
        story_points)
    logger.info('   ⏳ Evidence Classifier: PENDING (%s points)' % stories[2
        ].story_points)
    logger.info()
    completed_points = sum(s.story_points for s in stories if s.status ==
        StoryStatus.DONE)
    total_points = sum(s.story_points for s in stories)
    completion_rate = completed_points / total_points * 100
    print(
        f'📊 Overall Progress: {completed_points}/{total_points} points ({completion_rate:.1f}%)',
        )
    logger.info()
    logger.info('💡 STEP 6: Sprint Recommendations')
    logger.info('-' * 30)
    recommendations = ['✅ RBAC completion puts sprint ahead of schedule',
        '🎨 Focus on design system testing to ensure quality',
        '🤖 Begin evidence classifier development early',
        '📊 Consider parallel testing of completed features',
        '⚠️  Monitor scope creep on design system migration']
    logger.info('Based on current progress and project context:')
    for rec in recommendations:
        logger.info('   %s' % rec)
    logger.info()
    logger.info('🎯 STEP 7: Next Sprint Planning')
    logger.info('-' * 30)
    next_sprint_items = ['🚀 Sprint 3: Advanced Features & Polish',
        '📊 Compliance Insights Engine enhancement',
        '🔍 Advanced evidence analysis capabilities',
        '📈 Performance optimization and monitoring',
        '🧪 Comprehensive end-to-end testing',
        '📱 Mobile responsiveness improvements']
    logger.info('Potential Sprint 3 priorities:')
    for item in next_sprint_items:
        logger.info('   %s' % item)
    logger.info()
    logger.info('🎉 Demo Complete!')
    logger.info('=' * 60)
    logger.info('Sprint management system successfully demonstrated!')
    logger.info()
    logger.info('📁 Demo data saved to: .demo_sprint_data/')
    logger.info('🔧 Run individual commands:')
    logger.info('   python sprint_cli.py status')
    logger.info('   python sprint_cli.py generate-stories')
    logger.info('   python sprint_cli.py analyze-stories')
    logger.info('   python sprint_cli.py decompose-stories')


def demo_cli_commands() ->None:
    """Demonstrate CLI command usage"""
    logger.info('\n🖥️  CLI Commands Demo')
    logger.info('=' * 40)
    commands = [('python sprint_cli.py status',
        'Show current project status'), ('python sprint_cli.py init-sprint',
        'Initialize new sprint'), ('python sprint_cli.py generate-stories',
        'Generate user stories'), ('python sprint_cli.py analyze-stories',
        'Analyze story risks'), ('python sprint_cli.py decompose-stories',
        'Break down into tasks'), ('python sprint_cli.py track-progress',
        'Track implementation progress')]
    logger.info('Available CLI commands:')
    for cmd, description in commands:
        logger.info('   %s' % cmd)
        logger.info('      %s' % description)
        logger.info()


if __name__ == '__main__':
    try:
        demo_sprint_management()
        demo_cli_commands()
    except KeyboardInterrupt:
        logger.info('\n\n👋 Demo interrupted by user')
    except Exception as e:
        logger.info('\n❌ Demo error: %s' % e)
        import traceback
        traceback.print_exc()
