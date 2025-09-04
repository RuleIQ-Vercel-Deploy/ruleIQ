#!/usr/bin/env python3
"""
Test script to verify the LangGraph import chain is fixed.
"""

import sys
import traceback

def test_imports():
    """Test the import chain that was failing."""
    
    print("Testing import chain for langgraph_agent.nodes.compliance_nodes...")
    print("-" * 60)
    
    try:
        # Test the main import that was failing
        print("1. Importing compliance_nodes module...")
        from langgraph_agent.nodes.compliance_nodes import compliance_check_node
        print("   ✓ Successfully imported compliance_check_node")
        
        # Test the langsmith config that we fixed
        print("\n2. Testing langsmith_config import...")
        from config.langsmith_config import LangSmithConfig
        print("   ✓ Successfully imported LangSmithConfig")
        
        # Test other related imports
        print("\n3. Testing unified_state import...")
        from langgraph_agent.graph.unified_state import UnifiedComplianceState
        print("   ✓ Successfully imported UnifiedComplianceState")
        
        print("\n4. Testing cost_tracking import...")
        from langgraph_agent.utils.cost_tracking import track_node_cost
        print("   ✓ Successfully imported track_node_cost")
        
        print("\n5. Testing neo4j_service import...")
        from services.neo4j_service import get_neo4j_service
        print("   ✓ Successfully imported get_neo4j_service")
        
        print("\n" + "=" * 60)
        print("✅ ALL IMPORTS SUCCESSFUL! The import chain is fixed.")
        print("=" * 60)
        return True
        
    except SyntaxError as e:
        print(f"\n❌ SYNTAX ERROR DETECTED:")
        print(f"   File: {e.filename}")
        print(f"   Line: {e.lineno}")
        print(f"   Text: {e.text}")
        print(f"   Message: {e.msg}")
        traceback.print_exc()
        return False
        
    except ImportError as e:
        print(f"\n❌ IMPORT ERROR: {e}")
        traceback.print_exc()
        return False
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)