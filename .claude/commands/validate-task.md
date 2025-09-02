# Validate Task Completion

You are validating that a task meets its acceptance criteria before marking complete.

## Usage
`/validate-task [task_id]`

## Validation Process
1. Load task acceptance criteria
2. Run specific validation tests
3. Check for regressions
4. Verify documentation updated
5. Update task status

## Validation by Priority
### P0 Validation
- Tests collect successfully
- No import errors
- Environment configured

### P1 Validation  
- Security scan passes
- API endpoints respond
- Test coverage met

### P2+ Validation
- Feature works as specified
- Tests written and passing
- Documentation complete

## Example
```bash
/validate-task a02d81dc
# Runs validation suite for env var configuration task
# Returns: PASS/FAIL with specific issues if any
```