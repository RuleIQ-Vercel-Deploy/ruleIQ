#!/usr/bin/env python3
"""Test script to verify golden dataset ingestion."""

import json
import sys
from pathlib import Path
from services.ai.evaluation.tools.ingestion import GoldenDatasetIngestion

def main():
    """Test golden dataset ingestion."""
    
    # Load sample data
    if len(sys.argv) > 1:
        sample_file = Path(sys.argv[1])
    else:
        sample_file = Path("services/ai/evaluation/data/sample_golden_dataset.json")
    if not sample_file.exists():
        print(f"❌ Sample file not found: {sample_file}")
        return 1
    
    print("📚 Loading sample golden dataset...")
    with open(sample_file, 'r') as f:
        data = json.load(f)
    
    print(f"✅ Loaded {len(data['documents'])} documents")
    
    # Initialize ingestion
    print("🔧 Initializing ingestion pipeline...")
    ingestion = GoldenDatasetIngestion()
    
    # Ingest the data
    print("📥 Ingesting data to Neo4j...")
    try:
        result = ingestion.ingest_from_file(str(sample_file))
        
        if result["success"]:
            print(f"✅ Ingestion successful!")
            print(f"   - Documents processed: {result['documents_processed']}")
            print(f"   - Chunks created: {result['chunks_created']}")
            if result.get("embeddings_generated"):
                print(f"   - Embeddings generated: {result['embeddings_generated']}")
        else:
            print(f"❌ Ingestion failed!")
            for error in result.get("errors", []):
                print(f"   - {error}")
            return 1
            
    except Exception as e:
        print(f"❌ Error during ingestion: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Verify data in Neo4j
    print("\n🔍 Verifying data in Neo4j...")
    try:
        from services.ai.evaluation.infrastructure.neo4j_setup import Neo4jConnection
        
        conn = Neo4jConnection()
        with conn.get_session() as session:
            # Count golden dataset nodes
            result = session.run("""
                MATCH (d:GoldenDocument)
                RETURN count(d) as doc_count
            """)
            doc_count = result.single()["doc_count"]
            
            result = session.run("""
                MATCH (c:GoldenChunk)
                RETURN count(c) as chunk_count
            """)
            chunk_count = result.single()["chunk_count"]
            
            result = session.run("""
                MATCH (c:GoldenChunk)
                WHERE c.embedding IS NOT NULL
                RETURN count(c) as embedding_count
            """)
            embedding_count = result.single()["embedding_count"]
            
            print(f"✅ Neo4j verification:")
            print(f"   - Golden documents: {doc_count}")
            print(f"   - Golden chunks: {chunk_count}")
            print(f"   - Chunks with embeddings: {embedding_count}")
            
            # Check main app data is separate
            result = session.run("""
                MATCH (n)
                WHERE NOT (n:GoldenDocument OR n:GoldenChunk)
                RETURN count(n) as other_count
            """)
            other_count = result.single()["other_count"]
            print(f"   - Other nodes (main app): {other_count}")
            
    except Exception as e:
        print(f"❌ Error verifying data: {e}")
        return 1
    
    print("\n✅ Golden dataset ingestion test completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())