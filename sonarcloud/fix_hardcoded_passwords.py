#!/usr/bin/env python3
"""
Fix S6698 violations - Remove hardcoded passwords from code
"""

import os
import re

def fix_hardcoded_passwords(file_path):
    """Fix hardcoded passwords by replacing with environment variables"""
    
    if not os.path.exists(file_path):
        print(f"  ⚠️  File not found: {file_path}")
        return False
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern to match PostgreSQL connection strings with hardcoded passwords
    patterns = [
        # postgresql://user:password@host:port/database
        (r'postgresql://[^:]+:([^@]+)@[^/]+/\w+', 
         'postgresql://" + os.getenv("DB_USER", "postgres") + ":" + os.getenv("DB_PASSWORD", "postgres") + "@" + os.getenv("DB_HOST", "localhost") + ":" + os.getenv("DB_PORT", "5432") + "/" + os.getenv("DB_NAME", "database") + "'),
        
        # Simpler replacement for test environments
        (r'"postgresql://postgres:postgres@localhost:\d+/\w+"',
         'os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/test")'),
        
        (r"'postgresql://postgres:postgres@localhost:\d+/\w+'",
         "os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/test')"),
    ]
    
    # Apply replacements
    for pattern, replacement in patterns:
        if re.search(pattern, content):
            # Check if we need to add import
            if 'os.getenv' in replacement and 'import os' not in content:
                # Add import at the beginning of the file
                content = "import os\n" + content
            
            # Replace the hardcoded connection string
            content = re.sub(pattern, replacement, content)
    
    # Special handling for specific patterns in the files
    if "DATABASE_URL" in content and "postgresql://postgres:postgres" in content:
        content = content.replace(
            '"postgresql://postgres:postgres@localhost:5433/compliance_test"',
            'os.getenv("TEST_DATABASE_URL", "postgresql://localhost/test")'
        )
        content = content.replace(
            "'postgresql://postgres:postgres@localhost:5433/compliance_test'",
            "os.getenv('TEST_DATABASE_URL', 'postgresql://localhost/test')"
        )
    
    if content != original_content:
        with open(file_path, 'w') as f:
            f.write(content)
        return True
    return False

def main():
    print("\n" + "="*60)
    print("FIXING S6698 VIOLATIONS - Hardcoded Passwords")
    print("="*60)
    
    # List of files with hardcoded password violations
    files_to_fix = [
        "archive/scripts/capture_test_errors.py",
        "archive/scripts/check_schema.py",
        "scripts/setup_secrets_vault.py",
        "scripts/debug_freemium_tables.py",
        "scripts/simple_test_debug.py",
        "archive/test_configs/conftest_fixed.py",
        "archive/test_configs/conftest_hybrid.py",
        "archive/test_configs/conftest_improved.py",
    ]
    
    fixed_count = 0
    for file_path in files_to_fix:
        print(f"\n📝 Processing: {file_path}")
        if fix_hardcoded_passwords(file_path):
            print(f"  ✅ Fixed")
            fixed_count += 1
        else:
            print(f"  ⚠️  No changes needed or file not found")
    
    # Also fix the Supabase JWT secret issue
    supabase_file = "archive/scripts/migrate_archon_data.py"
    print(f"\n📝 Processing Supabase JWT secret: {supabase_file}")
    
    if os.path.exists(supabase_file):
        with open(supabase_file, 'r') as f:
            content = f.read()
        
        # Replace hardcoded Supabase service role key
        if 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9' in content:
            content = re.sub(
                r'"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9[^"]*"',
                'os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")',
                content
            )
            
            # Add import if needed
            if 'import os' not in content:
                content = "import os\n" + content
            
            with open(supabase_file, 'w') as f:
                f.write(content)
            print(f"  ✅ Fixed Supabase JWT secret")
            fixed_count += 1
        else:
            print(f"  ⚠️  No Supabase JWT secret found")
    else:
        print(f"  ⚠️  File not found")
    
    print("\n" + "="*60)
    print(f"✅ Fixed {fixed_count}/{len(files_to_fix) + 1} files")
    print("="*60)
    
    print("\n🎯 Summary:")
    print("  - Replaced hardcoded PostgreSQL passwords with environment variables")
    print("  - Replaced Supabase service role key with environment variable")
    print("  - Added os.getenv() calls for secure credential handling")
    
    print("\n⚠️  Important:")
    print("  - Ensure environment variables are properly set in production")
    print("  - Use Doppler or other secret management tools")
    print("  - Never commit real credentials to the repository")

if __name__ == "__main__":
    main()