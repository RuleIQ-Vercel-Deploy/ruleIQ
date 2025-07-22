# ruleIQ Technology Stack (Updated January 2025)

## Backend Stack
- **Framework**: FastAPI (Python 3.11+)
- **Database**: Neon PostgreSQL (cloud-based, SSL required)
- **ORM**: SQLAlchemy 2.0+ with async support
- **Authentication**: JWT with refresh tokens (python-jose)
- **Security**: bcrypt for password hashing, CORS middleware
- **AI Integration**: 
  - OpenAI GPT-4 (openai>=1.0.0)
  - Google Generative AI (google-generativeai>=0.8.0)
- **Task Queue**: Celery with Redis
- **HTTP Client**: aiohttp for async requests
- **Document Generation**: reportlab, python-docx
- **Cloud Integration**: boto3 (AWS), msal (Microsoft Graph)

## Development Tools
- **Code Quality**: 
  - Ruff (linting and formatting)
  - Black (code formatting)
  - isort (import sorting)
- **Testing**: 
  - pytest with asyncio support
  - pytest-xdist for parallel execution
  - httpx for HTTP testing
  - locust for load testing
- **Type Checking**: Pydantic 2.0+ for data validation
- **Environment**: python-dotenv for configuration

## Database & Infrastructure
- **Database**: Neon PostgreSQL (cloud-hosted, no local DB needed)
- **ORM**: SQLAlchemy 2.0+ with async support
- **Migrations**: Alembic
- **Redis**: Local Redis for caching and Celery (via Docker)
- **Connection**: asyncpg for async, psycopg2 for sync connections

## API & Web
- **Framework**: FastAPI with automatic OpenAPI docs
- **ASGI Server**: Uvicorn with standard extras
- **Middleware**: Custom error handling, CORS, security headers
- **Authentication**: JWT Bearer tokens
- **Validation**: Pydantic schemas with type hints

## External Integrations
- **AWS**: boto3 for cloud services integration
- **Microsoft**: msal for Graph API integration  
- **Google**: google-api-python-client for Google services
- **Enterprise**: cryptography for secure integrations

## Key Architecture Changes (2025)
- **Single Database**: Neon PostgreSQL for all environments
- **No Local DB**: Removed PostgreSQL from docker-compose.yml
- **Environment**: Uses .env.local consistently
- **Simplified Setup**: Only Redis runs locally via Docker