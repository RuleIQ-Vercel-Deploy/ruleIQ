#!/bin/bash
# Migration script from Docker Neo4j to AuraDB

echo "🔄 Migrating from Docker Neo4j to AuraDB..."
echo "==========================================="

# Step 1: Check if Docker Neo4j is running
if docker ps | grep -q "ruleiq-neo4j"; then
    echo "⚠️  Docker Neo4j container is running. Stopping..."
    docker stop ruleiq-neo4j
    echo "✅ Docker Neo4j container stopped"
else
    echo "✅ Docker Neo4j container is not running"
fi

# Step 2: Backup environment if it exists
if [ -f ".env" ]; then
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ Backed up existing .env file"
fi

# Step 3: Update environment variables
echo ""
echo "📝 Please update your .env file with the following Neo4j configuration:"
echo ""
echo "NEO4J_URI=neo4j+s://12e71bc4.databases.neo4j.io"
echo "NEO4J_USERNAME=neo4j"
echo "NEO4J_PASSWORD=<your-auradb-password>"
echo "NEO4J_DATABASE=neo4j"
echo ""

# Step 4: Test connection
echo "🔍 Testing AuraDB connection..."
python3 -c "
import os
from neo4j import GraphDatabase
import sys

uri = os.getenv('NEO4J_URI', 'neo4j+s://12e71bc4.databases.neo4j.io')
username = os.getenv('NEO4J_USERNAME', 'neo4j')
password = os.getenv('NEO4J_PASSWORD')

if not password:
    print('❌ NEO4J_PASSWORD not set in environment')
    sys.exit(1)

try:
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:
        result = session.run('RETURN 1 as test')
        if result.single()['test'] == 1:
            print('✅ Successfully connected to AuraDB!')
            
            # Get database info
            result = session.run('CALL dbms.components() YIELD name, versions, edition')
            for record in result:
                print(f'   Database: {record[\"name\"]} {record[\"versions\"][0]} ({record[\"edition\"]})')
    driver.close()
except Exception as e:
    print(f'❌ Connection failed: {e}')
    sys.exit(1)
" 2>/dev/null

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Migration complete! Your application is now using AuraDB."
    echo ""
    echo "📌 Important notes:"
    echo "   - The Docker Neo4j container has been stopped"
    echo "   - docker-compose.neo4j.yml has been archived"
    echo "   - Your data needs to be migrated separately if needed"
    echo "   - AuraDB Free tier limits: 200k nodes, 400k relationships"
else
    echo ""
    echo "⚠️  Connection test failed. Please check:"
    echo "   1. Your NEO4J_PASSWORD is set correctly"
    echo "   2. The AuraDB instance is running"
    echo "   3. Network connectivity to neo4j.io"
fi