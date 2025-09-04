# Database Initialization Usage Guide

This guide explains how to use the new database initialization system in ruleIQ.

## Quick Start

### 1. Basic Database Initialization

```python
from database import init_db

# Initialize the database with error handling
success = init_db()
if success:
    print("Database initialized successfully")
else:
    print("Database initialization failed")
```

### 2. Using with FastAPI

The database is automatically initialized in the FastAPI lifespan context:

```python
from database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if not init_db():
        raise RuntimeError("Database initialization failed")

    yield

    # Shutdown (handled automatically)
```

### 3. Manual Database Connection Testing

```python
from database import test_database_connection, test_async_database_connection

# Test sync connection
if test_database_connection():
    print("Sync database connection OK")

# Test async connection
import asyncio
async def test_async():
    if await test_async_database_connection():
        print("Async database connection OK")

asyncio.run(test_async())
```

## Session Management

### Synchronous Sessions

```python
from database import get_db, get_db_context

# Using generator (for FastAPI dependencies)
def some_endpoint():
    db = next(get_db())
    try:
        # Use db session
        result = db.execute("SELECT 1")
    finally:
        db.close()

# Using context manager
with get_db_context() as db:
    # Use db session
    result = db.execute("SELECT 1")
```

### Asynchronous Sessions

```python
from database import get_async_db

async def some_async_function():
    async for db in get_async_db():
        # Use async db session
        result = await db.execute("SELECT 1")
```

## Configuration

### Environment Variables

The database configuration uses these environment variables:

- `DATABASE_URL`: Required. PostgreSQL connection string
- `SQLALCHEMY_ECHO`: Optional. Set to "true" for SQL query logging
- `DB_POOL_SIZE`: Optional. Connection pool size (default: 10)
- `DB_MAX_OVERFLOW`: Optional. Maximum overflow connections (default: 20)
- `DB_POOL_RECYCLE`: Optional. Connection recycle time in seconds (default: 1800)
- `DB_POOL_TIMEOUT`: Optional. Connection timeout in seconds (default: 30)

### Example .env file

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/ruleiq
SQLALCHEMY_ECHO=false
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
```

## Advanced Usage

### Custom Configuration

```python
from database import DatabaseConfig

# Get configured URLs
original_url, sync_url, async_url = DatabaseConfig.get_database_urls()

# Get engine configuration
sync_kwargs = DatabaseConfig.get_engine_kwargs(is_async=False)
async_kwargs = DatabaseConfig.get_engine_kwargs(is_async=True)
```

### Engine Information

```python
from database import get_engine_info

# Get current engine status
info = get_engine_info()
print(f"Sync engine: {info['sync_engine_initialized']}")
print(f"Async engine: {info['async_engine_initialized']}")
```

### Cleanup

```python
from database import cleanup_db_connections

# Clean up all database connections
await cleanup_db_connections()
```

## Migration Support

The database initialization is compatible with Alembic migrations. After running migrations:

```python
from database import create_all_tables

# Create any missing tables (safe to run multiple times)
create_all_tables()
```

## Error Handling

All database initialization functions include comprehensive error handling:

- Automatic retry on connection failures
- Detailed logging with error messages
- Graceful degradation with informative error responses
- Proper resource cleanup on failures

## Testing

Run the test script to verify database initialization:

```bash
python test_db_init.py
```
