# Quick Command Reference

## Archon MCP (Task Management)
```python
# Essential
mcp__archon__health_check()
mcp__archon__list_tasks(filter_by="status", filter_value="todo")
mcp__archon__get_task(task_id="...")
mcp__archon__manage_task(action="update", task_id="...", update_fields={"status": "doing"})

# Research
mcp__archon__perform_rag_query(query="...", match_count=5)
mcp__archon__search_code_examples(query="...", match_count=3)
```

## Serena MCP (Code Intelligence)
```python
# Navigation
mcp__serena__find_symbol(name_path="ClassName/method_name", include_body=True)
mcp__serena__get_symbols_overview(relative_path="api/routers/auth.py")
mcp__serena__search_for_pattern(substring_pattern="def.*auth")

# Editing
mcp__serena__replace_symbol_body(name_path="...", relative_path="...", body="...")
mcp__serena__replace_regex(relative_path="...", regex="...", repl="...")

# Memory
mcp__serena__read_memory(memory_file_name="ALWAYS_READ_FIRST")
```

## Testing
```bash
make test-fast              # Backend quick tests
make test                   # Full backend suite
pnpm test                   # Frontend tests
pytest tests/test_file.py   # Specific test
```

## Development
```bash
# Start backend
doppler run -- python main.py

# Start frontend
pnpm dev --turbo

# Database
alembic upgrade head
```