from typing import Any
import os
'\nMigrate ALL Archon data from old Supabase to new Supabase\nThis includes tasks, sources, crawled pages, and code examples\n'
import logging
logger = logging.getLogger(__name__)
from supabase import create_client
OLD_SUPABASE_URL = 'https://nxmzlhiutzqvkyhhntez.supabase.co'
OLD_SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
NEW_SUPABASE_URL = 'https://wohtxsiayhtvycvkamev.supabase.co'
NEW_SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')

def migrate_table(table_name, old_client, new_client, batch_size=100) -> Any:
    """Migrate a table from old to new Supabase"""
    logger.info(f'\n📦 Migrating {table_name}...')
    try:
        all_data = []
        offset = 0
        while True:
            response = old_client.table(table_name).select('*').range(offset, offset + batch_size - 1).execute()
            if not response.data:
                break
            all_data.extend(response.data)
            logger.info(f'  Fetched {len(response.data)} records (total: {len(all_data)})')
            if len(response.data) < batch_size:
                break
            offset += batch_size
        if not all_data:
            logger.info('  No data to migrate')
            return 0
        for i in range(0, len(all_data), batch_size):
            batch = all_data[i:i + batch_size]
            new_client.table(table_name).upsert(batch).execute()
            logger.info(f'  Migrated batch {i // batch_size + 1} ({len(batch)} records)')
        logger.info(f'  ✅ Successfully migrated {len(all_data)} records')
        return len(all_data)
    except Exception as e:
        logger.info(f'  ❌ Error: {e}')
        return 0

def main() -> None:
    logger.info('=' * 60)
    logger.info('ARCHON DATA MIGRATION')
    logger.info('From: OLD Supabase (nxmzlhiutzqvkyhhntez)')
    logger.info('To:   NEW Supabase (wohtxsiayhtvycvkamev)')
    logger.info('=' * 60)
    old_supabase = create_client(OLD_SUPABASE_URL, OLD_SUPABASE_KEY)
    new_supabase = create_client(NEW_SUPABASE_URL, NEW_SUPABASE_KEY)
    tables = ['archon_sources', 'archon_prompts', 'archon_settings', 'archon_tasks', 'archon_project_sources', 'archon_document_versions', 'archon_crawled_pages', 'archon_code_examples']
    stats = {}
    for table in tables:
        count = migrate_table(table, old_supabase, new_supabase)
        stats[table] = count
    logger.info('\n📄 Updating project documents...')
    try:
        old_project = old_supabase.table('archon_projects').select('*').eq('id', '342d657c-fb73-4f71-9b6e-302857319aac').execute()
        if old_project.data and old_project.data[0].get('docs'):
            new_supabase.table('archon_projects').update({'docs': old_project.data[0]['docs']}).eq('id', '342d657c-fb73-4f71-9b6e-302857319aac').execute()
            logger.info('  ✅ Updated project docs field')
    except Exception as e:
        logger.info(f'  ❌ Error updating docs: {e}')
    logger.info('\n' + '=' * 60)
    logger.info('MIGRATION COMPLETE!')
    logger.info('=' * 60)
    for table, count in stats.items():
        status = '✅' if count > 0 else '⚠️'
        logger.info(f'{status} {table}: {count} records')
    logger.info('\n🎉 Your Archon knowledge base has been migrated!')
    logger.info('Tasks, sources, and documentation are now in the new Supabase.')
if __name__ == '__main__':
    main()
