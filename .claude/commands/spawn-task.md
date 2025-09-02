# Spawn Task to Specialist

You are spawning a task to a specialized agent. This command delegates a specific task with deadline and context.

## Usage
`/spawn-task [task_id] [specialist_name] [priority]`

## Process
1. Load task details from state file
2. Calculate deadline based on priority:
   - P0: 24 hours from now
   - P1: 48 hours from now
   - P2: 1 week from now
   
3. Determine specialist based on task domain:
   - Python/FastAPI/DB → backend-specialist
   - Tests/Coverage → qa-specialist
   - Security/Vulnerabilities → security-auditor
   - React/Next.js → frontend-specialist
   - Docker/CI/CD → infrastructure
   - Docs/README → documentation
   - UK/GDPR → compliance-uk
   - GraphRAG → graphrag-specialist

4. Create task context:
```json
{
  "task_id": "a02d81dc",
  "title": "Fix env var configuration for tests",
  "priority": "P0",
  "deadline": "2025-01-03T10:00:00",
  "acceptance_criteria": [
    "Environment variables properly loaded",
    "Tests can access configs",
    "No undefined env errors"
  ]
}
```

5. Invoke the specialist with context
6. Update state file with assignment
7. Set monitoring reminder