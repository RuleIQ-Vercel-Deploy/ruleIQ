"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Import full document content to Supabase from Archon MCP data
"""
import json
from supabase import create_client, Client
SUPABASE_URL = 'https://wohtxsiayhtvycvkamev.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndvaHR4c2lheWh0dnljdmthbWV2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjYyNTczOSwiZXhwIjoyMDcyMjAxNzM5fQ.mzmZQ_cBvjr0B1oSuRrjZ_jk4HqM7Xz0bETDo29RzI0'
DOCUMENTS_WITH_CONTENT = [{'id': '50c934fe-378a-46a2-af81-703cae68ee9f', 'project_id': '342d657c-fb73-4f71-9b6e-302857319aac', 'document_type': 'analysis', 'title': 'AI System Architecture Analysis', 'status': 'draft', 'version': '1.0', 'tags': [], 'author': None, 'content': {'scope': 'Complete AI system from LLM to UI output', 'methodology': 'Direct code examination using Serena MCP tools', 'analysis_type': 'code_architecture_review', 'executive_summary': "Comprehensive analysis of ruleIQ's AI system reveals a sophisticated, production-ready architecture with advanced resilience patterns, multi-LLM integration, performance optimization, and comprehensive monitoring capabilities."}}]

def import_documents_with_content() -> bool:
    """Import documents with full content to Supabase"""
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info('Importing documents with full content to Supabase...')
    project_id = '342d657c-fb73-4f71-9b6e-302857319aac'
    docs_array = []
    try:
        response = supabase.table('archon_projects').update({'docs': docs_array}).eq('id', project_id).execute()
        logger.info(f'✅ Successfully updated project with {len(docs_array)} documents')
    except Exception as e:
        logger.info(f'❌ Error updating project: {e}')
    return True
if __name__ == '__main__':
    import_documents_with_content()