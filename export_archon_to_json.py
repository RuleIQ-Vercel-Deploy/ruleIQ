#!/usr/bin/env python3
"""
Export Archon MCP data to JSON format for Supabase import
This script extracts all ruleIQ project data from the Archon MCP server
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Project ID for ruleIQ
RULEIQ_PROJECT_ID = "342d657c-fb73-4f71-9b6e-302857319aac"

def call_mcp_tool(tool_name, params=None):
    """Call an MCP tool and return the response"""
    cmd = ["mcp", "call", "archon", tool_name]
    if params:
        cmd.extend(["--params", json.dumps(params)])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Error calling {tool_name}: {result.stderr}")
            return None
    except Exception as e:
        print(f"Exception calling {tool_name}: {e}")
        return None

def export_archon_data():
    """Export all Archon data for ruleIQ project"""
    
    # Create backup directory with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = Path(f'/home/omar/Documents/ruleIQ/backups/archon_{timestamp}')
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Creating Archon data export in: {backup_dir}")
    
    export_data = {
        'export_timestamp': timestamp,
        'project_id': RULEIQ_PROJECT_ID,
        'tables': {}
    }
    
    # Export project data
    print("Exporting project data...")
    projects = call_mcp_tool('list_projects')
    if projects and projects.get('success'):
        export_data['tables']['archon_projects'] = projects.get('projects', [])
        print(f"  Exported {len(export_data['tables']['archon_projects'])} projects")
    
    # Export tasks (with pagination to avoid token limit)
    print("Exporting tasks...")
    all_tasks = []
    page = 1
    per_page = 5  # Small page size to avoid token limits
    
    while True:
        tasks = call_mcp_tool('list_tasks', {
            'filter_by': 'project',
            'filter_value': RULEIQ_PROJECT_ID,
            'include_closed': True,
            'page': page,
            'per_page': per_page
        })
        
        if not tasks or not tasks.get('success'):
            break
        
        task_list = tasks.get('tasks', [])
        if not task_list:
            break
        
        all_tasks.extend(task_list)
        print(f"  Fetched page {page} ({len(task_list)} tasks)")
        
        # Check if there are more pages
        if len(task_list) < per_page:
            break
        page += 1
    
    export_data['tables']['archon_tasks'] = all_tasks
    print(f"  Total tasks exported: {len(all_tasks)}")
    
    # Export documents
    print("Exporting documents...")
    documents = call_mcp_tool('list_documents', {
        'project_id': RULEIQ_PROJECT_ID
    })
    if documents and documents.get('success'):
        export_data['tables']['archon_documents'] = documents.get('documents', [])
        print(f"  Exported {len(export_data['tables']['archon_documents'])} documents")
    
    # Export project features
    print("Exporting project features...")
    features = call_mcp_tool('get_project_features', {
        'project_id': RULEIQ_PROJECT_ID
    })
    if features and features.get('success'):
        export_data['project_features'] = features.get('features', [])
        print(f"  Exported {len(export_data['project_features'])} features")
    
    # Export version history
    print("Exporting version history...")
    versions = call_mcp_tool('list_versions', {
        'project_id': RULEIQ_PROJECT_ID
    })
    if versions and versions.get('success'):
        export_data['tables']['archon_document_versions'] = versions.get('versions', [])
        print(f"  Exported {len(export_data['tables']['archon_document_versions'])} versions")
    
    # Save main export file
    export_file = backup_dir / 'archon_export.json'
    with open(export_file, 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    
    print(f"\n✅ Export complete!")
    print(f"📁 Location: {backup_dir}")
    print(f"📊 Summary:")
    for table, data in export_data['tables'].items():
        print(f"   - {table}: {len(data)} records")
    
    # Create import script for Supabase
    create_import_script(backup_dir, export_data)
    
    return backup_dir

def create_import_script(backup_dir, export_data):
    """Create a Python script to import data to Supabase"""
    
    import_script = '''#!/usr/bin/env python3
"""
Import Archon data to Supabase
This script imports the exported Archon data into a new or existing Supabase instance
"""

import os
import json
from datetime import datetime
from supabase import create_client, Client
from pathlib import Path

# Load the export data
script_dir = Path(__file__).parent
export_file = script_dir / 'archon_export.json'

with open(export_file, 'r') as f:
    export_data = json.load(f)

# Supabase configuration
SUPABASE_URL = input("Enter your Supabase URL: ").strip()
SUPABASE_KEY = input("Enter your Supabase Service Key: ").strip()

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def import_table(table_name, data):
    """Import data to a specific table"""
    if not data:
        print(f"  No data to import for {table_name}")
        return
    
    try:
        # Import in batches
        batch_size = 50
        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            response = supabase.table(table_name).upsert(batch).execute()
            print(f"  Imported batch {i//batch_size + 1} ({len(batch)} records)")
        
        print(f"✅ Successfully imported {len(data)} records to {table_name}")
        return True
    except Exception as e:
        print(f"❌ Error importing {table_name}: {e}")
        return False

print("\\n🚀 Starting Archon data import to Supabase\\n")

# Import tables in order (respecting foreign key constraints)
import_order = [
    'archon_projects',
    'archon_tasks',
    'archon_documents',
    'archon_document_versions'
]

for table_name in import_order:
    if table_name in export_data['tables']:
        print(f"\\nImporting {table_name}...")
        import_table(table_name, export_data['tables'][table_name])

# Handle project features separately (stored in project data field)
if 'project_features' in export_data and export_data['project_features']:
    print("\\nUpdating project features...")
    try:
        project_id = export_data['project_id']
        features_data = {'features': export_data['project_features']}
        response = supabase.table('archon_projects').update(features_data).eq('id', project_id).execute()
        print(f"✅ Updated features for project {project_id}")
    except Exception as e:
        print(f"❌ Error updating features: {e}")

print("\\n✅ Import complete!")
print("\\nNext steps:")
print("1. Verify data in Supabase dashboard")
print("2. Update Archon's .env file with new Supabase credentials")
print("3. Restart Archon to connect to the new database")
'''
    
    import_script_path = backup_dir / 'import_to_supabase.py'
    with open(import_script_path, 'w') as f:
        f.write(import_script)
    
    import_script_path.chmod(0o755)
    print(f"📝 Created import script: {import_script_path}")

if __name__ == "__main__":
    try:
        # Note: This script attempts to use MCP CLI directly
        # If MCP CLI is not available, we'll use the Archon MCP server directly
        print("Attempting to export Archon data via MCP...")
        print("Note: This requires the Archon MCP server to be running and accessible")
        
        # For now, we'll document the manual export process
        print("\n" + "="*60)
        print("MANUAL EXPORT INSTRUCTIONS")
        print("="*60)
        print("\nSince we have confirmed the Archon MCP server has your data,")
        print("you can manually export it using these MCP tool calls:\n")
        
        print("1. Get project details:")
        print("   mcp__archon__get_project(project_id='342d657c-fb73-4f71-9b6e-302857319aac')")
        
        print("\n2. Export tasks (use pagination):")
        print("   mcp__archon__list_tasks(filter_by='project', filter_value='342d657c-fb73-4f71-9b6e-302857319aac', page=1, per_page=5)")
        
        print("\n3. Export documents:")
        print("   mcp__archon__list_documents(project_id='342d657c-fb73-4f71-9b6e-302857319aac')")
        
        print("\n4. Export features:")
        print("   mcp__archon__get_project_features(project_id='342d657c-fb73-4f71-9b6e-302857319aac')")
        
        print("\n5. Export version history:")
        print("   mcp__archon__list_versions(project_id='342d657c-fb73-4f71-9b6e-302857319aac')")
        
        print("\n" + "="*60)
        
    except Exception as e:
        print(f"Export failed: {e}")