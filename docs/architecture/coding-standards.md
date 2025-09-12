# RuleIQ Coding Standards

## Overview
This document defines the coding standards and conventions for the RuleIQ compliance automation platform. All contributors must follow these standards to ensure consistency, maintainability, and quality across the codebase.

## Python Backend Standards

### Code Style
- **PEP 8 Compliance**: All Python code must follow PEP 8 with these specifications:
  - Line length: 100 characters maximum (enforced by ruff)
  - Indentation: 4 spaces (no tabs)
  - String quotes: Double quotes `"` for strings
  - Trailing commas: Required in multi-line structures

### File Organization
- **File length**: Maximum 500 lines per file
- **Function length**: Maximum 50 lines per function
- **Class length**: Maximum 100 lines per class
- **Module structure**: Group by feature/responsibility

### Naming Conventions
```python
# Variables and functions: snake_case
user_name = "John"
def calculate_compliance_score():
    pass

# Classes: PascalCase
class ComplianceAssessment:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT = 30

# Private methods/attributes: _leading_underscore
def _internal_validation():
    pass

# Type aliases: PascalCase
UserDict = Dict[str, Any]

# Enum values: UPPER_SNAKE_CASE
class Status(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
```

### Type Hints
All functions must include type hints:
```python
from typing import Optional, List, Dict
from decimal import Decimal

def calculate_risk_score(
    assessments: List[Assessment],
    weights: Optional[Dict[str, float]] = None
) -> Decimal:
    """Calculate weighted risk score."""
    pass
```

### Docstrings
Use Google-style docstrings for all public functions, classes, and modules:
```python
def process_compliance_data(
    data: Dict[str, Any],
    framework: str,
    validate: bool = True
) -> ComplianceResult:
    """
    Process compliance data against specified framework.
    
    Args:
        data: Raw compliance data from assessment
        framework: Compliance framework identifier (e.g., 'gdpr', 'iso27001')
        validate: Whether to validate data before processing
    
    Returns:
        Processed compliance result with score and recommendations
    
    Raises:
        ValidationError: If data validation fails
        FrameworkNotFoundError: If framework is not supported
    
    Example:
        >>> result = process_compliance_data(
        ...     {"controls": [...]},
        ...     "gdpr"
        ... )
        >>> print(result.score)
        85.5
    """
    pass
```

### Error Handling
```python
# Create domain-specific exceptions
class ComplianceError(Exception):
    """Base exception for compliance-related errors."""
    pass

class AssessmentError(ComplianceError):
    """Raised when assessment processing fails."""
    def __init__(self, assessment_id: str, reason: str):
        self.assessment_id = assessment_id
        self.reason = reason
        super().__init__(f"Assessment {assessment_id} failed: {reason}")

# Use specific exception handling
try:
    result = process_assessment(data)
except AssessmentError as e:
    logger.warning(f"Assessment failed: {e}")
    return ErrorResponse(error="assessment_failed", details=str(e))
except ComplianceError as e:
    logger.error(f"Compliance error: {e}")
    return ErrorResponse(error="compliance_error")
```

### Database Models
```python
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, UTC
import uuid

class Assessment(Base):
    """Assessment database model."""
    __tablename__ = "assessments"
    
    # Entity-specific primary key
    assessment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign keys with clear naming
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    framework_id = Column(UUID(as_uuid=True), ForeignKey("frameworks.framework_id"))
    
    # Timestamps with _at suffix
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), onupdate=lambda: datetime.now(UTC))
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Booleans with is_ prefix
    is_active = Column(Boolean, default=True)
    is_completed = Column(Boolean, default=False)
    
    # Counts with _count suffix
    control_count = Column(Integer, default=0)
    issue_count = Column(Integer, default=0)
```

## TypeScript/React Frontend Standards

### File Organization
```typescript
// Component files: PascalCase.tsx
components/ComplianceAssessment.tsx

// Utility files: camelCase.ts
utils/dateHelpers.ts

// Type definition files: types.ts or interfaces.ts
types/assessment.types.ts
```

### Component Structure
```typescript
// Functional components with TypeScript
import React, { useState, useEffect } from 'react';
import { AssessmentData } from '@/types/assessment.types';

interface ComplianceAssessmentProps {
  assessmentId: string;
  onComplete?: (result: AssessmentResult) => void;
  className?: string;
}

export const ComplianceAssessment: React.FC<ComplianceAssessmentProps> = ({
  assessmentId,
  onComplete,
  className = ''
}) => {
  const [data, setData] = useState<AssessmentData | null>(null);
  const [loading, setLoading] = useState(true);
  
  // Component logic...
  
  return (
    <div className={`assessment-container ${className}`}>
      {/* Component JSX */}
    </div>
  );
};
```

### State Management
```typescript
// Use React hooks and context for state
import { createContext, useContext, useReducer } from 'react';

interface ComplianceState {
  assessments: Assessment[];
  currentFramework: string | null;
  loading: boolean;
}

const ComplianceContext = createContext<ComplianceState | undefined>(undefined);

export const useCompliance = () => {
  const context = useContext(ComplianceContext);
  if (!context) {
    throw new Error('useCompliance must be used within ComplianceProvider');
  }
  return context;
};
```

### API Integration
```typescript
// Centralized API service
class ComplianceAPI {
  private baseURL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  
  async getAssessment(id: string): Promise<Assessment> {
    const response = await fetch(`${this.baseURL}/api/v1/assessments/${id}`, {
      headers: {
        'Authorization': `Bearer ${this.getToken()}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      throw new Error(`Failed to fetch assessment: ${response.statusText}`);
    }
    
    return response.json();
  }
}

export const complianceAPI = new ComplianceAPI();
```

## Testing Standards

### Python Tests
```python
import pytest
from datetime import datetime
from unittest.mock import Mock, patch

@pytest.fixture
def sample_assessment():
    """Provide sample assessment for testing."""
    return Assessment(
        assessment_id="123e4567-e89b-12d3-a456-426614174000",
        framework="gdpr",
        created_at=datetime.now(UTC)
    )

class TestComplianceService:
    """Test compliance service functionality."""
    
    def test_calculate_score_with_valid_data(self, sample_assessment):
        """Test score calculation with valid assessment data."""
        service = ComplianceService()
        score = service.calculate_score(sample_assessment)
        
        assert score >= 0
        assert score <= 100
        assert isinstance(score, Decimal)
    
    def test_calculate_score_handles_empty_controls(self):
        """Test that empty controls list returns zero score."""
        service = ComplianceService()
        assessment = Assessment(controls=[])
        
        score = service.calculate_score(assessment)
        
        assert score == 0
    
    @pytest.mark.parametrize("framework,expected", [
        ("gdpr", 85.5),
        ("iso27001", 92.0),
        ("pci-dss", 78.3)
    ])
    def test_framework_specific_scoring(self, framework, expected):
        """Test scoring for different compliance frameworks."""
        # Test implementation
        pass
```

### TypeScript/React Tests
```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ComplianceAssessment } from '@/components/ComplianceAssessment';

describe('ComplianceAssessment', () => {
  it('renders assessment form correctly', () => {
    render(<ComplianceAssessment assessmentId="123" />);
    
    expect(screen.getByText('Compliance Assessment')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /start assessment/i })).toBeEnabled();
  });
  
  it('handles assessment completion', async () => {
    const onComplete = jest.fn();
    render(
      <ComplianceAssessment 
        assessmentId="123" 
        onComplete={onComplete}
      />
    );
    
    const submitButton = screen.getByRole('button', { name: /complete/i });
    await userEvent.click(submitButton);
    
    await waitFor(() => {
      expect(onComplete).toHaveBeenCalledWith(
        expect.objectContaining({
          assessmentId: '123',
          score: expect.any(Number)
        })
      );
    });
  });
});
```

## Git Workflow

### Branch Naming
- `main` - Production branch
- `develop` - Development integration
- `feature/[task-id]-description` - New features
- `fix/[issue-id]-description` - Bug fixes
- `refactor/description` - Code refactoring
- `docs/description` - Documentation updates

### Commit Messages
```bash
# Format: type(scope): subject

feat(auth): add two-factor authentication
fix(api): resolve timeout in assessment endpoint
docs(readme): update installation instructions
refactor(services): extract compliance logic to separate module
test(auth): add unit tests for JWT validation
```

## Code Review Checklist

### Before Submitting PR
- [ ] All tests pass locally
- [ ] Code follows style guidelines (run `ruff check`)
- [ ] Type hints added for new functions
- [ ] Docstrings added/updated
- [ ] No hardcoded values or secrets
- [ ] Database migrations included if needed
- [ ] Frontend components are responsive
- [ ] API endpoints documented

### Review Focus Areas
1. **Security**: No exposed credentials, SQL injection prevention, input validation
2. **Performance**: Efficient queries, proper caching, pagination
3. **Error Handling**: Graceful failures, proper logging, user-friendly messages
4. **Testing**: Adequate coverage, edge cases handled
5. **Documentation**: Clear docstrings, updated README if needed

## Performance Guidelines

### Backend Optimization
```python
from functools import lru_cache
from typing import List
import asyncio

# Cache expensive computations
@lru_cache(maxsize=128)
def calculate_framework_score(framework_id: str, control_scores: tuple) -> float:
    """Cache framework score calculations."""
    # Expensive calculation
    return sum(control_scores) / len(control_scores)

# Use async for I/O operations
async def fetch_assessments_batch(user_ids: List[str]) -> List[Assessment]:
    """Fetch assessments for multiple users concurrently."""
    tasks = [fetch_user_assessments(uid) for uid in user_ids]
    results = await asyncio.gather(*tasks)
    return [item for sublist in results for item in sublist]

# Use generators for large datasets
def process_large_dataset(file_path: str) -> Generator[Dict, None, None]:
    """Process large file without loading into memory."""
    with open(file_path, 'r') as f:
        for line in f:
            data = json.loads(line)
            yield process_record(data)
```

### Frontend Optimization
```typescript
// Lazy loading for heavy components
const ComplianceChart = lazy(() => import('./ComplianceChart'));

// Memoization for expensive computations
const MemoizedAssessment = memo(({ data }) => {
  const score = useMemo(
    () => calculateComplexScore(data),
    [data]
  );
  
  return <AssessmentDisplay score={score} />;
});

// Debounce user input
const SearchInput = () => {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 300);
  
  useEffect(() => {
    if (debouncedQuery) {
      searchAPI(debouncedQuery);
    }
  }, [debouncedQuery]);
};
```

## Security Standards

### Authentication & Authorization
- Use JWT tokens with proper expiration
- Implement refresh token rotation
- Validate all user inputs
- Use parameterized database queries
- Implement rate limiting on APIs
- Follow principle of least privilege

### Data Protection
- Encrypt sensitive data at rest
- Use HTTPS for all communications
- Sanitize user inputs before storage
- Implement audit logging
- Regular security dependency updates

## Monitoring & Logging

### Logging Standards
```python
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def log_execution(func):
    """Decorator to log function execution."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger.debug(f"Entering {func.__name__} with args: {args[:2]}")  # Limit logged args
        try:
            result = await func(*args, **kwargs)
            logger.debug(f"Exiting {func.__name__} successfully")
            return result
        except Exception as e:
            logger.exception(f"Error in {func.__name__}: {e}")
            raise
    return wrapper

@log_execution
async def process_assessment(assessment_id: str) -> AssessmentResult:
    """Process assessment with automatic logging."""
    logger.info(f"Processing assessment {assessment_id}")
    # Processing logic
```

### Metrics Collection
- Response times for API endpoints
- Database query performance
- Error rates by service
- User action tracking (privacy-compliant)
- Resource utilization

## Continuous Improvement

### Code Quality Tools
```bash
# Python
ruff check .           # Linting
ruff format .          # Formatting
mypy .                 # Type checking
pytest --cov          # Test coverage

# TypeScript/React
npm run lint          # ESLint
npm run format        # Prettier
npm run typecheck     # TypeScript check
npm test             # Jest tests
```

### Regular Reviews
- Weekly code quality reviews
- Monthly dependency updates
- Quarterly security audits
- Performance profiling for critical paths

## Exceptions and Edge Cases

### Known Deviations
- Legacy payment module uses callbacks (migration planned)
- Some older endpoints lack full type hints (ongoing refactor)
- Frontend state management transitioning to modern patterns

### Technical Debt Registry
Document technical debt with:
- Description of the issue
- Impact on system
- Proposed solution
- Priority level
- Estimated effort

## Resources

### Internal Documentation
- [Architecture Overview](./tech-stack.md)
- [API Documentation](/docs/api/)
- [Database Schema](/docs/database/)

### External Resources
- [Python PEP 8](https://pep8.org/)
- [TypeScript Best Practices](https://www.typescriptlang.org/docs/handbook/declaration-files/do-s-and-don-ts.html)
- [React Documentation](https://react.dev/)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/best-practices/)