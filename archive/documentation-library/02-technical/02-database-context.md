# Database Context

## Purpose & Responsibility

The database layer provides persistent storage and data management for the ruleIQ compliance automation platform. It implements a comprehensive schema for user management, business profiles, compliance assessments, evidence collection, and AI-powered automation.

## Architecture Overview

### **Database Design Pattern**
- **Pattern**: Domain-driven design with rich entity models
- **Approach**: Normalized schema with strategic denormalization for performance
- **Technology**: PostgreSQL 15 with advanced features (JSONB, UUID, full-text search)

### **Performance Strategy**
- **Indexing**: Comprehensive composite indexes for query optimization
- **Caching**: Redis integration for session management and query caching
- **Connection Management**: Async/sync dual database configuration with connection pooling

## Dependencies

### **Incoming Dependencies**
- **API Layer**: All routers for CRUD operations and data retrieval
- **Service Layer**: Business logic services requiring data persistence
- **AI Services**: Interaction logging and analytics storage
- **Background Tasks**: Celery workers for data processing and reporting
- **Migration System**: Alembic for schema evolution and data migrations

### **Outgoing Dependencies**
- **PostgreSQL 15**: Primary database engine with advanced JSON support
- **Redis 7**: Caching layer and session storage
- **File Storage**: External file storage for evidence documents
- **Backup Systems**: Automated backup and recovery infrastructure
- **Monitoring**: Database performance monitoring and alerting

## Key Interfaces

### **Database Models**

#### **Core Entity Models**
```python
User                     # User authentication and profile management
├── BusinessProfile      # Company information and compliance context  
├── AssessmentSession    # Framework-specific compliance assessments
├── EvidenceItem         # Document storage and compliance evidence
├── ChatConversation     # AI assistant conversation management
└── GeneratedPolicy      # AI-generated compliance documents

ComplianceFramework      # Regulatory framework definitions
├── ImplementationPlan   # Compliance implementation roadmaps
└── ReadinessAssessment  # Compliance readiness evaluation

IntegrationConfiguration # Third-party integration settings
└── ReportSchedule      # Automated reporting configuration
```

#### **Model Relationships**
```sql
-- Primary relationships
User (1) ←→ (N) BusinessProfile
BusinessProfile (1) ←→ (N) AssessmentSession  
BusinessProfile (1) ←→ (N) EvidenceItem
User (1) ←→ (N) ChatConversation
BusinessProfile (1) ←→ (N) GeneratedPolicy

-- Framework relationships  
ComplianceFramework (1) ←→ (N) AssessmentSession
ComplianceFramework (1) ←→ (N) EvidenceItem
ComplianceFramework (1) ←→ (N) ImplementationPlan

-- Integration relationships
User (1) ←→ (N) IntegrationConfiguration
User (1) ←→ (N) ReportSchedule
```

### **Database Access Patterns**

#### **SQLAlchemy ORM Configuration**
```python
# Async database configuration
engine_kwargs = {
    "pool_size": 10,              # Production connection pool
    "max_overflow": 15,           # Connection overflow handling
    "pool_pre_ping": True,        # Connection health validation
    "pool_recycle": 1800,         # 30-minute connection recycling
    "echo": False                 # SQL logging (debug mode only)
}

# Dual async/sync support
class DatabaseManager:
    async_session: AsyncSession   # Primary async operations
    sync_session: Session         # Legacy sync operations (migration)
```

#### **Query Optimization Patterns**
```python
# Optimized queries with eager loading
query = select(BusinessProfile).options(
    selectinload(BusinessProfile.assessment_sessions),
    selectinload(BusinessProfile.evidence_items)
).where(BusinessProfile.user_id == user_id)

# Pagination with performance optimization
query = select(EvidenceItem).where(
    EvidenceItem.user_id == user_id
).order_by(EvidenceItem.created_at.desc()).limit(20).offset(offset)
```

## Implementation Context

### **Critical Schema Issues** ⚠️

#### **URGENT: Column Name Truncation Crisis**
**Impact**: Breaks ORM relationships and causes developer confusion
**Priority**: Critical - Must be fixed before production deployment

```sql
-- PROBLEMATIC: Truncated column names in business_profiles table
ALTER TABLE business_profiles 
RENAME COLUMN handles_persona TO handles_personal_data;
RENAME COLUMN processes_payme TO processes_payments;  
RENAME COLUMN stores_health_d TO stores_health_data;
RENAME COLUMN provides_financ TO provides_financial_services;
RENAME COLUMN operates_critic TO operates_critical_infrastructure;
RENAME COLUMN has_internation TO has_international_operations;

-- PROBLEMATIC: Inconsistent foreign key naming
ALTER TABLE assessment_sessions 
RENAME COLUMN business_profil TO business_profile_id;
ALTER TABLE generated_policies 
RENAME COLUMN business_profil TO business_profile_id;
```

#### **Root Cause Analysis**
- **Database constraints**: Column name length limitations causing truncation
- **Migration history**: Early migrations used truncated names
- **Workaround complexity**: Field mapping required in API layer
- **Developer impact**: Reduced code readability and maintainability

### **Database Schema Overview**

#### **Users Table**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **Business Profiles Table** ⚠️ **NEEDS FIXES**
```sql
-- CURRENT (PROBLEMATIC) SCHEMA:
CREATE TABLE business_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    company_name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    employee_count INTEGER,
    
    -- TRUNCATED COLUMN NAMES (CRITICAL ISSUE):
    handles_persona BOOLEAN,           -- Should be: handles_personal_data
    processes_payme BOOLEAN,           -- Should be: processes_payments  
    stores_health_d BOOLEAN,           -- Should be: stores_health_data
    provides_financ BOOLEAN,           -- Should be: provides_financial_services
    operates_critic BOOLEAN,           -- Should be: operates_critical_infrastructure
    has_internation BOOLEAN,           -- Should be: has_international_operations
    
    -- Additional fields
    data_sensitivity VARCHAR(20) DEFAULT 'Medium',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **Assessment Sessions Table** ⚠️ **NEEDS FIXES**
```sql
CREATE TABLE assessment_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- INCONSISTENT NAMING (CRITICAL ISSUE):
    business_profil UUID,              -- Should be: business_profile_id
    
    framework_id VARCHAR(50) NOT NULL,
    session_name VARCHAR(255),
    status VARCHAR(20) DEFAULT 'not_started',
    
    -- TRUNCATED COLUMN NAME:
    questions_answe JSONB,             -- Should be: questions_answered
    
    progress_percentage DECIMAL(5,2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### **Evidence Items Table**
```sql
CREATE TABLE evidence_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    business_profile_id UUID REFERENCES business_profiles(id),
    framework_id VARCHAR(50),
    
    evidence_name VARCHAR(255) NOT NULL,
    control_reference VARCHAR(100),
    file_path VARCHAR(500),
    file_type VARCHAR(50),
    file_size INTEGER,
    
    status VARCHAR(20) DEFAULT 'not_started',
    priority VARCHAR(10) DEFAULT 'medium',
    
    ai_metadata JSONB,                 -- AI analysis results
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Performance Optimization**

#### **Index Strategy**
```sql
-- Performance indexes (from performance_indexes.py)
CREATE INDEX idx_evidence_user_framework 
ON evidence_items(user_id, framework_id);

CREATE INDEX idx_evidence_user_status 
ON evidence_items(user_id, status);

CREATE INDEX idx_evidence_name_search 
ON evidence_items USING gin(evidence_name gin_trgm_ops);

CREATE INDEX idx_business_profiles_user_id 
ON business_profiles(user_id);

CREATE INDEX idx_assessment_sessions_user_id 
ON assessment_sessions(user_id);

-- JSONB indexes for metadata queries
CREATE INDEX idx_evidence_ai_metadata_gin 
ON evidence_items USING gin(ai_metadata);
```

#### **Query Performance Analysis**
```python
# Common query patterns and their optimization
PERFORMANCE_QUERIES = {
    'evidence_search': """
        SELECT * FROM evidence_items 
        WHERE user_id = %s 
        AND status = ANY(%s) 
        AND evidence_name ILIKE %s 
        ORDER BY created_at DESC 
        LIMIT %s OFFSET %s
    """,
    
    'assessment_dashboard': """
        SELECT a.*, bp.company_name 
        FROM assessment_sessions a
        JOIN business_profiles bp ON a.business_profil = bp.id  -- BROKEN FK
        WHERE a.user_id = %s 
        ORDER BY a.updated_at DESC
    """,
    
    'compliance_overview': """
        SELECT framework_id, 
               COUNT(*) as total_items,
               COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved_count
        FROM evidence_items 
        WHERE user_id = %s 
        GROUP BY framework_id
    """
}
```

### **Migration Strategy**

#### **Current Migration Status**
```
001_initial_migration.py     ✅ Basic table structure
002_base_schema.py           ✅ Core entity relationships  
003_core_tables.py           ✅ Assessment and evidence tables
004_add_integration_configs.py ✅ Third-party integrations
005_add_business_profile_data_sensitivity.py ✅ Data classification
006_add_performance_indexes.py ✅ Query optimization
007_add_evidence_metadata.py ✅ AI metadata support
```

#### **Required Critical Migration** ⚠️
```python
"""Fix column naming issues - URGENT MIGRATION REQUIRED"""

def upgrade():
    # Fix business_profiles column names
    op.execute('ALTER TABLE business_profiles RENAME COLUMN handles_persona TO handles_personal_data')
    op.execute('ALTER TABLE business_profiles RENAME COLUMN processes_payme TO processes_payments')
    op.execute('ALTER TABLE business_profiles RENAME COLUMN stores_health_d TO stores_health_data')
    op.execute('ALTER TABLE business_profiles RENAME COLUMN provides_financ TO provides_financial_services')
    op.execute('ALTER TABLE business_profiles RENAME COLUMN operates_critic TO operates_critical_infrastructure')
    op.execute('ALTER TABLE business_profiles RENAME COLUMN has_internation TO has_international_operations')
    
    # Fix foreign key column names
    op.execute('ALTER TABLE assessment_sessions RENAME COLUMN business_profil TO business_profile_id')
    op.execute('ALTER TABLE generated_policies RENAME COLUMN business_profil TO business_profile_id')
    
    # Fix other truncated names
    op.execute('ALTER TABLE assessment_sessions RENAME COLUMN questions_answe TO questions_answered')

def downgrade():
    # Reverse the changes (for rollback safety)
    op.execute('ALTER TABLE business_profiles RENAME COLUMN handles_personal_data TO handles_persona')
    # ... etc
```

### **Data Integrity Issues**

#### **Missing Constraints** ⚠️
```sql
-- MISSING: Business rule validation constraints
ALTER TABLE evidence_items 
ADD CONSTRAINT chk_evidence_status 
CHECK (status IN ('not_started', 'in_progress', 'collected', 'approved', 'rejected'));

ALTER TABLE business_profiles 
ADD CONSTRAINT chk_employee_count_positive 
CHECK (employee_count > 0);

ALTER TABLE business_profiles 
ADD CONSTRAINT chk_data_sensitivity 
CHECK (data_sensitivity IN ('Low', 'Medium', 'High', 'Critical'));

-- MISSING: Referential integrity
ALTER TABLE assessment_sessions 
ADD CONSTRAINT fk_assessment_business_profile 
FOREIGN KEY (business_profile_id) REFERENCES business_profiles(id);
```

#### **Data Quality Issues**
```sql
-- MISSING: Audit trail constraints
ALTER TABLE evidence_items 
ADD CONSTRAINT chk_approval_workflow 
CHECK (
    (status = 'approved' AND approved_at IS NOT NULL AND approved_by IS NOT NULL) OR
    (status != 'approved')
);
```

## Change Impact Analysis

### **Risk Factors**

#### **Critical Database Risks**
1. **Column Name Truncation**: ORM relationship failures, developer confusion
2. **Missing Constraints**: Data integrity violations, business rule enforcement
3. **Foreign Key Issues**: Cascading delete problems, orphaned records
4. **Performance Degradation**: Unoptimized queries with large datasets

#### **Breaking Change Potential**
1. **Schema Migrations**: API contract changes requiring frontend updates
2. **Column Name Fixes**: ORM model updates across all services
3. **Constraint Additions**: Existing data validation and cleanup required
4. **Index Changes**: Query performance impact during migration

### **Testing Requirements**

#### **Migration Testing**
- **Rollback Testing**: Ensure all migrations are reversible
- **Data Integrity**: Validate constraint additions don't break existing data
- **Performance Testing**: Measure query performance before/after migrations
- **Foreign Key Testing**: Validate relationship integrity after fixes

#### **Performance Testing**
- **Load Testing**: Database performance under concurrent user load
- **Query Optimization**: Index effectiveness measurement
- **Connection Pooling**: Pool exhaustion and recovery testing
- **Cache Integration**: Redis cache hit rates and invalidation testing

## Current Status

### **Production Readiness Assessment**
- **Schema Design**: ✅ Well-designed with modern PostgreSQL features
- **Performance**: ✅ Comprehensive indexing strategy implemented
- **Critical Issues**: ❌ Column naming issues block production deployment
- **Data Integrity**: ⚠️ Missing constraints need implementation
- **Migration System**: ✅ Alembic properly configured and working

### **Required Actions Before Production**

#### **Phase 1: Critical Fixes (Week 1)**
1. **Create migration to fix column names** - Highest priority
2. **Update ORM models to match new column names**
3. **Update API field mapping to use correct names**
4. **Remove field mapping workarounds once fixed**

#### **Phase 2: Data Integrity (Week 2)**
1. **Add missing CHECK constraints for business rules**
2. **Implement proper foreign key constraints**
3. **Add audit trail constraints for compliance**
4. **Validate existing data against new constraints**

#### **Phase 3: Optimization (Week 3)**
1. **Add missing functional indexes for common queries**
2. **Implement row-level security for multi-tenant data**
3. **Add database performance monitoring**
4. **Optimize connection pool configuration**

### **Monitoring and Maintenance**

#### **Database Health Monitoring**
```python
# Health check queries
HEALTH_CHECKS = {
    'connection_count': "SELECT count(*) FROM pg_stat_activity",
    'table_sizes': "SELECT schemaname,tablename,pg_size_pretty(size) FROM pg_tables_size",
    'index_usage': "SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0",
    'slow_queries': "SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC"
}
```

#### **Automated Maintenance**
- **Daily**: Connection pool monitoring and optimization
- **Weekly**: Index usage analysis and optimization recommendations  
- **Monthly**: Table statistics update and query plan refresh
- **Quarterly**: Database performance tuning and capacity planning

---

**Document Metadata**
- Created: 2025-01-07
- Version: 1.0.0
- Authors: AI Assistant
- Review Status: Initial Draft - CRITICAL ISSUES IDENTIFIED
- Next Review: 2025-01-08 (Urgent - schema fixes required)
- Dependencies: ARCHITECTURE_CONTEXT.md
- Change Impact: CRITICAL - database schema fixes required for production
- Related Files: database/*, alembic/versions/*, api/routers/business_profiles.py