#!/usr/bin/env python3
"""
Load the Golden Compliance Dataset into Neo4j AuraDB
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.compliance_graph_initializer import ComplianceGraphInitializer
from services.neo4j_service import Neo4jGraphRAGService
from neo4j import GraphDatabase


async def check_connection():
    """Check if Neo4j is accessible before loading data."""
    uri = os.getenv('NEO4J_URI')
    username = os.getenv('NEO4J_USERNAME')
    password = os.getenv('NEO4J_PASSWORD')

    print(f"🔍 Checking connection to: {uri}")

    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        with driver.session() as session:
            result = session.run('RETURN 1 as test')
            if result.single()['test'] == 1:
                # Get current stats
                node_count = session.run('MATCH (n) RETURN count(n) as count').single()['count']
                rel_count = session.run('MATCH ()-[r]->() RETURN count(r) as count').single()['count']

                print("✅ Connected successfully!")
                print("📊 Current database state:")
                print(f"   Nodes: {node_count:,}")
                print(f"   Relationships: {rel_count:,}")

                driver.close()
                return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


async def load_golden_dataset():
    """Load the golden compliance dataset into Neo4j."""

    print("\n📚 Loading Golden Compliance Dataset")
    print("=" * 50)

    neo4j_service = Neo4jGraphRAGService()
    initializer = ComplianceGraphInitializer(neo4j_service)

    try:
        # Initialize Neo4j connection
        print("\n1️⃣ Initializing Neo4j service...")
        await neo4j_service.initialize()
        print("   ✅ Service initialized")

        # Load the compliance graph
        print("\n2️⃣ Loading compliance data...")
        print("   This includes:")
        print("   • Compliance Domains (AML, Data Protection, etc.)")
        print("   • Jurisdictions (UK, EU, US, etc.)")
        print("   • Regulations (GDPR, 6AMLD, DORA, BSA, etc.)")
        print("   • Requirements, Controls, and Metrics")
        print("   • Risk Assessments and Relationships")
        print("")

        result = await initializer.initialize_full_compliance_graph()

        print("\n✅ Data loading complete!")
        print("\n📊 Loading Summary:")
        for key, value in result.items():
            if isinstance(value, dict):
                print(f"\n   {key}:")
                for sub_key, sub_value in value.items():
                    print(f"      {sub_key}: {sub_value}")
            else:
                print(f"   {key}: {value}")

        # Get final stats
        stats = await neo4j_service.get_graph_statistics()
        print("\n📈 Final Database Statistics:")
        print(f"   Total Nodes: {stats.get('total_nodes', 0):,}")
        print(f"   Total Relationships: {stats.get('total_relationships', 0):,}")
        print(f"   Node Labels: {', '.join(stats.get('node_labels', [])[:5])}...")
        print(f"   Relationship Types: {', '.join(stats.get('relationship_types', [])[:5])}...")

        return True

    except Exception as e:
        print(f"\n❌ Error loading data: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await neo4j_service.close()
        print("\n🔒 Neo4j connection closed")


async def main():
    """Main function to coordinate the data loading."""

    print("🚀 Neo4j AuraDB Golden Dataset Loader")
    print("=" * 50)

    # Check connection first
    if not await check_connection():
        print("\n⚠️  Cannot connect to Neo4j AuraDB")
        print("   Please ensure:")
        print("   1. The instance is fully provisioned")
        print("   2. Doppler has the correct credentials")
        print("   3. Run: doppler run -- python scripts/load-golden-dataset.py")
        sys.exit(1)

    # Confirm before loading
    print("\n⚠️  This will load the compliance golden dataset into Neo4j")
    response = input("Continue? (yes/no): ")

    if response.lower() != 'yes':
        print("❌ Aborted")
        sys.exit(0)

    # Load the data
    success = await load_golden_dataset()

    if success:
        print("\n🎉 Success! The golden compliance dataset is now loaded in Neo4j AuraDB")
        print("\n📝 Next steps:")
        print("   1. View the data at: https://console.neo4j.io")
        print("   2. Run your application: doppler run -- uvicorn api.main:app --host 0.0.0.0 --port 8000")
        print("   3. The IQ Agent can now use this compliance knowledge graph")
    else:
        print("\n❌ Data loading failed. Please check the error messages above.")
        sys.exit(1)


if __name__ == '__main__':
    # Run with Doppler: doppler run -- python scripts/load-golden-dataset.py
    asyncio.run(main())
