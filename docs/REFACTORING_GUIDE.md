# RuleIQ Code Refactoring Guide

## Priority 1: High Cognitive Complexity Functions

### 1. main.py Refactoring ✅
**Status**: Completed
- Created `main_refactored.py` with reduced complexity
- Extracted lifecycle management to `ApplicationLifecycle` class
- Separated route configuration to `ApplicationFactory`
- Created `HealthCheckService` for health endpoints
- **Complexity Reduction**: From ~40 to <10 per function

### 2. Common Patterns to Refactor

#### Pattern: Long Import Lists
**Problem**: Files with 20+ imports indicate poor module organization
**Solution**:
```python
# Before
from api.routers import router1, router2, router3, ... router20

# After - Group in separate module
# api/routers/__init__.py
from .auth import auth_router
from .users import users_router
# ... etc

# main.py
from api.routers import get_all_routers
for router in get_all_routers():
    app.include_router(router)
```

#### Pattern: Nested Conditionals
**Problem**: Deep nesting makes code hard to follow
**Solution**: Use early returns and guard clauses
```python
# Before
def process_data(data):
    if data:
        if data.is_valid():
            if data.has_permission():
                # actual logic
                return result
            else:
                return error
        else:
            return error
    else:
        return error

# After
def process_data(data):
    if not data:
        return error("No data provided")
    if not data.is_valid():
        return error("Invalid data")
    if not data.has_permission():
        return error("Permission denied")
    
    # actual logic with no nesting
    return result
```

#### Pattern: Long Functions
**Problem**: Functions > 50 lines are hard to test and understand
**Solution**: Extract to smaller, focused functions
```python
# Before
def process_assessment(assessment_id):
    # 100+ lines of code doing multiple things
    # validation logic
    # business logic
    # database operations
    # notification sending
    # logging
    
# After
def process_assessment(assessment_id):
    assessment = validate_assessment(assessment_id)
    result = apply_business_rules(assessment)
    save_to_database(result)
    send_notifications(result)
    log_processing(result)
    return result

def validate_assessment(assessment_id):
    # 10-15 lines focused on validation

def apply_business_rules(assessment):
    # 10-15 lines focused on business logic
```

## Priority 2: Code Duplication

### Common Duplications to Fix

#### 1. Database Session Management
**Location**: Multiple service files
**Solution**: Create a base repository pattern
```python
# database/base_repository.py
class BaseRepository:
    def __init__(self, model_class):
        self.model_class = model_class
    
    async def get_by_id(self, id):
        async with get_session() as session:
            return await session.get(self.model_class, id)
    
    async def create(self, data):
        async with get_session() as session:
            instance = self.model_class(**data)
            session.add(instance)
            await session.commit()
            return instance
```

#### 2. Error Handling
**Location**: API endpoints
**Solution**: Create error handling decorators
```python
# utils/error_handlers.py
def handle_api_errors(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except PermissionError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")
    return wrapper
```

#### 3. Logging Patterns
**Location**: Throughout codebase
**Solution**: Create logging mixins
```python
# utils/logging_mixin.py
class LoggingMixin:
    @property
    def logger(self):
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger
    
    def log_operation(self, operation, **kwargs):
        self.logger.info(f"{operation}", extra=kwargs)
```

## Priority 3: TODO Comments

### Conversion Strategy
1. **Critical TODOs** → GitHub Issues with P0/P1 labels
2. **Feature TODOs** → Product backlog items
3. **Optimization TODOs** → Performance backlog
4. **Documentation TODOs** → Documentation tasks

### TODO Categories Found

#### Security TODOs (Convert to P0)
- Implement rate limiting for AI endpoints
- Add input sanitization for SQL queries
- Implement API key rotation

#### Performance TODOs (Convert to P2)
- Cache frequently accessed framework data
- Optimize database queries with indexes
- Implement connection pooling for Redis

#### Feature TODOs (Convert to P3)
- Add batch processing for reports
- Implement webhook retries
- Add audit log export functionality

## Priority 4: Missing Type Hints

### Type Hint Standards
```python
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from pydantic import BaseModel

# Always use type hints for:
# 1. Function parameters
def process_data(
    data: Dict[str, Any],
    user_id: int,
    options: Optional[Dict[str, str]] = None
) -> ProcessResult:
    pass

# 2. Class attributes
class Service:
    repository: BaseRepository
    cache: Optional[CacheManager]
    
# 3. Return types
async def get_user(user_id: int) -> Optional[User]:
    pass
```

## Implementation Plan

### Week 1 (Days 1-3)
1. ✅ Set up SonarCloud integration
2. ✅ Create quality scanning tools
3. Refactor top 10 high-complexity functions
4. Extract common patterns to utilities

### Week 2 (Days 4-6)
1. Implement repository pattern for database
2. Create error handling framework
3. Add comprehensive type hints
4. Convert TODOs to trackable issues

### Week 3 (Days 7+)
1. Continuous monitoring via SonarCloud
2. Maintain Grade A/B rating
3. Document best practices
4. Team training on quality standards

## Success Metrics

### Target Metrics (Grade A/B)
- **Cognitive Complexity**: < 15 per function
- **Cyclomatic Complexity**: < 10 per function
- **Code Duplication**: < 3%
- **Code Coverage**: > 80%
- **Maintainability Index**: > 50
- **Technical Debt Ratio**: < 5%

### Current Status
- **Cognitive Complexity**: 198 functions > 15 (needs fixing)
- **Code Duplication**: 5.9% (needs reduction)
- **TODO Comments**: 458 (needs conversion)
- **Missing Docstrings**: 845 (needs addition)

## Quality Gates

### PR Merge Requirements
1. All tests passing
2. Code coverage > 80%
3. No critical SonarCloud issues
4. Cognitive complexity < 15
5. No security hotspots

### Monitoring
- Daily SonarCloud scans
- Weekly quality reports
- Monthly trend analysis
- Quarterly quality review

## Tools and Scripts

### Available Scripts
- `/scripts/code_quality_scanner.py` - Scan for quality issues
- `/scripts/complexity_reducer.py` - Auto-refactor complex functions
- `/scripts/duplicate_finder.py` - Find and fix duplications

### IDE Integration
```json
// .vscode/settings.json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.linting.mypyEnabled": true
}
```

## Best Practices Going Forward

1. **Write Clean Code First Time**
   - Keep functions under 20 lines
   - Complexity under 10
   - Always add type hints
   - Write docstrings immediately

2. **Code Review Checklist**
   - [ ] Cognitive complexity < 15
   - [ ] No code duplication
   - [ ] Type hints present
   - [ ] Docstrings added
   - [ ] Tests included

3. **Continuous Improvement**
   - Weekly refactoring sessions
   - Monthly quality reviews
   - Quarterly training on best practices

## Resources

- [SonarCloud Dashboard](https://sonarcloud.io/organizations/ruleiq)
- [Python Clean Code Guide](https://docs.python-guide.org/writing/style/)
- [Cognitive Complexity Explained](https://www.sonarsource.com/docs/CognitiveComplexity.pdf)
- [Refactoring Patterns](https://refactoring.guru/refactoring)