# RuleIQ Quick Reference Guide - 2025

## 🚀 Quick Start
```bash
# Always activate environment first
source /home/omar/Documents/ruleIQ/.venv/bin/activate

# Check Doppler secrets
doppler configs
doppler secrets get SECRET_NAME --plain

# Run tests
pytest                           # Run all tests
pytest tests/unit/              # Run unit tests only
pytest --collect-only           # Check for collection errors
pytest --cov=. --cov-report=html # Generate coverage report
```

## 🔧 Current Configuration

### Environment
- Python: 3.11.9
- Virtual Env: `/home/omar/Documents/ruleIQ/.venv`
- Secrets: Doppler (not local .env files)
- Database: PostgreSQL
- Cache: Redis

### Key Changes (September 2025)
- ✅ Celery removed → Use LangGraph
- ✅ Secrets in Doppler → Not .env files
- ✅ Test suite fixed → 817+ tests available
- ✅ Python 3.11 compatible

## 📁 Key Directories

### Backend
- `/api/routers/` - FastAPI endpoints (95+ files)
- `/services/` - Business logic (140+ files)
- `/database/` - Models and migrations (35+ files)
- `/langgraph_agent/` - Task orchestration (50+ files)

### Frontend
- `/frontend/app/` - Next.js pages
- `/frontend/components/` - React components
- `/frontend/lib/` - Utilities and helpers

### Tests
- `/tests/unit/` - Unit tests
- `/tests/integration/` - API integration tests
- `/tests/e2e/` - End-to-end tests
- `/tests/ai/` - AI service tests

## 🛠️ Common Commands

### Development
```bash
# Start backend
uvicorn main:app --reload --port 8000

# Start frontend
cd frontend && npm run dev

# Run linting
ruff check .
black . --check

# Type checking
mypy .
```

### Testing
```bash
# Run specific test file
pytest tests/unit/test_file.py -v

# Run with debugging
pytest -vv --tb=short

# Run async tests
pytest -m asyncio

# Skip slow tests
pytest -m "not slow"
```

### Doppler Secrets
```bash
# List all secrets
doppler secrets

# Get specific secret
doppler secrets get DATABASE_URL --plain

# Set secret
doppler secrets set KEY=value

# Download as .env (fallback only)
doppler secrets download --no-file --format env > .env.local
```

## ⚠️ Known Issues & Fixes

### Import Errors
- Check for syntax errors (trailing commas, malformed docstrings)
- Ensure Python 3.11 compatibility (Self type hint)
- Verify all dependencies installed

### Test Failures
- Database: Ensure PostgreSQL is running
- Redis: Start Redis for caching tests
- Secrets: Configure Doppler properly

### Common Error Fixes
```python
# Self type hint fix
try:
    from typing import Self
except ImportError:
    from typing_extensions import Self

# Missing settings attribute
data_dir = getattr(settings, 'data_dir', './data')

# 204 status code fix
@router.post('/endpoint', status_code=204)
async def handler() -> None:  # Return None for 204
    # process
    return None  # Not return data
```

## 📊 Current Metrics
- **Tests**: 817+ available
- **Files**: 26.5K Python, 17.4K TypeScript
- **Issues**: 13,846 SonarCloud issues
- **Security**: 126 vulnerabilities (High priority)
- **Coverage**: Now measurable (was 0%)

## 🎯 Priority Tasks
1. Fix security vulnerabilities (126)
2. Configure Doppler completely
3. Setup SonarCloud coverage
4. Remove Celery remnants
5. Fix database test configuration

## 📚 Key Services

### AI Services
- `services/ai/` - All AI integrations
- Circuit breaker patterns implemented
- Cost tracking enabled
- Multiple providers (OpenAI, Anthropic, Gemini)

### Authentication
- JWT-based authentication
- `/api/routers/auth.py` - Auth endpoints
- Doppler for secrets

### Compliance
- ISO 27001, SOC2, GDPR frameworks
- UK compliance specialized support
- `/services/compliance/` - Core logic

## 🔍 Debugging Tips

### Check Service Status
```python
# In Python shell
from main import app
print("App started successfully")

# Check database
from database.session import engine
engine.connect()

# Check Redis
import redis
r = redis.Redis()
r.ping()
```

### Common Pytest Issues
```bash
# Collection errors
pytest --collect-only 2>&1 | grep ERROR

# Import issues
python -c "from main import app"

# Async test issues
pytest -m asyncio --tb=short
```

## 📝 Notes
- Always use Doppler for secrets
- Never commit .env files
- Use LangGraph, not Celery
- Test coverage is real (817+ tests)
- Security issues are high priority

Last Updated: September 2025