# Generate Status Report

You generate comprehensive status reports for the project.

## Usage
`/report-status [format]`

Formats: summary | detailed | priority | timeline

## Report Sections
### Executive Summary
- Current priority level
- Tasks complete/total
- Critical blockers
- Next 24-hour focus

### Priority Status
```
P0 (Critical): 3/6 complete (50%)
  ✅ a02d81dc - Env vars fixed
  ⏳ 2ef17163 - Test DB in progress
  ❌ d28d8c18 - DateTime errors blocked
  
P1 (High): 0/5 complete (0%) - BLOCKED
  ⏸️ Waiting for P0 gate
```

### Timeline View
- Tasks by deadline
- Overdue items (RED)
- At risk items (YELLOW)
- On track items (GREEN)

### Metrics
- Velocity: tasks/day
- Quality: test pass rate
- Coverage: current %
- Blockers: count and age

## Example Output
```markdown
# RuleIQ Status Report - 2025-01-02

## 🎯 Current Focus: P0 Critical Blockers
- 50% complete (3/6 tasks)
- Est. completion: 18 hours
- Main blocker: Test infrastructure

## 📊 Overall Progress
- Total: 12/49 tasks (24.5%)
- This week: 8 tasks completed
- Velocity: 2.3 tasks/day
```