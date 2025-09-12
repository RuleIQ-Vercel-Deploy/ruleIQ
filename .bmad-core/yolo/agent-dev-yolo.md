# Dev Agent YOLO Template

## Auto-Decisions
- Use existing patterns from codebase
- Test coverage minimum: 80%
- Follow project lint rules
- Auto-fix minor issues

## Handoff Package
```json
{
  "artifacts": ["files_created", "files_modified"],
  "next_action": "run_tests",
  "context": {
    "story_id": "current",
    "tests_written": true,
    "coverage": 85
  }
}
```
