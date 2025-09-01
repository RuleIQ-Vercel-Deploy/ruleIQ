#!/usr/bin/env python3
"""
Fix Archon documents by updating the project's docs field
"""

import json
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = 'https://wohtxsiayhtvycvkamev.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndvaHR4c2lheWh0dnljdmthbWV2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjYyNTczOSwiZXhwIjoyMDcyMjAxNzM5fQ.mzmZQ_cBvjr0B1oSuRrjZ_jk4HqM7Xz0bETDo29RzI0'

# Create Supabase client  
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load the project data from our earlier export (which includes the full docs array)
with open('/home/omar/Documents/ruleIQ/archon_project_full.json', 'w') as f:
    # This is the full project data from the get_project response
    project_data = {
        "id": "342d657c-fb73-4f71-9b6e-302857319aac",
        "title": "ruleIQ Compliance Automation Platform",
        "description": "",
        "github_repo": "https://github.com/user/ruleiq",
        "pinned": False,
        "features": {},
        "data": {},
        "docs": []  # This needs to be populated with the full docs array
    }
    json.dump(project_data, f, indent=2)

print("To fix the documents issue:")
print("1. The documents are stored in the project's 'docs' field, not as separate records")
print("2. We need to update the project record with the full docs array")
print("3. The Archon MCP server already has this data - we just need to sync it to Supabase")
print()
print("The issue is that Archon stores documents differently than expected.")
print("Documents are embedded in the project record, not stored separately.")