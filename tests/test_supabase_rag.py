#!/usr/bin/env python3
"""
Test Supabase Agentic RAG System
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langgraph_agent.agents.rag_system import RAGSystem as AgenticRAGSystem


async def test_supabase_rag():
    """Test the Supabase-integrated Agentic RAG system"""
    print("🚀 Testing Supabase Agentic RAG System")
    print("=" * 50)

    try:
        # Initialize the RAG system
        print("📦 Initializing Agentic RAG System with Supabase...")
        rag_system = AgenticRAGSystem()
        print("✅ Successfully initialized RAG system")

        # Test database connection
        print("\n🔍 Testing database connection...")

        # Test getting available sources
        sources = await rag_system.get_available_sources()
        print(f"✅ Available sources: {sources}")

        # Test framework statistics
        stats = await rag_system.get_framework_statistics()
        print(f"📊 Framework statistics: {stats}")

        # Test a simple query if we have documentation
        if sources:
            print("\n🤖 Testing RAG query...")
            query = "How do I implement state management in LangGraph?"
            response = await rag_system.query_documentation(query, max_results=3)
            print(f"💬 Query: {query}")
            print(f"📝 Response: {response.answer[:200]}...")
            print(f"📊 Confidence: {response.confidence}")
            print(f"🔗 Sources: {len(response.sources)}")
        else:
            print("📝 No documentation found - ready for indexing!")

        print("\n🎉 All tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Clean up connections
        try:
            rag_system.close()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(test_supabase_rag())
