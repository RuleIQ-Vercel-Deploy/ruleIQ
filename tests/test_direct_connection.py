#!/usr/bin/env python3
"""Test Neo4j connection directly without singleton issues."""

import os
from neo4j import GraphDatabase

# Set environment variables
os.environ["NEO4J_URI"] = "bolt://localhost:7688"
os.environ["NEO4J_USER"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "ruleiq123"

print("Testing direct Neo4j connection...")
print(f"URI: {os.environ['NEO4J_URI']}")
print(f"User: {os.environ['NEO4J_USER']}")

try:
    driver = GraphDatabase.driver(
        os.environ["NEO4J_URI"],
        auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]),
    )

    with driver.session() as session:
        # Test basic connection
        result = session.run("RETURN 1 as test")
        print(f"✅ Connection successful: {result.single()['test']}")

        # Create a test document
        create_query = """
        CREATE (d:GoldenDocument {
            doc_id: 'test_doc',
            content: 'Test content',
            created_at: datetime()
        })
        RETURN d.doc_id as id
        """

        result = session.run(create_query)
        doc_id = result.single()["id"]
        print(f"✅ Created test document: {doc_id}")

        # Count documents
        count_result = session.run("MATCH (d:GoldenDocument) RETURN count(d) as count")
        count = count_result.single()["count"]
        print(f"✅ Total golden documents: {count}")

        # Clean up
        session.run("MATCH (d:GoldenDocument {doc_id: 'test_doc'}) DELETE d")
        print("✅ Cleaned up test document")

    driver.close()
    print("✅ All tests passed!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback

    traceback.print_exc()
