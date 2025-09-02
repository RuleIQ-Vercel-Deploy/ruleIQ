#!/usr/bin/env python3
"""
Export Archon data from Supabase for backup/migration
This script extracts all ruleIQ project data from the Archon Supabase database
"""

import os
import json
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv("/home/omar/Archon/.env")

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://nxmzlhiutzqvkyhhntez.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_KEY:
    print("Error: SUPABASE_SERVICE_KEY not found in environment")
    exit(1)

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def export_table(table_name, filters=None):
    """Export data from a specific table"""
    try:
        query = supabase.table(table_name).select("*")

        # Apply filters if provided
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        response = query.execute()
        return response.data
    except Exception as e:
        print(f"Error exporting {table_name}: {e}")
        return []


def export_archon_data():
    """Export all Archon data related to ruleIQ project"""

    # Create backup directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"/home/omar/Documents/ruleIQ/backups/archon_{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)

    print(f"Creating backup in: {backup_dir}")

    # Define tables to export
    tables_to_export = {
        "archon_projects": None,  # Export all projects
        "archon_tasks": None,  # Export all tasks
        "archon_sources": None,  # Export all sources
        "archon_project_sources": None,  # Export project-source links
        "archon_document_versions": None,  # Export document versions
        "archon_prompts": None,  # Export prompts
        "archon_settings": None,  # Export settings (be careful with sensitive data)
    }

    # Tables with large data (export selectively)
    large_tables = {
        "archon_crawled_pages": {"source_id": "supabase.com"},  # Example filter
        "archon_code_examples": None,  # Export all code examples
    }

    export_summary = {}

    # Export regular tables
    for table_name, filters in tables_to_export.items():
        print(f"Exporting {table_name}...")
        data = export_table(table_name, filters)

        if data:
            file_path = os.path.join(backup_dir, f"{table_name}.json")
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2, default=str)

            export_summary[table_name] = len(data)
            print(f"  Exported {len(data)} records")
        else:
            print(f"  No data found or error occurred")
            export_summary[table_name] = 0

    # Export large tables with pagination if needed
    for table_name, filters in large_tables.items():
        print(f"Exporting {table_name} (large table)...")
        data = export_table(table_name, filters)

        if data:
            file_path = os.path.join(backup_dir, f"{table_name}.json")
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2, default=str)

            export_summary[table_name] = len(data)
            print(f"  Exported {len(data)} records")
        else:
            export_summary[table_name] = 0

    # Special export for ruleIQ project specifically
    print("\nExporting ruleIQ project data specifically...")
    ruleiq_project_id = "342d657c-fb73-4f71-9b6e-302857319aac"

    # Get ruleIQ project
    ruleiq_project = export_table("archon_projects", {"id": ruleiq_project_id})
    if ruleiq_project:
        file_path = os.path.join(backup_dir, "ruleiq_project.json")
        with open(file_path, "w") as f:
            json.dump(ruleiq_project, f, indent=2, default=str)
        print(f"  Exported ruleIQ project data")

    # Get ruleIQ tasks
    ruleiq_tasks = export_table("archon_tasks", {"project_id": ruleiq_project_id})
    if ruleiq_tasks:
        file_path = os.path.join(backup_dir, "ruleiq_tasks.json")
        with open(file_path, "w") as f:
            json.dump(ruleiq_tasks, f, indent=2, default=str)
        print(f"  Exported {len(ruleiq_tasks)} ruleIQ tasks")

    # Create summary file
    summary = {
        "backup_timestamp": timestamp,
        "supabase_url": SUPABASE_URL,
        "tables_exported": export_summary,
        "ruleiq_project_id": ruleiq_project_id,
        "total_records": sum(export_summary.values()),
    }

    summary_path = os.path.join(backup_dir, "backup_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n✅ Backup complete!")
    print(f"📁 Location: {backup_dir}")
    print(f"📊 Total records exported: {summary['total_records']}")

    # Create restoration script
    create_restoration_script(backup_dir)

    return backup_dir


def create_restoration_script(backup_dir):
    """Create a script to restore the data"""

    restore_script = '''#!/usr/bin/env python3
"""
Restore Archon data to Supabase
Generated restoration script for backup
"""

import os
import json
from supabase import create_client, Client

# Supabase configuration (update these for your target database)
SUPABASE_URL = input("Enter Supabase URL: ")
SUPABASE_KEY = input("Enter Supabase Service Key: ")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def restore_table(table_name, file_path):
    """Restore data to a specific table"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if data:
            # Insert data in batches
            batch_size = 100
            for i in range(0, len(data), batch_size):
                batch = data[i:i+batch_size]
                response = supabase.table(table_name).insert(batch).execute()
                print(f"  Restored {len(batch)} records to {table_name}")
        
        return True
    except Exception as e:
        print(f"Error restoring {table_name}: {e}")
        return False

# Restore tables in order (respecting foreign key constraints)
tables_order = [
    'archon_settings',
    'archon_sources',
    'archon_projects',
    'archon_prompts',
    'archon_tasks',
    'archon_project_sources',
    'archon_document_versions',
    'archon_crawled_pages',
    'archon_code_examples'
]

backup_dir = os.path.dirname(os.path.abspath(__file__))

for table_name in tables_order:
    file_path = os.path.join(backup_dir, f'{table_name}.json')
    if os.path.exists(file_path):
        print(f"Restoring {table_name}...")
        restore_table(table_name, file_path)

print("✅ Restoration complete!")
'''

    restore_path = os.path.join(backup_dir, "restore_data.py")
    with open(restore_path, "w") as f:
        f.write(restore_script)

    os.chmod(restore_path, 0o755)
    print(f"📝 Created restoration script: {restore_path}")


if __name__ == "__main__":
    try:
        export_archon_data()
    except Exception as e:
        print(f"Export failed: {e}")
        print("\nPossible issues:")
        print("1. Supabase connection failed - check if the project is still active")
        print(
            "2. API keys expired - update SUPABASE_SERVICE_KEY in /home/omar/Archon/.env"
        )
        print("3. Network issues - check internet connection")
