# ruleIQ Code Style and Conventions

## Code Formatting
- **Formatter**: Ruff (primary) with Black as backup
- **Line Length**: 100 characters
- **Target Python Version**: 3.8+ (configured in ruff.toml)
- **Quote Style**: Double quotes
- **Indent Style**: 4 spaces (no tabs)

## Type Hints and Annotations
- **Type Annotations**: Required for all function parameters and return types
- **Pydantic**: Used for data validation and serialization
- **SQLAlchemy**: Modern async patterns with type hints
- **Exception**: Type annotations relaxed in test files

## Code Quality Tools
- **Ruff**: Primary linter with comprehensive rule set
  - Pyflakes (F) - Critical errors only
  - pycodestyle (E/W) - Style enforcement
  - Type annotations (ANN) - Required except in tests
  - Security (S) - Security-focused rules
  - pytest-specific (PT) - Test-specific rules
- **Import Organization**: isort with first-party packages defined
- **Security**: Mandatory security checks except in test files

## Testing Conventions
- **Framework**: pytest with asyncio support
- **Structure**: Tests mirror source code structure
- **Markers**: Comprehensive test categorization system
- **Fixtures**: Extensive use of pytest fixtures for setup
- **Async Testing**: Full async/await support with pytest-asyncio

## Database Patterns
- **ORM**: SQLAlchemy 2.0+ with async patterns
- **Models**: Individual model files in database/ directory
- **Migrations**: Alembic for database schema changes
- **Sessions**: Dependency injection for database sessions

## API Patterns
- **Routers**: FastAPI routers organized by domain
- **Schemas**: Pydantic models for request/response validation
- **Dependencies**: Dependency injection for auth, database, etc.
- **Error Handling**: Custom middleware for consistent error responses

## Security Standards
- **Authentication**: JWT tokens with refresh mechanism
- **Password Hashing**: bcrypt with appropriate rounds
- **Input Validation**: Pydantic schemas for all inputs
- **CORS**: Configured middleware for cross-origin requests
- **Security Headers**: Custom middleware for security headers

## File Organization
- **api/**: FastAPI routers, schemas, dependencies
- **database/**: SQLAlchemy models and database setup
- **services/**: Business logic and service layer
- **config/**: Configuration and settings
- **tests/**: Comprehensive test suite with markers
- **utils/**: Shared utilities and helpers