import os
#!/usr/bin/env python3
"""
Migrate ALL Archon data from old Supabase to new Supabase
This includes tasks, sources, crawled pages, and code examples
"""

from supabase import create_client
import json
from datetime import datetime

# OLD Supabase (source)
OLD_SUPABASE_URL = "https://nxmzlhiutzqvkyhhntez.supabase.co"
OLD_SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

# NEW Supabase (destination)
NEW_SUPABASE_URL = "https://wohtxsiayhtvycvkamev.supabase.co"
NEW_SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")


def migrate_table(table_name, old_client, new_client, batch_size=100):
    """Migrate a table from old to new Supabase"""
    print(f"\n📦 Migrating {table_name}...")

    try:
        # Get all data from old table
        all_data = []
        offset = 0

        while True:
            response = (
                old_client.table(table_name)
                .select("*")
                .range(offset, offset + batch_size - 1)
                .execute()
            )

            if not response.data:
                break

            all_data.extend(response.data)
            print(f"  Fetched {len(response.data)} records (total: {len(all_data)})")

            if len(response.data) < batch_size:
                break
            offset += batch_size

        if not all_data:
            print(f"  No data to migrate")
            return 0

        # Insert into new table in batches
        for i in range(0, len(all_data), batch_size):
            batch = all_data[i : i + batch_size]
            new_client.table(table_name).upsert(batch).execute()
            print(f"  Migrated batch {i//batch_size + 1} ({len(batch)} records)")

        print(f"  ✅ Successfully migrated {len(all_data)} records")
        return len(all_data)

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return 0


def main():
    print("=" * 60)
    print("ARCHON DATA MIGRATION")
    print("From: OLD Supabase (nxmzlhiutzqvkyhhntez)")
    print("To:   NEW Supabase (wohtxsiayhtvycvkamev)")
    print("=" * 60)

    # Create clients
    old_supabase = create_client(OLD_SUPABASE_URL, OLD_SUPABASE_KEY)
    new_supabase = create_client(NEW_SUPABASE_URL, NEW_SUPABASE_KEY)

    # Tables to migrate in order (respecting foreign keys)
    tables = [
        "archon_sources",  # Knowledge sources
        "archon_prompts",  # System prompts
        "archon_settings",  # Configuration
        "archon_tasks",  # Project tasks
        "archon_project_sources",  # Project-source links
        "archon_document_versions",  # Document versions
        "archon_crawled_pages",  # Knowledge content (this is the big one!)
        "archon_code_examples",  # Code snippets
    ]

    stats = {}

    for table in tables:
        count = migrate_table(table, old_supabase, new_supabase)
        stats[table] = count

    # Also update the project's docs field if needed
    print("\n📄 Updating project documents...")
    try:
        # Get project from old DB
        old_project = (
            old_supabase.table("archon_projects")
            .select("*")
            .eq("id", "342d657c-fb73-4f71-9b6e-302857319aac")
            .execute()
        )
        if old_project.data and old_project.data[0].get("docs"):
            # Update in new DB
            new_supabase.table("archon_projects").update(
                {"docs": old_project.data[0]["docs"]}
            ).eq("id", "342d657c-fb73-4f71-9b6e-302857319aac").execute()
            print("  ✅ Updated project docs field")
    except Exception as e:
        print(f"  ❌ Error updating docs: {e}")

    print("\n" + "=" * 60)
    print("MIGRATION COMPLETE!")
    print("=" * 60)

    for table, count in stats.items():
        status = "✅" if count > 0 else "⚠️"
        print(f"{status} {table}: {count} records")

    print("\n🎉 Your Archon knowledge base has been migrated!")
    print("Tasks, sources, and documentation are now in the new Supabase.")


if __name__ == "__main__":
    main()
