# Escalate Blocked Task

You are escalating a blocked task that needs additional attention.

## Usage
`/escalate [task_id] [reason]`

## Escalation Triggers
- P0 task blocked > 12 hours
- P1 task blocked > 36 hours
- Task failed 3+ attempts
- Critical dependency missing
- Specialist unresponsive

## Process
1. Document the specific blocker
2. Analyze failure patterns
3. Consider interventions:
   - Spawn additional specialist
   - Break into subtasks
   - Adjust approach
   - Request human assistance
4. Update escalation log
5. Notify orchestrator

## Example
```bash
/escalate a02d81dc "Test DB connection failing after 3 attempts"
# Creates escalation record and spawns additional help
```