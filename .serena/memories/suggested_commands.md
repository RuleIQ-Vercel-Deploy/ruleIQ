# ruleIQ Suggested Commands

## Development Commands

### Running the Application
```bash
# Start backend server (development)
uvicorn main:app --reload

# Start backend server (production)
uvicorn main:app --host 0.0.0.0 --port 8000

# Start with Docker
docker-compose up -d

# View logs
docker-compose logs -f
```

### Testing Commands
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=. --cov-report=html

# Run fast unit tests
make test-fast

# Run integration tests
make test-integration

# Run AI-specific tests
make test-ai

# Run security tests
make test-security

# Run tests in parallel
pytest -n auto --dist=worksteal

# Run specific test file
pytest tests/unit/test_specific.py

# Run tests with specific marker
pytest -m unit
pytest -m api
pytest -m security
```

### Code Quality Commands
```bash
# Format code with Ruff
ruff format .

# Check code style
ruff check .

# Fix auto-fixable issues
ruff check --fix .

# Run type checking (if mypy is installed)
mypy .

# Check import organization
isort --check-only .

# Fix imports
isort .
```

### Database Commands
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Downgrade migration
alembic downgrade -1

# Initialize database
python database/init_db.py

# Reset database (development)
python scripts/reset_db.py
```

### Development Utilities
```bash
# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Generate requirements
pip freeze > requirements.txt

# Clean up test artifacts
make clean-test

# Run performance benchmarks
pytest tests/performance/ --benchmark-only
```

### Docker Commands
```bash
# Build and start services
docker-compose up --build

# Stop services
docker-compose down

# View service logs
docker-compose logs backend

# Run commands in container
docker-compose exec backend python -c "import main"
```

### Linux System Commands
```bash
# Find files
find . -name "*.py" -type f

# Search in files
grep -r "pattern" --include="*.py" .

# List processes
ps aux | grep python

# Check port usage
netstat -tlnp | grep 8000

# Monitor system resources
top
htop

# Check disk usage
df -h
du -sh *

# View file contents
cat filename.py
less filename.py
head -n 20 filename.py
tail -f logs/app.log
```

## Task Completion Commands

### Before Committing
```bash
# Run comprehensive checks
ruff check .
ruff format .
pytest tests/
alembic check

# Or use the automated script
./scripts/pre_commit_check.sh
```

### After Feature Implementation
```bash
# Run relevant tests
pytest tests/unit/test_new_feature.py
pytest -m "unit or integration"

# Check code quality
ruff check .
ruff format .

# Update documentation if needed
# Generate API docs automatically via FastAPI
```

### Production Deployment
```bash
# Build for production
docker-compose -f docker-compose.prod.yml build

# Deploy
docker-compose -f docker-compose.prod.yml up -d

# Health check
curl http://localhost:8000/health

# View production logs
docker-compose -f docker-compose.prod.yml logs -f
```