#!/usr/bin/env python3
"""
Basic Neo4j connection and ingestion test.
"""

import asyncio
import os
from neo4j import AsyncGraphDatabase
from dotenv import load_dotenv

load_dotenv()


async def test_neo4j_connection():
    """Test basic Neo4j connection."""

    # Get credentials
    uri = "bolt://localhost:7688"  # Docker mapped port
    user = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "ruleiq123")

    print(f"Connecting to Neo4j at {uri}")
    print(f"User: {user}")

    # Test connection
    driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    try:
        async with driver.session() as session:
            # Test query
            result = await session.run("RETURN 'Connection successful!' as message")
            record = await result.single()
            print(f"✓ {record['message']}")

            # Create a test node
            create_result = await session.run(
                """
                CREATE (r:Regulation {
                    id: 'test-gdpr',
                    title: 'Test GDPR',
                    url: 'https://example.com',
                    risk_score: 8,
                    created_at: datetime()
                })
                RETURN r
            """,
            )

            test_record = await create_result.single()
            print(f"✓ Created test node: {test_record['r']['id']}")

            # Query the node
            query_result = await session.run(
                """
                MATCH (r:Regulation {id: 'test-gdpr'})
                RETURN r.title as title, r.risk_score as risk
            """,
            )

            query_record = await query_result.single()
            print(
                f"✓ Queried node: {query_record['title']} (risk: {query_record['risk']})",
            )

            # Clean up
            await session.run("MATCH (r:Regulation {id: 'test-gdpr'}) DELETE r")
            print("✓ Cleanup complete")

    finally:
        await driver.close()

    print("\n✅ Neo4j connection test passed!")


if __name__ == "__main__":
    asyncio.run(test_neo4j_connection())
