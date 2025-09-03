# Neon Database Setup for ruleIQ

## Why Neon?

To avoid confusion with multiple database instances, ruleIQ uses **Neon** as the primary PostgreSQL database for all environments. Neon provides:
- Serverless PostgreSQL with autoscaling
- Built-in connection pooling
- Automatic backups and branching
- SSL connections by default

## Setup Instructions

### 1. Get Your Neon Database URL

1. Sign up at [console.neon.tech](https://console.neon.tech)
2. Create a new project
3. Copy your connection string (it will look like):
   ```
   postgresql://user:password@host.neon.tech/database?sslmode=require
   ```

### 2. Configure Environment Variables

Create a `.env` file in the project root with your Neon database URL:

```bash
# Neon Database (REQUIRED - no local PostgreSQL needed!)
DATABASE_URL=postgresql://your-neon-connection-string

# Redis (still needed for caching and Celery)
REDIS_URL=redis://localhost:6379/0

# AI Services
GOOGLE_API_KEY=your-google-api-key

# Other required variables
JWT_SECRET_KEY=your-jwt-secret-key
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 3. Use the Neon Docker Compose File

Instead of the default `docker-compose.yml` (which includes local PostgreSQL), use:

```bash
# Stop any existing containers
docker compose down

# Start services with Neon configuration
docker compose -f docker-compose.neon.yml up -d
```

This will start:
- **app**: FastAPI application (port 8000)
- **redis**: Redis for caching and Celery (port 6379)
- **celery_worker**: Background task processor
- **celery_beat**: Scheduled task runner

**NO local PostgreSQL container** - all database connections go to Neon!

### 4. Initialize the Database

```bash
# Activate virtual environment
source .venv/bin/activate

# Run database initialization
python database/init_db.py
```

### 5. Verify the Setup

```bash
# Check API health
curl http://localhost:8000/health

# Check database connection
curl http://localhost:8000/api/v1/ai/health
```

## Important Notes

1. **No Local PostgreSQL**: The `docker-compose.neon.yml` file does NOT include a PostgreSQL container
2. **SSL Required**: Neon requires SSL connections (already configured in the connection string)
3. **Connection Pooling**: Neon provides built-in connection pooling, but the app also has its own pooling configured
4. **Development vs Production**: Use the same Neon database or create separate Neon projects for different environments

## Troubleshooting

### "Database engine not properly initialized"
- Check your DATABASE_URL is correctly set in `.env`
- Ensure the Neon database is accessible
- Run `python database/init_db.py` to initialize tables

### Connection timeouts
- Neon databases may sleep after inactivity
- First request after sleep may be slower
- Consider using Neon's "Always On" feature for production

### SSL errors
- Ensure your DATABASE_URL includes `?sslmode=require`
- The app automatically handles SSL configuration for Neon

## Migration from Local PostgreSQL

If you have data in a local PostgreSQL instance:

1. Export data: `pg_dump -h localhost -p 5433 -U postgres compliancegpt > backup.sql`
2. Import to Neon using their web console or CLI
3. Update all `.env` files to use the Neon DATABASE_URL
4. Remove the `db:` service from docker-compose.yml