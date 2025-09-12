# P0 Task Execution Plan - RuleIQ Critical Infrastructure

**Generated**: 2025-09-09  
**Priority**: P0 - CRITICAL (24-hour deadline)  
**Status**: ACTIVE  

## Executive Summary

Three critical P0 tasks remain to establish foundational infrastructure for RuleIQ. SEC-001 authentication bypass is COMPLETE. These tasks MUST be completed within 24 hours to unblock all downstream work.

## Task Overview

| Task ID | Name | Effort | Status | Deadline | Assignee |
|---------|------|--------|--------|----------|----------|
| FF-001 | Feature Flags System | 16h | TODO | 2025-09-10 09:00 UTC | Backend Lead |
| TEST-001 | Integration Test Framework | 24h | TODO | 2025-09-10 09:00 UTC | QA Lead |
| MON-001 | User Impact Mitigation | 8h | TODO | 2025-09-10 09:00 UTC | DevOps Lead |

## Current State Analysis

### Positive Findings
1. ✅ SEC-001 COMPLETE - JWT authentication middleware v2 implemented with feature flag
2. ✅ Basic feature flag system exists in `/config/feature_flags.py`
3. ✅ Redis already configured and available
4. ✅ Integration test structure exists with good fixtures
5. ✅ Database monitoring partially implemented
6. ✅ Async support throughout the codebase

### Gaps Identified
1. ❌ Feature flag system needs persistence layer and admin UI
2. ❌ Missing testcontainers integration for isolated testing
3. ❌ No Prometheus/Grafana monitoring stack
4. ❌ Missing automatic rollback triggers
5. ❌ No coverage reporting integration
6. ❌ Feature flag audit logging not implemented

## Execution Order & Dependencies

```mermaid
graph LR
    FF-001[Feature Flags<br/>16h] --> TEST-001[Integration Tests<br/>24h]
    FF-001 --> MON-001[Monitoring<br/>8h]
    TEST-001 --> P1[P1 Tasks]
    MON-001 --> P1
```

**Recommended Parallel Execution**:
- FF-001 and MON-001 can run in parallel
- TEST-001 benefits from FF-001 completion but can start immediately

---

# Task FF-001: Enhanced Feature Flags System

## Implementation Plan

### Phase 1: Core Infrastructure Enhancement (4 hours)

#### 1.1 Database Persistence Layer
```python
# /database/models/feature_flags.py
from sqlalchemy import Column, String, Boolean, Integer, JSON, DateTime
from database.base import Base

class FeatureFlagDB(Base):
    __tablename__ = 'feature_flags'
    
    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)
    enabled = Column(Boolean, default=False)
    percentage = Column(Integer, default=0)
    whitelist = Column(JSON, default=list)
    blacklist = Column(JSON, default=list)
    environments = Column(JSON, default=['development'])
    expires_at = Column(DateTime, nullable=True)
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    created_by = Column(String, nullable=True)
    
class FeatureFlagAudit(Base):
    __tablename__ = 'feature_flag_audits'
    
    id = Column(String, primary_key=True)
    flag_name = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False)  # created, updated, deleted, evaluated
    user_id = Column(String, nullable=True)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    result = Column(Boolean, nullable=True)  # For evaluation audits
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
```

#### 1.2 Enhanced Service Layer
```python
# /services/feature_flags_v2.py
from typing import Dict, Any, Optional, List
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from database.models.feature_flags import FeatureFlagDB, FeatureFlagAudit
import uuid

class EnhancedFeatureFlagService:
    """Production-ready feature flag service with persistence and caching"""
    
    def __init__(self, db_session: AsyncSession, redis_client):
        self.db = db_session
        self.redis = redis_client
        self.cache_ttl = 300  # 5 minutes
        self.evaluation_cache_ttl = 60  # 1 minute
        
    async def create_flag(self, flag_data: dict, created_by: str) -> FeatureFlagDB:
        """Create a new feature flag with audit trail"""
        flag = FeatureFlagDB(
            id=str(uuid.uuid4()),
            created_by=created_by,
            **flag_data
        )
        self.db.add(flag)
        
        # Audit log
        audit = FeatureFlagAudit(
            id=str(uuid.uuid4()),
            flag_name=flag.name,
            action='created',
            user_id=created_by,
            new_value=flag_data
        )
        self.db.add(audit)
        
        await self.db.commit()
        await self._invalidate_cache(flag.name)
        return flag
    
    async def update_flag(self, flag_name: str, updates: dict, updated_by: str):
        """Update flag with audit trail"""
        flag = await self.db.query(FeatureFlagDB).filter_by(name=flag_name).first()
        if not flag:
            raise ValueError(f"Flag {flag_name} not found")
        
        old_value = flag.to_dict()
        
        for key, value in updates.items():
            setattr(flag, key, value)
        flag.updated_at = datetime.utcnow()
        
        # Audit log
        audit = FeatureFlagAudit(
            id=str(uuid.uuid4()),
            flag_name=flag_name,
            action='updated',
            user_id=updated_by,
            old_value=old_value,
            new_value=updates
        )
        self.db.add(audit)
        
        await self.db.commit()
        await self._invalidate_cache(flag_name)
        
    async def evaluate(
        self, 
        flag_name: str, 
        user_id: Optional[str] = None,
        environment: str = "production",
        context: Dict[str, Any] = None
    ) -> bool:
        """Evaluate feature flag with caching and audit"""
        
        # Check evaluation cache first
        cache_key = f"ff:eval:{flag_name}:{user_id}:{environment}"
        cached = await self.redis.get(cache_key)
        if cached is not None:
            return cached == "1"
        
        # Get flag from cache or database
        flag = await self._get_flag(flag_name)
        if not flag:
            return False
        
        # Evaluation logic
        result = self._evaluate_flag(flag, user_id, environment, context)
        
        # Cache evaluation result
        await self.redis.setex(cache_key, self.evaluation_cache_ttl, "1" if result else "0")
        
        # Async audit logging (non-blocking)
        asyncio.create_task(self._log_evaluation(flag_name, user_id, result))
        
        return result
    
    async def _get_flag(self, flag_name: str) -> Optional[FeatureFlagDB]:
        """Get flag from cache or database"""
        # Try cache first
        cache_key = f"ff:flag:{flag_name}"
        cached = await self.redis.get(cache_key)
        
        if cached:
            return FeatureFlagDB.from_json(cached)
        
        # Load from database
        flag = await self.db.query(FeatureFlagDB).filter_by(name=flag_name).first()
        
        if flag:
            # Cache for future use
            await self.redis.setex(cache_key, self.cache_ttl, flag.to_json())
        
        return flag
    
    def _evaluate_flag(self, flag, user_id, environment, context) -> bool:
        """Core evaluation logic"""
        # Check environment
        if environment not in flag.environments:
            return False
        
        # Check expiration
        if flag.expires_at and datetime.utcnow() > flag.expires_at:
            return False
        
        # Check blacklist
        if user_id and user_id in flag.blacklist:
            return False
        
        # Check whitelist
        if user_id and user_id in flag.whitelist:
            return True
        
        # Check context-based rules
        if context and flag.metadata.get('rules'):
            if not self._evaluate_rules(flag.metadata['rules'], context):
                return False
        
        # Percentage rollout
        if flag.enabled and user_id:
            hash_val = hash(f"{flag.name}:{user_id}") % 100
            return hash_val < flag.percentage
        
        return flag.enabled
    
    async def get_all_flags_for_user(self, user_id: str, environment: str) -> Dict[str, bool]:
        """Get all flag states for a user (for frontend)"""
        flags = await self.db.query(FeatureFlagDB).all()
        
        result = {}
        for flag in flags:
            result[flag.name] = await self.evaluate(
                flag.name, user_id, environment
            )
        
        return result
```

### Phase 2: Admin API & UI (6 hours)

#### 2.1 FastAPI Routes
```python
# /api/routers/feature_flags.py
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from services.feature_flags_v2 import EnhancedFeatureFlagService

router = APIRouter(prefix="/api/v1/feature-flags", tags=["Feature Flags"])

@router.get("/", response_model=List[FeatureFlagResponse])
async def list_flags(
    environment: Optional[str] = Query(None),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """List all feature flags"""
    service = EnhancedFeatureFlagService(db, get_redis())
    return await service.list_flags(environment)

@router.post("/", response_model=FeatureFlagResponse)
async def create_flag(
    flag_data: CreateFeatureFlagRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new feature flag"""
    service = EnhancedFeatureFlagService(db, get_redis())
    return await service.create_flag(flag_data.dict(), current_user.id)

@router.put("/{flag_name}")
async def update_flag(
    flag_name: str,
    updates: UpdateFeatureFlagRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """Update a feature flag"""
    service = EnhancedFeatureFlagService(db, get_redis())
    await service.update_flag(flag_name, updates.dict(), current_user.id)
    return {"message": "Flag updated successfully"}

@router.post("/{flag_name}/evaluate")
async def evaluate_flag(
    flag_name: str,
    request: EvaluateRequest,
    db: AsyncSession = Depends(get_async_db)
):
    """Evaluate a feature flag for given context"""
    service = EnhancedFeatureFlagService(db, get_redis())
    result = await service.evaluate(
        flag_name,
        request.user_id,
        request.environment,
        request.context
    )
    return {"enabled": result}

@router.get("/{flag_name}/audit")
async def get_flag_audit(
    flag_name: str,
    limit: int = Query(100, le=1000),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_async_db)
):
    """Get audit trail for a feature flag"""
    audits = await db.query(FeatureFlagAudit)\
        .filter_by(flag_name=flag_name)\
        .order_by(FeatureFlagAudit.timestamp.desc())\
        .limit(limit)\
        .all()
    return audits

@router.get("/user/{user_id}")
async def get_user_flags(
    user_id: str,
    environment: str = Query("production"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get all feature flags for a user"""
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(403, "Forbidden")
    
    service = EnhancedFeatureFlagService(db, get_redis())
    return await service.get_all_flags_for_user(user_id, environment)
```

#### 2.2 React Admin Dashboard
```typescript
// /frontend/components/admin/FeatureFlagsManager.tsx
import React, { useState, useEffect } from 'react';
import { 
  Table, Switch, Button, Modal, Form, 
  InputNumber, Select, Tag, Timeline 
} from 'antd';

const FeatureFlagsManager: React.FC = () => {
  const [flags, setFlags] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editModal, setEditModal] = useState(false);
  const [selectedFlag, setSelectedFlag] = useState(null);
  
  const columns = [
    {
      title: 'Flag Name',
      dataIndex: 'name',
      key: 'name',
      render: (name) => <code>{name}</code>
    },
    {
      title: 'Status',
      key: 'status',
      render: (_, record) => (
        <Switch 
          checked={record.enabled}
          onChange={(checked) => handleToggle(record.name, checked)}
        />
      )
    },
    {
      title: 'Rollout',
      dataIndex: 'percentage',
      key: 'percentage',
      render: (pct) => (
        <Tag color={pct === 100 ? 'green' : pct > 0 ? 'blue' : 'gray'}>
          {pct}%
        </Tag>
      )
    },
    {
      title: 'Environments',
      dataIndex: 'environments',
      key: 'environments',
      render: (envs) => envs.map(env => <Tag key={env}>{env}</Tag>)
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <>
          <Button onClick={() => handleEdit(record)}>Edit</Button>
          <Button onClick={() => viewAudit(record.name)}>Audit</Button>
        </>
      )
    }
  ];
  
  const handleToggle = async (flagName: string, enabled: boolean) => {
    await api.put(`/feature-flags/${flagName}`, { enabled });
    fetchFlags();
  };
  
  const handleEdit = (flag) => {
    setSelectedFlag(flag);
    setEditModal(true);
  };
  
  // ... rest of component implementation
};
```

### Phase 3: Testing & Documentation (4 hours)

#### 3.1 Comprehensive Tests
```python
# /tests/test_feature_flags_v2.py
import pytest
from services.feature_flags_v2 import EnhancedFeatureFlagService

class TestEnhancedFeatureFlags:
    
    @pytest.mark.asyncio
    async def test_percentage_rollout(self, async_db_session):
        """Test percentage-based rollout"""
        service = EnhancedFeatureFlagService(async_db_session, fake_redis)
        
        # Create flag with 50% rollout
        await service.create_flag({
            'name': 'test_feature',
            'enabled': True,
            'percentage': 50,
            'environments': ['test']
        }, 'test_user')
        
        # Test with 100 users
        enabled_count = 0
        for i in range(100):
            result = await service.evaluate(
                'test_feature', 
                f'user_{i}',
                'test'
            )
            if result:
                enabled_count += 1
        
        # Should be approximately 50%
        assert 40 <= enabled_count <= 60
    
    @pytest.mark.asyncio
    async def test_audit_trail(self, async_db_session):
        """Test audit trail creation"""
        service = EnhancedFeatureFlagService(async_db_session, fake_redis)
        
        # Create and update flag
        flag = await service.create_flag({
            'name': 'audit_test',
            'enabled': False
        }, 'admin_user')
        
        await service.update_flag('audit_test', {
            'enabled': True,
            'percentage': 100
        }, 'admin_user')
        
        # Check audit trail
        audits = await async_db_session.query(FeatureFlagAudit)\
            .filter_by(flag_name='audit_test')\
            .all()
        
        assert len(audits) == 2
        assert audits[0].action == 'created'
        assert audits[1].action == 'updated'
    
    @pytest.mark.asyncio
    async def test_environment_isolation(self, async_db_session):
        """Test environment-specific flags"""
        service = EnhancedFeatureFlagService(async_db_session, fake_redis)
        
        await service.create_flag({
            'name': 'env_feature',
            'enabled': True,
            'environments': ['production']
        }, 'admin')
        
        # Should be disabled in development
        assert not await service.evaluate('env_feature', 'user1', 'development')
        
        # Should be enabled in production
        assert await service.evaluate('env_feature', 'user1', 'production')
```

### Phase 4: Migration & Deployment (2 hours)

#### 4.1 Database Migration
```python
# /alembic/versions/xxx_add_feature_flags_tables.py
"""Add feature flags tables

Revision ID: xxx
Create Date: 2025-09-09
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'feature_flags',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('name', sa.String, unique=True, nullable=False, index=True),
        sa.Column('enabled', sa.Boolean, default=False),
        sa.Column('percentage', sa.Integer, default=0),
        sa.Column('whitelist', sa.JSON, default=list),
        sa.Column('blacklist', sa.JSON, default=list),
        sa.Column('environments', sa.JSON, default=['development']),
        sa.Column('expires_at', sa.DateTime, nullable=True),
        sa.Column('metadata', sa.JSON, default=dict),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
        sa.Column('created_by', sa.String)
    )
    
    op.create_table(
        'feature_flag_audits',
        sa.Column('id', sa.String, primary_key=True),
        sa.Column('flag_name', sa.String, nullable=False, index=True),
        sa.Column('action', sa.String, nullable=False),
        sa.Column('user_id', sa.String),
        sa.Column('old_value', sa.JSON),
        sa.Column('new_value', sa.JSON),
        sa.Column('result', sa.Boolean),
        sa.Column('timestamp', sa.DateTime, index=True)
    )
    
    # Create index for performance
    op.create_index('idx_ff_audit_timestamp', 'feature_flag_audits', ['timestamp'])

def downgrade():
    op.drop_table('feature_flag_audits')
    op.drop_table('feature_flags')
```

---

# Task TEST-001: Integration Test Framework Setup

## Implementation Plan

### Phase 1: Testcontainers Integration (6 hours)

#### 1.1 Install Dependencies
```bash
pip install testcontainers[postgres,redis]
pip install pytest-asyncio pytest-cov pytest-xdist
pip install httpx  # For async testing
```

#### 1.2 Enhanced Test Configuration
```python
# /tests/integration/conftest_v2.py
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from testcontainers.compose import DockerCompose
import pytest
import asyncio

@pytest.fixture(scope="session")
def postgres_container():
    """Spin up PostgreSQL container for tests"""
    with PostgresContainer("postgres:15-alpine") as postgres:
        postgres.with_env("POSTGRES_PASSWORD", "test")
        postgres.with_env("POSTGRES_DB", "ruleiq_test")
        yield postgres

@pytest.fixture(scope="session")
def redis_container():
    """Spin up Redis container for tests"""
    with RedisContainer("redis:7-alpine") as redis:
        yield redis

@pytest.fixture(scope="session")
def docker_compose():
    """Use docker-compose for complex service dependencies"""
    with DockerCompose("./tests/docker", pull=True) as compose:
        compose.wait_for("http://localhost:8080/health")
        yield compose

@pytest.fixture
async def isolated_app(postgres_container, redis_container):
    """Create isolated FastAPI app with test containers"""
    from main import app
    from config.settings import Settings
    
    # Override settings with container URLs
    test_settings = Settings(
        DATABASE_URL=postgres_container.get_connection_url(),
        REDIS_URL=redis_container.get_connection_url(),
        ENVIRONMENT="testing"
    )
    
    app.state.settings = test_settings
    
    # Initialize database
    async with app.state.db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield app
    
    # Cleanup
    async with app.state.db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

### Phase 2: Coverage & Reporting (6 hours)

#### 2.1 Coverage Configuration
```ini
# /pytest.ini
[tool:pytest]
minversion = 7.0
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto

# Coverage settings
addopts = 
    --cov=.
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
    --cov-report=json
    --cov-fail-under=80
    -v
    --tb=short
    --strict-markers
    --disable-warnings

# Parallel execution
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
    security: Security tests
    
# Coverage exclusions
[coverage:run]
omit = 
    */tests/*
    */migrations/*
    */venv/*
    */__pycache__/*
    */node_modules/*
    
[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
```

#### 2.2 GitHub Actions Integration
```yaml
# /.github/workflows/integration-tests.yml
name: Integration Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: ruleiq_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
          
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
        
    - name: Run integration tests
      env:
        DATABASE_URL: postgresql://postgres:test@localhost:5432/ruleiq_test
        REDIS_URL: redis://localhost:6379
      run: |
        pytest tests/integration \
          --cov=. \
          --cov-report=xml \
          --cov-report=term \
          --junitxml=test-results.xml
          
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: integration
        
    - name: Publish test results
      uses: EnricoMi/publish-unit-test-result-action@v2
      if: always()
      with:
        files: test-results.xml
        
    - name: Comment PR with coverage
      uses: py-cov-action/python-coverage-comment-action@v3
      with:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        MINIMUM_GREEN: 85
        MINIMUM_ORANGE: 70
```

### Phase 3: Test Suite Implementation (8 hours)

#### 3.1 Authentication Tests (Validate SEC-001 Fix)
```python
# /tests/integration/test_auth_security.py
import pytest
from httpx import AsyncClient

class TestAuthenticationSecurity:
    """Validate SEC-001 fix is working correctly"""
    
    @pytest.mark.asyncio
    async def test_middleware_bypass_prevented(self, async_client: AsyncClient):
        """Test that authentication bypass is prevented"""
        
        # Attempt bypass techniques that worked before SEC-001 fix
        bypass_attempts = [
            {"Authorization": "Bearer null"},
            {"Authorization": "Bearer undefined"},
            {"Authorization": "Bearer "},
            {"Authorization": ""},
            # No Authorization header
            {},
        ]
        
        for headers in bypass_attempts:
            response = await async_client.get(
                "/api/v1/users/me",
                headers=headers
            )
            assert response.status_code == 401, \
                f"Bypass attempt succeeded with headers: {headers}"
    
    @pytest.mark.asyncio
    async def test_valid_token_required(self, async_client: AsyncClient):
        """Test that valid JWT is properly validated"""
        
        # Invalid token format
        response = await async_client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 401
        
        # Expired token
        expired_token = create_test_token(expired=True)
        response = await async_client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_feature_flag_controls_middleware(self, async_client: AsyncClient):
        """Test that feature flag properly controls middleware version"""
        
        # Check current middleware version
        response = await async_client.get("/api/v1/health/detailed")
        health_data = response.json()
        
        auth_status = health_data['services']['authentication']['middleware']
        assert auth_status['version'] == 'v2'
        assert auth_status['secure'] == True
        assert auth_status['vulnerability_fixed'] == True
```

#### 3.2 Feature Flag Integration Tests
```python
# /tests/integration/test_feature_flags.py
import pytest
from httpx import AsyncClient

class TestFeatureFlagsIntegration:
    
    @pytest.mark.asyncio
    async def test_flag_creation_and_evaluation(
        self, 
        async_client: AsyncClient,
        admin_headers: dict
    ):
        """Test complete feature flag lifecycle"""
        
        # Create flag
        flag_data = {
            "name": "test_integration_feature",
            "enabled": True,
            "percentage": 50,
            "environments": ["testing"]
        }
        
        response = await async_client.post(
            "/api/v1/feature-flags",
            json=flag_data,
            headers=admin_headers
        )
        assert response.status_code == 200
        
        # Evaluate flag
        eval_response = await async_client.post(
            "/api/v1/feature-flags/test_integration_feature/evaluate",
            json={
                "user_id": "test_user",
                "environment": "testing"
            }
        )
        assert eval_response.status_code == 200
        result = eval_response.json()
        assert "enabled" in result
```

### Phase 4: Performance & Load Testing (4 hours)

#### 4.1 Locust Configuration
```python
# /tests/performance/locustfile.py
from locust import HttpUser, task, between
import random

class RuleIQUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login and get token"""
        response = self.client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPassword123!"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def check_feature_flag(self):
        """Test feature flag evaluation performance"""
        self.client.post(
            f"/api/v1/feature-flags/new_feature/evaluate",
            json={
                "user_id": f"user_{random.randint(1, 1000)}",
                "environment": "production"
            },
            headers=self.headers
        )
    
    @task(2)
    def get_dashboard(self):
        """Test dashboard endpoint"""
        self.client.get("/api/v1/dashboard", headers=self.headers)
    
    @task(1)
    def health_check(self):
        """Test health endpoint"""
        self.client.get("/health")
```

---

# Task MON-001: User Impact Mitigation & Monitoring

## Implementation Plan

### Phase 1: Prometheus & Grafana Setup (3 hours)

#### 1.1 Docker Compose Configuration
```yaml
# /monitoring/docker-compose.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: ruleiq_prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: ruleiq_grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_INSTALL_PLUGINS=redis-datasource
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources
    networks:
      - monitoring

  alertmanager:
    image: prom/alertmanager:latest
    container_name: ruleiq_alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
    networks:
      - monitoring

volumes:
  prometheus_data:
  grafana_data:

networks:
  monitoring:
    driver: bridge
```

#### 1.2 Prometheus Configuration
```yaml
# /monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

rule_files:
  - "alerts/*.yml"

scrape_configs:
  - job_name: 'ruleiq-api'
    static_configs:
      - targets: ['host.docker.internal:8000']
    metrics_path: '/metrics'
    
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
      
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']
```

### Phase 2: Application Metrics (3 hours)

#### 2.1 Prometheus Integration
```python
# /monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from fastapi import Response
import time
from functools import wraps

# Define metrics
request_count = Counter(
    'ruleiq_requests_total',
    'Total requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'ruleiq_request_duration_seconds',
    'Request duration',
    ['method', 'endpoint']
)

active_users = Gauge(
    'ruleiq_active_users',
    'Number of active users'
)

feature_flag_evaluations = Counter(
    'ruleiq_feature_flag_evaluations',
    'Feature flag evaluations',
    ['flag_name', 'result']
)

auth_failures = Counter(
    'ruleiq_auth_failures_total',
    'Authentication failures',
    ['reason']
)

database_pool_size = Gauge(
    'ruleiq_database_pool_size',
    'Database connection pool size',
    ['pool_type']
)

# Middleware for automatic metrics
class MetricsMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request, call_next):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        
        # Record metrics
        request_count.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        request_duration.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response

# Metrics endpoint
async def metrics_endpoint():
    return Response(
        content=generate_latest(),
        media_type="text/plain"
    )
```

#### 2.2 Alert Rules
```yaml
# /monitoring/alerts/critical.yml
groups:
  - name: critical_alerts
    interval: 30s
    rules:
      - alert: HighErrorRate
        expr: |
          rate(ruleiq_requests_total{status=~"5.."}[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"
          
      - alert: AuthenticationFailures
        expr: |
          rate(ruleiq_auth_failures_total[5m]) > 10
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "High authentication failure rate"
          description: "{{ $value }} auth failures per second"
          
      - alert: DatabasePoolExhausted
        expr: |
          ruleiq_database_pool_size / ruleiq_database_pool_max > 0.9
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Database pool near exhaustion"
          description: "Pool usage at {{ $value }}%"
```

### Phase 3: Automatic Rollback System (2 hours)

#### 3.1 Rollback Service
```python
# /services/rollback_service.py
from typing import Dict, Any
import asyncio
from datetime import datetime, timedelta

class AutomaticRollbackService:
    """Automatic rollback based on monitoring metrics"""
    
    def __init__(self, metrics_client, feature_flag_service):
        self.metrics = metrics_client
        self.flags = feature_flag_service
        self.thresholds = {
            'error_rate': 0.05,  # 5% error rate
            'p95_latency': 2.0,  # 2 seconds
            'auth_failures': 100,  # per minute
        }
        
    async def monitor_and_rollback(self):
        """Continuous monitoring loop"""
        while True:
            try:
                metrics = await self.get_current_metrics()
                
                if self.should_rollback(metrics):
                    await self.execute_rollback(metrics)
                    
            except Exception as e:
                logger.error(f"Rollback monitor error: {e}")
                
            await asyncio.sleep(30)  # Check every 30 seconds
    
    def should_rollback(self, metrics: Dict[str, Any]) -> bool:
        """Determine if rollback is needed"""
        
        # Check error rate
        if metrics.get('error_rate', 0) > self.thresholds['error_rate']:
            return True
            
        # Check latency
        if metrics.get('p95_latency', 0) > self.thresholds['p95_latency']:
            return True
            
        # Check auth failures (potential attack)
        if metrics.get('auth_failures_per_min', 0) > self.thresholds['auth_failures']:
            return True
            
        return False
    
    async def execute_rollback(self, metrics: Dict[str, Any]):
        """Execute automatic rollback"""
        logger.warning(f"Executing automatic rollback due to metrics: {metrics}")
        
        # 1. Disable problematic feature flags
        recent_flags = await self.flags.get_recently_enabled_flags(minutes=30)
        for flag in recent_flags:
            await self.flags.disable_flag(flag.name, reason="Automatic rollback")
            
        # 2. Send alerts
        await self.send_rollback_alert(metrics, recent_flags)
        
        # 3. Create incident
        await self.create_incident(metrics, recent_flags)
        
    async def get_current_metrics(self) -> Dict[str, Any]:
        """Query Prometheus for current metrics"""
        queries = {
            'error_rate': 'rate(ruleiq_requests_total{status=~"5.."}[5m])',
            'p95_latency': 'histogram_quantile(0.95, rate(ruleiq_request_duration_seconds_bucket[5m]))',
            'auth_failures_per_min': 'rate(ruleiq_auth_failures_total[1m]) * 60'
        }
        
        results = {}
        for metric, query in queries.items():
            value = await self.metrics.query(query)
            results[metric] = value
            
        return results
```

#### 3.2 Integration with Main App
```python
# Add to main.py lifespan
from services.rollback_service import AutomaticRollbackService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ... existing code ...
    
    # Start rollback monitor
    rollback_service = AutomaticRollbackService(
        metrics_client=prometheus_client,
        feature_flag_service=feature_flag_service
    )
    rollback_task = asyncio.create_task(
        rollback_service.monitor_and_rollback()
    )
    app.state.rollback_task = rollback_task
    
    yield
    
    # Cleanup
    rollback_task.cancel()
```

## Success Criteria

### FF-001 Success Metrics
- ✅ Database persistence for feature flags
- ✅ Admin UI for flag management
- ✅ Audit trail for all changes
- ✅ <50ms evaluation latency
- ✅ 100% test coverage for flag service
- ✅ Gradual rollout capability
- ✅ Environment-specific configurations

### TEST-001 Success Metrics
- ✅ Testcontainers integration working
- ✅ 80%+ code coverage achieved
- ✅ CI/CD pipeline with automated tests
- ✅ Parallel test execution enabled
- ✅ SEC-001 fix validated with tests
- ✅ Coverage reports in PRs
- ✅ <5 minute test execution time

### MON-001 Success Metrics
- ✅ Prometheus & Grafana deployed
- ✅ All critical metrics exposed
- ✅ Alert rules configured
- ✅ Automatic rollback functional
- ✅ <5 minute incident detection
- ✅ Zero data loss guarantee
- ✅ Dashboard for real-time monitoring

## Risk Mitigation

1. **Database Migration Risk**: Test migrations in staging first
2. **Performance Impact**: Use caching aggressively
3. **Rollback False Positives**: Implement confirmation delay
4. **Test Flakiness**: Use testcontainers for isolation
5. **Monitoring Overhead**: Sample metrics appropriately

## Handoff Notes

### For Backend Lead (FF-001)
- Start with database models and migration
- Focus on caching for performance
- Implement audit logging from the start
- Create comprehensive API documentation

### For QA Lead (TEST-001)
- Set up testcontainers first
- Focus on SEC-001 validation tests
- Implement coverage reporting early
- Create test data factories

### For DevOps Lead (MON-001)
- Deploy monitoring stack first
- Configure alerts conservatively initially
- Test rollback in staging thoroughly
- Document incident response procedures

## Next Steps After P0 Completion

Once all P0 tasks are complete:
1. Run full regression test suite
2. Validate all security fixes
3. Deploy to staging environment
4. Begin P1 task execution
5. Schedule production deployment

---

**END OF P0 EXECUTION PLAN**