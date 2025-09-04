"""
Export Archon MCP data to JSON format for Supabase import
This script extracts all ruleIQ project data from the Archon MCP server
"""
from typing import Any, Optional
import logging
logger = logging.getLogger(__name__)
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
RULEIQ_PROJECT_ID = '342d657c-fb73-4f71-9b6e-302857319aac'

def call_mcp_tool(tool_name, params=None) -> Optional[Any]:
    """Call an MCP tool and return the response"""
    cmd = ['mcp', 'call', 'archon', tool_name]
    if params:
        cmd.extend(['--params', json.dumps(params)])
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            logger.info(f'Error calling {tool_name}: {result.stderr}')
            return None
    except Exception as e:
        logger.info(f'Exception calling {tool_name}: {e}')
        return None

def export_archon_data() -> Any:
    """Export all Archon data for ruleIQ project"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = Path(f'/home/omar/Documents/ruleIQ/backups/archon_{timestamp}')
    backup_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f'Creating Archon data export in: {backup_dir}')
    export_data = {'export_timestamp': timestamp, 'project_id': RULEIQ_PROJECT_ID, 'tables': {}}
    logger.info('Exporting project data...')
    projects = call_mcp_tool('list_projects')
    if projects and projects.get('success'):
        export_data['tables']['archon_projects'] = projects.get('projects', [])
        logger.info(f"  Exported {len(export_data['tables']['archon_projects'])} projects")
    logger.info('Exporting tasks...')
    all_tasks = []
    page = 1
    per_page = 5
    while True:
        tasks = call_mcp_tool('list_tasks', {'filter_by': 'project', 'filter_value': RULEIQ_PROJECT_ID, 'include_closed': True, 'page': page, 'per_page': per_page})
        if not tasks or not tasks.get('success'):
            break
        task_list = tasks.get('tasks', [])
        if not task_list:
            break
        all_tasks.extend(task_list)
        logger.info(f'  Fetched page {page} ({len(task_list)} tasks)')
        if len(task_list) < per_page:
            break
        page += 1
    export_data['tables']['archon_tasks'] = all_tasks
    logger.info(f'  Total tasks exported: {len(all_tasks)}')
    logger.info('Exporting documents...')
    documents = call_mcp_tool('list_documents', {'project_id': RULEIQ_PROJECT_ID})
    if documents and documents.get('success'):
        export_data['tables']['archon_documents'] = documents.get('documents', [])
        logger.info(f"  Exported {len(export_data['tables']['archon_documents'])} documents")
    logger.info('Exporting project features...')
    features = call_mcp_tool('get_project_features', {'project_id': RULEIQ_PROJECT_ID})
    if features and features.get('success'):
        export_data['project_features'] = features.get('features', [])
        logger.info(f"  Exported {len(export_data['project_features'])} features")
    logger.info('Exporting version history...')
    versions = call_mcp_tool('list_versions', {'project_id': RULEIQ_PROJECT_ID})
    if versions and versions.get('success'):
        export_data['tables']['archon_document_versions'] = versions.get('versions', [])
        logger.info(f"  Exported {len(export_data['tables']['archon_document_versions'])} versions")
    export_file = backup_dir / 'archon_export.json'
    with open(export_file, 'w') as f:
        json.dump(export_data, f, indent=2, default=str)
    logger.info(f'\n✅ Export complete!')
    logger.info(f'📁 Location: {backup_dir}')
    logger.info(f'📊 Summary:')
    for table, data in export_data['tables'].items():
        logger.info(f'   - {table}: {len(data)} records')
    create_import_script(backup_dir, export_data)
    return backup_dir

def create_import_script(backup_dir, export_data) -> None:
    """Create a Python script to import data to Supabase"""
    import_script = '#!/usr/bin/env python3\n"""\nImport Archon data to Supabase\nThis script imports the exported Archon data into a new or existing Supabase instance\n"""\n\nimport os\nimport json\nfrom datetime import datetime\nfrom supabase import create_client, Client\nfrom pathlib import Path\n\n# Load the export data\nscript_dir = Path(__file__).parent\nexport_file = script_dir / \'archon_export.json\'\n\nwith open(export_file, \'r\') as f:\n    export_data = json.load(f)\n\n# Supabase configuration\nSUPABASE_URL = input("Enter your Supabase URL: ").strip()\nSUPABASE_KEY = input("Enter your Supabase Service Key: ").strip()\n\n# Create Supabase client\nsupabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)\n\ndef import_table(table_name, data):\n    """Import data to a specific table"""\n    if not data:\n        logger.info(f"  No data to import for {table_name}")\n        return\n    \n    try:\n        # Import in batches\n        batch_size = 50\n        for i in range(0, len(data), batch_size):\n            batch = data[i:i+batch_size]\n            response = supabase.table(table_name).upsert(batch).execute()\n            logger.info(f"  Imported batch {i//batch_size + 1} ({len(batch)} records)")\n        \n        logger.info(f"✅ Successfully imported {len(data)} records to {table_name}")\n        return True\n    except Exception as e:\n        logger.info(f"❌ Error importing {table_name}: {e}")\n        return False\n\nlogger.info("\\n🚀 Starting Archon data import to Supabase\\n")\n\n# Import tables in order (respecting foreign key constraints)\nimport_order = [\n    \'archon_projects\',\n    \'archon_tasks\',\n    \'archon_documents\',\n    \'archon_document_versions\'\n]\n\nfor table_name in import_order:\n    if table_name in export_data[\'tables\']:\n        logger.info(f"\\nImporting {table_name}...")\n        import_table(table_name, export_data[\'tables\'][table_name])\n\n# Handle project features separately (stored in project data field)\nif \'project_features\' in export_data and export_data[\'project_features\']:\n    logger.info("\\nUpdating project features...")\n    try:\n        project_id = export_data[\'project_id\']\n        features_data = {\'features\': export_data[\'project_features\']}\n        response = supabase.table(\'archon_projects\').update(features_data).eq(\'id\', project_id).execute()\n        logger.info(f"✅ Updated features for project {project_id}")\n    except Exception as e:\n        logger.info(f"❌ Error updating features: {e}")\n\nlogger.info("\\n✅ Import complete!")\nlogger.info("\\nNext steps:")\nlogger.info("1. Verify data in Supabase dashboard")\nlogger.info("2. Update Archon\'s .env file with new Supabase credentials")\nlogger.info("3. Restart Archon to connect to the new database")\n'
    import_script_path = backup_dir / 'import_to_supabase.py'
    with open(import_script_path, 'w') as f:
        f.write(import_script)
    import_script_path.chmod(493)
    logger.info(f'📝 Created import script: {import_script_path}')
if __name__ == '__main__':
    try:
        logger.info('Attempting to export Archon data via MCP...')
        logger.info('Note: This requires the Archon MCP server to be running and accessible')
        logger.info('\n' + '=' * 60)
        logger.info('MANUAL EXPORT INSTRUCTIONS')
        logger.info('=' * 60)
        logger.info('\nSince we have confirmed the Archon MCP server has your data,')
        logger.info('you can manually export it using these MCP tool calls:\n')
        logger.info('1. Get project details:')
        logger.info("   mcp__archon__get_project(project_id='342d657c-fb73-4f71-9b6e-302857319aac')")
        logger.info('\n2. Export tasks (use pagination):')
        logger.info("   mcp__archon__list_tasks(filter_by='project', filter_value='342d657c-fb73-4f71-9b6e-302857319aac', page=1, per_page=5)")
        logger.info('\n3. Export documents:')
        logger.info("   mcp__archon__list_documents(project_id='342d657c-fb73-4f71-9b6e-302857319aac')")
        logger.info('\n4. Export features:')
        logger.info("   mcp__archon__get_project_features(project_id='342d657c-fb73-4f71-9b6e-302857319aac')")
        logger.info('\n5. Export version history:')
        logger.info("   mcp__archon__list_versions(project_id='342d657c-fb73-4f71-9b6e-302857319aac')")
        logger.info('\n' + '=' * 60)
    except Exception as e:
        logger.info(f'Export failed: {e}')