# Clean Setup Guide

This guide provides comprehensive instructions for setting up the RuleIQ compliance automation platform from scratch.

## Prerequisites

- **Python**: 3.11+ required
- **Node.js**: 20+ required
- **PostgreSQL**: 14+ required
- **Redis**: 6+ required (for caching)
- **Docker**: Latest version (optional, for containerized deployment)
- **Git**: 2.30+ required

### Required API Keys
- OpenAI API key (for GPT-4 integration)
- Neo4j AuraDB credentials (for knowledge graph)
- GitHub token (for PR management)
- Doppler token (for secrets management)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/ruleIQ.git
cd ruleIQ
```

### 2. Set Up Python Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set Up Frontend
```bash
cd frontend
pnpm install
cd ..
```

### 4. Database Setup
```bash
# Create PostgreSQL database
createdb ruleiq_dev

# Run migrations
alembic upgrade head

# Seed initial data (optional)
python scripts/seed_database.py
```

## Configuration

### 1. Environment Variables
Copy the example environment file and configure:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# API Keys
OPENAI_API_KEY=your_key_here
NEO4J_URI=neo4j+s://your-instance.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# Database
DATABASE_URL=postgresql://user:pass@localhost/ruleiq_dev

# Redis
REDIS_URL=redis://localhost:6379

# GitHub (for PR management)
GITHUB_TOKEN=ghp_your_token_here
```

### 2. Doppler Setup (Recommended)
```bash
# Install Doppler CLI
curl -Ls --tlsv1.2 --proto "=https" --retry 3 https://cli.doppler.com/install.sh | sudo sh

# Authenticate
doppler login

# Setup project
doppler setup
```

## Development Workflow

### 1. Start Services
Use the convenience script:
```bash
./start.sh
```

Or start services manually:
```bash
# Backend API
uvicorn api.main:app --reload --port 8000

# Frontend (in another terminal)
cd frontend && pnpm dev

# Workers (in another terminal)
celery -A api.workers worker --loglevel=info
```

### 2. Code Quality Checks
```bash
# Python linting and formatting
ruff check .
ruff format .

# TypeScript linting
cd frontend && pnpm lint

# Type checking
mypy api/
cd frontend && pnpm typecheck
```

### 3. Pre-commit Hooks
Install pre-commit hooks:
```bash
pre-commit install
```

## Testing

### Backend Tests
```bash
# Run all tests
pytest

# With coverage
pytest --cov=api --cov-report=html

# Specific test file
pytest tests/test_compliance.py

# Integration tests only
pytest -m integration
```

### Frontend Tests
```bash
cd frontend
pnpm test
pnpm test:e2e  # End-to-end tests
```

### SonarCloud Analysis
```bash
# Run local analysis
doppler run -- sonar-scanner
```

## Deployment

### Local Docker Deployment
```bash
docker-compose up -d
```

### Vercel Deployment (Frontend)
```bash
cd frontend
vercel --prod
```

### Cloud Run Deployment (Backend)
```bash
# Build and push container
gcloud builds submit --tag gcr.io/PROJECT_ID/ruleiq-api

# Deploy to Cloud Run
gcloud run deploy ruleiq-api \
  --image gcr.io/PROJECT_ID/ruleiq-api \
  --platform managed \
  --region us-central1
```

## PR Management Usage

The repository includes automated PR management tools:

### Analyze Open PRs
```bash
python scripts/pr_management/analyze_open_prs.py
```

### Clean Up PRs (Auto-merge/Close)
```bash
python scripts/pr_management/pr_cleanup_orchestrator.py
```

### Review Feature PR
```bash
python scripts/pr_management/feature_pr_reviewer.py PR_NUMBER
```

Reports are generated in `scripts/pr_management/reports/`.

## Important References

- **Architecture Overview**: See `.serena/memories/ALWAYS_READ_FIRST.md` for critical system architecture
- **API Documentation**: `api/README.md`
- **Frontend Documentation**: `frontend/README.md`
- **Database Schema**: `api/models/README.md`
- **CI/CD Pipeline**: `.github/workflows/README.md`

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Ensure PostgreSQL is running: `pg_ctl status`
   - Check DATABASE_URL in `.env`
   - Verify database exists: `psql -l`

2. **Redis Connection Failed**
   - Start Redis: `redis-server`
   - Check REDIS_URL in `.env`

3. **Frontend Build Errors**
   - Clear cache: `pnpm clean`
   - Reinstall deps: `rm -rf node_modules && pnpm install`

4. **API Type Errors**
   - Regenerate types: `pnpm generate:types`
   - Run type check: `mypy api/`

## Support

- **Issues**: Report at [GitHub Issues](https://github.com/your-org/ruleIQ/issues)
- **Documentation**: Check `.serena/memories/` for detailed guides
- **Slack**: Join #ruleiq-dev channel

## Next Steps

1. Read the architecture guide: `.serena/memories/ALWAYS_READ_FIRST.md`
2. Explore the codebase structure in `README.md`
3. Set up your IDE with recommended extensions
4. Run the test suite to verify setup
5. Create a feature branch and start developing!