# Doppler Neo4j Migration to AuraDB

## Required Doppler Secret Updates

Update the following secrets in your Doppler project:

### 1. Via Doppler CLI
```bash
# Update Neo4j URI to AuraDB
doppler secrets set NEO4J_URI "neo4j+s://12e71bc4.databases.neo4j.io"

# Username remains the same
doppler secrets set NEO4J_USERNAME "neo4j"

# Set your AuraDB password
doppler secrets set NEO4J_PASSWORD "<your-auradb-password>"

# Database name remains the same
doppler secrets set NEO4J_DATABASE "neo4j"
```

### 2. Via Doppler Dashboard
Navigate to your Doppler project and update:

| Secret Key | Old Value | New Value |
|------------|-----------|-----------|
| `NEO4J_URI` | `bolt://localhost:7688` | `neo4j+s://12e71bc4.databases.neo4j.io` |
| `NEO4J_USERNAME` | `neo4j` | `neo4j` |
| `NEO4J_PASSWORD` | `ruleiq123` | `<your-auradb-password>` |
| `NEO4J_DATABASE` | `neo4j` | `neo4j` |

## Verify Configuration

### Check current values:
```bash
doppler secrets get NEO4J_URI NEO4J_USERNAME NEO4J_DATABASE
```

### Test connection with Doppler:
```bash
doppler run -- python3 -c "
from neo4j import GraphDatabase
import os

uri = os.getenv('NEO4J_URI')
username = os.getenv('NEO4J_USERNAME')
password = os.getenv('NEO4J_PASSWORD')

print(f'Connecting to: {uri}')
driver = GraphDatabase.driver(uri, auth=(username, password))
with driver.session() as session:
    result = session.run('RETURN 1 as test')
    if result.single()['test'] == 1:
        print('✅ Successfully connected to AuraDB via Doppler!')
driver.close()
"
```

## Update Doppler Config in Code

The `app/core/doppler_config.py` file has been updated to use the new default:
- Changed default from `bolt://localhost:7687` to `neo4j+s://12e71bc4.databases.neo4j.io`

## Deployment Environments

Update these secrets for each Doppler environment:
- Development
- Staging  
- Production

### Set for specific environment:
```bash
# For staging
doppler secrets set NEO4J_URI "neo4j+s://12e71bc4.databases.neo4j.io" --config stg

# For production
doppler secrets set NEO4J_URI "neo4j+s://12e71bc4.databases.neo4j.io" --config prd
```

## Important Notes

1. **Protocol Change**: Use `neo4j+s://` (with SSL) instead of `bolt://`
2. **No Port Required**: AuraDB handles port management
3. **Password Security**: Never commit the AuraDB password to git
4. **Restart Services**: After updating Doppler secrets, restart your services:
   ```bash
   doppler run -- python main.py
   ```

## Rollback (if needed)

To rollback to Docker Neo4j:
```bash
doppler secrets set NEO4J_URI "bolt://localhost:7688"
doppler secrets set NEO4J_PASSWORD "ruleiq123"
```