#!/bin/bash
# Test Neo4j AuraDB Connection Script

echo "🔍 Testing Neo4j AuraDB Connection"
echo "==================================="
echo ""

# Check DNS resolution first
echo "1️⃣ Checking DNS resolution..."
INSTANCE_HOST="dd951128.databases.neo4j.io"

if host $INSTANCE_HOST > /dev/null 2>&1 || nslookup $INSTANCE_HOST > /dev/null 2>&1; then
    echo "✅ DNS resolved successfully"
else
    echo "❌ DNS not resolving yet"
    echo "   Instance may still be provisioning"
    echo "   Try again in a few minutes or check https://console.neo4j.io"
    exit 1
fi

echo ""
echo "2️⃣ Testing Neo4j connection..."

doppler run -- python3 -c "
from neo4j import GraphDatabase
import os
import sys

uri = os.getenv('NEO4J_URI')
username = os.getenv('NEO4J_USERNAME')
password = os.getenv('NEO4J_PASSWORD')

print(f'URI: {uri}')
print(f'Instance: {os.getenv(\"AURA_INSTANCENAME\")} ({os.getenv(\"AURA_INSTANCEID\")})')
print('')

try:
    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:
        result = session.run('RETURN 1 as test')
        if result.single()['test'] == 1:
            print('✅ Connection successful!')
            
            # Get database stats
            node_count = session.run('MATCH (n) RETURN count(n) as count').single()['count']
            rel_count = session.run('MATCH ()-[r]->() RETURN count(r) as count').single()['count']
            
            print(f'\\n📊 Database Statistics:')
            print(f'   Nodes: {node_count:,}')
            print(f'   Relationships: {rel_count:,}')
            
            # Get version
            version = session.run('CALL dbms.components() YIELD name, versions RETURN versions[0] as version').single()
            print(f'   Neo4j Version: {version[\"version\"]}')
            
    driver.close()
    print('\\n✅ Neo4j AuraDB is ready to use!')
    sys.exit(0)
    
except Exception as e:
    print(f'❌ Connection failed: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Success! Your RuleIQ application can now connect to Neo4j AuraDB"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Run your application: doppler run -- uvicorn api.main:app --host 0.0.0.0 --port 8000"
    echo "   2. The database is currently empty - ready for data"
    echo "   3. Monitor at: https://console.neo4j.io"
else
    echo ""
    echo "⚠️  Connection test failed"
    echo "   Check the instance status at https://console.neo4j.io"
fi