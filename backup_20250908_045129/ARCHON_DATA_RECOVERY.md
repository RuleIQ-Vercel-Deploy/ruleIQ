# Archon Data Recovery Guide

## 🎉 Good News!
Your Archon data is **SAFE and ACCESSIBLE** through the Archon MCP server! The data exists and can be recovered.

## Current Situation

### ✅ What's Working
- **Archon MCP server** is running and has all your ruleIQ project data
- **Project ID:** `342d657c-fb73-4f71-9b6e-302857319aac`
- **11 documents** are stored and accessible
- **Project metadata** is intact
- Data can be exported and imported to a new Supabase instance

### ❌ The Problem
- Original Supabase instance (`https://nxmzlhiutzqvkyhhntez.supabase.co`) appears to be inaccessible
- Archon UI cannot connect to the database
- Need to migrate data to a new Supabase instance

## Recovery Steps

### Step 1: Data Export (✅ COMPLETED)
The data has been exported to:
- **Export file:** `/home/omar/Documents/ruleIQ/archon_data_export.json`
- Contains: Projects, Documents, metadata
- Tasks require manual pagination (see below)

### Step 2: Create New Supabase Project
1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Create a new project
3. Note down:
   - Project URL (e.g., `https://xxxxx.supabase.co`)
   - Service Role Key (starts with `eyJ...`)

### Step 3: Set Up Database Schema
Run the schema creation script:
```bash
# Use the existing schema file
psql -h [your-supabase-host] -U postgres -d postgres < /home/omar/Archon/migration/complete_setup.sql
```

Or use Supabase SQL Editor with the content from `complete_setup.sql`

### Step 4: Import Data
```bash
# Run the import script
python /home/omar/Documents/ruleIQ/import_archon_to_supabase.py
```

This will:
- Import all projects
- Import all documents
- Provide instructions for task import

### Step 5: Export Tasks (Manual Process)
Due to the large number of tasks, they need to be exported in pages:

```python
# Using the Archon MCP server, export tasks page by page:
# Page 1
mcp__archon__list_tasks(
    filter_by='project',
    filter_value='342d657c-fb73-4f71-9b6e-302857319aac',
    page=1,
    per_page=10
)

# Save the response to tasks_page1.json
# Repeat for additional pages until all tasks are exported
```

### Step 6: Update Archon Configuration
1. Edit `/home/omar/Archon/.env`
2. Update with new Supabase credentials:
```env
SUPABASE_URL=https://your-new-project.supabase.co
SUPABASE_SERVICE_KEY=your-new-service-key
```

3. Restart Archon:
```bash
cd /home/omar/Archon
# Restart the Archon server
```

## Alternative Recovery Options

### Option A: Direct MCP Access (Current)
- Continue using Archon through the MCP server
- Data is accessible and safe
- No immediate action required

### Option B: Local Database
- Set up a local PostgreSQL instance
- Import the schema and data locally
- Configure Archon to use local database

### Option C: Contact Supabase Support
- If the original project should still be active
- Check if there are billing or access issues
- Request data export from their end

## Data Inventory

### What We Have
```json
{
  "projects": 1,
  "documents": 11,
  "document_types": [
    "analysis",
    "audit",
    "spec",
    "report",
    "note"
  ],
  "key_documents": [
    "AI System Architecture Analysis",
    "Test Suite Reality Check",
    "Phase 1 Completion Report",
    "Multi-Phase Audit Complete"
  ]
}
```

### Tasks (Need Manual Export)
- Multiple tasks exist but require pagination
- Use the MCP server to export in batches
- Each batch can be imported separately

## Quick Commands Reference

```bash
# Check Archon MCP status
mcp__archon__health_check()

# Get project details
mcp__archon__get_project(project_id="342d657c-fb73-4f71-9b6e-302857319aac")

# List documents
mcp__archon__list_documents(project_id="342d657c-fb73-4f71-9b6e-302857319aac")

# Export tasks (paginated)
mcp__archon__list_tasks(
    filter_by="project",
    filter_value="342d657c-fb73-4f71-9b6e-302857319aac",
    page=1,
    per_page=10
)
```

## Success Criteria
✅ New Supabase instance created  
✅ Schema deployed  
✅ Data imported  
✅ Archon connected to new database  
✅ UI accessible and functional  

## Support Files
- **Schema:** `/home/omar/Archon/migration/complete_setup.sql`
- **Export Data:** `/home/omar/Documents/ruleIQ/archon_data_export.json`
- **Import Script:** `/home/omar/Documents/ruleIQ/import_archon_to_supabase.py`
- **Export Script:** `/home/omar/Documents/ruleIQ/export_archon_data.py`

## Notes
- All your data is safe in the Archon MCP server
- The recovery process is straightforward
- Once migrated, Archon will work exactly as before
- Consider setting up regular backups going forward

---
*Generated: 2025-08-31*  
*Status: Data Safe, Recovery Path Clear*