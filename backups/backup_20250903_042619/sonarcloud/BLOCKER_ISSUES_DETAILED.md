# SonarCloud BLOCKER Issues - Detailed Report

Total Blocker Issues: 62

## Issues by Rule (for systematic fixing)

### [python] S930 - 45 violations

**Rule:** Remove this unexpected named argument 'request_origin'.

**Affected files:**
- `api/dependencies/auth.py` (lines: 304, 305, 306)
- `api/middleware/api_key_auth.py` (lines: 125, 127, 128)
- `langgraph_agent/nodes/notification_nodes.py` (lines: 851, 852, 857, 858, 862, 863)
- `langgraph_agent/tests/test_tenancy.py` (lines: 505)
- `services/ai/assistant.py` (lines: 4518, 4519, 4520, 4521, 4522, 4523, 4524)
- `services/ai/safety_manager.py` (lines: 921)
- `tests/fixtures/state_fixtures.py` (lines: 121)
- `tests/integration/api/test_freemium_endpoints.py` (lines: 223, 225, 628, 630, 647, 649, 650)
- `tests/integration/test_comprehensive_api_workflows.py` (lines: 56)
- `tests/integration/test_contract_validation.py` (lines: 47)
- `tests/integration/test_external_service_integration.py` (lines: 49, 223, 340, 541, 637)
- `tests/test_ai_neon.py` (lines: 60, 62, 79, 81)
- `tests/test_ai_policy_generator.py` (lines: 99)
- `tests/test_graph_execution.py` (lines: 89)
- `tests/test_state_management.py` (lines: 40)
- `workers/compliance_tasks.py` (lines: 40, 84)

### [secrets] S6698 - 11 violations

**Rule:** Make sure this PostgreSQL database password gets changed and removed from the code.

**Affected files:**
- `archive/scripts/capture_test_errors.py` (lines: 7, 8, 23)
- `archive/scripts/check_schema.py` (lines: 12)
- `archive/test_configs/conftest_fixed.py` (lines: 43)
- `archive/test_configs/conftest_hybrid.py` (lines: 29)
- `archive/test_configs/conftest_improved.py` (lines: 29)
- `scripts/debug_freemium_tables.py` (lines: 13)
- `scripts/setup_secrets_vault.py` (lines: 48, 49)
- `scripts/simple_test_debug.py` (lines: 14)

### [python] S3516 - 3 violations

**Rule:** Refactor this method to not always return the same value.

**Affected files:**
- `api/dependencies/token_blacklist.py` (lines: 244)
- `langgraph_agent/agents/memory_manager.py` (lines: 540)
- `langgraph_agent/nodes/task_scheduler_node.py` (lines: 241)

### [pythonsecurity] S2083 - 2 violations

**Rule:** Change this code to not construct the path from user-controlled data.

**Affected files:**
- `services/ai/evaluation/tools/ingestion.py` (lines: 23)
- `services/ai/evaluation/tools/ingestion_fixed.py` (lines: 68)

### [secrets] S7362 - 1 violations

**Rule:** Make sure this Supabase Service Role JWT secret gets revoked, changed, and removed from the code.

**Affected files:**
- `archive/scripts/migrate_archon_data.py` (lines: 13)

