# Database Migration Safety & Rollback Procedures

## Overview
This document provides comprehensive rollback procedures for all database changes in the ruleIQ brownfield enhancement project.

## Migration Risk Assessment

### Current Database Stack
- **PostgreSQL**: Main application database
- **Neo4j**: GraphRAG knowledge base
- **Redis**: Caching and session storage
- **pgvector**: Vector embeddings for AI features

### Risk Categories
1. **Schema Changes**: ALTER TABLE, new columns, constraints
2. **Data Migrations**: Moving/transforming existing data
3. **Index Changes**: Performance impact on running queries
4. **Relationship Changes**: Foreign keys, graph relationships

## Rollback Procedures by Migration Type

### 1. Schema Changes (PostgreSQL)

#### Forward Migration Template
```sql
-- Migration: add_user_preferences_table_v1.sql
BEGIN;

-- Create new table
CREATE TABLE IF NOT EXISTS user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    theme VARCHAR(50) DEFAULT 'light',
    notifications JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Create indexes
CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);

-- Add version tracking
INSERT INTO schema_versions (version, applied_at) 
VALUES ('add_user_preferences_v1', NOW());

COMMIT;
```

#### Rollback Script
```sql
-- Rollback: rollback_user_preferences_table_v1.sql
BEGIN;

-- Save data before dropping (if needed)
CREATE TABLE user_preferences_backup AS 
SELECT * FROM user_preferences;

-- Drop the table and indexes
DROP TABLE IF EXISTS user_preferences CASCADE;

-- Remove version tracking
DELETE FROM schema_versions 
WHERE version = 'add_user_preferences_v1';

COMMIT;
```

### 2. Column Additions/Modifications

#### Safe Addition Pattern
```sql
-- Forward: add_compliance_score_column.sql
BEGIN;

-- Add column as nullable first
ALTER TABLE assessments 
ADD COLUMN compliance_score DECIMAL(5,2);

-- Backfill with default values
UPDATE assessments 
SET compliance_score = 0.0 
WHERE compliance_score IS NULL;

-- Then add constraint if needed
ALTER TABLE assessments 
ALTER COLUMN compliance_score SET NOT NULL;

COMMIT;
```

#### Rollback
```sql
-- Rollback: remove_compliance_score_column.sql
BEGIN;

-- Archive the data first
CREATE TABLE archived_compliance_scores AS
SELECT id, compliance_score, updated_at 
FROM assessments 
WHERE compliance_score IS NOT NULL;

-- Remove the column
ALTER TABLE assessments 
DROP COLUMN compliance_score;

COMMIT;
```

### 3. Neo4j Graph Migration Safety

#### Forward Migration
```cypher
// Migration: add_risk_relationships.cypher
// Version: 2025-01-08-001

// Create backup point
CALL apoc.export.json.all("backup/neo4j_backup_20250108.json");

// Add new relationship type
MATCH (c:Control), (r:Risk)
WHERE c.risk_id = r.id
CREATE (c)-[:MITIGATES]->(r);

// Add metadata
CREATE (m:MigrationLog {
    version: '2025-01-08-001',
    description: 'Add MITIGATES relationships',
    applied_at: datetime(),
    node_count: 0,
    relationship_count: 0
});
```

#### Rollback
```cypher
// Rollback: remove_risk_relationships.cypher

// Remove new relationships
MATCH ()-[r:MITIGATES]->()
DELETE r;

// Restore from backup if needed
CALL apoc.import.json("backup/neo4j_backup_20250108.json");

// Remove migration log
MATCH (m:MigrationLog {version: '2025-01-08-001'})
DELETE m;
```

### 4. Data Migration Safety

#### Blue-Green Migration Pattern
```python
# migration_manager.py
class SafeMigration:
    def __init__(self, migration_name):
        self.migration_name = migration_name
        self.feature_flag = f"migration_{migration_name}_enabled"
        
    async def execute(self):
        """Execute migration with safety checks"""
        try:
            # 1. Create backup
            await self.create_backup()
            
            # 2. Run migration in transaction
            async with db.transaction() as tx:
                await self.run_migration(tx)
                
                # 3. Validate data integrity
                if not await self.validate_migration(tx):
                    raise MigrationError("Validation failed")
                    
            # 4. Enable via feature flag
            await self.enable_feature_flag()
            
        except Exception as e:
            await self.rollback()
            raise
            
    async def rollback(self):
        """Automatic rollback on failure"""
        # 1. Disable feature flag
        await self.disable_feature_flag()
        
        # 2. Restore from backup
        await self.restore_backup()
        
        # 3. Log failure
        logger.error(f"Migration {self.migration_name} rolled back")
```

## Feature Flag Implementation

### Configuration
```python
# config/feature_flags.py
FEATURE_FLAGS = {
    'new_user_preferences': {
        'enabled': False,
        'rollout_percentage': 0,
        'whitelist_users': [],
        'migration_version': 'v1'
    },
    'enhanced_ai_agent': {
        'enabled': False,
        'rollout_percentage': 10,
        'blacklist_users': [],
        'fallback_enabled': True
    }
}
```

### Usage Pattern
```python
# api/routes/users.py
@app.route('/api/users/preferences')
@require_auth
def get_preferences():
    if feature_flag_enabled('new_user_preferences', current_user):
        # New implementation
        return UserPreferencesV2.get(current_user.id)
    else:
        # Old implementation
        return UserPreferences.get(current_user.id)
```

## Monitoring & Alerts

### Health Checks
```python
# monitoring/db_health.py
async def check_migration_health():
    checks = {
        'schema_version': await check_schema_version(),
        'data_integrity': await validate_constraints(),
        'index_performance': await check_index_usage(),
        'orphaned_records': await find_orphaned_data()
    }
    
    if any(not v for v in checks.values()):
        await trigger_rollback_alert()
    
    return checks
```

### Rollback Triggers
1. **Automatic Triggers**
   - Error rate > 5% for 5 minutes
   - Response time > 2x baseline
   - Database connection errors > 10/minute
   - Data integrity check failures

2. **Manual Triggers**
   - Support team escalation
   - Customer impact detected
   - Performance degradation confirmed

## Testing Procedures

### Pre-Migration Testing
```bash
# 1. Run migration on staging
./scripts/migrate.sh --env staging --dry-run

# 2. Load test with production-like data
./scripts/load-test.sh --duration 1h --users 1000

# 3. Validate rollback procedure
./scripts/migrate.sh --env staging --rollback

# 4. Verify data integrity
./scripts/validate-data.sh --deep-check
```

### Post-Migration Validation
```python
# validation/post_migration.py
async def validate_migration(migration_name):
    validations = []
    
    # 1. Row counts match
    validations.append(await check_row_counts())
    
    # 2. No orphaned foreign keys
    validations.append(await check_referential_integrity())
    
    # 3. Indexes are being used
    validations.append(await check_index_usage())
    
    # 4. No performance degradation
    validations.append(await check_query_performance())
    
    # 5. Application health checks pass
    validations.append(await check_application_health())
    
    return all(validations)
```

## Emergency Procedures

### Immediate Rollback (< 5 minutes)
```bash
#!/bin/bash
# emergency_rollback.sh

# 1. Disable traffic to affected service
kubectl scale deployment api-server --replicas=0

# 2. Execute rollback
psql $DATABASE_URL < rollback/emergency_rollback.sql

# 3. Clear caches
redis-cli FLUSHALL

# 4. Restart services with old code
git checkout $LAST_KNOWN_GOOD_SHA
docker-compose up -d

# 5. Re-enable traffic
kubectl scale deployment api-server --replicas=3

# 6. Send notification
./notify.sh "Emergency rollback completed"
```

### Communication Plan
1. **T-0**: Issue detected, rollback initiated
2. **T+5m**: Stakeholders notified via Slack
3. **T+15m**: Status page updated
4. **T+30m**: Customer communication if impact > 5 minutes
5. **T+1h**: Post-mortem scheduled

## Success Metrics
- Zero data loss during migrations
- Rollback execution < 5 minutes
- 100% successful rollback tests before production
- Feature flag adoption for all schema changes
- Monitoring coverage for all migration paths