#!/usr/bin/env python3
"""
Update Archon tasks based on SonarCloud analysis results
"""

import requests
import json
from datetime import datetime

# Archon configuration
ARCHON_URL = "http://localhost:3737/api"
PROJECT_ID = "342d657c-fb73-4f71-9b6e-302857319aac"

# SonarCloud analysis results (from our recent scan)
SONAR_RESULTS = {
    "total_issues": 4521,
    "bugs": 358,
    "vulnerabilities": 16,
    "code_smells": 4147,
    "security_hotspots": 369,  # Not shown in latest but was in original
    "blocker": 62,
    "critical": 1514,
    "major": 1184,
    "minor": 1267,
    "info": 494,
    "coverage": 0.0,
    "duplicated_lines": 5.9,
    "technical_debt_hours": 439,
    "reliability_rating": "E",
    "security_rating": "E",
    "maintainability_rating": "A"
}

def get_existing_tasks():
    """Get all existing tasks for the project"""
    response = requests.get(f"{ARCHON_URL}/tasks?project_id={PROJECT_ID}")
    if response.status_code == 200:
        data = response.json()
        return data.get("tasks", [])
    return []

def archive_old_sprint_tasks():
    """Archive the old sprint tasks that are no longer relevant"""
    tasks = get_existing_tasks()
    archived_count = 0
    
    # Old task titles from initial sprint that should be archived
    old_task_patterns = [
        "Fix 22 Python undefined names",
        "Fix 2 security issues (passwords & hash)",
        "Fix 358 bugs identified by SonarCloud",
        "Auto-fix 429 Python issues with Ruff",
        "Format code with Black and Prettier"
    ]
    
    for task in tasks:
        if any(pattern in task.get("title", "") for pattern in old_task_patterns):
            # Archive the task
            response = requests.patch(
                f"{ARCHON_URL}/tasks/{task['id']}",
                json={"archived": True}
            )
            if response.status_code == 200:
                archived_count += 1
                print(f"✅ Archived: {task['title']}")
    
    return archived_count

def create_sonarcloud_sprint_tasks():
    """Create new sprint tasks based on SonarCloud analysis"""
    
    tasks_to_create = [
        {
            "title": "Fix 62 BLOCKER Issues",
            "description": f"""Fix all 62 blocker-level issues identified by SonarCloud.
These are the most critical issues that could cause application crashes or severe security vulnerabilities.

Priority: HIGHEST
Estimated Time: 2-3 days
Impact: Prevents critical failures and security breaches

Steps:
1. Run SonarCloud analysis to get blocker issue list
2. Group blockers by type (bugs, vulnerabilities, security hotspots)
3. Fix each blocker with proper testing
4. Verify fixes with re-scan""",
            "task_order": 100,
            "feature": "Code Quality",
            "status": "todo"
        },
        {
            "title": "Fix 16 Security Vulnerabilities",
            "description": f"""Address all 16 security vulnerabilities detected by SonarCloud.
Current Security Rating: E (worst)
Target: Achieve Security Rating B or better

Categories likely include:
- SQL injection risks
- XSS vulnerabilities
- Insecure cryptography
- Authentication bypasses
- Information disclosure

Steps:
1. Review each vulnerability in SonarCloud dashboard
2. Implement security best practices
3. Add security tests
4. Re-scan to verify fixes""",
            "task_order": 95,
            "feature": "Security",
            "status": "todo"
        },
        {
            "title": "Fix Top 100 Critical Bugs",
            "description": f"""Fix the most critical bugs from the 358 total bugs.
Current Reliability Rating: E (worst)
Target: Reduce bugs by 50% minimum

Focus on:
- Null pointer exceptions
- Resource leaks
- Race conditions
- Logic errors causing incorrect behavior

Approach:
1. Sort bugs by impact and frequency
2. Fix in batches of 20
3. Add unit tests for each fix
4. Track progress in SonarCloud""",
            "task_order": 90,
            "feature": "Bug Fixes",
            "status": "todo"
        },
        {
            "title": "Review and Fix 369 Security Hotspots",
            "description": f"""Review all 369 security hotspots for potential vulnerabilities.

Security hotspots are code patterns that need manual review to determine if they're vulnerable.

Common hotspots:
- Hardcoded credentials
- Weak cryptography
- File system access
- Command injection risks
- Unvalidated redirects

Process:
1. Review each hotspot in SonarCloud
2. Mark as 'Safe' or 'Fix needed'
3. Fix all vulnerable hotspots
4. Document security decisions""",
            "task_order": 85,
            "feature": "Security",
            "status": "todo"
        },
        {
            "title": "Fix Python Type Hints (845 S6903 violations)",
            "description": f"""Add missing type hints to 845 Python functions/methods.

This is the #1 rule violation in the codebase.
Benefits:
- Better IDE support
- Catch type errors early
- Improve code documentation
- Enable better static analysis

Strategy:
1. Start with API endpoints and core services
2. Use mypy to validate type hints
3. Add to CI/CD pipeline
4. Gradually type entire codebase""",
            "task_order": 80,
            "feature": "Code Quality",
            "status": "todo"
        },
        {
            "title": "Remove 458 TODO Comments (S1135)",
            "description": f"""Address or remove 458 TODO comments in TypeScript files.

TODOs indicate incomplete implementation or technical debt.
#2 most common issue in codebase.

Actions:
1. Review each TODO comment
2. Either implement the TODO or create a proper task
3. Remove resolved TODOs
4. Document decisions for deferred work""",
            "task_order": 75,
            "feature": "Technical Debt",
            "status": "todo"
        },
        {
            "title": "Reduce Code Duplication from 5.9% to <3%",
            "description": f"""Current duplication: 5.9%
Target: <3% (SonarCloud standard)

High duplication areas to refactor:
- API endpoint handlers
- Test fixtures and utilities
- Component patterns
- Database queries

Approach:
1. Identify duplication hotspots
2. Extract common utilities
3. Create shared components
4. Implement DRY principles""",
            "task_order": 70,
            "feature": "Code Quality",
            "status": "todo"
        },
        {
            "title": "Add Test Coverage (Currently 0%)",
            "description": f"""Implement comprehensive test coverage.
Current: 0%
Target: 80% minimum

Test Strategy:
1. Unit tests for all services (Jest/Pytest)
2. Integration tests for APIs
3. Component tests for React
4. E2E tests for critical flows

Priority order:
- Authentication/Authorization
- Payment processing
- Core business logic
- API endpoints
- React components""",
            "task_order": 65,
            "feature": "Testing",
            "status": "todo"
        },
        {
            "title": "Fix Cognitive Complexity Issues (198 S3776)",
            "description": f"""Refactor 198 functions with excessive cognitive complexity.

Functions are too complex to understand and maintain.
Target: Max complexity of 15 per function.

Refactoring techniques:
- Extract methods
- Early returns
- Replace conditionals with polymorphism
- Use guard clauses
- Simplify boolean expressions""",
            "task_order": 60,
            "feature": "Code Quality",
            "status": "todo"
        },
        {
            "title": "Setup SonarCloud Quality Gate",
            "description": f"""Configure and enforce quality gates in CI/CD.

Quality Gate Criteria:
- New code coverage > 80%
- Duplicated lines < 3%
- Maintainability rating >= A
- Reliability rating >= B
- Security rating >= B
- No new blockers or criticals

Implementation:
1. Configure quality gate in SonarCloud
2. Add to GitHub Actions
3. Block PRs that fail gate
4. Setup notifications""",
            "task_order": 55,
            "feature": "CI/CD",
            "status": "todo"
        }
    ]
    
    created_count = 0
    for task_data in tasks_to_create:
        task_data["project_id"] = PROJECT_ID
        task_data["assignee"] = "Development Team"
        
        response = requests.post(f"{ARCHON_URL}/tasks", json=task_data)
        if response.status_code in [200, 201]:
            created_count += 1
            print(f"✅ Created: {task_data['title']}")
        else:
            print(f"❌ Failed to create: {task_data['title']}")
            print(f"   Response: {response.status_code} - {response.text}")
    
    return created_count

def create_summary_report():
    """Create a summary report of the sprint plan"""
    
    report = f"""
# SonarCloud Quality Improvement Sprint

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Current Quality Metrics
- **Total Issues**: {SONAR_RESULTS['total_issues']}
- **Quality Gate**: FAILED ❌
- **Reliability Rating**: {SONAR_RESULTS['reliability_rating']} (Worst)
- **Security Rating**: {SONAR_RESULTS['security_rating']} (Worst)
- **Maintainability Rating**: {SONAR_RESULTS['maintainability_rating']} (Best!)
- **Code Coverage**: {SONAR_RESULTS['coverage']}%
- **Technical Debt**: {SONAR_RESULTS['technical_debt_hours']} hours

## Issue Breakdown
### By Type
- 🐛 Bugs: {SONAR_RESULTS['bugs']}
- 🔒 Vulnerabilities: {SONAR_RESULTS['vulnerabilities']}
- 💨 Code Smells: {SONAR_RESULTS['code_smells']}
- 🔥 Security Hotspots: {SONAR_RESULTS['security_hotspots']}

### By Severity
- 🚫 Blocker: {SONAR_RESULTS['blocker']}
- 🔴 Critical: {SONAR_RESULTS['critical']}
- 🟠 Major: {SONAR_RESULTS['major']}
- 🟡 Minor: {SONAR_RESULTS['minor']}
- ℹ️ Info: {SONAR_RESULTS['info']}

## Sprint Goals
1. **Immediate**: Fix all blocker issues
2. **Week 1**: Address security vulnerabilities and critical bugs
3. **Week 2**: Review security hotspots, add type hints
4. **Week 3**: Reduce duplication, add test coverage
5. **Week 4**: Setup quality gates, achieve passing status

## Success Metrics
- Zero blocker issues
- Security rating B or better
- Reliability rating B or better
- Code coverage > 80%
- Quality gate PASSING

## Tracking
- SonarCloud Dashboard: https://sonarcloud.io/summary/overall?id=ruliq-compliance-platform
- Archon Project: http://localhost:3737/
"""
    
    with open("SONARCLOUD_SPRINT_PLAN.md", "w") as f:
        f.write(report)
    
    print("\n" + "="*60)
    print(report)
    print("="*60)

def main():
    print("\n🚀 Updating Archon Tasks Based on SonarCloud Analysis")
    print("="*60)
    
    # Archive old tasks
    print("\n📦 Archiving old sprint tasks...")
    archived = archive_old_sprint_tasks()
    print(f"   Archived {archived} old tasks")
    
    # Create new tasks
    print("\n📝 Creating new SonarCloud improvement tasks...")
    created = create_sonarcloud_sprint_tasks()
    print(f"   Created {created} new tasks")
    
    # Generate report
    print("\n📊 Generating sprint report...")
    create_summary_report()
    
    print("\n✅ Archon tasks updated successfully!")
    print("   View tasks at: http://localhost:3737/")

if __name__ == "__main__":
    main()