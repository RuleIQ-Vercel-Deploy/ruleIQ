"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

ruleIQ Sprint Management System
Comprehensive sprint planning, tracking, and delivery management for the ruleIQ project.
"""

import json
import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import os

class Priority(Enum):
    CRITICAL = 'CRITICAL'
    """Class for Priority"""
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    LOW = 'LOW'

class StoryStatus(Enum):
    PENDING = 'PENDING'
    """Class for StoryStatus"""
    IN_PROGRESS = 'IN_PROGRESS'
    BLOCKED = 'BLOCKED'
    TESTING = 'TESTING'
    DONE = 'DONE'

class TaskType(Enum):
    FEATURE = 'FEATURE'
    """Class for TaskType"""
    BUG = 'BUG'
    TECHNICAL = 'TECHNICAL'
    DESIGN = 'DESIGN'
    TESTING = 'TESTING'
    DOCUMENTATION = 'DOCUMENTATION'

@dataclass
class AcceptanceCriteria:
    """Acceptance criteria for user stories"""
    description: str
    testable: bool = True
    automated_test: Optional[str] = None

@dataclass
class Task:
    """Individual implementation task"""
    id: str
    title: str
    description: str
    type: TaskType
    story_id: str
    estimated_hours: float
    assigned_to: Optional[str] = None
    status: StoryStatus = StoryStatus.PENDING
    dependencies: List[str] = None
    technical_notes: Optional[str] = None
    created_at: datetime.datetime = None

    def __post_init__(self) ->None:
        if self.dependencies is None:
            self.dependencies = []
        if self.created_at is None:
            self.created_at = datetime.datetime.now()

@dataclass
class UserStory:
    """User story with acceptance criteria and tasks"""
    id: str
    title: str
    description: str
    priority: Priority
    story_points: int
    feature_area: str
    acceptance_criteria: List[AcceptanceCriteria]
    tasks: List[Task] = None
    status: StoryStatus = StoryStatus.PENDING
    dependencies: List[str] = None
    technical_complexity: str = 'MEDIUM'
    estimated_hours: float = 0.0
    actual_hours: float = 0.0
    sprint_id: Optional[str] = None
    assigned_to: Optional[str] = None
    created_at: datetime.datetime = None

    def __post_init__(self) ->None:
        if self.tasks is None:
            self.tasks = []
        if self.dependencies is None:
            self.dependencies = []
        if self.created_at is None:
            self.created_at = datetime.datetime.now()

@dataclass
class Sprint:
    """Sprint definition with goals and capacity"""
    id: str
    name: str
    goal: str
    start_date: datetime.date
    end_date: datetime.date
    capacity_hours: float
    team_members: List[str]
    stories: List[UserStory] = None
    status: str = 'PLANNING'
    velocity_target: int = 0
    actual_velocity: int = 0
    retrospective_notes: Optional[str] = None
    created_at: datetime.datetime = None

    def __post_init__(self) ->None:
        if self.stories is None:
            self.stories = []
        if self.created_at is None:
            self.created_at = datetime.datetime.now()

class SprintManager:
    """Main sprint management system"""

    def __init__(self, data_dir: str='.sprint_data') ->None:
        self.data_dir = data_dir
        self.ensure_data_dir()

    def ensure_data_dir(self) ->None:
        """Ensure sprint data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)

    def init_sprint(self, sprint_data: Dict[str, Any]) ->Sprint:
        """Initialize a new sprint"""
        sprint = Sprint(id=sprint_data.get('id',
            f"sprint_{datetime.datetime.now().strftime('%Y%m%d')}"), name=
            sprint_data.get('name', 'New Sprint'), goal=sprint_data.get(
            'goal', 'Deliver high-priority features'), start_date=datetime.
            datetime.strptime(sprint_data.get('start_date'), '%Y-%m-%d').
            date(), end_date=datetime.datetime.strptime(sprint_data.get(
            'end_date'), '%Y-%m-%d').date(), capacity_hours=sprint_data.get
            ('capacity_hours', 80.0), team_members=sprint_data.get(
            'team_members', ['Development Team']), velocity_target=
            sprint_data.get('velocity_target', 20))
        self._save_sprint(sprint)
        return sprint

    def generate_sprint_stories(self, sprint_id: str, roadmap_context: Dict
        [str, Any]) ->List[UserStory]:
        """Generate user stories for the sprint based on roadmap and priorities"""
        stories = []
        rbac_story = UserStory(id='STORY-001', title=
            'Complete RBAC System Implementation', description=
            'As a system administrator, I want a complete role-based access control system so that users have appropriate permissions for their roles.'
            , priority=Priority.CRITICAL, story_points=8, feature_area=
            'Authentication & Authorization', acceptance_criteria=[
            AcceptanceCriteria('Admin can create and manage roles'),
            AcceptanceCriteria('Admin can assign permissions to roles'),
            AcceptanceCriteria(
            'Users are automatically assigned permissions based on roles'),
            AcceptanceCriteria(
            'API endpoints are protected by RBAC middleware'),
            AcceptanceCriteria('Audit logs capture all permission changes')
            ], technical_complexity='HIGH', estimated_hours=32.0)
        stories.append(rbac_story)
        design_story = UserStory(id='STORY-002', title=
            'Complete Teal Design System Migration', description=
            'As a user, I want a consistent teal-branded interface so that the application feels professional and trustworthy.'
            , priority=Priority.HIGH, story_points=13, feature_area=
            'Frontend Design System', acceptance_criteria=[
            AcceptanceCriteria(
            'All purple and cyan colors replaced with teal variants'),
            AcceptanceCriteria(
            'Aceternity components removed from codebase'),
            AcceptanceCriteria(
            'Feature flag NEXT_PUBLIC_USE_NEW_THEME implemented'),
            AcceptanceCriteria('WCAG 2.2 AA compliance maintained'),
            AcceptanceCriteria('Bundle size increase <5%')],
            technical_complexity='MEDIUM', estimated_hours=40.0)
        stories.append(design_story)
        evidence_story = UserStory(id='STORY-003', title=
            'AI Evidence Auto-Classification System', description=
            'As a compliance professional, I want uploaded evidence to be automatically classified and mapped to controls so that I can efficiently build my compliance portfolio.'
            , priority=Priority.HIGH, story_points=21, feature_area=
            'Evidence Management', acceptance_criteria=[AcceptanceCriteria(
            'AI classifies uploaded documents by type and relevance'),
            AcceptanceCriteria(
            'Evidence is automatically mapped to relevant framework controls'
            ), AcceptanceCriteria(
            'Classification confidence scores are displayed'),
            AcceptanceCriteria('Users can override AI classifications'),
            AcceptanceCriteria(
            'Bulk processing handles multiple files efficiently')],
            technical_complexity='HIGH', estimated_hours=64.0)
        stories.append(evidence_story)
        insights_story = UserStory(id='STORY-004', title=
            'Compliance Insights and Analytics Engine', description=
            'As a business owner, I want intelligent insights about my compliance status so that I can make informed decisions about risk management.'
            , priority=Priority.MEDIUM, story_points=13, feature_area=
            'Analytics & Insights', acceptance_criteria=[AcceptanceCriteria
            ('Dashboard shows compliance score trends over time'),
            AcceptanceCriteria(
            'System identifies compliance gaps and priorities'),
            AcceptanceCriteria('AI provides actionable recommendations'),
            AcceptanceCriteria('Export capabilities for compliance reports'
            ), AcceptanceCriteria(
            'Real-time alerts for critical compliance issues')],
            technical_complexity='MEDIUM', estimated_hours=40.0)
        stories.append(insights_story)
        performance_story = UserStory(id='STORY-005', title=
            'API Performance Optimization and Monitoring', description=
            'As a system administrator, I want optimized API performance with comprehensive monitoring so that the system meets SLA requirements.'
            , priority=Priority.MEDIUM, story_points=8, feature_area=
            'Infrastructure', acceptance_criteria=[AcceptanceCriteria(
            'All API endpoints respond within 200ms SLA'),
            AcceptanceCriteria(
            'Database queries are optimized with proper indexing'),
            AcceptanceCriteria(
            'Comprehensive performance monitoring dashboard'),
            AcceptanceCriteria(
            'Automated alerts for performance degradation'),
            AcceptanceCriteria(
            'Load testing validates performance under stress')],
            technical_complexity='MEDIUM', estimated_hours=24.0)
        stories.append(performance_story)
        return stories

    def analyze_stories(self, stories: List[UserStory]) ->Dict[str, Any]:
        """Analyze user stories for completeness and feasibility"""
        analysis = {'total_stories': len(stories), 'total_story_points':
            sum(story.story_points for story in stories),
            'total_estimated_hours': sum(story.estimated_hours for story in
            stories), 'priority_breakdown': {}, 'complexity_breakdown': {},
            'feature_area_breakdown': {}, 'recommendations': [], 'risks': [
            ], 'dependencies': []}
        for priority in Priority:
            count = len([s for s in stories if s.priority == priority])
            analysis['priority_breakdown'][priority.value] = count
        complexities = [s.technical_complexity for s in stories]
        for complexity in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
            count = complexities.count(complexity)
            analysis['complexity_breakdown'][complexity] = count
        feature_areas = {}
        for story in stories:
            area = story.feature_area
            if area not in feature_areas:
                feature_areas[area] = {'count': 0, 'story_points': 0,
                    'hours': 0}
            feature_areas[area]['count'] += 1
            feature_areas[area]['story_points'] += story.story_points
            feature_areas[area]['hours'] += story.estimated_hours
        analysis['feature_area_breakdown'] = feature_areas
        if analysis['total_story_points'] > 50:
            analysis['recommendations'].append(
                'Consider splitting sprint - current scope exceeds typical team capacity',
                )
        critical_stories = [s for s in stories if s.priority == Priority.
            CRITICAL]
        if len(critical_stories) > 2:
            analysis['recommendations'].append(
                'Too many critical priority stories - consider prioritization')
        high_complexity_stories = [s for s in stories if s.
            technical_complexity == 'CRITICAL']
        if len(high_complexity_stories) > 1:
            analysis['risks'].append(
                'Multiple critical complexity stories increase sprint risk')
        all_story_ids = [s.id for s in stories]
        for story in stories:
            for dep in story.dependencies:
                if dep not in all_story_ids:
                    analysis['dependencies'].append(
                        f'Story {story.id} depends on external item {dep}')
        return analysis

    def decompose_stories(self, stories: List[UserStory]) ->List[UserStory]:
        """Break down complex stories into specific implementation tasks"""
        for story in stories:
            if story.id == 'STORY-001':
                story.tasks = [Task('TASK-001-01',
                    'Implement RBAC database schema',
                    'Create tables for roles, permissions, user_roles',
                    TaskType.TECHNICAL, story.id, 8.0), Task('TASK-001-02',
                    'Build RBAC service layer',
                    'Implement role and permission management logic',
                    TaskType.FEATURE, story.id, 12.0), Task('TASK-001-03',
                    'Create RBAC middleware',
                    'Implement API route protection', TaskType.TECHNICAL,
                    story.id, 6.0), Task('TASK-001-04',
                    'Build admin interface',
                    'Create UI for role management', TaskType.FEATURE,
                    story.id, 8.0), Task('TASK-001-05',
                    'Implement audit logging',
                    'Track all permission changes', TaskType.FEATURE, story
                    .id, 4.0), Task('TASK-001-06',
                    'Write comprehensive tests',
                    'Unit and integration tests for RBAC', TaskType.TESTING,
                    story.id, 6.0)]
            elif story.id == 'STORY-002':
                story.tasks = [Task('TASK-002-01',
                    'Update Tailwind configuration',
                    'Replace purple/cyan with teal in config', TaskType.
                    TECHNICAL, story.id, 4.0), Task('TASK-002-02',
                    'Remove Aceternity components',
                    'Delete and replace with shadcn/ui', TaskType.TECHNICAL,
                    story.id, 8.0), Task('TASK-002-03',
                    'Implement feature flag system',
                    'Add NEXT_PUBLIC_USE_NEW_THEME support', TaskType.
                    TECHNICAL, story.id, 6.0), Task('TASK-002-04',
                    'Migrate component colors',
                    'Update all components to use teal palette', TaskType.
                    DESIGN, story.id, 16.0), Task('TASK-002-05',
                    'Accessibility testing',
                    'Ensure WCAG 2.2 AA compliance maintained', TaskType.
                    TESTING, story.id, 8.0), Task('TASK-002-06',
                    'Performance optimization',
                    'Keep bundle size increase under 5%', TaskType.
                    TECHNICAL, story.id, 4.0)]
            elif story.id == 'STORY-003':
                story.tasks = [Task('TASK-003-01',
                    'Design AI classification API',
                    'Define endpoints and data structures', TaskType.
                    TECHNICAL, story.id, 8.0), Task('TASK-003-02',
                    'Implement document analysis',
                    'Extract text and metadata from uploads', TaskType.
                    FEATURE, story.id, 16.0), Task('TASK-003-03',
                    'Build classification model',
                    'AI logic for document categorization', TaskType.
                    FEATURE, story.id, 20.0), Task('TASK-003-04',
                    'Control mapping logic',
                    'Map evidence to framework controls', TaskType.FEATURE,
                    story.id, 12.0), Task('TASK-003-05',
                    'Build confidence scoring',
                    'Display AI confidence levels', TaskType.FEATURE, story
                    .id, 6.0), Task('TASK-003-06',
                    'Create override interface',
                    'Allow manual classification changes', TaskType.FEATURE,
                    story.id, 8.0), Task('TASK-003-07',
                    'Implement bulk processing',
                    'Handle multiple file uploads', TaskType.TECHNICAL,
                    story.id, 6.0)]
            elif story.id == 'STORY-004':
                story.tasks = [Task('TASK-004-01',
                    'Design analytics data model',
                    'Schema for compliance metrics and trends', TaskType.
                    TECHNICAL, story.id, 6.0), Task('TASK-004-02',
                    'Build compliance scoring engine',
                    'Calculate and track compliance scores', TaskType.
                    FEATURE, story.id, 12.0), Task('TASK-004-03',
                    'Implement gap analysis',
                    'Identify and prioritize compliance gaps', TaskType.
                    FEATURE, story.id, 10.0), Task('TASK-004-04',
                    'Create insights dashboard',
                    'Visual display of compliance analytics', TaskType.
                    FEATURE, story.id, 12.0), Task('TASK-004-05',
                    'Build recommendation engine',
                    'AI-powered actionable insights', TaskType.FEATURE,
                    story.id, 8.0), Task('TASK-004-06',
                    'Implement export features',
                    'PDF/Excel report generation', TaskType.FEATURE, story.
                    id, 6.0)]
            elif story.id == 'STORY-005':
                story.tasks = [Task('TASK-005-01',
                    'Database query optimization',
                    'Add indexes and optimize slow queries', TaskType.
                    TECHNICAL, story.id, 8.0), Task('TASK-005-02',
                    'API response optimization',
                    'Reduce response times to <200ms', TaskType.TECHNICAL,
                    story.id, 6.0), Task('TASK-005-03',
                    'Implement performance monitoring',
                    'Real-time performance dashboards', TaskType.TECHNICAL,
                    story.id, 8.0), Task('TASK-005-04',
                    'Set up automated alerts',
                    'Alert system for performance issues', TaskType.
                    TECHNICAL, story.id, 4.0), Task('TASK-005-05',
                    'Conduct load testing',
                    'Validate performance under load', TaskType.TESTING,
                    story.id, 6.0)]
        return stories

    def track_sprint_implementation(self, sprint_id: str) ->Dict[str, Any]:
        """Track implementation progress for the current sprint"""
        sprint = self._load_sprint(sprint_id)
        if not sprint:
            return {'error': f'Sprint {sprint_id} not found'}
        progress = {'sprint_id': sprint_id, 'sprint_name': sprint.name,
            'sprint_goal': sprint.goal, 'start_date': sprint.start_date.
            isoformat(), 'end_date': sprint.end_date.isoformat(),
            'days_remaining': (sprint.end_date - datetime.date.today()).
            days, 'total_stories': len(sprint.stories), 'completed_stories':
            len([s for s in sprint.stories if s.status == StoryStatus.DONE]
            ), 'in_progress_stories': len([s for s in sprint.stories if s.
            status == StoryStatus.IN_PROGRESS]), 'blocked_stories': len([s for
            s in sprint.stories if s.status == StoryStatus.BLOCKED]),
            'story_points_completed': sum(s.story_points for s in sprint.
            stories if s.status == StoryStatus.DONE), 'story_points_total':
            sum(s.story_points for s in sprint.stories), 'hours_spent': sum
            (s.actual_hours for s in sprint.stories), 'hours_estimated':
            sum(s.estimated_hours for s in sprint.stories),
            'velocity_current': sum(s.story_points for s in sprint.stories if
            s.status == StoryStatus.DONE), 'velocity_target': sprint.
            velocity_target, 'stories_by_status': {}, 'blockers': [],
            'recommendations': []}
        for status in StoryStatus:
            stories_in_status = [s for s in sprint.stories if s.status ==
                status]
            progress['stories_by_status'][status.value] = {'count': len(
                stories_in_status), 'story_points': sum(s.story_points for
                s in stories_in_status), 'stories': [{'id': s.id, 'title':
                s.title, 'points': s.story_points} for s in stories_in_status]}
        blocked_stories = [s for s in sprint.stories if s.status ==
            StoryStatus.BLOCKED]
        for story in blocked_stories:
            progress['blockers'].append({'story_id': story.id, 'title':
                story.title, 'dependencies': story.dependencies, 'priority':
                story.priority.value})
        completion_rate = progress['completed_stories'] / progress[
            'total_stories'] if progress['total_stories'] > 0 else 0
        days_elapsed = (datetime.date.today() - sprint.start_date).days
        sprint_duration = (sprint.end_date - sprint.start_date).days
        expected_completion = (days_elapsed / sprint_duration if 
            sprint_duration > 0 else 0)
        if completion_rate < expected_completion - 0.2:
            progress['recommendations'].append(
                'Sprint is behind schedule - consider scope reduction or timeline extension',
                )
        if len(blocked_stories) > 0:
            progress['recommendations'].append(
                'Address blocked stories to maintain sprint momentum')
        if progress['hours_spent'] > progress['hours_estimated'] * 1.2:
            progress['recommendations'].append(
                'Actual effort exceeding estimates - review story complexity')
        return progress

    def _save_sprint(self, sprint: Sprint) ->None:
        """Save sprint to disk"""
        filepath = os.path.join(self.data_dir, f'{sprint.id}.json')
        with open(filepath, 'w') as f:
            sprint_dict = asdict(sprint)
            sprint_dict['start_date'] = sprint.start_date.isoformat()
            sprint_dict['end_date'] = sprint.end_date.isoformat()
            sprint_dict['created_at'] = sprint.created_at.isoformat()
            for i, story in enumerate(sprint_dict['stories']):
                story['created_at'] = sprint.stories[i].created_at.isoformat()
                story['priority'] = story['priority']
                story['status'] = story['status']
                for j, task in enumerate(story['tasks']):
                    task['created_at'] = sprint.stories[i].tasks[j
                        ].created_at.isoformat()
                    task['type'] = task['type']
                    task['status'] = task['status']
            json.dump(sprint_dict, f, indent=2)

    def _load_sprint(self, sprint_id: str) ->Optional[Sprint]:
        """Load sprint from disk"""
        filepath = os.path.join(self.data_dir, f'{sprint_id}.json')
        if not os.path.exists(filepath):
            return None
        with open(filepath, 'r') as f:
            data = json.load(f)
        try:
            start_date = datetime.datetime.strptime(data['start_date'],
                '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(data['end_date'], '%Y-%m-%d'
                ).date()
            created_at = datetime.datetime.fromisoformat(data['created_at'])
            stories = []
            for story_data in data.get('stories', []):
                story_created_at = datetime.datetime.fromisoformat(story_data
                    ['created_at'])
                acceptance_criteria = []
                for criteria_data in story_data.get('acceptance_criteria', []):
                    acceptance_criteria.append(AcceptanceCriteria(
                        description=criteria_data['description'], testable=
                        criteria_data.get('testable', True), automated_test
                        =criteria_data.get('automated_test')))
                tasks = []
                for task_data in story_data.get('tasks', []):
                    task_created_at = datetime.datetime.fromisoformat(task_data
                        ['created_at'])
                    task = Task(id=task_data['id'], title=task_data['title'
                        ], description=task_data['description'], type=
                        TaskType(task_data['type']), story_id=task_data[
                        'story_id'], estimated_hours=task_data[
                        'estimated_hours'], assigned_to=task_data.get(
                        'assigned_to'), status=StoryStatus(task_data[
                        'status']), dependencies=task_data.get(
                        'dependencies', []), technical_notes=task_data.get(
                        'technical_notes'), created_at=task_created_at)
                    tasks.append(task)
                story = UserStory(id=story_data['id'], title=story_data[
                    'title'], description=story_data['description'],
                    priority=Priority(story_data['priority']), story_points
                    =story_data['story_points'], feature_area=story_data[
                    'feature_area'], acceptance_criteria=
                    acceptance_criteria, tasks=tasks, status=StoryStatus(
                    story_data['status']), dependencies=story_data.get(
                    'dependencies', []), technical_complexity=story_data.
                    get('technical_complexity', 'MEDIUM'), estimated_hours=
                    story_data.get('estimated_hours', 0.0), actual_hours=
                    story_data.get('actual_hours', 0.0), sprint_id=
                    story_data.get('sprint_id'), assigned_to=story_data.get
                    ('assigned_to'), created_at=story_created_at)
                stories.append(story)
            sprint = Sprint(id=data['id'], name=data['name'], goal=data[
                'goal'], start_date=start_date, end_date=end_date,
                capacity_hours=data['capacity_hours'], team_members=data[
                'team_members'], stories=stories, status=data.get('status',
                'PLANNING'), velocity_target=data.get('velocity_target', 0),
                actual_velocity=data.get('actual_velocity', 0),
                retrospective_notes=data.get('retrospective_notes'),
                created_at=created_at)
            return sprint
        except (KeyError, ValueError, TypeError) as e:
            logger.info('Error deserializing sprint %s: %s' % (sprint_id, e))
            return None

def main() ->None:
    """CLI interface for sprint management"""
    import sys
    if len(sys.argv) < 2:
        logger.info('Usage: python sprint_management.py <command> [args]')
        print(
            'Commands: init_sprint, generate_stories, analyze_stories, decompose_stories, track_progress',
            )
        return
    command = sys.argv[1]
    manager = SprintManager()
    if command == 'init_sprint':
        sprint_data = {'id': 'sprint_2_evidence_classifier', 'name':
            'Sprint 2: Evidence Classification & Design System', 'goal':
            'Complete RBAC, implement evidence auto-classification, and finalize teal design system'
            , 'start_date': '2025-08-01', 'end_date': '2025-08-15',
            'capacity_hours': 120.0, 'team_members': ['Lead Developer',
            'Frontend Developer', 'AI Engineer'], 'velocity_target': 40}
        sprint = manager.init_sprint(sprint_data)
        logger.info('Initialized sprint: %s' % sprint.name)
    elif command == 'generate_stories':
        stories = manager.generate_sprint_stories(
            'sprint_2_evidence_classifier', {})
        logger.info('Generated %s user stories' % len(stories))
        for story in stories:
            logger.info('- %s: %s (%s pts)' % (story.id, story.title, story
                .story_points))
    elif command == 'analyze_stories':
        stories = manager.generate_sprint_stories(
            'sprint_2_evidence_classifier', {})
        analysis = manager.analyze_stories(stories)
        logger.info('Story Analysis:')
        logger.info('Total stories: %s' % analysis['total_stories'])
        logger.info('Total story points: %s' % analysis['total_story_points'])
        logger.info('Total estimated hours: %s' % analysis[
            'total_estimated_hours'])
        logger.info('Recommendations:')
        for rec in analysis['recommendations']:
            logger.info('- %s' % rec)
    elif command == 'decompose_stories':
        stories = manager.generate_sprint_stories(
            'sprint_2_evidence_classifier', {})
        stories = manager.decompose_stories(stories)
        logger.info('Story Decomposition:')
        for story in stories:
            logger.info('\n%s: %s' % (story.id, story.title))
            for task in story.tasks:
                logger.info('  - %s: %s (%sh)' % (task.id, task.title, task
                    .estimated_hours))
    elif command == 'track_progress':
        logger.info('Sprint progress tracking requires saved sprint data')

if __name__ == '__main__':
    main()
