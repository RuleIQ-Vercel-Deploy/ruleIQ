"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Export Archon data from Supabase for backup/migration
This script extracts all ruleIQ project data from the Archon Supabase database
"""
from typing import Any
import os
import json
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
load_dotenv('/home/omar/Archon/.env')
SUPABASE_URL = os.getenv('SUPABASE_URL', 'https://nxmzlhiutzqvkyhhntez.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
if not SUPABASE_KEY:
    logger.info('Error: SUPABASE_SERVICE_KEY not found in environment')
    exit(1)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def export_table(table_name, filters=None) -> Any:
    """Export data from a specific table"""
    try:
        query = supabase.table(table_name).select('*')
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        response = query.execute()
        return response.data
    except Exception as e:
        logger.info(f'Error exporting {table_name}: {e}')
        return []

def export_archon_data() -> Any:
    """Export all Archon data related to ruleIQ project"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f'/home/omar/Documents/ruleIQ/backups/archon_{timestamp}'
    os.makedirs(backup_dir, exist_ok=True)
    logger.info(f'Creating backup in: {backup_dir}')
    tables_to_export = {'archon_projects': None, 'archon_tasks': None, 'archon_sources': None, 'archon_project_sources': None, 'archon_document_versions': None, 'archon_prompts': None, 'archon_settings': None}
    large_tables = {'archon_crawled_pages': {'source_id': 'supabase.com'}, 'archon_code_examples': None}
    export_summary = {}
    for table_name, filters in tables_to_export.items():
        logger.info(f'Exporting {table_name}...')
        data = export_table(table_name, filters)
        if data:
            file_path = os.path.join(backup_dir, f'{table_name}.json')
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            export_summary[table_name] = len(data)
            logger.info(f'  Exported {len(data)} records')
        else:
            logger.info('  No data found or error occurred')
            export_summary[table_name] = 0
    for table_name, filters in large_tables.items():
        logger.info(f'Exporting {table_name} (large table)...')
        data = export_table(table_name, filters)
        if data:
            file_path = os.path.join(backup_dir, f'{table_name}.json')
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            export_summary[table_name] = len(data)
            logger.info(f'  Exported {len(data)} records')
        else:
            export_summary[table_name] = 0
    logger.info('\nExporting ruleIQ project data specifically...')
    ruleiq_project_id = '342d657c-fb73-4f71-9b6e-302857319aac'
    ruleiq_project = export_table('archon_projects', {'id': ruleiq_project_id})
    if ruleiq_project:
        file_path = os.path.join(backup_dir, 'ruleiq_project.json')
        with open(file_path, 'w') as f:
            json.dump(ruleiq_project, f, indent=2, default=str)
        logger.info('  Exported ruleIQ project data')
    ruleiq_tasks = export_table('archon_tasks', {'project_id': ruleiq_project_id})
    if ruleiq_tasks:
        file_path = os.path.join(backup_dir, 'ruleiq_tasks.json')
        with open(file_path, 'w') as f:
            json.dump(ruleiq_tasks, f, indent=2, default=str)
        logger.info(f'  Exported {len(ruleiq_tasks)} ruleIQ tasks')
    summary = {'backup_timestamp': timestamp, 'supabase_url': SUPABASE_URL, 'tables_exported': export_summary, 'ruleiq_project_id': ruleiq_project_id, 'total_records': sum(export_summary.values())}
    summary_path = os.path.join(backup_dir, 'backup_summary.json')
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    logger.info('\n✅ Backup complete!')
    logger.info(f'📁 Location: {backup_dir}')
    logger.info(f"📊 Total records exported: {summary['total_records']}")
    create_restoration_script(backup_dir)
    return backup_dir

def create_restoration_script(backup_dir) -> None:
    """Create a script to restore the data"""
    restore_script = '#!/usr/bin/env python3\n"""\nRestore Archon data to Supabase\nGenerated restoration script for backup\n"""\n\nimport os\nimport json\nfrom supabase import create_client, Client\n\n# Supabase configuration (update these for your target database)\nSUPABASE_URL = input("Enter Supabase URL: ")\nSUPABASE_KEY = input("Enter Supabase Service Key: ")\n\n# Create Supabase client\nsupabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)\n\ndef restore_table(table_name, file_path):\n    """Restore data to a specific table"""\n    try:\n        with open(file_path, \'r\') as f:\n            data = json.load(f)\n        \n        if data:\n            # Insert data in batches\n            batch_size = 100\n            for i in range(0, len(data), batch_size):\n                batch = data[i:i+batch_size]\n                response = supabase.table(table_name).insert(batch).execute()\n                logger.info(f"  Restored {len(batch)} records to {table_name}")\n        \n        return True\n    except Exception as e:\n        logger.info(f"Error restoring {table_name}: {e}")\n        return False\n\n# Restore tables in order (respecting foreign key constraints)\ntables_order = [\n    \'archon_settings\',\n    \'archon_sources\',\n    \'archon_projects\',\n    \'archon_prompts\',\n    \'archon_tasks\',\n    \'archon_project_sources\',\n    \'archon_document_versions\',\n    \'archon_crawled_pages\',\n    \'archon_code_examples\'\n]\n\nbackup_dir = os.path.dirname(os.path.abspath(__file__))\n\nfor table_name in tables_order:\n    file_path = os.path.join(backup_dir, f\'{table_name}.json\')\n    if os.path.exists(file_path):\n        logger.info(f"Restoring {table_name}...")\n        restore_table(table_name, file_path)\n\nlogger.info("✅ Restoration complete!")\n'
    restore_path = os.path.join(backup_dir, 'restore_data.py')
    with open(restore_path, 'w') as f:
        f.write(restore_script)
    os.chmod(restore_path, 493)
    logger.info(f'📝 Created restoration script: {restore_path}')
if __name__ == '__main__':
    try:
        export_archon_data()
    except Exception as e:
        logger.info(f'Export failed: {e}')
        logger.info('\nPossible issues:')
        logger.info('1. Supabase connection failed - check if the project is still active')
        print('2. API keys expired - update SUPABASE_SERVICE_KEY in /home/omar/Archon/.env')
        logger.info('3. Network issues - check internet connection')
