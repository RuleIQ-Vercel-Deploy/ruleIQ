# Check Priority Gate

You are checking if a priority level gate can advance.

## Usage
`/check-gate [priority]`

## Gate Requirements
- **P0**: All P0 tasks complete, `pytest --collect-only` succeeds
- **P1**: All P1 tasks complete, zero vulnerabilities, API functional
- **P2**: All P2 tasks complete, 80% coverage achieved
- **P3-P7**: All tasks in priority complete

## Process
1. Load current state from `task-state/current-state.json`
2. Check all tasks in priority level
3. Run validation tests for gate:
   ```bash
   # P0 Gate Test
   cd ~/Documents/ruleIQ
   pytest --collect-only
   
   # P1 Gate Test
   sonar-scanner -Dsonar.projectKey=ruleiq
   curl -X GET http://localhost:8000/health
   
   # P2 Gate Test
   pytest --cov=. --cov-report=term | grep TOTAL
   ```
4. If passed, update state to next priority
5. Report results

## Example
```bash
/check-gate P0
# Checks if all P0 tasks complete and tests discoverable
# If yes, advances to P1
```