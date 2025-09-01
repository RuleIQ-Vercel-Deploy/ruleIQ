#!/usr/bin/env python3
"""Test document ingestion directly."""

import sys
import os
from neo4j import GraphDatabase

# Force correct Neo4j settings
os.environ['NEO4J_URI'] = 'bolt://localhost:7688'
os.environ['NEO4J_PASSWORD'] = 'ruleiq123'

# Now import after setting env vars
from services.ai.evaluation.tools.ingest_docs import ManifestProcessor, GoldenDatasetBuilder

def test_connection():
    """Test Neo4j connection."""
    driver = GraphDatabase.driver('bolt://localhost:7688', auth=('neo4j', 'ruleiq123'))
    try:
        with driver.session() as session:
            result = session.run("RETURN 1 as num")
            print(f"Neo4j connection test: {result.single()['num']} - SUCCESS")
    except Exception as e:
        print(f"Neo4j connection failed: {e}")
    finally:
        driver.close()

def ingest_documents():
    """Ingest priority documents."""
    # Load manifest
    processor = ManifestProcessor('/home/omar/Documents/ruleIQ/data/manifests/compliance_ml_manifest.json')
    docs = processor.get_priority_documents(5)
    
    # Find accessible documents
    accessible_docs = []
    for doc in docs:
        if 'govinfo.gov' in doc.get('url', '') and doc['url'].endswith('.pdf'):
            accessible_docs.append(doc)
    
    print(f"Found {len(accessible_docs)} accessible PDF documents")
    
    # Process first accessible document
    if accessible_docs:
        builder = GoldenDatasetBuilder()
        
        # Manually fix the Neo4j connection
        from services.ai.evaluation.infrastructure.neo4j_setup import Neo4jConnection
        conn = builder.graph_ingestion.connection
        conn.uri = 'bolt://localhost:7688'
        conn.password = 'ruleiq123'
        
        doc = accessible_docs[0]
        print(f"\nProcessing: {doc['title']}")
        print(f"URL: {doc['url']}")
        
        golden_doc = builder.process_manifest_document(doc)
        if golden_doc:
            print(f"Document processed successfully!")
            print(f"Content length: {len(golden_doc.content)} chars")
            
            # Ingest into Neo4j
            result = builder.ingest_document(golden_doc)
            if result:
                print("✅ Successfully ingested into Neo4j!")
            else:
                print("❌ Failed to ingest into Neo4j")
        else:
            print("Failed to process document")

if __name__ == "__main__":
    print("Testing Neo4j connection...")
    test_connection()
    
    print("\nStarting document ingestion...")
    ingest_documents()