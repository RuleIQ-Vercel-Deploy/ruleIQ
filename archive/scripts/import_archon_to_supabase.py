#!/usr/bin/env python3
"""
Import Archon data to Supabase
This script imports the Archon MCP data into a Supabase instance
"""

import os
import json
from datetime import datetime
from supabase import create_client, Client
from pathlib import Path


def import_archon_data():
    """Import Archon data to Supabase"""

    # Load the export data
    export_file = Path("/home/omar/Documents/ruleIQ/archon_data_export.json")
    with open(export_file, "r") as f:
        export_data = json.load(f)

    print("=" * 60)
    print("ARCHON DATA IMPORT TO SUPABASE")
    print("=" * 60)

    # Get Supabase credentials
    print("\nPlease provide your Supabase credentials:")
    print("(You can find these in your Supabase project settings)")

    SUPABASE_URL = input("Enter Supabase URL (e.g., https://xxx.supabase.co): ").strip()
    SUPABASE_KEY = input("Enter Supabase Service Key (starts with 'eyJ...'): ").strip()

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Error: Both URL and Service Key are required")
        return False

    # Create Supabase client
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Connected to Supabase successfully")
    except Exception as e:
        print(f"❌ Error connecting to Supabase: {e}")
        return False

    # Import projects
    print("\n📁 Importing Projects...")
    projects = export_data["tables"]["archon_projects"]
    if projects:
        try:
            # Use upsert to handle existing data
            response = supabase.table("archon_projects").upsert(projects).execute()
            print(f"  ✅ Imported {len(projects)} project(s)")
        except Exception as e:
            print(f"  ❌ Error importing projects: {e}")

    # Import documents
    print("\n📄 Importing Documents...")
    documents = export_data["tables"]["archon_documents"]
    if documents:
        try:
            # Add project_id to each document if not present
            for doc in documents:
                if "project_id" not in doc:
                    doc["project_id"] = export_data["project_id"]

            # Import in batches
            batch_size = 50
            for i in range(0, len(documents), batch_size):
                batch = documents[i : i + batch_size]
                response = supabase.table("archon_documents").upsert(batch).execute()
                print(
                    f"  ✅ Imported batch {i//batch_size + 1} ({len(batch)} documents)"
                )
        except Exception as e:
            print(f"  ❌ Error importing documents: {e}")

    # Note about tasks
    print("\n📋 Tasks Note:")
    print("  ⚠️  Tasks require manual pagination due to size limits.")
    print("  Use the following approach to import tasks:")
    print()
    print("  1. Use Archon MCP to export tasks page by page:")
    print("     mcp__archon__list_tasks(filter_by='project', ")
    print(
        "                             filter_value='342d657c-fb73-4f71-9b6e-302857319aac',"
    )
    print("                             page=1, per_page=10)")
    print()
    print("  2. Save each page to a separate JSON file")
    print("  3. Import each page using this script's task import function")

    print("\n" + "=" * 60)
    print("IMPORT SUMMARY")
    print("=" * 60)
    print(f"✅ Projects imported: {len(projects)}")
    print(f"✅ Documents imported: {len(documents)}")
    print(f"⚠️  Tasks: Manual import required (see instructions above)")

    print("\n✨ Import complete!")
    print("\nNext steps:")
    print("1. Verify data in your Supabase dashboard")
    print("2. Update Archon's .env file with these Supabase credentials")
    print("3. Restart Archon to connect to the new database")

    # Save credentials for reference
    save_config = input("\nSave Supabase config for Archon? (y/n): ").lower()
    if save_config == "y":
        config_file = Path("/home/omar/Documents/ruleIQ/archon_supabase_config.txt")
        with open(config_file, "w") as f:
            f.write(f"# Archon Supabase Configuration\n")
            f.write(f"# Add these to Archon's .env file:\n\n")
            f.write(f"SUPABASE_URL={SUPABASE_URL}\n")
            f.write(f"SUPABASE_SERVICE_KEY={SUPABASE_KEY}\n")
        print(f"✅ Config saved to: {config_file}")
        print("   Copy these values to /home/omar/Archon/.env")

    return True


def import_tasks_batch(tasks_json_file, supabase_url, supabase_key):
    """Import a batch of tasks from a JSON file"""

    # Load tasks
    with open(tasks_json_file, "r") as f:
        tasks = json.load(f)

    # Connect to Supabase
    supabase: Client = create_client(supabase_url, supabase_key)

    # Import tasks
    try:
        response = supabase.table("archon_tasks").upsert(tasks).execute()
        print(f"✅ Imported {len(tasks)} tasks from {tasks_json_file}")
        return True
    except Exception as e:
        print(f"❌ Error importing tasks: {e}")
        return False


if __name__ == "__main__":
    try:
        print("🚀 Starting Archon data import to Supabase\n")

        # Check if export file exists
        export_file = Path("/home/omar/Documents/ruleIQ/archon_data_export.json")
        if not export_file.exists():
            print("❌ Export file not found. Please run the export process first.")
            exit(1)

        # Run import
        success = import_archon_data()

        if success:
            print("\n✅ Import process completed successfully!")
        else:
            print(
                "\n❌ Import process encountered errors. Please check the output above."
            )

    except KeyboardInterrupt:
        print("\n\n⚠️  Import cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
