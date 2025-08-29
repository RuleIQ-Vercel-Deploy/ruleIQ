#!/usr/bin/env python3
"""Test the Golden Dataset Retrieval API."""

import os
import sys
import json
import time
import requests
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_health_check(base_url: str = "http://localhost:8001") -> bool:
    """Test the health check endpoint."""
    print("🏥 Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"  Status: {data['status']}")
            print(f"  Neo4j Connected: {data['neo4j_connected']}")
            print(f"  Embedding Model: {data['embedding_model']}")
            print(f"  Vector Index Ready: {data['vector_index_ready']}")
            return data['neo4j_connected']
        else:
            print(f"  ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Health check error: {e}")
        return False


def test_ingestion(base_url: str = "http://localhost:8001") -> bool:
    """Test the ingestion endpoint."""
    print("\n📥 Testing Data Ingestion...")
    
    # Use the sample dataset
    dataset_path = "services/ai/evaluation/data/sample_golden_dataset.json"
    
    if not os.path.exists(dataset_path):
        print(f"  ❌ Sample dataset not found at: {dataset_path}")
        return False
    
    try:
        response = requests.post(
            f"{base_url}/ingest",
            json={"file_path": dataset_path}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Success: {data['success']}")
            print(f"  Documents Processed: {data['documents_processed']}")
            print(f"  Chunks Created: {data['chunks_created']}")
            print(f"  Embeddings Generated: {data['embeddings_generated']}")
            if data.get('errors'):
                print(f"  Errors: {data['errors']}")
            return data['success']
        else:
            print(f"  ❌ Ingestion failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"  ❌ Ingestion error: {e}")
        return False


def test_search(base_url: str = "http://localhost:8001") -> bool:
    """Test the search endpoint."""
    print("\n🔍 Testing Similarity Search...")
    
    test_queries = [
        {
            "query": "What are the principles of data protection under GDPR?",
            "limit": 3,
            "min_score": 0.7
        },
        {
            "query": "How should access control be implemented?",
            "limit": 2,
            "min_score": 0.8,
            "source_filter": "ISO 27001"
        },
        {
            "query": "What are HIPAA technical safeguards?",
            "limit": 2,
            "min_score": 0.75
        }
    ]
    
    all_successful = True
    
    for test_query in test_queries:
        print(f"\n  Query: '{test_query['query']}'")
        print(f"  Params: limit={test_query['limit']}, min_score={test_query['min_score']}")
        
        try:
            response = requests.post(
                f"{base_url}/search",
                json=test_query
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Results found: {data['total_results']}")
                print(f"  Processing time: {data['processing_time_ms']:.2f}ms")
                
                for i, result in enumerate(data['results'], 1):
                    print(f"    {i}. Score: {result['score']:.4f} | Doc: {result['doc_id']}")
                    print(f"       Preview: {result['content'][:80]}...")
            else:
                print(f"  ❌ Search failed: {response.status_code}")
                all_successful = False
        except Exception as e:
            print(f"  ❌ Search error: {e}")
            all_successful = False
    
    return all_successful


def test_statistics(base_url: str = "http://localhost:8001") -> bool:
    """Test the statistics endpoint."""
    print("\n📊 Testing Statistics...")
    
    try:
        response = requests.get(f"{base_url}/stats")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Document Count: {data['document_count']}")
            print(f"  Chunk Count: {data['chunk_count']}")
            print(f"  Unique Sources: {data['unique_sources']}")
            print(f"  Embedding Model: {data['embedding_model']}")
            print(f"  Embedding Dimension: {data['embedding_dimension']}")
            
            if data['documents']:
                print(f"  Documents in dataset:")
                for doc in data['documents']:
                    print(f"    - {doc['doc_id']} (source: {doc['source']})")
            
            return True
        else:
            print(f"  ❌ Statistics failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Statistics error: {e}")
        return False


def test_clear_dataset(base_url: str = "http://localhost:8001") -> bool:
    """Test clearing the dataset."""
    print("\n🗑️  Testing Dataset Clear...")
    
    try:
        response = requests.delete(f"{base_url}/clear")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  Message: {data['message']}")
            print(f"  Deleted Documents: {data['deleted_documents']}")
            return True
        else:
            print(f"  ❌ Clear failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ Clear error: {e}")
        return False


def main():
    """Run all API tests."""
    print("=" * 60)
    print("🚀 Golden Dataset Retrieval API Test Suite")
    print("=" * 60)
    
    base_url = "http://localhost:8001"
    
    # Check if API is running
    print(f"\n🔗 Testing API at: {base_url}")
    
    # Wait for API to be ready
    max_retries = 5
    for i in range(max_retries):
        try:
            response = requests.get(f"{base_url}/health", timeout=1)
            if response.status_code == 200:
                print("✅ API is running!")
                break
        except:
            if i < max_retries - 1:
                print(f"  Waiting for API to start... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                print("❌ API is not running. Please start it with:")
                print("   python services/ai/evaluation/tools/retrieval_api.py")
                return 1
    
    # Run tests
    results = {
        "Health Check": test_health_check(base_url),
        "Ingestion": test_ingestion(base_url),
        "Search": test_search(base_url),
        "Statistics": test_statistics(base_url),
        # "Clear Dataset": test_clear_dataset(base_url)  # Optional - uncomment to test
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️ Some tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())