#!/usr/bin/env python3
"""
Import full document content to Supabase from Archon MCP data
"""

import json
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = 'https://wohtxsiayhtvycvkamev.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndvaHR4c2lheWh0dnljdmthbWV2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjYyNTczOSwiZXhwIjoyMDcyMjAxNzM5fQ.mzmZQ_cBvjr0B1oSuRrjZ_jk4HqM7Xz0bETDo29RzI0'

# The full document data from the Archon MCP server (from get_project response)
DOCUMENTS_WITH_CONTENT = [
    {
        "id": "50c934fe-378a-46a2-af81-703cae68ee9f",
        "project_id": "342d657c-fb73-4f71-9b6e-302857319aac",
        "document_type": "analysis",
        "title": "AI System Architecture Analysis",
        "status": "draft",
        "version": "1.0",
        "tags": [],
        "author": None,
        "content": {
            "scope": "Complete AI system from LLM to UI output",
            "methodology": "Direct code examination using Serena MCP tools",
            "analysis_type": "code_architecture_review",
            "executive_summary": "Comprehensive analysis of ruleIQ's AI system reveals a sophisticated, production-ready architecture with advanced resilience patterns, multi-LLM integration, performance optimization, and comprehensive monitoring capabilities.",
            # ... (full content from the get_project response)
        }
    },
    # Add all other documents with their content here
]

def import_documents_with_content():
    """Import documents with full content to Supabase"""
    
    # Create Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("Importing documents with full content to Supabase...")
    
    # Since we have the full content from the MCP server, we need to update the project
    # to include the docs array with all content
    
    project_id = "342d657c-fb73-4f71-9b6e-302857319aac"
    
    # Get the docs array from the get_project response
    docs_array = []  # This should be populated with the full docs array from get_project
    
    try:
        # Update the project with the docs array
        response = supabase.table('archon_projects').update({
            'docs': docs_array
        }).eq('id', project_id).execute()
        
        print(f"✅ Successfully updated project with {len(docs_array)} documents")
        
    except Exception as e:
        print(f"❌ Error updating project: {e}")
    
    return True

if __name__ == "__main__":
    import_documents_with_content()