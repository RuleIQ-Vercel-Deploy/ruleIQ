# ruleIQ Database Configuration

This directory contains the database setup and models for the ruleIQ application.

## Setup Instructions

### 1. Environment Configuration

The database configuration uses environment variables for all settings. To set up your environment:

1. **Copy the environment template**:
   ```bash
   cp env.template .env.local
   ```

2. **Edit `.env.local`** with your database credentials:
   ```bash
   # Minimum required configuration
   DATABASE_URL=postgresql://username:password@localhost:5432/ruleiq
   ```

3. **Environment Loading Priority**:
   - `.env.local` - Local development (highest priority)
   - `.env` - Production configuration
   - System environment variables (fallback)

### 2. Database URLs

The system automatically derives appropriate database URLs for different contexts:

- **Original URL**: As specified in `DATABASE_URL`
- **Sync URL**: Automatically converted to use `psycopg2` driver
- **Async URL**: Automatically converted to use `asyncpg` driver

### 3. Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | Required | PostgreSQL connection string |
| `DB_POOL_SIZE` | 10 | Number of connections in pool |
| `DB_MAX_OVERFLOW` | 20 | Maximum overflow connections |
| `DB_POOL_RECYCLE` | 1800 | Connection recycle time (seconds) |
| `DB_POOL_TIMEOUT` | 30 | Connection timeout (seconds) |
| `SQLALCHEMY_ECHO` | false | Enable SQL query logging |

### 4. SSL Configuration

For production databases requiring SSL:
```bash
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
```

### 5. Database Initialization

The database engine and session makers are initialized lazily on first use. The system supports both synchronous and asynchronous operations.

### 6. Error Handling

The configuration includes comprehensive error handling:
- Validates required environment variables on startup
- Provides clear error messages for missing configuration
- Logs configuration source and connection details (without passwords)
- Handles invalid configuration values gracefully

### 7. Development vs Production

- **Development**: Use `.env.local` with local PostgreSQL
- **Production**: Use `.env` or system environment variables
- **Docker**: Environment variables are passed through docker-compose

### 8. Testing

For testing, use a separate database:
```bash
TEST_DATABASE_URL=postgresql://postgres:password@localhost:5432/ruleiq_test
```

## Files in this Directory

- `db_setup.py` - Core database configuration and connection management
- `models.py` - SQLAlchemy ORM models
- `repositories/` - Data access layer implementations
- `README.md` - This documentation file

## Troubleshooting

1. **"DATABASE_URL environment variable not set"**
   - Ensure you've created `.env.local` from the template
   - Check that the file contains `DATABASE_URL=...`

2. **Connection timeouts**
   - Verify PostgreSQL is running
   - Check firewall/network settings
   - Adjust `DB_POOL_TIMEOUT` if needed

3. **SSL errors**
   - Add `?sslmode=require` to DATABASE_URL for SSL
   - For local development, use `?sslmode=disable`

4. **Import errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility (3.11+)