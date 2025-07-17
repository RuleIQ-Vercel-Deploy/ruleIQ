#!/usr/bin/env python3
"""Test settings parsing"""
import os
import sys

# Set test environment variables
os.environ['CORS_ORIGINS'] = '["http://localhost:3000","http://localhost:3001"]'
os.environ['ALLOWED_FILE_TYPES'] = 'pdf,doc,docx,xls,xlsx'
os.environ['DATABASE_URL'] = 'postgresql://postgres:password@localhost:5432/test'
os.environ['SECRET_KEY'] = 'test-secret'
os.environ['JWT_SECRET'] = 'test-jwt-secret'
os.environ['ENCRYPTION_KEY'] = 'test-encryption-key-32-chars-long'

try:
    from config.settings import settings
    print("✓ Settings loaded successfully!")
    print(f"CORS Origins: {settings.cors_origins}")
    print(f"Allowed File Types: {settings.allowed_file_types}")
except Exception as e:
    print(f"✗ Failed to load settings: {e}")
    import traceback
    traceback.print_exc()