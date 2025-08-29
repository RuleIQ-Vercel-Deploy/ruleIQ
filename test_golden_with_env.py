#!/usr/bin/env python3
"""Test golden dataset ingestion with proper environment setup."""

import os
import sys

# Set environment variables FIRST, before ANY imports
os.environ['NEO4J_URI'] = 'bolt://localhost:7688'
os.environ['NEO4J_USER'] = 'neo4j'
os.environ['NEO4J_PASSWORD'] = 'ruleiq123'

# Now do imports
import json
from pathlib import Path

# Clear any cached modules
modules_to_clear = [
    'services.ai.evaluation.infrastructure.neo4j_setup',
    'services.ai.evaluation.tools.ingestion',
]
for module in modules_to_clear:
    if module in sys.modules:
        del sys.modules[module]

# Now import fresh
from services.ai.evaluation.tools.ingestion import GoldenDatasetIngestion
from services.ai.evaluation.infrastructure.neo4j_setup import Neo4jConnection

def main():
    """Test golden dataset ingestion."""
    
    # First test the connection directly
    print("🔌 Testing Neo4j connection...")
    conn = Neo4jConnection()
    
    # Force clear singleton state
    Neo4jConnection._instance = None
    Neo4jConnection._driver = None
    
    # Create fresh instance
    conn = Neo4jConnection()
    print(f"  URI: {conn.uri}")
    print(f"  User: {conn.user}")
    print(f"  Password: {conn.password}")
    
    sample_file = Path("services/ai/evaluation/data/sample_golden_dataset.json")
    if not sample_file.exists():
        print(f"❌ Sample file not found: {sample_file}")
        return 1
    
    print("📚 Loading sample golden dataset...")
    with open(sample_file, 'r') as f:
        data = json.load(f)
    
    print(f"✅ Loaded {len(data['documents'])} documents")
    
    print("🔧 Initializing ingestion pipeline...")
    ingestion = GoldenDatasetIngestion()
    
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
    
    print("\n✅ Golden dataset ingestion test completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
