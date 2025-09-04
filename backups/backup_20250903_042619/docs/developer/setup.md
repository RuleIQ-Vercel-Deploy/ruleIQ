# Development Environment Setup

## Prerequisites

- **Python**: 3.8+ (3.11 recommended)
- **Node.js**: 18+ (20 recommended)
- **PostgreSQL**: 13+
- **Redis**: 6+
- **pnpm**: Latest version
- **Docker**: For containerized development (optional)

## Quick Start

### 1. Clone and Setup Backend

```bash
# Clone repository
git clone https://github.com/your-org/ruleiq.git
cd ruleiq

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# 🔐 Secrets Management Setup
# RECOMMENDED: Doppler (Production secrets management)
curl -Ls https://cli.doppler.com/install.sh | sudo sh
doppler login
doppler setup  # Follow prompts to select project/config

# Alternative: Local environment file
cp .env.template .env
# Edit .env with your configuration (see Environment Variables section)

# Database setup
alembic upgrade head
python database/init_db.py

# Start backend server
# WITH DOPPLER (Recommended):
doppler run -- python main.py    # All secrets auto-injected

# WITHOUT DOPPLER (Local dev):
python main.py  # Runs on http://localhost:8000
```

### 2. Setup Frontend

```bash
# Navigate to frontend
cd frontend

# Install dependencies
pnpm install

# Environment setup
cp .env.local.template .env.local
# Edit .env.local (see Frontend Environment section)

# Start development server
pnpm dev  # Runs on http://localhost:3000
```

### 3. Verify Setup

- Backend API: http://localhost:8000/docs
- Frontend App: http://localhost:3000
- Health Check: http://localhost:8000/health

## Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/ruleiq

# Redis
REDIS_URL=redis://localhost:6379

# AI Services
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key  # Optional

# Authentication
JWT_SECRET_KEY=your_super_secret_jwt_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Application
DEBUG=true
ENVIRONMENT=development
HOST=0.0.0.0
PORT=8000
```

### Frontend (.env.local)

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Theme Configuration (for teal migration testing)
NEXT_PUBLIC_USE_NEW_THEME=false

# Analytics (optional)
NEXT_PUBLIC_GA_ID=your_google_analytics_id
```

## Database Setup

### Local PostgreSQL

```bash
# Install PostgreSQL (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql
CREATE DATABASE ruleiq;
CREATE USER ruleiq_user WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ruleiq TO ruleiq_user;
\q
```

### Using Docker

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Check containers
docker-compose ps
```

## Development Workflow

### 1. Code Quality Checks

**Backend:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Linting and formatting
ruff check .
ruff format .

# Type checking (if using mypy)
mypy .

# Run tests
pytest
```

**Frontend:**
```bash
cd frontend

# Type checking
pnpm typecheck

# Linting
pnpm lint

# Format code
pnpm format

# Run tests
pnpm test
```

### 2. Database Operations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Reset database (development only)
alembic downgrade base
alembic upgrade head
python database/init_db.py
```

### 3. Running Services

**Development Mode:**
```bash
# Terminal 1: Backend
source .venv/bin/activate
python main.py

# Terminal 2: Frontend
cd frontend
pnpm dev

# Terminal 3: Background workers (if needed)
celery -A celery_app worker --loglevel=info
```

**Production Mode:**
```bash
# Build frontend
cd frontend
pnpm build

# Start backend with production settings
ENVIRONMENT=production python main.py
```

## Testing

### Backend Tests

```bash
# Quick unit tests (2-5 minutes)
make test-fast

# Integration tests
make test-integration

# Full test suite
make test-full

# Specific test file
pytest tests/test_assessments.py -v

# With coverage
pytest --cov=. --cov-report=html
```

### Frontend Tests

```bash
cd frontend

# Unit tests
pnpm test

# Watch mode
pnpm test:watch

# E2E tests
pnpm test:e2e

# Visual regression tests (if configured)
pnpm test:visual

# Coverage report
pnpm test:coverage
```

## Docker Development

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild services
docker-compose build
docker-compose up -d
```

### Individual Services

```bash
# Database only
docker-compose up -d postgres

# Redis only
docker-compose up -d redis

# Full stack
docker-compose up -d
```

## Troubleshooting

### Common Issues

**Database Connection Errors:**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Restart PostgreSQL
sudo systemctl restart postgresql

# Check connection manually
psql -U ruleiq_user -d ruleiq -h localhost
```

**Frontend Build Errors:**
```bash
# Clear Next.js cache
cd frontend
rm -rf .next

# Reinstall dependencies
rm -rf node_modules
pnpm install

# Check for TypeScript errors
pnpm typecheck
```

**Python Import Errors:**
```bash
# Verify virtual environment
which python
pip list

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Port Conflicts:**
```bash
# Check what's using port 8000
lsof -i :8000

# Kill process on port 8000
kill -9 $(lsof -t -i:8000)
```

### Getting Help

1. **Check logs**: Always check terminal output for error details
2. **Health endpoints**: Use `/health` and `/api/monitoring/health`
3. **Documentation**: Review relevant docs in `/docs/`
4. **Git issues**: Check repository issues and discussions

## IDE Configuration

### VS Code Extensions

- Python
- Pylance
- Black Formatter
- ES7+ React/Redux/React-Native snippets
- Tailwind CSS IntelliSense
- TypeScript and JavaScript Language Features

### PyCharm/IntelliJ

- Enable Python plugin
- Configure interpreter to use virtual environment
- Set up code formatting with Black
- Configure pytest as test runner

## Performance Tips

1. **Database**: Use connection pooling (already configured)
2. **Frontend**: Enable Next.js optimizations
3. **Development**: Use pnpm instead of npm for faster installs
4. **Testing**: Run tests in parallel when possible
5. **Docker**: Use volume mounts for faster development cycles

## Security Notes

- Never commit `.env` files or secrets
- Use environment variables for all configuration
- Keep dependencies updated
- Follow secure coding practices
- Regularly review security documentation

---

*Next: See [Architecture Overview](architecture.md) for system design details.*