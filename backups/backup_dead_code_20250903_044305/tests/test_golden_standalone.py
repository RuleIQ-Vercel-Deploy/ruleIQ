#!/usr/bin/env python3
"""Standalone test for golden dataset ingestion - bypasses import issues."""

import os
import sys

# Set environment variables FIRST
os.environ["NEO4J_URI"] = "bolt://localhost:7688"
os.environ["NEO4J_USER"] = "neo4j"
os.environ["NEO4J_PASSWORD"] = "ruleiq123"

# Add path but don't import anything that might override env vars
sys.path.insert(0, ".")


def test_direct_neo4j():
    """Test Neo4j connection directly without any problematic imports."""
    from neo4j import GraphDatabase

    print("🔌 Testing direct Neo4j connection...")
    print(f"  URI: {os.environ['NEO4J_URI']}")
    print(f"  User: {os.environ['NEO4J_USER']}")
    print(f"  Password: {os.environ['NEO4J_PASSWORD']}")

    try:
        driver = GraphDatabase.driver(
            os.environ["NEO4J_URI"],
            auth=(os.environ["NEO4J_USER"], os.environ["NEO4J_PASSWORD"]),
        )

        with driver.session() as session:
            # Test connection
            result = session.run("RETURN 1 as test")
            print(f"✅ Connection successful: {result.single()['test']}")

            # Create the VECTOR index if it doesn't exist
            print("\n📊 Creating VECTOR index for golden dataset...")
            try:
                session.run(
                    """
                    CREATE VECTOR INDEX golden_chunk_embeddings IF NOT EXISTS
                    FOR (c:GoldenChunk)
                    ON (c.embedding)
                    OPTIONS {
                        indexConfig: {
                            `vector.dimensions`: 384,
                            `vector.similarity_function`: 'cosine',
                        },
                    }
                """,
                )
                print("✅ VECTOR index created/verified")
            except Exception as e:
                print(f"⚠️ Index might already exist: {e}")

            # Ingest sample data directly
            print("\n📥 Ingesting sample golden dataset...")

            # Sample document 1
            result = session.run(
                """
                CREATE (d:GoldenDocument {
                    doc_id: 'gdpr_article_5',
                    content: 'GDPR Article 5: Principles relating to processing of personal data. Personal data shall be processed lawfully, fairly and in a transparent manner.',
                    source: 'GDPR',
                    created_at: datetime()
                })
                RETURN d.doc_id as id
            """,
            )
            print(f"✅ Created document: {result.single()['id']}")

            # Sample chunk with embedding
            import numpy as np

            embedding = np.random.rand(384).tolist()  # Mock embedding

            result = session.run(
                """
                MATCH (d:GoldenDocument {doc_id: 'gdpr_article_5'})
                CREATE (c:GoldenChunk {
                    chunk_id: 'gdpr_article_5_chunk_1',
                    content: 'Personal data shall be processed lawfully, fairly and in a transparent manner.',
                    embedding: $embedding,
                    created_at: datetime()
                })
                CREATE (d)-[:HAS_CHUNK]->(c)
                RETURN c.chunk_id as id
            """,
                embedding=embedding,
            )
            print(f"✅ Created chunk with embedding: {result.single()['id']}")

            # Verify ingestion
            count_result = session.run(
                """
                MATCH (d:GoldenDocument)
                RETURN count(d) as doc_count
            """,
            )
            doc_count = count_result.single()["doc_count"]

            chunk_result = session.run(
                """
                MATCH (c:GoldenChunk)
                RETURN count(c) as chunk_count
            """,
            )
            chunk_count = chunk_result.single()["chunk_count"]

            print(f"\n📊 Current golden dataset status:")
            print(f"  - Documents: {doc_count}")
            print(f"  - Chunks: {chunk_count}")

            # Test vector search
            print("\n🔍 Testing vector similarity search...")
            query_embedding = np.random.rand(384).tolist()

            result = session.run(
                """
                CALL db.index.vector.queryNodes(
                    'golden_chunk_embeddings',
                    3,
                    $query_embedding
                ) YIELD node, score
                RETURN node.chunk_id as chunk_id, score
                LIMIT 3
            """,
                query_embedding=query_embedding,
            )

            print("✅ Vector search results:")
            for record in result:
                print(f"  - {record['chunk_id']}: score={record['score']:.4f}")

            # Clean up test data
            print("\n🧹 Cleaning up test data...")
            session.run(
                "MATCH (d:GoldenDocument {doc_id: 'gdpr_article_5'}) DETACH DELETE d",
            )
            print("✅ Test data cleaned up")

        driver.close()
        print("\n✅ All tests passed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_direct_neo4j()
    sys.exit(0 if success else 1)
