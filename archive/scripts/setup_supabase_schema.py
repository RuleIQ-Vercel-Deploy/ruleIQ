#!/usr/bin/env python3
"""
from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

Set up Archon schema in Supabase
"""

from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://wohtxsiayhtvycvkamev.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndvaHR4c2lheWh0dnljdmthbWV2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NjYyNTczOSwiZXhwIjoyMDcyMjAxNzM5fQ.mzmZQ_cBvjr0B1oSuRrjZ_jk4HqM7Xz0bETDo29RzI0"

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

logger.info("Setting up Archon schema in Supabase...")
logger.info("Please go to your Supabase dashboard:")
logger.info("https://supabase.com/dashboard/project/wohtxsiayhtvycvkamev/sql/new")
logger.info()
print(
    "Then paste the contents of setup_archon_supabase.sql into the SQL Editor and run it."
)
logger.info()
logger.info("The file is located at: /home/omar/Documents/ruleIQ/setup_archon_supabase.sql")
logger.info()
logger.info("After running the SQL, run the import script again:")
logger.info("python import_archon_to_supabase.py")
