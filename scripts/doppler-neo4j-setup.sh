#!/bin/bash
# Doppler Neo4j AuraDB Setup Script

echo "🔐 Doppler Neo4j AuraDB Configuration"
echo "======================================"
echo ""

# Check if Doppler CLI is installed
if ! command -v doppler &> /dev/null; then
    echo "❌ Doppler CLI not found. Please install it first:"
    echo "   curl -Ls --tlsv1.2 --proto \"=https\" --retry 3 https://cli.doppler.com/install.sh | sudo sh"
    exit 1
fi

echo "✅ Doppler CLI found"
echo ""

# Check if logged in
if ! doppler configure get token &> /dev/null; then
    echo "⚠️  Not logged into Doppler. Please run: doppler login"
    exit 1
fi

echo "📋 Current Neo4j configuration in Doppler:"
echo ""
doppler secrets get NEO4J_URI NEO4J_USERNAME NEO4J_DATABASE 2>/dev/null || echo "No secrets found"
echo ""

# Prompt for password
echo "🔑 Enter your AuraDB password (will not be displayed):"
read -s AURADB_PASSWORD
echo ""

if [ -z "$AURADB_PASSWORD" ]; then
    echo "❌ Password cannot be empty"
    exit 1
fi

echo "📝 Updating Doppler secrets..."
echo ""

# Update secrets
doppler secrets set NEO4J_URI="neo4j+s://12e71bc4.databases.neo4j.io" --silent
doppler secrets set NEO4J_USERNAME="neo4j" --silent
doppler secrets set NEO4J_PASSWORD="$AURADB_PASSWORD" --silent
doppler secrets set NEO4J_DATABASE="neo4j" --silent

echo "✅ Doppler secrets updated"
echo ""

# Test connection
echo "🔍 Testing AuraDB connection via Doppler..."
echo ""

doppler run -- python3 -c "
import os
import sys
from neo4j import GraphDatabase

uri = os.getenv('NEO4J_URI')
username = os.getenv('NEO4J_USERNAME')
password = os.getenv('NEO4J_PASSWORD')
database = os.getenv('NEO4J_DATABASE')

print(f'URI: {uri}')
print(f'Username: {username}')
print(f'Database: {database}')
print('')

try:
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session(database=database) as session:
        result = session.run('RETURN 1 as test')
        if result.single()['test'] == 1:
            print('✅ Successfully connected to AuraDB!')
            
            # Get node and relationship count
            node_count = session.run('MATCH (n) RETURN count(n) as count').single()['count']
            rel_count = session.run('MATCH ()-[r]->() RETURN count(r) as count').single()['count']
            
            print(f'   Nodes: {node_count}')
            print(f'   Relationships: {rel_count}')
            
    driver.close()
except Exception as e:
    print(f'❌ Connection failed: {e}')
    print('')
    print('Please check:')
    print('  1. Your AuraDB password is correct')
    print('  2. The AuraDB instance is active (not paused)')
    print('  3. Network connectivity to neo4j.io')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Setup complete! Your application is now configured to use AuraDB via Doppler."
    echo ""
    echo "📌 To run your application with Doppler:"
    echo "   doppler run -- uvicorn api.main:app --host 0.0.0.0 --port 8000"
    echo ""
    echo "📌 To verify configuration:"
    echo "   doppler secrets get NEO4J_URI NEO4J_USERNAME NEO4J_DATABASE"
else
    echo ""
    echo "⚠️  Setup completed but connection test failed."
fi