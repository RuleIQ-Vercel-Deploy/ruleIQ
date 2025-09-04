"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Import Archon data to Supabase
This script imports the Archon MCP data into a Supabase instance
"""
import os
import json
from datetime import datetime
from supabase import create_client, Client
from pathlib import Path

def import_archon_data() -> bool:
    """Import Archon data to Supabase"""
    export_file = Path('/home/omar/Documents/ruleIQ/archon_data_export.json')
    with open(export_file, 'r') as f:
        export_data = json.load(f)
    logger.info('=' * 60)
    logger.info('ARCHON DATA IMPORT TO SUPABASE')
    logger.info('=' * 60)
    logger.info('\nPlease provide your Supabase credentials:')
    logger.info('(You can find these in your Supabase project settings)')
    SUPABASE_URL = input('Enter Supabase URL (e.g., https://xxx.supabase.co): ').strip()
    SUPABASE_KEY = input("Enter Supabase Service Key (starts with 'eyJ...'): ").strip()
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.info('❌ Error: Both URL and Service Key are required')
        return False
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info('✅ Connected to Supabase successfully')
    except Exception as e:
        logger.info(f'❌ Error connecting to Supabase: {e}')
        return False
    logger.info('\n📁 Importing Projects...')
    projects = export_data['tables']['archon_projects']
    if projects:
        try:
            response = supabase.table('archon_projects').upsert(projects).execute()
            logger.info(f'  ✅ Imported {len(projects)} project(s)')
        except Exception as e:
            logger.info(f'  ❌ Error importing projects: {e}')
    logger.info('\n📄 Importing Documents...')
    documents = export_data['tables']['archon_documents']
    if documents:
        try:
            for doc in documents:
                if 'project_id' not in doc:
                    doc['project_id'] = export_data['project_id']
            batch_size = 50
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                response = supabase.table('archon_documents').upsert(batch).execute()
                print(f'  ✅ Imported batch {i // batch_size + 1} ({len(batch)} documents)')
        except Exception as e:
            logger.info(f'  ❌ Error importing documents: {e}')
    logger.info('\n📋 Tasks Note:')
    logger.info('  ⚠️  Tasks require manual pagination due to size limits.')
    logger.info('  Use the following approach to import tasks:')
    logger.info()
    logger.info('  1. Use Archon MCP to export tasks page by page:')
    logger.info("     mcp__archon__list_tasks(filter_by='project', ")
    print("                             filter_value='342d657c-fb73-4f71-9b6e-302857319aac',")
    logger.info('                             page=1, per_page=10)')
    logger.info()
    logger.info('  2. Save each page to a separate JSON file')
    logger.info("  3. Import each page using this script's task import function")
    logger.info('\n' + '=' * 60)
    logger.info('IMPORT SUMMARY')
    logger.info('=' * 60)
    logger.info(f'✅ Projects imported: {len(projects)}')
    logger.info(f'✅ Documents imported: {len(documents)}')
    logger.info(f'⚠️  Tasks: Manual import required (see instructions above)')
    logger.info('\n✨ Import complete!')
    logger.info('\nNext steps:')
    logger.info('1. Verify data in your Supabase dashboard')
    logger.info("2. Update Archon's .env file with these Supabase credentials")
    logger.info('3. Restart Archon to connect to the new database')
    save_config = input('\nSave Supabase config for Archon? (y/n): ').lower()
    if save_config == 'y':
        config_file = Path('/home/omar/Documents/ruleIQ/archon_supabase_config.txt')
        with open(config_file, 'w') as f:
            f.write(f'# Archon Supabase Configuration\n')
            f.write(f"# Add these to Archon's .env file:\n\n")
            f.write(f'SUPABASE_URL={SUPABASE_URL}\n')
            f.write(f'SUPABASE_SERVICE_KEY={SUPABASE_KEY}\n')
        logger.info(f'✅ Config saved to: {config_file}')
        logger.info('   Copy these values to /home/omar/Archon/.env')
    return True

def import_tasks_batch(tasks_json_file, supabase_url, supabase_key) -> bool:
    """Import a batch of tasks from a JSON file"""
    with open(tasks_json_file, 'r') as f:
        tasks = json.load(f)
    supabase: Client = create_client(supabase_url, supabase_key)
    try:
        response = supabase.table('archon_tasks').upsert(tasks).execute()
        logger.info(f'✅ Imported {len(tasks)} tasks from {tasks_json_file}')
        return True
    except Exception as e:
        logger.info(f'❌ Error importing tasks: {e}')
        return False
if __name__ == '__main__':
    try:
        logger.info('🚀 Starting Archon data import to Supabase\n')
        export_file = Path('/home/omar/Documents/ruleIQ/archon_data_export.json')
        if not export_file.exists():
            logger.info('❌ Export file not found. Please run the export process first.')
            exit(1)
        success = import_archon_data()
        if success:
            logger.info('\n✅ Import process completed successfully!')
        else:
            print('\n❌ Import process encountered errors. Please check the output above.')
    except KeyboardInterrupt:
        logger.info('\n\n⚠️  Import cancelled by user')
    except Exception as e:
        logger.info(f'\n❌ Unexpected error: {e}')