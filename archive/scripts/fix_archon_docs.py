#!/usr/bin/env python3
"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Fix Archon documents by updating the project's docs field
"""

import json
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://wohtxsiayhtvycvkamev.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndvaHR4c2lheWh0dnljdmthbWV2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjYyNTczOSwiZXhwIjoyMDcyMjAxNzM5fQ.mzmZQ_cBvjr0B1oSuRrjZ_jk4HqM7Xz0bETDo29RzI0"

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

with open("/home/omar/Documents/ruleIQ/archon_project_full.json", "w") as f:
    project_data = {
        "id": "342d657c-fb73-4f71-9b6e-302857319aac",
        "title": "ruleIQ Compliance Automation Platform",
        "description": "",
        "github_repo": "https://github.com/user/ruleiq",
        "pinned": False,
        "features": {},
        "data": {},
        "docs": [],  # This needs to be populated with the full docs array
    }
    json.dump(project_data, f, indent=2)

logger.info("To fix the documents issue:")
print(
    "1. The documents are stored in the project's 'docs' field, not as separate records"
)
logger.info("2. We need to update the project record with the full docs array")
print(
    "3. The Archon MCP server already has this data - we just need to sync it to Supabase"
)
logger.info()
logger.info("The issue is that Archon stores documents differently than expected.")
logger.info("Documents are embedded in the project record, not stored separately.")
