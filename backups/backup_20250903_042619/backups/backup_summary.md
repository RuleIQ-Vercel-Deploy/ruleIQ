# Database Backups - 20250826_043753

## Purpose
Backups created before LangGraph refactoring phases.

## Backup Locations
- **Neo4j**: `backups/neo4j_20250826_043753/`
- **Neon**: `backups/neon_20250826_043753/`

## Restoration Instructions

### Neo4j Restoration
```python
# Use scripts/restore_neo4j.py
python scripts/restore_neo4j.py backups/neo4j_20250826_043753/compliance_graph.json
```

### Neon Restoration
```python
# Critical data is in JSON format for selective restoration
# Check backups/neon_20250826_043753/database_info.json for table list
```

## Timestamp: 2025-08-26T04:38:04.709003
