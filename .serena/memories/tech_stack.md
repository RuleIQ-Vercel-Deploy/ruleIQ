# ruleIQ Technology Stack

## Backend Stack
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy 2.0+ (async)
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

## Database & ORM
- **Database**: PostgreSQL 14+
- **ORM**: SQLAlchemy 2.0+ with async support
- **Migrations**: Alembic
- **Connection**: psycopg2-binary for PostgreSQL driver

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