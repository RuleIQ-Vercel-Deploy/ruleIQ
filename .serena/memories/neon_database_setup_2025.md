# Neon Database Setup (January 2025)

## Current Database Configuration
ruleIQ now uses **Neon** as the ONLY database for all environments. No local PostgreSQL needed!

### Connection Details
- **Database URL**: Configured in `.env.local` 
- **Connection String**: `postgresql+asyncpg://neondb_owner:...@ep-sweet-truth-a89at3wo-pooler.eastus2.azure.neon.tech/neondb?sslmode=require`
- **SSL**: Required (already in connection string)

### Docker Setup
- **docker-compose.yml**: Updated to remove PostgreSQL container
- **Services**: Only Redis runs locally, all services connect to Neon
- **Environment**: All services use `.env.local` file

### Key Commands
```bash
# Start only Redis (Neon is cloud-based)
docker compose up -d redis

# Run the app
source .venv/bin/activate
python main.py

# Run tests
python -m pytest tests/
```

### Important Notes
1. **No Local PostgreSQL**: Removed from docker-compose.yml completely
2. **Single Database Source**: Neon for dev, staging, and production
3. **Environment Variables**: Everything uses `.env.local` (not .env)
4. **Test Database**: Also uses Neon (can create branches for testing)

### Benefits
- No database sync issues
- Production parity in development
- Built-in connection pooling
- Automatic backups
- SSL by default

### Verified Working
- ✅ Database connection tested successfully
- ✅ All services configured to use Neon
- ✅ No more confusion with multiple databases